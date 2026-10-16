#!/usr/bin/env python3
"""
L12 -- Superposition and entanglement simulators.

Course section: 11 (Understanding Superposition and Entanglement With Quantum
Simulators).  The original course ships three Java simulators; this lab is
the Python port of all three, plus the extra experiments that make the
physics obvious.

Run me::

    python labs/L12_simulators/lab.py

What you will build
-------------------
* **PhotonPolarizationMeasurement** -- the single-photon simulator.
* **EntangledPhotonMeasurement** -- the two-photon simulator, with the
  conditional probabilities that expose entanglement.
* A state-vector simulator you can drive interactively.
"""

from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from qc101.labkit import Lab
from qc101 import photon as ph
from qc101 import quantum as q
from qc101 import viz

lab = Lab("L12", "Superposition and entanglement simulators")
RNG = random.Random(20250101)


# ---------------------------------------------------------------------------
lab.section("1. The photon simulator")
# ---------------------------------------------------------------------------
lab.step("Port of the course's Java class PhotonPolarizationMeasurement.")

p = ph.PhotonPolarizationMeasurement(90.0, RNG)
outcomes = [p.measure_polarization(45.0) for _ in range(6)]
lab.note("photon at 90 deg, filter at 45 deg, six measurements:")
lab.note("  " + ", ".join("1 (aligned)" if o else "0 (anti-aligned)" for o in outcomes))
lab.check("the first measurement is random", outcomes[0] in (True, False))
lab.check("later measurements are deterministic", all(o == outcomes[0] for o in outcomes[1:]))
lab.note("The photon left the filter aligned or anti-aligned with it -- the original "
         "90-degree polarization is gone forever.")


# ---------------------------------------------------------------------------
lab.section("2. The statistics of the photon simulator")
# ---------------------------------------------------------------------------
lab.step("A 30-degree photon measured at 90 degrees, 20,000 times.")

aligned = 0
for _ in range(20000):
    photon = ph.PhotonPolarizationMeasurement(30.0, RNG)
    if photon.measure_polarization(90.0):
        aligned += 1
freq = aligned / 20000
expected = ph.malus_transmission(30.0, 90.0)
lab.note(f"aligned fraction = {freq:.4f}  (theory: {expected:.4f})")
lab.check_close("the simulator matches Malus's law", freq, expected, 0.01)

lab.step("The same data as a random variable.")
from qc101 import probability as pr

rv = pr.bernoulli(expected, name="aligned")
lab.show(rv.table())
lab.check_close("the mean equals the alignment probability", rv.mean(), expected, 1e-12)
lab.check_close("the standard deviation is sqrt(p(1-p))",
                rv.standard_deviation(), math.sqrt(expected * (1 - expected)), 1e-12)


# ---------------------------------------------------------------------------
lab.section("3. The entangled photon simulator")
# ---------------------------------------------------------------------------
lab.step("Port of the course's Java class EntangledPhotonMeasurement.")

lab.note("The Bell state (|00> + |11>)/sqrt(2) is entered as the four "
         "amplitudes (0.707106, 0, 0, 0.707106).")
pair = ph.EntangledPhotonMeasurement(0.707106, 0, 0, 0.707106, RNG)
pair.set_measurement_angles(90, 90)
lab.show(pair.report_measurement_probability())

probs = pair._outcome_probabilities()
lab.check_close("P(00) = 1/2", probs["00"], 0.5, 1e-4)
lab.check_close("P(11) = 1/2", probs["11"], 0.5, 1e-4)
lab.check_close("P(01) = 0", probs["01"], 0.0, 1e-9)
lab.check_close("P(10) = 0", probs["10"], 0.0, 1e-9)
lab.note("The two photons are ALWAYS found with the same polarization.  That is the "
         "signature of entanglement.")


# ---------------------------------------------------------------------------
lab.section("4. Measuring the entangled pair collapses it")
# ---------------------------------------------------------------------------
lab.step("Perform 12 joint measurements and watch the state change.")

for i in range(12):
    pair = ph.EntangledPhotonMeasurement(0.707106, 0, 0, 0.707106, RNG)
    pair.set_measurement_angles(90, 90)
    result = pair.perform_measurement()
    if i < 4:
        lab.note("  " + result.replace("\n", "  "))

pair = ph.EntangledPhotonMeasurement(0.707106, 0, 0, 0.707106, RNG)
pair.set_measurement_angles(90, 90)
pair.perform_measurement()
lab.note("after one measurement the state is no longer entangled:")
lab.note(f"  amplitudes are now ({pair.p00:.2f}, {pair.p01:.2f}, {pair.p10:.2f}, {pair.p11:.2f})")
lab.check(
    "the collapsed state is a product state",
    abs(pair.p00 * pair.p11 - pair.p01 * pair.p10) < 1e-6,
    "the determinant of the amplitude matrix vanishes -- that is the product test",
)
lab.note("A product state has p00*p11 = p01*p10.  The Bell state has p00*p11 = 0.5 "
         "and p01*p10 = 0, so it violates the product test.")


# ---------------------------------------------------------------------------
lab.section("5. The two simulators agree with the state-vector model")
# ---------------------------------------------------------------------------
lab.step("Cross-check the photon simulator against the qubit simulator.")

for angle in (0, 30, 45, 60, 90):
    # Photon model: probability of 'aligned' at a 0-degree filter.
    p_align = ph.malus_transmission(angle, 0.0)
    # Qubit model: |psi> = cos(theta)|0> + sin(theta)|1>, measured in Z.
    state = q.StateVector([complex(math.cos(math.radians(angle)), 0),
                            complex(math.sin(math.radians(angle)), 0)])
    p_zero = state.probabilities()[0]
    lab.note(f"  {angle:>3} deg: photon model {p_align:.4f}   qubit model {p_zero:.4f}")
    lab.check_close(f"the two models agree at {angle} deg", p_align, p_zero, 1e-12)
lab.note("Same physics, two languages: the photon simulator is the *experiment*, the "
         "state vector is the *model*.")


# ---------------------------------------------------------------------------
lab.section("6. The entangled state in the qubit simulator")
# ---------------------------------------------------------------------------
lab.step("Build the Bell state and measure the two photons separately.")

bell = q.bell_state()
lab.note(f"|Phi+> = {bell.to_dirac()}")
lab.show(bell.probability_table())

agree = 0
for _ in range(4000):
    sv = bell.copy()
    b0, sv = sv.measure_qubit(0, RNG)
    b1, sv = sv.measure_qubit(1, RNG)
    agree += 1 if b0 == b1 else 0
lab.note(f"the two photons agreed in {agree}/4000 measurements")
lab.check("the photons always agree", agree == 4000)

lab.step("Now measure them in different bases -- the correlation disappears.")
agree_x = 0
for _ in range(4000):
    sv = bell.copy()
    b0, sv = sv.measure_qubit(0, RNG)
    sv = sv.apply_single(q.H, 1)
    b1, sv = sv.measure_qubit(1, RNG)
    agree_x += 1 if b0 == b1 else 0
lab.note(f"they agreed in {agree_x}/4000 measurements ({agree_x / 4000:.3f}, chance is 0.5)")
lab.check("different bases give random agreement", abs(agree_x / 4000 - 0.5) < 0.05)
lab.note("This is the *only* thing entanglement adds over a classical pair of "
         "pre-shared random bits: the correlation exists only in a matching basis.")


# ---------------------------------------------------------------------------
lab.section("7. The simulator as an experiment you can steer")
# ---------------------------------------------------------------------------
lab.step("Change the angle and watch the distribution follow.")

lab.show(viz.table(
    ["photon angle", "P(aligned at 0 deg)", "P(aligned at 45 deg)"],
    [(angle, f"{ph.malus_transmission(angle, 0):.4f}", f"{ph.malus_transmission(angle, 45):.4f}")
     for angle in (0, 15, 30, 45, 60, 75, 90)],
))
lab.check("aligned light transmits fully", ph.malus_transmission(0, 0) == 1.0)
lab.check_close("orthogonal light is blocked", ph.malus_transmission(90, 0), 0.0, 1e-12)
lab.note("Change the numbers in the table above and re-run -- the simulator is yours "
         "to experiment with.")


if __name__ == "__main__":
    sys.exit(lab.finish())
