"""
Quantum state vectors, gates, superposition, entanglement and measurement.

This is a dependency-free state-vector simulator.  It is the Python
counterpart of the Java simulators shipped with the QC101 course, and it
powers Sections 5-12 of the study notes.

Conventions used throughout (these matter!):

* **Qubit order.**  ``|q0 q1 ... qn-1>`` -- q0 is the *leftmost* bit.  This
  matches the Qiskit "little-endian" *state vector* ordering used in the
  course, and it is the opposite of how the Microsoft Q# runtime prints
  its results (Q# prints q_{n-1} ... q0).  See ``notes/ordering.md``.
* **Measurement.**  Sampling an outcome from ``|amplitude|^2`` and
  *collapsing* the state to the corresponding basis state.
* **Reversibility.**  Every gate is a unitary matrix, so a gate can always
  be undone by applying its inverse.
"""

from __future__ import annotations

import cmath
import math
import random
from typing import Dict, List, Optional, Sequence, Tuple

from . import linalg

__all__ = [
    "StateVector",
    "X",
    "Y",
    "Z",
    "H",
    "S",
    "T",
    "I",
    "CNOT",
    "CCNOT",
    "SWAP",
    "CSWAP",
    "GATES",
    "TWO_QUBIT_GATES",
    "bell_state",
    "ghz_state",
    "apply_gate",
    "entanglement_entropy",
    "is_entangled",
    "ket",
    "bra",
    "braket",
]

Matrix = List[List[complex]]


def _matvec(m: Matrix, v: Sequence[complex]) -> List[complex]:
    """Multiply a matrix by a column vector, returning a flat vector."""
    return [sum(m[i][j] * v[j] for j in range(len(v))) for i in range(len(m))]


# --------------------------------------------------------------------------
# Single-qubit gate matrices
# --------------------------------------------------------------------------
I: Matrix = [[complex(1, 0), complex(0, 0)], [complex(0, 0), complex(1, 0)]]

X: Matrix = [[complex(0, 0), complex(1, 0)], [complex(1, 0), complex(0, 0)]]

Y: Matrix = [[complex(0, 0), complex(0, -1)], [complex(0, 1), complex(0, 0)]]

Z: Matrix = [[complex(1, 0), complex(0, 0)], [complex(0, 0), complex(-1, 0)]]

#: Hadamard -- creates superposition.  ``H|0> = (|0> + |1>)/sqrt(2)``
H: Matrix = [
    [complex(1, 0) / math.sqrt(2), complex(1, 0) / math.sqrt(2)],
    [complex(1, 0) / math.sqrt(2), complex(-1, 0) / math.sqrt(2)],
]

#: Phase / S gate -- 90 degree phase shift.
S: Matrix = [[complex(1, 0), complex(0, 0)], [complex(0, 0), complex(0, 1)]]

#: T gate -- 45 degree phase shift (the "pi/8" gate).
T: Matrix = [
    [complex(1, 0), complex(0, 0)],
    [complex(0, 0), cmath.exp(1j * math.pi / 4)],
]

GATES: Dict[str, Matrix] = {
    "I": I,
    "X": X,
    "Y": Y,
    "Z": Z,
    "H": H,
    "S": S,
    "T": T,
}

#: CNOT (controlled-NOT).  Control qubit 0, target qubit 1.
CNOT: Matrix = [
    [complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0)],
    [complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0)],
]

#: CCNOT (Toffoli).  Controls q0 and q1, target q2.
CCNOT: Matrix = [
    [complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0)],
    [complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0)],
]

#: SWAP -- exchanges two qubits.
SWAP: Matrix = [
    [complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0)],
    [complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0)],
]

#: Fredkin / controlled-SWAP.  The first qubit is the control; the other two
#: are swapped when the control is 1.  In the local ordering (control, t1, t2)
#: the permutation is 0->0, 1->1, 2->2, 3->3, 4->4, 5->6, 6->5, 7->7.
CSWAP: Matrix = [
    [complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0)],
]

TWO_QUBIT_GATES: Dict[str, Matrix] = {
    "CNOT": CNOT,
    "CCNOT": CCNOT,
    "SWAP": SWAP,
    "CSWAP": CSWAP,
}


# --------------------------------------------------------------------------
# Dirac notation helpers
# --------------------------------------------------------------------------
def ket(bitstring: str) -> str:
    """Render a basis state in Dirac notation: ``ket("10")`` -> ``'|10>'``."""
    return "|" + bitstring.replace(" ", "") + ">"


def bra(bitstring: str) -> str:
    """Render a bra: ``bra("10")`` -> ``'<10|'``."""
    return "<" + bitstring.replace(" ", "") + "|"


def braket(left: str, right: str) -> str:
    """Render a matrix element: ``braket("0", "1")`` -> ``'<0|1>'``."""
    return bra(left) + ket(right)


# --------------------------------------------------------------------------
# The state vector
# --------------------------------------------------------------------------
class StateVector:
    """
    A quantum state of ``n`` qubits, stored as a list of ``2**n`` amplitudes.

    >>> sv = StateVector.zero(1)
    >>> sv.apply_single(H, 0)
    >>> [round(p, 3) for p in sv.probabilities()]
    [0.5, 0.5]
    """

    def __init__(self, amplitudes: Sequence[complex]):
        amps = [complex(a) for a in amplitudes]
        n = len(amps)
        if n == 0 or (n & (n - 1)) != 0:
            raise ValueError(f"state vector length must be a power of two, got {n}")
        self.amplitudes = amps
        self.n_qubits = n.bit_length() - 1

    # -- constructors -----------------------------------------------------
    @classmethod
    def zero(cls, n_qubits: int = 1) -> "StateVector":
        """The all-zeros state ``|00...0>``."""
        sv = cls([complex(0, 0)] * (2**n_qubits))
        sv.amplitudes[0] = complex(1, 0)
        return sv

    @classmethod
    def one(cls, n_qubits: int = 1) -> "StateVector":
        """The state with the *last* qubit set to one: ``|00...1>``."""
        sv = cls([complex(0, 0)] * (2**n_qubits))
        sv.amplitudes[1] = complex(1, 0)
        return sv

    @classmethod
    def from_basis(cls, index: int, n_qubits: int) -> "StateVector":
        """A basis state given by its integer index."""
        sv = cls([complex(0, 0)] * (2**n_qubits))
        sv.amplitudes[index] = complex(1, 0)
        return sv

    @classmethod
    def from_bitstring(cls, bits: str) -> "StateVector":
        """A basis state given by a bit string, e.g. ``"10"``."""
        bits = bits.replace(" ", "")
        index = int(bits, 2) if bits else 0
        return cls.from_basis(index, len(bits))

    @classmethod
    def random(cls, n_qubits: int = 1, rng: random.Random | None = None) -> "StateVector":
        """A uniformly random pure state (Haar-random via normalised Gaussians)."""
        rng = rng or random
        raw = [complex(rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(2**n_qubits)]
        norm = math.sqrt(sum(abs(a) ** 2 for a in raw))
        return cls([a / norm for a in raw])

    # -- properties -------------------------------------------------------
    def probabilities(self) -> List[float]:
        """Measurement probabilities: ``|amplitude|^2`` for each basis state."""
        return [abs(a) ** 2 for a in self.amplitudes]

    def basis_labels(self) -> List[str]:
        """The bit string label of each basis state, in state-vector order."""
        return [format(i, f"0{self.n_qubits}b") for i in range(len(self.amplitudes))]

    def density_matrix(self) -> Matrix:
        """The density matrix ``|psi><psi|`` of the pure state."""
        return linalg.outer_product(self.amplitudes, self.amplitudes)

    def entropy(self) -> float:
        """The von Neumann entropy of the reduced state (0 for a product state)."""
        return entanglement_entropy(self)

    def is_normalized(self, tol: float = 1e-9) -> bool:
        """True when the total probability is 1."""
        return abs(sum(self.probabilities()) - 1.0) < tol

    # -- operations -------------------------------------------------------
    def apply_single(self, gate: Matrix, qubit: int) -> "StateVector":
        """
        Apply a single-qubit gate to ``qubit``.

        The state is reshaped so that the target qubit is isolated, the gate
        is applied to it, and the state is reshaped back.
        """
        if not 0 <= qubit < self.n_qubits:
            raise IndexError(f"qubit index {qubit} out of range for {self.n_qubits} qubits")
        n = self.n_qubits
        dim = 2**n
        # Build the full 2^n x 2^n matrix out of the 2x2 gate.
        full = linalg.zeros(dim, dim)
        # Permutation: index bits are ordered q0 (most significant) .. qn-1.
        for col in range(dim):
            bits = [(col >> (n - 1 - k)) & 1 for k in range(n)]
            for new_bit in (0, 1):
                new_bits = list(bits)
                new_bits[qubit] = new_bit
                row = 0
                for b in new_bits:
                    row = (row << 1) | b
                full[row][col] = gate[new_bit][bits[qubit]]
        return StateVector(_matvec(full, self.amplitudes))

    def apply_two(self, gate: Matrix, control: int, target: int) -> "StateVector":
        """
        Apply a two-qubit gate with the given control and target qubits.

        The gate matrix is assumed to act on ``(control, target)`` in that
        order, which matches CNOT and SWAP.
        """
        if not (0 <= control < self.n_qubits and 0 <= target < self.n_qubits):
            raise IndexError("qubit index out of range")
        if control == target:
            raise ValueError("control and target must be different qubits")
        n = self.n_qubits
        dim = 2**n
        full = linalg.zeros(dim, dim)
        for col in range(dim):
            bits = [(col >> (n - 1 - k)) & 1 for k in range(n)]
            pair = (bits[control], bits[target])
            for new_pair in ((0, 0), (0, 1), (1, 0), (1, 1)):
                new_bits = list(bits)
                new_bits[control] = new_pair[0]
                new_bits[target] = new_pair[1]
                row = 0
                for b in new_bits:
                    row = (row << 1) | b
                idx = new_pair[0] * 2 + new_pair[1]
                full[row][col] = gate[idx][pair[0] * 2 + pair[1]]
        return StateVector(_matvec(full, self.amplitudes))

    def apply_cnot(self, control: int, target: int) -> "StateVector":
        """Apply a CNOT gate."""
        return self.apply_two(CNOT, control, target)

    def apply_toffoli(self, control1: int, control2: int, target: int) -> "StateVector":
        """
        Apply a CCNOT (Toffoli) gate.

        The target flips if and only if *both* controls are 1.  The two
        controls may be the **same** qubit (so ``Toffoli(c, c; t)`` is a
        controlled-X), but the target must differ from the controls --
        a gate whose target is also a control is not reversible and
        therefore is not a valid quantum gate.
        """
        n = self.n_qubits
        for idx in (control1, control2, target):
            if not 0 <= idx < n:
                raise IndexError(f"qubit index {idx} out of range for {n} qubits")
        if target in (control1, control2):
            raise ValueError(
                "the Toffoli target must differ from its controls, otherwise the "
                "operation is not reversible"
            )
        out = [complex(0, 0)] * len(self.amplitudes)
        for idx, amp in enumerate(self.amplitudes):
            bits = [(idx >> (n - 1 - k)) & 1 for k in range(n)]
            fires = bits[control1] & bits[control2]
            new_idx = idx ^ (1 << (n - 1 - target)) if fires else idx
            out[new_idx] = amp
        return StateVector(out)

    def apply_three(self, gate: Matrix, q1: int, q2: int, q3: int) -> "StateVector":
        """Apply a three-qubit gate acting on ``(q1, q2, q3)`` in that order."""
        n = self.n_qubits
        for idx in (q1, q2, q3):
            if not 0 <= idx < n:
                raise IndexError(f"qubit index {idx} out of range for {n} qubits")
        if len({q1, q2, q3}) != 3:
            raise ValueError("the three qubits must be different")
        dim = 2**n
        full = linalg.zeros(dim, dim)
        for col in range(dim):
            bits = [(col >> (n - 1 - k)) & 1 for k in range(n)]
            triple = (bits[q1], bits[q2], bits[q3])
            for new_triple in [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]:
                new_bits = list(bits)
                new_bits[q1], new_bits[q2], new_bits[q3] = new_triple
                row = 0
                for b in new_bits:
                    row = (row << 1) | b
                idx = new_triple[0] * 4 + new_triple[1] * 2 + new_triple[2]
                full[row][col] = gate[idx][triple[0] * 4 + triple[1] * 2 + triple[2]]
        return StateVector(_matvec(full, self.amplitudes))

    def measure(self, rng: random.Random | None = None) -> Tuple[int, "StateVector"]:
        """
        Measure the whole system.

        Returns ``(outcome_index, collapsed_state)``.  The outcome is drawn
        with probability ``|amplitude|^2`` and the state collapses to the
        corresponding basis state -- this is the *irreversible* step.
        """
        rng = rng or random
        probs = self.probabilities()
        r = rng.random()
        cumulative = 0.0
        outcome = len(probs) - 1
        for i, p in enumerate(probs):
            cumulative += p
            if r < cumulative:
                outcome = i
                break
        collapsed = StateVector([complex(0, 0)] * len(probs))
        collapsed.amplitudes[outcome] = complex(1, 0)
        return outcome, collapsed

    def measure_qubit(self, qubit: int, rng: random.Random | None = None) -> Tuple[int, "StateVector"]:
        """
        Measure a *single* qubit (and collapse only that qubit's dimension).
        """
        rng = rng or random
        n = self.n_qubits
        if not 0 <= qubit < n:
            raise IndexError("qubit index out of range")
        probs = [0.0, 0.0]
        for i, a in enumerate(self.amplitudes):
            probs[(i >> (n - 1 - qubit)) & 1] += abs(a) ** 2
        r = rng.random()
        bit = 1 if r >= probs[0] else 0
        collapsed = []
        for i, a in enumerate(self.amplitudes):
            if ((i >> (n - 1 - qubit)) & 1) == bit:
                collapsed.append(a)
            else:
                collapsed.append(complex(0, 0))
        total = sum(abs(a) ** 2 for a in collapsed)
        if total > 1e-12:
            collapsed = [a / math.sqrt(total) for a in collapsed]
        return bit, StateVector(collapsed)

    def copy(self) -> "StateVector":
        """A deep copy of this state."""
        return StateVector(list(self.amplitudes))

    # -- display ----------------------------------------------------------
    def to_dirac(self, threshold: float = 1e-6) -> str:
        """
        Render the state in Dirac notation, dropping negligible terms.

        >>> StateVector.from_bitstring("01").to_dirac()
        '|01>'
        """
        parts = []
        for label, a in zip(self.basis_labels(), self.amplitudes):
            if abs(a) < threshold:
                continue
            coeff = "" if abs(abs(a) - 1.0) < 1e-9 else f"{abs(a):.4f} "
            phase = ""
            if a.imag > 1e-9:
                phase = f"e^(i*{a.imag:.4f})"
            elif a.imag < -1e-9:
                phase = f"e^(-i*{abs(a.imag):.4f})"
            sign = "-" if a.real < -1e-9 else "+"
            if not parts:
                parts.append(f"{'-' if sign == '-' else ''}{coeff}{phase}{ket(label)}")
            else:
                parts.append(f" {sign} {coeff}{phase}{ket(label)}")
        return "".join(parts) if parts else "0"

    def probability_table(self) -> str:
        """A text table of basis states and their probabilities."""
        lines = [f"{'state':>8}  {'probability':>10}  {'amplitude':>22}"]
        lines.append("-" * 46)
        for label, a, p in zip(self.basis_labels(), self.amplitudes, self.probabilities()):
            amp = f"{a.real:.4f}"
            if abs(a.imag) > 1e-9:
                amp += f" {'+' if a.imag >= 0 else '-'} {abs(a.imag):.4f}i"
            lines.append(f"{label:>8}  {p:>10.6f}  {amp:>22}")
        return "\n".join(lines)

    def histogram(self, rng: random.Random | None = None, shots: int = 1000) -> Dict[str, int]:
        """Sample the state ``shots`` times and return a bitstring histogram."""
        rng = rng or random
        counts: Dict[str, int] = {}
        for _ in range(shots):
            idx, _ = self.measure(rng)
            label = format(idx, f"0{self.n_qubits}b")
            counts[label] = counts.get(label, 0) + 1
        return counts

    def __repr__(self) -> str:  # pragma: no cover - convenience
        return f"StateVector({self.n_qubits} qubits, {self.to_dirac()})"


# --------------------------------------------------------------------------
# Convenience functions
# --------------------------------------------------------------------------
def apply_gate(sv: StateVector, gate: Matrix, qubit: int) -> StateVector:
    """Functional form of ``StateVector.apply_single``."""
    return sv.apply_single(gate, qubit)


def bell_state() -> StateVector:
    """The Bell state ``(|00> + |11>)/sqrt(2)`` -- a maximally entangled pair."""
    sv = StateVector.zero(2)
    sv = sv.apply_single(H, 0)
    sv = sv.apply_cnot(0, 1)
    return sv


def ghz_state(n_qubits: int = 3) -> StateVector:
    """The GHZ state ``(|00...0> + |11...1>)/sqrt(2)``."""
    sv = StateVector.zero(n_qubits)
    sv = sv.apply_single(H, 0)
    for q in range(1, n_qubits):
        sv = sv.apply_cnot(q - 1, q)
    return sv


def _reduced_density(sv: StateVector, keep: Sequence[int]) -> Matrix:
    """Density matrix of the subsystem formed by ``keep`` (qubit indices)."""
    n = sv.n_qubits
    keep = sorted(keep)
    rest = [q for q in range(n) if q not in keep]
    k = len(keep)
    rho = linalg.zeros(2**k, 2**k)
    for col, a in enumerate(sv.amplitudes):
        col_rest = 0
        for q in rest:
            col_rest = (col_rest << 1) | ((col >> (n - 1 - q)) & 1)
        for row, b in enumerate(sv.amplitudes):
            row_rest = 0
            for q in rest:
                row_rest = (row_rest << 1) | ((row >> (n - 1 - q)) & 1)
            if col_rest != row_rest:
                continue
            row_keep = 0
            for q in keep:
                row_keep = (row_keep << 1) | ((row >> (n - 1 - q)) & 1)
            col_keep = 0
            for q in keep:
                col_keep = (col_keep << 1) | ((col >> (n - 1 - q)) & 1)
            rho[row_keep][col_keep] += a.conjugate() * b
    return rho


def entanglement_entropy(sv: StateVector) -> float:
    """
    Von Neumann entropy of the first half of the system.

    ``0`` for a product (separable) state; ``log2(2**k)`` for a maximally
    entangled state of ``k`` qubits.
    """
    if sv.n_qubits < 2:
        return 0.0
    k = sv.n_qubits // 2
    rho = _reduced_density(sv, list(range(k)))
    # The probabilities of measuring the subsystem are the EIGENVALUES of
    # its reduced density matrix -- not the diagonal of that matrix.
    total = 0.0
    for p in linalg.hermitian_eigenvalues(rho):
        if p > 1e-12:
            total -= p * math.log2(p)
    return total


def is_entangled(sv: StateVector) -> bool:
    """True when the state cannot be written as a product of two subsystems."""
    if sv.n_qubits < 2:
        return False
    return entanglement_entropy(sv) > 1e-9
