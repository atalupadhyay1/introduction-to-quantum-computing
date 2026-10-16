# Section 14 — IBM Quantum Experience

> **Course section** 14 of 17 · **Lab** [`L15`](../labs/L15_qiskit/lab.py) · **Quiz** 4 questions

## What you should be able to do

- Find the current IBM Quantum platform and explain what it offers.
- Describe the difference between running on a simulator and on a real QPU.
- Explain what calibration data is and why it matters.
- Know what a *job* is in the IBM Quantum workflow.

## Where the platform lives

The course's "IBM Quantum Note" article points at the service. The current
address is

> **https://quantum-computing.ibm.com/**

(The course was recorded in 2019, when the platform was at a different URL
— this is one of the few things in the course that has genuinely moved on,
and the article exists precisely to point you at the right place.)

## What the platform gives you

- **Simulators** — a state-vector simulator and a shot-based one, for
  everything from 5 to a few hundred qubits.
- **Real QPUs** — IBM's superconducting processors, run in a queue.
- **Calibration data** — the current $T_1$, $T_2$, gate fidelities and
  readout errors for the device you are about to use.
- **Jobs** — a submission is a *job* with a status, not an immediate
  answer.

## Simulator versus hardware

| | simulator | real QPU |
|---|---|---|
| latency | instant | queued, minutes to hours |
| noise | none (or injectable) | decoherence, crosstalk, drift |
| result | exact amplitudes or counts | counts, with an error bar |
| qubit count | hundreds | tens (hundreds planned) |
| cost | free | free tier, then paid |

The practical consequence: **your circuit has to fit the device's
connectivity map**. On a heavy-hex lattice, not every pair of qubits is
connected, so a good algorithm compiled for an abstract device can need a
lot of extra SWAP gates on real hardware. `transpile()` does that for you,
but it changes the depth — and the depth is what costs you your fidelity.

## The honest picture

Hardware is improving fast, but a 100-qubit device with 1% two-qubit gate
error is not yet a machine that can run a deep algorithm. This is why the
course's algorithms — BB84, Shor's period finding on a handful of qubits —
are exactly the right scale to study today: they are small enough to run
on real hardware, and large enough to show the interesting physics.

## Try it yourself

You do not need an account for anything in this repository — every lab runs
against a local simulator. But if you want to try the real thing:

1. Create a free account at <https://quantum-computing.ibm.com/>.
2. `pip install qiskit-ibm-runtime`.
3. Save your API token from the platform's account page.
4. Load the backend and submit a circuit.

```python
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService.save_account(channel="ibm_quantum_platform", token="...")
backend = service.least_busy(operational=True, simulator=False)
```

## Self-check

- [ ] Do you know the current URL of the IBM Quantum platform?
- [ ] Can you name three differences between running on a simulator and on
      hardware?
- [ ] Do you know what calibration data is and why you look at it before
      submitting?
- [ ] Do you understand why circuit *depth* matters more on hardware than
      in a simulator?

## Where to go next

Section 15 — [IBM Qiskit: Programming and Algorithms](15-qiskit.md). The
toolkit itself, and two real algorithms.
