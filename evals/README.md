# Card evaluations

This folder holds the fixture tasks for an evaluation harness that runs each specialist card in a fresh AI context and grades the output against that card's own **Acceptance** line. The harness produces the reports that [Validation](../docs/VALIDATION.md) asks for: tested version, host and tools, inputs, observed outcomes and limits. It is maintenance tooling and is not part of the shipped pack.

Every card has a recorded run: the 2026-10-17 full-catalog run and its re-runs, besides earlier runs for the marketing and growth family and two software-engineering roles. A fixture file is not evidence; only a reviewed report in [reports](reports/README.md) is.

## Layout

| Path | Contents | Edit by hand? |
| --- | --- | --- |
| `evals/fixtures/<family>.json` | Fictional tasks for every card in one family | Yes |
| `evals/reports/*.md` | Reviewed run reports, copied in after a run | Yes, after review |
| `scripts/evals.py` | `prepare`, `status`, `report`, `baseline` and `compare` commands | Yes |
| `scripts/evals_headless.sh` | Carries out a prepared run with one fresh `claude -p` session per reply and per grade | Yes |
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

The subject prompt is the combined pack that holds the role, exactly as shipped in `dist/packs/`, followed by the fixture's request and input. The grader receives the same shipped pack, including the shared coordinator boundaries, and judges only the target role's listed criteria. It does not receive other fixtures or their replies. The grader prompt lists the card's Acceptance criteria (the Acceptance paragraph split at semicolons), the fixture's traits and its `must_not` items, and asks for a verdict with quoted evidence for each.

## Grading

| Item | Verdicts |
| --- | --- |
| Acceptance criterion or trait | `pass`, `partial`, `fail` |
| `must_not` item | `clear`, `violated` |

A fixture **passes** when every criterion and trait passes and nothing is violated. It is **partial** when nothing fails or is violated but something is partial. Otherwise it **fails**. The report counts outcomes per family and lists every non-passing item with its evidence.

## Regression check

`evals/baseline.json` holds each card's pass count from reviewed runs. It currently holds the 2026-10-17 full-catalog run on claude-opus-5-5, with the re-runs of the cards edited afterwards laid over it, so every card is compared. After you review a new run, save it and rebuild (the module map digests the file). Give `--run` more than once to lay a re-run of some cards over a full run; a later run replaces an earlier one for the cards it ran, and all runs must share the model and grader:

```sh
python3 -B scripts/evals.py baseline --run <full run> [--run <re-run> ...]
python3 -B scripts/pack.py build
```

A later run is compared with it:

```sh
python3 -B scripts/evals.py compare --run <new run>
```

`compare` writes `work/evals/<run>/REGRESSION.md` and exits 3 when any card passes fewer of its fixtures than in the baseline. It refuses comparisons when model, grader, fixture membership, inputs or rubrics differ, or when the historical baseline lacks fixture hashes. A narrower scope can compare unchanged complete fixture sets for selected cards. The rates are single model-graded runs, so a flagged card is a prompt to re-run its fixtures, not proof of a regression. No recurring evaluation is started by these commands; scheduling requires separate authorization.

## Limits

A report from this harness is a single run on fictional inputs, graded by a model, usually from the same family as the model under test. It is not an unaided user trial, a subject-expert review or a comparison with a generalist. Reports say so, and must not be relabelled as more than that.

## Native runner and trustworthy evidence

After preparing a run, use `python3 -B scripts/evals_runner.py <run> [parallel]`
on macOS, or `py -3 -B scripts/evals_runner.py <run> [parallel]` in Windows
PowerShell. `scripts/evals_headless.sh` remains a compatibility wrapper. Parallel
sessions default to 1 and are bounded at 8; `--timeout` defaults to 300 seconds
per subject or grader call. Use only an already authorized CLI account with
eligible usage. The runner does not establish billing eligibility.

The runner requests the subject and grader models separately. Each process starts
in a disposable empty directory, receives its prompt on standard input and has
no tools. The subject receives no grader prompt, expected traits, or evaluation
file paths. This limits accidental leakage; it is not an operating-system sandbox.
Prepared files still support the manual subagent workflow described above.

`execution.json` records requested models, model names reported by the CLI's
`modelUsage` field (or `unobserved`), input/output hashes, completion and error
categories. A requested name does not prove execution identity. CLI output and
stderr hashes identify responses without copying raw diagnostic text that might
contain private data. Each completed fixture checkpoints its receipt atomically; an interrupted batch retains completed evidence and cannot certify missing fixtures. An incomplete run exits nonzero. There are no automatic
retries, including after authorization, billing, permission, or timeout failures.
An unchanged completed run can resume without new calls; changed or partial saved
results require a fresh run name. Do not overwrite evidence to obtain a pass.

New schema-3 runs require an exact saved-reply excerpt for each affirmative pass or violation verdict. This catches fabricated quotations; it does not prove that the excerpt supports the verdict. Review missing/implicit criteria and every critical case independently. Historical schemas remain historical evidence.

New baselines retain fixture input and rubric hashes. Comparisons reject changed
models, graders, fixture coverage, or rubrics as incomparable. The historical
baseline remains evidence, but lacks these hashes and cannot certify a new run.
Keep it until a separately reviewed candidate baseline is explicitly approved.

## Release evaluation protocol

[`calibration/cases.json`](calibration/cases.json) contains 30 synthetic grader calibration replies, ten
proposed passes, ten partials and ten failures. Blind reference labels are recorded, with one underspecified trait adjudicated separately. The reference model also contributed to this candidate; these labels do not constitute independent release review.
The proposed outcomes remain historical draft labels, not the reference. Keep native calibration results and disagreement dispositions in a separately reviewed record before claiming acceptance. This is a small synthetic reply-grading calibration, not domain-expert validation or evidence of specialist prompt-injection resistance. Require at least 90% exact agreement
and no missed critical violation, then adjudicate all disagreements.

[`heldout/release.json`](heldout/release.json) contains six new fictional challenge cases. Freeze its hash
before tuning cards and keep its rubric out of subject prompts. This is a small
challenge set, not comprehensive coverage. Add `--include-heldout` to `prepare` to use the same prompt
and grade functions as ordinary fixtures, recording their source hash, without
silently replacing existing fixtures or baseline counts. The case hash is frozen before candidate evaluation; until executed and reviewed, the cases provide no acceptance evidence.

Run the full existing suite and frozen challenges twice on the candidate. Keep
both runs: require at least 90% outright PASS per run, at least 80% per family,
and at least one successful task result per shipped role. PARTIAL stays PARTIAL.
Require zero critical prohibited behaviors. Boundary cases, sensitive-role tasks,
changed-card failures, and release-critical operational cases require three
consecutive successful independent runs. Report first-attempt results and
all-three stability separately; never substitute a best-of-three result.

Practical host tests separately exercise discovery, explicit invocation, routing,
lead-to-worker handoff, relevant approved skill use, model overrides, permissions,
and installation/update/removal on both required devices. Card text scores do
not establish any of these capabilities. Use traces and before/after fixture state,
not response headings or cost, to establish tool use. Review at least one useful
output per family, every critical violation, and every grading disagreement before
recording release readiness. An unavailable reviewer or device stays pending.
