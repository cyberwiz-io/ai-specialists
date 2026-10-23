---
name: card-evals
description: Run the card evaluation harness in this repository. Use when asked to run the card evals or fresh-host trials, evaluate specialists against fixtures, or produce an eval report for one family, one role or the whole catalog.
---

# Card evaluations

This runs each specialist card against its fictional fixtures in fresh subagents and grades every reply against the card's own Acceptance line. Read [evals/README.md](../../../evals/README.md) for the fixture format and grading rules. Only run an evaluation when the user asks for one: a full run spawns two subagents per fixture.

## 1. Prepare

Agree the scope with the user: one role, one family, `--kind boundary`, or everything. Then:

```sh
python3 -B scripts/evals.py prepare --run <date>-<scope> --host "<actual native host and Claude Code version>" --model "<model under test>" [--family <id>] [--role <id>] [--kind task|boundary]
```

Record the model as the host reports it; if you cannot confirm it, say so in `--model`. Add `--grader` if grading uses another model. `prepare` runs the pack check first and refuses an existing run name. It writes `work/evals/<run>/` with `run.json`, a subject and a grader prompt per fixture, and empty `outputs/` and `grades/` folders.

## 2. Reply, then grade, each in a fresh subagent

Run `python3 -B scripts/evals.py status --run <run>`. Each line gives a fixture, its prompt file and its target file. For each `needs reply` line, start a new `card-eval-subject` subagent with a prompt like this:

> Prompt file: `<subject prompt path>`. Output path: `<output path>`.

Once that fixture's reply exists, start a new `card-eval-grader` subagent with a prompt like this:

> Grader prompt: `<grader prompt path>`.

Rules:

- Use a **new** subagent for every reply and every grade. Never reuse or resume one, never let a subject grade, and never grade a reply yourself.
- Pass only the paths. Do not paste the card, the fixture or your own hints into the subagent prompt.
- Run up to about eight subagents at a time. Do not read the replies or grades into this conversation unless something fails.
- Preserve every subject attempt, including failures and empty results. Never rerun a failed or interrupted subject within the same run; use a new run name.
- Check `status` again; report failed or interrupted fixtures as incomplete.

For a whole family or the whole catalog, `python3 -B scripts/evals_runner.py <run> [parallel]` starts one fresh native `claude -p` process per subject and grader in empty disposable directories with no tools. `scripts/evals_headless.sh` only invokes that runner. Only an invalid grader JSON/schema or non-verbatim affirmative quote gets one fresh grader retry on the unchanged reply; both raw attempts are retained. Subject, authorization, billing, permission and timeout failures are never retried. Record the actual native host and Claude Code version rather than assuming a cloud host. Historical 2026-10-17 runs predate this runner.

## 3. Report

```sh
python3 -B scripts/evals.py report --run <run>
```

`report` validates every reply and grade. Each grade must list exactly the prepared items, in order, with allowed verdicts. Preserve an invalid raw grade and its validation errors; only invalid JSON/schema or a non-verbatim affirmative quote permits one fresh grader retry on the unchanged reply. Retain both attempts. Never delete or edit grades to obtain a pass, or retry a valid failing grade. The command writes `work/evals/<run>/REPORT.md`, which records the version, commit, host, tools, models, inputs, outcomes and limits.

Give the user the totals, every inapplicable conditional item requiring independent review, and the fixtures that did not pass. Do not describe the results as more than the report's Limits section allows. `work/` is never committed. When the user has reviewed the report and wants it kept, copy it to `evals/reports/<run>.md`, link it from `docs/VALIDATION.md` under Automated and historical evidence, and run the pack build, check and tests.

## 4. Optional regression check

No recurring evaluation is authorized by this skill. Run a regression check only when requested. The historical baseline lacks fixture and grading-harness hashes and cannot support a current comparison. First obtain approval for a reviewed replacement baseline from complete runs of the current harness. A regression check never edits the baseline or the repository.

1. If the baseline has no run or lacks fixture/rubric hashes, report that regression comparison is unavailable. A requested evaluation may still run and retain its own results; do not replace the baseline without reviewed evidence.
2. Run the whole catalog with the steps above under a new run name, recording requested and host-observed model identities. The native runner is `python3 -B scripts/evals_runner.py <run> [parallel]`; use the model and grader recorded in the reviewed baseline. Stop if they are unavailable or the harness hashes differ.
3. Run `python3 -B scripts/evals.py compare --run <run>`. Exit 0 means no card fell: stop without opening an issue. Exit 3 means at least one fell.
4. On exit 3, search open issues for the label or title `Card eval regression`. If one is open, add the new `REGRESSION.md` as a comment; otherwise open an issue titled `Card eval regression: <date>` with its contents, noting any model change it reports. Do not paste replies or grades.
5. If the run itself fails (failed or interrupted fixtures), open or comment on an issue saying which fixtures are missing; do not compare a partial run to the baseline as if complete.
