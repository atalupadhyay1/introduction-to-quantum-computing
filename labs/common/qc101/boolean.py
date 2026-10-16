"""
Boolean algebra, truth tables, logic gates and XOR-based cryptography.

Covers Section 3.1 of QC101 (Boolean Algebra, Truth Tables, Logic Gates,
Equivalent Circuits, Universal Gate NAND, Exclusive OR) and the XOR cipher
used to motivate quantum cryptography in Section 4.
"""

from __future__ import annotations

import random
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

__all__ = [
    "AND",
    "OR",
    "NOT",
    "XOR",
    "NAND",
    "NOR",
    "truth_table",
    "and_from_or_not",
    "nand_to_and",
    "nand_to_or",
    "nand_to_not",
    "xor_bitstrings",
    "encrypt",
    "decrypt",
    "one_time_pad_encrypt",
    "one_time_pad_decrypt",
    "bit_frequency",
    "hamming_distance",
]

Bit = int
Expr = Callable[..., bool]


# --------------------------------------------------------------------------
# Primitive gates
# --------------------------------------------------------------------------
def AND(a: Bit, b: Bit) -> Bit:
    """AND gate: 1 only when both inputs are 1."""
    return int(bool(a) and bool(b))


def OR(a: Bit, b: Bit) -> Bit:
    """OR gate: 1 when at least one input is 1."""
    return int(bool(a) or bool(b))


def NOT(a: Bit) -> Bit:
    """NOT gate: flips the bit."""
    return int(not bool(a))


def XOR(a: Bit, b: Bit) -> Bit:
    """Exclusive OR: 1 exactly when the two inputs differ."""
    return int(bool(a) != bool(b))


def NAND(a: Bit, b: Bit) -> Bit:
    """NAND gate: NOT(AND(a, b)). A universal gate."""
    return NOT(AND(a, b))


def NOR(a: Bit, b: Bit) -> Bit:
    """NOR gate: NOT(OR(a, b))."""
    return NOT(OR(a, b))


# --------------------------------------------------------------------------
# Truth tables
# --------------------------------------------------------------------------
def truth_table(fn: Expr, inputs: Sequence[str] = ("A", "B")) -> List[Tuple[Tuple[Bit, ...], Bit]]:
    """
    Build the truth table of a boolean function.

    Returns a list of ``(input_tuple, output)`` pairs, ordered so that the
    input bits vary fastest on the right-hand side (the standard convention).
    """
    n = len(inputs)
    rows: List[Tuple[Tuple[Bit, ...], Bit]] = []
    for i in range(2**n):
        bits = tuple((i >> (n - 1 - k)) & 1 for k in range(n))
        rows.append((bits, int(bool(fn(*bits)))))
    return rows


def render_truth_table(
    fn: Expr,
    inputs: Sequence[str] = ("A", "B"),
    output: str = "OUT",
) -> str:
    """Render a truth table as a nicely aligned text table."""
    rows = truth_table(fn, inputs)
    header = list(inputs) + [output]
    widths = [max(len(h), 3) for h in header]
    for bits, out in rows:
        for k, b in enumerate(bits):
            widths[k] = max(widths[k], len(str(b)))
        widths[-1] = max(widths[-1], len(str(out)))

    def fmt(cells: Sequence[str]) -> str:
        return "| " + " | ".join(c.ljust(widths[i]) for i, c in enumerate(cells)) + " |"

    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    lines = [fmt(header), sep]
    for bits, out in rows:
        lines.append(fmt([str(b) for b in bits] + [str(out)]))
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Equivalent circuits
# --------------------------------------------------------------------------
def and_from_or_not(a: Bit, b: Bit) -> Bit:
    """
    AND built only from OR and NOT gates.

    De Morgan: ``A AND B = NOT( NOT(A) OR NOT(B) )``
    """
    return NOT(OR(NOT(a), NOT(b)))


def nand_to_and(a: Bit, b: Bit) -> Bit:
    """AND built from a single NAND gate: ``AND = NOT(NAND)``."""
    return NOT(NAND(a, b))


def nand_to_or(a: Bit, b: Bit) -> Bit:
    """OR built from NAND gates: ``OR = NAND(NOT A, NOT B)``."""
    return NAND(NOT(a), NOT(b))


def nand_to_not(a: Bit) -> Bit:
    """NOT built from a NAND gate: ``NOT A = NAND(A, A)``."""
    return NAND(a, a)


# --------------------------------------------------------------------------
# Bit sequences and XOR
# --------------------------------------------------------------------------
def xor_bitstrings(a: Sequence[Bit], b: Sequence[Bit]) -> List[Bit]:
    """
    Element-wise XOR of two bit sequences.

    Both sequences must have the same length.
    """
    if len(a) != len(b):
        raise ValueError(f"bit sequences must be the same length ({len(a)} != {len(b)})")
    return [XOR(x, y) for x, y in zip(a, b)]


def _bits_to_int(bits: Sequence[Bit]) -> int:
    value = 0
    for b in bits:
        value = (value << 1) | (int(b) & 1)
    return value


def _int_to_bits(value: int, length: int) -> List[Bit]:
    return [(value >> (length - 1 - i)) & 1 for i in range(length)]


def encrypt(message: str, key: Sequence[Bit]) -> List[Bit]:
    """
    Encrypt a text message with XOR against a shared secret bit sequence.

    The message is first converted to bytes, then each byte to 8 bits.
    """
    data = message.encode("utf-8")
    bits: List[Bit] = []
    for byte in data:
        bits.extend(_int_to_bits(byte, 8))
    if len(key) < len(bits):
        raise ValueError("key is too short for this message")
    return xor_bitstrings(bits, list(key[: len(bits)]))


def decrypt(cipher: Sequence[Bit], key: Sequence[Bit]) -> str:
    """Decrypt an XOR cipher by XOR-ing with the same shared secret again."""
    bits = xor_bitstrings(list(cipher), list(key[: len(cipher)]))
    data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        data.append(_bits_to_int(bits[i : i + 8]))
    return data.decode("utf-8", errors="replace")


def one_time_pad_encrypt(message: str, rng: random.Random | None = None) -> Tuple[List[Bit], List[Bit]]:
    """
    Encrypt with a *fresh random* one-time pad.

    Returns ``(cipher_bits, pad_bits)``.  Because the pad is random and used
    only once, the ciphertext is information-theoretically unbreakable.
    """
    rng = rng or random
    data = message.encode("utf-8")
    bits: List[Bit] = []
    for byte in data:
        bits.extend(_int_to_bits(byte, 8))
    pad = [rng.randint(0, 1) for _ in range(len(bits))]
    return xor_bitstrings(bits, pad), pad


def one_time_pad_decrypt(cipher: Sequence[Bit], pad: Sequence[Bit]) -> str:
    """Decrypt a one-time pad message."""
    return decrypt(cipher, pad)


# --------------------------------------------------------------------------
# Analysis helpers
# --------------------------------------------------------------------------
def bit_frequency(bits: Iterable[Bit]) -> float:
    """Fraction of 1-bits in a sequence (the mean of a Bernoulli variable)."""
    bits = list(bits)
    if not bits:
        return 0.0
    return sum(int(b) & 1 for b in bits) / len(bits)


def hamming_distance(a: Sequence[Bit], b: Sequence[Bit]) -> int:
    """Number of positions where two equal-length bit strings differ."""
    if len(a) != len(b):
        raise ValueError("bit strings must be the same length")
    return sum(1 for x, y in zip(a, b) if bool(x) != bool(y))
