# Section 10 — Entanglement

> **Course section** 10 of 17 · **Lab** [`L11`](../labs/L11_reversible_entanglement/lab.py) · **Quiz** 6 questions

## What you should be able to do

- Define entanglement, and distinguish a product state from an entangled one.
- Write the four Bell states and identify them.
- Compute the reduced density matrix and the entanglement entropy.
- State the CHSH inequality and what quantum correlations do to it.

## Product states versus entangled states

A two-qubit state is a **product state** if it factorizes:

$$
\lvert\psi\rangle = \lvert\alpha\rangle \otimes \lvert\beta\rangle
$$

Everything else is entangled. The canonical example is the Bell state

$$
\lvert\Phi^+\rangle = \frac{1}{\sqrt2}\bigl(\lvert00\rangle + \lvert11\rangle\bigr)
$$

which cannot be written in the product form at all.

## The four Bell states

$$
\begin{aligned}
\lvert\Phi^+\rangle &= \tfrac{1}{\sqrt2}(\lvert00\rangle + \lvert11\rangle)\\
\lvert\Phi^-\rangle &= \tfrac{1}{\sqrt2}(\lvert00\rangle - \lvert11\rangle)\\
\lvert\Psi^+\rangle &= \tfrac{1}{\sqrt2}(\lvert01\rangle + \lvert10\rangle)\\
\lvert\Psi^-\rangle &= \tfrac{1}{\sqrt2}(\lvert01\rangle - \lvert10\rangle)
\end{aligned}
$$

The first two differ in the relative phase of $|00\rangle$ and $|11\rangle$;
the last two in the relative phase of $|01\rangle$ and $|10\rangle$. The
phase difference is *not* observable in the computational basis — you need
the $X$ basis to see it.

## Measuring one qubit is enough

Measure $|\Phi^+\rangle$ in the computational basis. You get $00$ or $11$
with equal probability — never $01$ or $10$. If the first qubit is
measured, the second is *instantly* determined.

But the second qubit's outcome, on its own, is completely random. That is
why entanglement cannot be used to send information faster than light: Bob
sees a random bit, and only the *joint* statistics reveal the correlation.

## Reduced states and entropy

To measure the entanglement, trace one qubit out:

$$
\rho_A = \operatorname{Tr}_B \bigl(\lvert\psi\rangle\langle\psi\rvert\bigr)
$$

For the Bell state this gives $\rho_A = \tfrac12 I$ — the maximally mixed
state. Its eigenvalues are $\tfrac12, \tfrac12$, so the **entanglement
entropy** (the von Neumann entropy of the reduced state) is

$$
S = -\sum_i \lambda_i \log_2 \lambda_i = -2 \cdot \tfrac12 \log_2 \tfrac12
= 1 \text{ bit}
$$

Worked examples:

| state | entropy |
|---|---|
| $\lvert+\rangle \otimes \lvert+\rangle$ (product) | 0 bits |
| a Bell pair | 1 bit |
| GHZ on $n$ qubits, any balanced cut | 1 bit |
| a maximally entangled $n$-qubit state | $n/2$ bits |
| **two crossed Bell pairs**, $(q_0,q_2)$ and $(q_1,q_3)$ | **2 bits** |

That last row is the interesting one. Two *parallel* Bell pairs (say
$q_0q_1$ and $q_2q_3$) give only 1 bit across the $2|2$ cut, because each
pair can be traced out separately. But two *crossed* Bell pairs have a
$2|2$ cut whose reduced state has two eigenvalues of $\tfrac12$ each, so
the entropy is 2 bits.

> The entropy is computed from the **eigenvalues** of the reduced state, not
> from its diagonal. The lab checks this explicitly.

## CHSH and Bell's theorem

With two parties sharing a pair and each choosing a measurement setting
$\{a_0, a_1\}$ and $\{b_0, b_1\}$, define the correlation coefficients
$E_{xy} = P(\text{same outcome}) - P(\text{different outcome})$. The CHSH
parameter is

$$
S = E_{00} + E_{01} + E_{10} - E_{11}
$$

- **Classical (local hidden variable) theories:** $S \le 2$;
- **Quantum mechanics:** $S \le 2\sqrt2 \approx 2.83$.

Experiments close to the quantum bound rule out local hidden-variable
theories — which is the deepest practical payoff of entanglement.

## Try it yourself

```bash
python labs/L11_reversible_entanglement/lab.py
```

The lab creates Bell and GHZ states, computes their entanglement entropy
from the reduced-state eigenvalues, checks the crossed-Bell-pair case
gives 2 bits, and verifies that the CHSH-style correlation is stronger than
the classical bound.

## Self-check

- [ ] Can you write all four Bell states from memory?
- [ ] Can you explain why the Bell state cannot be written as a product?
- [ ] Do you know that the entropy comes from the reduced state's
      *eigenvalues*?
- [ ] Can you say what the CHSH bound is for classical theories and what
      quantum mechanics reaches?
- [ ] Have you run `python labs/L11_reversible_entanglement/lab.py`?

## Where to go next

Section 11 — [Superposition and Entanglement Simulators](11-simulators.md).
Build the simulators the course ships with, in Python.
