#!/usr/bin/env python3
"""
L05 -- Complex numbers: the arithmetic of quantum amplitudes.

Course section: 3.3 (Introduction to Complex Numbers, Imaginary i, Addition,
Subtraction, Multiplication, Division, Complex Conjugates, Squared
Magnitude, Euler's Formula, Polar Form, Fractional Powers, 2D Coordinates).

Run me::

    python labs/L05_complex_numbers/lab.py

What you will build
-------------------
* Arithmetic on complex numbers done by hand, then verified with code.
* The complex conjugate and squared magnitude -- the two operations that
  appear in every quantum formula.
* Division by the conjugate trick.
* Polar form, Euler's formula, fractional powers and complex roots.
"""

from __future__ import annotations

import cmath
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from qc101.labkit import Lab
from qc101 import complexnum as cn
from qc101 import viz

lab = Lab("L05", "Complex numbers")


# ---------------------------------------------------------------------------
lab.section("1. The imaginary unit i")
# ---------------------------------------------------------------------------
lab.step("i = sqrt(-1), so i^2 = -1.  Every complex number is a + b*i.")

lab.show(viz.table(
    ["expression", "value", "real part", "imaginary part"],
    [
        ("3 + 4i", cn.pretty(3 + 4j), 3.0, 4.0),
        ("-7 + 2i", cn.pretty(-7 + 2j), -7.0, 2.0),
        ("6 - 2i", cn.pretty(6 - 2j), 6.0, -2.0),
    ],
))
lab.check_equal("3 + 4i has real part 3", (3 + 4j).real, 3.0)
lab.check_equal("3 + 4i has imaginary part 4", (3 + 4j).imag, 4.0)
lab.note("A *real* number is a special case: b = 0.  Quantum amplitudes are complex "
         "because the phase of an amplitude is physically meaningful.")


# ---------------------------------------------------------------------------
lab.section("2. Addition and subtraction")
# ---------------------------------------------------------------------------
lab.step("Add and subtract, keeping real and imaginary parts separate.")

cases = [
    ((2, 3), (1, 1), "add"),
    ((7, -2), (0, 3), "sub"),
    ((9, 0), (0, 1), "add"),
]
rows = []
for (ar, ai), (br, bi), op in cases:
    a, b = complex(ar, ai), complex(br, bi)
    r = cn.add(a, b) if op == "add" else cn.sub(a, b)
    rows.append((cn.pretty(a), op, cn.pretty(b), cn.pretty(r)))
lab.show(viz.table(["A", "op", "B", "A op B"], rows))
lab.check_equal("2+3i + 1+1i = 3+4i", cn.add(2 + 3j, 1 + 1j), 3 + 4j)
lab.check_equal("7-2i - 0+3i = 7-5i", cn.sub(7 - 2j, 0 + 3j), 7 - 5j)


# ---------------------------------------------------------------------------
lab.section("3. Multiplication by a real number, and complex x complex")
# ---------------------------------------------------------------------------
lab.step("Scalar multiplication: k*(a+bi) = ka + kbi.")

lab.check_equal("3*(2+3i) = 6+9i", cn.mul_real(3, 2 + 3j), 6 + 9j)
lab.check_equal("-4*(2-3i) = -8+12i", cn.mul_real(-4, 2 - 3j), -8 + 12j)
lab.check_equal("(4+6i)/2 = 2+3i", cn.div_real(4 + 6j, 2), 2 + 3j)
lab.check_equal("(7+2i)/-3 = -7/3 - 2/3 i", cn.div_real(7 + 2j, -3), complex(-7 / 3, -2 / 3))

lab.step("Complex x complex: treat i as an unknown and use i^2 = -1.")

lab.note("(3+4i)(5+6i) = 15 + 18i + 20i + 24i^2 = 15 + 38i - 24 = -9 + 38i")
lab.check_equal("(3+4i)(5+6i) = -9+38i", cn.mul(3 + 4j, 5 + 6j), -9 + 38j)
lab.note("(-7+2i)(3-4i) = -21 + 28i + 6i - 8i^2 = -21 + 34i + 8 = -13 + 34i")
lab.check_equal("(-7+2i)(3-4i) = -13+34i", cn.mul(-7 + 2j, 3 - 4j), -13 + 34j)
lab.note("(6-2i)(-9+4i) = -54 + 24i + 18i - 8i^2 = -54 + 42i + 8 = -46 + 42i")
lab.check_equal("(6-2i)(-9+4i) = -46+42i", cn.mul(6 - 2j, -9 + 4j), -46 + 42j)
lab.note("The imaginary part of a product is a_sum*b_real + a_real*b_sum - the "
         "'subtractive' structure that makes interference possible.")


# ---------------------------------------------------------------------------
lab.section("4. The complex conjugate and squared magnitude")
# ---------------------------------------------------------------------------
lab.step("conj(a+bi) = a-bi, and |z|^2 = z * conj(z) = a^2 + b^2.")

lab.check_equal("conj(3+4i) = 3-4i", cn.conjugate(3 + 4j), 3 - 4j)
lab.check_equal("|3+4i|^2 = 25", cn.squared_magnitude(3 + 4j), 25.0)
lab.check_equal("|7-6i|^2 = 85", cn.squared_magnitude(7 - 6j), 85.0)
lab.check("|z|^2 is always a non-negative real number",
          cn.squared_magnitude(complex(-3, -4)) == 25.0)
lab.note("This is the single most important formula in the course: a state vector's "
         "probability of outcome k is |amplitude_k|^2.  The conjugate is what makes the "
         "imaginary parts cancel.")


# ---------------------------------------------------------------------------
lab.section("5. Division by the conjugate trick")
# ---------------------------------------------------------------------------
lab.step("Multiply numerator and denominator by the conjugate of the denominator.")

lab.note("a/b = (a * conj(b)) / (b * conj(b)) = (a * conj(b)) / |b|^2")
# (3+4i)/(7-6i) = (3+4i)(7+6i) / 85 = (-3 + 46i) / 85
lab.check_equal("(3+4i)/(7-6i) = (-3 + 46i)/85",
                cn.div(3 + 4j, 7 - 6j), complex(-3 / 85, 46 / 85))
# (6-2i)/(-9+4i) = (6-2i)(-9-4i) / 97 = (-62 - 6i) / 97
lab.check_equal("(6-2i)/(-9+4i) = (-62 - 6i)/97",
                cn.div(6 - 2j, -9 + 4j), complex(-62 / 97, -6 / 97))
lab.check_close("the division equals the builtin (real part)",
                cn.div(3 + 4j, 7 - 6j).real, ((3 + 4j) / (7 - 6j)).real, 1e-12)
lab.check_close("the division equals the builtin (imaginary part)",
                cn.div(3 + 4j, 7 - 6j).imag, ((3 + 4j) / (7 - 6j)).imag, 1e-12)


# ---------------------------------------------------------------------------
lab.section("6. Polar form, Euler's formula and 2D coordinates")
# ---------------------------------------------------------------------------
lab.step("Every complex number is a point (a, b) in the plane, or a polar point (r, theta).")

rows = []
for z in (1 + 0j, 0 + 1j, 3 + 4j, -1 - 1j, 0 - 2j):
    r, theta = cn.to_polar(z)
    rows.append((cn.pretty(z), f"{r:.4f}", f"{theta:.4f}", cn.polar_pretty(z)))
lab.show(viz.table(["z", "r = |z|", "theta (rad)", "polar form"], rows))

lab.check_close("|3+4i| = 5", cn.magnitude(3 + 4j), 5.0, 1e-12)
lab.check_close("Euler: r*e^(i*theta) reproduces the original", cn.from_polar(*cn.to_polar(3 + 4j)), 3 + 4j, 1e-12)
lab.note("Euler's formula e^(i*theta) = cos(theta) + i*sin(theta) is the bridge between "
         "the Cartesian and polar views -- and the bridge between rotation matrices and "
         "phase gates.")


# ---------------------------------------------------------------------------
lab.section("7. Fractional powers and complex roots")
# ---------------------------------------------------------------------------
lab.step("Square root of i using Euler's formula.")

roots = cn.sqrt_i()
lab.note("i = e^(i*pi/2)  =>  sqrt(i) = e^(i*pi/4) = cos(pi/4) + i*sin(pi/4)")
lab.note(f"sqrt(i) = {cn.pretty(roots[0])}  and  {cn.pretty(roots[1])}")
lab.check_close("the principal root squares to i", roots[0] ** 2, 1j, 1e-12)
lab.check_close("the other root also squares to i", roots[1] ** 2, 1j, 1e-12)
lab.check_close("the principal root is (1+i)/sqrt(2)", roots[0], complex(1 / math.sqrt(2), 1 / math.sqrt(2)), 1e-12)

lab.step("The three cube roots of 11.")
cube_roots = cn.nth_roots(11 + 0j, 3)
for r in cube_roots:
    lab.note(f"  {cn.pretty(r)}   (cube = {cn.pretty(r ** 3)})")
    lab.check_close("each cube root cubes back to 11", r**3, 11 + 0j, 1e-9)
lab.check("there are exactly 3 cube roots", len(cube_roots) == 3)
lab.note("This is the structure behind the quantum Fourier transform: complex roots of "
         "unity are what let you 'rotate' a register of qubits.")


# ---------------------------------------------------------------------------
lab.section("8. Why quantum amplitudes must be complex")
# ---------------------------------------------------------------------------
lab.step("Compare a real superposition with a complex one.")

from qc101 import quantum as q

real_super = q.StateVector([complex(1 / math.sqrt(2), 0), complex(1 / math.sqrt(2), 0)])
complex_super = q.StateVector([complex(1 / math.sqrt(2), 0), complex(0, 1 / math.sqrt(2))])
lab.note(f"real     : {real_super.to_dirac()}")
lab.note(f"complex  : {complex_super.to_dirac()}")
lab.note("The measurement probabilities are identical, but the states are different -- "
         "and the S gate can tell them apart:")
lab.note(f"  S(real)    = {real_super.apply_single(q.S, 0).to_dirac()}")
lab.note(f"  S(complex) = {complex_super.apply_single(q.S, 0).to_dirac()}")
lab.check("the two states are distinguishable by a phase gate",
          real_super.apply_single(q.S, 0).amplitudes != complex_super.apply_single(q.S, 0).amplitudes,
          "phase is information")
lab.note("Probabilities alone are not the whole story: the *phase* of the amplitudes is "
         "what interference uses.  That is why the course insists on complex numbers.")


if __name__ == "__main__":
    sys.exit(lab.finish())
