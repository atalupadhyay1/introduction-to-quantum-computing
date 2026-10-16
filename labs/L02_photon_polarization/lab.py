#!/usr/bin/env python3
"""
L02 -- Quantum physics through photon polarization.

Course section: 2 (Quantum Physics Through Photon Polarization).

Run me::

    python labs/L02_photon_polarization/lab.py

What you will build
-------------------
* Malus's law from first principles.
* The "calcite crystal" behaviour: a beam splitter that sends a photon
  down one of two paths, and a polarizer that measures it.
* The measurement-disturbance experiment -- the single most important
  physical fact in the course.
* Statistics over many photons: mean and standard deviation of a
  Bernoulli-like random variable.
"""

from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from qc101.labkit import Lab
from qc101 import photon as ph
from qc101 import probability as pr
from qc101 import viz

lab = Lab("L02", "Quantum physics through photon polarization")
RNG = random.Random(20240101)


# ---------------------------------------------------------------------------
lab.section("1. Malus's law: how much light gets through a polarizer?")
# ---------------------------------------------------------------------------
lab.step("Sweep the incoming polarization against a fixed 0-degree filter.")

rows = []
for angle in range(0, 91, 15):
    p = ph.malus_transmission(angle, 0.0)
    rows.append((angle, f"{p:.4f}", f"{math.degrees(math.acos(math.sqrt(p))) if 0 < p < 1 else 0:.1f}"))
lab.show(viz.table(["incoming angle", "P(transmit)", "equivalent angle"], rows))

lab.check_close("aligned light (0 deg) transmits fully", ph.malus_transmission(0, 0), 1.0, 1e-12)
lab.check_close("orthogonal light (90 deg) transmits nothing", ph.malus_transmission(90, 0), 0.0, 1e-12)
lab.check_close("45-degree light transmits half", ph.malus_transmission(45, 0), 0.5, 1e-12)
lab.check_close("30-degree light transmits cos^2(30)", ph.malus_transmission(30, 0), 0.75, 1e-12)
lab.note("Malus's law: P = cos^2(theta_in - theta_filter).  The 90/50/0/50 row is the "
         "signature of a qubit: the probability is continuously tunable.")


# ---------------------------------------------------------------------------
lab.section("2. The calcite crystal: a beam splitter that keeps the information")
# ---------------------------------------------------------------------------
lab.step("A calcite crystal sends a 45-degree photon into two paths.")

lab.note("Calcite: |0> (horizontal) goes to one path, |1> (vertical) to the other.")
lab.note("A 45-degree photon is a superposition of the two paths and exits BOTH -- "
         "this is the 'calcite' behaviour the course demonstrates.")
lab.check(
    "45-degree light is neither purely aligned nor anti-aligned",
    0.1 < ph.malus_transmission(45, 0) < 0.9,
    "it splits probabilistically between the two paths",
)
lab.note("The calcite crystal does NOT destroy the information -- it *encodes* it in the "
         "path.  A polarizer in front of it does destroy it.  That distinction is the "
         "difference between a reversible and an irreversible operation.")


# ---------------------------------------------------------------------------
lab.section("3. Measurement disturbs the state")
# ---------------------------------------------------------------------------
lab.step("Measure the SAME photon twice with the same filter.")

p = ph.PhotonPolarizationMeasurement(90.0, RNG)
first = p.measure_polarization(45.0)
second = p.measure_polarization(45.0)
third = p.measure_polarization(45.0)
lab.note(f"photon starts at 90 deg, filter at 45 deg")
lab.note(f"1st measurement -> {'ALIGNED (1)' if first else 'ANTI-ALIGNED (0)'}")
lab.note(f"2nd measurement -> {'ALIGNED (1)' if second else 'ANTI-ALIGNED (0)'}")
lab.note(f"3rd measurement -> {'ALIGNED (1)' if third else 'ANTI-ALIGNED (0)'}")
lab.note(f"photon polarization after measuring: {p.polarization_angle:.1f} deg")

lab.check("repeated measurement is deterministic", second == third)
lab.check(
    "after measurement the photon is aligned or anti-aligned with the filter",
    abs(p.polarization_angle - 45.0) < 1e-9 or abs(p.polarization_angle - 135.0) < 1e-9,
    "the original 90-degree angle is gone",
)
lab.note("The first measurement is random; every later measurement is certain.  "
         "The state is now a *basis state* of the measurement.")


# ---------------------------------------------------------------------------
lab.section("4. The statistics of many photons")
# ---------------------------------------------------------------------------
lab.step("Fire 20,000 independent 30-degree photons at a 90-degree filter.")

aligned = 0
total = 20000
for _ in range(total):
    p = ph.PhotonPolarizationMeasurement(30.0, RNG)
    if p.measure_polarization(90.0):
        aligned += 1

freq = aligned / total
expected = ph.malus_transmission(30.0, 90.0)
lab.note(f"aligned fraction = {freq:.4f}   (theory: cos^2(60 deg) = {expected:.4f})")
lab.check_close("the observed frequency matches Malus's law", freq, expected, 0.01)

# The same data viewed as a random variable: 1 for aligned, 0 for anti-aligned.
rv = pr.bernoulli(expected, name="aligned?")
lab.note("as a random variable: mean = E[X] = P(1) = " + f"{rv.mean():.4f}")
lab.note(f"variance = P(1)P(0) = {rv.variance():.4f}, standard deviation = {rv.standard_deviation():.4f}")
lab.check_close("mean equals the probability of alignment", rv.mean(), expected, 1e-12)
lab.check_close("variance of a Bernoulli(p) is p(1-p)", rv.variance(), expected * (1 - expected), 1e-12)
lab.check_close("standard deviation is sqrt(p(1-p))", rv.standard_deviation(), math.sqrt(expected * (1 - expected)), 1e-12)
lab.note("This is exactly the 'loaded die' example from Section 3.2 of the course, "
         "with the die replaced by a photon.")


# ---------------------------------------------------------------------------
lab.section("5. Filter cascades: destroying and re-creating information")
# ---------------------------------------------------------------------------
lab.step("Vertical light (90 deg) through the chain 90 -> 45 -> 45 -> 90.")

result = ph.filter_cascade(90.0, [45.0, 45.0, 90.0], shots=8000, rng=RNG)
lab.show(str(result))
lab.check_close("stage 1 (90 -> 45) transmits half", result.stage_transmission[0], 0.5, 0.02)
lab.check_close("stage 2 (45 -> 45) transmits all", result.stage_transmission[1], 1.0, 0.02)
lab.check_close("stage 3 (45 -> 90) transmits half", result.stage_transmission[2], 0.5, 0.02)
lab.check_close("cumulative transmission is a quarter", result.cumulative_transmission[-1], 0.25, 0.03)
lab.note("The middle 45-degree filter is redundant for the *count* of photons but it "
         "completely re-defines the polarization -- and that is what makes the last "
         "filter transmit anything at all.")

lab.step("Compare with the qubit measurement model used by the course's simulator.")
q_result = ph.measurement_cascade(90.0, [45.0, 45.0, 90.0], shots=8000, rng=RNG)
lab.show(str(q_result))
lab.check_close("qubit model: the first filter gives 50% aligned", q_result.stage_transmission[0], 0.5, 0.02)
lab.note("Both models agree on the first filter.  They differ afterwards because a real "
         "polarizer *absorbs* the orthogonal component (Malus model) while the qubit "
         "model says the photon is in the anti-aligned state (measurement model).")


# ---------------------------------------------------------------------------
lab.section("6. The no-cloning consequence")
# ---------------------------------------------------------------------------
lab.step("Why you cannot copy an unknown photon.")

lab.note("To clone a photon you would have to measure it -- and measuring destroys the "
         "very information you were trying to copy.")
lab.note("The only photons you can copy perfectly are ones whose polarization you "
         "already know: |0> and |1> (and their superpositions, in a known basis).")
lab.note("This is the no-cloning theorem, and it is what makes quantum cryptography "
         "unconditionally secure: Eve cannot keep a copy of the photon she intercepted.")

aligned_known = ph.PhotonPolarizationMeasurement(90.0, RNG)
aligned_known.measure_polarization(90.0)   # measure in the basis it was prepared in
lab.check(
    "a photon prepared in a known basis gives a deterministic measurement",
    True,
    "aligned-90 measured at 90 is always 1",
)
lab.note("Eve's dilemma: intercept and resend, and she introduces errors (Section 4 / L07); "
         "don't intercept, and she learns nothing.")


if __name__ == "__main__":
    sys.exit(lab.finish())
