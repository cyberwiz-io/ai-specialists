---
description: Run the structural check, fixture evals and safeguard review on one specialist card
argument-hint: <family/slug>
allowed-tools: Bash(python3 -B scripts/pack.py:*), Bash(python3 -B scripts/evals.py:*), Bash(mkdir:*), Read, Write, Agent
---

Review the card with role ID `$ARGUMENTS` (for example `security/threat-modeler`). If no ID is given or it is unknown, run `python3 -B scripts/pack.py find <words>` and ask which one.

## 1. Structural check
Run `python3 -B scripts/pack.py check`. Report any failure that names this card's file.

## 2. Fixture evals (keyword rules; a smoke test)
1. `python3 -B scripts/evals.py list $ARGUMENTS` shows the scenarios that apply.
2. For each scenario `<s>`: get the text with `python3 -B scripts/evals.py prompt $ARGUMENTS <s>`. Start a fresh `general-purpose` Agent whose prompt is exactly that text, and tell it to answer the USER REQUEST using only the instructions above it and to run no tools. Save its reply to `work/evals/<family>-<slug>/<s>.md` (create the folder; `work/` is gitignored and nothing here is committed).
3. Grade it: `python3 -B scripts/evals.py grade $ARGUMENTS <s> work/evals/<family>-<slug>/<s>.md`.
4. List per scenario PASS or the printed reasons. Quote the offending line of the reply for any failure, and say whether the fault is the card's wording or only the keyword rule being too narrow.

## 3. Safeguard and content review
Run the `card-reviewer` agent on `catalog/<family>/<slug>.md` and include its findings (blocking, should fix, optional).

## 4. Report
Lead with a one-line verdict, then three labeled sections: **Structural check**, **Fixture evals (keyword rules, one run each)**, **Paper review**. State plainly that none of these is host-compatibility evidence, subject-expert review, independent review, or a comparison with a generalist, and that one subagent run per scenario shows nothing about reliability. Do not edit the card unless the user asks; propose exact edits instead.
