#!/usr/bin/env python3
"""
L11 -- Reversible gates, multi-qubit systems and entanglement.

Course sections: 8 (Reversible and Irreversible State Transformations),
9 (Multi-Qubit Systems) and 10 (Entanglement).

Run me::

    python labs/L11_reversible_entanglement/lab.py

What you will build
-------------------
* The reversible gate catalogue: X, CNOT, Toffoli, SWAP, Fredkin.
* Why the Toffoli is the *universal reversible gate*.
* Multi-qubit states, and why 2^n amplitudes is the whole story.
* The Bell state, and a numerical proof that it is entangled (it cannot be
  written as a product).
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

lab = Lab("L11", "Reversible gates, multi-qubit systems and entanglement")


# ---------------------------------------------------------------------------
lab.section("1. Reversible state transformations")
# ---------------------------------------------------------------------------
lab.step("A NOT gate is a reversible transformation.")

sv = q.StateVector.zero(1)
after = sv.apply_single(q.X, 0)
lab.note(f"|0> --X--> {after.to_dirac()} --X--> {after.apply_single(q.X, 0).to_dirac()}")
lab.check("X is its own inverse", after.apply_single(q.X, 0).to_dirac() == sv.to_dirac())
lab.check("X is unitary", la.is_unitary(q.X))
lab.note("A reversible transformation is a *permutation* of the basis states: no "
         "information is lost, so no information can be recovered that was not there.")


# ---------------------------------------------------------------------------
lab.section("2. Multi-qubit systems")
# ---------------------------------------------------------------------------
lab.step("Two qubits have four basis states; three have eight.")

for n in (1, 2, 3, 4):
    sv = q.StateVector.zero(n)
    lab.note(f"{n} qubit(s): {len(sv.amplitudes)} amplitudes, "
             f"{len(sv.basis_labels())} basis states, "
             f"state = {sv.to_dirac()}")

lab.check("2 qubits have 4 basis states", len(q.StateVector.zero(2).amplitudes) == 4)
lab.check("3 qubits have 8 basis states", len(q.StateVector.zero(3).amplitudes) == 8)
lab.check("10 qubits have 1024 basis states", len(q.StateVector.zero(10).amplitudes) == 1024)
lab.note("A multi-qubit state is a column matrix of 2^n complex numbers.  The whole "
         "of quantum computing is manipulating that column matrix.")


# ---------------------------------------------------------------------------
lab.section("3. CNOT and Toffoli")
# ---------------------------------------------------------------------------
lab.step("The controlled gates in action.")

rows = []
for bits in ("00", "01", "10", "11"):
    sv = q.StateVector.from_bitstring(bits)
    cnot = sv.apply_cnot(0, 1)
    rows.append((bits, cnot.to_dirac()))
lab.show(viz.table(["input", "after CNOT(q0->q1)"], rows))
lab.check("CNOT maps |00> to |00>", q.StateVector.from_bitstring("00").apply_cnot(0, 1).to_dirac() == "|00>")
lab.check("CNOT maps |01> to |01>", q.StateVector.from_bitstring("01").apply_cnot(0, 1).to_dirac() == "|01>")
lab.check("CNOT maps |10> to |11>", q.StateVector.from_bitstring("10").apply_cnot(0, 1).to_dirac() == "|11>")
lab.check("CNOT maps |11> to |10>", q.StateVector.from_bitstring("11").apply_cnot(0, 1).to_dirac() == "|10>")
lab.note("CNOT is a *bit flip conditioned on a control bit* -- exactly the XOR gate of "
         "lab L03, but reversible.  The control qubit is NOT changed.")

lab.step("Toffoli (CCNOT) in its three configurations.")
for bits in ("000", "011", "110", "111"):
    sv = q.StateVector.from_bitstring(bits)
    lab.note(f"  |{bits}> --CCNOT(q0,q1;q2)--> {sv.apply_toffoli(0, 1, 2).to_dirac()}")
lab.check("Toffoli in AND configuration: |110> -> |111>",
          q.StateVector.from_bitstring("110").apply_toffoli(0, 1, 2).to_dirac() == "|111>")
lab.check("Toffoli in AND configuration: |100> unchanged",
          q.StateVector.from_bitstring("100").apply_toffoli(0, 1, 2).to_dirac() == "|100>")
lab.check("Toffoli in NOT configuration: |111> -> |110>",
          q.StateVector.from_bitstring("111").apply_toffoli(0, 1, 2).to_dirac() == "|110>")
lab.check("Toffoli in fanout configuration: |110> -> |111>",
          q.StateVector.from_bitstring("110").apply_toffoli(0, 1, 2).to_dirac() == "|111>")
lab.note("These three configurations are exactly how the course uses CCNOT: AND, NOT "
         "and FANOUT.  The Toffoli is the *universal reversible gate*.")


# ---------------------------------------------------------------------------
lab.section("4. The Toffoli is universal for reversible computation")
# ---------------------------------------------------------------------------
lab.step("Build any classical function out of Toffoli gates.")

lab.note("AND  A,B -> T    = Toffoli(A, B; T)          with T starting in |0>")
lab.note("NOT  T           = Toffoli(C, C; T)          with a constant-1 qubit C")
lab.note("COPY A -> B      = Toffoli(C, A; B)          with a constant-1 qubit C")
lab.note("XOR  A,B -> A    = Toffoli(A,B;C), Toffoli(A,B;C), CNOT(B->A)  with C=|0>")


# Verify the XOR-of-2 construction numerically (A on q0, B on q1, ancilla C on q2).
def xor_two_to_a(a, b):
    """A ^= B using the compute / uncompute / apply pattern."""
    sv = q.StateVector.from_bitstring(f"{a}{b}0")
    sv = sv.apply_toffoli(0, 1, 2)   # compute: C = A AND B
    sv = sv.apply_toffoli(0, 1, 2)   # uncompute: C back to 0
    sv = sv.apply_cnot(1, 0)         # apply:  A = A XOR B
    return sv.to_dirac()


lab.show(viz.table(["A", "B", "after A ^= B (3 Toffolis)"],
                    [(a, b, xor_two_to_a(a, b)) for a in (0, 1) for b in (0, 1)]))
lab.check("the Toffoli XOR construction is correct",
          all(xor_two_to_a(a, b) == f"|{a ^ b}{b}0>" for a in (0, 1) for b in (0, 1)),
          "A ^= B, B unchanged, the ancilla restored to |0>")


# Copy, using a constant-1 ancilla.
def copy_a_to_b(a):
    sv = q.StateVector.from_bitstring(f"{a}10")
    sv = sv.apply_toffoli(1, 0, 2)   # controls: q1 (the constant 1) and q0 (=A); target q2
    return sv.to_dirac()


lab.show(viz.table(["A", "after COPY A -> B (C=1 is the ancilla)"],
                    [(a, copy_a_to_b(a)) for a in (0, 1)]))
lab.check("the Toffoli COPY construction is correct",
          all(copy_a_to_b(a) == f"|{a}1{a}>" for a in (0, 1)))
lab.note("Note the rule: a Toffoli's TARGET must differ from its controls -- "
         "otherwise the operation is not reversible.  The two CONTROLS may be the "
         "same qubit, which is how you build a controlled-NOT from a Toffoli.")
lab.note("Because every classical gate can be built from Toffoli, and every quantum "
         "gate can be built from Toffoli + Hadamard + phase gates, a quantum computer "
         "can run any classical algorithm -- and then some.")


# ---------------------------------------------------------------------------
lab.section("5. SWAP and Fredkin")
# ---------------------------------------------------------------------------
lab.step("SWAP exchanges two qubits; Fredkin swaps them conditionally.")

lab.check("SWAP maps |10> to |01>", q.StateVector.from_bitstring("10").apply_two(q.SWAP, 0, 1).to_dirac() == "|01>")
lab.check("SWAP is its own inverse",
          q.StateVector.from_bitstring("10").apply_two(q.SWAP, 0, 1).apply_two(q.SWAP, 0, 1).to_dirac() == "|10>")
lab.check("Fredkin with control 0 does nothing",
          q.StateVector.from_bitstring("010").apply_three(q.CSWAP, 0, 1, 2).to_dirac() == "|010>")
lab.check("Fredkin with control 1 swaps",
          q.StateVector.from_bitstring("110").apply_three(q.CSWAP, 0, 1, 2).to_dirac() == "|101>")
lab.note("SWAP is the same trick as the X gates on a qubit: it is just 'move the "
         "information'.  Fredkin is a *controlled* SWAP.")


# ---------------------------------------------------------------------------
lab.section("6. The Bell state")
# ---------------------------------------------------------------------------
lab.step("Prepare the Bell state with H and CNOT.")

bell = q.bell_state()
lab.note(f"|Phi+> = {bell.to_dirac()}")
lab.show(bell.probability_table())
lab.check("the Bell state has two equal components",
          abs(bell.amplitudes[0].real - 1 / math.sqrt(2)) < 1e-12 and
          abs(bell.amplitudes[3].real - 1 / math.sqrt(2)) < 1e-12)
lab.check("the middle amplitudes are zero",
          abs(bell.amplitudes[1]) < 1e-12 and abs(bell.amplitudes[2]) < 1e-12)


# ---------------------------------------------------------------------------
lab.section("7. Proving that the Bell state is entangled")
# ---------------------------------------------------------------------------
lab.step("Try to write |Phi+> as |a> (x) |b> -- it is impossible.")

# If |Phi+> = |a> (x) |b> with |a> = (a0, a1) and |b> = (b0, b1), then
# the amplitudes would be (a0 b0, a0 b1, a1 b0, a1 b1).  The Bell state has
# (c, 0, 0, c), so a0*b1 = 0 and a1*b0 = 0 while a0*b0 != 0 and a1*b1 != 0.
# That forces a1 = 0 and b1 = 0 -- contradicting a1*b1 != 0.
lab.note("A product state |a>(x)|b> has amplitudes (a0b0, a0b1, a1b0, a1b1).")
lab.note("The Bell state has (c, 0, 0, c): a0*b1 = 0 and a1*b0 = 0, but a0*b0 != 0 "
         "and a1*b1 != 0.")
lab.note("a0*b0 != 0 forces a0 != 0 and b0 != 0.")
lab.note("a0*b1 = 0 then forces b1 = 0, so a1*b1 = 0 -- a contradiction.")

prod = la.kron([[1 / math.sqrt(2)], [1 / math.sqrt(2)]], [[1 / math.sqrt(2)], [1 / math.sqrt(2)]])
lab.show("the closest product state |+>(x)|+> =\n" + la.format_matrix(prod))
lab.note("|Phi+> = (|00> + |11>)/sqrt(2) is NOT that state -- and no product state "
         "matches it.  The Bell state is genuinely entangled.")

product_state = q.StateVector([prod[i][0] for i in range(4)])
lab.check("the entanglement entropy of the Bell state is 1 bit",
          abs(bell.entropy() - 1.0) < 1e-9)
lab.check("the product state |+>(x)|+> has zero entanglement entropy",
          abs(product_state.entropy()) < 1e-9)
lab.check("the Bell state is entangled", q.is_entangled(bell))
lab.note("The entropy is 1 bit for a 2-qubit maximally entangled pair, and 0 for any "
         "product state.  This is a numerical, quantitative definition of "
         "entanglement.")


# ---------------------------------------------------------------------------
lab.section("8. The signature of entanglement: perfect correlation")
# ---------------------------------------------------------------------------
lab.step("Measure both qubits in the same basis.")

counts = bell.histogram(__import__("random").Random(3), shots=4000)
lab.show(viz.histogram(counts))
lab.check("only 00 and 11 ever occur", set(counts) <= {"00", "11"})
lab.check("they occur equally often", abs(counts.get("00", 0) - counts.get("11", 0)) < 200)
lab.note("The outcomes are perfectly correlated, yet each one alone is uniformly "
         "random.  You always get 0-0 or 1-1 -- never 0-1.")

lab.step("Now measure them in DIFFERENT bases and the correlation vanishes.")
import random as _random

same = 0
for _ in range(4000):
    sv = bell.copy()
    # Measure qubit 0 in the Z basis, qubit 1 in the X basis
    # (a Hadamard before measuring turns the Z measurement into an X one).
    b0, sv = sv.measure_qubit(0, _random.Random())
    sv = sv.apply_single(q.H, 1)
    b1, sv = sv.measure_qubit(1, _random.Random())
    same += 1 if b0 == b1 else 0
lab.note(f"agreement when measuring in different bases: {same / 4000:.4f} (chance = 0.5)")
lab.check("different bases give random agreement", abs(same / 4000 - 0.5) < 0.05)
lab.note("A classical pair of correlated coins could reproduce the same-basis "
         "result, but NOT this: the correlation vanishes the moment you look from a "
         "different angle.  That is the signature of true entanglement.")


# ---------------------------------------------------------------------------
lab.section("9. The GHZ state and scaling")
# ---------------------------------------------------------------------------
lab.step("The GHZ state generalises the Bell state to n qubits.")

for n in (2, 3, 4):
    ghz = q.ghz_state(n)
    lab.note(f"  GHZ({n}) = {ghz.to_dirac()}   entropy = {ghz.entropy():.4f} bits")
lab.check("GHZ(3) has an entanglement entropy of 1 bit", abs(q.ghz_state(3).entropy() - 1.0) < 1e-9)
lab.note("The entanglement entropy of a GHZ state is 1 bit for ANY cut, because its "
         "Schmidt rank is 2.  A *maximally* entangled register of n qubits has n/2 bits "
         "of entropy: two Bell pairs (4 qubits) have 2 bits, and a 100-qubit maximally "
         "entangled state has 50.")
# Two *crossed* Bell pairs: (q0,q2) and (q1,q3).  Crossing them means the
# 2|2 cut separates the two halves of each pair, giving 2 bits of entropy.
max_ent = q.StateVector.zero(4).apply_single(q.H, 0).apply_cnot(0, 2)
max_ent = max_ent.apply_single(q.H, 1).apply_cnot(1, 3)
lab.note(f"two Bell pairs: {max_ent.to_dirac()}")
lab.note(f"  entanglement entropy = {max_ent.entropy():.4f} bits")
lab.check("two Bell pairs have 2 bits of entanglement", abs(max_ent.entropy() - 2.0) < 1e-9)


if __name__ == "__main__":
    sys.exit(lab.finish())
