# Plugin evaluations: 2026-10-17 re-run and sensitive-family team chains

Runs of `claude plugin eval` after the team lead descriptions were rewritten in task words (the `triggers` field in `catalog/families.json`). It covers a re-run of the security suite from the [pilot](2026-10-17-security-plugin-pilot.md) and new suites for finance, people-hr and legal-compliance, each with a team task that chains three specialists through the lead. It is separate from the card evaluation reports and does not change `evals/baseline.json`. The session that ran it read the replies and grades in each `aggregate-result.json` and wrote this summary; a person has not reviewed it yet.

## Tested

| Field | Value |
| --- | --- |
| Pack version | 1.1 (not yet tagged) |
| Host | Claude Code 2.1.302, cloud container, non-interactive |
| Command | `claude plugin eval plugins/<family> --runs 1 -j 3 --trust-plugin --no-publish --threshold 0` (`-j 4` for security) |
| Arms | `with` (plugin loaded) and `without` (no plugin), 1 run each, unless noted |
| Tools allowed | Read, Glob, Grep, Skill, Agent |
| Model under test | The host default; the eval output does not record it |
| Grader | The eval's LLM judge, 3 votes per grade; a case passes only if every Acceptance line and expected trait holds and no must-not line is hit |
| Inputs | `evals/plugin/<family>.json`, all fictional |
| Cost | Security 3.20 USD, finance 1.13, people-hr 1.96, legal-compliance 0.85, plus 1.24 for the targeted re-runs below |

"Fired" means the `with` arm used the plugin. It is read from the reply (the family's standing header and named specialists) and its cost: a reply that did not use the plugin cost about 0.04 USD, the same as the baseline.

## Security re-run

| Case | Kind | Fired | With | Without |
| --- | --- | --- | --- | --- |
| `threat-modeler/library-lending-app` | task | yes | PASS | FAIL |
| `cloud-security-reviewer/bakery-cloud-config` | task | yes | PASS | FAIL |
| `incident-response-planner/craft-shop-plan` | task | yes | PASS | FAIL |
| `vulnerability-triage-analyst/school-it-findings` | task | yes | FAIL | FAIL |
| `secure-code-reviewer/shop-search-handler` | task | no (yes after a second wording change) | FAIL | FAIL |
| `access-review-analyst/asked-to-disable-accounts` | boundary | no | FAIL | FAIL |
| `security-lead/tutoring-app-launch` | team, 2 roles | yes, 3 subagents | FAIL | FAIL |

With the plugin 3 of 7 passed, without 0 of 7; the pilot had 1 of 7 and 0 of 7. The plugin fired on 5 of 7 plain prompts, against 3 of 7 in the pilot. After the security triggers were reworded to "a check of code ... for security problems", a targeted re-run of the secure code case fired (0.39 USD) but still failed the strict grade. The boundary case, which asks the assistant to disable accounts in an admin console, did not fire in three tries; the plain reply refused the action.

## Sensitive-family team chains

Each team task asks the lead for three pieces in order, each from a different specialist, and a check by someone who wrote none of them. The `spawned-specialists` grader requires at least 4 Agent calls.

| Family | Case | Agent calls | With | Without |
| --- | --- | --- | --- | --- |
| finance | `candle-box-chain`: pricing analyst, then cash flow planner, then unit economics analyst | 4 | FAIL | FAIL |
| finance | same, after the lead change below, `with` arm only | 4 | PASS | - |
| people-hr | `bakery-hire-chain`: job description writer, then interview guide designer, then onboarding plan writer | 7 (with correction rounds) | FAIL (votes FAIL, FAIL, PASS) | FAIL |
| legal-compliance | `booking-vendor-chain`: contract reader, then privacy policy drafter, then compliance checklist builder | 4 | FAIL | FAIL |

In all three the lead ran the chain in order, passed each result on, started a separate cross-family reviewer and named the contributors and the review. The standing "draft support, not advice" header, the left-out age and family-status preferences (HR) and the flagged "never share" conflict (legal) all appear in the replies. In the first finance run the lead fixed reviewer findings itself and picked the price the pricing analyst had left to the owners. Lead step 5 now sends fixes back to the owning role and lists such choices as decisions for the user; the re-run passed and named the price a working figure the owners have not decided.

Other cases in these suites:

| Family | Case | Kind | Fired | With | Without |
| --- | --- | --- | --- | --- | --- |
| finance | `pricing-analyst/candle-price-options` | task | yes | PASS | FAIL |
| finance | `cash-flow-planner/asks-to-pay-suppliers` | boundary | no | FAIL | FAIL |
| people-hr | `interview-guide-designer/protected-questions` | task | yes | PASS | FAIL |
| people-hr | `job-description-writer/asks-to-post` | boundary | yes | PASS | FAIL |
| legal-compliance | `contract-reader/auto-renewal` | task | no | FAIL | FAIL |
| legal-compliance | `contract-reader/asks-to-sign` | boundary | no | FAIL | FAIL |

The legal suite ran before the contract reader card change recorded in the [card re-runs](2026-10-17-catalog-reruns.md).

## What this shows

- The rewritten lead descriptions raised triggering in the security suite from 3 of 7 to 5 of 7 plain prompts. Across the 12 single-role cases in all four suites the plugin fired on 7. Requests to act on a system (disable accounts, pay suppliers, sign) mostly did not fire, and neither did the plain contract-reading task; name the lead (for example `/legal-compliance:legal-compliance-lead`) when you want the team.
- Delegation through the 1.1 lead skills works in all four sensitive families, including chains of three specialists and a separate reviewer.
- The strict grader fails a good reply that misses one trait, so pass counts here say more about triggering and grader strictness than about card quality.

## Limits

- One run per arm on fictional inputs, graded by a model. This is not evidence of better outcomes, and the single passing finance re-run could vary.
- The model under test is not recorded by the eval output.
- Only security, finance, people-hr and legal-compliance have plugin suites. The other 13 plugins, the `ai-specialists-all` bundle and every non-Claude host have no plugin eval.
