---
description: Scaffold a new specialist card, add its manifest entry, then build and check
argument-hint: <family> <slug> "<Role name>"
allowed-tools: Bash(python3 -B scripts/pack.py:*), Bash(python3 -B scripts/evals.py:*), Bash(python3 -B -m unittest:*), Read, Edit, Write, Grep, Glob
---

Add the specialist described by `$ARGUMENTS` (family id, slug, quoted role name). Ask for any of the three that is missing or unclear.

1. **Read first.** `docs/CARD-GUIDE.md`, `catalog/<family>/INDEX.md`, one sibling card in the family as a shape example, and `catalog/families.json` for the family entry.
2. **Distinct deliverable.** Ask the user what artifact this role produces and for whom. Run `python3 -B scripts/pack.py find <words>` for look-alikes. If a sibling already produces the same artifact, stop and recommend editing that card instead (CONTRIBUTING.md: a different style is not a new role).
3. **Manifest.** Add `{"slug": ..., "name": ...}` to the family's `roles` in `catalog/families.json` and raise the top-level `total` by one. If the family lists `packs`, add the slug to exactly one pack, keeping each combined pack under 32 KB. Use a `prefix` only for the original `core` roles.
4. **Card.** Write `catalog/<family>/<slug>.md` in the exact shape from the card guide: title in sentence case, `ID: <family>/<slug>. Version: <contents of VERSION>.`, then Use for, Inputs, Method, Deliver, Acceptance, Safeguards (required for security, finance, people-hr and legal-compliance: source, uncertain, authorization, escalate, and "not professional advice"), Handoff (real role IDs in backticks, the sentence "All Coordinator boundaries apply", plus one role-specific limit). Keep it about 1.4 to 2.4 KB, materials only, fictional examples only, no named laws or standards, and no restricted word (publish, deploy, credential, token, connect, install, upload, execute, guarantee, compliant and the rest in the card guide) unless the same paragraph rules it out.
5. **Counts and notes.** The roster size is hand-written in several places. Find them with `grep -rn "124" --include=*.md --include=*.py .` (ignore `dist/`, `catalog/*/INDEX.md` and `adapters/`, which are generated) and update each: `README.md`, `docs/ROADMAP.md` (catalog status and the family row in the inventory table), `docs/VALIDATION.md`, `pack/START-HERE.md`, and the expected counts and the "total says 123 but roster has 124" message in `tests/test_pack.py`. Add a line under Unreleased in `CHANGELOG.md`.
6. **Build and verify.** Run `python3 -B scripts/pack.py build`, then `check`, then `python3 -B scripts/evals.py selfcheck`, then `python3 -B -m unittest discover -s tests`. Fix the source file named by any failure; never edit generated files.
7. **Review.** Run `/review-card <family>/<slug>` and summarize the result.

Do not commit or open a pull request unless asked. Finish with the list of files changed.
