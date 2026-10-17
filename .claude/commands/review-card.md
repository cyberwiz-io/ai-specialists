---
description: Run the structural check, fixture evals and safeguard review on one specialist card
argument-hint: <family/slug>
allowed-tools: Bash(python3 -B scripts/pack.py:*), Bash(python3 -B scripts/evals.py:*), Read, Agent
---

Review the card with role ID `$ARGUMENTS` (for example `security/threat-modeler`). If no ID is given or it is unknown, run `python3 -B scripts/pack.py find <words>` and ask which one.

## 1. Structural check
Run `python3 -B scripts/pack.py check`. Report any failure that names this card's file.

## 2. Fixture eval (graded against the card's Acceptance line)
Follow `.claude/skills/card-evals/SKILL.md` for this one role: `python3 -B scripts/evals.py prepare --run <date>-<slug> --host "Claude Code (cloud)" --model "<model as the host reports it>" --role $ARGUMENTS`, then a fresh `card-eval-subject` and a fresh `card-eval-grader` subagent per fixture, then `status` and `report`. Run files stay under the ignored `work/evals/`; nothing is committed. Summarize the report's outcome per fixture and quote the evidence for any non-pass. Say whether a failure points at the card's wording or at the fixture.

## 3. Safeguard and content review
Run the `card-reviewer` agent on `catalog/<family>/<slug>.md` and include its findings (blocking, should fix, optional).

## 4. Report
Lead with a one-line verdict, then three labeled sections: **Structural check**, **Fixture eval (model-graded, one run)**, **Paper review**. State plainly that none of these is host-compatibility evidence, subject-expert review, independent review, or a comparison with a generalist, and that one subagent run per scenario shows nothing about reliability. Do not edit the card unless the user asks; propose exact edits instead.
