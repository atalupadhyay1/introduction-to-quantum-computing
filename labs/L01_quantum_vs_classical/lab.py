#!/usr/bin/env python3
"""
L01 -- What makes a quantum computer different?

Course section: 1 (Introduction).

Run me::

    python labs/L01_quantum_vs_classical/lab.py

What you will build
-------------------
* A mental (and numerical) model of the difference between the classical
  von Neumann architecture and the quantum circuit model.
* The exponential size of the Hilbert space, and what that buys and costs.
* A *bit* versus a *qubit* comparison table, backed by numbers you compute.
"""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from qc101.labkit import Lab
from qc101 import quantum as q
from qc101 import viz

lab = Lab("L01", "Quantum computing versus classical computing")


# ---------------------------------------------------------------------------
lab.section("1. The von Neumann architecture versus the circuit model")
# ---------------------------------------------------------------------------
lab.step("A classical computer stores state in memory and executes instructions in sequence.")
lab.note("Von Neumann: memory + CPU + sequential instruction stream.")
lab.note("A quantum computer has no 'memory that holds the program'.  It has a *state* "
         "of qubits that is transformed by a sequence of *gates*.")
lab.note("There is no 'fetch-decode-execute' loop -- the whole circuit is a unitary "
         "matrix applied to the state vector.")

lab.check(
    "a classical bit holds 1 of 2 values",
    len([0, 1]) == 2,
    "a bit is a scalar that is either 0 or 1",
)
lab.check(
    "a qubit's state vector has 2 complex amplitudes",
    len(q.StateVector.zero(1).amplitudes) == 2,
    "|psi> = alpha|0> + beta|1>",
)


# ---------------------------------------------------------------------------
lab.section("2. The Hilbert space grows exponentially")
# ---------------------------------------------------------------------------
lab.step("Compute the number of basis states for n qubits.")

rows = []
for n in range(1, 25):
    basis_states = 2**n
    amplitudes = 2 * basis_states          # complex numbers, real + imaginary
    bytes_needed = amplitudes * 16
    rows.append((n, basis_states, f"{bytes_needed:,}"))

lab.show(viz.table(["qubits", "basis states", "bytes for the state vector"], rows))

lab.check("2 qubits have 4 basis states", 2**2 == 4)
lab.check("50 qubits have more than a quadrillion basis states", 2**50 > 10**15)
lab.note("A 300-qubit state vector would need more bytes than the age of the universe "
         "to store -- which is exactly why we *simulate* small systems and *run* "
         "large ones on real hardware.")


# ---------------------------------------------------------------------------
lab.section("3. Classical bits versus qubits")
# ---------------------------------------------------------------------------
lab.step("Compare how many classical bits fit in the same register.")

for n in (10, 20, 30):
    classical_bits = 2**n
    classical_bytes = classical_bits * 8          # one byte per bit
    quantum_bytes = (2**n) * 2 * 16               # state vector of n qubits
    ratio = quantum_bytes / classical_bytes
    lab.note(f"n={n:>3}: a classical register stores {classical_bits:,} bits "
             f"({classical_bytes:,} bytes); the quantum state vector needs "
             f"{quantum_bytes:,} bytes -- {ratio:,.0f}x more.")

lab.check(
    "the quantum state vector is always larger than the matching classical register",
    all((2**n) * 32 > (2**n) * 8 for n in (10, 20, 30)),
    "the state vector stores amplitudes, not just bits",
)
lab.note("The exponential *size* of the state vector is a resource, not a cost: a single "
         "quantum circuit acts on all 2^n amplitudes at once.")


# ---------------------------------------------------------------------------
lab.section("4. Superposition is a different kind of '2 bits at once'")
# ---------------------------------------------------------------------------
lab.step("Contrast 'two classical bits' with 'one qubit in superposition'.")

sv = q.StateVector.zero(1).apply_single(q.H, 0)
probs = sv.probabilities()
lab.note(f"H|0> = {sv.to_dirac()}")
lab.note(f"measurement probabilities: P(0) = {probs[0]:.4f}, P(1) = {probs[1]:.4f}")

lab.check_close("H|0> gives P(0) = 1/2", probs[0], 0.5, 1e-9)
lab.check_close("H|0> gives P(1) = 1/2", probs[1], 0.5, 1e-9)
lab.check_close("the amplitudes have unit magnitude", abs(sv.amplitudes[0]), 1 / math.sqrt(2), 1e-9)

lab.note("A qubit in superposition is NOT '0 and 1 at the same time' in the sense of a "
         "classical unknown.  It is a *complex amplitude pair*; the phase between the "
         "two amplitudes is physical and can be made to interfere.")

# Phase matters: |0> + i|1> behaves differently from |0> + |1> under S.
sv_phase = q.StateVector([complex(1 / math.sqrt(2), 0), complex(0, 1 / math.sqrt(2))])
sv_plain = q.StateVector([complex(1 / math.sqrt(2), 0), complex(1 / math.sqrt(2), 0)])
after_phase = sv_phase.apply_single(q.S, 0)
after_plain = sv_plain.apply_single(q.S, 0)
lab.note(f"S(|0>+i|1>) = {after_phase.to_dirac()}")
lab.note(f"S(|0>+|1>)  = {after_plain.to_dirac()}")
lab.check(
    "the phase of a superposition changes the result of a later gate",
    after_phase.amplitudes != after_plain.amplitudes,
    "phase is a physical degree of freedom",
)
lab.note("Two qubits in superposition can be *entangled*: their joint state cannot be "
         "written as two independent qubits.  That is the subject of labs L11 and L12.")


# ---------------------------------------------------------------------------
lab.section("5. The three stages of a quantum program")
# ---------------------------------------------------------------------------
lab.step("Irreversible initialisation -> reversible gates -> irreversible measurement.")

sv = q.StateVector.zero(3)
lab.note("initialise: |000>  (irreversible: you cannot recover the pre-initialisation state)")
sv = sv.apply_single(q.H, 0)
lab.note(f"apply H on q0: {sv.to_dirac()}  (reversible: H is its own inverse)")
sv = sv.apply_cnot(0, 1)
lab.note(f"apply CNOT q0->q1: {sv.to_dirac()}  (reversible)")
outcome, collapsed = sv.measure()
lab.note(f"measure: outcome {outcome:03b}, state collapses to {collapsed.to_dirac()}  (irreversible)")

lab.check_close("total probability is conserved at every step", sum(sv.probabilities()), 1.0, 1e-9)
lab.check("measurement collapses the state to a basis state", collapsed.probabilities().count(1.0) == 1)
lab.note("This pattern -- irreversible init, reversible core, irreversible readout -- is the "
         "backbone of the whole course.")


# ---------------------------------------------------------------------------
lab.section("6. Superposition is not free: interference is the real resource")
# ---------------------------------------------------------------------------
lab.step("Show that a random-looking answer can be recovered by uncomputing.")

sv = q.StateVector.zero(2)
sv = sv.apply_single(q.H, 0)
sv = sv.apply_cnot(0, 1)
lab.note(f"Bell state: {sv.to_dirac()}")
counts = sv.histogram(__import__("random").Random(0), shots=2000)
lab.show(viz.histogram(counts))
lab.check("a Bell state never produces 01 or 10", set(counts) <= {"00", "11"})
lab.note("Shor's algorithm and Grover's search both work by this trick: create a "
         "superposition, use interference to amplify the amplitudes you want, then "
         "measure.  The measurement is random; the *distribution* is not.")


if __name__ == "__main__":
    sys.exit(lab.finish())
