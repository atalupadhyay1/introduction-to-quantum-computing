# Appendix

Three reference sections:

- [Formula sheet](formula-sheet.md) — every equation the course uses, on one
  page.
- [Glossary](glossary.md) — the vocabulary, in one place.
- [API reference](api-reference.md) — the shared `qc101` library that every
  lab is built on.

## Reading order for the appendix

If you are revising for an exam, read the **formula sheet** first, then
skim the **glossary** for terms you could not define, then use the **API
reference** as a lookup while you work through the labs.

## Everything in one place

| Topic | Where |
|---|---|
| The 17 course sections | [the index](../index.md) |
| Chapter guides | [`docs/`](../) |
| Runnable labs | [`labs/`](../labs/) |
| The shared library | [`labs/common/qc101/`](../labs/common/qc101/) |
| Q# program | [`qsharp/QB4/`](../qsharp/QB4/) |
| Quizzes | [`quizzes/`](../quizzes/) |
| The study site | [`site/`](../site/) |
| Notebooks | [`notebooks/`](../notebooks/) |

## A note on accuracy

Every number quoted in this package was produced by running the code in
this repository, not by transcribing the course's slides. The labs are
auto-graded, and `python tools/labcheck.py` re-checks all 350 assertions,
so if you change a library and break something, the runner will tell you.

The derivations that are *not* in the course videos but were needed to make
the quantum KNN work are written out in
[chapter 17](../17-quantum-ml.md) and in
[`docs/17-quantum-ml.md`](../17-quantum-ml.md).
