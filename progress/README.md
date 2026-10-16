# Recorded progress

This directory holds the machine-readable results of your work. Both files
are **personal** and are deliberately not tracked in git.

| File | Written by | Contents |
|---|---|---|
| `lab_results.json` | `python tools/labcheck.py --save` | per-lab pass/fail, check counts, runtime |
| `quiz_results.json` | `python tools/quiz.py` | per-section question counts, correct answers, score |

Read them back with:

```bash
python tools/progress.py          # a human-readable dashboard
python tools/progress.py --json   # the raw numbers
python tools/progress.py --reset  # delete both files and start over
```

`tools/labcheck.py --save` and `tools/quiz.py` create these files on first
run, so you never have to create them by hand.
