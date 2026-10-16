# Section 9 — Multi-Qubit Systems

> **Course section** 9 of 17 · **Lab** [`L11`](../labs/L11_reversible_entanglement/lab.py) · **Quiz** 6 questions

## What you should be able to do

- Build the $2^n$-dimensional basis of an $n$-qubit system.
- Use the Kronecker product to combine single-qubit states and operators.
- Read a multi-qubit bitstring in the right order (and spot the trap).
- Apply CNOT, SWAP, CSWAP and Toffoli by hand.

## The state space grows exponentially

$n$ qubits have $2^n$ basis states:

| qubits | basis states | state vector length |
|---|---|---|
| 1 | 2 | 2 |
| 2 | 4 | 4 |
| 3 | 8 | 8 |
| 10 | 1024 | 1024 |
| 50 | $1.1 \times 10^{15}$ | $1.1 \times 10^{15}$ |

A 50-qubit state vector is 16 MB — fine. A 1000-qubit one is 16 TB —
hopeless. This is the trade-off the course keeps returning to: a
simulator needs memory proportional to $2^n$, a real device needs gates
proportional to the circuit depth.

## Tensor products

To build the joint state of two systems, take the Kronecker product:

$$
\lvert\psi\rangle \otimes \lvert\phi\rangle
$$

With the standard convention that $q_0$ is the **leftmost** qubit, the index
of a basis state is

$$
\text{index} = b_0 2^{n-1} + b_1 2^{n-2} + \cdots + b_{n-1} 2^{0}
$$

so $|0\rangle \otimes |1\rangle$ is the *second* column of the 4×4
identity:

$$
|0\rangle \otimes |1\rangle =
\begin{pmatrix} 0 \\ 1 \\ 0 \\ 0 \end{pmatrix}
$$

**Order matters.** $|0\rangle \otimes |1\rangle \ne |1\rangle \otimes
|0\rangle$: they are different basis states of the same space. And the
ordering of qubits inside the tensor product is a *convention* — which is
precisely where the Q# and Qiskit ordering traps in sections 13 and 15 come
from.

## Two-qubit gates

| Gate | Action |
|---|---|
| CNOT | flip the target iff the control is $\lvert1\rangle$ |
| CZ | flip the phase of the target iff the control is $\lvert1\rangle$ |
| SWAP | exchange the two qubits |
| CSWAP (Fredkin) | swap the two targets iff the control is $\lvert1\rangle$ |
| Toffoli (CCNOT) | flip the target iff **both** controls are $\lvert1\rangle$ |

The CNOT is the workhorse. The SWAP can be built from three CNOTs, and the
CSWAP from two CNOTs and one Toffoli. The Toffoli is genuinely
three-qubit: it cannot be built from two-qubit gates alone.

## Writing a bitstring

You must be explicit about the convention. In this repository, and in most
textbooks, the state vector is written **left to right** in the order
$q_0, q_1, \dots$, so index 5 of a 3-qubit register is the bitstring
`101` meaning $q_0 = 1, q_1 = 0, q_2 = 1$.

Qiskit, by contrast, stores qubit 0 as the **least significant** bit, so
its `get_counts()` prints bitstrings most-significant-qubit first. Q#
prints `(q2, q1, q0)`. All three are the *same* physics with a different
bookkeeping convention, and confusing them is the single most common
source of "wrong but plausible" answers in the course.

## Try it yourself

```bash
python labs/L11_reversible_entanglement/lab.py
```

## Self-check

- [ ] Can you write out the four basis states of a 2-qubit system?
- [ ] Can you compute $|0\rangle \otimes |1\rangle$ as a column vector and
      explain the index convention you used?
- [ ] Do you know how many Toffoli gates you need to swap two qubits, and
      why a Toffoli cannot be made from two-qubit gates?
- [ ] Can you state the difference between "the state vector is written
      $q_0$ first" and "Qiskit's counts are printed $q_{n-1}$ first"?

## Where to go next

Section 10 — [Entanglement](10-entanglement.md). The most famous property
of quantum mechanics, and the one that makes quantum information different.
