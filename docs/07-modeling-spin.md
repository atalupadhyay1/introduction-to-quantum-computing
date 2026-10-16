# Section 7 — Modeling Quantum Spin States with Math

> **Course section** 7 of 17 · **Lab** [`L10`](../labs/L10_dirac_notation/lab.py) · **Quiz** 6 questions

## What you should be able to do

- Write a spin state as a column vector and apply a gate to it.
- Use Dirac notation fluently: bras, kets, inner and outer products.
- Write and use the Hadamard, $X$, $Y$ and $Z$ gates.
- Read probabilities off a state vector with the Born rule.

## Column matrix representation

A pure spin state is a **column vector of complex amplitudes**:

$$
|\psi\rangle = \alpha|0\rangle + \beta|1\rangle
\quad\longleftrightarrow\quad
\begin{pmatrix}\alpha \\ \beta\end{pmatrix},
\qquad |\alpha|^2 + |\beta|^2 = 1
$$

A mixed state is a density matrix $\rho = |\psi\rangle\langle\psi|$, but
you do not need it until the course's later sections.

## Dirac notation

| Notation | Meaning |
|---|---|
| $\lvert\psi\rangle$ | ket — a state |
| $\langle\psi\rvert$ | bra — the *adjoint* of the ket |
| $\langle\phi\lvert\psi\rangle$ | inner product — a complex number |
| $\lvert\phi\rangle\langle\psi\rvert$ | outer product — an operator |
| $\langle\psi\lvert\psi\rangle$ | 1 for a normalized state |

The adjoint rule is the one to memorise: $\langle\psi| = \psi^\dagger$, and
for a column vector $\psi = (\psi_1, \psi_2)^T$ the bra is the *row* vector
$(\psi_1^*, \psi_2^*)$.

## The gates

$$
H = \frac{1}{\sqrt2}\begin{pmatrix} 1 & 1 \\ 1 & -1\end{pmatrix},
\qquad
X = \begin{pmatrix} 0 & 1 \\ 1 & 0\end{pmatrix},
\qquad
Y = \begin{pmatrix} 0 & -i \\ i & 0\end{pmatrix},
\qquad
Z = \begin{pmatrix} 1 & 0 \\ 0 & -1\end{pmatrix}
$$

plus the phase gates

$$
S = \begin{pmatrix} 1 & 0 \\ 0 & i\end{pmatrix},
\qquad
T = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\pi/4}\end{pmatrix}
$$

Each one does something specific to the Bloch sphere:

| Gate | Action |
|---|---|
| $X$ | rotate 180° about the $x$ axis (bit flip) |
| $Y$ | rotate 180° about the $y$ axis |
| $Z$ | rotate 180° about the $z$ axis (phase flip) |
| $H$ | rotate 90° about the axis $(\hat{x} + \hat{z})/\sqrt2$ |

Two facts worth checking yourself:

- $H|0\rangle = |+\rangle = (|0\rangle + |1\rangle)/\sqrt2$ and
  $H|1\rangle = |-\rangle = (|0\rangle - |1\rangle)/\sqrt2$;
- $H^2 = I$, so **$H$ is its own inverse**;
- $X$, $Y$ and $Z$ are Hermitian *and* unitary, so $X^2 = Y^2 = Z^2 = I$.

## The operator picture

The alternative to "apply a matrix to a vector" is the **operator
picture**: a gate is an operator that acts on a ket and produces a new ket,

$$
\hat{A}\lvert\psi\rangle = \lvert\psi'\rangle
$$

with matrix elements $\langle\phi|\hat{A}|\psi\rangle$ giving the
transition amplitudes. The two pictures are the same thing; the operator
picture just makes the symmetry arguments easier to see.

A useful identity: the adjoint of an operator reverses the order and
conjugates the bras and kets,

$$
\langle\psi|\hat{A}^\dagger|\phi\rangle = \langle\hat{A}\psi|\phi\rangle
$$

which is what lets you "undo" a gate by applying its adjoint.

## The Bloch sphere

Every pure qubit state is a point on the unit sphere. The map from
$(\theta, \phi)$ to amplitudes is

$$
\alpha = \cos\frac{\theta}{2}, \qquad \beta = e^{i\phi}\sin\frac{\theta}{2}
$$

so the $z$-coordinate of the sphere point is
$z = |\alpha|^2 - |\beta|^2 = P(0) - P(1)$, and the transverse projection
has length $2|\alpha||\beta| = 2\sqrt{P(0)P(1)}$. Measuring the state in
the computational basis gives $P(0) = (1 + z)/2$.

## Try it yourself

```bash
python labs/L10_dirac_notation/lab.py
```

The lab works in Dirac notation throughout: it applies gates, checks the
inner-product rules, verifies that every gate matrix is unitary, and shows
that $H$ maps $|0\rangle$ to $|+\rangle$ and back.

## Self-check

- [ ] Can you write $\langle\psi|$ given $\lvert\psi\rangle$?
- [ ] Can you compute $H|0\rangle$ and $H|1\rangle$ from the matrix?
- [ ] Do you know which of $H, X, Y, Z, S, T$ are their own inverses?
- [ ] Can you relate the Bloch-sphere $z$ coordinate to a measurement
      probability?
- [ ] Have you run `python labs/L10_dirac_notation/lab.py`?

## Where to go next

Section 8 — [Reversible and Irreversible State Transformations](08-reversible-irreversible.md).
Everything so far has been reversible. Now find out what changes when a
measurement enters.
