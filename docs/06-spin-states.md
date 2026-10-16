# Section 6 — Quantum Physics of Spin States

> **Course section** 6 of 17 · **Lab** [`L09`](../labs/L09_spin_states/lab.py) · **Quiz** 6 questions

## What you should be able to do

- Describe the spin-1/2 system and its two basis states.
- Explain the Stern-Gerlach experiment and what it proved.
- Connect spin-up/spin-down to $|0\rangle$ and $|1\rangle$.
- Say why spin makes a *better* qubit than photon polarization for some
  experiments.

## Spin-1/2

A particle with spin $\tfrac12$ — an electron, a proton, a neutron — has
exactly two possible results when you measure the component of its angular
momentum along any axis:

- spin **up**: $S_z = +\tfrac12\hbar$
- spin **down**: $S_z = -\tfrac12\hbar$

This is the definition of a two-level system, so a spin-1/2 particle *is* a
qubit. By convention:

$$
|\uparrow\rangle \equiv |0\rangle, \qquad
|\downarrow\rangle \equiv |1\rangle
$$

## The Stern-Gerlach experiment

Silver atoms fired through a non-uniform magnetic field split into **two**
beams, not a continuous spread. Before the experiment, one expected a
continuous distribution of magnetic moment. The result said: the component
is quantised.

The devastating follow-up is *Stern-Gerlach on a superposition*. Take an
atom whose spin is already in a superposition of up and down, and pass it
through an SG apparatus oriented along a **different** axis. You do not get
"up and down along the new axis" — you get a *third* distribution, with
$50/50$ outcomes along the new axis for a spin prepared along $\hat{z}$.

That is the "quantum" of it. The pre-existing state does not survive the
measurement; the apparatus *overwrites* it with a new one. And the
probabilities are the squares of amplitudes in the new basis.

## Superposition in the Bloch sphere

A spin-1/2 state in a magnetic field precesses. The full state is

$$
|\psi\rangle = \cos\frac{\theta}{2}\,|0\rangle + e^{i\phi}\sin\frac{\theta}{2}\,|1\rangle
$$

with $0 \le \theta \le \pi$ and $0 \le \phi < 2\pi$. The angle $\theta$ is
the polar angle on the Bloch sphere and $\phi$ is the azimuth:

- $\theta = 0$ → $|0\rangle$ (spin up), the north pole;
- $\theta = \pi$ → $|1\rangle$ (spin down), the south pole;
- $\theta = \pi/2$ → the equator, the equal-probability superpositions
  $|+\rangle$ and $|-\rangle$.

## Spin versus polarization

| | Photon polarization | Spin-1/2 |
|---|---|---|
| Basis states | H / V | up / down |
| Direct measurement? | yes, with a polarizer | yes, with a Stern-Gerlach apparatus |
| Rotation | rotate the polarizer | rotate the magnetic field |
| Natural implementation | optics | semiconductors (qubits) |

Both are two-level systems, so the mathematics is identical. Spins are how
real hardware implements qubits.

## Try it yourself

```bash
python labs/L09_spin_states/lab.py
```

The lab simulates the Stern-Gerlach experiment: prepare a state, measure it
along an arbitrary axis, and check that the distribution matches the Born
rule for that axis.

## Self-check

- [ ] Can you state the two eigenvalues of $S_z$?
- [ ] Can you explain what the Stern-Gerlach experiment showed that classical
      physics did not expect?
- [ ] Do you know what a spin prepared along $\hat{z}$ gives when measured
      along $\hat{x}$?
- [ ] Have you run `python labs/L09_spin_states/lab.py`?

## Where to go next

Section 7 — [Modeling Quantum Spin States with Math](07-modeling-spin.md).
Now write the spin state as a column vector and start multiplying matrices.
