# Glossary

| Term | Meaning |
|---|---|
| **Amplitude** | A complex number whose *squared modulus* is a probability. |
| **Adjoint** ($A^\dagger$) | The conjugate transpose, $(A^*)^T$. |
| **Bell state** | A maximally entangled two-qubit state; there are four. |
| **Bit string** | A sequence of classical bits; the outcome of a measurement. |
| **Born rule** | $P = \lvert\text{amplitude}\rvert^2$. |
| **Bra / ket** | $\langle\psi\rvert$ is the adjoint of $\lvert\psi\rangle$. |
| **Calibration** | The measured error rates of a real quantum device. |
| **Collapse** | The irreversible projection of a state onto a measurement eigenstate. |
| **Complex number** | $a + bi$, with $i^2 = -1$. |
| **Conjugate** | $\bar z = a - bi$ for $z = a+bi$. |
| **Controlled NOT (CNOT)** | Flips the target qubit iff the control is $\lvert1\rangle$. |
| **Density matrix** | $\rho = \lvert\psi\rangle\langle\psi\rvert$; for a mixed state it is a sum over an ensemble. |
| **Dirac notation** | $\lvert\psi\rangle$, $\langle\psi\rvert$, $\langle\phi\lvert\psi\rangle$. |
| **Entanglement** | A state that cannot be written as a product of single-system states. |
| **Entanglement entropy** | $S = -\sum\lambda_i\log_2\lambda_i$ of a reduced state. |
| **Eve** | The eavesdropper in a key-distribution protocol. |
| **Feature map** | The circuit that turns data $\lvert0\rangle^n$ into a state $\lvert\phi(x)\rangle$. |
| **Fidelity** | $|\langle\phi(x)\mid\phi(z)\rangle|^2$; the quantum kernel. |
| **GHZ state** | $(\lvert0\ldots0\rangle + \lvert1\ldots1\rangle)/\sqrt2$. |
| **Hadamard ($H$)** | The gate that creates a uniform superposition; $H^2 = I$. |
| **Interference** | Amplitudes adding or cancelling; the engine of quantum algorithms. |
| **Irreversible** | Cannot be undone: measurement and reset. |
| **Kernel** | $K(x,z)$; the similarity function a kernel machine uses. |
| **Kronecker product** | $\otimes$; builds joint states and operators. |
| **Malus's law** | $P(\text{pass}) = \cos^2(\theta_p - \theta_f)$. |
| **Mixed state** | A statistical mixture of pure states; needs a density matrix. |
| **No-cloning theorem** | An unknown quantum state cannot be copied exactly. |
| **Pauli gates** | $X$, $Y$, $Z$ — the single-qubit gates that flip a bit or a phase. |
| **Phase gate** | $S$ ($\pi/2$ rotation) and $T$ ($\pi/4$ rotation) about $z$. |
| **Product state** | $\lvert\alpha\rangle\otimes\lvert\beta\rangle$; not entangled. |
| **Pure state** | A single ket; needs a state vector. |
| **QBER** | Quantum bit error rate: the fraction of wrong sifted bits. |
| **Qubit** | A two-level quantum system: $\lvert\psi\rangle = \alpha\lvert0\rangle + \beta\lvert1\rangle$. |
| **Reversible** | Has an inverse; every unitary gate does. |
| **Sifting** | Discarding the BB84 rounds where the bases differed. |
| **State vector** | The column vector of amplitudes. |
| **Superposition** | A linear combination of basis states. |
| **SVM** | Support vector machine: finds the maximum-margin boundary. |
| **Tensor product** | See Kronecker product. |
| **Toffoli (CCNOT)** | Flips the target iff *both* controls are $\lvert1\rangle$. |
| **Transpile** | Turning a circuit into one the target device can run. |
| **Unitary** | $A^\dagger A = I$; the condition for reversibility. |
| **Von Neumann entropy** | $S = -\sum \lambda_i \log_2 \lambda_i$. |
| **Z-basis** | The computational basis $\lvert0\rangle, \lvert1\rangle$. |
| **X-basis** | The diagonal basis $\lvert+\rangle, \lvert-\rangle$. |
