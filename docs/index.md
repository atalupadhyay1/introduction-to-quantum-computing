# QC101 — Quantum Computing & Introduction to Quantum Machine Learning

A complete, interactive study package for the Udemy course
[**QC101 — Introduction to Quantum Computing / Quantum Physics for
Beginners**](https://www.udemy.com/course/qc101-introduction-to-quantum-computing-quantum-physics-for-beginners/)
by Kumaresan Ramanathan (17 sections, 286 lectures, ~11h 53m).

The course is **maths first**, and so is this package. Every concept in
the course has a matching chapter here *and* a runnable, auto-graded lab.

## The chapters

| # | Chapter | Lab | Quiz |
|---|---|---|---|
| 1 | [Introduction](01-introduction.md) | L01 | 5 |
| 2 | [Quantum Physics Through Photon Polarization](02-photon-polarization.md) | L02 | 6 |
| 3 | [Math Foundation](03-math-foundation.md) | L03–L06 | 7 |
| 4 | [Quantum Cryptography](04-quantum-cryptography.md) | L07 | 6 |
| 5 | [A Math Model for Quantum Physics](05-math-model.md) | L08 | 6 |
| 6 | [Quantum Physics of Spin States](06-spin-states.md) | L09 | 6 |
| 7 | [Modeling Quantum Spin States with Math](07-modeling-spin.md) | L10 | 6 |
| 8 | [Reversible and Irreversible Transformations](08-reversible-irreversible.md) | L11 | 6 |
| 9 | [Multi-Qubit Systems](09-multi-qubit.md) | L11 | 6 |
| 10 | [Entanglement](10-entanglement.md) | L11 | 6 |
| 11 | [Superposition and Entanglement Simulators](11-simulators.md) | L12 | 5 |
| 12 | [The Quantum Computing Model](12-quantum-computing-model.md) | L13 | 6 |
| 13 | [Microsoft Q# Programming](13-qsharp.md) | L14 | 6 |
| 14 | [IBM Quantum Experience](14-ibm-quantum.md) | L15 | 4 |
| 15 | [IBM Qiskit: Programming and Algorithms](15-qiskit.md) | L15 | 7 |
| 16 | [Machine Learning Foundation](16-ml-foundation.md) | L16 | 8 |
| 17 | [Quantum Machine Learning with Qiskit](17-quantum-ml.md) | L17 | 7 |

Plus the [appendix](appendix/appendix.md): formula sheet, glossary and the
API reference for the shared `qc101` library.

## How to use this package

```bash
# 1. set up (once)
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# 2. run every lab, with an auto-graded pass/fail table
python tools/labcheck.py

# 3. quiz yourself on any section
python tools/quiz.py -s 4

# 4. see how you are doing
python tools/progress.py

# 5. read the study site in your browser
python tools/build_site.py && python -m http.server -d site 8000
```

The labs are numbered to match the course's sections, and each lab says
which course section it belongs to at the top of the file.

## The labs

| Lab | Course section | Checks |
|---|---|---|
| L01 | 1 Introduction | 12 |
| L02 | 2 Photon polarization | 17 |
| L03 | 3 Boolean logic | 17 |
| L04 | 3 Probability and statistics | 18 |
| L05 | 3 Complex numbers | 29 |
| L06 | 3 Linear algebra | 47 |
| L07 | 4 BB84 | 18 |
| L08 | 5 Math model | 16 |
| L09 | 6 Spin states | 13 |
| L10 | 7 Dirac notation | 20 |
| L11 | 8–10 Reversible gates, multi-qubit, entanglement | 29 |
| L12 | 11 Simulators | 19 |
| L13 | 12 Quantum computing model | 13 |
| L14 | 13 Q# | 10 |
| L15 | 14–15 Qiskit | 16 |
| L16 | 16 Machine learning foundation | 30 |
| L17 | 17 Quantum machine learning | 24 |

**350 auto-graded checks in total.**

## Where the material came from

- The course's own 17-section syllabus and lecture list.
- The official [Packt companion repository](https://github.com/PacktPublishing/QC101-Quantum-Computing-and-Introduction-to-Quantum-Machine-Learning)
  — the seven "Course Articles", the Q# project, the Python lab files and
  the Java simulators.
- The course's own code, **modernized** for Qiskit 2.x: `BasicAer`,
  `QuantumInstance`, `bind_parameters` and `qiskit.algorithms.Shor` were all
  removed in Qiskit 1.0, so this package rebuilds those parts.

Nothing here is a summary of the videos; it is a second, runnable
implementation of everything the course teaches.
