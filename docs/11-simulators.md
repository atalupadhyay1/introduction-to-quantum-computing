# Section 11 — Superposition and Entanglement with Quantum Simulators

> **Course section** 11 of 17 · **Lab** [`L12`](../labs/L12_simulators/lab.py) · **Quiz** 5 questions

## What you should be able to do

- Run a classical photon simulator and a quantum one side by side.
- Explain the difference between the two on the same experiment.
- Simulate a pair of entangled photons and predict the joint statistics.
- Cross-check an independent simulator against the qubit model.

## The course ships three Java simulators

The course's "Download the Simulator Code" article points at a ZIP with
three programs:

| Program | What it does |
|---|---|
| `ClassicalPhoton` | a classical wave through polarizers, with intensity arithmetic |
| `PhotonPolarizationMeasurement` | a single photon, with random outcomes |
| `EntangledPhotonMeasurement` | a pair of entangled photons, joint statistics |

They are written in Java. This repository ships **Python ports** in lab
L12, so you can run them without a JVM, and then cross-check them against
the qubit model built earlier in the course.

## The classical photon

The classical simulator keeps the *intensity* in each polarization
direction. Malus's law is applied as

$$
P_{\text{align}} = \cos^2(\theta_f - \theta_p)
$$

and the "aligned" state sets $\theta_p \leftarrow \theta_f$, while the
"anti-aligned" state sets $\theta_p \leftarrow \theta_f + 90°$.

## The quantum photon

The quantum simulator picks a *single* outcome at random, with probabilities
given by the squared overlaps. The difference is visible in the cascade:

| | classical | quantum |
|---|---|---|
| conditional probability of each stage | $[0.5, 1.0, 0.5]$ | $[0.5, 1.0, 0.5]$ |
| cumulative probability | $[0.5, 0.5, 0.25]$ | $[0.5, 0.5, 0.25]$ |

The *numbers* agree — Malus's law is Malus's law. What differs is the
mechanism: the classical simulator splits the intensity and the quantum one
collapses.

## The entangled pair

The entangled simulator keeps the four joint probabilities
$(p_{00}, p_{01}, p_{10}, p_{11})$. After a local rotation of the basis by
$\theta$ the outcome probability is the squared inner product with the
rotated basis state.

The prediction is the one you already know:

- measured in the **same** basis: only $00$ and $11$ occur, each with
  probability $\tfrac12$;
- measured in **different** bases: the four outcomes each occur with
  probability $\tfrac14$ — the correlation is gone.

The second line is the security of quantum key distribution in one
sentence: a useful correlation needs a common basis, and the basis is what
an eavesdropper has to guess.

## Cross-checking the models

Lab L12 runs the qubit model and the photon simulator on the *same*
experiment and compares the numbers. This is the most valuable habit in the
course: two independently written models agreeing is real evidence, where
one model agreeing with itself is not.

## Try it yourself

```bash
python labs/L12_simulators/lab.py
```

## Self-check

- [ ] Can you state the difference between the classical and the quantum
      photon simulator in one sentence?
- [ ] Can you predict the joint outcomes of an entangled pair measured in
      two different bases?
- [ ] Do you know why measuring in different bases destroys the
      correlation?
- [ ] Have you run `python labs/L12_simulators/lab.py` and seen the two
      models agree?

## Where to go next

Section 12 — [The Quantum Computing Model](12-quantum-computing-model.md).
Now put the physics into a programming model.
