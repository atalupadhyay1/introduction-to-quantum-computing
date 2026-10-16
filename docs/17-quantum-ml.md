# Section 17 — Quantum Machine Learning with Qiskit

> **Course section** 17 of 17 · **Lab** [`L17`](../labs/L17_quantum_machine_learning/lab.py) · **Quiz** 7 questions

## What you should be able to do

- Run the classical KNN and the quantum KNN side by side, and show they
  agree.
- Explain the quantum KNN mathematically: why the interference amplitude is
  the square root of four times the classical weight.
- Explain support vector machines, soft margins, the kernel trick and
  one-vs-rest.
- Train a quantum support vector machine on the iris dataset.

## The lectures

| Lecture | What it covers |
|---|---|
| KNN Problem Description | the task: two training points, one query |
| Code for Classical KNN | the algorithm in Python |
| Code for Quantum KNN | the circuit |
| Math for Classical KNN | normalisation, distance, weights |
| Math Prerequisites for Quantum KNN | amplitude encoding and interference |
| Math for Quantum KNN | the quantum KNN worked out |
| Connecting Math and Code (classical) | the two agree |
| Connecting Math and Code (quantum) | the two agree |
| Introduction to Classification | decision boundaries |
| SVMs: Separation | the maximum-margin hyperplane |
| SVMs: Overfitting | one rogue point ruins the boundary |
| SVMs: Soft Margins | the hinge loss and the C parameter |
| SVMs: Higher Dimensions and Kernels | the kernel trick |
| SVMs: Multiple Classes | one-vs-rest and one-vs-one |
| Quantum Support Vector Machines | the ZZ feature map and QSVC |
| Significance of Quantum ML | the honest summary |

## The classical KNN

Normalise the vectors, compute the squared Euclidean distance, turn each
distance into a weight, and normalise the weights into probabilities:

$$
w_i = 1 - 0.25\, d_i^2, \qquad
P(c \mid x) = \frac{\sum_{i \in c} w_i}{\sum_i w_i}
$$

On the course's data this gives $P(1) = 0.5244$ and $P(0) = 0.4756$.

## The quantum KNN, and why it works

The circuit encodes the training vectors and the query as *amplitudes*, and
a Hadamard on a "training vs query" qubit makes the two halves interfere.
At a slot holding a training component $v_i$ and the query component $q_i$,
the amplitude in the training half becomes

$$
\frac{v_i + q_i}{2\sqrt2}
$$

and now the identity that makes the whole thing work:

$$
\begin{aligned}
\sum_i (v_i + q_i)^2 &= \sum_i \bigl(v_i^2 + q_i^2 + 2 v_i q_i\bigr)
= 2 + 2\sum_i v_i q_i\\
\text{and}\quad w &= 1 - 0.25\,d^2 = 1 - 0.25\bigl(2 - 2\sum_i v_i q_i\bigr)
= 0.5\bigl(1 + \sum_i v_i q_i\bigr)
\end{aligned}
$$

so

$$
\sum_i (v_i + q_i)^2 = 4\,w
$$

**The interference amplitude is the square root of four times the classical
weight.** Because the probabilities in each class sum to the same total
denominator, the *conditional* probability of measuring a class is exactly
the classical normalised weight.

The lab confirms this three ways: 20 000 shots give $P(1) = 0.5248$
against the classical $0.5244$, and the exact statevector answer agrees to
machine precision.

## Support vector machines

An SVM finds the **widest empty strip** between two classes. The boundary
sits between two hyperplanes $w \cdot x + b = \pm 1$, the margin is
$2/\lVert w\rVert$, and only the points touching the hyperplanes — the
*support vectors* — constrain the solution.

- **Overfitting:** one mislabelled point far out on the wrong side drags
  the whole boundary with it. The lab shows a clean dataset separated
  perfectly and a spoiled one that is not.
- **Soft margins:** allow violations and charge for them,
  $\min \tfrac12\lVert w\rVert^2 + C\sum_i \text{slack}_i$. Big $C$ means
  few mistakes and a weird boundary; small $C$ means mistakes are cheap and
  the boundary stays smooth.
- **Kernels:** $K(x,z) = \phi(x)\cdot\phi(z)$ lets you use a linear SVM in
  a high-dimensional feature space without ever building $\phi$. The
  polynomial kernel $(x \cdot z + c)^d$ is the standard example — and on
  the rings dataset, the linear kernel scores 0.50 while the polynomial
  kernel scores 0.96.
- **Multiple classes:** one-vs-rest (one binary SVM per class) or
  one-vs-one (one per pair).

## Quantum support vector machines

The quantum kernel is

$$
K(x, z) = \bigl|\langle \phi(x) \mid \phi(z)\rangle\bigr|^2
$$

with $\lvert\phi(x)\rangle = U(x)\lvert0\rangle^n$. The course uses the
**ZZ feature map** with 4 features, 2 repetitions and linear entanglement.
The lab computes a kernel entry directly from the state vectors, then
trains a real `QSVC` on the iris dataset and reproduces the course's
predictions: `[5.0, 3.3, 1.5, 0.3] → 0` and `[6.0, 2.9, 5.2, 1.7] → 2`.

The course's original `qsvm.py` used `BasicAer`, `QuantumInstance` and
`algorithm_globals`, all removed in Qiskit 1.0. The modern equivalents are
`FidelityQuantumKernel` with a `QMLSampler`, and `QSVC(quantum_kernel=...)`.

## The significance — honestly

| Claim | Reality |
|---|---|
| "a quantum computer learns faster" | not shown; data loading usually dominates |
| "the quantum kernel is exponentially rich" | true in principle, hard to exploit |
| "you can read out the whole feature map" | no — you read out an expectation value |
| "it is a drop-in replacement" | yes: the kernel is the interface |

1. Quantum machine learning is **not** a speed-up for everything. It is a
   new way to compute a similarity.
2. The useful part is the **kernel**: a quantum circuit can evaluate a
   function of two data points that is awkward to write down classically.
3. Everything else — the loss, the optimizer, the train/test split — stays
   classical, exactly as in section 16.
4. The real obstacle is **hardware**: today's devices are noisy, and a deep
   feature map needs a lot of error correction before it beats a classical
   kernel machine.

## Try it yourself

```bash
python labs/L17_quantum_machine_learning/lab.py
```

## Self-check

- [ ] Can you derive $\sum_i (v_i + q_i)^2 = 4w$ from the definitions?
- [ ] Can you explain what the Hadamard on the "training vs query" qubit
      does, in terms of sum and difference?
- [ ] Do you know what the margin of an SVM is, and what $C$ controls?
- [ ] Can you write the quantum kernel and explain what the feature map
      does?
- [ ] Have you run `python labs/L17_quantum_machine_learning/lab.py` and
      seen the quantum KNN match the classical one?

## Where to go next

You have reached the end of the course. Two good next steps:

- run `python tools/quiz.py` and `python tools/progress.py` to see where you
  stand;
- read the [appendix](appendix/appendix.md) for the formula sheet, the
  glossary and the API reference for the shared library.
