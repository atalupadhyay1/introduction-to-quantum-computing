#!/usr/bin/env python3
"""
L13 -- The quantum computing model: circuits, gates and compilation.

Course section: 12 (Quantum Computing Model).

Run me::

    python labs/L13_quantum_computing_model/lab.py

What you will build
-------------------
* The circuit model end to end: build -> compile -> run -> read out.
* A mini "compiler" that turns a gate list into a single unitary matrix.
* The distinction between a *state vector* (simulator) and *counts*
  (hardware), and why they are different kinds of answer.
* The three-stage program structure: irreversible init, reversible gates,
  irreversible measurement.
"""

from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from qc101.labkit import Lab
from qc101 import linalg as la
from qc101 import quantum as q
from qc101 import viz

lab = Lab("L13", "The quantum computing model")
RNG = random.Random(8080)


# ---------------------------------------------------------------------------
lab.section("1. A circuit is a list of gates")
# ---------------------------------------------------------------------------
lab.step("Build the Bell-state circuit: H on q0, then CNOT q0 -> q1.")

circuit = [
    ("h", 0),
    ("cx", 0, 1),
]
lab.show(viz.table(["step", "gate", "qubits"],
                    [(i + 1, g[0], ", ".join(map(str, g[1:]))) for i, g in enumerate(circuit)]))


def apply_one(sv, gate):
    """Apply a single gate tuple to a state vector."""
    if gate[0] == "h":
        return sv.apply_single(q.H, gate[1])
    if gate[0] == "x":
        return sv.apply_single(q.X, gate[1])
    if gate[0] == "y":
        return sv.apply_single(q.Y, gate[1])
    if gate[0] == "z":
        return sv.apply_single(q.Z, gate[1])
    if gate[0] == "s":
        return sv.apply_single(q.S, gate[1])
    if gate[0] == "t":
        return sv.apply_single(q.T, gate[1])
    if gate[0] == "cx":
        return sv.apply_cnot(gate[1], gate[2])
    if gate[0] == "ccx":
        return sv.apply_toffoli(gate[1], gate[2], gate[3])
    if gate[0] == "swap":
        return sv.apply_two(q.SWAP, gate[1], gate[2])
    raise ValueError(f"unknown gate {gate[0]}")


def run_circuit(n_qubits, gates, state=None):
    """Apply a list of gates to a state vector and return the result."""
    sv = state if state is not None else q.StateVector.zero(n_qubits)
    for g in gates:
        sv = apply_one(sv, g)
    return sv


result = run_circuit(2, circuit)
lab.note(f"result: {result.to_dirac()}")
lab.check("the circuit produces the Bell state", result.to_dirac().endswith("|00> + 0.7071 |11>"))
lab.check_close("the state is normalised", sum(result.probabilities()), 1.0, 1e-12)


# ---------------------------------------------------------------------------
lab.section("2. Compiling a circuit into one matrix")
# ---------------------------------------------------------------------------
lab.step("Multiply the gate matrices together: U = U_n ... U_2 U_1.")


def gate_matrix(n_qubits, gate):
    """
    Build the full dim x dim matrix of a single gate.

    The matrix is read off by applying the gate to each basis state: the
    basis state that lands in row r tells us ``M[r][c]``.
    """
    dim = 2**n_qubits
    matrix = la.zeros(dim, dim)
    for col in range(dim):
        sv = q.StateVector.from_basis(col, n_qubits)
        sv = apply_one(sv, gate)
        for row, amp in enumerate(sv.amplitudes):
            if abs(amp) > 1e-12:
                matrix[row][col] = amp
    return matrix


def compile_circuit(n_qubits, gates):
    """
    Return the full unitary matrix of a gate list: ``U = U_n ... U_2 U_1``.

    The gates are applied left to right, so each new gate is *pre*-multiplied
    onto the accumulated matrix.
    """
    dim = 2**n_qubits
    total = la.identity(dim)
    for g in gates:
        total = la.mul(gate_matrix(n_qubits, g), total)
    return total


U = compile_circuit(2, circuit)
lab.show("the compiled unitary:\n" + la.format_matrix(U))
lab.check("the compiled matrix is unitary", la.is_unitary(U))
lab.check("the matrix has 4 rows and 4 columns", la.dims(U) == (4, 4))

# Applying the matrix to |00> must give the same answer as the gate list.
via_matrix = [sum(U[i][j] * (1.0 if j == 0 else 0.0) for j in range(4)) for i in range(4)]
lab.note(f"U|00> = {[round(x.real, 4) for x in via_matrix]}")
lab.check("the matrix reproduces the circuit result",
          all(abs(via_matrix[i] - result.amplitudes[i]) < 1e-12 for i in range(4)))


# ---------------------------------------------------------------------------
lab.section("3. The three stages of a quantum program")
# ---------------------------------------------------------------------------
lab.step("init (irreversible) -> gates (reversible) -> measure (irreversible).")

sv = q.StateVector.zero(3)
lab.note("init: |000>")
sv = run_circuit(3, [("h", 0), ("cx", 0, 1), ("cx", 1, 2)], sv)
lab.note(f"gates: {sv.to_dirac()}")
outcome, collapsed = sv.measure(RNG)
lab.note(f"measure: outcome {outcome:03b}, state {collapsed.to_dirac()}")
lab.check("the GHZ state is produced", abs(sv.amplitudes[0].real - 1 / math.sqrt(2)) < 1e-12)
lab.check("measurement collapses to a basis state", collapsed.probabilities().count(1.0) == 1)
lab.note("Everything interesting happens between the irreversible steps.")


# ---------------------------------------------------------------------------
lab.section("4. State vector versus counts")
# ---------------------------------------------------------------------------
lab.step("The same circuit, read out two different ways.")

sv = run_circuit(2, [("h", 0), ("cx", 0, 1)])
lab.note("STATE VECTOR (what the simulator holds):")
lab.show(sv.probability_table())
lab.note("COUNTS (what the hardware returns, after 2000 shots):")
counts = sv.histogram(RNG, shots=2000)
lab.show(viz.histogram(counts))
lab.check("the counts have only two outcomes", set(counts) <= {"00", "11"})
lab.check("the counts are close to the probabilities",
          abs(counts.get("00", 0) / 2000 - 0.5) < 0.05)
lab.note("The state vector is the *complete* description; the counts are a sample "
         "from it.  A real device gives you counts -- so any algorithm must be "
         "designed so that the *distribution* of outcomes carries the answer, not "
         "any single shot.")


# ---------------------------------------------------------------------------
lab.section("5. Reversibility and the inverse circuit")
# ---------------------------------------------------------------------------
lab.step("Every circuit has an inverse: undo each gate in reverse order.")

sv = run_circuit(2, [("h", 0), ("cx", 0, 1), ("h", 1)])
lab.note(f"after the circuit: {sv.to_dirac()}")
inverse = [("h", 1), ("cx", 0, 1), ("h", 0)]
back = run_circuit(2, inverse, sv)
lab.note(f"after the inverse: {back.to_dirac()}")
lab.check("the inverse restores the initial state", back.to_dirac() == "|00>")
lab.note("Self-inverse gates (H, X, CNOT, SWAP, Toffoli) can simply be repeated in the "
         "same order; general gates must be undone in reverse order.")


# ---------------------------------------------------------------------------
lab.section("6. The circuit as a matrix you can inspect")
# ---------------------------------------------------------------------------
lab.step("The adjoint of the circuit unitary is the inverse circuit.")

U = compile_circuit(2, [("h", 0), ("cx", 0, 1)])
U_dag = la.adjoint(U)
lab.show("U^dagger U:\n" + la.format_matrix(la.mul(U_dag, U)))
lab.check("U^dagger U = I", la.is_identity(la.mul(U_dag, U)))
lab.check("the adjoint of the circuit is unitary", la.is_unitary(U_dag))
lab.note("This is the formal statement of 'the gates are reversible': the adjoint of "
         "the whole circuit is the circuit that undoes it.")


# ---------------------------------------------------------------------------
lab.section("7. How many gates is 'big'?")
# ---------------------------------------------------------------------------
lab.step("The cost of a circuit is the number of gates and the width.")

rows = []
for n in (1, 2, 3, 4, 5):
    rows.append((n, 2**n, 16 * 2**n, f"{2**n} x {2**n}"))
lab.show(viz.table(["qubits", "amplitudes", "bytes of state", "matrix size"], rows))
lab.note("A simulator needs memory proportional to 2^n; a real device needs gates "
         "proportional to the circuit depth.  That is the trade-off the course keeps "
         "coming back to.")

lab.check("the state vector grows as 2^n", 2**20 == 1048576)
lab.note("A 50-qubit state vector is 16 MB -- fine.  A 1,000-qubit state vector is "
         "16 TB -- hopeless.  Hence the interest in error-corrected hardware.")


if __name__ == "__main__":
    sys.exit(lab.finish())
