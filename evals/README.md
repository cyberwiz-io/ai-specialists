# Fixture evals

Offline checks that give the specialist cards, and the experimental [Claude Code adapter](../adapters/claude-code/README.md), something repeatable to be judged against. They are maintenance tooling and are not part of the shipped pack or its release archive.

## What this is, and is not

Each file in `scenarios/` holds a fictional request, the roles it applies to, and keyword rules (`must_match_any`, `must_not_match`) with a reason for each. The scenarios come from the paper-review table in [Validation](../docs/VALIDATION.md): a request to publish, a request to act on a system, a sensitive-domain decision, an unsupported claim, no image tools, and missing inputs.

Keyword rules are a smoke test. A pass does not show that a response is good, safe or reliable, and a fail can mean the rule is too narrow. One run per scenario says nothing about consistency. No result here is host-compatibility evidence, subject-expert review, independent review, or a comparison with a well-instructed generalist.

## Commands

```sh
python3 -B scripts/evals.py selfcheck                      # each scenario's good sample passes and bad sample fails
python3 -B scripts/evals.py list [role-id]                 # scenarios that apply
python3 -B scripts/evals.py prompt <role-id> <scenario>    # adapter agent text plus the request, for a runner
python3 -B scripts/evals.py grade <role-id> <scenario> <response-file>
```

The script never calls a model. To run a scenario, give the `prompt` output to an AI host, save the reply as a file, and grade it. In Claude Code, `/review-card <role-id>` does this with a fresh subagent per scenario and saves replies under the ignored `work/evals/` folder. Model replies are not committed.

## Add a scenario

Add `scenarios/<id>.json` with `id` (matching the file name), `source`, `applies_to` (role-ID patterns such as `security/*`, or `sensitive`), a fictional `prompt`, `graders`, and `samples.good` / `samples.bad`. `selfcheck` and the tests reject a scenario whose good sample fails or whose bad sample passes.
