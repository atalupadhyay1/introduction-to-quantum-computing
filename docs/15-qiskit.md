# Section 15 — Quantum Programming and Algorithms with IBM Qiskit

> **Course section** 15 of 17 · **Lab** [`L15`](../labs/L15_qiskit/lab.py) · **Quiz** 7 questions

## What you should be able to do

- Build, transpile, run and read results from a Qiskit circuit.
- Use the modern 2.x APIs: `AerSimulator`, `Statevector`, `Operator`,
  `assign_parameters`.
- Implement BB84 in Qiskit with a quantum random number generator.
- Implement Shor's period finding with a real quantum circuit and recover
  the period from the measurement statistics.

## The API has moved

The course was recorded against Qiskit 0.x. Qiskit 1.0 removed a great
deal, and Qiskit 2.x removed more. This is why the course ships a
"Shor's Algorithm — Temporary Fix" article: the code stopped running.

| Old (removed) | Modern |
|---|---|
| `BasicAer.get_backend("qasm_simulator")` | `qiskit_aer.AerSimulator()` |
| `QuantumInstance(backend, shots=...)` | `qiskit_ibm_runtime` primitives, or a plain `backend.run(..., shots=...)` |
| `circuit.bind_parameters({...})` | `circuit.assign_parameters({...})` |
| `qiskit.algorithms.Shor` | build the circuit yourself |
| `qiskit.utils.algorithm_globals` | `numpy.random.default_rng(seed)` |
| `circuit.save_statevector()` | `qiskit.quantum_info.Statevector(circuit)` |
| `qiskit.algorithms.phase_estimation` | `qiskit.synthesis` / your own circuit |

## The course's five circuits

| File | What it shows |
|---|---|
| `circuit1.py` | a three-qubit GHZ state with `measure_all` |
| `circuit2.py` | building the circuit programmatically with `CXGate().append` |
| `circuit3.py` | `Parameter` objects, `assign_parameters`, and `initialize` |
| `circuit4.py` | a custom gate built from a circuit with `to_gate()` |
| `circuit5.py` | a custom *instruction* with `to_instruction()` |
| `compute_matrix.py` | the unitary of a circuit, via `Operator` |
| `simulate_circuit.py` | running with 1000 shots |

The difference between `to_gate()` and `to_instruction()` matters: a
**gate** is reversible and can be controlled; an **instruction** is not, and
`decompose()` expands it back into its parts.

## BB84 in Qiskit

The course's `bb84.py` uses a quantum random number generator for every
random choice — the bit and the basis:

```python
circuit = QuantumCircuit(1, 1)
circuit.x(0)          # if the bit is 1
circuit.barrier()
circuit.h(0)          # if the basis is diagonal
circuit.barrier()
circuit.measure(0, 0)
```

The `barrier()` calls are cosmetic but instructive: they stop the
optimiser from merging the gates across the random choice, which would
change the physics.

## Shor's algorithm

Shor's algorithm reduces factoring to finding the **period** $r$ of

$$
f(x) = a^x \bmod N
$$

for a random $a$ coprime to $N$. The classical part of the reduction is
easy; the hard part — computing a discrete logarithm — is where the
quantum part enters.

The quantum circuit is Kitaev's order-finding circuit:

1. the counting register ($m$ qubits) goes into a uniform superposition;
2. the target register is prepared in $\lvert1\rangle$;
3. for each counting qubit $i$, apply a **controlled** $U^{2^i}$, where
   $U\lvert y\rangle = a \cdot y \bmod N$;
4. apply the **inverse QFT** to the counting register;
5. measure the counting register.

The measurement lands on multiples of $2^m / r$, so $r$ falls out of the
*distribution*, recovered by a continued-fraction expansion of
$y/2^m$.

The lab implements exactly this with $N = 15$, $a = 2$, $m = 4$. The
classical period is 4, and the quantum run gives peaks at
$0, 4, 8, 12$ — the multiples of $16/4 = 4$ — and recovers $r = 4$. Then

$$
\gcd\bigl(2^{4/2} - 1, 15\bigr) = \gcd(3, 15) = 3
$$

and 3 is a factor of 15.

## Try it yourself

```bash
python labs/L15_qiskit/lab.py
```

The lab runs the five course circuits, compiles a circuit to a matrix, runs
BB84 with a QRNG (batched so that 400 rounds need only ~18 simulator
calls), and runs the period finder.

## Self-check

- [ ] Can you name the modern replacement for each of `BasicAer`,
      `bind_parameters` and `qiskit.algorithms.Shor`?
- [ ] Do you know the difference between `to_gate()` and `to_instruction()`?
- [ ] Can you explain why the period-finding measurement peaks at multiples
      of $2^m/r$?
- [ ] Have you run `python labs/L15_qiskit/lab.py` and seen the period
      recovered?

## Where to go next

Section 16 — [Machine Learning Foundation](16-ml-foundation.md). Before
quantum machine learning, the classical machine learning it replaces.
