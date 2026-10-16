# Setup

Everything you need to get the QC101 study companion running.

---

## 1. Requirements

| | Minimum | Notes |
|---|---|---|
| Python | 3.10 | 3.11 or 3.12 recommended; tested on 3.11.6 |
| Disk | ~250 MB | the virtual environment dominates; the repo itself is ~5 MB |
| Network | only for `pip install` | after that, everything runs offline |
| dotnet | *optional* | only needed to actually compile the Q# project (section 13) |
| Node | *optional* | only needed to re-vendor KaTeX |

The core labs and the shared library use **only the Python standard
library**, so you can start working immediately with nothing installed at
all. The Qiskit stack is needed for labs L15 and L17 and for the notebooks.

---

## 2. Install

```bash
git clone https://github.com/atalupadhyay1/introduction-to-quantum-computing.git
cd introduction-to-quantum-computing

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Verify:

```bash
make selftest      # 167 checks — no third-party packages needed
make labs          # all 17 labs
```

`make` on its own lists every available target.

---

## 3. The study site

The site is **pre-built** — `site/content/` is committed, so there is
nothing to do. Serve it with any static server:

```bash
make serve                        # http://localhost:8000
# or
python -m http.server 8000 --bind 0.0.0.0 --directory site
```

> `site/vendor/katex/` is a vendored copy of KaTeX 0.19 so that the maths
> renders **offline**. If you edit a chapter and want the site to pick it
> up, rebuild it with `make site` (needs `markdown` and
> `pymdown-extensions`, both in `requirements.txt`).

---

## 4. Running the pieces individually

```bash
# one lab, fully narrated
python labs/L12_simulators/lab.py

# all labs, summary only
python tools/labcheck.py
python tools/labcheck.py --list
python tools/labcheck.py L15 -v           # one lab, verbose
python tools/labcheck.py --save           # record results

# the shared library on its own
python labs/common/qc101/selftest.py

# quizzes
python tools/quiz.py --list
python tools/quiz.py -s 7 -n 5
python tools/quiz.py --all --markdown > quizzes.md

# progress
python tools/progress.py

# the site is complete and self-consistent
python tools/site_check.py
```

---

## 5. Notebooks

```bash
pip install jupyterlab
jupyter lab notebooks/
```

All five notebooks run top to bottom with no errors. They bootstrap the
`qc101` library themselves (each one contains a short path-fixing preamble),
so you can run them from any directory.

---

## 6. The Q# project (optional)

`qsharp/QB4/` contains the course's four-qubit Q# program, modernised from
the original `.csproj` to the current SDK:

```xml
<TargetFramework>net8.0</TargetFramework>
<PackageReference Include="Microsoft.Quantum.Sdk" Version="0.27.0" />
```

To compile and run it you need the .NET SDK and the Q# compiler:

```bash
dotnet --version           # 8.0 or later
dotnet workload install quantum

cd qsharp/QB4
dotnet run                 # 10 000 trials, 16 bitstring histogram
```

If you do not have .NET installed, **you are not blocked**: lab
`L14_qsharp` contains a faithful Python transliteration of `QB4.qs` that
runs the same circuits and reproduces the same histograms, and it is the
part that is auto-graded.

---

## 7. Troubleshooting

**`ModuleNotFoundError: No module named 'qc101'`**
The labs add `labs/common` to `sys.path` themselves. If you import the
library from your own script, do the same:

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "labs" / "common"))
import qc101
```

**`ModuleNotFoundError: No module named 'qiskit'`**
The Qiskit packages are optional. Install them with
`pip install -r requirements.txt`, or use `python3 -m venv` and then
`pip install` inside the activated environment.

**Lab L15 or L17 is slow**
L17 fits a quantum-kernel SVM, which is genuinely expensive. Use
`--exact` free paths where offered, and expect roughly a minute. L15 was
optimised (batched BB84 into 24-qubit circuits) down to about 7 seconds.

**Aer complains about the number of qubits**
`AerSimulator` supports up to 27 qubits per circuit in this setup. The
batched BB84 helper in `labs/L15_qiskit` caps each circuit at 24 qubits on
purpose.

**The site shows raw `$...$` instead of rendered maths**
KaTeX's auto-render script did not load. Check that
`site/vendor/katex/contrib/auto-render.min.js` exists and that you are
serving the site over HTTP (not opening the HTML with `file://`, which
blocks module loading in some browsers).

**Port 8000 is already in use**
`make serve PORT=8080`.

---

## 8. Running on a Raspberry Pi or an old laptop

The Qiskit labs are the only heavy part. Without them:

* `make selftest` and `make labs` still run everything except L15/L16/L17;
* the study site is fully functional and weighs 3 MB;
* the notebooks need only `numpy` for the last two.

---

## 9. Uninstalling

```bash
rm -rf .venv progress/lab_results.json progress/quiz_results.json
```

The repository itself is self-contained; nothing is installed system-wide.
