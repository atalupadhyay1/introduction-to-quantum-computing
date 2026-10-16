# Section 16 — Machine Learning Foundation

> **Course section** 16 of 17 · **Lab** [`L16`](../labs/L16_machine_learning_foundation/lab.py) · **Quiz** 8 questions

## What you should be able to do

- Describe the structure of a machine-learning system and name the stages.
- Train a linear model with gradient descent and explain the learning rate.
- Diagnose underfitting and overfitting, and use a train/test split.
- Fit a logistic (sigmoid) model and use the log-loss.
- Explain what L1 and L2 regularization do, and why they differ.
- Write a one-hidden-layer neural network and its back-propagation.

## The lectures

| Lecture | What it covers |
|---|---|
| Introduction to Machine Learning | the three ingredients: data, model, loss |
| What Is AI? | AI ⊃ ML ⊃ DL, and where quantum ML fits |
| Structure of ML Systems | the pipeline from data collection to deployment |
| Learning with Models | parameters, and fitting them |
| Speed Up Learning | gradient descent, learning rate, feature scaling |
| Underfit and Overfit | bias, variance, and the train/test split |
| Classification | labels, decision boundaries, the confusion matrix |
| Sigmoid Models | logistic regression and the log-loss |
| Regularization 1 / 2 | L2 and L1, and what they do to the weights |
| Machine Learning Libraries | the same model in scikit-learn |
| Machine Learning Coding | a classifier written from scratch |
| Multi-Layer Network 1 | forward pass, sigmoid, back-propagation |

## The three ingredients

| Ingredient | What it is | Example in this course |
|---|---|---|
| data | examples with the right answers | two concentric rings |
| model | a family of functions with tunable knobs | $w \cdot x + b$ |
| loss | a number that says how wrong the model is | mean squared error |

Training means nudging the **parameters** until the loss stops falling. The
whole loop is:

```
data -> features -> model -> predictions -> loss
  ^                                      |
  +--------- update the parameters ------+
```

## Learning with models

The simplest model with learnable parameters is a line,
$\hat y = w \cdot x + b$. Gradient descent on the mean squared error does

$$
w \leftarrow w - \eta\, \frac{\partial L}{\partial w}
$$

where $\eta$ is the learning rate. Too small and you crawl; too large and
you overshoot and diverge.

**Feature scaling** is the single biggest speed-up. If one feature is
measured in millimetres and another in kilometres, the gradient is
dominated by the big one, and the same learning rate that converges on
scaled features will *explode* on unscaled ones. The standard fix is
standardization: subtract the mean, divide by the standard deviation.

## Underfitting and overfitting

The lab's dataset is two concentric rings — the classic case where a
straight line cannot do better than chance:

| model | train accuracy | test accuracy |
|---|---|---|
| linear | 0.587 | 0.500 |
| quadratic (adds $x^2, y^2, xy$) | 0.980 | 0.960 |

Underfitting is **high bias**: the model is too simple to capture the
pattern. Overfitting is **high variance**: the model is so flexible that it
memorises noise. The lab makes the overfitting curve visible by fitting
$\sin(2\pi x) + \text{noise}$ with polynomials of increasing degree using
only 10 of 20 points:

| degree | train RMSE | test RMSE |
|---|---|---|
| 1 | 0.5538 | 0.5220 |
| 3 | 0.1237 | 0.1946 |
| 5 | 0.0840 | 0.1870 |
| 7 | 0.0463 | 0.3148 |
| 9 | 0.0337 | 0.4537 |
| 12 | 0.0338 | 0.5365 |

The training error falls monotonically; the test error has a minimum and
then turns back up. **Only a held-out test set can tell you where the
sweet spot is.**

## Classification and the sigmoid

A logistic-regression model outputs a probability:

$$
z = w \cdot x + b, \qquad p = \sigma(z) = \frac{1}{1 + e^{-z}}
$$

The decision boundary is where $p = 0.5$, i.e. where $z = 0$ — a *straight
line* in feature space, even though $p$ itself is curved. The loss is the
**log-loss** (binary cross-entropy):

$$
L = -\bigl[y\log p + (1-y)\log(1-p)\bigr]
$$

which is the same "surprise" measure as the entropy in section 10: $-\log p$
is how many bits of surprise the model assigned to the answer it got wrong.

Accuracy alone is not enough. The confusion matrix gives precision
($TP/(TP+FP)$), recall ($TP/(TP+FN)$) and $F_1$.

## Regularization

Add a penalty for large weights:

$$
\begin{aligned}
\text{L2 (ridge):}\quad & L + \frac{\lambda}{2}\lVert w\rVert^2\\
\text{L1 (lasso):}\quad & L + \lambda \lVert w\rVert_1
\end{aligned}
$$

L2 shrinks every weight smoothly. L1 can drive some weights *exactly* to
zero, which is how lasso performs feature selection. On the lab's data
with one pure-noise feature:

| regularizer | weight on the noise feature |
|---|---|
| none | 0.8386 |
| L2 (ridge) | 0.3474 |
| L1 (lasso) | 0.0561 |

## Neural networks

One hidden layer with sigmoid activations:

$$
a_1 = \sigma(W_1 x + b_1), \qquad a_2 = \sigma(W_2 a_1 + b_2)
$$

The non-linearity is the point: stacking *linear* layers still gives a
linear model. The lab trains such a network on **XOR** — a problem no
single linear layer can solve — and it converges to the right answers.

This is the idea behind quantum neural networks in the wider literature: a
variational circuit is a hidden layer whose weights are trained the same
way.

## Try it yourself

```bash
python labs/L16_machine_learning_foundation/lab.py
```

## Self-check

- [ ] Can you name the three ingredients and the seven stages of an ML
      system?
- [ ] Can you explain, with an example, why feature scaling matters for
      gradient descent?
- [ ] Do you know the difference between high bias and high variance, and
      how you tell them apart?
- [ ] Can you write the log-loss and say what $-\log p$ means?
- [ ] Can you explain the difference between L1 and L2 in one sentence?
- [ ] Have you run `python labs/L16_machine_learning_foundation/lab.py`?

## Where to go next

Section 17 — [Quantum Machine Learning with Qiskit](17-quantum-ml.md). Now
replace the distance and the kernel with quantum circuits.
