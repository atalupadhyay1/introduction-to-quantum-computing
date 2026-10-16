# Section 3 — Math Foundation

> **Course section** 3 of 17 · **Labs** [`L03`](../labs/L03_boolean_logic/lab.py) [`L04`](../labs/L04_probability_statistics/lab.py) [`L05`](../labs/L05_complex_numbers/lab.py) [`L06`](../labs/L06_linear_algebra/lab.py) · **Quiz** 7 questions

## What you should be able to do

- Manipulate complex numbers: add, multiply, divide, conjugate, modulus.
- Apply the rules of probability: addition, multiplication, conditional
  probability, independence.
- Read and write Boolean logic, and convert between truth tables,
  expressions and logic gates.
- Do the linear algebra quantum computing actually needs: matrix-vector
  products, adjoints, inverses, eigenvalues, and the Kronecker product.

## Why this section exists

The course's own "Course Article" on *Quantum Computing Through Math* says
it plainly: a quantum circuit is a complex matrix acting on a complex
vector, and the result is a probability distribution. You cannot read a
quantum program without this mathematics.

## Complex numbers

$i$ is the square root of $-1$, so $i^2 = -1$. Every complex number is
$z = a + bi$ with $a, b \in \mathbb{R}$.

| Operation | Formula |
|---|---|
| Conjugate | $\bar z = a - bi$ |
| Modulus | $\lvert z\rvert = \sqrt{a^2 + b^2}$ |
| Modulus squared | $\lvert z\rvert^2 = z \bar z = a^2 + b^2$ |
| Polar form | $z = r e^{i\theta}$, $r = \lvert z\rvert$ |
| Division | $\dfrac{a+bi}{c+di} = \dfrac{(a+bi)(c-di)}{c^2 + d^2}$ |

Worked example:

$$
\frac{3 + 4i}{7 - 6i} = \frac{(3+4i)(7+6i)}{49 + 36}
= \frac{21 + 18i + 28i + 24i^2}{85}
= \frac{-3 + 46i}{85}
$$

so $\operatorname{Re} = -3/85 \approx -0.0353$ and $\operatorname{Im} =
46/85 \approx 0.5412$.

> **Python trap.** `(3+4j)/(7-6j).real` parses as
> `(3+4j)/((7-6j).real)` — a float divided by a complex. Always write
> `((3+4j)/(7-6j)).real`.

## Probability

| Rule | Formula |
|---|---|
| Addition | $P(A \cup B) = P(A) + P(B) - P(A \cap B)$ |
| Multiplication (independent) | $P(A \cap B) = P(A) P(B)$ |
| Conditional | $P(A \mid B) = P(A \cap B) / P(B)$ |
| Complement | $P(A^c) = 1 - P(A)$ |
| Mutually exclusive | $P(A \cap B) = 0$ |

Expectation and variance of a discrete random variable:

$$
\mu = \sum_i x_i p_i, \qquad
\sigma^2 = \sum_i (x_i - \mu)^2 p_i
$$

and the covariance of two variables is $\operatorname{Cov}(X,Y) =
E[XY] - \mu_X \mu_Y$. The correlation coefficient divides that by
$\sigma_X \sigma_Y$.

## Boolean logic

AND, OR and NOT are the three classical gates; NAND and NOR are universal,
and XOR is the one quantum computing cares about most (it is the
self-inverse "controlled NOT" when you attach a control).

| $a$ | $b$ | AND | OR | XOR |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 |
| 0 | 1 | 0 | 1 | 1 |
| 1 | 0 | 0 | 1 | 1 |
| 1 | 1 | 1 | 1 | 0 |

De Morgan's laws, which you will use constantly when reasoning about
circuits:

$$
\overline{A \land B} = \bar A \lor \bar B, \qquad
\overline{A \lor B} = \bar A \land \bar B
$$

## Linear algebra

This is the part that matters most. A qubit state is a column vector of
complex amplitudes; a gate is a matrix.

**Matrix-vector product** is row-by-column:

$$
(A v)_i = \sum_j A_{ij} v_j
$$

**Adjoint (conjugate transpose)** $A^\dagger = (A^*)^T$:

- $A$ is **unitary** if $A^\dagger A = I$ — this is what makes a gate
  reversible;
- $A$ is **Hermitian** if $A^\dagger = A$ — this is what makes an
  observable have real eigenvalues.

**Eigenvalues.** If $A v = \lambda v$ then $v$ is an eigenvector and
$\lambda$ an eigenvalue. The course's "Computing Eigen Values" article
describes the trick: multiply a matrix by an eigenvector, factor out the
eigenvalue, and the remaining equation is the eigenvector's own system.

**The Kronecker product** builds multi-qubit states. If $A$ is $m\times m$
and $B$ is $n\times n$ then $A \otimes B$ is $mn \times mn$ and its index
runs as $i\cdot n + k$:

$$
|0\rangle \otimes |1\rangle =
\begin{pmatrix} 0 \\ 1 \\ 0 \\ 0 \end{pmatrix}
$$

## Try it yourself

```bash
python labs/L03_boolean_logic/lab.py
python labs/L04_probability_statistics/lab.py
python labs/L05_complex_numbers/lab.py
python labs/L06_linear_algebra/lab.py
```

Lab L06 is the biggest of the four (47 checks) and covers everything from
matrix multiplication to the power method for finding dominant eigenvalues.

## Self-check

- [ ] Can you divide two complex numbers and simplify the result by hand?
- [ ] Do you know when $P(A \cap B) = P(A)P(B)$ is valid, and what to do
      when it is not?
- [ ] Can you write the truth table for XOR and explain why it is
      self-inverse?
- [ ] Can you compute $A^\dagger$ for a 2×2 complex matrix?
- [ ] Do you know what "unitary" guarantees and why it matters?

## Where to go next

Section 4 — [Quantum Cryptography](04-quantum-cryptography.md). The
mathematics is in place; now use it to do something practical.
