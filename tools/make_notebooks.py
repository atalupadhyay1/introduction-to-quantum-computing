#!/usr/bin/env python3
"""Generate the QC101 Jupyter notebooks."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "notebooks"
OUT.mkdir(parents=True, exist_ok=True)

PREAMBLE = """\
import math
import sys
from pathlib import Path

# Make the shared qc101 library importable, whether the notebook is opened
# from the repository root or from inside the notebooks/ directory.
_here = Path.cwd().resolve()
for _candidate in (_here / "labs" / "common",
                   _here.parent / "labs" / "common",
                   _here / ".." / "labs" / "common"):
    if (_candidate / "qc101").is_dir():
        sys.path.insert(0, str(_candidate.resolve()))
        break
else:
    raise SystemExit("Could not find the qc101 library -- run this notebook "
                     "from the repository root or from notebooks/.")

from qc101 import boolean, complexnum, linalg, photon, probability, quantum, viz
from qc101.labkit import Lab

print("qc101 library ready")
"""


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": text.splitlines(keepends=True)}


def notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.11",
                "mimetype": "text/x-python",
                "codemirror_mode": {"name": "ipython", "version": 3},
                "pygments_lexer": "ipython3",
                "nbconvert_exporter": "python",
                "file_extension": ".py",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


# --------------------------------------------------------------------------
NOTEBOOKS = {}

# ---------------------------------------------------------------- 01
NOTEBOOKS["01_math_foundation"] = notebook([
    md("""# 1. The mathematical foundation

The QC101 course teaches the mathematics *first*, because quantum mechanics
is written in complex numbers, linear algebra and probability.

This notebook uses the shared `qc101` library that every lab in the
repository is built on.
"""),
    code(PREAMBLE),
    md("""## Complex numbers

The modulus of a complex number is the length of the vector it represents:
$$|z| = \\sqrt{a^2 + b^2}$$
and the product of a number with its conjugate is the modulus squared.
"""),
    code("""z = 3 + 4j                       # a plain Python complex number
print("z            =", z)
print("|z|          =", complexnum.magnitude(z))
print("|z|^2        =", complexnum.squared_magnitude(z))
print("conjugate    =", complexnum.conjugate(z))
print("z * z_bar    =", complexnum.mul(z, complexnum.conjugate(z)))
print("polar        =", complexnum.polar_pretty(z))"""),
    md("""## Linear algebra: matrices, adjoints and unitarity

A quantum gate is a unitary matrix.  A matrix is unitary when
$A^\\dagger A = I$, and that is exactly what makes it reversible.
"""),
    code("""H = quantum.H
X = quantum.X
print("H =\\n", linalg.format_matrix(H))
print("H^dagger H == I :", linalg.matrix_equals(linalg.mul(linalg.adjoint(H), H),
                                               linalg.identity(2)))
print("H is Hermitian  :", linalg.is_hermitian(H))
print("H is unitary    :", linalg.is_unitary(H))"""),
    md("""## Eigenvalues

Multiplying a matrix by an eigenvector and factoring out the eigenvalue
leaves the eigenvector's own system of equations.
"""),
    code("""for value, vector in linalg.eigenpairs_2x2(H):
    print(f"lambda = {value},  v = {vector}")
    product = linalg.mul(H, [[c] for c in vector])       # matrix x column
    print("   H v =", [row[0] for row in product])"""),
    md("""## The Kronecker product

This is how multi-qubit states are built.  With $q_0$ leftmost, the index
runs as `i * rows(B) + k`.
"""),
    code("""zero = [[1], [0]]
one = [[0], [1]]
print("|0> tensor |1> =", linalg.kron(zero, one))
print("|1> tensor |0> =", linalg.kron(one, zero))"""),
    md("""## Probability

The rules you need for quantum measurement statistics.
"""),
    code("""rng = __import__("random").Random(7)
coin = probability.bernoulli(0.5, name="Head")
print("distribution :", coin.distribution)
print("mean         :", coin.mean())
print("variance     :", coin.variance())
tosses = coin.sample(1000, rng)
print("mean of 1000 tosses :", probability.mean(tosses))"""),
    md("""## Boolean logic

AND, OR, NOT, and the truth tables they generate.
"""),
    code("""print(boolean.render_truth_table(lambda a, b: boolean.AND(a, b)))
print()
print(boolean.render_truth_table(lambda a, b: boolean.XOR(a, b)))"""),
])

# ---------------------------------------------------------------- 02
NOTEBOOKS["02_qubit_basics"] = notebook([
    md("""# 2. Qubits, gates and entanglement

The core of the course's quantum model, in a notebook.
"""),
    code(PREAMBLE),
    md("""## A qubit and its probabilities

$$|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle, \\qquad
|\\alpha|^2 + |\\beta|^2 = 1$$
"""),
    code("""sv = quantum.StateVector([1, 0])          # the state |0>
print(sv)
print("P(0) =", sv.probabilities()[0], " P(1) =", sv.probabilities()[1])
print("basis labels:", sv.basis_labels())"""),
    md("""## Applying gates

A gate is a unitary matrix; applying it multiplies the state vector.
"""),
    code("""sv = quantum.StateVector([1, 0])
for name, gate in (("H", quantum.H), ("X", quantum.X), ("Z", quantum.Z)):
    after = sv.apply_single(gate, 0)
    print(f"after {name}: {after}   P(0) = {after.probabilities()[0]:.4f}")"""),
    md("""## Measuring

Measurement is the irreversible step.  It returns an outcome sampled from
the Born distribution.
"""),
    code("""import random
rng = random.Random(42)
sv = quantum.StateVector([1, 0]).apply_single(quantum.H, 0)
counts = {0: 0, 1: 0}
for _ in range(2000):
    bit, collapsed = sv.measure_qubit(0, rng)
    counts[bit] += 1
print("counts:", counts)
print("the state collapsed to:", collapsed)"""),
    md("""## Two qubits: the Bell state

H on q0 then CNOT gives $(|00\\rangle + |11\\rangle)/\\sqrt2$.
"""),
    code("""bell = quantum.bell_state()
print("state      :", bell)
print("labels     :", bell.basis_labels())
probs = bell.probabilities()
print("P(00) =", probs[0])
print("P(11) =", probs[3])"""),
    md("""## Entanglement entropy

The entropy of the *reduced* state tells you how entangled the pair is.
"""),
    code("""product = quantum.StateVector([0.5, 0.5, 0.5, 0.5])
print("Bell pair entropy    :", quantum.entanglement_entropy(bell))
print("product state entropy:", quantum.entanglement_entropy(product))
print("Bell pair is entangled:", quantum.is_entangled(bell))
print("product is entangled  :", quantum.is_entangled(product))"""),
    md("""## The Q# ordering trap

Q# prints results right-to-left, the state vector is written left-to-right.
This is the course's 'Verifying Results' article in one cell.
"""),
    code("""# q0 = 1, q1 = 0  ->  Q# says "01", the textbook says "10"
state = quantum.StateVector([0, 1, 0, 0])
print("state vector (q0 first):", state)
print("Q# would print        : '01'")"""),
])

# ---------------------------------------------------------------- 03
NOTEBOOKS["03_bb84"] = notebook([
    md("""# 3. BB84, end to end

The course's quantum key distribution protocol, with the quantum bit error
rate measured in all three scenarios.
"""),
    code(PREAMBLE),
    md("""## The protocol

Each round: Alice picks a bit and a basis, Bob picks a basis, they compare
bases publicly and keep the matching rounds.
"""),
    code("""from qc101 import bb84

for label, kwargs in (("no eavesdropper", {"eve": False}),
                       ("eve, same basis ", {"eve": True, "eve_resend_mode": "same_basis"}),
                       ("eve, random basis", {"eve": True, "eve_resend_mode": "random_basis"})):
    result = bb84.run_bb84(rounds=2000, seed=2024, **kwargs)
    print(f"{label}:  sifted {result.sifted_length:>3}  "
          f"QBER {result.qber * 100:5.2f}%  "
          f"detected: {result.detected}  keys match: {result.key_matches}")"""),
    md("""## Why 25%?

Half the sifted rounds used the same basis (no error) and half used
different bases (half of *those* are wrong):

$$Q = \\tfrac12 \\cdot 0 + \\tfrac12 \\cdot \\tfrac12 = \\tfrac14$$
"""),
    code("""print("no eavesdropper       :   0.00%")
print("eve, same basis        : ~ 25.00%   (the textbook intercept-resend)")
print("eve, random basis      : ~ 37.50%   (a noisier but stronger attack)")
print("one-way abort threshold: ~ 11.00%")
print()
print("the threshold used by the library:", bb84.QBER_THRESHOLD)"""),
    md("""## The one-time pad

$C = M \\oplus K$ and $M = C \\oplus K$.  With a one-time, uniformly random,
equal-length key this is unconditionally secure.
"""),
    code("""import random
rng = random.Random(99)

message = "ATTACK AT DAWN"
cipher, pad = boolean.one_time_pad_encrypt(message, rng)
plain = boolean.one_time_pad_decrypt(cipher, pad)
print("message  :", message)
print("pad bits :", "".join(map(str, pad[:32])), "...")
print("cipher   :", "".join(map(str, cipher[:32])), "...")
print("decrypted:", plain)
print("round trip works:", plain == message)"""),
])

# ---------------------------------------------------------------- 04
NOTEBOOKS["04_quantum_knn"] = notebook([
    md("""# 4. The quantum KNN, from the maths up

This is the heart of the course's section 17.  We will:

1. compute the classical KNN;
2. work out what the quantum circuit computes;
3. show the two are the same number.
"""),
    code(PREAMBLE),
    code("""import math

TRAINING = [[0.9798, 0.2, 1], [0.3, 0.954, 0]]
QUERY = [0.85, 0.5268]

def normalize(v):
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v]"""),
    md("""## Step 1: the classical KNN

Normalise, compute squared distances, turn distances into weights, and
normalise the weights into probabilities.
"""),
    code("""vectors = [normalize(t[:2]) for t in TRAINING]
q = normalize(QUERY)

weights = []
for v in vectors:
    d2 = sum((qi - vi) ** 2 for qi, vi in zip(q, v))
    weights.append((d2, 1 - 0.25 * d2))

total = sum(w for _, w in weights)
classical = {t[2]: 0.0 for t in TRAINING}
for t, (_, w) in zip(TRAINING, weights):
    classical[t[2]] += w / total

for t, (d2, w) in zip(TRAINING, weights):
    print(f"class {t[2]}:  d^2 = {d2:.6f}   w = {w:.6f}")
print("classical probabilities:", classical)"""),
    md("""## Step 2: the interference amplitudes

At a slot holding a training component $v_i$ and the query component $q_i$,
the Hadamard on the 'training vs query' qubit leaves the amplitude

$$\\frac{v_i + q_i}{2\\sqrt2}$$

so the probability of that slot in the training half is proportional to
$(v_i + q_i)^2$.
"""),
    code("""for label, v in zip(("training 0", "training 1"), vectors):
    interference = sum((vi + qi) ** 2 for vi, qi in zip(v, q))
    d2 = sum((qi - vi) ** 2 for qi, vi in zip(q, v))
    classical_w = 1 - 0.25 * d2
    print(f"{label}:  sum (v_i + q_i)^2 = {interference:.6f}   "
          f"4 * w = {4 * classical_w:.6f}   equal: {abs(interference - 4*classical_w) < 1e-12}")"""),
    md("""## Step 3: the class probability

Sum the interference amplitudes per class, then normalise.
"""),
    code("""quantum = {0: 0.0, 1: 0.0}
for v, t in zip(vectors, TRAINING):
    quantum[t[2]] += sum((vi + qi) ** 2 for vi, qi in zip(v, q))

total = sum(quantum.values())
quantum = {k: v / total for k, v in quantum.items()}

for k in sorted(classical):
    print(f"class {k}:  classical {classical[k]:.6f}   quantum {quantum[k]:.6f}")"""),
    md("""## Step 4: the real circuit

The same thing, done with Qiskit.  If Qiskit is installed the next cell
runs; otherwise it prints a note.
"""),
    code("""try:
    import numpy as np
    from qiskit import QuantumCircuit, transpile
    from qiskit.quantum_info import Statevector
    from qiskit_aer import AerSimulator

    amplitudes = [0.0] * 16

    def index(q0, q1, q2, q3):
        return q0 + 2 * q1 + 4 * q2 + 8 * q3

    for v, t in zip(vectors, TRAINING):
        class_bit = 1 if t[2] == TRAINING[0][2] else 0
        amplitudes[index(class_bit, 0, 0, 0)] = v[0] / 2
        amplitudes[index(class_bit, 1, 0, 0)] = v[1] / 2
    for class_bit in (1, 0):
        amplitudes[index(class_bit, 0, 0, 1)] = q[0] / 2
        amplitudes[index(class_bit, 1, 0, 1)] = q[1] / 2

    qc = QuantumCircuit(4, 2)
    qc.initialize(amplitudes)
    qc.h(3)
    qc.measure(3, 0)
    qc.measure(0, 1)

    counts = (AerSimulator().run(transpile(qc, AerSimulator()), shots=20000)
              .result().get_counts())
    q3zero = counts.get("00", 0) + counts.get("10", 0)
    p1 = counts.get("10", 0) / q3zero
    print("counts:", counts)
    print(f"quantum P(class 1) = {p1:.4f}   classical = {classical[1]:.4f}")
except ImportError as exc:
    print("Qiskit is not installed:", exc)"""),
])

# ---------------------------------------------------------------- 05
NOTEBOOKS["05_quantum_svm"] = notebook([
    md("""# 5. The quantum support vector machine

The other half of section 17: replace the classical kernel with a quantum
one.
"""),
    code(PREAMBLE),
    code("""import numpy as np"""),
    md("""## The classical kernel and the quantum one

$$K(x, z) = \\phi(x) \\cdot \\phi(z)
\\qquad\\longrightarrow\\qquad
K(x, z) = |\\langle\\phi(x)|\\phi(z)\\rangle|^2$$
"""),
    code("""try:
    from qiskit.circuit.library import zz_feature_map
    from qiskit.quantum_info import Statevector

    feature_map = zz_feature_map(feature_dimension=4, reps=2, entanglement="linear")
    print(feature_map.decompose())
except ImportError as exc:
    print("Qiskit is not installed:", exc)"""),
    md("""## A kernel entry, computed from the state vectors

The kernel is just the squared overlap of two feature-map states.
"""),
    code("""try:
    def feature_state(x):
        return Statevector(feature_map.assign_parameters(list(x)))

    x1 = [5.0, 3.3, 1.5, 0.3]
    x2 = [6.0, 2.9, 5.2, 1.7]
    k12 = abs(np.vdot(feature_state(x1).data, feature_state(x2).data)) ** 2
    k11 = abs(np.vdot(feature_state(x1).data, feature_state(x1).data)) ** 2
    print(f"K(x1, x1) = {k11:.6f}")
    print(f"K(x1, x2) = {k12:.6f}")
except ImportError as exc:
    print("Qiskit is not installed:", exc)"""),
    md("""## Training a QSVC

The course's `qsvm.py`, modernized: `BasicAer` and `QuantumInstance` were
removed in Qiskit 1.0.
"""),
    code("""try:
    from sklearn.datasets import load_iris
    from qiskit_machine_learning.algorithms import QSVC
    from qiskit_machine_learning.kernels import FidelityQuantumKernel
    from qiskit_machine_learning.primitives import QMLSampler
    from qiskit_machine_learning.state_fidelities import ComputeUncompute

    iris = load_iris()
    kernel = FidelityQuantumKernel(
        feature_map=feature_map,
        fidelity=ComputeUncompute(sampler=QMLSampler()),
    )
    qsvc = QSVC(quantum_kernel=kernel)
    qsvc.fit(iris.data, iris.target)
    print("predictions:",
          qsvc.predict([[5.0, 3.3, 1.5, 0.3], [6.0, 2.9, 5.2, 1.7]]))
except ImportError as exc:
    print("qiskit-machine-learning is not installed:", exc)"""),
    md("""## What this is actually worth

Quantum machine learning is mainly a new way to compute a *similarity*.
The data wrangling, the loss and the optimizer stay classical.
"""),
])

# --------------------------------------------------------------------------
for name, data in NOTEBOOKS.items():
    path = OUT / f"{name}.ipynb"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=1)
        handle.write("\n")
    print(f"wrote {path.name}: {len(data['cells'])} cells")
