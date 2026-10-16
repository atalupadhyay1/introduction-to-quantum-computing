#!/usr/bin/env python3
"""
Site integrity check.

Verifies that the study site in ``site/`` is complete and self-consistent.
Pure standard library -- no Node, no npm, no network.

    python tools/site_check.py
    python tools/site_check.py --verbose
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
CONTENT = SITE / "content"
DOCS = ROOT / "docs"
QUIZZES = ROOT / "quizzes" / "questions"

REQUIRED_FILES = [
    "index.html",
    "assets/style.css",
    "assets/app.js",
    "assets/widgets.js",
    "vendor/katex/katex.min.css",
    "vendor/katex/katex.min.js",
    "vendor/katex/contrib/auto-render.min.js",
    "content/manifest.json",
]

EXPECTED_CHAPTERS = 17
EXPECTED_APPENDIX = 4

# Routes the single-page app knows about.  Every one of them must be
# reachable from the manifest and from the chapter list.
APP_ROUTES = [
    "#/welcome",
    "#/chapters",
    "#/playground",
    "#/quiz",
    "#/progress",
]


class Checker:
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self.problems: List[str] = []
        self.passed = 0

    def check(self, ok: bool, label: str, detail: str = "") -> bool:
        if ok:
            self.passed += 1
            if self.verbose:
                print(f"  [PASS] {label}" + (f"  -- {detail}" if detail else ""))
        else:
            self.problems.append(label + (f" -- {detail}" if detail else ""))
            print(f"  [FAIL] {label}" + (f"  -- {detail}" if detail else ""))
        return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    c = Checker(args.verbose)

    # ---------------------------------------------------------------- files
    print("Site files")
    for rel in REQUIRED_FILES:
        c.check((SITE / rel).is_file(), f"{rel} exists")
    if not CONTENT.is_dir():
        print("\n  site/content is missing -- run `make site` first.")
        return 1

    # ------------------------------------------------------------ manifest
    print("\nManifest")
    try:
        manifest = json.loads((CONTENT / "manifest.json").read_text())
    except Exception as exc:  # pragma: no cover
        print(f"  [FAIL] manifest.json is not valid JSON -- {exc}")
        return 1

    sections = manifest.get("sections", [])
    appendix = manifest.get("appendix", [])
    c.check(len(sections) == EXPECTED_CHAPTERS,
            f"manifest lists {EXPECTED_CHAPTERS} chapters",
            f"found {len(sections)}")
    c.check(len(appendix) == EXPECTED_APPENDIX,
            f"manifest lists {EXPECTED_APPENDIX} appendix pages",
            f"found {len(appendix)}")
    c.check([s["number"] for s in sections] == list(range(1, EXPECTED_CHAPTERS + 1)),
            "chapters are numbered 1..17 with no gaps")

    # every chapter page exists and is non-trivial
    for section in sections:
        page = CONTENT / "chapters" / f"{section['slug']}.html"
        ok = page.is_file() and page.stat().st_size > 500
        c.check(ok, f"chapter page {section['slug']}.html is built",
                "missing or too small" if not ok else f"{page.stat().st_size} bytes")

    for page_info in appendix:
        page = CONTENT / "chapters" / f"{page_info['slug']}.html"
        ok = page.is_file() and page.stat().st_size > 200
        c.check(ok, f"appendix page {page_info['slug']}.html is built")

    # --------------------------------------------------------------- docs
    print("\nSource documents")
    md_files = sorted(DOCS.glob("[0-9][0-9]-*.md"))
    c.check(len(md_files) == EXPECTED_CHAPTERS,
            f"docs/ holds {EXPECTED_CHAPTERS} chapter markdown files",
            f"found {len(md_files)}")
    for path in md_files:
        text = path.read_text()
        c.check(len(text) > 800, f"{path.name} has real content",
                f"{len(text)} chars")
    c.check((DOCS / "index.md").is_file(), "docs/index.md exists")
    for name in ("appendix", "formula-sheet", "glossary", "api-reference"):
        c.check((DOCS / "appendix" / f"{name}.md").is_file(),
                f"docs/appendix/{name}.md exists")

    # ------------------------------------------------------------- quizzes
    print("\nQuiz bank")
    quiz_files = sorted(QUIZZES.glob("section_*.json"))
    c.check(len(quiz_files) == EXPECTED_CHAPTERS,
            f"one quiz file per section ({EXPECTED_CHAPTERS})",
            f"found {len(quiz_files)}")
    total = 0
    bad_answers = 0
    for path in quiz_files:
        questions = json.loads(path.read_text())
        total += len(questions)
        for q in questions:
            kind = q.get("type", "single")
            n = len(q.get("choices", []))
            if kind == "multi":
                if not all(0 <= a < n for a in q.get("answer", [])):
                    bad_answers += 1
            elif kind in ("single",):
                if not (0 <= int(q.get("answer", -1)) < n):
                    bad_answers += 1
            elif kind == "truefalse":
                if str(q.get("answer", "")).lower() not in ("true", "false"):
                    bad_answers += 1
            elif kind == "number":
                try:
                    float(q.get("answer"))
                except (TypeError, ValueError):
                    bad_answers += 1
            else:
                bad_answers += 1
    c.check(total == manifest.get("questionCount", total),
            "manifest question count matches the bank",
            f"bank has {total}, manifest says {manifest.get('questionCount')}")
    c.check(total >= 100, "the bank has at least 100 questions", f"{total}")
    c.check(bad_answers == 0, "every answer index is in range",
            f"{bad_answers} bad answers")

    # ------------------------------------------------------------- routes
    print("\nRouting")
    index_html = (SITE / "index.html").read_text()
    app_js = (SITE / "assets" / "app.js").read_text()
    for route in APP_ROUTES:
        c.check(route.lstrip("#/") in app_js or route in app_js,
                f"the app knows the {route} route")
    c.check("katex" in index_html.lower(), "index.html loads KaTeX")
    c.check("widgets.js" in index_html and "app.js" in index_html,
            "index.html loads app.js and widgets.js")
    c.check(not re.search(r'<(script|link)[^>]+(src|href)="https?://', index_html),
            "index.html loads nothing from a CDN (fully offline)")

    # ------------------------------------------------------------- widgets
    print("\nWidgets")
    widgets_js = (SITE / "assets" / "widgets.js").read_text()
    for name in ("bloch", "gates", "polarizer", "bb84", "bell", "knn",
                 "twoQubit", "period"):
        c.check(re.search(rf"\b{name}\s*:\s*\w+Widget", widgets_js) is not None,
                f"the {name} widget is registered")

    # ---------------------------------------------------------- js syntax
    if shutil.which("node"):
        print("\nJavaScript syntax")
        for rel in ("assets/app.js", "assets/widgets.js"):
            proc = subprocess.run(["node", "--check", str(SITE / rel)],
                                  capture_output=True, text=True)
            c.check(proc.returncode == 0, f"{rel} parses",
                    proc.stderr.strip().splitlines()[0] if proc.returncode else "")

    # ------------------------------------------------------------- summary
    total_checks = c.passed + len(c.problems)
    print("\n" + "-" * 72)
    if c.problems:
        print(f"Site check FAILED: {len(c.problems)} of {total_checks} problems")
        for problem in c.problems:
            print(f"  - {problem}")
        return 1
    print(f"Site check passed: {c.passed}/{total_checks} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
