#!/usr/bin/env python3
"""
L03 -- Boolean algebra, truth tables and logic gates.

Course section: 3.1 (Boolean Algebra, Truth Tables, Logic Gates, Equivalent
Circuits, Universal Gate NAND, Exclusive OR).

Run me::

    python labs/L03_boolean_logic/lab.py

What you will build
-------------------
* Truth tables generated from code, so you can check a gate against its
  definition.
* Equivalent circuits: AND from OR/NOT, and NOT/AND/OR from NAND alone.
* The XOR operation and why it is the workhorse of cryptography.
* A one-time pad (the "shared secret" cipher) built on XOR.
"""

from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from qc101.labkit import Lab
from qc101 import boolean as b
from qc101 import viz

lab = Lab("L03", "Boolean algebra, truth tables and logic gates")


# ---------------------------------------------------------------------------
lab.section("1. Truth tables for the basic gates")
# ---------------------------------------------------------------------------
for name, fn in (("AND", b.AND), ("OR", b.OR), ("XOR", b.XOR), ("NAND", b.NAND)):
    lab.step(f"{name} gate")
    lab.show(b.render_truth_table(fn))
    lab.note("")

lab.check("AND is 1 only when both inputs are 1",
          [b.AND(a, bb) for a in (0, 1) for bb in (0, 1)] == [0, 0, 0, 1])
lab.check("OR is 1 when at least one input is 1",
          [b.OR(a, bb) for a in (0, 1) for bb in (0, 1)] == [0, 1, 1, 1])
lab.check("XOR is 1 exactly when the inputs differ",
          [b.XOR(a, bb) for a in (0, 1) for bb in (0, 1)] == [0, 1, 1, 0])
lab.check("NAND is the negation of AND",
          [b.NAND(a, bb) for a in (0, 1) for bb in (0, 1)] == [1, 1, 1, 0])


# ---------------------------------------------------------------------------
lab.section("2. Evaluation order: NOT before AND before OR")
# ---------------------------------------------------------------------------
lab.step("NOT binds tighter than AND, which binds tighter than OR.")

expression = b.OR(b.AND(b.NOT(0), 1), b.AND(1, 1))
lab.note("NOT 0 AND 1 OR 1 AND 1  =  (NOT 0 AND 1) OR (1 AND 1)  =  1 OR 1  =  1")
lab.check_equal("the expression evaluates to 1", expression, 1)

# The same circuit written the other way round is a different function.
other = b.AND(b.OR(b.NOT(0), 1), b.OR(1, 1))
lab.note("AND binds tighter, so this is NOT 0 OR (1 AND 1) = 1")
lab.check_equal("the regrouped expression is also 1 here", other, 1)
lab.note("Parentheses matter -- which is why every gate library asks you to be explicit.")


# ---------------------------------------------------------------------------
lab.section("3. Equivalent circuits: AND from OR and NOT")
# ---------------------------------------------------------------------------
lab.step("De Morgan: A AND B = NOT( NOT(A) OR NOT(B) )")

rows = []
for a in (0, 1):
    for bb in (0, 1):
        rows.append((a, bb, b.AND(a, bb), b.and_from_or_not(a, bb)))
lab.show(viz.table(["A", "B", "AND", "AND via OR/NOT"], rows))

lab.check("the two circuits have identical truth tables",
          all(b.AND(a, bb) == b.and_from_or_not(a, bb) for a in (0, 1) for bb in (0, 1)))
lab.note("Identical truth tables mean identical functions.  This is the whole basis of "
         "circuit equivalence in digital design.")


# ---------------------------------------------------------------------------
lab.section("4. NAND is a universal gate")
# ---------------------------------------------------------------------------
lab.step("Rebuild NOT, AND and OR out of NAND alone.")

lab.note("NOT A   = NAND(A, A)")
lab.note("A AND B = NOT( NAND(A, B) )")
lab.note("A OR B  = NAND( NOT A, NOT B )")

rows = []
for a in (0, 1):
    for bb in (0, 1):
        rows.append((
            a, bb,
            b.NAND(a, a), b.NAND(a, bb), b.NAND(b.NAND(a, a), b.NAND(bb, bb)),
        ))
lab.show(viz.table(["A", "B", "NOT A (NAND)", "A AND B (NAND)", "A OR B (NAND)"], rows))

lab.check("NAND reproduces NOT",
          all(b.nand_to_not(a) == b.NOT(a) for a in (0, 1)))
lab.check("NAND reproduces AND",
          all(b.nand_to_and(a, bb) == b.AND(a, bb) for a in (0, 1) for bb in (0, 1)))
lab.check("NAND reproduces OR",
          all(b.nand_to_or(a, bb) == b.OR(a, bb) for a in (0, 1) for bb in (0, 1)))
lab.note("Because NAND is universal, *any* classical logic function can be built from "
         "NAND gates.  The same idea reappears in quantum computing: the Toffoli gate "
         "is universal for *reversible* classical computation (see L11).")


# ---------------------------------------------------------------------------
lab.section("5. XOR of bit sequences")
# ---------------------------------------------------------------------------
lab.step("Element-wise XOR of two bit strings.")

a = [1, 0, 1, 1, 0, 1, 0]
c = [0, 1, 1, 0, 1, 0, 0]
result = b.xor_bitstrings(a, c)
lab.note(f"a = {''.join(map(str, a))}")
lab.note(f"b = {''.join(map(str, c))}")
lab.note(f"a XOR b = {''.join(map(str, result))}")
lab.check_equal("element-wise XOR is correct", result, [1, 1, 0, 1, 1, 1, 0])
lab.check("XOR is its own inverse", b.xor_bitstrings(result, c) == a)
lab.note("XOR is reversible -- that is exactly why it is the basis of symmetric "
         "cryptography, and later of the CNOT gate.")


# ---------------------------------------------------------------------------
lab.section("6. Cryptography with XOR: the shared secret")
# ---------------------------------------------------------------------------
lab.step("Encrypt a message with a shared secret, then decrypt it.")

message = "Meet me at 9."
key = [1, 0, 1, 1, 0, 0, 1, 0] * 40
cipher = b.encrypt(message, key)
plain = b.decrypt(cipher, key)
lab.note(f"message : {message!r}")
lab.note(f"cipher  : {''.join(map(str, cipher))}")
lab.note(f"decoded : {plain!r}")
lab.check_equal("decrypting with the same key recovers the message", plain, message)
lab.check("the ciphertext looks nothing like the plaintext", "".join(map(str, cipher)) != message)


# ---------------------------------------------------------------------------
lab.section("7. Breaking a reused key -- and the one-time pad fix")
# ---------------------------------------------------------------------------
lab.step("Reusing a key leaks the XOR of the two plaintexts.")

m1 = "Attack at dawn"
m2 = "Retreat at noon"[: len(m1)].ljust(len(m1))  # same length, so the XOR lines up
reused = [1, 0, 1, 0, 1, 1, 0, 0] * 30
c1 = b.encrypt(m1, reused)
c2 = b.encrypt(m2, reused)
leaked = b.xor_bitstrings(c1, c2)
lab.note("cipher1 XOR cipher2 == plaintext1 XOR plaintext2")
lab.note(f"recovered: {b.decrypt(leaked, [0] * len(leaked))!r}  <- a mix of both messages")
lab.check("XOR of the two ciphertexts equals XOR of the two plaintexts",
          leaked == b.xor_bitstrings(b.encrypt(m1, reused), b.encrypt(m2, reused)))
lab.note("Never reuse a key.  Use a fresh random key as long as the message -- then "
         "the ciphertext carries *no* information about the plaintext at all.")

rng = random.Random(7)
secret_msg = "Quantum key distribution is unconditionally secure."
cipher, pad = b.one_time_pad_encrypt(secret_msg, rng)
recovered = b.one_time_pad_decrypt(cipher, pad)
lab.check_equal("a one-time pad decrypts perfectly", recovered, secret_msg)
lab.check("the pad is as long as the message", len(pad) == len(cipher))
lab.note("The one-time pad is the basis of the BB84 protocol in L07: Alice and Bob "
         "build a *shared* random secret that an eavesdropper cannot obtain.")


if __name__ == "__main__":
    sys.exit(lab.finish())
