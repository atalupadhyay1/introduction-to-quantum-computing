# Section 2 — Quantum Physics Through Photon Polarization

> **Course section** 2 of 17 · **Lab** [`L02`](../labs/L02_photon_polarization/lab.py) · **Quiz** 6 questions

## What you should be able to do

- State Malus's law and use it.
- Explain why polarization behaves like a *two-state* system.
- Distinguish a classical wave superposition from a quantum one.
- Run a polarization cascade in code and predict the outcome before running it.

## Photons are the friendliest quantum system

A photon of light travelling in a fixed direction has exactly **two**
independent polarization states:

- **horizontal** (H)
- **vertical** (V)

That is all you need. A photon is the qubit of this section, with
$|0\rangle \equiv \mathrm{H}$ and $|1\rangle \equiv \mathrm{V}$.

## Malus's law

Send a photon polarized at angle $\theta_p$ into a polarizer whose
transmission axis is at angle $\theta_f$. The probability it passes is

$$
P(\text{pass}) = \cos^2(\theta_p - \theta_f)
$$

and the probability it is absorbed is

$$
P(\text{block}) = \sin^2(\theta_p - \theta_f)
$$

Two special cases are worth memorising:

| Setup | $P(\text{pass})$ |
|---|---|
| Same angle ($\theta_p = \theta_f$) | $1$ |
| 90° apart | $0$ |
| 45° apart | $\tfrac12$ |

Worked example: a photon at $0^\circ$ through a polarizer at $60^\circ$ gives
$P(\text{pass}) = \cos^2 60^\circ = 0.25$.

## Superposition, and the part that is genuinely quantum

A polarizer at $45^\circ$ transmits a photon that is in the state

$$
|+\rangle = \frac{1}{\sqrt 2}\bigl(|0\rangle + |1\rangle\bigr)
$$

and a polarizer at $-45^\circ$ transmits

$$
|-\rangle = \frac{1}{\sqrt 2}\bigl(|0\rangle - |1\rangle\bigr)
$$

A **classical** wave can also be split between two directions, and the
interference pattern is the same. The difference appears when you *measure*
the polarization:

- a classical wave keeps both components and shows them in the intensity;
- a quantum photon is found in **one** definite polarization, chosen at
  random, with probabilities $|\alpha|^2$ and $|\beta|^2$.

That irreversible, probabilistic collapse is what makes it quantum, and it is
exactly the Born rule you will formalise in section 5.

## The cascade

Three polarizers in a row is the classic demonstration. With
$0^\circ \rightarrow 45^\circ \rightarrow 90^\circ$:

| Stage | Conditional probability of passing |
|---|---|
| 0° (input already 0°) | $1$ |
| 45° | $\cos^2 45^\circ = 0.5$ |
| 90° | $\cos^2 45^\circ = 0.5$ |

Total probability of emerging: $0.5 \times 0.5 = 0.25$. But remove the middle
polarizer and the probability is **zero** — the $45^\circ$ polarizer is what
*created* the superposition that the $90^\circ$ polarizer then destroyed.
This is interference, and it is the same phenomenon that underlies every
quantum algorithm.

## Try it yourself

```bash
python labs/L02_photon_polarization/lab.py
```

The lab implements the polarizer as a matrix, runs the cascade, and checks
that the *conditional* probabilities are $[0.5, 1.0, 0.5]$ while the
*cumulative* ones are $[0.5, 0.5, 0.25]$.

## Self-check

- [ ] Can you compute $P(\text{pass})$ for any pair of angles?
- [ ] Can you explain why a classical wave and a quantum photon differ even
      though both can be "in two directions at once"?
- [ ] Do you know why the three-polarizer cascade lets 25% of the light
      through, but removing the middle polarizer lets 0% through?
- [ ] Have you run `python labs/L02_photon_polarization/lab.py`?

## Where to go next

Section 3 — [Math Foundation](03-math-foundation.md). Photon polarization
gave you the intuition; the next section gives you the formal toolkit.
