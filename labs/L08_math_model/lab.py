#!/usr/bin/env python3
"""
L08 -- Developing a math model for quantum physics.

Course section: 5 (Modeling Physics with Math, Subtractive Probabilities
Through Complex Numbers, Modeling Superposition Through Matrices, Overview of
Math Model).

Run me::

    python labs/L08_math_model/lab.py

What you will build
-------------------
* The central insight of the course: **quantum amplitudes can be negative or
  complex, so probabilities can *subtract*.**
* The double-slit experiment, simulated: amplitudes add, then you square.
* The complete math model, assembled into one object you can query.
"""

from __future__ import annotations

import cmath
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from qc101.labkit import Lab
from qc101 import quantum as q
from qc101 import viz

lab = Lab("L08", "A math model for quantum physics")


# ---------------------------------------------------------------------------
lab.section("1. Why classical probability is not enough")
# ---------------------------------------------------------------------------
lab.step("Classical probabilities only ever ADD.")

p_a, p_b = 0.5, 0.5
lab.note(f"Two independent 50/50 outcomes: P(A or B) = {p_a + p_b} (they add).")
lab.note("But in quantum mechanics, two paths can *cancel*: the total probability "
         "can be SMALLER than either path alone, and even exactly zero.")

lab.note("The fix: work with AMPLITUDES (complex numbers) instead of probabilities.")
lab.note("   amplitude = sqrt(probability) * e^(i*phase)")
lab.note("   probability = |amplitude|^2")
lab.note("Amplitude addition can give cancellation; probability addition cannot.")


# ---------------------------------------------------------------------------
lab.section("2. The double slit, simulated")
# ---------------------------------------------------------------------------
lab.step("Two paths, each with amplitude a, reach the same point on the screen.")

lab.note("Path 1 amplitude: a1, Path 2 amplitude: a2")
lab.note("Total amplitude: a1 + a2    (note: ADDITION of amplitudes)")
lab.note("Total probability: |a1 + a2|^2")

cases = [
    ("both in phase (constructive)", 0.5 + 0.0j, 0.5 + 0.0j),
    ("opposite phase (destructive)", 0.5 + 0.0j, -0.5 + 0.0j),
    ("90 degrees apart", 0.5 + 0.0j, 0.5j),
]
rows = []
for label, a1, a2 in cases:
    total = a1 + a2
    rows.append((label, f"{a1} + {a2}", f"{total}", f"{abs(total) ** 2:.4f}",
                 f"{(abs(a1) ** 2) + (abs(a2) ** 2):.4f}"))
lab.show(viz.table(
    ["case", "amplitudes", "sum", "|sum|^2 (quantum)", "sum of |a|^2 (classical)"],
    rows,
))

lab.check_close("in-phase amplitudes give probability 1", abs((0.5 + 0.5) ** 2), 1.0, 1e-12)
lab.check_close("opposite amplitudes cancel to probability 0", abs((0.5 - 0.5) ** 2), 0.0, 1e-12)
lab.check("classical addition would predict 0.5 in the destructive case",
          abs((0.5 - 0.5) ** 2) < (0.5 ** 2 + 0.5 ** 2),
          "the quantum probability is SMALLER than the classical one")
lab.note("This single fact -- that amplitudes add and probabilities are their squared "
         "magnitudes -- explains interference, and therefore the entire power of "
         "quantum computing.")


# ---------------------------------------------------------------------------
lab.section("3. A two-path interferometer")
# ---------------------------------------------------------------------------
lab.step("Model a Mach-Zehnder-like setup with a phase on one path.")

for phase_deg in (0, 60, 120, 180):
    phase = cmath.exp(1j * math.radians(phase_deg))
    # First beam splitter sends 1/sqrt(2) down each path; the phase shifter adds
    # `phase` on one path; the second beam splitter recombines with 1/sqrt(2).
    a1 = 0.5                       # path 1: (1/sqrt2)(1/sqrt2)
    a2 = 0.5 * phase               # path 2: (1/sqrt2)(1/sqrt2) * phase
    p0 = abs(a1 + a2) ** 2         # detector 0 (the "same" port)
    p1 = abs(a1 - a2) ** 2         # detector 1 (the "other" port)
    lab.note(f"phase {phase_deg:>3} deg -> P(detector 0) = {p0:.4f}, P(detector 1) = {p1:.4f}")
    if phase_deg == 180:
        lab.check_close("a 180-degree phase sends all the light to detector 1", p1, 1.0, 1e-12)
        lab.check_close("and none to detector 0", p0, 0.0, 1e-12)
    lab.check_close(f"total probability is conserved at {phase_deg} deg", p0 + p1, 1.0, 1e-12)
lab.note("Sweeping the phase moves the interference pattern -- this is how a "
         "quantum Mach-Zehnder interferometer measures a tiny change in path length.")


# ---------------------------------------------------------------------------
lab.section("4. The math model, assembled")
# ---------------------------------------------------------------------------
lab.step("Everything the course needs, in one place.")

lab.note("1. A system of n qubits has a state vector of 2^n complex amplitudes.")
lab.note("2. The amplitudes are normalised: sum of |a_i|^2 = 1.")
lab.note("3. A gate is a unitary matrix U; the new state is U|psi>.")
lab.note("4. Measurement samples an outcome i with probability |a_i|^2 and collapses "
         "the state to |i>.")
lab.note("5. Because amplitudes can cancel, the probability of an outcome can be "
         "smaller than any individual path's contribution -- interference.")

sv = q.StateVector.zero(2).apply_single(q.H, 0).apply_cnot(0, 1)
lab.note(f"\nExample: H on q0 then CNOT gives {sv.to_dirac()}")
lab.note(f"Probabilities: {dict(zip(sv.basis_labels(), [round(p, 4) for p in sv.probabilities()]))}")
lab.check("the state is normalised", sv.is_normalized())
lab.check("H then CNOT gives the Bell state", sv.to_dirac().endswith("|00> + 0.7071 |11>"))
lab.note("Note that the Bell state is a superposition of TWO basis states -- and the "
         "probability of '01' is exactly 0.  A classical description cannot produce "
         "that; a classical probability model would predict 25% for each outcome.")


# ---------------------------------------------------------------------------
lab.section("5. Reversible versus irreversible, in the model")
# ---------------------------------------------------------------------------
lab.step("Every gate preserves the norm; measurement does not.")

before = q.StateVector.zero(2).apply_single(q.H, 0)
after = before.apply_single(q.X, 0)
lab.check("a unitary gate preserves the norm",
          abs(sum(before.probabilities()) - sum(after.probabilities())) < 1e-12)
lab.check("X is its own inverse",
          after.apply_single(q.X, 0).to_dirac() == before.to_dirac())

outcome, collapsed = before.measure()
lab.note(f"after measurement: outcome {outcome:02b}, state {collapsed.to_dirac()}")
lab.check("measurement destroys the superposition",
          collapsed.to_dirac() in ("|00>", "|10>"),
          "q0 is the leftmost bit in this course, so H on q0 gives |00> or |10>")
lab.note("The information about the pre-measurement angle is gone -- you cannot "
         "recover it, no matter how clever you are.  This is why the *measurement* "
         "step is the only non-reversible part of a quantum algorithm.")


# ---------------------------------------------------------------------------
lab.section("6. The model predicts the photon experiments")
# ---------------------------------------------------------------------------
lab.step("Check the model against the photon polarizer behaviour.")

from qc101 import photon as ph

# A 45-degree photon measured at 0 degrees: amplitude for '0' is cos(45), for '1' is sin(45).
angle = 45.0
amp0 = math.cos(math.radians(angle))
amp1 = math.sin(math.radians(angle))
lab.note(f"45-degree photon -> amplitudes (cos45, sin45) = ({amp0:.4f}, {amp1:.4f})")
lab.note(f"probabilities: P(0) = {amp0 ** 2:.4f}, P(1) = {amp1 ** 2:.4f}")
lab.check_close("the model reproduces Malus's law", amp0**2, ph.malus_transmission(45, 0), 1e-12)
lab.check_close("P(0) + P(1) = 1", amp0**2 + amp1**2, 1.0, 1e-12)
lab.note("The polarizer and the qubit model agree: the filter at 0 degrees measures "
         "the photon in the {horizontal, vertical} basis.")


if __name__ == "__main__":
    sys.exit(lab.finish())
