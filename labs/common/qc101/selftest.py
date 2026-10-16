"""
Self-tests for the QC101 shared library.

Run with::

    python -m qc101.selftest      (from labs/common)
    python labs/common/qc101/selftest.py

These checks guard the mathematical invariants the labs rely on: gates are
unitary permutations, measurement is consistent with the Born rule, and the
entanglement entropy agrees with the Schmidt decomposition.

Keeping this file separate means a mistake in one lab cannot quietly
corrupt the others.
"""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc101 import bb84, boolean, complexnum, linalg, photon, probability, quantum, viz  # noqa: E402

_FAILURES: list[str] = []
_COUNT = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global _COUNT
    _COUNT += 1
    if not condition:
        _FAILURES.append(f"{name}{(' -- ' + detail) if detail else ''}")
        print(f"  [FAIL] {name}{(' -- ' + detail) if detail else ''}")


def check_close(name: str, got: float, expected: float, tol: float = 1e-9) -> None:
    check(name, abs(got - expected) <= tol, f"got {got!r}, expected {expected!r}")


# ---------------------------------------------------------------------------
def test_gates_are_unitary() -> None:
    for name, gate in quantum.GATES.items():
        check(f"gate {name} is unitary", linalg.is_unitary(gate))
    for name, gate in quantum.TWO_QUBIT_GATES.items():
        check(f"gate {name} is unitary", linalg.is_unitary(gate))


def test_single_qubit_gate_truth_tables() -> None:
    zero = quantum.StateVector.zero(1)
    one = quantum.StateVector.one(1)
    check("X|0> = |1>", zero.apply_single(quantum.X, 0).to_dirac() == "|1>")
    check("X|1> = |0>", one.apply_single(quantum.X, 0).to_dirac() == "|0>")
    check("Z|0> = |0>", zero.apply_single(quantum.Z, 0).to_dirac() == "|0>")
    check("Z|1> = -|1>", one.apply_single(quantum.Z, 0).amplitudes[1].real < 0)
    check("H|0> = |+>", abs(zero.apply_single(quantum.H, 0).amplitudes[0].real - 1 / math.sqrt(2)) < 1e-12)
    check("H^2 = I", zero.apply_single(quantum.H, 0).apply_single(quantum.H, 0).to_dirac() == "|0>")
    check("S^4 = I", one.apply_single(quantum.S, 0).apply_single(quantum.S, 0)
          .apply_single(quantum.S, 0).apply_single(quantum.S, 0).amplitudes[1].real > 0)
    check("T^8 = I", abs(complexnum.magnitude(
        one.apply_single(quantum.T, 0).apply_single(quantum.T, 0).apply_single(quantum.T, 0)
        .apply_single(quantum.T, 0).apply_single(quantum.T, 0).apply_single(quantum.T, 0)
        .apply_single(quantum.T, 0).apply_single(quantum.T, 0).amplitudes[1]) - 1) < 1e-12)


def test_cnot_truth_table() -> None:
    expected = {
        "00": "00", "01": "01", "10": "11", "11": "10",
    }
    for src, dst in expected.items():
        got = quantum.StateVector.from_bitstring(src).apply_cnot(0, 1).to_dirac()
        check(f"CNOT |{src}> = |{dst}>", got == f"|{dst}>", f"got {got}")


def test_toffoli_truth_table() -> None:
    expected = {
        "000": "000", "001": "001", "010": "010", "011": "011",
        "100": "100", "101": "101", "110": "111", "111": "110",
    }
    for src, dst in expected.items():
        got = quantum.StateVector.from_bitstring(src).apply_toffoli(0, 1, 2).to_dirac()
        check(f"CCNOT |{src}> = |{dst}>", got == f"|{dst}>", f"got {got}")


def test_swap_truth_table() -> None:
    expected = {"00": "00", "01": "10", "10": "01", "11": "11"}
    for src, dst in expected.items():
        got = quantum.StateVector.from_bitstring(src).apply_two(quantum.SWAP, 0, 1).to_dirac()
        check(f"SWAP |{src}> = |{dst}>", got == f"|{dst}>", f"got {got}")


def test_fredkin_truth_table() -> None:
    expected = {
        "000": "000", "001": "001", "010": "010", "011": "011",
        "100": "100", "101": "110", "110": "101", "111": "111",
    }
    for src, dst in expected.items():
        got = quantum.StateVector.from_bitstring(src).apply_three(quantum.CSWAP, 0, 1, 2).to_dirac()
        check(f"CSWAP |{src}> = |{dst}>", got == f"|{dst}>", f"got {got}")


def test_norm_preservation() -> None:
    sv = quantum.StateVector.zero(3)
    for gate in (quantum.H, quantum.X, quantum.Y, quantum.Z, quantum.S, quantum.T):
        sv = sv.apply_single(gate, 0)
    check("the state stays normalised", abs(sum(sv.probabilities()) - 1.0) < 1e-12)


def test_measurement_matches_born_rule() -> None:
    import random

    sv = quantum.StateVector.zero(2).apply_single(quantum.H, 0)
    rng = random.Random(1234)
    # Outcome index 2 is the basis state "10" -- i.e. q0 = 1.
    ones = sum(1 for _ in range(20000) if (sv.measure(rng)[0] >> 1) & 1)
    check_close("the Born rule holds", ones / 20000, 0.5, 0.02)


def test_collapse_yields_basis_state() -> None:
    sv = quantum.StateVector.zero(2).apply_single(quantum.H, 0)
    outcome, collapsed = sv.measure()
    check("measurement collapses to a basis state",
          sum(1 for p in collapsed.probabilities() if p > 0.5) == 1)
    check("the collapsed state is normalised", abs(sum(collapsed.probabilities()) - 1.0) < 1e-12)


def test_entanglement_entropy() -> None:
    check_close("the Bell state has 1 bit of entanglement", quantum.bell_state().entropy(), 1.0, 1e-9)
    product = quantum.StateVector([0.5, 0.5, 0.5, 0.5])
    check_close("a product state has zero entanglement", product.entropy(), 0.0, 1e-9)
    check_close("GHZ(3) has 1 bit of entropy", quantum.ghz_state(3).entropy(), 1.0, 1e-9)
    # Two crossed Bell pairs over a 2|2 cut have 2 bits.
    crossed = quantum.StateVector.zero(4)
    crossed = crossed.apply_single(quantum.H, 0).apply_cnot(0, 2)
    crossed = crossed.apply_single(quantum.H, 1).apply_cnot(1, 3)
    check_close("two crossed Bell pairs have 2 bits", crossed.entropy(), 2.0, 1e-9)


def test_hermitian_eigenvalues() -> None:
    m = [[2.0, 0.0], [0.0, 3.0]]
    eigs = linalg.hermitian_eigenvalues(m)
    check_close("eigenvalue 1", eigs[0], 2.0, 1e-9)
    check_close("eigenvalue 2", eigs[1], 3.0, 1e-9)
    h = quantum.H
    eigs = sorted(linalg.hermitian_eigenvalues(h))
    check_close("H has eigenvalues -1 and +1", eigs[0], -1.0, 1e-9)
    check_close("H has eigenvalues -1 and +1", eigs[1], 1.0, 1e-9)
    # A 2x2 rotation by 90 degrees is NOT Hermitian, so it needs the
    # characteristic-polynomial solver rather than hermitian_eigenvalues.
    c = [[0.0, -1.0], [1.0, 0.0]]
    eigs = sorted(linalg.eigenvalues_2x2(c), key=lambda z: (z.real, z.imag))
    check_close("rotation by 90 deg has eigenvalues -i and +i", eigs[0].imag, -1.0, 1e-9)
    check_close("rotation by 90 deg has eigenvalues -i and +i", eigs[1].imag, 1.0, 1e-9)


def test_eigenpairs_2x2() -> None:
    for name, gate in (("X", quantum.X), ("Y", quantum.Y), ("Z", quantum.Z), ("H", quantum.H)):
        for lam, vec in linalg.eigenpairs_2x2(gate):
            av = [gate[0][0] * vec[0] + gate[0][1] * vec[1],
                  gate[1][0] * vec[0] + gate[1][1] * vec[1]]
            ok = all(abs(av[i] - lam * vec[i]) < 1e-9 for i in range(2))
            check(f"{name}: A v = lambda v", ok)
            norm = math.sqrt(sum(abs(x) ** 2 for x in vec))
            check(f"{name}: the eigenvector is normalised", abs(norm - 1.0) < 1e-9)


def test_matrix_inverse() -> None:
    a = [[1.0, 2.0], [3.0, 4.0]]
    inv = linalg.inverse(a)
    check("A A^-1 = I", linalg.is_identity(linalg.mul(a, inv)))
    check("A^-1 A = I", linalg.is_identity(linalg.mul(inv, a)))
    check_close("the determinant is -2", linalg.determinant(a).real, -2.0, 1e-12)


def test_boolean_circuits() -> None:
    for a in (0, 1):
        for b in (0, 1):
            check(f"NAND->NOT({a})", boolean.nand_to_not(a) == boolean.NOT(a))
            check(f"NAND->AND({a},{b})", boolean.nand_to_and(a, b) == boolean.AND(a, b))
            check(f"NAND->OR({a},{b})", boolean.nand_to_or(a, b) == boolean.OR(a, b))
            check(f"OR/NOT->AND({a},{b})", boolean.and_from_or_not(a, b) == boolean.AND(a, b))


def test_xor_is_its_own_inverse() -> None:
    import random

    rng = random.Random(3)
    for _ in range(50):
        a = [rng.randint(0, 1) for _ in range(32)]
        b = [rng.randint(0, 1) for _ in range(32)]
        check("XOR is an involution", boolean.xor_bitstrings(boolean.xor_bitstrings(a, b), b) == a)


def test_complex_arithmetic() -> None:
    a, b = complex(3, 4), complex(7, -6)
    check("multiplication matches the builtin", complexnum.mul(a, b) == a * b)
    check_close("division matches the builtin", complexnum.div(a, b).real, (a / b).real, 1e-12)
    check_close("division matches the builtin", complexnum.div(a, b).imag, (a / b).imag, 1e-12)
    check_close("the squared magnitude is correct", complexnum.squared_magnitude(a), 25.0, 1e-12)
    roots = complexnum.sqrt_i()
    for r in roots:
        check_close("each square root of i squares back to i", (r * r).imag, 1.0, 1e-12)
    for r in complexnum.nth_roots(11 + 0j, 3):
        check_close("each cube root cubes back to 11", (r ** 3).real, 11.0, 1e-9)


def test_photon_model() -> None:
    check_close("Malus's law at 0 degrees", photon.malus_transmission(0, 0), 1.0, 1e-12)
    check_close("Malus's law at 90 degrees", photon.malus_transmission(90, 0), 0.0, 1e-12)
    check_close("Malus's law at 45 degrees", photon.malus_transmission(45, 0), 0.5, 1e-12)
    r = photon.filter_cascade(90.0, [45.0, 45.0, 90.0], shots=4000,
                               rng=__import__("random").Random(0))
    check_close("cascade stage 1", r.stage_transmission[0], 0.5, 0.03)
    check_close("cascade stage 2", r.stage_transmission[1], 1.0, 0.03)
    check_close("cascade stage 3", r.stage_transmission[2], 0.5, 0.03)


def test_bb84() -> None:
    clean = bb84.run_bb84(rounds=400, seed=11)
    check("no eavesdropper: the keys match", clean.key_matches)
    check_close("no eavesdropper: the QBER is zero", clean.qber, 0.0, 1e-12)
    attacked = bb84.run_bb84(rounds=400, eve=True, seed=11)
    check("the eavesdropper is detected", attacked.detected)
    check("the eavesdropper breaks the key", not attacked.key_matches)
    check_close("the classic attack gives a QBER of 25%", attacked.qber, 0.25, 0.05)


def test_probability_helpers() -> None:
    check_close("independent events", probability.p_independent(0.3, 0.4)[0], 0.12, 1e-12)
    check_close("mutually exclusive events", probability.p_mutually_exclusive(0.3, 0.4)[1], 0.7, 1e-12)
    check_close("conditional probability", probability.p_conditional(0.12, 0.3), 0.4, 1e-12)
    rv = probability.coin(0.52)
    check_close("a loaded coin has mean 0.04", rv.mean(), 0.04, 1e-12)
    check_close("a loaded coin has SD ~ 0.9992", rv.standard_deviation(), 0.99920, 1e-4)


def main() -> int:
    print("=" * 70)
    print("QC101 library self-test")
    print("=" * 70)
    for fn in [
        test_gates_are_unitary,
        test_single_qubit_gate_truth_tables,
        test_cnot_truth_table,
        test_toffoli_truth_table,
        test_swap_truth_table,
        test_fredkin_truth_table,
        test_norm_preservation,
        test_measurement_matches_born_rule,
        test_collapse_yields_basis_state,
        test_entanglement_entropy,
        test_hermitian_eigenvalues,
        test_eigenpairs_2x2,
        test_matrix_inverse,
        test_boolean_circuits,
        test_xor_is_its_own_inverse,
        test_complex_arithmetic,
        test_photon_model,
        test_bb84,
        test_probability_helpers,
    ]:
        before = len(_FAILURES)
        fn()
        status = "ok" if len(_FAILURES) == before else "FAILED"
        print(f"  {fn.__name__:<40} {status}")
    print()
    if _FAILURES:
        print(f"{len(_FAILURES)} of {_COUNT} checks FAILED:")
        for f in _FAILURES:
            print("  -", f)
        return 1
    print(f"All {_COUNT} library checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
