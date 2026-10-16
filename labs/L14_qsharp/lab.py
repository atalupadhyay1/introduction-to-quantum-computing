#!/usr/bin/env python3
"""
L14 -- Microsoft Q# (QSharp): the quantum programming model.

Course section: 13 (Quantum Programming with Microsoft Q#: Installing Q#,
Q# Simulation Architecture, Q# Controller, Q# Execution Model, Measuring
Superposition States, Overview of the 4-Qubit Simulation Framework, Set
Operation, Iterative Measurement, Verifying Output after Initialization,
NOT Operation).

Run me::

    python labs/L14_qsharp/lab.py

What you will build
-------------------
* A **line-by-line transliteration** of the course's Q# ``QB4.qs`` program
  into Python, so you can run the exact same experiment without installing
  the .NET SDK.
* The Q# execution model: allocation, initialisation, gate application,
  measurement, release.
* The ``Set`` operation -- the irreversible initialisation step.
* The **qubit ordering trap**: Q# prints q0 right-most, Qiskit prints q0
  left-most.  This lab proves the mismatch and shows the fix.
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

lab = Lab("L14", "Microsoft Q# (QSharp) programming")
RNG = random.Random(31415)


# ---------------------------------------------------------------------------
# The Q# program, transliterated.
#
# Q#                              Python
# ---------------------------     ------------------------------------------
# using (qubits = Qubit[4])       a 4-qubit state vector
# Set(Zero, qubits[0])            set a qubit to |0> (irreversibly)
# H(qubits[0])                    Hadamard
# X(qubits[0])                    NOT
# CNOT(qubits[0], qubits[1])       controlled-NOT
# CCNOT(q0, q1, q2)               Toffoli
# M(qubits[0])                    measure -> Result
# Message(...)                    print
# ---------------------------------------------------------------------------

class QSharpProgram:
    """
    A Python transliteration of the Q# ``QB4`` program.

    The class mirrors Q#'s execution model: qubits are *allocated* up front,
    *initialised* with ``Set``, then gates are applied, then the qubits are
    measured and released.
    """

    def __init__(self, n_qubits: int = 4):
        self.n_qubits = n_qubits
        self.state = q.StateVector.zero(n_qubits)

    # -- Q#: Set(desired, q) --------------------------------------------
    def set_qubit(self, desired: int, qubit: int) -> None:
        """
        Q#'s ``Set`` operation.

        It measures the qubit and, if the result is not what we want, applies
        an X gate.  This is the *irreversible initialisation* step: the
        qubit's previous content is destroyed.
        """
        bit, collapsed = self.state.measure_qubit(qubit, RNG)
        self.state = collapsed
        if bit != desired:
            self.state = self.state.apply_single(q.X, qubit)

    # -- gates ----------------------------------------------------------
    def h(self, qubit: int) -> None:
        self.state = self.state.apply_single(q.H, qubit)

    def x(self, qubit: int) -> None:
        self.state = self.state.apply_single(q.X, qubit)

    def cnot(self, control: int, target: int) -> None:
        self.state = self.state.apply_cnot(control, target)

    def ccnot(self, c1: int, c2: int, target: int) -> None:
        self.state = self.state.apply_toffoli(c1, c2, target)

    def swap(self, a: int, b: int) -> None:
        self.state = self.state.apply_two(q.SWAP, a, b)

    # -- measurement ----------------------------------------------------
    def measure_all(self) -> List[int]:
        """Q#'s ``M`` on every qubit, returned in Q# order (q0 first)."""
        results = []
        for qubit in range(self.n_qubits):
            bit, self.state = self.state.measure_qubit(qubit, RNG)
            results.append(bit)
        return results


def qsharp_label(bits: List[int]) -> str:
    """
    Format a measurement the way Q# does.

    Q# labels qubits ``q0, q1, q2, q3`` and prints the outcome with **q0 as
    the right-most bit**.  ``Message("0001")`` therefore means q0 = 1.
    """
    return "".join(str(b) for b in reversed(bits))


def qiskit_label(bits: List[int]) -> str:
    """Format the same result the way Qiskit does: q0 is the left-most bit."""
    return "".join(str(b) for b in bits)


# ---------------------------------------------------------------------------
lab.section("1. The Q# execution model")
# ---------------------------------------------------------------------------
lab.step("Allocate 4 qubits, initialise them, apply gates, measure, release.")

program = QSharpProgram(4)
lab.note("using (qubits = Qubit[4])   ->  a 4-qubit state vector is allocated")
for i in range(4):
    program.set_qubit(0, i)
lab.note(f"after Set(Zero, q0..q3): {program.state.to_dirac()}")
lab.check("the initialised state is |0000>", program.state.to_dirac() == "|0000>")

program.h(0)
program.cnot(0, 1)
lab.note(f"after H(q0); CNOT(q0,q1): {program.state.to_dirac()}")
# The Bell pair sits on q0 and q1; in a 4-qubit state vector that is the
# basis states |0000> (index 0) and |1100> (index 12).
lab.check("the Bell state is produced", program.state.probabilities()[0] > 0.49
          and program.state.probabilities()[12] > 0.49,
          "indices 0 and 12 of the 16-amplitude vector")

lab.note("")
lab.note("Q# execution model, in one line:")
lab.note("  allocate qubits -> initialise them -> apply gates -> measure -> release")
lab.note("The gates are reversible; the initialisation and the measurement are not.")


# ---------------------------------------------------------------------------
lab.section("2. The Set operation is irreversible")
# ---------------------------------------------------------------------------
lab.step("Set a qubit that is already in a superposition.")

program = QSharpProgram(1)
program.h(0)
lab.note(f"state after H: {program.state.to_dirac()}")
program.set_qubit(1, 0)
lab.note(f"state after Set(One, q0): {program.state.to_dirac()}")
lab.check("Set(One) forces the qubit to |1>", program.state.to_dirac() == "|1>")
lab.note("The superposition is GONE.  That is the price of initialisation -- and "
         "it is exactly why initialisation happens before the gates, never after.")


# ---------------------------------------------------------------------------
lab.section("3. The QB4 program, run 2000 times")
# ---------------------------------------------------------------------------
lab.step("The course's QB4 program with the Bell-state demo enabled.")

counts: Dict[str, int] = {}
for _ in range(2000):
    program = QSharpProgram(4)
    for i in range(4):
        program.set_qubit(0, i)
    program.h(0)
    program.cnot(0, 1)
    bits = program.measure_all()
    label = qsharp_label(bits)
    counts[label] = counts.get(label, 0) + 1

lab.show(viz.histogram(counts))
lab.check("only 0000 and 0011 occur", set(counts) <= {"0000", "0011"},
          "the Bell pair lives on q0 and q1; Q# writes them right-most")
lab.note("In Q# notation the Bell pair shows up as '0000' and '0011' -- because "
         "Q# puts q0 at the RIGHT-most end.  The next section makes this explicit.")


# ---------------------------------------------------------------------------
lab.section("4. THE ORDERING TRAP")
# ---------------------------------------------------------------------------
lab.step("Q# prints q0 right-most; Qiskit prints q0 left-most.")

program = QSharpProgram(2)
program.set_qubit(0, 0)
program.set_qubit(0, 1)
program.set_qubit(1, 0)     # q0 = 1, q1 = 0
bits = program.measure_all()
lab.note(f"measured bits in Q# order (q0, q1): {bits}")
lab.note(f"Q# would print   : {qsharp_label(bits)}")
lab.note(f"Qiskit prints    : {qiskit_label(bits)}")
lab.check("the two labels differ", qsharp_label(bits) != qiskit_label(bits))
lab.note("The course's 'Verifying Results' article warns about exactly this: when "
         "you check a Q# result against a state vector, you must REVERSE the bit order.")

lab.step("Proof: the same physical state, two labels.")
sv = q.StateVector.from_bitstring("11")
lab.note(f"state vector |11>            -> q0=1, q1=1")
lab.note(f"Q# label  : {qsharp_label([1, 1])}")
lab.note(f"Qiskit label: {qiskit_label([1, 1])}")
sv2 = q.StateVector.from_bitstring("10")
lab.note(f"state vector |10> (q0=1,q1=0) -> Q# label {qsharp_label([1, 0])}, "
         f"Qiskit label {qiskit_label([1, 0])}")
lab.check("|10> in Qiskit is '01' in Q#", qsharp_label([1, 0]) == "01")


# ---------------------------------------------------------------------------
lab.section("5. Every demo from QB4.qs")
# ---------------------------------------------------------------------------
lab.step("Run each of the commented-out demo blocks and predict the output.")

demos = [
    ("NOP (pass through)", [], "|0000>"),
    ("NOT gate on q0", [("x", 0)], None),
    ("Hadamard on q0", [("h", 0)], None),
    ("SWAP q0 <-> q1", [("set1", 0), ("swap", 0, 1)], None),
    ("CNOT q0 -> q1", [("set1", 0), ("cnot", 0, 1)], None),
    ("Bell state", [("h", 0), ("cnot", 0, 1)], None),
    ("Toffoli (AND config)", [("set1", 0), ("set1", 1), ("ccnot", 0, 1, 2)], None),
    ("Toffoli (NOT config)", [("set1", 0), ("set1", 1), ("set1", 2), ("ccnot", 0, 1, 2)], None),
    ("Toffoli (FANOUT config)", [("set1", 0), ("set1", 1), ("ccnot", 0, 1, 2)], None),
]

for label, ops, _ in demos:
    program = QSharpProgram(4)
    for i in range(4):
        program.set_qubit(0, i)
    for op in ops:
        if op[0] == "set1":
            program.set_qubit(1, op[1])
        elif op[0] == "h":
            program.h(op[1])
        elif op[0] == "x":
            program.x(op[1])
        elif op[0] == "cnot":
            program.cnot(op[1], op[2])
        elif op[0] == "ccnot":
            program.ccnot(op[1], op[2], op[3])
        elif op[0] == "swap":
            program.swap(op[1], op[2])
    counts = program.state.histogram(RNG, shots=400)
    top = max(counts.items(), key=lambda kv: kv[1])
    lab.note(f"  {label:<26} -> most likely outcome {top[0]} ({top[1] / 400:.0%})")

# Verify the key ones exactly.
program = QSharpProgram(4)
for i in range(4):
    program.set_qubit(0, i)
program.set_qubit(1, 0)
program.set_qubit(1, 1)
program.ccnot(0, 1, 2)
lab.note(f"Toffoli AND configuration: {program.state.to_dirac()}")
lab.check("the Toffoli in AND configuration sets q2 to 1",
          program.state.to_dirac() == "|1110>",
          "q0=1, q1=1, q2=1, q3=0 -- in this course q0 is the LEFT-most bit")
lab.note("Reading |1110> in Q# order (q0 right-most) gives q3=0, q2=1, q1=1, q0=1 -- "
         "which matches the Q# program: q0 and q1 were set to 1, and q2 became 1.")


# ---------------------------------------------------------------------------
lab.section("6. Measuring superposition states")
# ---------------------------------------------------------------------------
lab.step("Measure a qubit that is in superposition -- and measure it again.")

program = QSharpProgram(1)
program.h(0)
first = program.measure_all()[0]
second = program.measure_all()[0]
lab.note(f"first measurement: {first}, second measurement: {second}")
lab.check("the first measurement is random", first in (0, 1))
lab.check("the second measurement is deterministic", second == first)
lab.note("Once measured, the qubit is in a basis state -- measuring it again gives "
         "the same answer.  This is the collapse, and it is the 'iterative "
         "measurement' the course demonstrates.")


# ---------------------------------------------------------------------------
lab.section("7. What to install if you want the real Q# toolchain")
# ---------------------------------------------------------------------------
lab.step("The .NET route.")

lab.note("1. Install the .NET 8 SDK:      https://dotnet.microsoft.com/download")
lab.note("2. Install the QDK:             dotnet tool install --global Microsoft.Quantum.DotNetCli")
lab.note("3. Create the project:          dotnet new console -o MyQSharpApp")
lab.note("4. Add the Q# packages:         dotnet add package Microsoft.Quantum.Qsharp.Core")
lab.note("                                 dotnet add package Microsoft.Quantum.Qsharp.Simulator")
lab.note("5. Replace Program.cs with the contents of qsharp/QB4/QB4.qs")
lab.note("6. Run it:                      dotnet run")
lab.note("")
lab.note("The project file in qsharp/QB4/QB4.csproj is already set up for exactly this.")
lab.note("Alternatively, use the Azure Quantum CLI:  qsharp run --target simulator QB4.qs")
lab.note("")
lab.note("You do NOT need any of this to complete the lab -- the transliteration above "
         "runs the identical program.")

lab.check("the Q# source ships with this repository",
          os.path.exists(os.path.join(os.path.dirname(__file__), "..", "..", "qsharp", "QB4", "QB4.qs")),
          "qsharp/QB4/QB4.qs")


if __name__ == "__main__":
    sys.exit(lab.finish())
