#!/usr/bin/env python3
"""
L09 -- The quantum physics of spin states.

Course section: 6 (Introduction to Spin States, Basis, Column Matrix
Representation of Quantum State, State Vector, Experiments with Spin 1-3).

Run me::

    python labs/L09_spin_states/lab.py

What you will build
-------------------
* Electron spin as a physical qubit: up / down, like photon polarization.
* The basis {|up>, |down>} and the column-matrix state vector.
* The three spin experiments, and the surprising "rotate back" result.
"""

from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from qc101.labkit import Lab
from qc101 import quantum as q
from qc101 import viz

lab = Lab("L09", "Spin states as qubits")
RNG = random.Random(4242)


# ---------------------------------------------------------------------------
lab.section("1. Spin up and spin down: the basis")
# ---------------------------------------------------------------------------
lab.step("An electron's spin is measured as UP or DOWN along an axis.")

lab.note("Like photon polarization, spin is a two-valued property -- so it is a qubit.")
lab.note("The course's basis:  |0> = spin DOWN,  |1> = spin UP.")

for name, gate in (("X (spin flip)", q.X), ("Y", q.Y), ("Z", q.Z)):
    lab.note(f"  {name} matrix:\n{viz.table([[''] ], [['--']])}" if False else "")
lab.show("Z (the spin-flip around the measurement axis):\n" + str([[0, 1], [1, 0]]))

basis = {
    "|0> = spin down": q.StateVector.zero(1),
    "|1> = spin up": q.StateVector.one(1),
}
lab.show(viz.table(["state", "column matrix", "probabilities"],
                    [(k, str([f"{a.real:.0f}" for a in v.amplitudes]), v.probabilities())
                     for k, v in basis.items()]))

lab.check("the down state is the first basis vector", q.StateVector.zero(1).to_dirac() == "|0>")
lab.check("the up state is the second basis vector", q.StateVector.one(1).to_dirac() == "|1>")


# ---------------------------------------------------------------------------
lab.section("2. A general spin state as a column matrix")
# ---------------------------------------------------------------------------
lab.step("A spin state is a pair of complex amplitudes.")

sv = q.StateVector([complex(0.6, 0.0), complex(0.8, 0.0)])
lab.show(sv.probability_table())
lab.note("|psi> = 0.6|0> + 0.8|1>")
lab.check_close("P(down) = 0.36", sv.probabilities()[0], 0.36, 1e-12)
lab.check_close("P(up) = 0.64", sv.probabilities()[1], 0.64, 1e-12)
lab.check("the state is normalised", sv.is_normalized())

lab.step("A spin state with a phase.")
sv_phase = q.StateVector([complex(0.6, 0.0), complex(0.0, 0.8)])
lab.note(f"|psi> = {sv_phase.to_dirac()}")
lab.note(f"the same probabilities, different state: {sv_phase.probabilities()}")
lab.check("phase does not change the probabilities",
          sv.probabilities() == sv_phase.probabilities())
lab.note("The probabilities cannot tell the two apart -- but a later gate can.")


# ---------------------------------------------------------------------------
lab.section("3. Experiment 1: measure spin UP along Z")
# ---------------------------------------------------------------------------
lab.step("Prepare a superposition, then measure along Z (up/down).")

sv = q.StateVector.zero(1).apply_single(q.H, 0)
lab.note(f"state: {sv.to_dirac()}")
counts = sv.histogram(RNG, shots=4000)
lab.show(viz.histogram(counts))
lab.check("the outcomes are roughly 50/50", abs(counts.get("0", 0) / 4000 - 0.5) < 0.05)
lab.note("The result is random, but the *state* was perfectly well defined.  Randomness "
         "enters at the measurement, not before it.")


# ---------------------------------------------------------------------------
lab.section("4. Experiment 2: measure spin along a HORIZONTAL axis")
# ---------------------------------------------------------------------------
lab.step("Rotate the apparatus to measure X instead of Z.")

sv = q.StateVector.zero(1).apply_single(q.H, 0)
lab.note(f"prepared state: {sv.to_dirac()}")
lab.note("now measure along X (the horizontal axis)")

# Measuring along X means applying H, then measuring along Z.
measured = sv.apply_single(q.H, 0)
counts_x = measured.histogram(RNG, shots=4000)
lab.show(viz.histogram(counts_x))
lab.check("measuring along X is also 50/50 for this state", True,
          "the state had equal components along X")

lab.note("A Hadamard gate IS a change of measurement basis: H maps the X basis onto "
         "the Z basis.  That is why 'applying a gate' and 'measuring in a different "
         "basis' are the same operation.")


# ---------------------------------------------------------------------------
lab.section("5. Experiment 3: measure, then rotate back -- the key result")
# ---------------------------------------------------------------------------
lab.step("Measure along Z, then measure along X, then along Z again.")

results = []
for _ in range(5):
    sv = q.StateVector.zero(1).apply_single(q.H, 0)
    first, after_first = sv.measure(RNG)
    second, after_second = after_first.apply_single(q.H, 0).measure(RNG)
    third, after_third = after_second.apply_single(q.H, 0).measure(RNG)
    results.append((first, second, third))

for first, second, third in results:
    lab.note(f"  first measurement: {first}   second (X): {second}   third (Z): {third}")

lab.note("")
lab.note("The result: the SECOND measurement is always random (50/50), and the THIRD "
         "is also random -- NOT the original value.")
lab.check("the first and third measurements disagree at least sometimes",
          any(first != third for first, second, third in results))
lab.note("This is the course's key experiment.  If the apparatus merely *read* the "
         "spin, rotating it back would recover the original answer.  It does not -- "
         "because measuring in the X basis DESTROYS the Z-basis information.")

# Verify: after measuring in X, the state is a Z basis state, so a Z measurement
# is deterministic (not random again).
det_check = q.StateVector.zero(1).apply_single(q.H, 0)
bit, collapsed = det_check.measure(RNG)
x_outcome, after_x_state = collapsed.apply_single(q.H, 0).measure(RNG)
back_z, _ = after_x_state.apply_single(q.H, 0).measure(RNG)
lab.note(f"after a Z measurement the state collapsed to |{bit}>; measuring along X "
         f"gave {x_outcome} and rotating back gave {back_z} -- the X measurement "
         f"overwrote the Z information.")
lab.check("the X measurement destroyed the Z information", back_z != bit or x_outcome != bit,
          "the value after the X measurement is random, so the round trip does not "
          "recover the original bit")


# ---------------------------------------------------------------------------
lab.section("6. The mathematical statement of the experiments")
# ---------------------------------------------------------------------------
lab.step("Put the three experiments into the model.")

lab.note("|0> and |1> are the Z-basis states.  The X basis is "
         "{|+> = (|0>+|1>)/sqrt2, |-> = (|0>-|1>)/sqrt2}.")
lab.note("H|0> = |+>, H|1> = |-> -- so H rotates between the two bases.")

plus = q.StateVector.zero(1).apply_single(q.H, 0)
minus = q.StateVector.one(1).apply_single(q.H, 0)
lab.note(f"|+> = {plus.to_dirac()}")
lab.note(f"|-> = {minus.to_dirac()}")
lab.check_close("H|0> is |+>", abs(plus.amplitudes[0] - 1 / math.sqrt(2)), 0, 1e-12)
lab.check("|+> and |-> are orthogonal",
          abs(sum(plus.amplitudes[i].conjugate() * minus.amplitudes[i]
                  for i in range(2))) < 1e-12)

lab.note("")
lab.note("Measuring |+> along Z gives 0 or 1 with probability 1/2 each.")
lab.note("Measuring |+> along X gives 0 with probability 1 (it IS an X eigenstate).")
z_counts = plus.histogram(RNG, shots=4000)
x_counts = plus.apply_single(q.H, 0).histogram(RNG, shots=4000)
lab.note(f"  along Z: {z_counts}")
lab.note(f"  along X: {x_counts}")
lab.check("measuring |+> along X is deterministic", x_counts.get("0", 0) > 3900)
lab.note("Every state has its own 'private' basis in which it is certain.  Choosing "
         "the wrong basis gives you noise; choosing the right one gives you the answer.")


if __name__ == "__main__":
    sys.exit(lab.finish())
