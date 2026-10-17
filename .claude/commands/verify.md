---
description: Rebuild generated files, then run the pack check and unit tests
allowed-tools: Bash(python3 -B scripts/pack.py:*), Bash(python3 -B scripts/evals.py:*), Bash(python3 -B -m unittest:*)
---

Run these in order from the repository root and stop at the first failure:

1. `python3 -B scripts/pack.py build`
2. `python3 -B scripts/pack.py check`
3. `python3 -B -m unittest discover -s tests`

On success, report the PASS line and the test count. On failure, quote the failing lines verbatim, name the source file to edit (never a generated file), fix it, and rerun from step 1. Do not commit.
