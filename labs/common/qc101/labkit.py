"""
A tiny lab harness.

Every lab in this repository follows the same shape::

    from qc101.labkit import Lab

    lab = Lab("L03", "Boolean algebra and logic gates")
    lab.section("1. Truth tables")
    lab.check("AND truth table matches", ...)
    lab.note("NAND is universal because ...")
    lab.finish()

``lab.finish()`` prints a summary and returns a process exit code, so a
lab can be run standalone (``python lab.py``) or by ``tools/labcheck.py``.
"""

from __future__ import annotations

import sys
import time
import traceback
from typing import Any, Callable, List, Optional

__all__ = ["Lab", "CheckResult"]


class CheckResult:
    """The outcome of a single check."""

    def __init__(self, name: str, passed: bool, detail: str = ""):
        self.name = name
        self.passed = passed
        self.detail = detail

    def __str__(self) -> str:
        mark = "PASS" if self.passed else "FAIL"
        suffix = f"  -- {self.detail}" if self.detail else ""
        return f"  [{mark}] {self.name}{suffix}"


class Lab:
    """
    A self-checking lab session.

    Parameters
    ----------
    code:
        Short lab code, e.g. ``"L03"``.
    title:
        Human-readable title.
    verbose:
        When True, notes and extra output are printed as they happen.
    """

    def __init__(self, code: str, title: str, verbose: bool = True):
        self.code = code
        self.title = title
        self.verbose = verbose
        self.checks: List[CheckResult] = []
        self.notes: List[str] = []
        self._section = ""
        self._started = time.time()

    # -- structure --------------------------------------------------------
    def section(self, title: str) -> None:
        """Start a new numbered section of the lab."""
        self._section = title
        if self.verbose:
            print()
            print("=" * 72)
            print(f"  {self.code}  |  {title}")
            print("=" * 72)

    def step(self, text: str) -> None:
        """Print an experiment step."""
        if self.verbose:
            print(f"\n-- {text}")

    def note(self, text: str) -> None:
        """Record (and optionally print) an explanatory note."""
        self.notes.append(text)
        if self.verbose:
            print(f"   {text}")

    def show(self, text: str) -> None:
        """Print raw output (a table, a matrix, a histogram)."""
        if self.verbose:
            print(text)

    # -- checking ---------------------------------------------------------
    def check(self, name: str, condition: Any, detail: str = "") -> bool:
        """
        Record a check.  ``condition`` may be a bool or a callable returning
        a bool.  Returns the boolean outcome so it can be chained.
        """
        if callable(condition):
            try:
                passed = bool(condition())
            except Exception as exc:  # pragma: no cover - defensive
                passed = False
                detail = f"{detail} (raised {exc!r})".strip()
        else:
            passed = bool(condition)
        self.checks.append(CheckResult(name, passed, detail))
        if self.verbose:
            print(CheckResult(name, passed, detail))
        return passed

    def check_close(self, name: str, got, expected, tol: float = 1e-6, detail: str = "") -> bool:
        """Check that ``got`` is within ``tol`` of ``expected``.

        Works for scalars and for (nested) sequences of numbers.
        """
        if isinstance(got, (list, tuple)) and isinstance(expected, (list, tuple)):
            ok = len(got) == len(expected) and all(
                abs(g - e) <= tol for g, e in zip(got, expected)
            )
        else:
            ok = abs(got - expected) <= tol
        d = detail or f"got {got!r}, expected {expected!r} (tol {tol})"
        return self.check(name, ok, d)

    def check_equal(self, name: str, got: Any, expected: Any, detail: str = "") -> bool:
        """Check exact equality of two values."""
        ok = got == expected
        d = detail or f"got {got!r}, expected {expected!r}"
        return self.check(name, ok, d)

    def error(self, message: str) -> None:
        """Record a fatal problem with the lab."""
        self.check("lab completed without errors", False, message)

    # -- finishing --------------------------------------------------------
    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed(self) -> int:
        return sum(1 for c in self.checks if not c.passed)

    def summary(self) -> str:
        """A one-paragraph summary of the lab."""
        elapsed = time.time() - self._started
        return (
            f"{self.code} {self.title}: {self.passed} passed, {self.failed} failed "
            f"({len(self.checks)} checks, {elapsed:.2f}s)"
        )

    def finish(self) -> int:
        """
        Print the final summary.  Returns 0 when every check passed and 1
        otherwise, so the lab can be used as a script.
        """
        elapsed = time.time() - self._started
        print()
        print("-" * 72)
        status = "ALL CHECKS PASSED" if self.failed == 0 else f"{self.failed} CHECK(S) FAILED"
        print(f"{self.code} {self.title}: {self.passed}/{len(self.checks)} checks passed  [{status}, {elapsed:.2f}s]")
        print("-" * 72)
        if self.failed:
            for c in self.checks:
                if not c.passed:
                    print(f"  FAILED: {c.name} -- {c.detail}")
        return 0 if self.failed == 0 else 1


def run_section(title: str, body: Callable[[], None]) -> None:
    """Helper for wrapping a section body in a try/except."""
    print(f"\n-- {title}")
    try:
        body()
    except Exception:
        traceback.print_exc()
        raise
