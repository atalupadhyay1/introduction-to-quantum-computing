# Section 4 — Quantum Cryptography

> **Course section** 4 of 17 · **Lab** [`L07`](../labs/L07_bb84_cryptography/lab.py) · **Quiz** 6 questions

## What you should be able to do

- Run the BB84 protocol end to end and explain every step.
- Compute the quantum bit error rate for the no-eve, same-basis-eve and
  random-basis-eve cases.
- Say why a one-time pad is unconditionally secure and what it needs.
- Explain why classical "public key" cryptography is a different game.

## The protocol (BB84, 1984)

Bennett and Brassard named their protocol after the year. Each round:

1. **Alice** picks a random bit $b \in \{0,1\}$ and a random basis
   $B \in \{Z, X\}$.
2. Alice sends a photon prepared in that basis: $Z$ (rectilinear, 0°/90°)
   or $X$ (diagonal, 45°/135°).
3. **Bob** picks a random basis $B'$ and measures.
4. Alice and Bob **publicly announce their bases** (never the bit values).
5. They keep only the rounds where $B = B'$; those bits form the key.

The security rests on one fact: **measuring in the wrong basis destroys the
information**. A photon in state $|+\rangle$ measured in the $Z$ basis gives
$0$ or $1$ with equal probability, no matter what it "really" was.

## The quantum bit error rate

Let $Q$ be the fraction of sifted bits that disagree. This is the number
that reveals an eavesdropper.

| Scenario | QBER |
|---|---|
| No eavesdropper | $0\%$ |
| Eve intercepts and resends **in the basis she measured in** (the textbook attack) | $25\%$ |
| Eve intercepts and resends **in a random basis** | $37.5\%$ |

**Where 25% comes from.** Eve measures each photon in a basis of her own
choosing and resends a fresh photon in *that* basis.

- With probability $\tfrac12$ she happens to pick Alice's basis, so she
  measures the bit correctly and resends it correctly — no error.
- With probability $\tfrac12$ she picks the other basis, so her result is
  random, and Bob's reading of her resend is random too — a 50% error rate.

$$
Q = \tfrac12 \cdot 0 + \tfrac12 \cdot \tfrac12 = \tfrac14 = 25\%
$$

**Where 37.5% comes from.** A noisier but stronger attack: Eve resends in
a *random* basis instead of the one she measured in. Then

- $\tfrac14$ of the time she measures Alice's basis *and* resends in
  Alice's basis: no error at all;
- $\tfrac14$ of the time she measures the wrong basis but resends in
  Alice's basis: her bit is random, so a 50% error rate;
- $\tfrac12$ of the time she resends in the wrong basis: Bob's reading is
  random, so a 50% error rate.

$$
Q = \tfrac14 \cdot 0 + \tfrac14 \cdot \tfrac12 + \tfrac12 \cdot \tfrac12
= \tfrac38 = 37.5\%
$$

Both are far above the threshold, so both are caught.

**The threshold.** In a one-way BB84 system, aborting when $Q > 11\%$ is
the standard rule. The bound is $Q_{\text{intercept}} \approx 0.1464$,
and the abort threshold is roughly $\frac{2}{3}$ of that.

## The one-time pad

BB84 only gives you a shared *random* key. To encrypt a message with it you
need the one-time pad:

$$
C = M \oplus K, \qquad M = C \oplus K
$$

It is **unconditionally secure** — secure regardless of how much
computation the eavesdropper can do — but only if:

- the key is used **once** and only once;
- the key is **uniformly random**;
- the key is **the same length** as the message;
- the key is shared **secretly**.

Reuse a key and XOR-ing the two ciphertexts leaks the XOR of the two
plaintexts. That is exactly how the Vigenère cipher falls.

## Try it yourself

```bash
python labs/L07_bb84_cryptography/lab.py
```

The lab runs the full protocol, sifts the key, measures the QBER in all
three scenarios, and then applies a one-time pad to a message and shows the
ciphertext decrypts perfectly.

## Self-check

- [ ] Can you explain why the bases may be announced publicly but the bit
      values may not?
- [ ] Can you derive the 25% QBER figure from scratch?
- [ ] Do you know the three requirements of a one-time pad, and what
      happens if you break each one?
- [ ] Have you run `python labs/L07_bb84_cryptography/lab.py`?

## Where to go next

Section 5 — [A Math Model for Quantum Physics](05-math-model.md). You have
seen the physics; now build the formal model that makes it computable.
