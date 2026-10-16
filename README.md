# QC101 — Quantum Computing & Introduction to Quantum Machine Learning

A complete, hands-on study companion for the Udemy course
**[QC101 — Introduction to Quantum Computing / Quantum Physics for Beginners](https://www.udemy.com/course/qc101-introduction-to-quantum-computing-quantum-physics-for-beginners/)**
by **Kumaresan Ramanathan** (17 sections · 286 lectures · ~11h53m).

Everything here is *runnable*. There is no pseudo-code: the 17 labs execute
against a real quantum stack (a dependency-free simulator written for this
course **plus** Qiskit / Aer / Qiskit Machine Learning), the quizzes are
auto-graded, and the study site ships live interactive widgets.

The course is math-first, and so is this repository. Complex numbers,
probability and statistics, Boolean logic and linear algebra are introduced
as the *backbone* of quantum mechanics, and every quantum concept is
derived from them rather than asserted.

---

## What's in the box

| Piece | What it is | Count |
|---|---|---|
| [`docs/`](docs/) | Chapter-by-chapter study guide, one file per course section | 17 chapters + `index.md` + 4 appendix pages |
| [`labs/`](labs/) | Runnable, auto-graded hands-on labs | 17 labs, **350 checks** |
| [`labs/common/qc101/`](labs/common/qc101/) | The shared library the labs build on | 9 modules, **167 self-tests** |
| [`quizzes/`](quizzes/) | Auto-graded question bank, one JSON per section | **104 questions** |
| [`notebooks/`](notebooks/) | Executable Jupyter notebooks (math → qubit → BB84 → KNN → QSVM) | 5 notebooks |
| [`site/`](site/) | Self-contained interactive study site (no build step, no CDN) | 8 live widgets + quiz + progress |
| [`qsharp/QB4/`](qsharp/QB4/) | The course's Q# program, modernised to `net8.0` | 1 project |
| [`tools/`](tools/) | Runner scripts (labs, quiz, progress, site build & check) | 7 scripts |

---

## Quick start

```bash
git clone https://github.com/atalupadhyay1/introduction-to-quantum-computing.git
cd introduction-to-quantum-computing

python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

make selftest        # 167 checks on the shared library   (~2 s)
make labs            # all 17 labs                        (~100 s)
make site            # build the study site into site/
make site-check      # verify the site is complete        (~1 s)
make serve           # serve the study site on :8000
make check           # everything above that can fail
```

Full instructions, including the "no-Qiskit" fallback, are in
[`SETUP.md`](SETUP.md).

---

## The 17 sections, mapped

| # | Course section | Chapter | Lab | What the lab does |
|---|---|---|---|---|
| 1 | Introduction | [01](docs/01-introduction.md) | [L01](labs/L01_quantum_vs_classical) | Classical bits vs. qubits, why a qubit is not "a bit that is both" |
| 2 | Photon Polarization | [02](docs/02-photon-polarization.md) | [L02](labs/L02_photon_polarization) | Malus's law, polarizers, the photon as the physical qubit |
| 3 | Math Foundation | [03](docs/03-math-foundation.md) | [L03](labs/L03_boolean_logic) · [L04](labs/L04_probability_statistics) · [L05](labs/L05_complex_numbers) · [L06](labs/L06_linear_algebra) | Boolean logic → gates; probability → amplitudes; complex numbers → phase; linear algebra → unitaries |
| 4 | Quantum Cryptography | [04](docs/04-quantum-cryptography.md) | [L07](labs/L07_bb84_cryptography) | BB84 end to end, sifting, QBER, the one-time pad |
| 5 | A Math Model for Quantum Physics | [05](docs/05-math-model.md) | [L08](labs/L08_math_model) | The Dirac notation model, state vectors, operators |
| 6 | Quantum Physics of Spin States | [06](docs/06-spin-states.md) | [L09](labs/L09_spin_states) | Spin-½, the Bloch sphere, Rabi-ish rotations |
| 7 | Modeling Spin States with Math | [07](docs/07-modeling-spin.md) | [L10](labs/L10_dirac_notation) | Pauli's matrices, spinors, expectation values |
| 8 | Reversible and Irreversible Transformations | [08](docs/08-reversible-irreversible.md) | [L11](labs/L11_reversible_entanglement) | Reversible vs. destructive measurement, gates as matrices |
| 9 | Multi-Qubit Systems | [09](docs/09-multi-qubit.md) | [L11](labs/L11_reversible_entanglement) | Tensor products, the 2-qubit state space, CNOT/Toffoli |
| 10 | Entanglement | [10](docs/10-entanglement.md) | [L11](labs/L11_reversible_entanglement) | Bell states, CHSH, entanglement entropy, EPR |
| 11 | Superposition & Entanglement Simulators | [11](docs/11-simulators.md) | [L12](labs/L12_simulators) | The course's Java simulators, ported to Python |
| 12 | Quantum Computing Model | [12](docs/12-quantum-computing-model.md) | [L13](labs/L13_quantum_computing_model) | Circuits, the measurement cascade, stabilizers, grover's setup |
| 13 | Microsoft Q# | [13](docs/13-qsharp.md) | [L14](labs/L14_qsharp) | The Q# program, transliterated and executed in Python |
| 14 | IBM Quantum Experience | [14](docs/14-ibm-quantum.md) | [L15](labs/L15_qiskit) | The IBM platform, circuits in Qiskit, `AerSimulator` |
| 15 | IBM Qiskit Programming & Algorithms | [15](docs/15-qiskit.md) | [L15](labs/L15_qiskit) | QFT, period finding, Shor's algorithm, batched BB84 on a real simulator |
| 16 | Machine Learning Foundation | [16](docs/16-ml-foundation.md) | [L16](labs/L16_machine_learning_foundation) | Supervised learning, over/underfitting, regularisation, sigmoid models |
| 17 | Quantum Machine Learning with Qiskit | [17](docs/17-quantum-ml.md) | [L17](labs/L17_quantum_machine_learning) | Quantum KNN, quantum kernels, the QSVM |

---

## The labs

Every lab is a single self-contained `lab.py` that prints a narrated walkthrough
and then **checks its own work**. A lab is a success only if every check
passes, so the labs double as the test suite for the library.

```bash
python labs/L07_bb84_cryptography/lab.py     # one lab, with full narration
python tools/labcheck.py                     # all 17, summary only
python tools/labcheck.py --list              # what is available
python tools/labcheck.py L07 L15 -v          # two labs, verbose
python tools/labcheck.py --save              # record results for the dashboard
```

Current status:

```
L01  12 checks   L07  20 checks   L13  13 checks
L02  17 checks   L08  16 checks   L14  10 checks
L03  17 checks   L09  13 checks   L15  16 checks
L04  18 checks   L10  20 checks   L16  30 checks
L05  29 checks   L11  29 checks   L17  24 checks
L06  47 checks   L12  19 checks
                        350 checks total, all passing
```

The shared library has its own suite:

```bash
python labs/common/qc101/selftest.py        # 167 checks
```

### The shared library

`labs/common/qc101/` is **pure Python with no third-party dependencies**, so
the math labs run anywhere, instantly, with no install step.

| Module | Contents |
|---|---|
| `complexnum` | Complex arithmetic, polar form, roots of unity, `i` |
| `boolean` | Truth tables, AND/OR/NOT/XOR, reversible gates, one-time pad |
| `probability` | Distributions, Bayes, expectation, variance, sampling |
| `linalg` | Matrices, Kronecker products, RREF, determinants, eigenvalues |
| `quantum` | State vectors, gates, measurement, entanglement, density matrices |
| `photon` | Polarization, Malus's law, Jones-like vectors, interference |
| `bb84` | The BB84 protocol, sifting, QBER, eavesdropper models |
| `viz` | ASCII plotting for Bloch spheres, probability bars, histograms |
| `labkit` | The lab harness: `section` / `step` / `note` / `show` / `check` |

---

## The study site

```bash
make site        # regenerate site/content from docs/ and quizzes/
make site-check  # 77 checks: files, manifest, routes, widgets, JS syntax
make serve       # http://localhost:8000
```

The site is a plain single-page app: `index.html` + three assets + a
vendored copy of KaTeX. No bundler, no CDN, no network access required —
it works from a `file://` URL or any static host.

It provides:

* a **navigable chapter reader** for all 17 chapters and the 4 appendix pages;
* **8 live widgets** — Bloch sphere, gate playground, Malus polarizer, BB84
  eavesdropper, Bell state inspector, 2-qubit Bell stepper, quantum KNN,
  and period-finding peak finder;
* an **auto-graded quiz** over all 104 questions with immediate feedback;
* a **progress dashboard** that reads the results written by
  `tools/labcheck.py --save` and `tools/quiz.py`;
* a **dark/light theme** and a formula sheet that always stays one click away.

---

## Quizzes and progress

```bash
python tools/quiz.py --list                # the whole bank
python tools/quiz.py                       # interactive, mixed sections
python tools/quiz.py -s 4 -n 10            # 10 questions from section 4
python tools/quiz.py --all --markdown      # export every question as Markdown
python tools/progress.py                   # your dashboard
python tools/progress.py --reset           # start over
```

Answers are graded automatically, explanations are shown either way, and your
scores are written to `progress/quiz_results.json`, which is what the site's
progress page reads.

---

## Notebooks

```bash
pip install jupyter
jupyter lab notebooks/
```

Five notebooks, all of which execute end to end with no errors:

| Notebook | Topic |
|---|---|
| `01_math_foundation.ipynb` | Complex numbers, Boolean logic, probability, linear algebra |
| `02_qubit_basics.ipynb` | State vectors, gates, measurement, Bloch sphere |
| `03_bb84.ipynb` | The protocol, the eavesdropper, the one-time pad |
| `04_quantum_knn.ipynb` | The course's quantum KNN, and the identity behind it |
| `05_quantum_svm.ipynb` | Feature maps, quantum kernels, a QSVM on iris |

---

## A note on the Qiskit labs

The course's original code targets the pre-1.0 Qiskit API (`BasicAer`,
`QuantumInstance`, `qiskit.algorithms.Shor`). That API no longer exists. The
Qiskit labs here are **modernised for Qiskit 2.x**:

| Old | New |
|---|---|
| `BasicAer.get_backend` | `qiskit_aer.AerSimulator` |
| `QuantumInstance` | `SamplerV2` / `QMLSampler` |
| `qiskit.algorithms.Shor` | built from the QFT + period-finding, as in `labs/L15_qiskit` |
| `qiskit.utils.algorithm_globals` | `numpy.random.default_rng` |
| `save_statevector()` | `Statevector(circuit)` |
| `save_unitary()` | `Operator(circuit)` |
| `QuantumKernel` | `FidelityQuantumKernel(feature_map=..., fidelity=ComputeUncompute(...))` |

The physics and the results are unchanged — only the API surface is.

---

## Repository layout

```
.
├── Makefile                 # every task you need, one command each
├── requirements.txt         # pinned Python dependencies
├── SETUP.md                 # installation, troubleshooting, optional pieces
├── README.md
├── docs/                    # 17 chapters + index + appendix
│   └── appendix/            # formula sheet, glossary, API reference
├── labs/                    # 17 auto-graded labs
│   └── common/qc101/        # the shared, dependency-free library
├── notebooks/               # 5 executable notebooks
├── quizzes/questions/       # 104 questions, one JSON per section
├── qsharp/QB4/              # the course's Q# program (net8.0)
├── site/                    # the interactive study site
├── tools/                   # labcheck / quiz / progress / build_site / site_check / generators
└── progress/                # recorded results (JSON)
```

---

## License & attribution

The study material here is original work written to accompany the QC101
course. 

The study site vendors **KaTeX 0.19** (`site/vendor/katex/`) so that the
maths renders with no network access; KaTeX is MIT-licensed and its licence
is included at `site/vendor/katex/LICENSE`.
