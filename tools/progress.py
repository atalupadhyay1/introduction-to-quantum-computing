#!/usr/bin/env python3
"""
Track your progress through the QC101 study package.

The progress report is built from two sources:

* ``progress/quiz_results.json`` -- written by ``tools/quiz.py``;
* ``progress/lab_results.json`` -- written by ``tools/labcheck.py --save``.

Run it::

    python tools/progress.py            # the report
    python tools/progress.py --reset    # start over
    python tools/progress.py --json     # machine readable

Everything is stored under ``progress/`` which is deliberately kept out of
git (see ``.gitignore``), because it is personal to you.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROGRESS_DIR = ROOT / "progress"
QUIZ_RESULTS = PROGRESS_DIR / "quiz_results.json"
LAB_RESULTS = PROGRESS_DIR / "lab_results.json"

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

SECTION_TITLES = {
    1: "Introduction",
    2: "Quantum Physics Through Photon Polarization",
    3: "Math Foundation",
    4: "Quantum Cryptography",
    5: "A Math Model for Quantum Physics",
    6: "Quantum Physics of Spin States",
    7: "Modeling Spin States with Math",
    8: "Reversible and Irreversible Transformations",
    9: "Multi-Qubit Systems",
    10: "Entanglement",
    11: "Superposition and Entanglement Simulators",
    12: "Quantum Computing Model",
    13: "Microsoft Q# Programming",
    14: "IBM Quantum Experience",
    15: "IBM Qiskit: Programming and Algorithms",
    16: "Machine Learning Foundation",
    17: "Quantum Machine Learning with Qiskit",
}

SECTION_LAB = {
    1: "L01", 2: "L02", 3: "L03-L06", 4: "L07", 5: "L08", 6: "L09",
    7: "L10", 8: "L11", 9: "L11", 10: "L11", 11: "L12", 12: "L13",
    13: "L14", 14: "L15", 15: "L15", 16: "L16", 17: "L17",
}


def colour(text: str, code: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{code}{text}{RESET}"


def load(path: Path) -> list:
    if not path.exists():
        return []
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return []


def quiz_stats() -> dict[int, dict]:
    """Best and latest quiz score per section."""
    history = load(QUIZ_RESULTS)
    best: dict[int, dict] = {}
    for run in history:
        results = run.get("results", [])
        for entry in results:
            section = entry.get("section", 0)
            stats = best.setdefault(section, {"correct": 0, "total": 0, "runs": 0})
            stats["correct"] += 1 if entry.get("correct") else 0
            stats["total"] += 1
        for section in {e.get("section", 0) for e in results}:
            best.setdefault(section, {"correct": 0, "total": 0, "runs": 0})
            best[section]["runs"] += 1
    return best


def lab_stats() -> dict[str, dict]:
    history = load(LAB_RESULTS)
    latest: dict[str, dict] = {}
    for run in history:
        for entry in run.get("labs", []):
            latest[entry.get("code", "?")] = entry
    return latest


def bar(fraction: float, width: int = 24) -> str:
    filled = int(round(fraction * width))
    return "#" * filled + "." * (width - filled)


def build_report() -> dict:
    quizzes = quiz_stats()
    labs = lab_stats()
    sections = []
    for section in sorted(SECTION_TITLES):
        q = quizzes.get(section, {"correct": 0, "total": 0, "runs": 0})
        sections.append({
            "section": section,
            "title": SECTION_TITLES[section],
            "lab": SECTION_LAB.get(section, ""),
            "quiz_correct": q["correct"],
            "quiz_total": q["total"],
            "quiz_runs": q["runs"],
        })
    lab_list = sorted(labs.values(), key=lambda entry: entry.get("code", ""))
    return {"sections": sections, "labs": lab_list}


def print_report(report: dict) -> None:
    print()
    print(colour(f"{BOLD}QC101 progress report{RESET}", ""))
    print("=" * 74)

    print()
    print(colour(f"{BOLD}Quizzes{RESET}", ""))
    print(f"{'SEC':<5}{'SCORE':<12}{'BAR':<26}{'SECTION'}")
    print("-" * 74)
    answered = 0
    correct = 0
    for entry in report["sections"]:
        total = entry["quiz_total"]
        got = entry["quiz_correct"]
        answered += total
        correct += got
        fraction = got / total if total else 0.0
        score = f"{got}/{total}" if total else "-"
        bar_text = bar(fraction) if total else " " * 24
        colour_bar = colour(bar_text, GREEN if fraction >= 0.8 else
                            (YELLOW if fraction >= 0.6 else RED))
        print(f"{entry['section']:<5}{score:<12}{colour_bar:<32}"
              f"{entry['title'][:30]}")
    print("-" * 74)
    fraction = correct / answered if answered else 0.0
    print(f"{'ALL':<5}{f'{correct}/{answered}':<12}{colour(bar(fraction), GREEN):<32}"
          f"{'overall'}")

    if report["labs"]:
        print()
        print(colour(f"{BOLD}Labs{RESET}", ""))
        print(f"{'LAB':<8}{'CHECKS':<14}{'RESULT'}")
        print("-" * 74)
        for entry in report["labs"]:
            checks = entry.get("checks", 0)
            total = entry.get("total", checks)
            status = entry.get("status", "unknown")
            colour_status = colour(status, GREEN if status == "PASS" else RED)
            print(f"{entry.get('code', '?'):<8}{f'{checks}/{total}':<14}{colour_status}")
        print("-" * 74)

    print()
    remaining = [e for e in report["sections"] if e["quiz_total"] == 0]
    if remaining:
        print(colour(f"{len(remaining)} section(s) still need a quiz attempt:", YELLOW))
        for entry in remaining:
            print(f"  section {entry['section']:>2}  {entry['title']}")
    else:
        print(colour("Every section has a quiz attempt on record.", GREEN))
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="QC101 progress report.")
    parser.add_argument("--reset", action="store_true",
                        help="delete the saved progress and start over")
    parser.add_argument("--json", action="store_true",
                        help="print the report as JSON")
    args = parser.parse_args()

    if args.reset:
        for path in (QUIZ_RESULTS, LAB_RESULTS):
            if path.exists():
                path.unlink()
                print(f"removed {path.relative_to(ROOT)}")
        print("progress reset")
        return 0

    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
