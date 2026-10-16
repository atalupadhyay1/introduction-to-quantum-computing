# Section 1 — Introduction

> **Course section** 1 of 17 · **Lab** [`L01`](../labs/L01_quantum_vs_classical/lab.py) · **Quiz** 5 questions

## What you should be able to do

- Explain what a quantum computer is *for*, and what it is not for.
- Name the three ingredients of every quantum algorithm.
- Say which of the course's 17 sections you will need for each later topic.
- Run the first lab and read its auto-graded output.

## The one-sentence version

A quantum computer is **not** a faster classical computer. It is a special
purpose device that solves a small family of problems exponentially faster
by exploiting superposition and entanglement — and everything else about
computing still happens on the classical machine.

## The shape of the course

The course is deliberately **maths first**. Before a single gate is applied
you spend three sections on the mathematics that quantum physics is written
in:

```
  complex numbers  ->  probability  ->  linear algebra  ->  boolean logic
        \                 |                 |                 /
         \                |                 |                /
          +---------------+----------------+----------------+
                                  |
                    the language of quantum mechanics
```

| Section | Topic | Lab |
|---|---|---|
| 1 | Introduction | L01 |
| 2 | Quantum physics through photon polarization | L02 |
| 3 | Math foundation: complex numbers, probability, linear algebra, logic | L03–L06 |
| 4 | Quantum cryptography (BB84) | L07 |
| 5 | A math model for quantum physics | L08 |
| 6 | Quantum physics of spin states | L09 |
| 7 | Modeling spin states with math | L10 |
| 8 | Reversible and irreversible transformations | L11 |
| 9 | Multi-qubit systems | L11 |
| 10 | Entanglement | L11 |
| 11 | Superposition and entanglement simulators | L12 |
| 12 | The quantum computing model | L13 |
| 13 | Quantum programming with Microsoft Q# | L14 |
| 14 | IBM Quantum Experience | L15 |
| 15 | Quantum programming and algorithms with IBM Qiskit | L15 |
| 16 | Machine learning foundation | L16 |
| 17 | Quantum machine learning with Qiskit | L17 |

## The three ingredients of a quantum algorithm

1. **A state** — the description of the system, in this course a vector of
   amplitudes.
2. **A transformation** — a unitary matrix (a "gate") applied to that state.
3. **A measurement** — the irreversible step that turns amplitudes into
   numbers you can read.

Every lab in this repository follows the same shape, because every quantum
program follows the same shape:

```python
state = initial_state()          # 1. state
for gate in gates:                # 2. transformations
    state = apply(gate, state)
outcome = measure(state)          # 3. measurement
```

## What a quantum computer is good for

| Problem | Speed-up | Why |
|---|---|---|
| Factoring integers (Shor) | exponential | period finding + QFT |
| Simulating molecules and materials | exponential | the simulator *is* the physics |
| Unstructured search (Grover) | quadratic | amplitude amplification |
| Quantum simulation of many-body systems | exponential | same reason as above |

And what it is **not** good for: sorting, spreadsheet work, rendering video,
or anything where a good classical algorithm already exists.

## Try it yourself

```bash
python labs/L01_quantum_vs_classical/lab.py
```

The lab contrasts a classical bit-flipping circuit with a quantum
superposition, and shows you what "reading out" a superposition actually
costs you. Every check is auto-graded, and the lab ends with a one-line
summary.

## Self-check

- [ ] Can you state the one-sentence difference between a quantum computer
      and a classical computer?
- [ ] Can you name the three stages of a quantum program?
- [ ] Do you know which two sections of the course are about machine
      learning, and why the classical one comes first?
- [ ] Have you run `python labs/L01_quantum_vs_classical/lab.py` and seen it
      pass?

## Where to go next

Section 2 — [Quantum Physics Through Photon Polarization](02-photon-polarization.md).
Light is the most familiar quantum system there is, and polarization is a
two-state system you can reason about without any machinery at all.
