---
name: card-evals
description: Run the card evaluation harness in this repository. Use when asked to run the card evals or fresh-host trials, evaluate specialists against fixtures, or produce an eval report for one family, one role or the whole catalog.
---

# Card evaluations

This runs each specialist card against its fictional fixtures in fresh subagents and grades every reply against the card's own Acceptance line. Read [evals/README.md](../../../evals/README.md) for the fixture format and grading rules. Only run an evaluation when the user asks for one: a full run spawns two subagents per fixture.

## 1. Prepare

Agree the scope with the user: one role, one family, `--kind boundary`, or everything. Then:

```sh
python3 -B scripts/evals.py prepare --run <date>-<scope> --host "<host, such as Claude Code (cloud)>" --model "<model under test>" [--family <id>] [--role <id>] [--kind task|boundary]
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
- If a subagent fails or writes nothing, start a fresh one for that fixture once. If it fails again, leave the fixture and report it as missing.
- Check `status` again until no lines remain, or until only fixtures that failed twice are left.

For a whole family or the whole catalog, `scripts/evals_headless.sh <run> [parallel]` does this step without subagents: it starts one fresh `claude -p` session per reply and per grade, outside the repository, with memory and settings off and only these two agents' instructions, and retries each step once. Record `--host` as "Claude Code <version> (cloud), one fresh claude -p session per reply and per grade" when you prepare such a run. The 2026-10-17 full-catalog run took about an hour at six to eight sessions.

## 3. Report

```sh
python3 -B scripts/evals.py report --run <run>
```

`report` validates every reply and grade. Each grade must list exactly the prepared items, in order, with allowed verdicts. If a grade is invalid, delete it and grade that fixture again with a fresh grader. Do not edit grades by hand. The command writes `work/evals/<run>/REPORT.md`, which records the version, commit, host, tools, models, inputs, outcomes and limits.

Give the user the totals and the fixtures that did not pass. Do not describe the results as more than the report's Limits section allows. `work/` is never committed. When the user has reviewed the report and wants it kept, copy it to `evals/reports/<run>.md`, link it from `docs/VALIDATION.md` under Recorded evaluations, and run the pack build, check and tests.

## 4. Weekly regression check

A scheduled task runs this unattended. It never edits the baseline or the repository.

1. If `evals/baseline.json` has `"run": null`, there is nothing to compare with. Stop and say so; do not run the evals.
2. Run the whole catalog with the steps above, named `<date>-weekly`, recording the model as the host reports it. Use `scripts/evals_headless.sh <date>-weekly` for step 2, and `--model claude-opus-5-5` unless the baseline's model is no longer available, in which case say so in the issue.
3. Run `python3 -B scripts/evals.py compare --run <run>`. Exit 0 means no card fell: stop without opening an issue. Exit 3 means at least one fell.
4. On exit 3, search open issues for the label or title `Card eval regression`. If one is open, add the new `REGRESSION.md` as a comment; otherwise open an issue titled `Card eval regression: <date>` with its contents, noting any model change it reports. Do not paste replies or grades.
5. If the run itself fails (missing fixtures after one retry), open or comment on an issue saying which fixtures are missing; do not compare a partial run to the baseline as if complete.
