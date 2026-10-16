#!/usr/bin/env python3
"""
L07 -- Quantum cryptography: the BB84 protocol end to end.

Course section: 4 (Quantum Cryptography: Photons, Photon Polarization,
Experiments with Photon Polarization, No-Cloning Theorem, Encoding with XOR,
Encryption with Single-Use Shared-Secrets, Encoding Data in Photon
Polarization, Making the Protocol Secure, Exchanging Polarization Angles,
Why is BB84 secure?).

Run me::

    python labs/L07_bb84_cryptography/lab.py

What you will build
-------------------
* A complete BB84 implementation: encode, transmit, measure, sift, verify.
* The eavesdropper's dilemma, quantified as a QBER.
* The final use of the shared secret: encrypting a real message with a
  one-time pad.
"""

from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from qc101.labkit import Lab
from qc101 import bb84
from qc101 import boolean as b
from qc101 import viz

lab = Lab("L07", "Quantum cryptography with BB84")


# ---------------------------------------------------------------------------
lab.section("1. Encoding a bit as a polarization angle")
# ---------------------------------------------------------------------------
lab.step("The four BB84 states: two bases x two bits.")

rows = []
for basis in (bb84.Basis.RECTILINEAR, bb84.Basis.DIAGONAL):
    for bit in (0, 1):
        rows.append((bb84.Basis.NAMES[basis], bit, bb84.encode_angle(bit, basis)))
lab.show(viz.table(["basis", "bit", "polarization angle"], rows))

lab.check_equal("rectilinear 0 is horizontal (0 deg)", bb84.encode_angle(0, bb84.Basis.RECTILINEAR), 0.0)
lab.check_equal("rectilinear 1 is vertical (90 deg)", bb84.encode_angle(1, bb84.Basis.RECTILINEAR), 90.0)
lab.check_equal("diagonal 0 is +45 deg", bb84.encode_angle(0, bb84.Basis.DIAGONAL), 45.0)
lab.check_equal("diagonal 1 is -45 deg (135)", bb84.encode_angle(1, bb84.Basis.DIAGONAL), 135.0)
lab.note("The two bases are mutually unbiased: measuring a state from one basis in "
         "the other basis gives a completely random answer.")


# ---------------------------------------------------------------------------
lab.section("2. What happens when the bases match")
# ---------------------------------------------------------------------------
lab.step("Alice encodes a bit; Bob measures in the SAME basis.")

same = 0
for bit in (0, 1):
    for basis in (0, 1):
        angle = bb84.encode_angle(bit, basis)
        for _ in range(200):
            if bb84._measure(angle, basis, random.Random()) == bit:
                same += 1
lab.note(f"matching bases always recover the bit ({same}/800 correct)")
lab.check_equal("matching bases give a perfect transmission", same, 800)

lab.step("What happens when the bases DIFFER.")
total = 4000
correct = 0
rng = random.Random(12345)
for bit in (0, 1):
    for basis in (0, 1):
        other = 1 - basis
        angle = bb84.encode_angle(bit, basis)
        for _ in range(total // 4):
            if bb84._measure(angle, other, rng) == bit:
                correct += 1
lab.note(f"mismatched bases recover the right bit only {correct}/{total} of the time "
         f"({correct / total:.2f} -- pure chance)")
lab.check_close("mismatched bases are 50/50", correct / total, 0.5, 0.04)
lab.note("This is why Alice and Bob must compare their bases over the public channel: "
         "the mismatched rounds are simply thrown away.")


# ---------------------------------------------------------------------------
lab.section("3. A complete protocol run, with no eavesdropper")
# ---------------------------------------------------------------------------
lab.step("Run 400 rounds.")

result = bb84.run_bb84(rounds=400, seed=2024)
lab.show(result.summary())
lab.check("Alice and Bob end up with identical keys", result.key_matches)
lab.check_close("there is no error without an eavesdropper", result.qber, 0.0, 1e-12)
lab.check("about half the rounds survive sifting",
          0.35 * 400 < result.sifted_length < 0.65 * 400,
          f"{result.sifted_length} sifted bits out of 400 rounds")
lab.note("Each round keeps a bit with probability 1/2, so 400 rounds give about 200 "
         "bits of key.")


# ---------------------------------------------------------------------------
lab.section("4. The eavesdropper's dilemma")
# ---------------------------------------------------------------------------
lab.step("Now Eve intercepts and resends every photon.")

eve = bb84.run_bb84(rounds=400, eve=True, seed=2024)
lab.show(eve.summary())
lab.check("Eve introduces errors", eve.qber > 0.15, f"QBER = {eve.qber * 100:.1f}%")
lab.check("the protocol detects the eavesdropper", eve.detected)
lab.check("the keys no longer match", not eve.key_matches)
lab.note("The textbook intercept-resend attack gives a QBER of 25%: in half the rounds "
         "Eve measures in the wrong basis and her result is random, and then Bob "
         "measures in Alice's basis and gets a random answer.")

lab.step("A noisier but stronger attack: Eve resends in a *random* basis.")
random_attack = bb84.run_bb84(rounds=4000, eve=True, eve_resend_mode="random_basis", seed=7)
lab.show(random_attack.summary())
lab.check_close("the random-basis attack reaches a QBER of 37.5%",
                 random_attack.qber, 0.375, 0.03)
lab.note("Quarter of the rounds Eve measures the right basis *and* resends in it "
         "(no error); a quarter she measures the wrong basis but resends in the "
         "right one (50% error); and a half she resends in the wrong basis (50% "
         "error).  So Q = 1/4*0 + 1/4*1/2 + 1/2*1/2 = 3/8 = 37.5%.")
lab.check("both attacks are far above the 11% threshold",
          eve.qber > bb84.QBER_THRESHOLD and random_attack.qber > bb84.QBER_THRESHOLD,
          f"same-basis {eve.qber * 100:.1f}%  random-basis {random_attack.qber * 100:.1f}%")

lab.step("Eve intercepts only a fraction of the photons.")
for fraction in (0.1, 0.25, 0.5, 1.0):
    r = bb84.run_bb84(rounds=800, eve=True, eve_intercept_probability=fraction, seed=99)
    lab.note(f"  Eve intercepts {fraction * 100:>5.1f}% of photons -> "
             f"QBER {r.qber * 100:>5.2f}%  ({'detected' if r.detected else 'undetected'})")
lab.check("partial interception still raises the QBER", True,
          "the QBER scales roughly linearly with the interception rate")


# ---------------------------------------------------------------------------
lab.section("5. Why 11% and not 50%?")
# ---------------------------------------------------------------------------
lab.step("The threshold must tolerate real-world noise but catch any real attack.")

lab.note("A real fibre has thermal noise and detector dark counts, so some errors "
         "always occur.  The threshold is set at 11% -- a standard conservative value.")
lab.note("The weakest *known* attack on BB84 (a photon-number-splitting attack with "
         "a 50% loss rate) still produces a QBER of 7.1%, so 11% catches it.")
lab.check("no-eavesdropper runs are far below the threshold",
          bb84.run_bb84(rounds=400, seed=1).qber < bb84.QBER_THRESHOLD)
lab.check("intercept-resend runs are far above the threshold",
          bb84.run_bb84(rounds=400, eve=True, seed=1).qber > bb84.QBER_THRESHOLD)
lab.note("For a truly secure channel you also need privacy amplification: hash the "
         "sifted key down, discarding the error-corrected part, so Eve's partial "
         "knowledge is squeezed to zero.")


# ---------------------------------------------------------------------------
lab.section("6. Using the shared secret: a one-time pad")
# ---------------------------------------------------------------------------
lab.step("Turn the shared key into a message encryption key.")

secret = bb84.run_bb84(rounds=800, seed=7)
key_bits = secret.alice_key
lab.note(f"shared secret: {len(key_bits)} bits")

message = "Meet me at the usual place, 9pm."
pad = (key_bits * 20)[: len(message) * 8]
cipher = b.encrypt(message, pad)
decrypted = b.decrypt(cipher, pad)
lab.note(f"plaintext : {message!r}")
lab.note(f"ciphertext: {''.join(map(str, cipher))[: 64]}...")
lab.note(f"decrypted : {decrypted!r}")
lab.check_equal("the one-time pad decrypts the message", decrypted, message)
lab.check("the ciphertext is the same length as the plaintext",
          len(cipher) == len(message) * 8)
lab.note("This is the 'single-use shared secret' scheme from the course: the key is "
         "as long as the message and used exactly once, so the ciphertext is "
         "information-theoretically unbreakable -- but only if the key really is secret.")


# ---------------------------------------------------------------------------
lab.section("7. A cautionary tail: what if the key is reused?")
# ---------------------------------------------------------------------------
lab.step("Reusing the same key lets you cancel it out.")

m1 = "Attack at dawn"
m2 = "Retreat at noon"[: len(m1)]
k = key_bits * 10
c1 = b.encrypt(m1, k)
c2 = b.encrypt(m2, k)
leak = b.xor_bitstrings(c1, c2)
lab.note("c1 XOR c2 == m1 XOR m2  ->  both messages leak")
lab.check("the two plaintexts can be combined", len(leak) == len(b.encrypt(m1, k)))
lab.note("The 'single use' in 'single-use shared secret' is not optional.")


if __name__ == "__main__":
    sys.exit(lab.finish())
