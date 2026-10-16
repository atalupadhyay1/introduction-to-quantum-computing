#!/usr/bin/env python3
"""
L06 -- Linear algebra: the language of quantum gates.

Course section: 3.4 (Matrices, Matrix Dimensions, Addition, Subtraction,
Scalar Multiplication, Multiplication, Non-commutativity, Outer and Inner
Products, Identity Matrix, Matrix Inverse, Transpose, Complex Conjugate,
Adjoint, Unitary, Hermitian, Vectors and Transformations, Eigenvectors and
Eigenvalues).

Run me::

    python labs/L06_linear_algebra/lab.py

What you will build
-------------------
* A matrix toolkit in pure Python: add, scale, multiply, transpose, invert.
* The adjoint, and the difference between a **unitary** matrix (reversible)
  and a **Hermitian** matrix (self-adjoint observable).
* Eigenvectors and eigenvalues of the Pauli gates, and what "invariant
  direction" means for a quantum state.
"""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from qc101.labkit import Lab
from qc101 import linalg as la
from qc101 import quantum as q
from qc101 import viz

lab = Lab("L06", "Linear algebra for quantum computing")


def show(m):
    return la.format_matrix(m)


def cn_pretty(z):
    """Render a complex number compactly for report lines."""
    if abs(z.imag) < 1e-12:
        return f"{z.real:.4f}"
    sign = "+" if z.imag >= 0 else "-"
    return f"{z.real:.4f}{sign}{abs(z.imag):.4f}i"



# ---------------------------------------------------------------------------
lab.section("1. Matrix dimensions and arithmetic")
# ---------------------------------------------------------------------------
lab.step("A 2x2 and a 3x2 matrix.")

a = [[1, 2], [3, 4]]
b = [[5, 6], [7, 8]]
lab.show("A =\n" + show(a))
lab.show("B =\n" + show(b))
lab.show("A + B =\n" + show(la.add(a, b)))
lab.show("A - B =\n" + show(la.sub(a, b)))
lab.show("2A  =\n" + show(la.scale(2, a)))

lab.check_equal("addition is element-wise", la.add(a, b), [[6, 8], [10, 12]])
lab.check_equal("subtraction is element-wise", la.sub(a, b), [[-4, -4], [-4, -4]])
lab.check_equal("scalar multiplication touches every element", la.scale(2, a), [[2, 4], [6, 8]])
lab.check_equal("dimensions are (rows, cols)", la.dims(a), (2, 2))


# ---------------------------------------------------------------------------
lab.section("2. Matrix multiplication: row by column")
# ---------------------------------------------------------------------------
lab.step("(AB)[i][j] = sum_k A[i][k] * B[k][j]")

lab.show("A =\n" + show(a))
lab.show("B =\n" + show(b))
lab.show("A x B =\n" + show(la.mul(a, b)))
lab.note("A x B = [[1*5+2*7, 1*6+2*8], [3*5+4*7, 3*6+4*8]] = [[19, 22], [43, 50]]")

lab.check_equal("A x B is correct", la.mul(a, b), [[19, 22], [43, 50]])
lab.check("multiplication is not commutative", la.mul(a, b) != la.mul(b, a))
try:
    la.mul(a, [[1, 2], [3, 4], [5, 6]])   # 2x2 times 3x2: cols(A)=2 != rows(B)=3
    ok = False
except ValueError:
    ok = True
lab.check("a 2x2 times a 3x2 raises (cols must match rows)", ok)
lab.check("a 2x2 times a 2x3 IS possible",
          la.dims(la.mul(a, [[1, 2, 3], [4, 5, 6]])) == (2, 3),
          "the rule is cols(A) == rows(B)")

lab.step("Associativity and distributivity.")
lab.note("A(B+C) = AB + AC")
lab.check("matrix multiplication is associative",
          la.mul(a, la.add(b, b)) == la.add(la.mul(a, b), la.mul(a, b)))
lab.note("(A+B)(C+D) = AC + AD + BC + BD")
lab.check("matrix multiplication is distributive",
          la.mul(la.add(a, a), la.add(b, b)) == la.add(
              la.add(la.mul(a, b), la.mul(a, b)),
              la.add(la.mul(a, b), la.mul(a, b)),
          ))


# ---------------------------------------------------------------------------
lab.section("3. Outer and inner products")
# ---------------------------------------------------------------------------
lab.step("The outer product of a column and a row builds a table of all pairwise products.")

col = [[1], [2]]
row = [[3, 4]]
lab.show("column x row =\n" + show(la.mul(col, row)))
lab.check_equal("the outer product is the pairwise table", la.mul(col, row), [[3, 4], [6, 8]])

lab.step("The inner product of two vectors is a single number.")
v = [1 + 0j, 0 - 1j]
w = [1 + 0j, 0 + 1j]
lab.note(f"<v|v> = conj(v) . v = {la.inner_product(v, v)}")
lab.note(f"<v|conj(v)> = {la.inner_product(v, w)}")
lab.check_close("<v|v> is always |v|^2", la.inner_product(v, v).real, 2.0, 1e-12)
lab.check_close("<v|conj(v)> is zero -- v and conj(v) are orthogonal",
                la.inner_product(v, w).real, 0.0, 1e-12)
lab.note("Note the conjugation on the FIRST argument -- this is the quantum-mechanics "
         "convention, and it is why <psi|psi> is always real and positive.")


# ---------------------------------------------------------------------------
lab.section("4. Identity, transpose, inverse")
# ---------------------------------------------------------------------------
lab.step("A x I = A, and A x A^-1 = I.")

identity = la.identity(2)
lab.show("I =\n" + show(identity))
lab.show("A^-1 =\n" + show(la.inverse(a)))
lab.check("A x A^-1 = I", la.is_identity(la.mul(a, la.inverse(a))))
lab.check("A^-1 x A = I", la.is_identity(la.mul(la.inverse(a), a)))
lab.check_equal("the determinant of [[1,2],[3,4]] is -2", la.determinant(a).real, -2.0)

lab.step("The transpose interchanges rows and columns.")
lab.show("A^T =\n" + show(la.transpose(a)))
lab.check_equal("the transpose is correct", la.transpose(a), [[1, 3], [2, 4]])
lab.note("The transpose of a product reverses the order: (AB)^T = B^T A^T.")
lab.check("the transpose of a product reverses the order",
          la.transpose(la.mul(a, b)) == la.mul(la.transpose(b), la.transpose(a)))


# ---------------------------------------------------------------------------
lab.section("5. The adjoint, unitary and Hermitian matrices")
# ---------------------------------------------------------------------------
lab.step("The adjoint is the transpose of the complex conjugate: A^dagger.")

c = [[1, 1j], [-1j, 2]]
lab.show("C =\n" + show(c))
lab.show("conj(C) =\n" + show(la.conjugate(c)))
lab.show("C^dagger =\n" + show(la.adjoint(c)))
lab.check("the adjoint of a matrix is its conjugate transpose",
          la.adjoint(c) == la.transpose(la.conjugate(c)))

lab.step("Unitary matrices are reversible transformations.")
for name, gate in (("X", q.X), ("Y", q.Y), ("Z", q.Z), ("H", q.H), ("S", q.S), ("T", q.T)):
    lab.note(f"  {name}: unitary={la.is_unitary(gate)!s:<5} hermitian={la.is_hermitian(gate)!s:<5} "
             f"A^dagger A = I? {la.is_identity(la.mul(la.adjoint(gate), gate))}")
    lab.check(f"{name} is unitary", la.is_unitary(gate))
    lab.check(f"{name} dagger times {name} is the identity",
              la.is_identity(la.mul(la.adjoint(gate), gate)))

lab.note("H is both unitary AND Hermitian: H^-1 = H = H^dagger, so H squared is I.")
lab.check("H is Hermitian", la.is_hermitian(q.H))
lab.check("H squared is the identity", la.is_identity(la.mul(q.H, q.H)))

lab.step("Hermitian matrices are self-adjoint observables (measurements).")
lab.check("Z is Hermitian", la.is_hermitian(q.Z))
lab.check("S is NOT Hermitian but IS unitary", la.is_hermitian(q.S) is False and la.is_unitary(q.S))
lab.note("This is the course's headline pattern: initialisation and measurement are "
         "Hermitian (irreversible); the gates in between are unitary (reversible).")


# ---------------------------------------------------------------------------
lab.section("6. Vectors as state columns and linear transformations")
# ---------------------------------------------------------------------------
lab.step("A transformation matrix maps a coordinate to a new coordinate.")

theta = math.radians(30)
rotation = [[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]]
point = [1, 0]
rotated = [row[0] * point[0] + row[1] * point[1] for row in rotation]
lab.show("R(30 deg) =\n" + show(rotation))
lab.note(f"(1,0) rotated by 30 deg -> ({rotated[0]:.4f}, {rotated[1]:.4f})")
lab.check_close("the x component is cos(30)", rotated[0], math.cos(theta), 1e-12)
lab.check_close("the y component is sin(30)", rotated[1], math.sin(theta), 1e-12)
lab.check("a rotation matrix is unitary", la.is_unitary(rotation))


# ---------------------------------------------------------------------------
lab.section("7. Eigenvectors and eigenvalues: invariant directions")
# ---------------------------------------------------------------------------
lab.step("Find the directions a transformation leaves unchanged.")

for name, gate in (("X", q.X), ("Y", q.Y), ("Z", q.Z), ("H", q.H)):
    lab.note(f"{name}:")
    for lam, vec in la.eigenpairs_2x2(gate):
        lab.note(f"   eigenvalue {cn_pretty(lam)}   eigenvector "
                 f"({cn_pretty(vec[0])}, {cn_pretty(vec[1])})")
    lab.check(f"{name} has two eigenvalues", len(la.eigenvalues_2x2(gate)) == 2)

lab.step("Verify the eigen relation A v = lambda v for the X gate.")
lam, vec = la.eigenpairs_2x2(q.X)[0]
av = [q.X[0][0] * vec[0] + q.X[0][1] * vec[1], q.X[1][0] * vec[0] + q.X[1][1] * vec[1]]
for i in range(2):
    lab.check_close(f"component {i}: (Av)_i = lambda * v_i", av[i].real, (lam * vec[i]).real, 1e-9)
lab.note("An eigenvector of the X gate is a state the gate leaves unchanged (up to a "
         "global phase).  The X gate's eigenvectors are exactly the states it can "
         "measure perfectly.")

lab.step("Dominant eigenpair by power iteration (the 'computing eigen values' trick).")
dom = [[2, 1], [1, 2]]          # eigenvalues 3 and 1 -- a clean dominant one
lam, vec = la.power_iteration(dom)
lab.note(f"power iteration on [[2,1],[1,2]] -> eigenvalue {cn_pretty(lam)}, eigenvector "
         f"({cn_pretty(vec[0])}, {cn_pretty(vec[1])})")
lab.check_close("the dominant eigenvalue is 3", lam.real, 3.0, 1e-8)
lab.check("the eigenvector is (1,1)/sqrt(2)", abs(vec[0].real - 1 / math.sqrt(2)) < 1e-8)
lab.note("Power iteration needs a UNIQUE dominant eigenvalue.  The Hadamard gate has "
         "eigenvalues +1 and -1 -- equal magnitude -- so the iteration oscillates "
         "between the two eigendirections instead of converging.  Use the exact "
         "2x2 solver for that case.")


# ---------------------------------------------------------------------------
lab.section("8. The Kronecker product composes qubits")
# ---------------------------------------------------------------------------
lab.step("|0> tensor |1> is a two-qubit state.")

k = la.kron([[1], [0]], [[0], [1]])
lab.show("|0> (x) |1> =\n" + show(k))
lab.check_equal("|0> (x) |1> is the column (0,1,0,0)^T", k, [[0], [1], [0], [0]])
lab.note("Index 1 is the binary state '01' -- remember that in this course q0 is the "
         "LEFTMOST bit, so |0> (x) |1> means 'q0=0, q1=1'.")
lab.note("The tensor product of two qubits is a 4x4 matrix acting on 4 amplitudes.  "
         "This is how a 2-qubit gate like CNOT is built from the 1-qubit blocks.")


if __name__ == "__main__":
    sys.exit(lab.finish())
