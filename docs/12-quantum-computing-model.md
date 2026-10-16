# Section 12 — The Quantum Computing Model

> **Course section** 12 of 17 · **Lab** [`L13`](../labs/L13_quantum_computing_model/lab.py) · **Quiz** 6 questions

## What you should be able to do

- Name the three stages of a quantum program and why each is what it is.
- Compile a gate list into a single unitary matrix and apply it to any input.
- Distinguish a state-vector simulator from a shot-based device.
- Work out the depth and gate count of a circuit.

## The three-stage program

```
  1. INITIALISE   (irreversible)   prepare the qubits in a known state
  2. COMPUTE      (reversible)     apply gates
  3. READ OUT     (irreversible)   measure
```

The middle stage is reversible because the *whole* program, including
initialisation and measurement, is a quantum channel. This is why a quantum
computer is a strange device: the interesting part (the computation) can be
undone, but the part that produces the answer cannot.

## Compiling a circuit to a matrix

A gate list $[g_1, g_2, \dots, g_k]$ acting on a column state vector
compiles to a single matrix:

$$
U = G_k \cdots G_2 G_1
$$

**Order matters.** Gates are applied left to right to the *state*, so the
first gate's matrix is on the *right*. The lab checks this explicitly
because getting it backwards produces plausible but wrong answers.

The compiled matrix is the circuit's unitary, and it has two great
properties: it can be applied to any input state, and it can be inverted
($\text{circuit}^{-1}$ is the reversed gate list with each gate replaced by
its adjoint).

## Simulator versus device

| | state-vector simulator | real device (or shot-based simulator) |
|---|---|---|
| returns | exact complex amplitudes | integer counts |
| answers | "the probability is 0.3141..." | "the probability is about 0.31" |
| cost | memory $\propto 2^n$ | time $\propto$ shots $\times$ depth |
| noise | none | decoherence, gate error, readout error |

Both are *correct* answers to different questions. The course's
`simulate_circuit.py` uses 1000 shots precisely so you see the difference
between the two.

## Circuit size

For an $n$-qubit circuit:

- the state vector has $2^n$ complex amplitudes (16 bytes each);
- a full $2^n \times 2^n$ unitary has $2^{2n}$ entries — for $n = 10$ that
  is a *billion* entries, which is why simulators never build the full
  matrix;
- a real device needs the *depth* and the *gate count*, not the state size.

That is the fundamental trade: the simulator's cost explodes with the state
size, the device's cost grows with the circuit.

## Try it yourself

```bash
python labs/L13_quantum_computing_model/lab.py
```

The lab builds a gate-list compiler, checks that the compiled matrix
reproduces the circuit's result, verifies that the inverse circuit undoes
the original, and contrasts state-vector output with counts.

## Self-check

- [ ] Can you say which stage of a quantum program is irreversible and why
      each one is?
- [ ] Do you know which side of the matrix product the first gate goes on?
- [ ] Can you explain why a simulator does not build a full $2^n \times 2^n$
      matrix?
- [ ] Have you run `python labs/L13_quantum_computing_model/lab.py`?

## Where to go next

Section 13 — [Microsoft Q# Programming](13-qsharp.md). Your first real
quantum programming language.
