# Evaluation reports

Reviewed reports from the [card evaluation harness](../README.md) go here, one file per run, named after the run, such as `2026-10-17-security.md`. Each one is the `REPORT.md` that `python3 -B scripts/evals.py report` wrote, copied here unchanged after a person has reviewed it. Link each report from [Validation](../../docs/VALIDATION.md).

Recorded so far: [2026-10-17-catalog](2026-10-17-catalog.md) (every card) and its [re-runs](2026-10-17-catalog-reruns.md), [2026-10-17-marketing-growth](2026-10-17-marketing-growth.md), [2026-10-17-se-code-reviewer](2026-10-17-se-code-reviewer.md), [2026-10-17-se-debugging-analyst](2026-10-17-se-debugging-analyst.md). Plugin eval pilots (`claude plugin eval`, written by hand from its `result.json`): [2026-10-17-security-plugin-pilot](2026-10-17-security-plugin-pilot.md) and [2026-10-17-plugin-evals](2026-10-17-plugin-evals.md) (security re-run and finance, people-hr and legal-compliance team chains).

A report states the tested version and commit, host and tools, models, inputs, outcomes and limits. Keep its Limits section. A report is evidence for that run only, not for later versions or other hosts.
