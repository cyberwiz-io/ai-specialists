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

## 3. Report

```sh
python3 -B scripts/evals.py report --run <run>
```

`report` validates every reply and grade. Each grade must list exactly the prepared items, in order, with allowed verdicts. If a grade is invalid, delete it and grade that fixture again with a fresh grader. Do not edit grades by hand. The command writes `work/evals/<run>/REPORT.md`, which records the version, commit, host, tools, models, inputs, outcomes and limits.

Give the user the totals and the fixtures that did not pass. Do not describe the results as more than the report's Limits section allows. `work/` is never committed. When the user has reviewed the report and wants it kept, copy it to `evals/reports/<run>.md`, link it from `docs/VALIDATION.md` under Recorded evaluations, and run the pack build, check and tests.
