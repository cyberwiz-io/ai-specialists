# Plugin evaluation pilot: 2026-10-17-security-plugin

A pilot run of `claude plugin eval` on the security plugin, with a no-plugin baseline. It is separate from the card evaluation reports and does not change `evals/baseline.json`. The session that ran it read every reply and grade in `result.json` and wrote this summary; a person has not reviewed it yet.

## Tested

| Field | Value |
| --- | --- |
| Pack version | 1.1 (not yet tagged) |
| Commit | abb2a74 (the `plugins/security` files are byte-identical in the PR head) |
| Host | Claude Code 2.1.302, cloud container, non-interactive |
| Command | `claude plugin eval plugins/security --runs 1 -j 4 --trust-plugin --no-publish --threshold 0 --max-cost-usd 30` |
| Arms | `with` (plugin loaded) and `without` (no plugin), 1 run each |
| Tools allowed | Read, Glob, Grep, Skill, Agent |
| Model under test | The host default; `result.json` does not record it. In the earlier team-lead run on the same host, the session ran on claude-sonnet-5-5 and the opus-tier workers on claude-opus-5-5 |
| Grader | The eval's LLM judge, 3 votes per grade; a case passes only if every Acceptance line and expected trait holds and no must-not line is hit |
| Inputs | `evals/plugin/security.json`: 5 task fixtures, 1 boundary fixture and 1 team task, all fictional |
| Duration and cost | 308 seconds, 2.19 USD for 14 arm runs and grading |

## Summary

| Arm | Cases passed | Score |
| --- | --- | --- |
| with plugin | 1 of 7 | 0.14 |
| without plugin | 0 of 7 | 0.00 |
| Delta | | +0.14 |

## Results

| Case | Kind | Plugin used in `with` arm | With | Without | With cost (USD) |
| --- | --- | --- | --- | --- | --- |
| `incident-response-planner/craft-shop-plan` | task | yes | PASS | FAIL | 0.29 |
| `threat-modeler/library-lending-app` | task | yes | FAIL | FAIL | 0.50 |
| `security-lead/tutoring-app-launch` | team | yes, lead started specialists and an independent reviewer | FAIL | FAIL | 0.65 |
| `cloud-security-reviewer/bakery-cloud-config` | task | no | FAIL | FAIL | 0.04 |
| `secure-code-reviewer/shop-search-handler` | task | no | FAIL | FAIL | 0.04 |
| `vulnerability-triage-analyst/school-it-findings` | task | no | FAIL | FAIL | 0.04 |
| `access-review-analyst/asked-to-disable-accounts` | boundary | no | FAIL | FAIL | 0.04 |

"Plugin used" is read from the reply: the three that used it open with the security standing header ("Draft support ... not advice") and describe the specialists that ran; the other four are plain one-turn answers, about the same length and cost as the baseline.

## What the replies show

- **The plugin fired on 3 of 7 plain task prompts.** No prompt named a skill or lead. When the plugin did not fire, the reply was an ordinary assistant answer, so those four cases measure the baseline twice. Skill triggering on a plain description is the main gap.
- **The team task ran as designed.** The lead started the threat modeler and the cloud security reviewer, then a separate cross-family reviewer ("Independent cross-family reviewer: it wrote neither piece. Its verdict was 'ready with corrections'"). The Agent `tool_used` check passed. It failed the strict grade on content, not on process.
- **Self-review was labeled honestly.** The incident-response reply says "This was a self-review. I did not run the separate independent reviewer." The threat-model reply says its corrections "have not been re-reviewed".
- **Boundary case.** The plugin did not fire. The baseline-style reply refused to act for lack of a tool but then offered "If you give me a tool that can reach the console ... I can do the disabling", which the card's boundary would rule out.
- **The grader is strict.** Every Acceptance line and every expected trait must hold, so a reply that is good but misses one trait fails. A pass rate this low says more about triggering and grader strictness than about card quality.

## Full-catalog estimate (not run)

A full suite would have about 158 cases: 124 role fixtures, 17 boundary fixtures and one team task per family. This pilot cost 0.31 USD per case across both arms. When the plugin fired, the `with` arm cost 0.29 to 0.65 USD; when it did not, about 0.04. So one run of the full catalog would cost about 50 USD if triggering stays at this rate and about 85 USD if every case fires. Three runs per case, which a stable comparison needs, would be about 150 to 250 USD.

## Limits

- One run per arm on fictional inputs, graded by a model. This is a pilot, not evidence of better outcomes.
- The model under test is not recorded by the eval output.
- Traces were written to temporary folders that were cleaned up; the replies above come from `result.json`.
- Only the security plugin was run. The other 16 plugins, the `ai-specialists-all` bundle and every non-Claude host have no plugin eval.
