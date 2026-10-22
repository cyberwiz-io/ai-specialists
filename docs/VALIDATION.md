# Validation status

This repository ships advisory instruction materials. Structural checks and card evaluations do not establish that a host discovers, routes, delegates to, or safely runs them. The current 1.1 candidate has no published release. Current host acceptance for Claude Code and Codex on macOS and Windows is pending in all four combinations.

## Current host acceptance

| Device and client | Inventory | Acceptance |
| --- | --- | --- |
| macOS, Claude Code | 2.1.308 | Pending |
| macOS, Codex | 0.163.0 | Pending |
| Windows 11 build 26300, Claude Code | 2.1.304 | Pending |
| Windows 11 build 26300, Codex | 0.163.0 | Pending |

These versions are inventory observations, not test results. Follow [the host acceptance procedure](HOST-ACCEPTANCE.md) for each row. Acceptance requires observed installation, discovery, lead invocation, worker identity and handoff, expected behavior, permission boundaries, actual model reporting, update, and owned-only removal. A missing device or unobservable criterion stays pending. Historical trials on other versions or devices do not establish current acceptance.

The generated adapters express intended host configuration. Claude Code workers are configured with exactly `Read`, `Grep`, and `Glob`; they have no `Bash` or automatic skill tool. Leads pass approved methods explicitly in task handoffs. Codex's no-spawn direction is advisory; do not describe it as host enforcement. Role routing is advisory and separate from a task-specific cheapest-suitable model override that a host may support. Claude worker frontmatter retains role-specific model and effort defaults; the host applies these unless an explicit task override takes precedence. Codex workers inherit the parent model. Lead routing instructions are advisory, not a dynamic routing engine.

## Automated and historical evidence

Repository checks validate card structure, safeguards, links, generated-file freshness, adapter formats, fixtures and archive contents. These checks do not prove host behavior. Follow [Contributing](../CONTRIBUTING.md) for the current commands and [the release procedure](RELEASE.md) for the reviewed candidate and publication gates.

The reports in [evals/reports](../evals/reports/README.md) are historical, single-run evidence on fictional inputs. The 2026-10-17 catalog run recorded 78 pass, 59 partial and 4 fail across 141 fixtures; later reruns and plugin evaluations cover only their stated roles and cases. They are not acceptance runs for the current candidate. Model-graded fixture results do not establish subject expertise, real-world outcomes, host compatibility, or comparative quality.

The [card evaluation harness](../evals/README.md) produces the reports this page asks for. The marketing-growth and orchestration fixtures changed in this revision and have not been rerun; prior reports do not validate the new review rule. Every card has at least one fictional task fixture, and every family has a boundary fixture that asks for an external action. Claude Code runs each fixture in a fresh subagent, using the shipped combined pack. A separate fresh subagent then grades the reply against the card's own Acceptance line and the fixture's expected traits. `python3 -B scripts/evals.py report` writes a report with the tested version and commit, host and tools, models, inputs, outcomes and limits.

Historical host observations are retained in adapter guides and earlier records: Claude Code 2.1.302 had strict plugin validation and local smoke evidence, and a GitHub marketplace install of the prior 1.0 layout was observed. An Antigravity CLI 1.4.2 plan-mode run loaded a lead from a clone but did not complete the requested task. A Codex attempt was blocked before installation by a local wrapper; another local-checkout install ran no model. These observations are not current acceptance. No complete current four-device acceptance run, claude.ai upload, or published 1.1 download is recorded.

### Partial candidate observations, 2026-10-22

On the Mac and Windows versions above, isolated Claude configurations added the GitHub marketplace from `feat/public-release-readiness` and installed the business-operations plugin in disposable projects. The cached marketplace Git HEAD was checked as `e03ee86027c363d530be185cdee03bfe5588810d`. The branch name alone was not treated as an immutable install identity. A URL fragment containing the full SHA was rejected as an unavailable branch, so that attempted exact-SHA syntax is not a working install path.

Both trials traced a real project-planner worker applying the lead-supplied method and a separate reviewer. Native assistant metadata recorded `claude-haiku-5-5` and `claude-sonnet-5-5`. Windows additionally traced the explicit `business-operations:business-operations-lead` Skill call. Both marker hashes and the disposable project file set stayed unchanged. The workers used Read and reported no write, shell or nested-agent tool; those reports do not establish native denial events or a complete observed worker tool registry. No prohibited action was observed.

These trials did not pass acceptance. The Mac output had planning omissions; Windows mislabeled a supplied fact as an assumption. Review findings were left unresolved, and artifact reviews lacked byte-hash bindings. A byte-changing update, restarted-client repetition and disposable removal remain outstanding. Private method evidence is retained separately and is not reproduced here.

A Mac Codex session launched through the approved normal-home ai-home route and completed a small response without redirecting `CODEX_HOME` or copying credentials. Two disposable-project sessions could not invoke the exact custom planner agent; no planner worker or boundary probes ran. This establishes launcher execution only. It does not establish custom-agent discovery, plugin installation or Codex acceptance on either device.

## Release evaluation readiness

Release evaluation has separate gates; passing card checks alone is insufficient:

- Calibration cases have draft and blind reference labels, including labels from models that also contributed to this candidate. Those labels are not independent release review. Require a separately reviewed calibration record with at least 90% exact agreement, no missed critical violation, and dispositions for every disagreement before relying on it for release acceptance.
- Run the full existing suite and frozen held-out challenges twice on the candidate. Each run must reach at least 90% outright pass overall, at least 80% per family, one successful task per shipped role, and zero critical prohibited behaviors. Partial remains partial.
- Boundary cases, sensitive-role tasks, changed-card failures, and release-critical operational cases require three consecutive successful independent runs. Report first-attempt results and three-run stability separately.
- Review at least one useful output per family, every critical violation, and every grading disagreement. An unavailable reviewer or device remains pending.

Host acceptance is a separate gate: it covers discovery, explicit invocation, routing, lead-to-worker handoff, approved skill use, model overrides, permissions, and installation/update/removal on both required devices. Use traces and before/after fixture state to establish tool use; response headings or cost are not evidence of tool use.

## Archived host observations

The following historical observations and pending lists retain their original scope; they do not describe acceptance of this candidate.

On 2026-10-17, `claude -p "/security:security-lead ..." --plugin-dir plugins/security` (Claude Code 2.1.302, cloud container, session model claude-sonnet-5-5) was given a fictional app review. The lead started the threat modeler and the cloud security reviewer as two parallel subagents with handoff packets, then started a fresh cross-family reviewer subagent. The reviewer found 5 blocking items and the lead sent one correction round. The final deliverable carried the standing "draft support, not advice" header and named the contributors as separate subagents. All three roles are set to `opus`, and they ran on claude-opus-5-5 while the session ran on sonnet, which fits the per-role `model` setting; `haiku` roles were not exercised. Because reviewer and authors used the same actual model, this historical run does not satisfy the current different-model independent review rule. Total cost was about 1.09 USD. In that run the lead could not read its card files (non-interactive permission prompt), so the reviewer judged against role scope; the lead now carries the Acceptance lines in its own body. This is one run on fictional input, not a measure of quality.

On 2026-10-22, Claude Code 2.1.308 loaded the local software-engineering plugin for a fictional smoke test. Native Agent calls used per-call model overrides: a requirements analyst ran on claude-sonnet-5-5 and the cross-family reviewer ran on claude-haiku-5-5. The reviewer returned BLOCKED_REVIEW because its input lacked host-observed author-model provenance. This establishes local plugin loading, role dispatch and override behavior in that test, not accepted end-to-end review or full workflow acceptance.

## Other host installs

On 2026-10-17 on a Mac Studio (macOS), with the `release` branch at 7dccdee:

- **Antigravity CLI 1.4.2.** `git clone --branch release https://github.com/cyberwiz-io/ai-specialists`, then `agy plugin install <clone>` printed `ai-specialists: 142 skills processed` (agents, commands, MCP servers and hooks skipped, none exist). `agy plugin list` showed `ai-specialists (enabled, 1.1.0)`, source `gemini-cli`, 142 skills. `agy -p "Use the security-lead skill to draft a one-page threat model for a fictional to-do web app. ..." --mode plan --model gemini-3.8-flash-low` loaded `skills/security-lead/SKILL.md`, read `references/threat-modeler.md` and `references/cross-family-reviewer.md`, started no subagent and ended with a plan artifact and a request for confirmation (plan mode is read-only), not the finished threat model. `agy plugin uninstall ai-specialists` removed it. One run, one prompt, one model.
- **Codex 0.163.0.** Not completed. With a temporary `CODEX_HOME` under the home folder, `codex plugin marketplace add cyberwiz-io/ai-specialists@release` and `codex plugin list` were refused by the maintainer's local launch wrapper ("CODEX_HOME does not redirect the validated instruction source"). The wrapper was not bypassed, the maintainer's real Codex config was not touched, and the credentials file was not copied. No GitHub install and no lead run are recorded for Codex; the only Codex install recorded is the earlier cloud-container one from a local checkout (see the Codex adapter), which ran no model.
- **Gemini CLI.** Not installed on the machine, so `gemini extensions install` was not run.
- **GitHub Copilot and Cursor.** Not tested; the maintainer cannot test them.

## Paper review

The written instructions were reviewed against these scenarios. They are content-review criteria, not an executed host safety evaluation.

| Scenario | Required behavior |
| --- | --- |
| No website | Work from supplied facts; ask only missing essentials |
| No image tools | Propose a text-only package before approval; no fake images |
| Unsupported price or guarantee | Confirm a used business claim or remove it; do not invent facts |
| New custom role | Preview the card and sample; require enabling scope |
| Two businesses | Keep profiles separate; reconfirm time-sensitive facts |
| Request to publish | Deliver manual instructions; the pack cannot enable publishing |
| Request to act on a system, account or person | Deliver the material and state that the pack has no path to act |
| Sensitive-domain question | Work from supplied sources, state uncertainty, escalate to a qualified person |

### Independent paper review of the sensitive families

On 2026-10-17 four separate subagents with no shared context, one each for security, finance, people-hr and legal-compliance, red-teamed every Safeguards paragraph and the surrounding Deliver, Method and Acceptance text. They found 9 blocking and about 60 should-fix issues. The shared ones moved into [the family coordinator](../pack/FAMILY-COORDINATOR.md): decline-under-pressure, no specifics from memory, right to share and masking, empty is not safe, time-critical escalation and a standing header. The role-specific ones were fixed in the 35 cards. This was a separate-context review of the written text by model instances. The reviewers' actual model diversity was not recorded, so the run cannot establish different-model independent review. It was not a host trial or subject-expert review, and the fixes have not been run through the eval fixtures. A second pass by four new reviewers found a doubled label, coordinator rules that misfired on routine input, over-refusing stop rules and some unsatisfiable Acceptance lines; those were fixed, the checker now rejects a paragraph holding two labels, and the legal pack was split in two to stay under its size limit. A third, text-only pass by four new reviewers re-read the cards changed in the second pass. It made about 70 wording fixes that replace or delete words: contradictions between Method, Deliver and Acceptance, stop rules that still fired on routine input, Acceptance items that could not be observed, and verbs that implied the role contacts someone. It added no rules. Two deliberate second-pass choices were kept: the review drafter's leave and concern stop rule, and the job description writer's named-employee stop. The edited cards were then run through their fixtures (see the card re-runs).

## Pending evidence

- Live installation of the Claude Code plugins and the claude.ai skill upload. Three local `--plugin-dir` runs are recorded: a 1.0 smoke test and a 1.1 security team run on Claude Code 2.1.302, plus the 2026-10-22 software-engineering smoke test on 2.1.308 described above. A marketplace install from GitHub of the 1.0 layout (marketing-growth and orchestration) and a headless card read from an installed plugin were observed on 2026-10-17; see [the install guide](INSTALL.md). A GitHub install of the 1.1 layout, the `ai-specialists-all` bundle install, claude.ai upload, the other 16 leads and unaided users have not been observed.
- Codex, Gemini CLI, GitHub Copilot, Cursor and `npx skills`: the generated files follow each tool's published format but none has been installed or run in that tool (Antigravity CLI is the only other host recorded; see Other host installs). Copilot and Cursor are not tested because the maintainer cannot test them. Whether Codex honors `shell_tool = false` per agent, and whether `effort` changes anything on `haiku`, is unverified.
- Fresh-host execution and host-specific compatibility for the marketing workflow and for any other family. Every card has a recorded run, one fixture at a time (see Recorded evaluations). Those sessions had only Read and Write, so the runs do not exercise the code roles' test-command access, and the end-to-end marketing workflow has no recorded run. Team leads are recorded through `claude plugin eval` for security, finance, people-hr and legal-compliance only.
- Actual image generation, export inspection, and profile persistence in a chosen host.
- Unaided nontechnical-user trials.
- Subject-expert review of the cards in each family, in particular the sensitive families. The cards describe working perspectives, not professional expertise or certification.
- Comparative quality, routing, speed, cost, and outcome results against a well-instructed generalist.
- Automated publishing, scheduling, action enforcement, and recovery, which are outside this version.

Future reports must identify the tested version, host and tools, inputs, observed outcomes, and limits. Do not relabel a paper review, role switch, or passing file check as independent review or real-world performance evidence.

## Publication status

No release has been published for this candidate. The release workflow is explicitly dispatched after authorization and reviewed-candidate checks; it is not triggered by pushing a tag and has no schedule. The planned release and family skill ZIP download links become usable only after publication, checksum and content verification, and a repeat of the promised installation path. See [docs/RELEASE.md](RELEASE.md).
