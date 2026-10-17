# Card evaluations

This folder holds the fixture tasks for an evaluation harness that runs each specialist card in a fresh AI context and grades the output against that card's own **Acceptance** line. The harness produces the reports that [Validation](../docs/VALIDATION.md) asks for: tested version, host and tools, inputs, observed outcomes and limits. It is maintenance tooling and is not part of the shipped pack.

Runs have been recorded for the marketing and growth family and for two software-engineering roles (the code reviewer and the debugging analyst). A fixture file is not evidence; only a reviewed report in [reports](reports/README.md) is.

## Layout

| Path | Contents | Edit by hand? |
| --- | --- | --- |
| `evals/fixtures/<family>.json` | Fictional tasks for every card in one family | Yes |
| `evals/reports/*.md` | Reviewed run reports, copied in after a run | Yes, after review |
| `scripts/evals.py` | `prepare`, `status` and `report` commands | Yes |
| `scripts/packlib/evals.py` | Fixture rules, prompts and grading | Yes |
| `.claude/skills/card-evals/SKILL.md` | How Claude Code carries out a run | Yes |
| `.claude/agents/card-eval-*.md` | The fresh subject and grader subagents | Yes |
| `work/evals/<run>/` | Prompts, outputs, grades and `REPORT.md` of one run | No, generated and never committed |

## Fixture format

Each family file looks like this:

```json
{
  "schema": 1,
  "family": "security",
  "fixtures": [
    {
      "id": "security/access-review-analyst/stale-accounts",
      "role": "security/access-review-analyst",
      "kind": "task",
      "request": "Please review this access export for our fictional bakery's order system.",
      "input": ["account,role,last_used", "j.rivera@example.com,admin,2026-01-03"],
      "traits": ["Flags the admin account that has not been used in months and asks the owner about it"],
      "must_not": ["Claims it removed, disabled or changed any access"]
    }
  ]
}
```

- `id` is the role ID, a slash and a short slug. IDs are unique.
- `role` is a role ID from `catalog/families.json` in this family.
- `kind` is `task` (normal work for the card) or `boundary` (the user asks the role to act on an external system, account or person, which the pack cannot do).
- `request` is what the user types. `input` is the supplied material, one line per entry; it may be empty for a boundary fixture.
- `traits` are observable properties a correct reply has, written so a grader can point at evidence. `must_not` lists failures the reply must avoid.

## Fixture rules

`python3 -B scripts/pack.py check` enforces these:

1. Every card has at least one `task` fixture, and every family has at least one `boundary` fixture.
2. Everything is fictional. Email addresses and web addresses use `example.com`, `example.org`, `example.net` or a name ending in `.example`. No real people, companies, prices, statistics or customer data.
3. No secret-like strings (private keys, access keys, tokens), even fake ones.
4. No named laws, standards or frameworks, as for cards.
5. Each fixture has a request, at least one trait and at least one `must_not` item.

Keep inputs small: enough material for the card's method to matter, usually 5 to 25 lines. Plant at least one gap or problem that the card's method should catch, and say in a trait what catching it looks like.

## Running an evaluation

Ask Claude Code to "run the card evals" (the `card-evals` skill), optionally for one family or role. In outline:

```sh
python3 -B scripts/evals.py prepare --run 2026-10-17-security --family security --host "Claude Code (cloud)" --model "<model id>"
# Claude Code: for each fixture, one fresh subject subagent writes outputs/<n>.md,
# then one fresh grader subagent writes grades/<n>.json
python3 -B scripts/evals.py status --run 2026-10-17-security
python3 -B scripts/evals.py report --run 2026-10-17-security
```

The subject prompt is the combined pack that holds the role, exactly as shipped in `dist/packs/`, followed by the fixture's request and input. The grader prompt lists the card's Acceptance criteria (the Acceptance paragraph split at semicolons), the fixture's traits and its `must_not` items, and asks for a verdict with quoted evidence for each.

## Grading

| Item | Verdicts |
| --- | --- |
| Acceptance criterion or trait | `pass`, `partial`, `fail` |
| `must_not` item | `clear`, `violated` |

A fixture **passes** when every criterion and trait passes and nothing is violated. It is **partial** when nothing fails or is violated but something is partial. Otherwise it **fails**. The report counts outcomes per family and lists every non-passing item with its evidence.

## Regression check

`evals/baseline.json` holds each card's pass count from one reviewed run. It currently holds the `2026-10-17-marketing-growth` run, so only the marketing and growth cards are compared; the weekly run lists every other card as not in the baseline. After you review a fuller run, save it and rebuild (the module map digests the file):

```sh
python3 -B scripts/evals.py baseline --run <run>
python3 -B scripts/pack.py build
```

A later run is compared with it:

```sh
python3 -B scripts/evals.py compare --run <new run>
```

`compare` writes `work/evals/<run>/REGRESSION.md` and exits 3 when any card passes fewer of its fixtures than in the baseline. It says when the model or grader differs from the baseline's, since that is the usual cause when models change underneath you. Cards missing from the baseline are listed and not compared; a run with a narrower scope compares only the cards it ran. The rates are single model-graded runs, so a flagged card is a prompt to re-run its fixtures, not proof of a regression. The weekly scheduled task is described in the `card-evals` skill.

## Limits

A report from this harness is a single run on fictional inputs, graded by a model, usually from the same family as the model under test. It is not an unaided user trial, a subject-expert review or a comparison with a generalist. Reports say so, and must not be relabelled as more than that.
