"""
Complex numbers, conjugates, polar form and Euler's formula.

This module is a dependency-free re-implementation of the complex-number
material covered in Section 3 of QC101.  Everything here is plain Python so
that it can also run inside a browser (Pyodide) with zero installs.

The representation of a complex number is the Python builtin ``complex``.
For a number ``z = a + b*i`` we have ``z.real == a`` and ``z.imag == b``.

Author: QC101 Study Pack
"""

from __future__ import annotations

import cmath
import math
from typing import Iterable, List, Sequence, Tuple

__all__ = [
    "add",
    "sub",
    "mul_real",
    "div_real",
    "mul",
    "div",
    "conjugate",
    "squared_magnitude",
    "magnitude",
    "to_polar",
    "from_polar",
    "euler",
    "power",
    "nth_roots",
    "sqrt_i",
    "pretty",
]


# --------------------------------------------------------------------------
# Addition / subtraction
# --------------------------------------------------------------------------
def add(a: complex, b: complex) -> complex:
    """Return ``a + b``."""
    return a + b


def sub(a: complex, b: complex) -> complex:
    """Return ``a - b``."""
    return a - b


# --------------------------------------------------------------------------
# Scalar (real number) multiplication / division
# --------------------------------------------------------------------------
def mul_real(k: float, z: complex) -> complex:
    """Multiply a complex number by a real scalar: ``k * (a + bi) = ka + kbi``."""
    return k * z


def div_real(z: complex, k: float) -> complex:
    """Divide a complex number by a non-zero real scalar."""
    if k == 0:
        raise ZeroDivisionError("cannot divide by zero")
    return z / k


# --------------------------------------------------------------------------
# Complex x Complex multiplication and division
# --------------------------------------------------------------------------
def mul(a: complex, b: complex) -> complex:
    """Multiply two complex numbers, treating ``i`` as an unknown with ``i**2 = -1``."""
    return a * b


def div(a: complex, b: complex) -> complex:
    """
    Divide ``a / b`` using the complex-conjugate method.

    ``a / b = (a * conj(b)) / (b * conj(b)) = (a * conj(b)) / |b|^2``

    The denominator becomes a real number, which is the whole trick.
    """
    if b == 0:
        raise ZeroDivisionError("cannot divide by zero")
    num = a * conjugate(b)
    den = squared_magnitude(b)
    return num / den


# --------------------------------------------------------------------------
# Conjugate, magnitude
# --------------------------------------------------------------------------
def conjugate(z: complex) -> complex:
    """Return the complex conjugate ``a - bi``."""
    return z.conjugate()


def squared_magnitude(z: complex) -> float:
    """Return ``|z|^2 = a^2 + b^2`` (equivalently ``z * conj(z)``)."""
    return z.real * z.real + z.imag * z.imag


def magnitude(z: complex) -> float:
    """Return ``|z| = sqrt(a^2 + b^2)``."""
    return math.sqrt(squared_magnitude(z))


# --------------------------------------------------------------------------
# Polar form and Euler's formula
# --------------------------------------------------------------------------
def euler(r: float, theta: float) -> complex:
    """
    Euler's formula: ``r * e^(i*theta) = r*(cos(theta) + i*sin(theta))``.

    ``theta`` is in radians.
    """
    return r * cmath.exp(1j * theta)


def to_polar(z: complex) -> Tuple[float, float]:
    """
    Convert ``a + bi`` to polar form ``(r, theta)``.

    ``r = sqrt(a^2 + b^2)`` and ``theta = atan2(b, a)`` (radians).
    """
    return cmath.polar(z)


def from_polar(r: float, theta: float) -> complex:
    """Convert polar form ``(r, theta)`` back to ``a + bi``."""
    return cmath.rect(r, theta)


def power(z: complex, exponent: float) -> complex:
    """
    Complex exponentiation via polar form: ``z**p = r**p * e^(i*p*theta)``.

    This is how fractional powers (e.g. square roots) are computed exactly.
    """
    if z == 0:
        if exponent == 0:
            return complex(1.0, 0.0)
        return complex(0.0, 0.0)
    r, theta = cmath.polar(z)
    return cmath.rect(r**exponent, exponent * theta)


def nth_roots(z: complex, n: int) -> List[complex]:
    """
    Return the ``n`` distinct ``n``-th roots of ``z``.

    Roots are ``r**(1/n) * e^(i*(theta + 2*pi*k)/n)`` for ``k = 0 .. n-1``.
    """
    if n < 1:
        raise ValueError("n must be a positive integer")
    if z == 0:
        return [complex(0.0, 0.0)]
    r, theta = cmath.polar(z)
    root_r = r ** (1.0 / n)
    return [cmath.rect(root_r, (theta + 2 * math.pi * k) / n) for k in range(n)]


def sqrt_i() -> Tuple[complex, complex]:
    """
    The two square roots of ``i``:

        ``sqrt(i) = 1/sqrt(2) + i/sqrt(2)``  and  ``-1/sqrt(2) - i/sqrt(2)``

    Verified from Euler's formula: ``i = e^(i*pi/2)`` so
    ``i^(1/2) = e^(i*pi/4) = cos(pi/4) + i sin(pi/4)``.
    """
    s = 1.0 / math.sqrt(2.0)
    return (complex(s, s), complex(-s, -s))


# --------------------------------------------------------------------------
# Pretty printing
# --------------------------------------------------------------------------
def pretty(z: complex, places: int = 4) -> str:
    """
    Render a complex number in the familiar ``a + bi`` style used in the course.

    ``pretty(3 + 4j)`` -> ``'3 + 4i'``
    """
    a, b = z.real, z.imag
    if abs(b) < 10 ** (-places):
        return f"{a:.{places}g}"
    if abs(a) < 10 ** (-places):
        return f"{b:.{places}g}i"
    sign = "+" if b >= 0 else "-"
    return f"{a:.{places}g} {sign} {abs(b):.{places}g}i"


def format_list(values: Iterable[complex], places: int = 4) -> str:
    """Render an iterable of complex numbers as a bracketed list."""
    return "[" + ", ".join(pretty(v, places) for v in values) + "]"


def polar_pretty(z: complex, places: int = 4) -> str:
    """Render a complex number in polar form, e.g. ``1.414 e^(i*0.7854)``."""
    r, theta = cmath.polar(z)
    return f"{r:.{places}g} e^(i*{theta:.{places}g})"
