#!/usr/bin/env python3
"""
L16 -- Machine learning foundation: the classical half of the course.

Course section: 16 (Machine Learning Foundation).

Run me::

    python labs/L16_machine_learning_foundation/lab.py

What you will build
-------------------
* A *linear model* and the idea of "learning the parameters" by hand.
* Gradient descent, the learning rate, and why feature scaling matters.
* The bias/variance trade-off: underfit, just right, overfit.
* Classification with a logistic (sigmoid) model and the log-loss.
* L1 and L2 regularization -- the shrinkage that keeps models honest.
* A one-hidden-layer neural network, with back-propagation written out.
* A side-by-side comparison with the same model written in scikit-learn.

Everything here is plain Python on purpose: the course teaches the maths
first, and quantum machine learning is only meaningful once the classical
machine-learning machinery is second nature.  Section 17 of the course then
replaces the classical distance function and the classical kernel with
quantum circuits.
"""

from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from qc101.labkit import Lab
from qc101 import linalg as la
from qc101 import viz

lab = Lab("L16", "Machine learning foundation")
RNG = random.Random(4242)


# ===========================================================================
# Small vector / matrix helpers (plain Python, no numpy)
# ===========================================================================
def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def sigmoid(z):
    """The logistic function, numerically safe for large |z|."""
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


def log_loss(y, p, eps=1e-12):
    """Binary cross-entropy for one example."""
    p = min(max(p, eps), 1 - eps)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def mean(values):
    return sum(values) / len(values)


# ===========================================================================
# The dataset: two concentric rings
# ===========================================================================
def make_circles(n_per_class=100, r_inner=1.2, r_outer=2.6, noise=0.28, seed=13):
    """
    Two concentric rings: class 0 on the inner ring, class 1 on the outer.

    This is the classic 'not linearly separable' dataset.  A straight line
    can do no better than chance; a *quadratic* boundary separates the two
    rings perfectly, because the radius -- not the direction -- is what
    carries the label.
    """
    rng = random.Random(seed)
    data = []
    for radius, label in ((r_inner, 0), (r_outer, 1)):
        for _ in range(n_per_class):
            angle = rng.uniform(0, 2 * math.pi)
            r = radius + rng.gauss(0, noise)
            data.append((r * math.cos(angle), r * math.sin(angle), label))
    rng.shuffle(data)
    return data


def split(data, fraction=0.75, seed=11):
    """Shuffle and split into (train, test)."""
    rng = random.Random(seed)
    shuffled = data[:]
    rng.shuffle(shuffled)
    cut = int(len(shuffled) * fraction)
    return shuffled[:cut], shuffled[cut:]


def polynomial_features(row, degree):
    """The design-matrix row for a 2-D point and a polynomial degree."""
    x, y = row[0], row[1]
    if degree == 1:
        return [x, y]
    if degree == 2:
        return [x, y, x * x, y * y, x * y]
    return [x ** p for p in range(1, degree + 1)]


def standardize(matrix):
    """Return (scaled matrix, means, standard deviations)."""
    n = len(matrix[0])
    means = [sum(row[j] for row in matrix) / len(matrix) for j in range(n)]
    sds = [math.sqrt(sum((row[j] - means[j]) ** 2 for row in matrix) / len(matrix))
           or 1.0 for j in range(n)]
    scaled = [[(row[j] - means[j]) / sds[j] for j in range(n)] for row in matrix]
    return scaled, means, sds


# ===========================================================================
# 1. Introduction to machine learning
# ===========================================================================
lab.section("1. Introduction to machine learning")

lab.step("A program that follows rules you wrote by hand ...")
lab.show("""
    if 'free' in subject and 'money' in subject:   -> spam
""")
lab.note("breaks the moment the wording changes.  Machine learning flips the "
         "problem: you show the program many *examples* and it works out the "
         "rule itself.")

lab.note("The three ingredients of every machine-learning system")
lab.show(viz.table(
    ["ingredient", "what it is", "in this lab"],
    [
        ("data", "examples with the right answers", "two concentric rings"),
        ("model", "a family of functions with tunable knobs", "w . x + b"),
        ("loss", "a number that says how wrong the model is", "mean squared error"),
    ]))
lab.note("The knobs (the *parameters*) start at random values.  Training means "
         "nudging them until the loss stops falling.")

lab.step("The whole loop, in one picture")
lab.show("""
    data  ->  features  ->  model  ->  predictions  ->  loss
      ^                                       |
      |                                       v
      +------------  update the parameters  -+
""")
lab.note("Everything else in machine learning -- decision trees, neural "
         "networks, support vector machines, quantum kernels -- is a different "
         "choice of *model* inside this same loop.")


# ===========================================================================
# 2. What is AI?
# ===========================================================================
lab.section("2. What is AI?")

lab.step("AI, ML and deep learning are nested circles, not synonyms.")
lab.show(viz.table(
    ["circle", "meaning", "example"],
    [
        ("AI", "any system that does something that needs intelligence",
         "a chess engine's search"),
        ("ML", "AI that learns its rules from data instead of being told them",
         "spam filtering"),
        ("DL", "ML using many-layered neural networks",
         "image recognition"),
        ("Quantum ML", "ML where part of the model is a quantum circuit",
         "the quantum kernel in section 17"),
    ]))

lab.step("The quantum part is narrow -- and that is fine.")
lab.note("A quantum circuit can be used for exactly two things in an ML "
         "pipeline: (a) to *measure* something, and (b) to compute a "
         "*kernel* / similarity.  The data wrangling, the loss and the "
         "optimizer stay classical.")
lab.note("This is why section 16 exists: the quantum algorithms in section 17 "
         "are drop-in replacements for two classical pieces, and you cannot "
         "judge them without knowing what those pieces do.")


# ===========================================================================
# 3. Structure of ML systems
# ===========================================================================
lab.section("3. Structure of ML systems")

lab.step("A realistic ML system has more parts than 'the model'.")
lab.show(viz.table(
    ["stage", "what happens", "failure mode if you skip it"],
    [
        ("data collection", "gather examples", "garbage in, garbage out"),
        ("feature engineering", "turn raw rows into numbers", "leaky features"),
        ("train/test split", "hold data back", "you are grading your own exam"),
        ("model + loss", "choose the family and the score", "wrong objective"),
        ("optimizer", "fit the parameters", "no convergence"),
        ("validation", "measure on unseen data", "no idea if it generalises"),
        ("deployment", "serve predictions", "training/serving skew"),
    ]))

lab.step("Feature engineering: the part people underrate.")
lab.note("A 'feature' is one number you hand to the model.  A row of the iris "
         "dataset is [sepal length, sepal width, petal length, petal width] -- "
         "four features, four numbers.")
lab.note("You may add features yourself: squared terms for a curved decision "
         "boundary, ratios, day-of-week, ...  Section 17's quantum kernel "
         "does exactly this, but the squaring happens in a quantum circuit.")


# ===========================================================================
# 4. Learning with models
# ===========================================================================
lab.section("4. Learning with models")

lab.step("The simplest model with learnable parameters: a straight line.")
lab.note("y_hat = w . x + b, with w the weight vector and b the bias.")
lab.note("Training = choosing w and b so that the line fits the data.")

X = [[1.0, 2.0], [2.0, 1.0], [3.0, 4.0], [4.0, 3.0], [5.0, 5.0], [6.0, 4.0]]
Y = [3.0, 3.0, 7.0, 7.0, 10.0, 10.0]


def mse(weights, bias, xs, ys):
    """Mean squared error of a linear model."""
    total = 0.0
    for x, y in zip(xs, ys):
        total += (dot(weights, x) + bias - y) ** 2
    return total / len(xs)


def fit_linear(xs, ys, steps=2000, lr=0.05):
    """Plain gradient descent on the mean squared error."""
    n_features = len(xs[0])
    weights = [0.0] * n_features
    bias = 0.0
    losses = []
    for _ in range(steps):
        errors = [dot(weights, x) + bias - y for x, y in zip(xs, ys)]
        losses.append(sum(e * e for e in errors) / len(errors))
        grad_w = [0.0] * n_features
        grad_b = 0.0
        for x, e in zip(xs, errors):
            for j in range(n_features):
                grad_w[j] += e * x[j]
            grad_b += e
        n = len(errors)
        weights = [w - lr * g / n for w, g in zip(weights, grad_w)]
        bias -= lr * grad_b / n
    return weights, bias, losses


w, b, losses = fit_linear(X, Y)
lab.show(viz.table(
    ["quantity", "value"],
    [("w", ", ".join(f"{v:.4f}" for v in w)),
     ("b", f"{b:.4f}"),
     ("loss after 0 steps", f"{losses[0]:.4f}"),
     ("loss after 2000 steps", f"{losses[-1]:.6f}")]))
lab.check("the loss went down", losses[-1] < losses[0] * 1e-3)
lab.check_close("the fitted model reproduces the training data",
                [dot(w, x) + b for x in X], Y, tol=0.05)
lab.note("The exact answer for this data is w = (1, 1) and b = 0: every target "
         "is the sum of the two features.  Gradient descent found it.")


# ===========================================================================
# 5. Speed up learning
# ===========================================================================
lab.section("5. Speed up learning")

lab.step("Gradient descent: walk downhill in the direction of the gradient.")
lab.show("""
    w  <-  w  -  learning_rate * d(loss)/dw
""")
lab.note("The learning rate is the size of each step.  Too small and you "
         "crawl; too large and you overshoot and diverge.")

lab.step("Compare learning rates on the same problem.")
rows = []
for lr in (0.001, 0.01, 0.05, 0.2, 0.5):
    _, _, ls = fit_linear(X, Y, steps=400, lr=lr)
    rows.append((lr, f"{ls[-1]:.6f}", f"{ls[-1] < ls[0]}"))
lab.show(viz.table(["learning rate", "final loss", "loss decreased?"], rows))
lab.check("a moderate learning rate converges", losses[-1] < 1e-3)

lab.step("Feature scaling: the single biggest speed-up for gradient descent.")
lab.note("Gradient descent is only well-behaved when the features have "
         "comparable scales.  With one feature measured in millimetres and "
         "another in kilometres, the gradient is dominated by the big one.")

rows = []
for lr in (0.05, 0.5, 5.0):
    _, _, ls_raw = fit_linear(X, Y, steps=400, lr=lr)
    scaled_X = [[v / 10.0 for v in x] for x in X]
    _, _, ls_scl = fit_linear(scaled_X, Y, steps=400, lr=lr)
    rows.append((lr, f"{ls_raw[-1]:.6f}", f"{ls_scl[-1]:.6f}"))
lab.show(viz.table(
    ["learning rate", "raw features", "scaled features"], rows))
lab.note("Look at the learning rate 0.5 row: with the raw features the loss "
         "explodes, with the scaled features it converges.  Same data, same "
         "model -- only the units changed.")
lab.check("a big learning rate diverges on the raw features",
          not math.isfinite(float(rows[1][1])) or float(rows[1][1]) > 1.0,
          f"final loss on raw features = {rows[1][1]}")
lab.check("the same learning rate converges on the scaled features",
          math.isfinite(float(rows[1][2])) and float(rows[1][2]) < 1.0,
          f"final loss on scaled features = {rows[1][2]}")
lab.note("Standardization (subtract the mean, divide by the standard "
         "deviation) is the usual fix.  Section 17's feature map effectively "
         "does this inside a quantum circuit.")


# ===========================================================================
# 6. Underfit and overfit
# ===========================================================================
lab.section("6. Underfit and overfit")

lab.step("Build the dataset and split it into training and test sets.")
data = make_circles(n_per_class=100)
train, test = split(data, 0.75)
lab.show(viz.table(
    ["split", "rows", "class 0", "class 1"],
    [("train", len(train), sum(1 for r in train if r[2] == 0),
      sum(1 for r in train if r[2] == 1)),
     ("test", len(test), sum(1 for r in test if r[2] == 0),
      sum(1 for r in test if r[2] == 1))]))
lab.check("the test set is held back and is smaller", 0 < len(test) < len(train))
lab.note("Two concentric rings.  Which class a point belongs to depends on "
         "its *radius*, not on which side of a line it is -- so a straight "
         "line cannot do better than chance.")

lab.step("A polynomial model: add x^2, y^2 and x*y as extra features.")


def poly_fit(train_rows, degree, steps=15000, lr=0.4, lam=0.0):
    """Fit a linear model on polynomial features, with optional L2 penalty."""
    Xtr = [polynomial_features(r, degree) for r in train_rows]
    Ytr = [float(r[2]) for r in train_rows]
    Xs, means, sds = standardize(Xtr)
    n_features = len(Xs[0])
    weights = [0.0] * n_features
    bias = 0.0
    for step in range(steps):
        rate = lr / (1.0 + step / 2000.0)          # decay keeps high degrees stable
        errors = [dot(weights, x) + bias - y for x, y in zip(Xs, Ytr)]
        grad_w = [0.0] * n_features
        grad_b = 0.0
        for x, e in zip(Xs, errors):
            for j in range(n_features):
                grad_w[j] += e * x[j]
            grad_b += e
        n = len(errors)
        weights = [w - rate * (g / n + lam * w) for w, g in zip(weights, grad_w)]
        bias -= rate * grad_b / n
    return weights, bias, means, sds


def poly_accuracy(weights, bias, rows, degree, means, sds):
    correct = 0
    for row in rows:
        features = polynomial_features(row, degree)
        scaled = [(features[j] - means[j]) / sds[j] for j in range(len(features))]
        guess = 1 if dot(weights, scaled) + bias >= 0.5 else 0
        correct += 1 if guess == row[2] else 0
    return correct / len(rows)


rows = []
for degree in (1, 2, 3):
    weights, bias, means, sds = poly_fit(train, degree)
    rows.append((degree,
                 f"{poly_accuracy(weights, bias, train, degree, means, sds):.3f}",
                 f"{poly_accuracy(weights, bias, test, degree, means, sds):.3f}"))
lab.show(viz.table(["polynomial degree", "train accuracy", "test accuracy"], rows))
lab.check("the straight line is no better than chance",
          float(rows[0][2]) < 0.7,
          f"linear test accuracy = {rows[0][2]}")
lab.check("the quadratic model beats the linear one on the test set",
          float(rows[1][2]) > float(rows[0][2]) + 0.2,
          f"linear {rows[0][2]} vs quadratic {rows[1][2]}")

lab.step("Underfit vs overfit, made visible with a 1-D curve.")
lab.note("Fit y = sin(2*pi*x) + noise with polynomials of increasing degree, "
         "using only 10 of the 20 points.  This time we solve the normal "
         "equations exactly (a touch of the linear algebra from section 6 of "
         "the course) instead of running gradient descent.")

rng = random.Random(5)
curve_x = [i / 19.0 for i in range(20)]
curve_y = [math.sin(2 * math.pi * x) + rng.gauss(0, 0.12) for x in curve_x]
curve_train = [(curve_x[i], curve_y[i]) for i in range(0, 20, 2)]
curve_test = [(curve_x[i], curve_y[i]) for i in range(1, 20, 2)]


def ridge_solve(design_rows, targets, lam=1e-6):
    """
    Solve the ridge-regression normal equations (X^T X + lam I) w = X^T y.

    The tiny lam keeps the system solvable when there are more basis
    functions than data points.
    """
    n = len(design_rows[0])
    xtx = [[sum(r[i] * r[j] for r in design_rows) for j in range(n)]
           for i in range(n)]
    xty = [sum(r[i] * t for r, t in zip(design_rows, targets)) for i in range(n)]
    for i in range(n):
        xtx[i][i] += lam
    inverse = la.inverse(xtx)
    return [sum(inverse[i][j] * xty[j] for j in range(n)).real for i in range(n)]


def curve_rmse(weights, points):
    total = 0.0
    for x, y in points:
        features = [x ** p for p in range(len(weights))]
        total += (dot(weights, features) - y) ** 2
    return math.sqrt(total / len(points))


rows = []
for degree in (1, 3, 5, 7, 9, 12):
    design_train = [[x ** p for p in range(degree + 1)] for x, _ in curve_train]
    weights = ridge_solve(design_train, [y for _, y in curve_train])
    rows.append((degree,
                 f"{curve_rmse(weights, curve_train):.4f}",
                 f"{curve_rmse(weights, curve_test):.4f}"))
lab.show(viz.table(
    ["degree", "train RMSE", "test RMSE"], rows))
lab.check("the straight line underfits -- bad on both sets",
          float(rows[0][1]) > float(rows[1][1]) and float(rows[0][2]) > float(rows[1][2]))
lab.check("the training error keeps falling as the model gets more flexible",
          float(rows[-1][1]) < float(rows[0][1]))
lab.check("but the test error turns back up -- that is overfitting",
          float(rows[-1][2]) > float(rows[1][2]),
          f"degree 3 test RMSE {rows[1][2]} vs degree 12 test RMSE {rows[-1][2]}")
lab.note("Underfitting: the model is too simple to capture the pattern "
         "(high bias).")
lab.note("Overfitting: the model is so flexible that it memorises noise "
         "(high variance).  The sweet spot lives between the two -- and only "
         "a held-out test set can tell you where it is.")


# ===========================================================================
# 7. Classification
# ===========================================================================
lab.section("7. Classification")

lab.step("Classification predicts a *label*, not a number.")
lab.show(viz.table(
    ["problem", "input", "output", "loss"],
    [("regression", "features x", "a real number y", "mean squared error"),
     ("classification", "features x", "a class label", "log-loss / accuracy")]))

lab.step("Accuracy is not enough -- a confusion matrix tells the truth.")
lab.note("For a binary classifier there are four outcomes:")
lab.show(viz.table(
    ["", "predicted 1", "predicted 0"],
    [("actually 1", "true positive", "false negative"),
     ("actually 0", "false positive", "true negative")]))
lab.note("Precision = TP/(TP+FP) -- of the ones you flagged, how many were "
         "right?")
lab.note("Recall = TP/(TP+FN) -- of the real ones, how many did you catch?")
lab.note("A model that always predicts 1 has 50% accuracy on a balanced "
         "problem and recall 1.0 -- useless, and the metrics say so.")


def metrics(truth, guesses):
    tp = sum(1 for t, g in zip(truth, guesses) if t == 1 and g == 1)
    tn = sum(1 for t, g in zip(truth, guesses) if t == 0 and g == 0)
    fp = sum(1 for t, g in zip(truth, guesses) if t == 0 and g == 1)
    fn = sum(1 for t, g in zip(truth, guesses) if t == 1 and g == 0)
    total = tp + tn + fp + fn
    acc = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return acc, precision, recall, f1


truth = [1, 1, 1, 0, 0, 0, 1, 0]
guesses = [1, 1, 0, 0, 1, 0, 1, 0]
acc0, prec, rec, f1 = metrics(truth, guesses)
lab.show(viz.table(
    ["metric", "value"],
    [("accuracy", f"{acc0:.3f}"),
     ("precision", f"{prec:.3f}"),
     ("recall", f"{rec:.3f}"),
     ("F1", f"{f1:.3f}")]))
lab.check_close("accuracy counts the four right answers", acc0, 0.75)
lab.check_close("precision is 3/4", prec, 0.75)
lab.check_close("recall is 3/4", rec, 0.75)
lab.note("One false positive (index 4) costs precision; one false negative "
         "(index 2) costs recall.")


# ===========================================================================
# 8. Sigmoid models
# ===========================================================================
lab.section("8. Sigmoid models")

lab.step("Turn a real number into a probability with the logistic function.")
lab.show(viz.table(
    ["z", "sigmoid(z)"],
    [(z, f"{sigmoid(z):.4f}") for z in (-4, -1, 0, 1, 4)]))
lab.check_close("sigmoid(0) is one half", sigmoid(0.0), 0.5)
lab.check("sigmoid is increasing", sigmoid(-1.0) < sigmoid(0.0) < sigmoid(1.0))
lab.note("A logistic-regression model is: z = w . x + b,  p = sigmoid(z).")
lab.note("The decision boundary is where p = 0.5, i.e. where z = 0 -- a "
         "straight line in feature space, even though p itself is curved.")


def logistic_fit(xs, ys, steps=6000, lr=0.4, lam=0.0):
    """Gradient descent on the binary log-loss."""
    n_features = len(xs[0])
    weights = [0.0] * n_features
    bias = 0.0
    losses = []
    for step in range(steps):
        rate = lr / (1.0 + step / 2000.0)
        total = 0.0
        grad_w = [0.0] * n_features
        grad_b = 0.0
        for x, y in zip(xs, ys):
            p = sigmoid(dot(weights, x) + bias)
            total += log_loss(y, p)
            delta = (p - y)
            for j in range(n_features):
                grad_w[j] += delta * x[j]
            grad_b += delta
        n = len(xs)
        losses.append(total / n)
        weights = [w - rate * (g / n + lam * w) for w, g in zip(weights, grad_w)]
        bias -= rate * grad_b / n
    return weights, bias, losses


def design_rows(rows, degree, means=None, sds=None):
    raw = [polynomial_features(r, degree) for r in rows]
    if means is None:
        return standardize(raw)
    scaled = [[(row[j] - means[j]) / sds[j] for j in range(len(row))] for row in raw]
    return scaled, means, sds


# The linear model on raw features is hopeless on concentric rings; the
# quadratic one works -- exactly like section 6.
Xlin_tr, mu_lin, sd_lin = design_rows(train, 1)
Xlin_te, _, _ = design_rows(test, 1, mu_lin, sd_lin)
Ytr = [float(r[2]) for r in train]
Yte = [int(r[2]) for r in test]

lw_lin, lb_lin, _ = logistic_fit(Xlin_tr, Ytr, steps=4000, lr=0.2)
lin_guesses = [1 if sigmoid(dot(lw_lin, x) + lb_lin) >= 0.5 else 0 for x in Xlin_te]
lin_acc = metrics(Yte, lin_guesses)[0]

Xq_tr, mu_q, sd_q = design_rows(train, 2)
Xq_te, _, _ = design_rows(test, 2, mu_q, sd_q)
lw, lb, lloss = logistic_fit(Xq_tr, Ytr, steps=6000, lr=0.4)
guesses = [1 if sigmoid(dot(lw, x) + lb) >= 0.5 else 0 for x in Xq_te]
acc, prec, rec, f1 = metrics(Yte, guesses)

lab.show(viz.table(
    ["quantity", "value"],
    [("log-loss at step 0", f"{lloss[0]:.4f}"),
     ("log-loss at the end", f"{lloss[-1]:.4f}"),
     ("test accuracy, linear features", f"{lin_acc:.3f}"),
     ("test accuracy, quadratic features", f"{acc:.3f}")]))
lab.check("the log-loss went down", lloss[-1] < lloss[0])
lab.check("the linear model is no better than chance", lin_acc < 0.7)
lab.check("the quadratic model classifies the test set well", acc > 0.9)
lab.show(viz.table(
    ["metric", "on the held-out test set"],
    [("accuracy", f"{acc:.3f}"),
     ("precision", f"{prec:.3f}"),
     ("recall", f"{rec:.3f}"),
     ("F1", f"{f1:.3f}")]))
lab.note("The log-loss is the same 'surprise' measure as the entropy in "
         "section 10 of the course: -log p is how many bits of surprise the "
         "model assigned to the answer it got wrong.")


# ===========================================================================
# 9. Regularization 1
# ===========================================================================
lab.section("9. Regularization 1")

lab.step("Regularization adds a penalty for large weights to the loss.")
lab.show("""
    L2 (ridge):  loss + (lambda / 2) * ||w||^2
    L1 (lasso):  loss + lambda * ||w||_1
""")
lab.note("L2 shrinks every weight smoothly towards zero.  L1 can drive some "
         "weights exactly to zero, which is how lasso does feature selection.")

lab.step("Same data, same model, different lambda.")
rows = []
for lam in (0.0, 0.001, 0.01, 0.1, 1.0):
    w_, b_, ls_ = logistic_fit(Xq_tr, Ytr, steps=6000, lr=0.4, lam=lam)
    g_ = [1 if sigmoid(dot(w_, x) + b_) >= 0.5 else 0 for x in Xq_te]
    a_ = metrics(Yte, g_)[0]
    norm = math.sqrt(sum(v * v for v in w_))
    rows.append((lam, f"{ls_[-1]:.4f}", f"{norm:.4f}", f"{a_:.3f}"))
lab.show(viz.table(
    ["lambda", "training log-loss", "||w||", "test accuracy"], rows))
lab.check("a bigger lambda shrinks the weights",
          float(rows[-1][2]) < float(rows[0][2]))
lab.check("the unregularized model has the lowest training loss",
          float(rows[0][1]) <= float(rows[-1][1]) + 1e-9)
lab.note("Notice the trade-off: every extra bit of shrinkage buys a lower "
         "training loss *penalty* at the price of a worse fit.  The right "
         "lambda is chosen on a validation set, never on the test set.")


# ===========================================================================
# 10. Regularization 2
# ===========================================================================
lab.section("10. Regularization 2")

lab.step("L1 versus L2 on a dataset with one useless feature.")
lab.note("Add a third feature that is pure noise -- the model should learn "
         "to ignore it, and regularization helps it do so.")

rng = random.Random(99)
noisy_train = [(r[0], r[1], rng.gauss(0, 2.0), r[2]) for r in train]
noisy_test = [(r[0], r[1], rng.gauss(0, 2.0), r[2]) for r in test]
Xtr3 = [polynomial_features(r, 2) + [r[2]] for r in noisy_train]
Xte3 = [polynomial_features(r, 2) + [r[2]] for r in noisy_test]
mu3 = [sum(r[j] for r in Xtr3) / len(Xtr3) for j in range(len(Xtr3[0]))]
sd3 = [math.sqrt(sum((r[j] - mu3[j]) ** 2 for r in Xtr3) / len(Xtr3))
       or 1.0 for j in range(len(Xtr3[0]))]
Xtr3s = [[(r[j] - mu3[j]) / sd3[j] for j in range(len(r))] for r in Xtr3]
Xte3s = [[(r[j] - mu3[j]) / sd3[j] for j in range(len(r))] for r in Xte3]
Ytr3 = [float(r[3]) for r in noisy_train]
Yte3 = [int(r[3]) for r in noisy_test]


def l1_logistic_fit(xs, ys, steps=6000, lr=0.4, lam=0.02):
    """Logistic regression with an L1 penalty (sub-gradient descent)."""
    n_features = len(xs[0])
    weights = [0.0] * n_features
    bias = 0.0
    for step in range(steps):
        rate = lr / (1.0 + step / 2000.0)
        grad_w = [0.0] * n_features
        grad_b = 0.0
        for x, y in zip(xs, ys):
            p = sigmoid(dot(weights, x) + bias)
            delta = p - y
            for j in range(n_features):
                grad_w[j] += delta * x[j]
            grad_b += delta
        n = len(xs)
        weights = [w - rate * (g / n + lam * (1 if w > 0 else (-1 if w < 0 else 0)))
                   for w, g in zip(weights, grad_w)]
        bias -= rate * grad_b / n
    return weights, bias


rows = []
w_none, b_none = logistic_fit(Xtr3s, Ytr3, steps=6000, lr=0.4)[:2]
w_l2, b_l2 = logistic_fit(Xtr3s, Ytr3, steps=6000, lr=0.4, lam=0.02)[:2]
w_l1, b_l1 = l1_logistic_fit(Xtr3s, Ytr3, steps=6000, lr=0.4, lam=0.02)
for name, (w_, b_) in (("none", (w_none, b_none)),
                       ("L2 (ridge)", (w_l2, b_l2)),
                       ("L1 (lasso)", (w_l1, b_l1))):
    g = [1 if sigmoid(dot(w_, x) + b_) >= 0.5 else 0 for x in Xte3s]
    a = metrics(Yte3, g)[0]
    rows.append((name, ", ".join(f"{v:+.4f}" for v in w_), f"{a:.3f}"))
lab.show(viz.table(
    ["regularizer", "weights (x, y, x^2, y^2, xy, noise)", "test accuracy"], rows))

noise_none = abs(float(rows[0][1].split(", ")[-1]))
noise_l2 = abs(float(rows[1][1].split(", ")[-1]))
noise_l1 = abs(float(rows[2][1].split(", ")[-1]))
lab.check("without regularization the model leans on the noise feature",
          noise_none > 0.5, f"noise weight = {noise_none:.4f}")
lab.check("L2 shrinks the noise weight but keeps it non-zero",
          0 < noise_l2 < noise_none, f"L2 noise weight = {noise_l2:.4f}")
lab.check("L1 drives the noise weight almost to zero",
          noise_l1 < noise_l2 / 3, f"L1 noise weight = {noise_l1:.4f}")
lab.note("L1's hallmark: the useless weight can be driven to exactly zero, "
         "so the model drops the feature entirely.")


# ===========================================================================
# 11. Machine learning libraries
# ===========================================================================
lab.section("11. Machine learning libraries")

lab.step("Everything above is ~50 lines.  scikit-learn does the same thing "
         "better, faster and with fewer bugs.")

lab.note("Your hand-written version:")
lab.show("""
    weights = [0.0] * n_features
    bias = 0.0
    for _ in range(steps):
        errors = [...]
        weights = [w - lr * g / n for w, g in zip(weights, grad_w)]
""")
lab.note("The library version:")
lab.show("""
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression().fit(X_train, y_train)
    model.predict(X_test)
""")

lab.step("Run the library version on exactly the same data.")
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score

    sk_model = LogisticRegression(max_iter=2000).fit(Xq_tr, Ytr)
    sk_guesses = [int(p) for p in sk_model.predict(Xq_te)]
    sk_acc = accuracy_score([int(y) for y in Yte], sk_guesses)
    lab.show(viz.table(
        ["model", "test accuracy"],
        [("our gradient descent", f"{acc:.3f}"),
         ("scikit-learn LogisticRegression", f"{sk_acc:.3f}")]))
    lab.check("our model is as good as the library's", abs(acc - sk_acc) < 0.06)
    lab.note("Same data, same model, same answer -- which is exactly what you "
             "want from a learning algorithm: the result is a property of the "
             "data, not of your code.")
except ImportError:                                   # pragma: no cover
    lab.note("scikit-learn is not installed; skipping the comparison.")
    lab.note("Install it with: pip install scikit-learn")


# ===========================================================================
# 12. Machine learning coding
# ===========================================================================
lab.section("12. Machine learning coding")

lab.step("Write a k-nearest-neighbour classifier from scratch -- the same "
         "algorithm section 17 replaces with a quantum circuit.")


def euclidean(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def knn_predict(train_rows, query, k=5):
    """Majority vote of the k closest training rows."""
    distances = sorted(
        ((euclidean(query[:2], row[:2]), row[2]) for row in train_rows),
        key=lambda pair: pair[0],
    )
    votes = [label for _, label in distances[:k]]
    ones = sum(1 for v in votes if v == 1)
    return 1 if ones * 2 > len(votes) else 0, distances[:k]


train2 = [(r[0], r[1], r[2]) for r in train]
test2 = [(r[0], r[1], r[2]) for r in test]
correct = 0
for row in test2:
    guess, _ = knn_predict(train2, row, k=5)
    correct += 1 if guess == row[2] else 0
knn_acc = correct / len(test2)
lab.show(viz.table(
    ["classifier", "test accuracy"],
    [("logistic regression, linear features", f"{lin_acc:.3f}"),
     ("logistic regression, quadratic features", f"{acc:.3f}"),
     ("k-nearest neighbours (k=5)", f"{knn_acc:.3f}")]))
lab.check("the hand-written KNN works", knn_acc > 0.9)

lab.step("K is a hyper-parameter -- and it has the same under/overfit story.")
rows = []
for k in (1, 3, 5, 11, 25, 51):
    c = 0
    for row in test2:
        guess, _ = knn_predict(train2, row, k=k)
        c += 1 if guess == row[2] else 0
    rows.append((k, f"{c / len(test2):.3f}"))
lab.show(viz.table(["k", "test accuracy"], rows))
lab.check("a small k works well here", float(rows[0][1]) > 0.9)
lab.check("a very large k washes the structure out",
          float(rows[-1][1]) < float(rows[0][1]),
          f"k={rows[0][0]} -> {rows[0][1]}, k={rows[-1][0]} -> {rows[-1][1]}")
lab.note("k=1 memorises individual points; k=51 averages over a quarter of "
         "the training set.  The same trade-off as polynomial degree in "
         "section 6.")


# ===========================================================================
# 13. Multi-layer network 1
# ===========================================================================
lab.section("13. Multi-layer network 1")

lab.step("A neural network is just layers of weighted sums with a "
         "non-linearity in between.")

lab.note("Layer 1: a1 = sigmoid(W1 . x + b1)")
lab.note("Layer 2: a2 = sigmoid(W2 . a1 + b2)")
lab.note("The non-linearity (the sigmoid) is what makes the stack more "
         "powerful than one linear layer.")


class TinyNet:
    """One hidden layer, sigmoid activations, trained by gradient descent."""

    def __init__(self, n_inputs, n_hidden, seed=3):
        rng = random.Random(seed)
        self.W1 = [[rng.uniform(-1, 1) for _ in range(n_inputs)]
                   for _ in range(n_hidden)]
        self.b1 = [rng.uniform(-0.1, 0.1) for _ in range(n_hidden)]
        self.W2 = [rng.uniform(-1, 1) for _ in range(n_hidden)]
        self.b2 = 0.0

    def forward(self, x):
        self.z1 = [dot(row, x) + b for row, b in zip(self.W1, self.b1)]
        self.a1 = [sigmoid(z) for z in self.z1]
        self.z2 = dot(self.W2, self.a1) + self.b2
        self.a2 = sigmoid(self.z2)
        return self.a2

    def backward(self, x, y, lr):
        """One gradient-descent step on the binary log-loss."""
        delta2 = self.a2 - y                    # dL/dz2 for sigmoid + log-loss
        for j in range(len(self.W2)):
            self.W2[j] -= lr * delta2 * self.a1[j]
        self.b2 -= lr * delta2
        for i in range(len(self.a1)):
            d = delta2 * self.W2[i] * self.a1[i] * (1 - self.a1[i])
            for j in range(len(x)):
                self.W1[i][j] -= lr * d * x[j]
            self.b1[i] -= lr * d

    def loss(self, xs, ys):
        return mean([log_loss(y, self.forward(x)) for x, y in zip(xs, ys)])


lab.step("Train the network on XOR -- the classic 'not linearly separable' "
         "problem.")
xor_x = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
xor_y = [0.0, 1.0, 1.0, 0.0]

net = TinyNet(2, 4, seed=5)
losses = []
for _ in range(4000):
    for x, y in zip(xor_x, xor_y):
        net.forward(x)
        net.backward(x, y, 0.5)
    losses.append(net.loss(xor_x, xor_y))

lab.show(viz.table(
    ["step", "log-loss"],
    [(0, f"{losses[0]:.4f}"),
     (500, f"{losses[500]:.4f}"),
     (2000, f"{losses[2000]:.4f}"),
     (3999, f"{losses[-1]:.4f}")]))
lab.check("the loss fell", losses[-1] < 0.2 * losses[0])

predictions = [int(net.forward(x) >= 0.5) for x in xor_x]
lab.show(viz.table(
    ["x1", "x2", "target", "network"],
    [[x[0], x[1], int(y), p] for x, y, p in zip(xor_x, xor_y, predictions)]))
lab.check("the network solves XOR", predictions == [0, 1, 1, 0])
lab.note("A single linear layer *cannot* do this -- the hidden layer's "
         "sigmoid bends the decision boundary.  This is the idea behind "
         "quantum neural networks in the wider literature (variational "
         "circuits are 'hidden layers' whose weights are trained the same "
         "way).")


# ===========================================================================
# 14. Bridge to quantum machine learning
# ===========================================================================
lab.section("14. Bridge to quantum machine learning")

lab.step("Everything in section 16 appears again in section 17 -- but two "
         "pieces get replaced by quantum circuits.")

lab.show(viz.table(
    ["classical piece", "used in", "quantum replacement in section 17"],
    [
        ("squared Euclidean distance", "k-NN",
         "a quantum circuit that overlaps amplitude-encoded states"),
        ("the kernel K(x, y)", "support vector machines",
         "a quantum feature map: |phi(x)> = U(x)|0>"),
    ]))

lab.step("The quantum KNN in one line of maths.")
lab.show("""
    classical:   w_i = 1 - 0.25 * d(x, x_i)^2 ,  P(c|x) = sum_{i in c} w_i / sum_i w_i
    quantum:     P(c|x) = |<psi_x|psi_c>|^2   with |psi> built by a quantum circuit
""")
lab.note("Both compute 'how close is x to the class c examples'.  The quantum "
         "version computes it by *interference* instead of by arithmetic.")
lab.note("That is the whole idea of quantum machine learning: replace one "
         "inner product with a quantum one, and the data is processed by "
         "quantum interference at the same time.")

lab.step("What you should be able to answer before starting section 17.")
for q in [
    "What are features, and why do you scale them?",
    "What is the loss, and what does gradient descent minimise?",
    "What is the difference between underfitting and overfitting?",
    "What does a sigmoid model output, and what is its decision boundary?",
    "What do L1 and L2 regularization do to the weights?",
    "What is a kernel, and why would you replace it with a quantum circuit?",
]:
    lab.note(f"  * {q}")


if __name__ == "__main__":
    sys.exit(lab.finish())
