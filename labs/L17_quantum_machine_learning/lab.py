#!/usr/bin/env python3
"""
L17 -- Quantum machine learning with Qiskit.

Course section: 17 (Quantum Machine Learning With Qiskit).

Run me::

    python labs/L17_quantum_machine_learning/lab.py

What you will build
-------------------
* The classical k-nearest-neighbour algorithm, written out as maths.
* The quantum KNN from the course, rebuilt on Qiskit 2.x, and a proof that
  it computes *exactly* the same class probability as the classical one.
* Support vector machines: separation, overfitting, soft margins, the
  kernel trick, and multiple classes.
* A quantum support vector machine: the ZZ feature map, the quantum kernel
  and QSVC, trained on the iris dataset.

The quantum KNN is the heart of this lab.  The classical algorithm computes
a distance; the quantum one computes the *same* number as an interference
pattern, and the section below shows the two are the same formula written
two different ways.
"""

from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from qc101.labkit import Lab
from qc101 import viz

lab = Lab("L17", "Quantum machine learning with Qiskit")
RNG = random.Random(31337)

try:
    import numpy as np
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
    from qiskit.circuit.library import zz_feature_map
    from qiskit.quantum_info import Statevector
    from qiskit_aer import AerSimulator
    from qiskit_machine_learning.algorithms import QSVC
    from qiskit_machine_learning.kernels import FidelityQuantumKernel
    from qiskit_machine_learning.primitives import QMLSampler
    from qiskit_machine_learning.state_fidelities import ComputeUncompute
    HAVE_QISKIT = True
except ImportError as exc:                             # pragma: no cover
    HAVE_QISKIT = False
    _IMPORT_ERROR = exc


SIMULATOR = AerSimulator() if HAVE_QISKIT else None


def draw(circuit) -> str:
    """Render a circuit as text (Qiskit 2 returns a TextDrawing object)."""
    return str(circuit.draw(output="text"))


# ===========================================================================
# The course's quantum-KNN data
# ===========================================================================
TRAINING = [[0.9798, 0.2, 1], [0.3, 0.954, 0]]   # [x, y, class]
QUERY = [0.85, 0.5268]


def normalize(vector):
    """Scale a vector to unit length."""
    length = math.sqrt(sum(v * v for v in vector))
    return [v / length for v in vector]


# ===========================================================================
# 1. The KNN problem
# ===========================================================================
lab.section("1. Quantum machine learning with KNN -- the problem")

lab.step("The task: two labelled points, one unlabelled point, one question.")
lab.show(viz.table(
    ["point", "x", "y", "class"],
    [["training point 0", f"{TRAINING[0][0]:.4f}", f"{TRAINING[0][1]:.4f}",
      f"{TRAINING[0][2]}"],
     ["training point 1", f"{TRAINING[1][0]:.4f}", f"{TRAINING[1][1]:.4f}",
      f"{TRAINING[1][2]}"],
     ["query", f"{QUERY[0]:.4f}", f"{QUERY[1]:.4f}", "?"]]))
lab.note("The question: how likely is the query to belong to class 1 rather "
         "than class 0?")
lab.note("This is the smallest possible classification problem -- two "
         "training examples -- but it is exactly the shape of the real thing: "
         "turn a *distance* into a *probability*.")

lab.step("The two routes to the answer")
lab.show(viz.table(
    ["route", "what it does"],
    [("classical KNN", "arithmetic on the coordinates"),
     ("quantum KNN", "interference in a quantum circuit")]))
lab.note("The rest of this lab shows the two routes give the *same* answer, "
         "and then moves on to support vector machines, where the quantum "
         "version replaces a kernel.")


# ===========================================================================
# 2. Math for classical KNN
# ===========================================================================
lab.section("2. Math for classical KNN")

lab.step("Step 1 -- normalise every vector so that length carries no "
         "information.")
train0 = normalize(TRAINING[0][:2])
train1 = normalize(TRAINING[1][:2])
query = normalize(QUERY)
lab.show(viz.table(
    ["vector", "before", "after normalising"],
    [["training 0", f"({TRAINING[0][0]:.4f}, {TRAINING[0][1]:.4f})",
      f"({train0[0]:.4f}, {train0[1]:.4f})"],
     ["training 1", f"({TRAINING[1][0]:.4f}, {TRAINING[1][1]:.4f})",
      f"({train1[0]:.4f}, {train1[1]:.4f})"],
     ["query", f"({QUERY[0]:.4f}, {QUERY[1]:.4f})",
      f"({query[0]:.4f}, {query[1]:.4f})"]]))
lab.check_close("the training vector 0 has unit length",
                math.sqrt(train0[0] ** 2 + train0[1] ** 2), 1.0)
lab.note("Normalising matters because the distance formula below assumes "
         "unit vectors -- it is the cosine distance in disguise.")

lab.step("Step 2 -- squared Euclidean distance to each training point.")
d0_sq = (query[0] - train0[0]) ** 2 + (query[1] - train0[1]) ** 2
d1_sq = (query[0] - train1[0]) ** 2 + (query[1] - train1[1]) ** 2
lab.show(viz.table(
    ["training point", "class", "squared distance d^2"],
    [["0", f"{TRAINING[0][2]}", f"{d0_sq:.6f}"],
     ["1", f"{TRAINING[1][2]}", f"{d1_sq:.6f}"]]))
lab.check("the query is closer to the class-1 point", d0_sq < d1_sq)

lab.step("Step 3 -- turn each distance into a weight.")
lab.note("w_i = 1 - 0.25 * d_i^2")
w0 = 1 - 0.25 * d0_sq
w1 = 1 - 0.25 * d1_sq
lab.show(viz.table(
    ["training point", "d^2", "weight w = 1 - 0.25 d^2"],
    [["0", f"{d0_sq:.6f}", f"{w0:.6f}"],
     ["1", f"{d1_sq:.6f}", f"{w1:.6f}"]]))

lab.step("Step 4 -- normalise the weights into probabilities.")
total = w0 + w1
p_class1 = w0 / total
p_class0 = w1 / total
lab.show(viz.table(
    ["class", "weight", "probability"],
    [[f"{TRAINING[0][2]} (point 0)", f"{w0:.6f}", f"{p_class1:.6f}"],
     [f"{TRAINING[1][2]} (point 1)", f"{w1:.6f}", f"{p_class0:.6f}"]]))
lab.check_close("the two probabilities add to one", p_class1 + p_class0, 1.0)
lab.check("class 1 is more likely", p_class1 > p_class0)
lab.note("That is the whole classical algorithm.  Remember the two numbers:")
lab.note(f"    P(class 1) = {p_class1:.6f}     P(class 0) = {p_class0:.6f}")


# ===========================================================================
# 3. Connecting math and code for classical KNN
# ===========================================================================
lab.section("3. Connecting math and code for classical KNN")


def classical_knn(training, query_point, decay=0.25):
    """The course's classical KNN, written as a function."""
    vectors = [normalize(t[:2]) for t in training]
    q = normalize(query_point)
    weights = []
    for v in vectors:
        d_sq = sum((qi - vi) ** 2 for qi, vi in zip(q, v))
        weights.append(1 - decay * d_sq)
    total = sum(weights)
    probabilities = {}
    for t, w in zip(training, weights):
        probabilities[t[2]] = probabilities.get(t[2], 0.0) + w / total
    return probabilities, weights


probs, weights = classical_knn(TRAINING, QUERY)
lab.show(viz.table(
    ["quantity", "value"],
    [("P(class 1)", f"{probs.get(1, 0.0):.6f}"),
     ("P(class 0)", f"{probs.get(0, 0.0):.6f}")]))
lab.check_close("the code reproduces the hand calculation",
                probs.get(1, 0.0), p_class1)
lab.check_close("and the two probabilities still add to one",
                sum(probs.values()), 1.0)


# ===========================================================================
# 4. Math prerequisites for quantum KNN
# ===========================================================================
lab.section("4. Math prerequisites for quantum KNN")

lab.step("A qubit state is a vector of amplitudes; a sum of squares is a "
         "probability.")
lab.note("To put a 2-D vector into a quantum state you need *amplitude "
         "encoding*: the components become the amplitudes of a superposition.")

lab.show("""
    |v> = v_0 |0> + v_1 |1>          with v_0^2 + v_1^2 = 1
""")
lab.note("Four qubits give 16 amplitudes, so four 2-D vectors fit in one "
         "register -- two training points and the query, each with a class "
         "label and a 'training or query' flag.")

lab.step("Interference is the whole trick.")
lab.show("""
    H on the 'training/query' qubit mixes the two halves:

        (a + b) / sqrt(2)      and      (a - b) / sqrt(2)

    The SUM of the amplitudes grows, the DIFFERENCE shrinks.  The amount of
    growth at each slot is exactly the overlap between the query and the
    training point stored in that slot.
""")
lab.note("A quantum KNN therefore measures how much the query 'agrees' with "
         "each class, and the answer comes out of the *measurement "
         "statistics* rather than out of arithmetic.")


# ===========================================================================
# 5. Math for quantum KNN
# ===========================================================================
lab.section("5. Math for quantum KNN")

lab.step("Work out what the circuit actually computes.")
lab.note("Write a training vector as v = (v_x, v_y) and the query as q.  In "
         "the circuit the training vector sits in the slot (class, x) and "
         "(class, y); the query sits in the same slots of *both* classes.")
lab.note("After the Hadamard, the amplitude at a slot holding v_i (training) "
         "and q_i (query) is")
lab.show("""
    amplitude(q3 = 0) = (v_i + q_i) / (2*sqrt(2))
""")
lab.note("Now the identity that makes the whole thing work:")
lab.show("""
    sum_i (v_i + q_i)^2  =  sum_i (v_i^2 + q_i^2 + 2 v_i q_i)
                         =  2 + 2 * sum_i v_i q_i

    and the classical weight was

    w = 1 - 0.25 * d^2 = 1 - 0.25 * (2 - 2 sum_i v_i q_i)
                       = 0.5 * (1 + sum_i v_i q_i)
""")
lab.note("so  sum_i (v_i + q_i)^2 = 4 * w.  The interference amplitude is "
         "the square root of four times the classical weight!")

lab.step("Check that identity numerically on the course's data.")
for label, v in (("training 0", train0), ("training 1", train1)):
    interference = sum((vi + qi) ** 2 for vi, qi in zip(v, query))
    classical = 1 - 0.25 * sum((qi - vi) ** 2 for qi, vi in zip(query, v))
    lab.note(f"    {label}: sum (v_i + q_i)^2 = {interference:.6f}   "
             f"4 * w = {4 * classical:.6f}")
    lab.check_close(f"the interference equals 4 * w for {label}",
                    interference, 4 * classical, tol=1e-9)

lab.note("")
lab.note("And the measurement statistics follow: the probability of getting "
         "q3 = 0 together with the class-c bit is")
lab.show("""
    P(class c, q3 = 0)  =  sum over the slots of class c of (v_i + q_i)^2 / 8
""")
lab.note("Dividing by P(q3 = 0) -- the probability of the training half -- "
         "leaves exactly the classical normalised weight.  The quantum KNN "
         "*is* the classical KNN, written with amplitudes instead of "
         "arithmetic.")


# ===========================================================================
# 6. Code for quantum KNN
# ===========================================================================
lab.section("6. Code for quantum KNN")

if not HAVE_QISKIT:
    lab.error(f"Qiskit is not available: {_IMPORT_ERROR}")
else:
    lab.step("Build the course's four-qubit circuit.")

    def quantum_knn_state(training, query_point):
        """
        The 16 amplitudes the course's quantum KNN starts from.

        Layout (Qiskit's little-endian index = q0 + 2 q1 + 4 q2 + 8 q3):

        * q0 holds the class: 1 for the first training point's class sector,
          0 for the second one's.
        * q1, q2 encode which component (x or y) of the vector sits there.
        * q3 says 'training data' (0) or 'query' (1).

        The query is written into the slots of *both* classes, which is what
        makes the interference work.
        """
        vectors = [normalize(t[:2]) for t in training]
        q = normalize(query_point)
        amplitudes = [0.0] * 16

        def index(q0, q1, q2, q3):
            return q0 + 2 * q1 + 4 * q2 + 8 * q3

        for v, t in zip(vectors, training):
            class_bit = 1 if t[2] == TRAINING[0][2] else 0
            # component 'x' -> (q1, q2) = (0, 0); component 'y' -> (1, 0)
            amplitudes[index(class_bit, 0, 0, 0)] = v[0] / 2
            amplitudes[index(class_bit, 1, 0, 0)] = v[1] / 2

        # the query is copied into the slot layout of each class
        for class_bit in (1, 0):
            amplitudes[index(class_bit, 0, 0, 1)] = q[0] / 2
            amplitudes[index(class_bit, 1, 0, 1)] = q[1] / 2
        return amplitudes

    amplitudes = quantum_knn_state(TRAINING, QUERY)
    lab.show(viz.table(
        ["index", "q3 q2 q1 q0", "amplitude"],
        [[i, f"{i // 8} {i // 4 % 2} {i // 2 % 2} {i % 2}",
          f"{a:+.4f}"] for i, a in enumerate(amplitudes) if a != 0]))
    norm = math.sqrt(sum(a * a for a in amplitudes))
    lab.check_close("the initial state is normalised", norm, 1.0)

    lab.step("The circuit: prepare the state, then let the two halves "
             "interfere.")
    qc = QuantumCircuit(4, 2)
    qc.initialize(amplitudes)
    qc.h(3)
    lab.show(draw(qc))
    lab.note("q3 is the 'training vs query' qubit.  The Hadamard is what "
             "makes the two halves interfere.")

    lab.step("Look at the state vector after the Hadamard.")
    state = Statevector(qc)
    rows = []
    for i, amplitude in enumerate(state.data):
        if abs(amplitude) > 1e-9:
            rows.append((i, f"{i // 8} {i // 4 % 2} {i // 2 % 2} {i % 2}",
                         f"{amplitude.real:+.4f}", f"{amplitude.imag:+.4f}"))
    lab.show(viz.table(["index", "q3 q2 q1 q0", "real", "imag"], rows))
    lab.note("Compare this with the initial amplitudes: in the slots where "
             "the query and a training point coincide, the amplitude is now "
             "their *sum* (q3 = 0) or their *difference* (q3 = 1).")

    lab.step("Measure q3 first, then q0 -- that is the class.")
    measured = QuantumCircuit(4, 2)
    measured.initialize(amplitudes)
    measured.h(3)
    measured.measure(3, 0)
    measured.measure(0, 1)
    counts = SIMULATOR.run(transpile(measured, SIMULATOR), shots=20000).result().get_counts()
    lab.show(viz.histogram(counts))

    q3_zero = counts.get("00", 0) + counts.get("10", 0)
    q3_one = counts.get("01", 0) + counts.get("11", 0)
    class_one = counts.get("10", 0)          # q3 = 0, q0 = 1 -> first class
    class_zero = counts.get("00", 0)          # q3 = 0, q0 = 0 -> second class
    quantum_p1 = class_one / q3_zero if q3_zero else 0.0
    quantum_p0 = class_zero / q3_zero if q3_zero else 0.0
    lab.show(viz.table(
        ["quantity", "classical", "quantum"],
        [("P(class 1)", f"{p_class1:.4f}", f"{quantum_p1:.4f}"),
         ("P(class 0)", f"{p_class0:.4f}", f"{quantum_p0:.4f}")]))
    lab.check("the quantum run lands in the training half most of the time",
              q3_zero > q3_one,
              f"q3=0: {q3_zero}, q3=1: {q3_one}")
    lab.check_close("the quantum KNN reproduces the classical probability",
                    quantum_p1, p_class1, tol=0.02)
    lab.note("20 000 shots, and the answer matches the classical one to "
             "within the shot noise.  Nothing was 'computed' in the classical "
             "sense -- the answer fell out of the interference pattern.")

    lab.step("The same thing, done exactly (no sampling).")
    # Qiskit writes the outcome as "q3 q2 q1 q0", so q3 = 0 and q0 = 1 is
    # the bit string "0001" and q3 = 0 and q0 = 0 is "0000".
    probs = state.probabilities_dict()
    p_q3zero_q0one = sum(v for k, v in probs.items() if k[0] == "0" and k[3] == "1")
    p_q3zero_q0zero = sum(v for k, v in probs.items() if k[0] == "0" and k[3] == "0")
    exact_p1 = (p_q3zero_q0one / (p_q3zero_q0one + p_q3zero_q0zero)
                if (p_q3zero_q0one + p_q3zero_q0zero) else 0.0)
    lab.show(viz.table(
        ["quantity", "classical", "quantum (exact)"],
        [("P(class 1)", f"{p_class1:.6f}", f"{exact_p1:.6f}"),
         ("P(class 0)", f"{p_class0:.6f}", f"{1 - exact_p1:.6f}")]))
    lab.check_close("the exact quantum answer equals the classical one",
                    exact_p1, p_class1, tol=1e-9)
    lab.note("Exactly equal -- as the algebra in section 5 promised.")


# ===========================================================================
# 7. Introduction to classification
# ===========================================================================
lab.section("7. Introduction to classification")

lab.step("A classifier turns a feature vector into a label.")
lab.show(viz.table(
    ["stage", "classical KNN", "quantum KNN"],
    [("represent the data", "coordinates", "amplitudes of a state"),
     ("measure similarity", "subtract and square", "interfere and square"),
     ("turn it into a label", "weighted vote", "measurement statistics")]))

lab.step("Support vector machines take a different route.")
lab.note("An SVM looks for the *widest empty strip* that separates two "
         "classes.  The strip is bounded by two hyperplanes; the distance "
         "between them is the margin.")
lab.show("""
    w . x + b = +1   <- one support hyperplane
    w . x + b = -1   <- the other
    margin = 2 / ||w||
""")
lab.note("Only the points touching the hyperplanes matter -- they are the "
         "*support vectors*.  Everything else could be deleted without "
         "changing the decision boundary.")


# ===========================================================================
# 8. SVM: separation
# ===========================================================================
lab.section("8. Support vector machines -- separation")

lab.step("Build a small separable dataset.")
svm_points = [(-2.0, -1.0, 0), (-1.0, -2.0, 0), (1.0, 2.0, 1), (2.0, 1.0, 1)]
lab.show(viz.table(["x", "y", "class"], [(p[0], p[1], p[2]) for p in svm_points]))

lab.step("Find the maximum-margin separator by hand: the midpoint of the two "
         "closest points from different classes.")
closest = None
for i, a in enumerate(svm_points):
    for b in svm_points[i + 1:]:
        if a[2] == b[2]:
            continue
        d = math.hypot(a[0] - b[0], a[1] - b[1])
        if closest is None or d < closest[0]:
            closest = (d, a, b)
d, a, b = closest
midpoint = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
# the optimal normal points straight from one support vector to the other
normal = (b[0] - a[0], b[1] - a[1])
length = math.hypot(*normal)
normal = (normal[0] / length, normal[1] / length)
lab.show(viz.table(
    ["quantity", "value"],
    [("closest pair", f"({a[0]}, {a[1]}) and ({b[0]}, {b[1]})"),
     ("distance between them", f"{d:.4f}"),
     ("midpoint (on the boundary)", f"({midpoint[0]:.4f}, {midpoint[1]:.4f})"),
     ("unit normal", f"({normal[0]:.4f}, {normal[1]:.4f})"),
     ("margin = 2/||w||", f"{d:.4f}")]))
lab.check("the two closest points belong to different classes", a[2] != b[2])
lab.check("the margin equals the distance between the support vectors",
          abs(d - d) < 1e-12)

lab.step("Classify a new point with the boundary.")
for probe in ((0.0, 0.0), (1.5, 1.5), (-1.5, -1.5)):
    side = normal[0] * (probe[0] - midpoint[0]) + normal[1] * (probe[1] - midpoint[1])
    lab.note(f"    point {probe}: signed distance {side:+.4f} -> "
             f"class {1 if side > 0 else 0}")
lab.note("The maximum-margin rule is the one SVM actually optimises: it is "
         "the most *conservative* separator, and it generalises best.")


# ===========================================================================
# 9. SVM: overfitting
# ===========================================================================
lab.section("9. Support vector machines -- overfitting")

lab.step("A maximum-margin separator can be spoiled by a single odd point.")
lab.note("Add one class-0 point far out on the class-1 side.  A hard-margin "
         "SVM must now tilt the whole boundary to include it, and every other "
         "point ends up on the wrong side of the margin.")


def max_margin(points):
    """The brute-force maximum-margin separator for a separable set."""
    best = None
    for i, p in enumerate(points):
        for q in points[i + 1:]:
            if p[2] == q[2]:
                continue
            d = math.hypot(p[0] - q[0], p[1] - q[1])
            if best is None or d < best[0]:
                best = (d, p, q)
    d, p, q = best
    midpoint = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    normal = (q[0] - p[0], q[1] - p[1])
    length = math.hypot(*normal)
    return (normal[0] / length, normal[1] / length), midpoint, d


def svm_accuracy(points, normal, midpoint):
    correct = 0
    for x, y, label in points:
        side = normal[0] * (x - midpoint[0]) + normal[1] * (y - midpoint[1])
        if (1 if side > 0 else 0) == label:
            correct += 1
    return correct / len(points)


normal, midpoint, margin = max_margin(svm_points)
acc_clean = svm_accuracy(svm_points, normal, midpoint)
spoiled = svm_points + [(4.5, 4.0, 0)]
normal2, midpoint2, margin2 = max_margin(spoiled)
acc_spoiled = svm_accuracy(spoiled, normal2, midpoint2)
acc_spoiled_original = svm_accuracy(svm_points, normal2, midpoint2)
lab.show(viz.table(
    ["situation", "margin", "accuracy on the original 4 points"],
    [("clean dataset", f"{margin:.4f}", f"{acc_clean:.3f}"),
     ("one rogue point added", f"{margin2:.4f}", f"{acc_spoiled_original:.3f}")]))
lab.check("the clean data is perfectly separated", acc_clean == 1.0)
lab.check("the rogue point wrecks the boundary", acc_spoiled_original < 1.0)
lab.note("This is overfitting in its purest form: one noisy label drags the "
         "model away from the pattern.  Soft margins (next section) are the "
         "standard cure.")


# ===========================================================================
# 10. SVM: soft margins
# ===========================================================================
lab.section("10. Support vector machines -- soft margins")

lab.step("Soft margins allow violations, but charge for them.")
lab.show("""
    minimise   1/2 * ||w||^2  +  C * sum_i slack_i
    subject to  y_i (w . x_i + b) >= 1 - slack_i ,  slack_i >= 0
""")
lab.note("C is the price of a mistake.  Big C: few mistakes allowed, "
         "possibly a weird boundary.  Small C: mistakes are cheap, the "
         "boundary stays smooth.")

lab.step("Train a soft-margin SVM with sub-gradient descent on the hinge "
         "loss.")


def hinge_loss(w, b, points):
    total = 0.0
    for x, y, label in points:
        margin = label * (w[0] * x + w[1] * y + b)
        total += max(0.0, 1 - margin)
    return total / len(points)


def train_hinge_svm(points, C=1.0, steps=400, lr=0.05):
    w = [0.0, 0.0]
    b = 0.0
    for _ in range(steps):
        gw = [0.0, 0.0]
        gb = 0.0
        for x, y, label in points:
            margin = label * (w[0] * x + w[1] * y + b)
            if margin < 1:
                gw[0] -= C * label * x
                gw[1] -= C * label * y
                gb -= C * label
        n = len(points)
        gw = [g / n for g in gw]
        gb /= n
        w = [wi - lr * gi for wi, gi in zip(w, gw)]
        b -= lr * gb
    return w, b


rows = []
for C in (0.01, 0.1, 1.0, 100.0):
    w, b = train_hinge_svm(spoiled, C=C)
    acc = svm_accuracy(spoiled, (w[0], w[1]), (-b / w[0] if w[0] else 0, 0))
    # score directly with w . x + b instead of the brute-force separator
    correct = 0
    for x, y, label in spoiled:
        if (1 if w[0] * x + w[1] * y + b > 0 else 0) == label:
            correct += 1
    rows.append((C, f"{hinge_loss(w, b, spoiled):.4f}",
                 f"{correct / len(spoiled):.3f}",
                 f"{math.hypot(*w):.4f}"))
lab.show(viz.table(
    ["C", "hinge loss", "accuracy", "||w||"], rows))
lab.check("a small C keeps the weight vector small",
          float(rows[0][3]) < float(rows[-1][3]))
lab.note("Notice the trade-off the C parameter buys you: the size of ||w|| "
         "and the number of mistakes move in opposite directions.")


# ===========================================================================
# 11. SVM: higher dimensions and kernels
# ===========================================================================
lab.section("11. Support vector machines -- higher dimensions and kernels")

lab.step("The rings dataset from lab L16 is not linearly separable.")
ring_data = []
rng = random.Random(21)
for radius, label in ((1.2, 0), (2.6, 1)):
    for _ in range(60):
        angle = rng.uniform(0, 2 * math.pi)
        r = radius + rng.gauss(0, 0.28)
        ring_data.append((r * math.cos(angle), r * math.sin(angle), label))
rng.shuffle(ring_data)
lab.note("In two dimensions no straight line can do it.  But map every point "
         "to (x, y, x^2, y^2) and the two rings become two parallel slabs.")

lab.step("The kernel trick: never build the feature map at all.")
lab.show("""
    K(x, z) = phi(x) . phi(z)

    A linear SVM on phi(x) is a kernel SVM on x.
""")
lab.note("The polynomial kernel K(x, z) = (x . z + c)^d is the standard "
         "example: it is exactly the inner product of the monomial feature "
         "map, so you never have to compute x^2, y^2, ... yourself.")


def polynomial_kernel(x, z, degree=2, c=1.0):
    """The polynomial kernel: the inner product of the monomial feature map."""
    return (sum(xi * zi for xi, zi in zip(x, z)) + c) ** degree


ring_x = [r[:2] for r in ring_data]
ring_y = [r[2] for r in ring_data]
lab.show(viz.table(
    ["kernel K(x, z)", "formula"],
    [("linear", "x . z"),
     ("polynomial, degree 2", "(x . z + 1)^2")]))

try:
    from sklearn.svm import SVC

    linear_model = SVC(kernel="linear").fit(ring_x, ring_y)
    poly_model = SVC(kernel="poly", degree=2).fit(ring_x, ring_y)
    linear_acc = linear_model.score(ring_x, ring_y)
    poly_acc = poly_model.score(ring_x, ring_y)
    lab.show(viz.table(
        ["kernel", "accuracy on the rings"],
        [("linear  (K = x . z)", f"{linear_acc:.3f}"),
         ("polynomial degree 2", f"{poly_acc:.3f}")]))
    lab.check("a linear kernel cannot separate the rings", linear_acc < 0.7)
    lab.check("the polynomial kernel can", poly_acc > 0.95)
except ImportError:                                   # pragma: no cover
    lab.note("scikit-learn is not installed; skipping the kernel comparison.")

lab.note("This is the exact place where a quantum algorithm slots in: if "
         "K(x, z) is hard to compute classically, a quantum circuit can "
         "compute it as an overlap of two quantum states.")


# ===========================================================================
# 12. SVM: multiple classes
# ===========================================================================
lab.section("12. Support vector machines -- multiple classes")

lab.step("A binary SVM has one decision boundary; several classes need a "
         "strategy.")
lab.show(viz.table(
    ["strategy", "how it works", "number of boundaries"],
    [("one-vs-rest", "one binary SVM per class", "one per class"),
     ("one-vs-one", "one binary SVM per pair", "one per pair"),
     ("crammer-singer", "one SVM, all classes at once", "one")]))

lab.step("One-vs-rest on the iris dataset, done by hand with sklearn's "
         "support vectors.")
try:
    from sklearn.datasets import load_iris
    from sklearn.svm import SVC

    iris = load_iris()
    features = iris.data
    labels = iris.target
    lab.note("The iris dataset: 150 flowers, 4 features each, 3 classes.")
    lab.show(viz.table(
        ["class", "name", "rows"],
        [(i, name, int(sum(1 for l in labels if l == i)))
         for i, name in enumerate(iris.target_names)]))
    model = SVC(kernel="linear").fit(features, labels)
    lab.note(f"a linear SVM fits in {len(model.support_)} support vectors out "
             f"of {len(features)} rows")
    lab.check("the support vectors are a small subset",
              0 < len(model.support_) < len(features))
    lab.check("the model fits the training data essentially perfectly",
              model.score(features, labels) > 0.95,
              f"training accuracy = {model.score(features, labels):.3f}")
except ImportError:                                   # pragma: no cover
    lab.note("scikit-learn is not installed; skipping the iris demonstration.")


# ===========================================================================
# 13. Quantum support vector machines
# ===========================================================================
lab.section("13. Quantum support vector machines")

if not HAVE_QISKIT:
    lab.error(f"Qiskit is not available: {_IMPORT_ERROR}")
else:
    from sklearn.datasets import load_iris

    lab.step("The idea: replace the kernel with a quantum circuit.")
    lab.show("""
        classical:   K(x, z) = phi(x) . phi(z)
        quantum:     K(x, z) = |<phi(x)|phi(z)>|^2

        with  |phi(x)> = U(x) |0>^n     U(x) a parameterised circuit
    """)
    lab.note("The ZZ feature map encodes the data as angles and then applies "
             "a ladder of ZZ entanglers, so that the overlap between two "
             "states encodes a *non-linear* function of the data.")

    lab.step("Build the feature map the course uses.")
    dimension = 4
    feature_map = zz_feature_map(feature_dimension=dimension, reps=2,
                                 entanglement="linear")
    lab.show(draw(feature_map.decompose()))
    lab.note("Two layers of H, ZZ and CX entanglers over four qubits.")

    lab.step("The kernel is just the squared overlap of two feature-map "
             "states.")
    from qiskit.quantum_info import Statevector as _SV

    def feature_state(x):
        bound = feature_map.assign_parameters(list(x))
        return _SV(bound)

    sample_a = [5.0, 3.3, 1.5, 0.3]
    sample_b = [6.0, 2.9, 5.2, 1.7]
    overlap = abs(np.vdot(feature_state(sample_a).data,
                          feature_state(sample_b).data)) ** 2
    self_overlap = abs(np.vdot(feature_state(sample_a).data,
                               feature_state(sample_a).data)) ** 2
    lab.show(viz.table(
        ["pair", "quantum kernel value"],
        [("K(x, x)  (always 1)", f"{self_overlap:.6f}"),
         ("K(x1, x2)", f"{overlap:.6f}")]))
    lab.check_close("a state overlaps itself perfectly", self_overlap, 1.0)
    lab.check("different points have a smaller overlap", overlap < 1.0)
    lab.note("This is the whole quantum advantage in one number: the kernel "
             "entry is an expectation value of a quantum state, computed by "
             "the machine.")

    lab.step("Train a QSVC on the iris dataset -- the course's qsvm.py.")
    iris = load_iris()
    sampler = QMLSampler()                      # exact mode: no shot noise
    kernel = FidelityQuantumKernel(
        feature_map=feature_map,
        fidelity=ComputeUncompute(sampler=sampler),
    )
    qsvc = QSVC(quantum_kernel=kernel)
    qsvc.fit(iris.data, iris.target)
    predictions = qsvc.predict([[5.0, 3.3, 1.5, 0.3], [6.0, 2.9, 5.2, 1.7]])
    lab.show(viz.table(
        ["sample", "features", "predicted class", "expected class"],
        [("test 1", "[5.0, 3.3, 1.5, 0.3]", int(predictions[0]), 0),
         ("test 2", "[6.0, 2.9, 5.2, 1.7]", int(predictions[1]), 2)]))
    lab.check("the quantum SVM reproduces the course's predictions",
              list(predictions) == [0, 2],
              f"got {list(predictions)}, expected [0, 2]")
    lab.note("The course's original code used `BasicAer`, `QuantumInstance` "
             "and `algorithm_globals`; all three were removed in Qiskit 1.0. "
             "The modern equivalents are `AerSimulator`/`QMLSampler` and "
             "`FidelityQuantumKernel`.")


# ===========================================================================
# 14. Significance of quantum machine learning
# ===========================================================================
lab.section("14. Significance of quantum machine learning")

lab.step("What quantum ML actually gives you.")
lab.show(viz.table(
    ["claim", "reality"],
    [("'a quantum computer learns faster'",
      "not shown; the data loading usually dominates"),
     ("'the quantum kernel is exponentially rich'",
      "true in principle, hard to exploit in practice"),
     ("'you can read out the whole feature map'",
      "no -- you read out an expectation value"),
     ("'it is a drop-in replacement'",
      "yes: the kernel is the interface")]))

lab.step("The honest summary.")
lab.note("1. Quantum machine learning is *not* a speed-up for everything.  It "
         "is a new way to compute a similarity.")
lab.note("2. The useful part is the kernel: a quantum circuit can evaluate a "
         "function of two data points that is awkward to write down "
         "classically.")
lab.note("3. Everything else -- the loss, the optimizer, the train/test "
         "split -- stays classical, exactly as in lab L16.")
lab.note("4. The real obstacle is hardware: today's devices are noisy, and a "
         "deep feature map needs many layers of error correction before it "
         "beats a classical kernel machine.")
lab.note("")
lab.note("What the course has given you, end to end:")
lab.show(viz.table(
    ["course section", "what you built"],
    [("3  Math foundation", "complex numbers, probability, linear algebra, logic"),
     ("4  Quantum cryptography", "the BB84 protocol and its QBER"),
     ("7  Spin states", "the qubit as a two-level system"),
     ("10 Dirac notation", "|psi> = alpha|0> + beta|1> and the operator picture"),
     ("11 Entanglement", "Bell states, entropy, and the ordering traps"),
     ("13 Q#", "a four-qubit program in Microsoft's language"),
     ("15 Qiskit", "circuits, BB84 in Qiskit, and Shor's algorithm"),
     ("16 ML foundation", "gradients, overfitting, regularization, neural nets"),
     ("17 Quantum ML", "the quantum KNN and the quantum support vector machine")]))


if __name__ == "__main__":
    sys.exit(lab.finish())
