#!/usr/bin/env python3
"""
The QC101 quiz engine.

Every question lives in ``quizzes/questions/<section>.json`` and looks like
this::

    {
      "id": "s03-q01",
      "section": 3,
      "type": "single",            # single | multi | truefalse | number | text
      "question": "What is i^2?",
      "choices": ["-1", "1", "i", "-i"],
      "answer": 0,                  # index for single, list of indices for multi
      "explanation": "i^2 = -1 by definition.",
      "difficulty": 1               # 1 easy, 2 medium, 3 hard
    }

Run it::

    python tools/quiz.py                 # quiz on every section
    python tools/quiz.py 3 7             # quiz on sections 3 and 7
    python tools/quiz.py --section 12 -n 5
    python tools/quiz.py --list
    python tools/quiz.py --all           # every question, no limit
    python tools/quiz.py --markdown      # emit the questions as markdown

The quiz writes its results to ``progress/quiz_results.json`` so that
``tools/progress.py`` can turn them into a progress report.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = ROOT / "quizzes" / "questions"
PROGRESS_DIR = ROOT / "progress"
RESULTS_FILE = PROGRESS_DIR / "quiz_results.json"

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

SECTION_TITLES = {
    1: "Introduction",
    2: "Quantum Physics Through Photon Polarization",
    3: "Math Foundation: Complex Numbers, Probability, Linear Algebra & Logic",
    4: "Quantum Cryptography",
    5: "Developing a Math Model for Quantum Physics",
    6: "Quantum Physics of Spin States",
    7: "Modeling Quantum Spin States with Math",
    8: "Reversible and Irreversible State Transformations",
    9: "Multi-Qubit Systems",
    10: "Entanglement",
    11: "Understanding Superposition and Entanglement With Quantum Simulators",
    12: "Quantum Computing Model",
    13: "Quantum Programming with Microsoft Q#",
    14: "IBM Quantum Experience",
    15: "Quantum Programming and Algorithms With IBM Qiskit",
    16: "Machine Learning Foundation",
    17: "Quantum Machine Learning With Qiskit",
}


def colour(text: str, code: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{code}{text}{RESET}"


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_questions(section: int | None = None) -> list[dict]:
    """Load every question, or only those of one section."""
    questions: list[dict] = []
    if not QUESTIONS_DIR.is_dir():
        return questions
    for path in sorted(QUESTIONS_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        for question in data:
            if section is None or question.get("section") == section:
                questions.append(question)
    return questions


def available_sections() -> list[int]:
    return sorted({q.get("section", 0) for q in load_questions()})


# ---------------------------------------------------------------------------
# Grading
# ---------------------------------------------------------------------------
def grade(question: dict, answer) -> bool:
    """Is this answer correct?"""
    expected = question.get("answer")
    kind = question.get("type", "single")

    if kind == "multi":
        if not isinstance(answer, (list, tuple)):
            answer = [answer] if answer is not None else []
        return sorted(int(a) for a in answer) == sorted(int(a) for a in expected)
    if kind == "number":
        try:
            return abs(float(answer) - float(expected)) <= float(
                question.get("tolerance", 1e-6))
        except (TypeError, ValueError):
            return False
    if kind == "text":
        return str(answer).strip().lower() == str(expected).strip().lower()
    if kind == "truefalse":
        return str(answer).strip().lower() == str(expected).strip().lower()
    return int(answer) == int(expected)


def read_answer(question: dict) -> object:
    """Ask the user for an answer and return it in the question's own type."""
    kind = question.get("type", "single")
    choices = question.get("choices", [])

    if kind == "single":
        for i, choice in enumerate(choices):
            print(f"    {chr(ord('A') + i)}) {choice}")
        raw = input("    Your answer (letter): ").strip().upper()
        if not raw:
            return None
        if raw.isdigit():
            index = int(raw) - 1
        else:
            index = ord(raw[0]) - ord("A")
        return index if 0 <= index < len(choices) else None

    if kind == "multi":
        for i, choice in enumerate(choices):
            print(f"    {chr(ord('A') + i)}) {choice}")
        raw = input("    Your answers (letters, comma separated): ").strip().upper()
        picked = []
        for piece in raw.replace(" ", "").split(","):
            if not piece:
                continue
            index = int(piece) - 1 if piece.isdigit() else ord(piece[0]) - ord("A")
            if 0 <= index < len(choices):
                picked.append(index)
        return picked

    if kind == "truefalse":
        print("    (T)rue or (F)alse?")
        raw = input("    Your answer: ").strip().lower()
        return raw[0] if raw else None

    if kind == "number":
        return input("    Your answer: ").strip()

    return input("    Your answer: ").strip()


def explain(question: dict, answer, correct: bool) -> str:
    """Render the feedback block for one question."""
    lines = []
    if correct:
        lines.append(colour("  [PASS]", GREEN))
    else:
        lines.append(colour("  [FAIL]", RED))
        expected = question.get("answer")
        kind = question.get("type", "single")
        choices = question.get("choices", [])
        if kind == "multi" and isinstance(expected, (list, tuple)):
            expected = ", ".join(choices[i] for i in expected)
        elif kind in ("single", "truefalse") and isinstance(expected, int) \
                and 0 <= expected < len(choices):
            expected = choices[expected]
        lines.append(f"  expected: {expected}")
        if question.get("type") == "single" and isinstance(answer, int) \
                and 0 <= answer < len(choices):
            lines.append(f"  you said : {choices[answer]}")
    if question.get("explanation"):
        lines.append(f"  {question['explanation']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
def record_results(results: list[dict]) -> None:
    """Append this run to ``progress/quiz_results.json``."""
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    history = []
    if RESULTS_FILE.exists():
        try:
            with RESULTS_FILE.open(encoding="utf-8") as handle:
                history = json.load(handle)
        except json.JSONDecodeError:
            history = []
    history.append({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "results": results,
    })
    with RESULTS_FILE.open("w", encoding="utf-8") as handle:
        json.dump(history, handle, indent=2)


# ---------------------------------------------------------------------------
# Markdown export
# ---------------------------------------------------------------------------
def to_markdown(questions: list[dict]) -> str:
    """Render the question bank as a markdown study sheet."""
    out = ["# QC101 quiz bank", ""]
    by_section: dict[int, list[dict]] = {}
    for question in questions:
        by_section.setdefault(question.get("section", 0), []).append(question)
    for section in sorted(by_section):
        title = SECTION_TITLES.get(section, f"Section {section}")
        out.append(f"## Section {section} -- {title}")
        out.append("")
        for number, question in enumerate(by_section[section], start=1):
            out.append(f"**{section}.{number}.** {question['question']}")
            out.append("")
            for i, choice in enumerate(question.get("choices", [])):
                marker = "x" if i in _as_indices(question) else " "
                out.append(f"- [{marker}] {choice}")
            if not question.get("choices"):
                out.append(f"- *answer:* `{question.get('answer')}`")
            out.append("")
            if question.get("explanation"):
                out.append(f"> {question['explanation']}")
                out.append("")
    return "\n".join(out)


def _as_indices(question: dict) -> list[int]:
    answer = question.get("answer")
    if isinstance(answer, (list, tuple)):
        return [int(a) for a in answer]
    if isinstance(answer, int) and question.get("type") in ("single", "multi"):
        return [answer]
    return []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="Run the QC101 quizzes.")
    parser.add_argument("sections", nargs="*", type=int,
                        help="section numbers to quiz (default: everything)")
    parser.add_argument("-n", "--count", type=int, default=5,
                        help="questions per section (default 5)")
    parser.add_argument("-s", "--section", type=int, help="quiz a single section")
    parser.add_argument("--all", action="store_true",
                        help="ask every question in the section")
    parser.add_argument("--list", action="store_true",
                        help="list the sections that have questions")
    parser.add_argument("--markdown", action="store_true",
                        help="print the question bank as markdown and exit")
    parser.add_argument("--seed", type=int, help="seed the question shuffle")
    args = parser.parse_args()

    if args.list:
        for section in available_sections():
            count = len(load_questions(section))
            print(f"  section {section:>2}  {count:>3} questions  "
                  f"{SECTION_TITLES.get(section, '')}")
        return 0

    if args.markdown:
        print(to_markdown(load_questions()))
        return 0

    sections = args.sections or ([args.section] if args.section else available_sections())
    rng = random.Random(args.seed)

    total = 0
    correct_total = 0
    per_section = []
    all_results = []

    for section in sections:
        pool = load_questions(section)
        if not pool:
            print(colour(f"No questions for section {section}.", YELLOW))
            continue
        if args.all:
            picked = pool
        else:
            picked = rng.sample(pool, min(args.count, len(pool)))

        title = SECTION_TITLES.get(section, "")
        print()
        print(colour(f"{BOLD}Section {section} -- {title}{RESET}", ""))
        print("=" * 72)
        section_correct = 0
        for question in picked:
            total += 1
            print()
            print(f"  {question['id']}.  {question['question']}")
            answer = read_answer(question)
            correct = grade(question, answer)
            section_correct += 1 if correct else 0
            print(explain(question, answer, correct))
            all_results.append({
                "id": question["id"],
                "section": section,
                "correct": correct,
            })
        pct = 100 * section_correct / len(picked)
        print()
        print(colour(f"  section {section}: {section_correct}/{len(picked)} correct "
                     f"({pct:.0f}%)", GREEN if pct >= 60 else RED))
        per_section.append((section, section_correct, len(picked)))
        correct_total += section_correct

    print()
    print("=" * 72)
    pct = 100 * correct_total / total if total else 0.0
    print(colour(f"{BOLD}Total: {correct_total}/{total} correct ({pct:.0f}%){RESET}", ""))
    for section, got, out_of in per_section:
        print(f"  section {section:>2}: {got}/{out_of}")
    print(colour(f"Results written to {RESULTS_FILE.relative_to(ROOT)}", DIM))

    record_results(all_results)
    return 0 if pct >= 60 else 1


if __name__ == "__main__":
    sys.exit(main())
