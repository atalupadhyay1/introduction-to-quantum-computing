"""
QC101 shared lab library.

Dependency-free helpers used by every lab in this repository.  Import them
with::

    from qc101 import quantum, linalg, boolean, probability, photon, bb84, viz

The package deliberately avoids numpy / qiskit so that the *math* labs run
in any Python 3.8+ environment and inside a browser via Pyodide.  The
Qiskit-based labs (L14-L17) import qiskit directly and need the full
install -- see ``SETUP.md``.
"""

from __future__ import annotations

__version__ = "1.0.0"

from . import boolean, bb84, complexnum, linalg, photon, probability, quantum, viz  # noqa: F401

__all__ = [
    "boolean",
    "bb84",
    "complexnum",
    "linalg",
    "photon",
    "probability",
    "quantum",
    "viz",
]
