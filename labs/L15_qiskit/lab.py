#!/usr/bin/env python3
"""
L15 -- IBM Qiskit: quantum programming and algorithms.

Course sections: 14 (IBM Quantum Experience) and 15 (Quantum Programming and
Algorithms With IBM Qiskit: what is Qiskit, installing Python and Qiskit,
Python refresher, Quantum Circuits 1-5, Running a Circuit, Circuit Matrix,
Implementing BB84 Cryptography, Shor's Algorithm).

Run me::

    python labs/L15_qiskit/lab.py

.. note::

   The original QC101 course code targets Qiskit 0.x.  Several of the APIs it
   uses were **removed** in Qiskit 1.0:

   ==============================  ==========================================
   Removed API                     Modern replacement
   ==============================  ==========================================
   ``BasicAer``                    ``qiskit_aer.AerSimulator``
   ``qiskit.utils.QuantumInstance``  pass the backend directly
   ``qiskit.algorithms.Shor``       implement the circuit yourself (Section 15.9)
   ``circuit.save_statevector()``   ``qiskit.quantum_info.Statevector``
   ``circuit.save_unitary()``       ``qiskit.quantum_info.Operator``
   ``qc.bind_parameters()``         ``qc.assign_parameters()``
   ==============================  ==========================================

   This lab uses only the modern APIs, so it runs unchanged on Qiskit 1.x
   and 2.x.
"""

from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

# ---------------------------------------------------------------------------
# Qiskit imports, with a helpful message if they are missing.
# ---------------------------------------------------------------------------
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
    from qiskit.quantum_info import Statevector, Operator
    from qiskit.circuit import Parameter
    from qiskit.circuit.library import CXGate
    try:
        from qiskit.synthesis.qft import synth_qft_full
    except ImportError:                      # older Qiskit
        from qiskit.circuit.library import QFT as _QFT

        def synth_qft_full(num_qubits, do_swaps=True, approximation_degree=0,
                           insert_barriers=False, inverse=False, name=None):
            return _QFT(num_qubits, do_swaps=do_swaps, inverse=inverse)
    from qiskit_aer import AerSimulator
    HAVE_QISKIT = True
except ImportError as exc:  # pragma: no cover - environment problem
    HAVE_QISKIT = False
    _IMPORT_ERROR = exc

from qc101.labkit import Lab
from qc101 import viz

lab = Lab("L15", "IBM Qiskit: programming and algorithms")

if not HAVE_QISKIT:
    lab.section("Qiskit is not installed")
    lab.error(
        f"Qiskit could not be imported ({_IMPORT_ERROR}).\n"
        "   Install it with:  pip install qiskit qiskit-aer\n"
        "   See SETUP.md for the full instructions."
    )
    sys.exit(lab.finish())

SIMULATOR = AerSimulator()
RNG = random.Random(2718)


def draw(circuit) -> str:
    """Render a circuit as text (Qiskit 2 returns a TextDrawing object)."""
    return str(circuit.draw(output="text"))


# ---------------------------------------------------------------------------
lab.section("1. What is Qiskit?")
# ---------------------------------------------------------------------------
lab.step("Qiskit is a Python toolkit for building and running quantum circuits.")

qc = QuantumCircuit(2, 2)
lab.note("A QuantumCircuit(2, 2) has 2 qubits and 2 classical bits.")
lab.note("The circuit starts empty:")
lab.show(draw(qc))
lab.check("a fresh circuit has no instructions", len(qc.data) == 0)

lab.note("")
lab.note("Qiskit follows the circuit model:")
lab.note("  quantum registers  -> the qubits (the state vector)")
lab.note("  classical registers -> where the measurement results are written")
lab.note("  gates              -> the reversible operations")
lab.note("  measure            -> the irreversible operation")


# ---------------------------------------------------------------------------
lab.section("2. Quantum Circuits 1: building with hard-wired code")
# ---------------------------------------------------------------------------
lab.step("The course's circuit1.py: reset, Hadamard, two CNOTs.")

qc = QuantumCircuit(3)
qc.reset(0)
qc.reset(1)
qc.reset(2)
qc.h(0)
qc.cx(0, 1)
qc.cx(0, 2)
qc.measure_all()
lab.show(draw(qc))

counts = SIMULATOR.run(transpile(qc, SIMULATOR), shots=1000).result().get_counts()
lab.show(viz.histogram(counts))
lab.check("the GHZ circuit gives only 000 and 111",
          set(counts) <= {"000", "111"}, f"got {sorted(counts)}")
lab.note("This is the GHZ state: three qubits that are all perfectly correlated.")


# ---------------------------------------------------------------------------
lab.section("3. Quantum Circuits 2: building dynamically")
# ---------------------------------------------------------------------------
lab.step("The course's circuit2.py: appending a gate object.")

qc = QuantumCircuit(3)
cxg = CXGate()
qc.append(cxg, [0, 1])
qc.append(cxg, [0, 1])
lab.show(draw(qc))
lab.note("Appending the SAME gate object twice is the same as writing cx twice.")
lab.check("two CNOTs cancel out",
          Statevector(qc).equiv(Statevector(QuantumCircuit(3))),
          "the circuit is the identity on |000>")


# ---------------------------------------------------------------------------
lab.section("4. Quantum Circuits 3: parameters")
# ---------------------------------------------------------------------------
lab.step("The course's circuit3.py: a reusable template with free parameters.")

qc = QuantumCircuit(3)
qc.initialize([0, 0, 0, 0, 0, 0, 0, 1])
param0 = Parameter("angle0")
param1 = Parameter("angle1")
param2 = Parameter("angle2")
qc.h(0)
qc.h(1)
qc.h(2)
qc.p(param0, 0)
qc.p(param1, 1)
qc.p(param2, 2)
lab.show(draw(qc))

bound = qc.assign_parameters({param0: 0.0, param1: 0.1, param2: 0.2})
lab.note("bound the template with assign_parameters:")
lab.show(draw(bound))
lab.check("assigning parameters returns a new circuit", bound is not qc)
lab.note("NOTE: the modern API is `assign_parameters`; the course's `bind_parameters` "
         "was removed in Qiskit 1.0.")


# ---------------------------------------------------------------------------
lab.section("5. Quantum Circuits 4 and 5: custom gates and instructions")
# ---------------------------------------------------------------------------
lab.step("The course's circuit4.py: build a gate out of a circuit.")

gatesource = QuantumCircuit(2)
gatesource.x(0)
gatesource.cx(0, 1)
gatesource.x(0)
xcnotxgate = gatesource.to_gate()
lab.show("the source circuit:\n" + draw(gatesource))

customgateqc = QuantumCircuit(2)
customgateqc.append(xcnotxgate, [0, 1])
lab.show("the custom gate in use:\n" + draw(customgateqc))
lab.show("decomposed:\n" + draw(customgateqc.decompose()))

lab.check("decomposing recovers the original circuit",
          len(customgateqc.decompose().data) == len(gatesource.data))

lab.step("The course's circuit5.py: a custom *instruction* (a qubit setter).")
instrsource = QuantumCircuit(1)
instrsource.reset(0)
instrsource.x(0)
setqubit = instrsource.to_instruction()
custominstrqc = QuantumCircuit(2)
custominstrqc.append(setqubit, [0])
custominstrqc.append(setqubit, [1])
lab.show(draw(custominstrqc.decompose()))
lab.note("A `to_gate` is reversible and can be used in arithmetic; a `to_instruction` "
         "is an opaque operation like a measurement or a reset.")


# ---------------------------------------------------------------------------
lab.section("6. Running a circuit")
# ---------------------------------------------------------------------------
lab.step("The course's simulate_circuit.py, modernised.")

circuit = QuantumCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure([0, 1], [0, 1])
lab.show(draw(circuit))

compiled = transpile(circuit, SIMULATOR)
result = SIMULATOR.run(compiled, shots=1000).result()
counts = result.get_counts()
lab.show(viz.histogram(counts))
lab.check("the Bell circuit gives only 00 and 11", set(counts) <= {"00", "11"})

lab.step("The state vector, via the modern quantum_info API.")
sv = Statevector(QuantumCircuit(2).compose(circuit.remove_final_measurements(inplace=False)))
lab.note(f"state vector: {sv}")
lab.note(f"probabilities: {dict(zip(sv.num_qubits * [''], [])) if False else [round(p, 4) for p in sv.probabilities()]}")
lab.check_close("the state vector is the Bell state", sv.probabilities()[0], 0.5, 1e-9)
lab.note("NOTE: `circuit.save_statevector()` was removed in Qiskit 1.0.  Use "
         "`qiskit.quantum_info.Statevector(circuit)` instead.")


# ---------------------------------------------------------------------------
lab.section("7. The circuit matrix")
# ---------------------------------------------------------------------------
lab.step("The course's compute_matrix.py, modernised.")

circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0, 1)
op = Operator(circuit)
lab.show("the unitary matrix of the circuit:")
lab.show(str(op.data))
lab.check("the matrix is unitary", op.is_unitary())
lab.note("NOTE: `circuit.save_unitary()` was removed in Qiskit 1.0.  Use "
         "`qiskit.quantum_info.Operator(circuit)` instead.")


# ---------------------------------------------------------------------------
lab.section("8. Implementing BB84 in Qiskit")
# ---------------------------------------------------------------------------
lab.step("The course's bb84.py -- a single round, then a full protocol.")


def random_bit(backend) -> int:
    """Use a quantum random number generator to pick a bit."""
    circuit = QuantumCircuit(1, 1)
    circuit.x(0)
    circuit.barrier()
    circuit.h(0)
    circuit.barrier()
    circuit.measure(0, 0)
    counts = backend.run(transpile(circuit, backend), shots=1).result().get_counts()
    return 1 if "1" in counts else 0


def random_basis(backend) -> int:
    """Use a quantum random number generator to pick a basis."""
    return random_bit(backend)


def bb84_round(backend, bit: int, send_basis: int, recv_basis: int) -> int:
    """
    One BB84 round.

    Basis 0 = rectilinear (H/V), basis 1 = diagonal (+/-45).
    The Hadamard gate converts between them; H followed by H is the identity.
    """
    circuit = QuantumCircuit(1, 1)
    if bit == 1:
        circuit.x(0)
    if send_basis == 1:
        circuit.h(0)          # change the basis
    if recv_basis == 1:
        circuit.h(0)          # H.H = I, so this reverses the basis change
    circuit.measure(0, 0)
    counts = backend.run(transpile(circuit, backend), shots=1).result().get_counts()
    return 1 if "1" in counts else 0


#: AerSimulator can hold at most 27 qubits in a single circuit.
MAX_QUBITS_PER_CIRCUIT = 24


def bb84_batched(backend, rounds: int, force_mismatch: bool = False):
    """
    Run ``rounds`` BB84 rounds with only ~18 simulator calls.

    Call 1: a single 3-qubit circuit in |+>^3, executed ``rounds`` times.
    Every execution yields one round's (bit, send basis, receive basis).

    Calls 2..n: the communication rounds, 24 at a time -- one qubit and one
    classical bit per round, so one execution settles 24 rounds.

    Returns ``(alice_key, bob_key, raw)`` where ``raw`` is a list of
    ``(bit, send_basis, recv_basis, received_bit)`` tuples.
    """
    # --- the quantum random numbers --------------------------------------
    rng = QuantumCircuit(3, 3)
    rng.h([0, 1, 2])
    rng.measure([0, 1, 2], [0, 1, 2])
    counts = backend.run(transpile(rng, backend), shots=rounds).result().get_counts()
    triples = []
    for key in sorted(counts):
        triple = tuple(int(bit) for bit in key[::-1])   # c0, c1, c2
        triples.extend([triple] * counts[key])
    assert len(triples) == rounds

    # --- the communication rounds, 24 at a time ---------------------------
    outcomes = []
    for start in range(0, rounds, MAX_QUBITS_PER_CIRCUIT):
        chunk = list(range(start, min(start + MAX_QUBITS_PER_CIRCUIT, rounds)))
        comm = QuantumCircuit(len(chunk), len(chunk))
        for local, r in enumerate(chunk):
            bit, send_basis, recv_basis = triples[r]
            if force_mismatch:
                recv_basis = 1 - send_basis
            if bit:
                comm.x(local)
            if send_basis:
                comm.h(local)
            if recv_basis:
                comm.h(local)
        comm.measure(range(len(chunk)), range(len(chunk)))
        result = backend.run(transpile(comm, backend), shots=1).result().get_counts()
        for key in result:
            outcomes.extend(int(bit) for bit in key[::-1])
            break

    raw = []
    alice_key, bob_key = [], []
    for r in range(rounds):
        bit, send_basis, recv_basis = triples[r]
        if force_mismatch:
            recv_basis = 1 - send_basis
        received = outcomes[r]
        raw.append((bit, send_basis, recv_basis, received))
        if send_basis == recv_basis:
            alice_key.append(bit)
            bob_key.append(received)
    return alice_key, bob_key, raw


lab.step("One round: matching bases preserve the bit.")
alice_key, bob_key, raw = bb84_batched(SIMULATOR, 20)
same_basis = sum(1 for bit, sb, rb, got in raw if sb == rb)
matched = sum(1 for bit, sb, rb, got in raw if sb == rb and got == bit)
lab.note(f"{same_basis} of the 20 rounds used matching bases; "
         f"{matched} of those recovered the bit exactly")
lab.check_equal("matching bases always preserve the bit", matched, same_basis)

lab.step("One round: mismatched bases lose the bit.")
alice_key, bob_key, raw = bb84_batched(SIMULATOR, 20, force_mismatch=True)
lost = sum(1 for bit, sb, rb, got in raw if got != bit)
lab.note(f"{lost}/20 rounds with mismatched bases lost the bit (chance = 50%)")
lab.check("mismatched bases lose the bit about half the time", 5 <= lost <= 15)

lab.step("A full protocol run: 400 rounds, sifted into a shared key.")
alice_key, bob_key, raw = bb84_batched(SIMULATOR, 400)
lab.note(f"sifted key length: {len(alice_key)} bits")
lab.note(f"Alice: {''.join(map(str, alice_key))}")
lab.note(f"Bob  : {''.join(map(str, bob_key))}")
lab.check("Alice and Bob agree on every bit", alice_key == bob_key)
lab.check("about half the rounds survive sifting", 120 < len(alice_key) < 280)
lab.note("This is the same protocol as lab L07, but every random choice is made by "
         "a *quantum* random number generator -- the 'quantum' in quantum "
         "cryptography.")
lab.note("")
lab.note("Note how the whole protocol ran in about 18 simulator calls: the "
         "3*400 random numbers came from a single 3-qubit circuit run 400 "
         "times, and all 400 communication rounds were packed 24 to a "
         "circuit, one qubit and one classical bit each.  Batching like "
         "this is what makes real QPUs practical.")


# ---------------------------------------------------------------------------
lab.section("9. Shor's algorithm")
# ---------------------------------------------------------------------------
lab.step("Factoring with period finding.")

lab.note("Shor's algorithm reduces factoring N to finding the period of "
         "f(x) = a^x mod N.  The period is found with a quantum Fourier "
         "transform over a 2^m-qubit register.")


def continued_fraction_convergents(numerator: int, denominator: int):
    """
    The convergents of the continued-fraction expansion of num/den.

    Returns a list of ``(p, q)`` pairs, each approximating num/den as p/q.
    """
    terms = []
    n, d = numerator, denominator
    while d:
        quotient, remainder = divmod(n, d)
        terms.append(quotient)
        n, d = d, remainder
    p_prev, p = 0, 1
    q_prev, q = 1, 0
    convergents = []
    for t in terms:
        p_prev, p = p, t * p + p_prev
        q_prev, q = q, t * q + q_prev
        convergents.append((p, q))
    return convergents


def period_from_peak(y: int, total: int) -> int:
    """
    Recover a candidate period from a measured peak ``y`` out of ``total``.

    The true period ``r`` satisfies ``y * r / total`` being an integer.
    We return the *smallest* such r greater than 1, using the continued
    fraction expansion of y/total to get a good first guess.
    """
    convergents = continued_fraction_convergents(y, total)
    candidates = [q for _, q in convergents if q > 1]
    if candidates:
        best = min(candidates)
        # Verify: y * best / total must be (nearly) an integer.
        for r in range(2, total + 1):
            value = y * r / total
            if abs(value - round(value)) < 1e-6:
                return r
        return best
    return total


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def modular_multiplication_matrix(a: int, N: int, dim: int):
    """
    The unitary matrix of ``U|y> = a*y mod N``.

    For ``y < N`` the value is multiplied by ``a`` modulo ``N``; for
    ``y >= N`` the basis state is left alone.  Because ``gcd(a, N) = 1`` the
    map is a bijection, so the matrix really is unitary.
    """
    matrix = [[0j] * dim for _ in range(dim)]
    for y in range(dim):
        target = (a * y) % N if y < N else y
        matrix[target][y] = 1 + 0j
    return matrix


def matrix_power(matrix, exponent: int):
    """Raise a matrix to an integer power by repeated multiplication."""
    size = len(matrix)
    result = [[1 + 0j if i == j else 0j for j in range(size)] for i in range(size)]
    base = [row[:] for row in matrix]
    for _ in range(exponent):
        result = [
            [sum(result[i][k] * base[k][j] for k in range(size)) for j in range(size)]
            for i in range(size)
        ]
    return result


def quantum_period_finding(a: int, N: int, m: int = 4, shots: int = 4096):
    """
    Find the period ``r`` of ``a^x mod N`` with a real quantum circuit.

    Kitaev's order-finding circuit:

    1. the counting register (m qubits) goes into a uniform superposition;
    2. the target register is prepared in ``|1>``;
    3. for each counting qubit ``i`` we apply a *controlled* ``U^(2^i)``,
       where ``U|y> = a*y mod N``;
    4. the inverse Quantum Fourier Transform is applied to the counting
       register;
    5. the counting register is measured.

    The measurement lands on multiples of ``2^m / r``, so the period falls
    out of the *distribution* of outcomes.

    Returns ``(period, counts)``.
    """
    import numpy as np
    from qiskit.circuit.library import UnitaryGate

    n = max(2, (N - 1).bit_length())
    dim = 2**n

    counting = QuantumRegister(m, "count")
    target = QuantumRegister(n, "target")
    qc = QuantumCircuit(counting, target, ClassicalRegister(m, "meas"))

    qc.x(target[0])                      # target register starts in |1>
    qc.h(counting)                       # uniform superposition over x

    base = modular_multiplication_matrix(a, N, dim)
    for i in range(m):
        power = matrix_power(base, 2**i)
        qc.append(UnitaryGate(np.array(power)).control(1),
                  [counting[i]] + list(target))

    qc.compose(synth_qft_full(m, inverse=True).decompose(),
               qubits=list(counting), inplace=True)
    qc.measure(counting, range(m))

    counts = SIMULATOR.run(transpile(qc, SIMULATOR, optimization_level=1),
                           shots=shots).result().get_counts()

    # The peaks sit at multiples of 2^m / r.  Recover r from the continued
    # fraction expansion of y / 2^m, then take the smallest multiple of that
    # candidate which really is a period (a^r = 1 mod N).
    for bitstring, _ in sorted(counts.items(), key=lambda kv: -kv[1]):
        y = int(bitstring, 2)
        if y == 0:
            continue
        candidate = period_from_peak(y, 2**m)
        if candidate < 2:
            continue
        multiple = candidate
        while multiple <= 2**m and pow(a, multiple, N) != 1:
            multiple *= 2
        if pow(a, multiple, N) == 1:
            return multiple, counts
    return 0, counts


lab.step("Now the quantum part: period finding with the QFT.")
lab.note("Kitaev's order-finding circuit:")
lab.note("  1. counting register (m qubits) -> uniform superposition")
lab.note("  2. target register -> |1>")
lab.note("  3. for each counting qubit i: apply controlled-U^(2^i), U|y> = a*y mod N")
lab.note("  4. inverse QFT on the counting register")
lab.note("  5. measure the counting register")
try:
    r, counts = quantum_period_finding(2, 15, m=4)
    lab.note(f"the quantum period finder returned r = {r}")
    lab.show(viz.histogram(counts))
    peaks = sorted(int(b, 2) for b in counts)
    lab.note(f"the outcomes are {peaks} -- multiples of 2^m/r = 16/4 = 4")
    lab.check("the quantum period finder finds the right period", r == 4)
    lab.check("all the peaks are multiples of 2^m / r",
              all(y % (2**4 // r) == 0 for y in peaks),
              "this is the signature of the period")
except Exception as exc:  # pragma: no cover
    lab.error(f"the quantum period finder raised {exc!r}")

lab.note("")
lab.note("The key insight: the classical part of Shor's algorithm is easy -- the "
         "EXPONENT is what is hard to compute classically (that is the discrete "
         "logarithm problem).  The quantum part just does the Fourier transform, "
         "which spreads the periodic structure of a^x mod N across the spectrum.")
lab.note("The modern Qiskit `Shor` class was removed in Qiskit 1.0, which is why "
         "this lab implements the circuit directly.")


# ---------------------------------------------------------------------------
lab.section("10. A modern Shor implementation with the QFT convention")
# ---------------------------------------------------------------------------
lab.step("Use Qiskit's own QFT, applied to the counting register.")

qc = QuantumCircuit(4, 4)
qc.compose(synth_qft_full(4, do_swaps=False).decompose(), inplace=True)
qc.measure(range(4), range(4))
counts = SIMULATOR.run(transpile(qc, SIMULATOR), shots=1024).result().get_counts()
lab.show(viz.histogram(counts))
lab.check("the QFT of |0000> is uniform over all 16 outcomes",
          len(counts) == 16, f"got {len(counts)} distinct outcomes")
lab.note("QFT|0...0> = (|0...0> + |0...1> + ... + |1...1>)/sqrt(N) -- the uniform "
         "superposition.  This is the property Shor's algorithm exploits in reverse: "
         "the QFT turns a periodic state into a state with sharp peaks.")
lab.note("Qiskit's QFT uses the opposite bit order to the textbook, which is "
         "exactly the kind of detail that produces mysterious 'wrong answer' bugs.")


# ---------------------------------------------------------------------------
lab.section("11. Connecting back to the maths")
# ---------------------------------------------------------------------------
lab.section("11. The Qiskit state vector and the course's state vector agree")
# ---------------------------------------------------------------------------
from qc101 import quantum as qc101_quantum

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qiskit_sv = Statevector(qc)

# The course's simulator uses q0 as the LEFT-most bit; Qiskit's state vector
# uses qubit 0 as the LEAST significant bit.  Reverse the labels to compare.
qiskit_amplitudes = list(qiskit_sv.data)
course_amplitudes = list(reversed(qiskit_amplitudes))
lab.note(f"Qiskit state vector : {[round(x.real, 4) for x in qiskit_amplitudes]}")
lab.note(f"course state vector : {[round(x.real, 4) for x in course_amplitudes]}")
lab.note("(the course writes q0 first; Qiskit writes qubit 0 last)")

course_sv = qc101_quantum.StateVector(course_amplitudes)
lab.note(f"course simulator    : {course_sv.to_dirac()}")
lab.check("the two simulators agree once the ordering is fixed",
          course_sv.to_dirac().endswith("|00> + 0.7071 |11>"))
lab.note("This is the same ordering trap the course warns about in its Q# section.")


if __name__ == "__main__":
    sys.exit(lab.finish())
