# Section 13 — Quantum Programming with Microsoft Q#

> **Course section** 13 of 17 · **Lab** [`L14`](../labs/L14_qsharp/lab.py) · **Quiz** 6 questions

## What you should be able to do

- Read and write basic Q# — `let` bindings, `mutable` variables, message
  passing, `if`/`elif`/`else`.
- Understand Q#'s qubit ordering, and avoid the ordering trap.
- Run the course's `QB4` program and explain each of its demos.
- Say why learning Q# before Qiskit is worthwhile.

## Why Q# first

The course's "Q#, Qiskit, or Cirq?" note makes the argument: Q# has
almost no classical control flow to hide behind. There are no loops over
classical data, no `if` on a classical value, no arrays of classical
integers. What you write *is* the quantum program. Learn the physics in
Q#, then the plumbing in Qiskit.

## The language in one page

```qsharp
namespace QC101 {
    operation Set(desired : Result, q : Qubit) : Unit {
        if (M(q) != desired) {
            X(q);
        }
    }
}
```

| Construct | Meaning |
|---|---|
| `let x = 5;` | immutable binding |
| `mutable y = 0;` | a binding that can be updated |
| `set y = y + 1;` | update a mutable binding |
| `Message` | a value passed between operations |
| `Qubit` | a qubit reference; cannot be copied |
| `Result` | the `Zero` / `One` outcome of a measurement |
| `return (q0, q1);` | a tuple of results, **in reverse qubit order** |

## The ordering trap

This is the single most important practical fact in the section, and the
course has a whole article about it ("Verifying Results").

- A Q# **result array** is printed **right to left**: `(q2, q1, q0)`.
- A **state vector** is written **left to right**: $(q_0, q_1, q_2)$.

So if you multiply a CCNOT matrix by a state vector to check your result by
hand, you must **reverse the ordering** first. Get it wrong and you get an
answer that looks plausible and is wrong.

The lab demonstrates it directly: with $q_0 = 1$ and $q_1 = 0$, Q# reports
`"01"` while the same state written in textbook order is `"10"`.

## The QB4 program

The course's `QB4.qs` is a four-qubit demonstration program. It runs
10 000 trials and prints a histogram over all sixteen bit strings. The
demos are:

| Demo | What it shows |
|---|---|
| NOP | the default state `0000` |
| X | a single flip |
| H | a superposition |
| SWAP | exchanging two qubits |
| CNOT | a controlled flip |
| Bell | $H$ then CNOT producing a Bell pair |
| Toffoli | a doubly-controlled flip |

The `Set` operation is the reusable bit of code: it measures a qubit and
applies $X$ if the outcome is not the one you want. It is the quantum
version of "set this bit to a given value" — and the reason it needs a
measurement is that setting a bit is *not* reversible, unlike `X`.

## Running it

Q# needs the .NET SDK and the Quantum Development Kit, which is not
installed in this sandbox. So this repository ships:

- `qsharp/QB4/QB4.qs` — the course's program, modernized (the original
  targeted the legacy SDK 0.12 and `netcoreapp3.1`; the copy here targets
  `net8.0` and `Microsoft.Quantum.Sdk` 0.27.0);
- `qsharp/QB4/QB4.csproj` — the modernized project file;
- lab **L14** — a runnable Python *transliteration* of the same program, so
  you can see the behaviour without a .NET toolchain.

To run the real thing:

```bash
dotnet new console -o QB4
cd QB4
dotnet add package Microsoft.Quantum.Sdk
cp ../qsharp/QB4/QB4.qs .
dotnet run
```

## Try it yourself

```bash
python labs/L14_qsharp/lab.py
```

## Self-check

- [ ] Can you write a Q# operation that sets a qubit to a given value?
- [ ] Do you know that the result array comes back in reverse qubit order,
      and that the state vector does not?
- [ ] Can you explain what each of the seven QB4 demos shows?
- [ ] Have you run `python labs/L14_qsharp/lab.py`?

## Where to go next

Section 14 — [IBM Quantum Experience](14-ibm-quantum.md). The service where
the circuits run on real hardware.
