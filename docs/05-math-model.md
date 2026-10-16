# Section 5 — Developing a Math Model for Quantum Physics

> **Course section** 5 of 17 · **Lab** [`L08`](../labs/L08_math_model/lab.py) · **Quiz** 6 questions

## What you should be able to do

- Write a pure qubit state, normalize it, and read probabilities off it.
- State the Born rule and the normalization condition.
- Explain what a "probability subtraction" trick is and why it is useful.
- Distinguish deterministic from probabilistic operations, and evolution
  from collapse.

## From physics to a model

Von Neumann's model of a measurement has two stages:

1. **Evolution** — a deterministic, reversible, unitary transformation
   (Schrödinger evolution).
2. **Collapse** — a non-unitary projection onto an eigenstate of the
   measurement operator.

The course's "Subtractive Probabilities Through Complex Numbers" and
"Modeling Superposition Through Matrices" articles are the two halves of
this: the first shows how to *get* a probability, the second shows how
superposition is *represented*.

## The state

A pure qubit state is

$$
|\psi\rangle = \alpha |0\rangle + \beta |1\rangle, \qquad
|\alpha|^2 + |\beta|^2 = 1
$$

with the probabilities given by the **Born rule**:

$$
P(0) = |\alpha|^2, \qquad P(1) = |\beta|^2
$$

Written as a column vector:

$$
|\psi\rangle = \begin{pmatrix} \alpha \\ \beta \end{pmatrix}
$$

## Subtracting probabilities

Here is the trick the course builds on. Suppose you want the probability of
"outcome 0" for a state $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$:

$$
P(0) = |\langle 0 | \psi\rangle|^2
$$

The **subtractive** method works backwards from the total. Since the two
outcomes are the only ones available and the state is normalized,

$$
P(0) = 1 - P(1)
$$

and $P(1)$ is obtained by projecting the state onto $|1\rangle$ and taking
the squared modulus. In code this is a single matrix-vector product, and
the reason the course insists on the algebra is that the same projection
gives you the *post-measurement* state for free.

## Superposition through matrices

Every gate is a $2\times2$ complex matrix acting on the column vector:

$$
|\psi'\rangle = U |\psi\rangle
$$

and the states reachable from $|0\rangle$ are exactly the columns of $U$.
If the columns of $U$ are $|u_0\rangle$ and $|u_1\rangle$ then

$$
U = \begin{pmatrix} u_{00} & u_{10} \\ u_{01} & u_{11} \end{pmatrix}
$$

— the first *column* is the image of $|0\rangle$ and the second is the image
of $|1\rangle$. Getting this orientation backwards is the single most
common bug in a first quantum program, and lab L08 checks it explicitly.

## Deterministic versus probabilistic

| | Deterministic | Probabilistic |
|---|---|---|
| Example | X gate, Z gate | Measurement |
| Reversible? | yes | no |
| Input $\to$ output | one to one | many to one |
| Physics | unitary evolution | collapse |

The whole point of the model is that **only measurement is
irreversible**. Everything else in a quantum program can be undone.

## Try it yourself

```bash
python labs/L08_math_model/lab.py
```

The lab builds the math model from scratch, checks that the columns of a
gate matrix are the images of the basis states, and compares the
"subtractive probability" method against direct projection.

## Self-check

- [ ] Can you write down a normalized state and read two probabilities off
      it?
- [ ] Can you explain the subtractive method in your own words?
- [ ] Do you know which column of a gate matrix is the image of $|0\rangle$?
- [ ] Have you run `python labs/L08_math_model/lab.py`?

## Where to go next

Section 6 — [Quantum Physics of Spin States](06-spin-states.md). The
photons were a warm-up; spin gives you a second, very physical route to the
same mathematics.
