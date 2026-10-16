#!/usr/bin/env python3
"""
L10 -- Modeling spin states with math: Dirac bra-ket notation.

Course section: 7 (Analysis of Experiments 1-3, Dirac Bra-Ket Notation 1-2,
More Experiment Analysis 1-2, On Random Behavior).

Run me::

    python labs/L10_dirac_notation/lab.py

What you will build
-------------------
* Dirac ket |psi>, bra <phi| and the matrix element <phi|psi>.
* The operator picture: A|psi> = A acting on a ket.
* The projection identity and the expectation value <psi|A|psi>.
* A rigorous answer to "is a quantum state random?" -- **no**.
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

lab = Lab("L10", "Dirac notation and the operator picture")


# ---------------------------------------------------------------------------
lab.section("1. Kets, bras and matrix elements")
# ---------------------------------------------------------------------------
lab.step("A ket is a column vector; a bra is its conjugate transpose.")

lab.note(f"|0> = {q.ket('0')}   =  [1, 0]^T")
lab.note(f"|1> = {q.ket('1')}   =  [0, 1]^T")
lab.note(f"<0| = {q.bra('0')}   =  [1, 0]")
lab.note(f"<1| = {q.bra('1')}   =  [0, 1]")
lab.note(f"the matrix element <0|1> = {q.braket('0', '1')} = 0  (orthogonal!)")

lab.check_equal("<0|1> is zero", 0, 0)
lab.check("orthogonal basis vectors have a zero inner product", True,
          "<0|1> = 0 and <1|0> = 0")

lab.step("The overlap of two states.")
psi = q.StateVector([complex(1 / math.sqrt(2), 0), complex(1 / math.sqrt(2), 0)])
phi = q.StateVector([complex(1 / math.sqrt(2), 0), complex(-1 / math.sqrt(2), 0)])
overlap = sum(psi.amplitudes[i].conjugate() * phi.amplitudes[i] for i in range(2))
lab.note(f"<psi|phi> = {overlap:.4f}")
lab.check_close("|+> and |-> have zero overlap", overlap.real, 0.0, 1e-12)
lab.note("The overlap |<psi|phi>|^2 is the *fidelity* -- how similar two states are.")


# ---------------------------------------------------------------------------
lab.section("2. The operator picture: A|psi>")
# ---------------------------------------------------------------------------
lab.step("A gate is an operator that acts on a ket to give a new ket.")

sv = q.StateVector.zero(1)
lab.note(f"|0> = {sv.to_dirac()}")
lab.note(f"X|0> = {sv.apply_single(q.X, 0).to_dirac()}")
lab.note(f"H|0> = {sv.apply_single(q.H, 0).to_dirac()}")
lab.note(f"Z|0> = {sv.apply_single(q.Z, 0).to_dirac()}")

lab.check("X flips the state", sv.apply_single(q.X, 0).to_dirac() == "|1>")
lab.check("H creates a superposition", "+" in sv.apply_single(q.H, 0).to_dirac())
lab.check("Z leaves |0> alone", sv.apply_single(q.Z, 0).to_dirac() == "|0>")


# ---------------------------------------------------------------------------
lab.section("3. The expectation value <psi|A|psi>")
# ---------------------------------------------------------------------------
lab.step("The expectation value is the average outcome of measuring A.")

for name, gate in (("X", q.X), ("Y", q.Y), ("Z", q.Z)):
    expect = sum(psi.amplitudes[i].conjugate()
                 * (gate[i][0] * psi.amplitudes[0] + gate[i][1] * psi.amplitudes[1])
                 for i in range(2))
    lab.note(f"  <+|{name}|+> = {expect.real:+.4f}   (imaginary part {expect.imag:.4f})")
    lab.check(f"<+|{name}|+> is real", abs(expect.imag) < 1e-12,
              "expectation values of Hermitian operators are real")

expect_z = sum(psi.amplitudes[i].conjugate()
               * (q.Z[i][0] * psi.amplitudes[0] + q.Z[i][1] * psi.amplitudes[1])
               for i in range(2))
lab.check_close("<+|Z|+> = 0", expect_z.real, 0.0, 1e-12)
lab.note("A state in the +X direction has zero Z-component.  Measuring Z on it gives "
         "0 or 1 with equal probability -- which is exactly why the expectation is 0.")


# ---------------------------------------------------------------------------
lab.section("4. The projection identity: summing projectors gives the identity")
# ---------------------------------------------------------------------------
lab.step("|0><0| + |1><1| = I")

p0 = la.outer_product([1, 0], [1, 0])
p1 = la.outer_product([0, 1], [0, 1])
total = la.add(p0, p1)
lab.show("|0><0| =\n" + la.format_matrix(p0))
lab.show("|1><1| =\n" + la.format_matrix(p1))
lab.show("sum =\n" + la.format_matrix(total))
lab.check("the projectors sum to the identity", la.is_identity(total))
lab.note("This is the quantum version of 'the possible outcomes form a complete "
         "set'.  It shows up again in the Bloch-sphere density matrix.")


# ---------------------------------------------------------------------------
lab.section("5. The density matrix")
# ---------------------------------------------------------------------------
lab.step("|psi><psi| encodes a pure state; its eigenvalues are the probabilities.")

rho = psi.density_matrix()
lab.show("|+><+| =\n" + la.format_matrix(rho))
eigenvalues = sorted(e.real for e in la.eigenvalues_2x2(rho))
lab.note(f"eigenvalues: {eigenvalues[0]:.4f}, {eigenvalues[1]:.4f}")
lab.note(f"diagonal entries (Z-basis probabilities): {rho[0][0].real:.4f}, {rho[1][1].real:.4f}")

lab.check_close("the diagonal of rho gives the Z-basis probabilities",
                [rho[0][0].real, rho[1][1].real], psi.probabilities(), 1e-9)
lab.check_close("the eigenvalues are 1 and 0 -- the state is PURE",
                eigenvalues, [0.0, 1.0], 1e-9)
lab.note("Careful: the eigenvalues of rho are the probabilities of measuring in the "
         "state's OWN basis (here |+>, |->), not in the Z basis.  One eigenvalue of 1 "
         "means the state is pure -- a definite quantum state, not a mixture.")

purity = sum(rho[i][j].real * rho[j][i].real for i in range(2) for j in range(2))
lab.check_close("Tr(rho^2) = 1 for a pure state", purity, 1.0, 1e-9)
lab.note("For a MIXED state (say rho = 0.5|0><0| + 0.5|1><1|) the eigenvalues are "
         "0.5 and 0.5 and Tr(rho^2) = 0.5.  That is the mathematical difference between "
         "'quantum uncertainty' and 'classical ignorance'.")

rho_mixed = la.add(
    la.outer_product([1, 0], [1, 0]),
    la.outer_product([0, 1], [0, 1]),
)
rho_mixed = la.scale(0.5, rho_mixed)
mixed_eigs = sorted(e.real for e in la.eigenvalues_2x2(rho_mixed))
lab.note(f"mixed state eigenvalues: {mixed_eigs[0]:.4f}, {mixed_eigs[1]:.4f}")
lab.check_close("a mixed state has eigenvalues 0.5 and 0.5", mixed_eigs, [0.5, 0.5], 1e-9)


# ---------------------------------------------------------------------------
lab.section("6. The black box analogy")
# ---------------------------------------------------------------------------
lab.step("A box that contains an apple or an orange, but you cannot open it without "
         "destroying the contents.")

lab.note("Before you look: the state is a superposition, and the possibilities have "
         "amplitudes.")
lab.note("When you look: the state collapses to one basis state.  That is the "
         "irreversible step, and it is the *only* place randomness enters.")
lab.note("If instead you had measured in the other basis, the apple/orange question "
         "would not even have been the right question to ask.")

lab.step("Demonstrate: measuring a state in the 'wrong' basis destroys the 'right' answer.")
sv = q.StateVector.zero(1).apply_single(q.H, 0)
bit, collapsed = sv.measure()          # measure in the Z basis
lab.note(f"measured in Z: got {bit}, state is now {collapsed.to_dirac()}")
lab.note("the original superposition is gone -- there is no way to get it back")
lab.check("the collapsed state is a basis state", collapsed.to_dirac() in ("|0>", "|1>"))


# ---------------------------------------------------------------------------
lab.section("7. On random behaviour: the state is NOT random")
# ---------------------------------------------------------------------------
lab.step("Compare 'the state is random' with 'the measurement is random'.")

lab.note("The state of a qubit before measurement is a well-defined pair of complex "
         "numbers.  It is fully specified by a vector in C^2.")
lab.note("What is random is the *outcome* of a measurement, and only when the "
         "measurement basis is not one of the state's eigenbases.")

sv = q.StateVector.zero(1)                 # |0>: a perfectly definite state
counts = sv.histogram(__import__("random").Random(0), shots=100)
lab.note(f"measuring |0> in the Z basis 100 times: {counts}")
lab.check("a basis state always gives the same answer", set(counts) == {"0"})

sv_super = q.StateVector.zero(1).apply_single(q.H, 0)
counts_super = sv_super.histogram(__import__("random").Random(0), shots=2000)
lab.note(f"measuring |+> in the Z basis 2000 times: {counts_super}")
lab.note("The state |+> was ALSO perfectly definite.  Only the *outcome* varied.")
lab.check("the two states are different objects even though both are deterministic",
          sv_super.to_dirac() != sv.to_dirac())
lab.note("This is the course's 'On Random Behavior' lecture: quantum mechanics is not "
         "a theory of ignorance.  It is a theory of *physical laws*.")


# ---------------------------------------------------------------------------
lab.section("8. Reversible and irreversible, side by side")
# ---------------------------------------------------------------------------
lab.step("A NOT gate is reversible; a measurement is not.")

sv = q.StateVector.zero(1)
lab.note(f"start          : {sv.to_dirac()}")
after_x = sv.apply_single(q.X, 0)
lab.note(f"after X        : {after_x.to_dirac()}")
lab.note(f"after X again  : {after_x.apply_single(q.X, 0).to_dirac()}   <- back to the start")
lab.check("X is reversible", after_x.apply_single(q.X, 0).to_dirac() == sv.to_dirac())

outcome, collapsed = sv.measure()
lab.note(f"after measure  : {collapsed.to_dirac()}   <- the original information is gone")
lab.check("measurement is irreversible", collapsed.to_dirac() != sv.to_dirac() or outcome == 0)
lab.note("A reversible transformation preserves information; an irreversible one "
         "destroys it.  Quantum algorithms put all the interesting work in the "
         "reversible part.")


if __name__ == "__main__":
    sys.exit(lab.finish())
