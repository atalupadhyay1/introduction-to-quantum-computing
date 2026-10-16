"""
BB84 quantum key distribution -- a full, runnable implementation.

This implements the protocol taught in Section 4 of QC101 and Section 15
("Implementing BB84 Cryptography") of the Qiskit part of the course.

Protocol summary
----------------
1. **Alice** picks a random bit ``a`` and a random basis ``b_A``.
2. Alice encodes the bit as photon polarization:
   ``b_A = 0`` (rectilinear) -> ``0 deg`` for 0, ``90 deg`` for 1
   ``b_A = 1`` (diagonal)  -> ``45 deg`` for 0, ``135 deg`` for 1
3. **Bob** picks a random basis ``b_B`` and measures the photon in it.
   If ``b_B != b_A`` the result is random and the bit is *lost*.
4. Over a **public** channel Alice and Bob announce only their *bases*
   (never the bit values).
5. They **sift**: keep only the rounds where the bases matched.
6. They **verify** by comparing a sample of the sifted key publicly; if the
   error rate (QBER) is too high they abort.

If an eavesdropper (Eve) measures the photon and resends it, she
introduces errors in exactly the rounds where she guessed the wrong basis.
The QBER therefore rises from 0% (no Eve) to 25% (Eve intercepts every
photon), which is detectable in a handful of rounds.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

__all__ = [
    "Basis",
    "Round",
    "BB84Result",
    "run_bb84",
    "encode_angle",
    "basis_angle",
    "QBER_THRESHOLD",
]

#: Fraction of mismatched bits above which we abort the protocol.
QBER_THRESHOLD = 0.11  # 11% -- the conservative, widely used bound.


class Basis:
    """The two BB84 bases."""

    RECTILINEAR = 0
    DIAGONAL = 1

    NAMES = {RECTILINEAR: "rectilinear (0/90 deg)", DIAGONAL: "diagonal (45/135 deg)"}


def basis_angle(basis: int, bit: int) -> float:
    """
    The polarization angle that encodes ``bit`` in ``basis``.

    ``basis_angle(0, 0) = 0``   ``basis_angle(0, 1) = 90``
    ``basis_angle(1, 0) = 45``  ``basis_angle(1, 1) = 135``
    """
    if basis == Basis.RECTILINEAR:
        return 0.0 if bit == 0 else 90.0
    if basis == Basis.DIAGONAL:
        return 45.0 if bit == 0 else 135.0
    raise ValueError(f"unknown basis {basis}")


def encode_angle(bit: int, basis: int) -> float:
    """Alias of :func:`basis_angle` -- the angle Alice actually sends."""
    return basis_angle(basis, bit)


def _measure(angle: float, basis: int, rng: random.Random) -> int:
    """
    Measure a photon of polarization ``angle`` in ``basis``.

    Returns 0 or 1.  When the photon's polarization is *not* aligned or
    anti-aligned with the basis, the outcome is random -- this is the
    physical source of eavesdropping errors.
    """
    axis = basis_angle(basis, 0)
    delta = math.radians(angle - axis)
    p_zero = math.cos(delta) ** 2
    return 0 if rng.random() < p_zero else 1


@dataclass
class Round:
    """One round of the protocol, with every random choice recorded."""

    index: int
    bit: int
    alice_basis: int
    angle: float
    bob_basis: int
    bob_bit: int
    eve_present: bool = False
    eve_basis: Optional[int] = None
    eve_bit: Optional[int] = None
    matched_basis: bool = False
    sifted: bool = False

    def describe(self) -> str:
        lines = [
            f"Round {self.index:>3}: "
            f"bit={self.bit}  A-basis={Basis.NAMES[self.alice_basis]:<26} "
            f"angle={self.angle:>5.1f} deg  B-basis={Basis.NAMES[self.bob_basis]:<26} "
            f"B-bit={self.bob_bit}"
        ]
        if self.eve_present:
            lines.append(
                f"          Eve measured in {Basis.NAMES[self.eve_basis]:<26} "
                f"got {self.eve_bit}"
            )
        if self.sifted:
            status = "KEPT" if self.bob_bit == self.bit else "MISMATCH (eavesdropping!)"
            lines.append(f"          -> sifted: {status}")
        return "\n".join(lines)


@dataclass
class BB84Result:
    """The outcome of a full BB84 run."""

    rounds: List[Round] = field(default_factory=list)
    alice_key: List[int] = field(default_factory=list)
    bob_key: List[int] = field(default_factory=list)
    eve_present: bool = False
    eve_intercepts: int = 0

    @property
    def sifted_length(self) -> int:
        """How many bits survived the sifting step."""
        return len(self.alice_key)

    @property
    def mismatches(self) -> int:
        """How many sifted bits disagree -- the error count."""
        return sum(1 for a, b in zip(self.alice_key, self.bob_key) if a != b)

    @property
    def qber(self) -> float:
        """Quantum bit error rate: mismatches / sifted bits."""
        if not self.alice_key:
            return 0.0
        return self.mismatches / len(self.alice_key)

    @property
    def detected(self) -> bool:
        """True when the QBER exceeds the abort threshold."""
        return self.qber > QBER_THRESHOLD

    @property
    def key_matches(self) -> bool:
        """True when Alice's and Bob's sifted keys are identical."""
        return self.alice_key == self.bob_key

    def summary(self) -> str:
        """A human-readable report of the run."""
        lines = [
            "=" * 66,
            f"BB84 protocol summary ({'EAVE' if self.eve_present else 'no eavesdropper'})",
            "=" * 66,
            f"rounds executed        : {len(self.rounds)}",
            f"rounds sifted (matched): {self.sifted_length}",
            f"mismatched bits        : {self.mismatches}",
            f"QBER                   : {self.qber * 100:.2f}%",
            f"abort threshold        : {QBER_THRESHOLD * 100:.2f}%",
            f"eavesdropping detected : {'YES' if self.detected else 'no'}",
            f"keys identical         : {'YES' if self.key_matches else 'NO'}",
        ]
        if self.eve_present:
            lines.append(f"Eve intercepted        : {self.eve_intercepts} photons")
        if self.alice_key:
            lines.append("")
            lines.append(f"Alice's key : {''.join(str(b) for b in self.alice_key)}")
            lines.append(f"Bob's key   : {''.join(str(b) for b in self.bob_key)}")
            lines.append("")
            lines.append(
                "This shared secret can now be used as a one-time pad to encrypt "
                "a message."
            )
        else:
            lines.append("")
            lines.append("No key was produced (no rounds had matching bases).")
        return "\n".join(lines)


def run_bb84(
    rounds: int = 200,
    eve: bool = False,
    eve_intercept_probability: float = 1.0,
    eve_resend_mode: str = "same_basis",
    seed: Optional[int] = None,
    verbose: bool = False,
) -> BB84Result:
    """
    Run the BB84 protocol end to end.

    Parameters
    ----------
    rounds:
        How many photons Alice sends.
    eve:
        When True, an eavesdropper intercepts photons, measures them and
        resends them (the classic *intercept-resend* attack).
    eve_intercept_probability:
        Probability that Eve intercepts any given photon.
    eve_resend_mode:
        ``"same_basis"`` (default) -- Eve resends in the basis she measured
        in.  This is the textbook attack and yields a QBER of **25%** on the
        sifted key.  ``"random_basis"`` -- Eve resends in a *random* basis,
        which is a stronger (and noisier) attack giving ~37.5%.
    seed:
        Seed for the RNG, so runs are reproducible.
    verbose:
        Print every round as it happens.
    """
    if eve_resend_mode not in ("same_basis", "random_basis"):
        raise ValueError("eve_resend_mode must be 'same_basis' or 'random_basis'")
    rng = random.Random(seed)
    result = BB84Result(eve_present=eve)

    for i in range(rounds):
        bit = rng.randint(0, 1)
        alice_basis = rng.randint(0, 1)
        angle = encode_angle(bit, alice_basis)
        bob_basis = rng.randint(0, 1)

        eve_basis: Optional[int] = None
        eve_bit: Optional[int] = None
        if eve and rng.random() < eve_intercept_probability:
            eve_basis = rng.randint(0, 1)
            eve_bit = _measure(angle, eve_basis, rng)
            # Eve resends a photon.  She has no way to know which basis
            # Alice used, so she either reuses her own measurement basis
            # ("same_basis") or picks a fresh one at random.
            resend_basis = eve_basis if eve_resend_mode == "same_basis" else rng.randint(0, 1)
            angle = basis_angle(resend_basis, eve_bit)
            result.eve_intercepts += 1

        bob_bit = _measure(angle, bob_basis, rng)
        matched = alice_basis == bob_basis

        rnd = Round(
            index=i,
            bit=bit,
            alice_basis=alice_basis,
            angle=angle,
            bob_basis=bob_basis,
            bob_bit=bob_bit,
            eve_present=eve_basis is not None,
            eve_basis=eve_basis,
            eve_bit=eve_bit,
            matched_basis=matched,
            sifted=matched,
        )
        result.rounds.append(rnd)

        if matched:
            result.alice_key.append(bit)
            result.bob_key.append(bob_bit)

        if verbose:
            print(rnd.describe())

    return result
