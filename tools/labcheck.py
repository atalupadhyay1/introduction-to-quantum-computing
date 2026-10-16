#!/usr/bin/env python3
"""
Run every QC101 lab and report a pass/fail summary.

Usage::

    python tools/labcheck.py                 # run everything
    python tools/labcheck.py L03 L07         # run only those labs
    python tools/labcheck.py --list          # list the labs
    python tools/labcheck.py -v L12          # verbose output
    python tools/labcheck.py --quiet         # only print the summary
    python tools/labcheck.py --save          # also record the results

Exit code 0 when every lab passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABS_DIR = ROOT / "labs"

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


def colour(text: str, code: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{code}{text}{RESET}"


def discover_labs() -> list[Path]:
    """Find every ``labs/L*/lab.py``."""
    return sorted(p for p in LABS_DIR.glob("L*/lab.py"))


def lab_code(path: Path) -> str:
    """Extract the ``L03`` style code from a lab path."""
    m = re.match(r"(L\d+)", path.parent.name)
    return m.group(1) if m else path.parent.name


def run_lab(path: Path, verbose: bool) -> tuple[bool, str, float]:
    """
    Run one lab as a **subprocess**, exactly the way a student would.

    Running out-of-process isolates crashes and lets us capture the lab's
    own one-line summary.

    Returns ``(passed, summary_line, seconds)``.
    """
    started = time.time()
    cmd = [sys.executable, str(path)]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=900,
        )
    except subprocess.TimeoutExpired:
        return False, "timed out", time.time() - started

    elapsed = time.time() - started
    output = (proc.stdout or "") + (proc.stderr or "")
    summary = last_summary_line(output)

    if verbose and output:
        sys.stdout.write(output)
    if not summary:
        tail = [ln for ln in output.strip().splitlines() if ln.strip()]
        summary = tail[-1] if tail else f"exit code {proc.returncode}"
    return proc.returncode == 0, summary, elapsed


def last_summary_line(output: str) -> str:
    """Find the lab's one-line summary in its output."""
    for line in reversed(output.splitlines()):
        if re.match(r"^L\d+\s", line.strip()) and "check" in line:
            return line.strip()
    return ""


def save_results(records: list[dict]) -> None:
    """Record this run so that ``tools/progress.py`` can report on it."""
    progress_dir = ROOT / "progress"
    progress_dir.mkdir(parents=True, exist_ok=True)
    path = progress_dir / "lab_results.json"
    history = []
    if path.exists():
        try:
            with path.open(encoding="utf-8") as handle:
                history = json.load(handle)
        except json.JSONDecodeError:
            history = []
    history.append({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "labs": records,
    })
    with path.open("w", encoding="utf-8") as handle:
        json.dump(history, handle, indent=2)
    print(f"results saved to {path.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the QC101 labs.")
    parser.add_argument("codes", nargs="*", help="lab codes to run, e.g. L03 L07")
    parser.add_argument("--list", action="store_true", help="list the available labs")
    parser.add_argument("-v", "--verbose", action="store_true", help="show each lab's output")
    parser.add_argument("-q", "--quiet", action="store_true", help="only print the summary")
    parser.add_argument("--save", action="store_true",
                        help="write the results to progress/lab_results.json")
    args = parser.parse_args()

    labs = discover_labs()
    if args.list:
        for path in labs:
            print(f"{lab_code(path):<6} {path.parent.name}")
        return 0

    if args.codes:
        wanted = {c.upper() for c in args.codes}
        labs = [p for p in labs if lab_code(p) in wanted]
        if not labs:
            print(f"No labs matched {args.codes}.  Try --list.", file=sys.stderr)
            return 1

    print(colour(f"{BOLD}QC101 lab runner{RESET}  ({len(labs)} labs)\n", ""))
    print(f"{'LAB':<6} {'RESULT':<10} {'TIME':<8} SUMMARY")
    print("-" * 78)

    failures = []
    total_checks = 0
    records = []
    for path in labs:
        code = lab_code(path)
        passed, summary, elapsed = run_lab(path, args.verbose)
        m = re.search(r"(\d+)/(\d+) checks", summary)
        if m:
            total_checks += int(m.group(2))
        records.append({
            "code": code,
            "name": path.parent.name,
            "status": "PASS" if passed else "FAIL",
            "checks": int(m.group(1)) if m else 0,
            "total": int(m.group(2)) if m else 0,
            "seconds": round(elapsed, 2),
        })
        status = colour("PASS", GREEN) if passed else colour("FAIL", RED)
        print(f"{code:<6} {status:<10} {elapsed:>6.2f}s  {summary}")
        if not passed:
            failures.append((code, summary))

    print("-" * 78)
    if failures:
        print(colour(f"{RED}{len(failures)} lab(s) FAILED{RESET}", RED))
        for code, summary in failures:
            print(f"  {code}: {summary}")
        if args.save:
            save_results(records)
        return 1
    print(colour(f"{GREEN}All {len(labs)} labs passed{RESET}"
                 + (f" ({total_checks} checks)" if total_checks else ""), GREEN))
    if args.save:
        save_results(records)
    return 0


if __name__ == "__main__":
    sys.exit(main())
