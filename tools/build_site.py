#!/usr/bin/env python3
"""
Build the QC101 study site.

The site is a static single-page app.  This script turns the markdown in
``docs/`` into HTML, copies the quiz question bank next to it, and writes
a small JSON manifest that the app uses for its navigation.

Run it::

    python tools/build_site.py
    python -m http.server -d site 8000     # then open http://localhost:8000

Everything is written into ``site/content/`` which is generated output and
is kept out of git (see ``.gitignore``).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"
CONTENT = SITE / "content"
QUESTIONS = ROOT / "quizzes" / "questions"

SECTIONS = [
    (1, "01-introduction", "Introduction", "L01"),
    (2, "02-photon-polarization", "Quantum Physics Through Photon Polarization", "L02"),
    (3, "03-math-foundation", "Math Foundation", "L03–L06"),
    (4, "04-quantum-cryptography", "Quantum Cryptography", "L07"),
    (5, "05-math-model", "A Math Model for Quantum Physics", "L08"),
    (6, "06-spin-states", "Quantum Physics of Spin States", "L09"),
    (7, "07-modeling-spin", "Modeling Spin States with Math", "L10"),
    (8, "08-reversible-irreversible", "Reversible and Irreversible Transformations", "L11"),
    (9, "09-multi-qubit", "Multi-Qubit Systems", "L11"),
    (10, "10-entanglement", "Entanglement", "L11"),
    (11, "11-simulators", "Superposition and Entanglement Simulators", "L12"),
    (12, "12-quantum-computing-model", "The Quantum Computing Model", "L13"),
    (13, "13-qsharp", "Microsoft Q# Programming", "L14"),
    (14, "14-ibm-quantum", "IBM Quantum Experience", "L15"),
    (15, "15-qiskit", "IBM Qiskit: Programming and Algorithms", "L15"),
    (16, "16-ml-foundation", "Machine Learning Foundation", "L16"),
    (17, "17-quantum-ml", "Quantum Machine Learning with Qiskit", "L17"),
]


def render_markdown(text: str) -> str:
    """Render markdown to HTML, keeping the maths for KaTeX to pick up."""
    try:
        import markdown
    except ImportError:
        return "<pre class='raw'>" + _escape(text) + "</pre>"

    extensions = ["extra", "sane_lists", "toc", "tables", "fenced_code"]
    extension_configs = {
        "toc": {"permalink": False},
    }
    try:
        import pymdownx  # noqa: F401
        extensions += ["pymdownx.arithmatex", "pymdownx.superfences",
                       "pymdownx.details", "pymdownx.tasklist"]
        extension_configs["pymdownx.arithmatex"] = {
            "generic": True,
            "smart_dollar": True,
        }
    except ImportError:
        pass

    html = markdown.markdown(text, extensions=extensions,
                             extension_configs=extension_configs)
    # Outside the arithmatex extension, pick up any leftover $...$ and $$...$$.
    html = re.sub(r"(?<!\\)\$\$(.+?)\$\$", r"\\[\1\\]", html, flags=re.S)
    return html


def _escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build() -> int:
    if not DOCS.is_dir():
        print(f"No docs directory at {DOCS}", file=sys.stderr)
        return 1

    if CONTENT.exists():
        shutil.rmtree(CONTENT)
    (CONTENT / "chapters").mkdir(parents=True)
    (CONTENT / "quizzes").mkdir(parents=True)

    manifest = {"sections": [], "appendix": [], "generated": None}

    for number, slug, title, lab in SECTIONS:
        source = DOCS / f"{slug}.md"
        if not source.exists():
            print(f"  missing {source.name}", file=sys.stderr)
            continue
        html = render_markdown(source.read_text(encoding="utf-8"))
        (CONTENT / "chapters" / f"{slug}.html").write_text(html, encoding="utf-8")
        manifest["sections"].append({
            "number": number,
            "slug": slug,
            "title": title,
            "lab": lab,
        })

    # the appendix
    for source in sorted((DOCS / "appendix").glob("*.md")):
        html = render_markdown(source.read_text(encoding="utf-8"))
        (CONTENT / "chapters" / f"{source.stem}.html").write_text(html, encoding="utf-8")
        manifest["appendix"].append({
            "slug": source.stem,
            "title": source.stem.replace("-", " ").title(),
        })

    # the index page
    index = DOCS / "index.md"
    if index.exists():
        html = render_markdown(index.read_text(encoding="utf-8"))
        (CONTENT / "index.html").write_text(html, encoding="utf-8")

    # the quiz question bank
    total = 0
    for source in sorted(QUESTIONS.glob("*.json")):
        shutil.copy(source, CONTENT / "quizzes" / source.name)
        questions = json.loads(source.read_text(encoding="utf-8"))
        total += len(questions)

    manifest["questionCount"] = total
    (CONTENT / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"built {len(manifest['sections'])} chapters, "
          f"{len(manifest['appendix'])} appendix pages and "
          f"{total} quiz questions into {CONTENT.relative_to(ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the QC101 study site.")
    parser.parse_args()
    return build()


if __name__ == "__main__":
    sys.exit(main())
