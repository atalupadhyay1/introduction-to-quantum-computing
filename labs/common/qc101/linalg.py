"""
Linear algebra for quantum computing, in dependency-free Python.

Covers Section 3.4 of QC101: matrix dimensions, addition, subtraction,
scalar multiplication, multiplication (row-by-column), non-commutativity,
associativity/distributivity, outer and inner products, the identity matrix,
the inverse, the transpose, the complex conjugate, the adjoint (dagger),
unitary and Hermitian matrices, and eigenvectors/eigenvalues.

Matrices are lists of row lists.  Entries are Python ``int``/``float`` or
``complex`` -- so a "complex matrix" needs no special type.
"""

from __future__ import annotations

import cmath
import math
from typing import List, Sequence, Tuple

Matrix = List[List[complex]]
Vector = List[complex]

__all__ = [
    "zeros",
    "identity",
    "dims",
    "is_square",
    "add",
    "sub",
    "scale",
    "mul",
    "transpose",
    "conjugate",
    "adjoint",
    "inverse",
    "determinant",
    "inner_product",
    "outer_product",
    "kron",
    "is_unitary",
    "is_hermitian",
    "is_identity",
    "eigenvalues_2x2",
    "hermitian_eigenvalues",
    "jacobi_eigenvalues_real",
    "eigenpairs_2x2",
    "power_iteration",
    "rref",
    "format_matrix",
    "matrix_equals",
]


# --------------------------------------------------------------------------
# Construction
# --------------------------------------------------------------------------
def zeros(rows: int, cols: int) -> Matrix:
    """A rows x cols matrix of zeros."""
    return [[complex(0, 0) for _ in range(cols)] for _ in range(rows)]


def identity(n: int) -> Matrix:
    """The n x n identity matrix."""
    m = zeros(n, n)
    for i in range(n):
        m[i][i] = complex(1, 0)
    return m


def dims(m: Matrix) -> Tuple[int, int]:
    """Return ``(rows, cols)`` of a matrix."""
    if not m:
        return (0, 0)
    return (len(m), len(m[0]))


def is_square(m: Matrix) -> bool:
    """True when the matrix has as many rows as columns."""
    r, c = dims(m)
    return r == c


# --------------------------------------------------------------------------
# Arithmetic
# --------------------------------------------------------------------------
def _check_same_dims(a: Matrix, b: Matrix) -> None:
    if dims(a) != dims(b):
        raise ValueError(f"dimension mismatch: {dims(a)} vs {dims(b)}")


def add(a: Matrix, b: Matrix) -> Matrix:
    """Element-wise addition."""
    _check_same_dims(a, b)
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def sub(a: Matrix, b: Matrix) -> Matrix:
    """Element-wise subtraction."""
    _check_same_dims(a, b)
    return [[x - y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def scale(k: complex, m: Matrix) -> Matrix:
    """Multiply every element of the matrix by the scalar ``k``."""
    return [[k * x for x in row] for row in m]


def mul(a: Matrix, b: Matrix) -> Matrix:
    """
    Matrix multiplication, row-by-column.

    ``(A B)[i][j] = sum_k A[i][k] * B[k][j]``
    """
    rows_a, cols_a = dims(a)
    rows_b, cols_b = dims(b)
    if cols_a != rows_b:
        raise ValueError(f"cannot multiply {dims(a)} by {dims(b)}")
    out = zeros(rows_a, cols_b)
    for i in range(rows_a):
        for j in range(cols_b):
            out[i][j] = sum(a[i][k] * b[k][j] for k in range(cols_a))
    return out


# --------------------------------------------------------------------------
# Transforms
# --------------------------------------------------------------------------
def transpose(m: Matrix) -> Matrix:
    """Interchange rows and columns."""
    if not m:
        return []
    return [list(col) for col in zip(*m)]


def conjugate(m: Matrix) -> Matrix:
    """Complex-conjugate every element."""
    return [[x.conjugate() if isinstance(x, complex) else complex(x).conjugate() for x in row] for row in m]


def adjoint(m: Matrix) -> Matrix:
    """The adjoint (dagger): transpose of the complex conjugate."""
    return transpose(conjugate(m))


# --------------------------------------------------------------------------
# Inversion and determinants
# --------------------------------------------------------------------------
def determinant(m: Matrix) -> complex:
    """
    Determinant via cofactor expansion (fine for the small matrices used here).
    """
    n, _ = dims(m)
    if n == 0:
        return complex(1, 0)
    if n == 1:
        return m[0][0]
    if n == 2:
        return m[0][0] * m[1][1] - m[0][1] * m[1][0]
    total = complex(0, 0)
    for j in range(n):
        minor = [row[:j] + row[j + 1 :] for row in m[1:]]
        sign = 1 if j % 2 == 0 else -1
        total += sign * m[0][j] * determinant(minor)
    return total


def inverse(m: Matrix) -> Matrix:
    """
    Matrix inverse via Gauss-Jordan elimination with partial pivoting.
    """
    n, _ = dims(m)
    if n == 0 or not is_square(m):
        raise ValueError("only square matrices can be inverted")
    aug = [[complex(x) for x in row] + [complex(1 if i == j else 0) for j in range(n)] for i, row in enumerate(m)]

    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot_row][col]) < 1e-12:
            raise ValueError("matrix is singular and cannot be inverted")
        aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
        pivot = aug[col][col]
        aug[col] = [x / pivot for x in aug[col]]
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            if factor != 0:
                aug[r] = [a - factor * b for a, b in zip(aug[r], aug[col])]

    return [row[n:] for row in aug]


def rref(m: Matrix) -> Matrix:
    """Reduced row echelon form (used for linear-dependency checks)."""
    rows, cols = dims(m)
    aug = [[complex(x) for x in row] for row in m]
    lead = 0
    for r in range(rows):
        if lead >= cols:
            break
        pivot_row = None
        for i in range(r, rows):
            if abs(aug[i][lead]) > 1e-12:
                pivot_row = i
                break
        if pivot_row is None:
            lead += 1
            r -= 1
            continue
        aug[r], aug[pivot_row] = aug[pivot_row], aug[r]
        pivot = aug[r][lead]
        aug[r] = [x / pivot for x in aug[r]]
        for i in range(rows):
            if i != r and abs(aug[i][lead]) > 1e-12:
                factor = aug[i][lead]
                aug[i] = [a - factor * b for a, b in zip(aug[i], aug[r])]
        lead += 1
    return aug


# --------------------------------------------------------------------------
# Products
# --------------------------------------------------------------------------
def inner_product(a: Vector, b: Vector) -> complex:
    """
    The conjugate inner product ``<a|b> = sum_i conj(a_i) * b_i``.

    Note the conjugation on the *first* argument -- this is the convention
    used in quantum mechanics.
    """
    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    return sum((x.conjugate() if isinstance(x, complex) else complex(x).conjugate()) * y for x, y in zip(a, b))


def outer_product(a: Vector, b: Vector) -> Matrix:
    """The outer product ``|a><b|`` as a matrix."""
    return [[(ai.conjugate() if isinstance(ai, complex) else complex(ai).conjugate()) * bj for bj in b] for ai in a]


def kron(a: Matrix, b: Matrix) -> Matrix:
    """Kronecker (tensor) product -- the operation that composes qubit states."""
    ra, ca = dims(a)
    rb, cb = dims(b)
    out = zeros(ra * rb, ca * cb)
    for i in range(ra):
        for j in range(ca):
            for k in range(rb):
                for l in range(cb):
                    out[i * rb + k][j * cb + l] = a[i][j] * b[k][l]
    return out


# --------------------------------------------------------------------------
# Special matrix properties
# --------------------------------------------------------------------------
def matrix_equals(a: Matrix, b: Matrix, tol: float = 1e-9) -> bool:
    """Element-wise comparison with a tolerance."""
    if dims(a) != dims(b):
        return False
    return all(abs(x - y) < tol for ra, rb in zip(a, b) for x, y in zip(ra, rb))


def is_identity(m: Matrix, tol: float = 1e-9) -> bool:
    """True when the matrix equals the identity matrix."""
    n, _ = dims(m)
    return matrix_equals(m, identity(n), tol)


def is_unitary(m: Matrix, tol: float = 1e-9) -> bool:
    """
    True when ``A^dagger A = I``.

    A unitary matrix is a *reversible* state transformation: it preserves
    total probability and can be undone by its own inverse.
    """
    return matrix_equals(mul(adjoint(m), m), identity(dims(m)[0]), tol)


def is_hermitian(m: Matrix, tol: float = 1e-9) -> bool:
    """
    True when ``A^dagger = A``.

    A Hermitian matrix is a *self-adjoint* operator, typically associated
    with an observable (a measurement).
    """
    return matrix_equals(adjoint(m), m, tol)


# --------------------------------------------------------------------------
# Eigenvalues / eigenvectors
# --------------------------------------------------------------------------
def eigenvalues_2x2(m: Matrix) -> List[complex]:
    """
    Eigenvalues of a 2x2 matrix from the characteristic polynomial
    ``lambda^2 - tr(A) lambda + det(A) = 0``.
    """
    a, b = m[0]
    c, d = m[1]
    trace = a + d
    det = a * d - b * c
    disc = cmath.sqrt(trace * trace - 4 * det)
    return [(trace + disc) / 2, (trace - disc) / 2]


def eigenpairs_2x2(m: Matrix) -> List[Tuple[complex, Vector]]:
    """
    Return ``[(eigenvalue, eigenvector), ...]`` for a 2x2 matrix.

    The eigenvector for ``lambda`` solves ``(A - lambda I) v = 0``; we take
    the null space of ``A - lambda I`` via row reduction.
    """
    a, b = m[0]
    c, d = m[1]
    pairs: List[Tuple[complex, Vector]] = []
    for lam in eigenvalues_2x2(m):
        # (A - lambda*I) v = 0
        mat = [[a - lam, b], [c, d - lam]]
        red = rref(mat)
        # The pivot columns of the RREF are the leading-1 columns; any
        # remaining column is free and parameterises the null space.
        pivot_cols: List[int] = []
        for r in range(len(red)):
            for j in range(2):
                if abs(red[r][j]) > 1e-12:
                    pivot_cols.append(j)
                    break
        free_cols = [j for j in range(2) if j not in pivot_cols]
        if not free_cols:
            # A - lambda*I is the zero matrix: every vector is an eigenvector.
            vec = [complex(1, 0), complex(0, 0)]
        else:
            free_col = free_cols[0]
            vec = [complex(0, 0), complex(0, 0)]
            vec[free_col] = complex(1, 0)
            if pivot_cols:
                pivot_col = pivot_cols[0]
                # The null space obeys  red[0][pivot]*v[pivot] + red[0][free]*v[free] = 0
                if abs(red[0][pivot_col]) > 1e-12:
                    vec[pivot_col] = -red[0][free_col] / red[0][pivot_col] * vec[free_col]
        norm = math.sqrt(sum(abs(x) ** 2 for x in vec))
        if norm > 1e-12:
            vec = [x / norm for x in vec]
        pairs.append((lam, vec))
    return pairs


def jacobi_eigenvalues_real(a: List[List[float]], max_sweeps: int = 100, tol: float = 1e-14) -> List[float]:
    """
    Eigenvalues of a **real symmetric** matrix, by the Jacobi method.

    The Jacobi method repeatedly applies plane rotations that zero out
    off-diagonal elements.  It is simple, unconditionally stable and
    converges quadratically -- perfect for the small matrices used here.
    """
    n = len(a)
    if n == 0:
        return []
    m = [list(row) for row in a]
    for _ in range(max_sweeps):
        # Locate the largest off-diagonal element.
        p = q = 0
        biggest = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                if abs(m[i][j]) > biggest:
                    biggest, p, q = abs(m[i][j]), i, j
        if biggest < tol:
            break
        app, aqq, apq = m[p][p], m[q][q], m[p][q]
        theta = 0.5 * math.atan2(2.0 * apq, aqq - app)
        c, s = math.cos(theta), math.sin(theta)
        for k in range(n):
            if k != p and k != q:
                akp, akq = m[k][p], m[k][q]
                m[k][p] = m[p][k] = c * akp - s * akq
                m[k][q] = m[q][k] = s * akp + c * akq
        m[p][p] = c * c * app - 2 * s * c * apq + s * s * aqq
        m[q][q] = s * s * app + 2 * s * c * apq + c * c * aqq
        m[p][q] = m[q][p] = 0.0
    return sorted(m[i][i] for i in range(n))


def hermitian_eigenvalues(m: Matrix, max_sweeps: int = 100) -> List[float]:
    """
    Eigenvalues of a **Hermitian** matrix (A = A^dagger), returned as real
    numbers sorted in increasing order.

    Implementation: the *realification* of a Hermitian matrix

        [ Re(A)  -Im(A) ]
        [ Im(A)   Re(A) ]

    is a real symmetric matrix of twice the size whose eigenvalues are
    each eigenvalue of ``A`` repeated twice.  We run the real Jacobi
    method on it and take every other eigenvalue.
    """
    n = dims(m)[0]
    if n == 0:
        return []
    size = 2 * n
    real = [[0.0] * size for _ in range(size)]
    for i in range(n):
        for j in range(n):
            value = m[i][j]
            re_v = value.real if isinstance(value, complex) else float(value)
            im_v = value.imag if isinstance(value, complex) else 0.0
            real[i][j] = re_v
            real[j][i] = re_v
            real[i][j + n] = -im_v
            real[j + n][i] = -im_v
            real[i + n][j] = im_v
            real[j + n][i] = im_v
            real[i + n][j + n] = re_v
            real[j + n][i + n] = re_v
    eigs = jacobi_eigenvalues_real(real, max_sweeps=max_sweeps)
    # Each eigenvalue of A appears twice; take every other one.
    return sorted(eigs[::2][:n])


def power_iteration(m: Matrix, v0: Vector | None = None, iterations: int = 500, tol: float = 1e-12) -> Tuple[complex, Vector]:
    """
    Dominant eigenpair of a matrix by power iteration.

    Returns ``(eigenvalue, eigenvector)``.  This is the "computing eigen
    values" technique referenced in the course notes: multiply the matrix by
    an eigenvector repeatedly and the eigenvector direction is preserved.

    The eigenvalue is estimated with the **Rayleigh quotient**
    ``lambda = v^dagger A v / v^dagger v``, which is exact for eigenvectors
    and stable for near-eigenvectors.

    .. note::
       Power iteration needs a *unique* dominant eigenvalue.  If the
       largest ``|lambda|`` is repeated (as for the Hadamard gate, whose
       eigenvalues are ``+1`` and ``-1``) the iteration oscillates between
       the two eigendirections instead of converging.  Use
       :func:`eigenpairs_2x2` in that case.
    """
    n, _ = dims(m)
    v = list(v0) if v0 is not None else [complex(1, 0)] + [complex(0, 0)] * (n - 1)
    norm = math.sqrt(sum(abs(x) ** 2 for x in v))
    if norm > 0:
        v = [x / norm for x in v]
    lam = complex(0, 0)
    prev_lam = complex(0, 0)
    for _ in range(iterations):
        w = [sum(m[i][j] * v[j] for j in range(n)) for i in range(n)]
        wnorm = math.sqrt(sum(abs(x) ** 2 for x in w))
        if wnorm < 1e-15:
            break
        w = [x / wnorm for x in w]
        # Rayleigh quotient of the current vector.
        num = sum(v[i].conjugate() * sum(m[i][j] * v[j] for j in range(n)) for i in range(n))
        den = sum(abs(x) ** 2 for x in v)
        new_lam = num / den if den else complex(0, 0)
        delta = max(abs(w[i] - v[i]) for i in range(n))
        v = w
        lam = new_lam
        if abs(new_lam - prev_lam) < tol and delta < 1e-12:
            break
        prev_lam = new_lam
    return lam, v


# --------------------------------------------------------------------------
# Display
# --------------------------------------------------------------------------
def format_matrix(m: Matrix, fmt: str = "{:>8.3f}") -> str:
    """Render a matrix as an aligned text table (real and imaginary parts)."""
    if not m:
        return "[]"
    rows = len(m)
    cols = len(m[0])
    cells = []
    for r in range(rows):
        for c in range(cols):
            v = m[r][c]
            if isinstance(v, complex) and abs(v.imag) > 1e-12:
                cells.append(fmt.format(v.real) + fmt.format(v.imag).rjust(0) + "i")
            else:
                cells.append(fmt.format(v.real if isinstance(v, complex) else v))
    widths = [max(len(cells[r * cols + c]) for r in range(rows)) for c in range(cols)]
    out = []
    for r in range(rows):
        out.append("[" + "  ".join(cells[r * cols + c].rjust(widths[c]) for c in range(cols)) + "]")
    return "\n".join(out)
