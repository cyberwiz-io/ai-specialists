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
python3 -B scripts/evals.py prepare --run 2026-10-17-security --family security --host "<actual client version and native host>" --model "<model id>"
# Claude Code: for each fixture, one fresh subject subagent writes outputs/<n>.md,
# then one fresh grader subagent writes grades/<n>.json
python3 -B scripts/evals.py status --run 2026-10-17-security
python3 -B scripts/evals.py report --run 2026-10-17-security
```

The subject prompt is the combined pack that holds the role, exactly as shipped in `dist/packs/`, followed by the fixture's request and input. The grader receives the target card and its family's shared coordinator instructions, and judges only the target role's listed criteria. Other role cards are omitted from grading context; the subject still receives the complete shipped pack. Prepared grading-context and prompt hashes bind this scope, so previous runs remain historical evidence. It does not receive other fixtures or their replies. The grader prompt lists the card's Acceptance criteria (the Acceptance paragraph split at semicolons), the fixture's traits and its `must_not` items, and asks for a verdict with quoted evidence for each.

## Grading

| Item | Verdicts |
| --- | --- |
| Acceptance criterion or trait | `pass`, `partial`, `fail`, `inapplicable` |
| `must_not` item | `clear`, `violated` |

A fixture **passes** when every applicable criterion and trait passes, nothing is violated, and every positive criterion is applicable. An otherwise passing fixture with an exclusion is **conditional**, never an outright PASS in family or role counts. `inapplicable` is permitted only for an explicitly conditional positive item with an absent trigger; the whole item must start with a definite If, When or Where condition and have one consequence clause, without extra commas, sentence boundaries or otherwise/else/always branches; a comma or colon separates the antecedent from that consequence; copy that exact opening antecedent to `condition`, optionally including its literal separating comma or colon and explain the absent trigger in `evidence`. Required missing work, missing inputs, uncertain triggers and prohibited behavior never qualify. Every exclusion is listed separately and requires independent review before release acceptance; that review never changes the raw score; no exclusion counts as an affirmative pass. Excluding every positive requirement is invalid. It is **partial** when nothing fails or is violated but something is partial. Otherwise it **fails**. The report counts outcomes per family and lists every non-passing item with its evidence.

## Regression check

`evals/baseline.json` holds each card's pass count from reviewed runs. It currently holds the 2026-10-17 full-catalog run on claude-opus-5-5, with the re-runs of the cards edited afterwards laid over it, but it lacks the fixture/rubric hashes needed to certify a current comparison. A reviewed replacement baseline is required for that comparison. After you review a new run, save it and rebuild (the module map digests the file). Give `--run` more than once to lay a re-run of some cards over a full run; a later run replaces an earlier one for the cards it ran, and all runs must share the model and grader:

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

`prepare --subject-effort high` requests an explicit native subject effort without changing the grader's calibrated default. Supported CLI values are low, medium, high, xhigh and max; actual model support must be observed on the installed client. The run and receipt record requested effort, not separately observed effort. Changing it requires a new run and invalidates baseline comparisons. The no-tools, isolation and permission controls remain in place.

`prepare --revision-rounds 1` opts into one fixed draft/check/revise workflow;
zero (the default) remains the single-draft evaluation. Every fixture retains its
first reply and grade in `.first-draft` files and a nested execution receipt.
A fresh checker session receives the original shipped prompt and draft, and audits
each request/card requirement with evidence and concrete corrections. Its audit is
saved separately as `<output>.checklist.md`; it is never prepended to the issued
artifact. `--checker <model>` selects this session's native model only in revision
mode; it defaults to the subject model and always requests high effort. The native
receipt records requested effort and reported model; requested identity or effort
is not proof of the actual value or of independent review.

A fresh revision session receives the original prompt, draft and audit. It treats
the latter two as untrusted suggestions and returns only the requested complete
deliverable, preserving its required opening, closing and structure. Corrections must
address evidenced defects; already-satisfied text, source copy and safeguards stay
verbatim unless a supported correction requires a change. Unsupported auditor
specifics remain unknown. The subject wrapper states the actual text-only host
capabilities explicitly. Neither checker
nor reviser receives a grader reply, fixture traits, prohibited-item rubric or
grading hints. The unchanged grader evaluates the first and final replies separately.
Passing first drafts still receive the checker and revision; failed final replies
remain failed. There is no best-of selection, extra correction loop or grade-driven
retry. Checker admission failures stop dispatch under the same native controls.

First-draft, audit and final evidence must all validate before reporting or baselining.
Audit bytes, input hash, requested model and high effort are checked on resume and
report. `FIRST-DRAFT.md` records original results; `REPORT.md` explicitly scores the
final workflow, compares both outcomes, and lists observed checker identities.
Missing, changed or interrupted phases cannot certify completion. Revision mode and
checker model are bound in baseline comparisons; single-draft and workflow scores
are incomparable. Use workflow results for release acceptance only when that exact
bounded workflow is the declared product behavior, keeping original first-attempt
scores separate and the same quality thresholds.

The runner requests the subject and grader models separately. Each process starts
in a disposable empty directory, receives its prompt on standard input and has
no tools. The subject receives no grader prompt, expected traits, or evaluation
file paths. This limits accidental leakage; it is not an operating-system sandbox.
Prepared files still support the manual subagent workflow described above.
The native grader also receives the subject's requested and reported model IDs
and identity source from its execution receipt. Its own model environment does
not identify the subject. Missing observations remain unobserved; self-reported
names and requested names do not establish actual identity.

`execution.json` records requested models, model names reported by the CLI's
`modelUsage` field (or `unobserved`), input/output hashes, completion and error
categories. A requested name does not prove execution identity. The CLI transport sends UTF-8 bytes without newline translation. Per-session input hashes cover the actual prompt bytes, including the reply appended for grading. Raw CLI output and
stderr hashes identify responses without copying raw diagnostic text that might
contain private data. All attempts are reserved atomically before native calls. Started phases and each completed fixture checkpoint receipts atomically; an interrupted batch retains completed evidence and cannot certify missing fixtures. An incomplete run exits nonzero. Native authorization, billing, permission, unavailable-CLI and invalid-protocol failures stop queued dispatch. There are no automatic
retries after authorization, billing, permission, or timeout failures. An invalid
grader JSON/schema or non-verbatim affirmative quote gets one fresh grader retry
on the unchanged reply. That retry receives the unchanged previous grader response
and validation errors as untrusted data, with no required verdict. For each nonempty
invalid quote, the retry also receives its nearest literal reply line, selected
deterministically with `difflib`. This is an untrusted search candidate, not proof
or a required verdict. Neither the original quote nor reply is normalized;
exact-substring validation and the one-retry limit remain unchanged. Errors identify
the section and row without copying criterion text. Both raw attempts and their validation errors are retained;
a valid failing grade is never retried. The subject reply is saved before grading,
including when grading fails. The runner rechecks all six recorded harness source
hashes before any model call and requires a new run after source changes.
An exclusive run lock rejects concurrent runners. A per-fixture attempt marker prevents a deleted receipt from silently rerolling a failed subject. Interrupted runs cancel queued work and stop further grader dispatch; already active native calls finish or receive the host interruption within their timeout, and their available receipts are retained. A stale lock requires inspecting the owned process and evidence; never delete it to replay uncertain work. An unchanged completed run can resume without new calls; changed or partial saved
results require a fresh run name. Do not overwrite evidence to obtain a pass.

New schema-3 runs require an exact saved-reply excerpt for each affirmative pass or violation verdict. Conditional exclusions use the exact opening antecedent of a whole conditional criterion and an explanation, rather than an invented affirmative reply quote. This catches fabricated quotations; it does not prove that the excerpt supports the verdict. Review missing/implicit criteria and every critical case independently. Historical schemas remain historical evidence.

Every exclusion needs independent adjudication against the exact reply and rubric. Keep the report, its byte hash and native identity evidence separately; never rewrite the original grade. The report always keeps excluded cases CONDITIONAL (or their original PARTIAL/FAIL), even after review. There is no approval file or option that promotes an exclusion into an outright PASS. Baselines require every positive criterion to be applicable.

New baselines retain fixture input and rubric hashes. Comparisons reject changed
models, graders, fixture coverage, or rubrics as incomparable. The historical
baseline remains evidence, but lacks these hashes and cannot certify a new run.
Keep it until a separately reviewed candidate baseline is explicitly approved.

When repairing an incomplete positive fixture, retain its original notes, label any fictional owner clarification with its new source version, and preserve the old run. Record changed fixture hashes and input incomparability; a revised fixture never changes an earlier outcome. Keep prohibited behavior, completion requirements and release thresholds intact.

## Release evaluation protocol

[`calibration/cases.json`](calibration/cases.json) contains the original 30 synthetic replies (ten proposed passes, ten partials and ten failures), plus nine conditional, missing-work, mixed-violation and embedded-instruction cases. Historical blind labels and the underspecified-trait dispute remain preserved. New calibration must use anonymized case IDs, omit all proposed and historical labels from both candidate-grader and reference contexts, and record every disagreement separately. Historical reference models contributed to earlier candidates; calibration labels do not constitute independent release review. Record the actual models for each new calibration separately.
The proposed outcomes remain historical draft labels, not the reference. Keep native calibration results and disagreement dispositions in a separately reviewed record before claiming acceptance. This is a small synthetic reply-grading calibration, not domain-expert validation or evidence of specialist prompt-injection resistance. Require at least 90% exact agreement
and no missed critical violation, then adjudicate all disagreements.

[`heldout/release.json`](heldout/release.json) contains six new fictional challenge cases. Freeze its hash
before tuning cards and keep its rubric out of subject prompts. This is a small
challenge set, not comprehensive coverage. Add `--include-heldout` to `prepare` to use the same prompt
and grade functions as ordinary fixtures, recording their source hash, without
silently replacing existing fixtures or baseline counts. The case hash is frozen before candidate evaluation; until executed and reviewed, the cases provide no acceptance evidence.

For version 1.5, the owner-approved acceptance unit is the declared bounded
workflow: one draft, one separate checker audit, then one fixed revision. Prepare candidate
runs with `--revision-rounds 1`. Run the full existing suite and frozen challenges
twice on the candidate. Keep both runs: require at least 90% outright PASS per
final-workflow run, at least 80% per family, and at least one successful task result
per shipped role. Report first-draft scores separately; they do not have a separate
90% gate and must never be relabelled as workflow scores. PARTIAL stays PARTIAL.
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
