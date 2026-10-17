# Validation status

This repository is an instruction pack. Checks of files and instructions do not prove that an AI host follows them reliably.

## Automated checks

Run `python3 -B scripts/pack.py check` and the test command in [Contributing](../CONTRIBUTING.md) to verify the current checkout. Together they verify that:

- the roster in `catalog/families.json` matches the cards on disk (124 specialists in 17 families), with unique IDs;
- each card has the required labels in order, the right ID and version, and its Coordinator-boundary sentence;
- sensitive-family cards carry a Safeguards paragraph covering sources, uncertainty, authorization, escalation and "not advice";
- restricted words (publish, deploy, credential, connect, certified and similar) appear only where a card rules them out, and no card names a law, standard or framework;
- every handoff names a real role ID, cards and combined packs stay under their size limits, and no two cards share a deliverable;
- generated files (indexes, registry, combined packs, module map) match their sources, each combined pack is under 32 KB, local links resolve, every source file belongs to a module, and no archive is committed;
- the release command rebuilds the archive and verifies its members and bytes before CI attaches it to a tagged release.

- every card has an evaluation fixture and every family a boundary fixture, with fictional data only;
- every `SKILL.md` (root `skills/`, plugins and the Codex plugin) has a 1 to 64 character lowercase name matching its folder, a description within limits, and only the six Agent Skills frontmatter fields (plugin role skills may add `disable-model-invocation`);
- the marketplace and each `plugin.json` have the required keys, every plugin entry points to a real folder, no name keeps the old `core-` prefix, and the `ai-specialists-all` bundle stays under its description budget;
- each family's plugin has its lead skill with working links to its references, one worker agent per card, and an entry in the marketplace and the install guide; no worker has the Agent tool, and only the four code roles have allowlisted commands; the release also writes and verifies one upload-ready skill ZIP per family;
- the Codex, Gemini CLI, Copilot and Cursor outputs parse and follow their documented shape, and every generated file matches its source;
- CI runs `claude plugin validate --strict` (Claude Code 2.1.302) on the marketplace, all 17 plugins, `skills/` and the Codex plugin. It passed on this branch.

These are structural checks of the written instructions.

## Evaluation harness

The [card evaluation harness](../evals/README.md) produces the reports this page asks for. Every card has at least one fictional task fixture, and every family has a boundary fixture that asks for an external action. Claude Code runs each fixture in a fresh subagent, using the shipped combined pack. A separate fresh subagent then grades the reply against the card's own Acceptance line and the fixture's expected traits. `python3 -B scripts/evals.py report` writes a report with the tested version and commit, host and tools, models, inputs, outcomes and limits.

## Recorded evaluations

Reviewed reports go in [evals/reports](../evals/reports/README.md) and are linked here.

| Run | Scope | Host and model | Outcome |
| --- | --- | --- | --- |
| [2026-10-17-marketing-growth](../evals/reports/2026-10-17-marketing-growth.md) | Marketing and growth family, 11 fixtures (10 task, 1 boundary) | Claude Code (cloud), claude-opus-5-5 graded by claude-opus-5-5 | 6 pass, 3 partial, 2 fail |
| [2026-10-17-security-plugin-pilot](../evals/reports/2026-10-17-security-plugin-pilot.md) | Security plugin via `claude plugin eval`, 7 cases (5 task, 1 boundary, 1 team), with and without the plugin | Claude Code 2.1.302 (cloud), host default model, LLM judge | With plugin 1 of 7, without 0 of 7; the plugin fired on 3 of 7 plain prompts |
| [2026-10-17-se-code-reviewer](../evals/reports/2026-10-17-se-code-reviewer.md) | Software engineering code reviewer, 2 fixtures (1 task, 1 boundary), pack 1.1 | Claude Code (cloud), claude-sonnet-5-5 graded by claude-sonnet-5-5 | 1 pass, 1 partial, 0 fail |
| [2026-10-17-se-debugging-analyst](../evals/reports/2026-10-17-se-debugging-analyst.md) | Software engineering debugging analyst, 1 fixture (task), pack 1.1 | Claude Code (cloud), claude-sonnet-5-5 graded by claude-sonnet-5-5 | 1 pass, 0 partial, 0 fail |

This run is also the regression baseline in `evals/baseline.json`. The report keeps the role IDs of its commit; the four `core/` roles it names were later renamed `marketing-growth/` without other card changes, and the baseline uses the new IDs. It covers one family only; the other families have no recorded run, so their fresh-host evidence below is still pending. Each result is a single model-graded run on fictional inputs, as the report's Limits section says.

## Team lead run

On 2026-10-17, `claude -p "/security:security-lead ..." --plugin-dir plugins/security` (Claude Code 2.1.302, cloud container, session model claude-sonnet-5-5) was given a fictional app review. The lead started the threat modeler and the cloud security reviewer as two parallel subagents with handoff packets, then started a fresh cross-family reviewer subagent. The reviewer found 5 blocking items and the lead sent one correction round. The final deliverable carried the standing "draft support, not advice" header and named the contributors as separate subagents. All three roles are set to `opus`, and they ran on claude-opus-5-5 while the session ran on sonnet, which fits the per-role `model` setting; `haiku` roles were not exercised. Total cost was about 1.09 USD. In that run the lead could not read its card files (non-interactive permission prompt), so the reviewer judged against role scope; the lead now carries the Acceptance lines in its own body. This is one run on fictional input, not a measure of quality.

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

On 2026-10-17 four separate subagents with no shared context, one each for security, finance, people-hr and legal-compliance, red-teamed every Safeguards paragraph and the surrounding Deliver, Method and Acceptance text. They found 9 blocking and about 60 should-fix issues. The shared ones moved into [the family coordinator](../pack/FAMILY-COORDINATOR.md): decline-under-pressure, no specifics from memory, right to share and masking, empty is not safe, time-critical escalation and a standing header. The role-specific ones were fixed in the 35 cards. This is independent review of the written text by model instances, not a host trial or subject-expert review, and the fixes have not been run through the eval fixtures. A second pass by four new reviewers found a doubled label, coordinator rules that misfired on routine input, over-refusing stop rules and some unsatisfiable Acceptance lines; those were fixed, the checker now rejects a paragraph holding two labels, and the legal pack was split in two to stay under its size limit. The second-pass fixes have not been reviewed again.

## Pending evidence

- Live installation of the Claude Code plugins and the claude.ai skill upload. Two local runs are recorded, both with `--plugin-dir` on Claude Code 2.1.302: a 1.0 smoke test that loaded a plugin and read a card on demand, and a 1.1 team run of `/security:security-lead` (below). A marketplace install from GitHub of the 1.0 layout (marketing-growth and orchestration) and a headless card read from an installed plugin were observed on 2026-10-17; see [the install guide](INSTALL.md). A GitHub install of the 1.1 layout, the `ai-specialists-all` bundle install, claude.ai upload, the other 16 leads and unaided users have not been observed.
- Codex, Gemini CLI, GitHub Copilot, Cursor and `npx skills`: the generated files follow each tool's published format but none has been installed or run in that tool. Whether Codex honors `shell_tool = false` per agent, and whether `effort` changes anything on `haiku`, is unverified.
- Fresh-host execution and host-specific compatibility for the marketing workflow and for any other family. Card runs are recorded one fixture at a time for the marketing and growth family and for two software-engineering roles, the code reviewer and debugging analyst (see Recorded evaluations). Those subagents had only Read and Write, so the runs do not exercise the roles' test-command access; the end-to-end marketing workflow, the remaining software-engineering roles and the other families have no recorded card run (the security plugin pilot is listed separately).
- Actual image generation, export inspection, and profile persistence in a chosen host.
- Unaided nontechnical-user trials.
- Subject-expert review of the cards in each family, in particular the sensitive families. The cards describe working perspectives, not professional expertise or certification.
- Comparative quality, routing, speed, cost, and outcome results against a well-instructed generalist.
- Automated publishing, scheduling, action enforcement, and recovery, which are outside this version.

Future reports must identify the tested version, host and tools, inputs, observed outcomes, and limits. Do not relabel a paper review, role switch, or passing file check as independent review or real-world performance evidence.
