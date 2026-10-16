# Section 8 — Reversible and Irreversible State Transformations

> **Course section** 8 of 17 · **Lab** [`L11`](../labs/L11_reversible_entanglement/lab.py) · **Quiz** 6 questions

## What you should be able to do

- Say why a gate is reversible and what "unitary" has to do with it.
- Distinguish the reversible operations (gates) from the irreversible ones
  (measurement, reset).
- State and apply the no-cloning theorem's consequences.
- Build a circuit that computes a classical function *in place*.

## Reversible means invertible

A gate $U$ is reversible because

$$
U^\dagger U = I \quad\Longrightarrow\quad U^{-1} = U^\dagger
$$

so you can always undo it. Concretely: $H^{-1} = H$, $X^{-1} = X$,
$T^{-1} = T^\dagger = T^3$.

The corollary is the one that matters for computing: **you cannot have a
quantum program that computes a function and then forgets the input.**
Any classical function you want to compute with a quantum circuit must be
written so that the input is preserved, typically in extra "ancilla"
qubits.

The lab's XOR construction is exactly this. With an ancilla $C = |0\rangle$:

$$
\text{Toffoli}(A,B;C)\;\to\;\text{Toffoli}(A,B;C)\;\to\;\text{CNOT}(B \to A)
$$

computes $(A \oplus B, B, 0)$ — the XOR of the two inputs, with the
original inputs intact and the ancilla returned to $|0\rangle$. The first
Toffoli *computes* $A \land B$ into $C$, the second *uncomputes* it (which
is possible because the Toffoli is its own inverse), and the CNOT does the
XOR using the copy.

## Irreversible operations

| Operation | Irreversible? | Why |
|---|---|---|
| Any unitary gate | no | it has an inverse |
| Measurement | **yes** | many-to-one, information is destroyed |
| Reset to $|0\rangle$ | **yes** | same |
| Preparation of a state | **yes** | the state you prepared is gone |

Measurement is modelled by a projector $P = |0\rangle\langle0|$ (or its
partner). The post-measurement state is

$$
\lvert\psi'\rangle = \frac{P\lvert\psi\rangle}{\lVert P\lvert\psi\rangle\rVert}
$$

— the *normalized projection*, which is why the post-measurement state is
always a basis state (or a superposition within a degenerate subspace).

## No-cloning

**The theorem.** There is no unitary operation that maps
$|\psi\rangle \mapsto |\psi\rangle|\psi\rangle$ for every unknown state
$|\psi\rangle$.

**The proof sketch.** If such a $U$ existed, then $U(|0\rangle|0\rangle) =
|00\rangle$ and $U(|1\rangle|1\rangle) = |11\rangle$. By linearity,
$U(|+\rangle|+\rangle) = \frac12(|00\rangle + |11\rangle)$. But cloning
should give $|+\rangle|+\rangle = \frac12(|00\rangle + |01\rangle +
|10\rangle + |11\rangle)$. These differ, so no such $U$ exists.

**Why it matters.** It is the reason quantum cryptography is interesting
(an eavesdropper cannot copy the qubits and keep a perfect copy) and the
reason quantum error correction is hard (you cannot back up a qubit).

Note that the theorem is about *unknown* states: you can clone a known
state, and you can clone a whole *basis* consistently, which is exactly
what the classical "intercept and resend" attack does.

## Different bases, different answers

Two states can be perfectly distinguishable in one basis and completely
indistinguishable in another:

$$
|+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt2},
\qquad
|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt2}
$$

Both give 50/50 in the $Z$ basis; they are perfectly distinguishable in the
$X$ basis (measure with $H$ first, then in $Z$). The overlap
$\langle +|-\rangle = 0$ is the right measure of "how different" two
states are, and it is the quantity the quantum kernel computes in section 17.

## Try it yourself

```bash
python labs/L11_reversible_entanglement/lab.py
```

The lab builds the in-place XOR circuit above, verifies the ancilla is
restored, shows that $H$ before $X$ is what makes "different bases" give
random answers, and introduces multi-qubit systems and entanglement.

## Self-check

- [ ] Can you explain why a classical function computed by a quantum
      circuit must preserve its input?
- [ ] Do you know the one-line proof idea for no-cloning?
- [ ] Can you list which of measurement, reset, X, CNOT and H are
      reversible?
- [ ] Have you run `python labs/L11_reversible_entanglement/lab.py`?

## Where to go next

Section 9 — [Multi-Qubit Systems](09-multi-qubit.md). One qubit is
understood; now build the tensor products.
