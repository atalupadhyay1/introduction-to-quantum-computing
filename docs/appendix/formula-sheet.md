# Formula sheet

Every equation the course uses, on one page.

## Complex numbers

| | |
|---|---|
| Definition | $i^2 = -1$, $z = a + bi$ |
| Conjugate | $\bar z = a - bi$ |
| Modulus | $\lvert z\rvert = \sqrt{a^2+b^2}$ |
| Modulus squared | $\lvert z\rvert^2 = z\bar z = a^2 + b^2$ |
| Polar form | $z = re^{i\theta}$, $r = \lvert z\rvert$ |
| Multiplication | $(a+bi)(c+di) = (ac-bd) + (ad+bc)i$ |
| Division | $\dfrac{a+bi}{c+di} = \dfrac{(a+bi)(c-di)}{c^2+d^2}$ |
| Euler | $e^{i\theta} = \cos\theta + i\sin\theta$ |

## Probability

| | |
|---|---|
| Addition | $P(A\cup B) = P(A)+P(B)-P(A\cap B)$ |
| Multiplication (independent) | $P(A\cap B) = P(A)P(B)$ |
| Conditional | $P(A\mid B) = P(A\cap B)/P(B)$ |
| Complement | $P(A^c) = 1-P(A)$ |
| Mutually exclusive | $P(A\cap B) = 0$ |
| Total probability | $P(B) = \sum_i P(B\mid A_i)P(A_i)$ |
| Bayes | $P(A\mid B) = \dfrac{P(B\mid A)P(A)}{\sum_i P(B\mid A_i)P(A_i)}$ |

## Statistics

| | |
|---|---|
| Expectation | $\mu = \sum_i x_i p_i$ |
| Variance | $\sigma^2 = \sum_i (x_i-\mu)^2 p_i$ |
| Standard deviation | $\sigma = \sqrt{\sigma^2}$ |
| Covariance | $\operatorname{Cov}(X,Y) = E[XY] - \mu_X\mu_Y$ |
| Correlation | $\rho = \operatorname{Cov}(X,Y)/(\sigma_X\sigma_Y)$ |

## Linear algebra

| | |
|---|---|
| Adjoint | $A^\dagger = (A^*)^T$ |
| Unitary | $A^\dagger A = I$ |
| Hermitian | $A^\dagger = A$ |
| Inner product | $\langle a \mid b\rangle = a^\dagger b$ |
| Outer product | $\lvert a\rangle\langle b\rvert = ab^\dagger$ |
| Eigenpair | $Av = \lambda v$ |
| Trace | $\operatorname{tr}(A) = \sum_i A_{ii}$ |
| Determinant | $\det(A)$ |
| Kronecker index | $i \cdot \text{rows}(B) + k$ |
| Trace trick | $\operatorname{tr}(AB) = \sum_i \lambda_i(A)\lambda_i(B)$ |

## Qubits and states

| | |
|---|---|
| State | $\lvert\psi\rangle = \alpha\lvert0\rangle + \beta\lvert1\rangle$ |
| Normalization | $\lvert\alpha\rvert^2 + \lvert\beta\rvert^2 = 1$ |
| Born rule | $P(0) = \lvert\alpha\rvert^2$, $P(1) = \lvert\beta\rvert^2$ |
| Projection | $P(0) = \lvert\langle 0\mid\psi\rangle\rvert^2$ |
| Subtractive | $P(0) = 1 - P(1)$ |
| Inner product of a state with itself | $\langle\psi\mid\psi\rangle = 1$ |
| Bloch angles | $\alpha = \cos\frac\theta2$, $\beta = e^{i\phi}\sin\frac\theta2$ |
| Bloch $z$ | $z = P(0) - P(1)$ |

## Gates

$$
\begin{aligned}
H &= \frac{1}{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix}
& X &= \begin{pmatrix}0&1\\1&0\end{pmatrix}
& Y &= \begin{pmatrix}0&-i\\i&0\end{pmatrix}
& Z &= \begin{pmatrix}1&0\\0&-1\end{pmatrix}\\[4pt]
S &= \begin{pmatrix}1&0\\0&i\end{pmatrix}
& T &= \begin{pmatrix}1&0\\0&e^{i\pi/4}\end{pmatrix}
& \mathrm{CNOT} &= \begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&0&1\\0&0&1&0\end{pmatrix}
\end{aligned}
$$

| | |
|---|---|
| $H\lvert0\rangle$ | $\lvert+\rangle = (\lvert0\rangle+\lvert1\rangle)/\sqrt2$ |
| $H\lvert1\rangle$ | $\lvert-\rangle = (\lvert0\rangle-\lvert1\rangle)/\sqrt2$ |
| $S$ | phase gate; $S^2 = Z$, $S^4 = I$ |
| $T$ | $\pi/8$ gate; $T^2 = S$, $T^4 = Z$ |
| Toffoli in 2-qubit gates | 6 |

## Optics

| | |
|---|---|
| Malus's law | $P(\text{pass}) = \cos^2(\theta_p - \theta_f)$ |
| Anti-aligned | $P(\text{pass}) = \sin^2(\Delta\theta)$ |
| 45° polarizer | $\lvert+\rangle$, $\lvert-\rangle$ |

## Entanglement

| | |
|---|---|
| Bell states | $\Phi^\pm = (\lvert00\rangle \pm \lvert11\rangle)/\sqrt2$, $\Psi^\pm = (\lvert01\rangle \pm \lvert10\rangle)/\sqrt2$ |
| Reduced state | $\rho_A = \operatorname{Tr}_B(\lvert\psi\rangle\langle\psi\rvert)$ |
| Entropy | $S = -\sum_i \lambda_i \log_2 \lambda_i$ |
| Bell pair | 1 bit |
| Maximally entangled $n$-qubit | $n/2$ bits |
| Crossed Bell pairs, $2\lvert2$ cut | 2 bits |
| CHSH | $S = E_{00}+E_{01}+E_{10}-E_{11}$ |
| CHSH bounds | classical $\le 2$, quantum $\le 2\sqrt2$ |

## Cryptography

| | |
|---|---|
| BB84 bases | rectilinear $Z$ (0°/90°), diagonal $X$ (45°/135°) |
| Ideal QBER, no eve | 0% |
| QBER, eve resends in the basis she measured in | 25% |
| QBER, eve resends in a random basis | 37.5% |
| One-way abort threshold | $\approx 11\%$ |
| One-time pad | $C = M \oplus K$, $M = C \oplus K$ |

## Machine learning

| | |
|---|---|
| Linear model | $\hat y = w\cdot x + b$ |
| Gradient step | $w \leftarrow w - \eta\,\partial L/\partial w$ |
| Sigmoid | $\sigma(z) = 1/(1+e^{-z})$ |
| Log-loss | $L = -\bigl[y\log p + (1-y)\log(1-p)\bigr]$ |
| Hinge loss | $\max(0, 1 - y(w\cdot x + b))$ |
| Soft-margin SVM | $\min \tfrac12\lVert w\rVert^2 + C\sum_i \text{slack}_i$ |
| Margin | $2/\lVert w\rVert$ |
| L2 penalty | $\tfrac{\lambda}{2}\lVert w\rVert^2$ |
| L1 penalty | $\lambda\lVert w\rVert_1$ |
| Accuracy | $(TP+TN)/(TP+TN+FP+FN)$ |
| Precision | $TP/(TP+FP)$ |
| Recall | $TP/(TP+FN)$ |
| $F_1$ | $2PR/(P+R)$ |
| KNN weight | $w_i = 1 - 0.25 d_i^2$ |
| Kernel trick | $K(x,z) = \phi(x)\cdot\phi(z)$ |
| Polynomial kernel | $K(x,z) = (x\cdot z + c)^d$ |
| Quantum kernel | $K(x,z) = \lvert\langle\phi(x)\mid\phi(z)\rangle\rvert^2$ |
| Quantum KNN identity | $\sum_i (v_i+q_i)^2 = 4w_i$ |

## Algorithms

| | |
|---|---|
| Shor | factor $N$ via the period $r$ of $a^x \bmod N$ |
| Period finding | Kitaev's order-finding circuit + inverse QFT |
| Peaks | multiples of $2^m/r$ |
| Factoring | $\gcd(a^{r/2}\pm 1, N)$ |
| QFT | $\lvert j\rangle \mapsto \frac{1}{\sqrt{2^m}}\sum_k e^{2\pi i jk/2^m}\lvert k\rangle$ |
| Grover | $\Theta(\sqrt{N})$ queries instead of $N$ |
