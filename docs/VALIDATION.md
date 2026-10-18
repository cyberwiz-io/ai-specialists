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
- the Codex, Gemini CLI, Copilot and Cursor outputs parse and follow their documented shape, and every generated file matches its source. On 2026-10-17 every generated file was also checked against the vendors' current documentation (Agent Skills specification, Codex plugin and subagent docs, Gemini CLI extension and skills reference, Copilot custom agent reference, Cursor plugin reference). All passed after one fix: the Codex `interface.shortDescription` now fits the documented 30 characters. The plugin role skills carry the Claude Code field `disable-model-invocation`, which the strict Agent Skills validator rejects; the root `skills/` copies do not. Cursor documents only `name` and `description` for agents, so the read-only tool limits probably do not apply there. No vendor publishes a JSON schema, so these checks follow the prose docs;
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
| [2026-10-17-catalog](../evals/reports/2026-10-17-catalog.md) | Every card, 141 fixtures (124 task, 17 boundary), pack 1.1 | Claude Code 2.1.302 (cloud), claude-opus-5-5 graded by claude-opus-5-5, one fresh `claude -p` session per reply and per grade | 78 pass, 59 partial, 4 fail |
| [2026-10-17-catalog-reruns](../evals/reports/2026-10-17-catalog-reruns.md) | Re-runs of the cards edited after the full run: security, finance, people-hr, legal-compliance (with the three boundary fixtures from PR #8), cover letter writer, meeting facilitator | Same as the full run | Latest result per role: 23 pass, 22 partial, 0 fail across 45 fixtures |
| [2026-10-17-plugin-evals](../evals/reports/2026-10-17-plugin-evals.md) | `claude plugin eval` for security (re-run), finance, people-hr and legal-compliance, each with a team task; the three new ones chain three specialists | Claude Code 2.1.302 (cloud), host default model, LLM judge | Security with plugin 3 of 7 (fired on 5 of 7); every team task ran its specialists and a separate reviewer; one finance chain passed after a lead fix |
| [2026-10-17-se-code-reviewer](../evals/reports/2026-10-17-se-code-reviewer.md) | Software engineering code reviewer, 2 fixtures (1 task, 1 boundary), pack 1.1 | Claude Code (cloud), claude-sonnet-5-5 graded by claude-sonnet-5-5 | 1 pass, 1 partial, 0 fail |
| [2026-10-17-se-debugging-analyst](../evals/reports/2026-10-17-se-debugging-analyst.md) | Software engineering debugging analyst, 1 fixture (task), pack 1.1 | Claude Code (cloud), claude-sonnet-5-5 graded by claude-sonnet-5-5 | 1 pass, 0 partial, 0 fail |

The regression baseline in `evals/baseline.json` is the full-catalog run with the re-runs laid over it for the roles they cover: 80 of 144 fixtures pass outright, every card is included, and the model and grader are claude-opus-5-5. Partial results mostly mark one trait or Acceptance item missed. The earlier marketing-growth run used the `core/` role IDs of its commit, later renamed `marketing-growth/`. Each result is a single model-graded run on fictional inputs, as each report's Limits section says.

## Team lead run

On 2026-10-17, `claude -p "/security:security-lead ..." --plugin-dir plugins/security` (Claude Code 2.1.302, cloud container, session model claude-sonnet-5-5) was given a fictional app review. The lead started the threat modeler and the cloud security reviewer as two parallel subagents with handoff packets, then started a fresh cross-family reviewer subagent. The reviewer found 5 blocking items and the lead sent one correction round. The final deliverable carried the standing "draft support, not advice" header and named the contributors as separate subagents. All three roles are set to `opus`, and they ran on claude-opus-5-5 while the session ran on sonnet, which fits the per-role `model` setting; `haiku` roles were not exercised. Total cost was about 1.09 USD. In that run the lead could not read its card files (non-interactive permission prompt), so the reviewer judged against role scope; the lead now carries the Acceptance lines in its own body. This is one run on fictional input, not a measure of quality.

## Other host installs

On 2026-10-17 on a Mac Studio (macOS), with the `release` branch at 7dccdee:

- **Antigravity CLI 1.4.2.** `git clone --branch release https://github.com/cyberwiz-io/ai-specialists`, then `agy plugin install <clone>` printed `ai-specialists: 142 skills processed` (agents, commands, MCP servers and hooks skipped, none exist). `agy plugin list` showed `ai-specialists (enabled, 1.1.0)`, source `gemini-cli`, 142 skills. `agy -p "Use the security-lead skill to draft a one-page threat model for a fictional to-do web app. ..." --mode plan --model gemini-3.8-flash-low` loaded `skills/security-lead/SKILL.md`, read `references/threat-modeler.md` and `references/cross-family-reviewer.md`, started no subagent and ended with a plan artifact and a request for confirmation (plan mode is read-only), not the finished threat model. `agy plugin uninstall ai-specialists` removed it. One run, one prompt, one model.
- **Codex 0.163.0.** Not completed. With a temporary `CODEX_HOME` under the home folder, `codex plugin marketplace add cyberwiz-io/ai-specialists@release` and `codex plugin list` were refused by the maintainer's local launch wrapper ("CODEX_HOME does not redirect the validated instruction source"). The wrapper was not bypassed, the maintainer's real Codex config was not touched, and the credentials file was not copied. No plugin install and no lead run are recorded for Codex.
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

On 2026-10-17 four separate subagents with no shared context, one each for security, finance, people-hr and legal-compliance, red-teamed every Safeguards paragraph and the surrounding Deliver, Method and Acceptance text. They found 9 blocking and about 60 should-fix issues. The shared ones moved into [the family coordinator](../pack/FAMILY-COORDINATOR.md): decline-under-pressure, no specifics from memory, right to share and masking, empty is not safe, time-critical escalation and a standing header. The role-specific ones were fixed in the 35 cards. This is independent review of the written text by model instances, not a host trial or subject-expert review, and the fixes have not been run through the eval fixtures. A second pass by four new reviewers found a doubled label, coordinator rules that misfired on routine input, over-refusing stop rules and some unsatisfiable Acceptance lines; those were fixed, the checker now rejects a paragraph holding two labels, and the legal pack was split in two to stay under its size limit. A third, text-only pass by four new reviewers re-read the cards changed in the second pass. It made about 70 wording fixes that replace or delete words: contradictions between Method, Deliver and Acceptance, stop rules that still fired on routine input, Acceptance items that could not be observed, and verbs that implied the role contacts someone. It added no rules. Two deliberate second-pass choices were kept: the review drafter's leave and concern stop rule, and the job description writer's named-employee stop. The edited cards were then run through their fixtures (see the card re-runs).

## Pending evidence

- Live installation of the Claude Code plugins and the claude.ai skill upload. Two local runs are recorded, both with `--plugin-dir` on Claude Code 2.1.302: a 1.0 smoke test that loaded a plugin and read a card on demand, and a 1.1 team run of `/security:security-lead` (below). A marketplace install from GitHub of the 1.0 layout (marketing-growth and orchestration) and a headless card read from an installed plugin were observed on 2026-10-17; see [the install guide](INSTALL.md). A GitHub install of the 1.1 layout, the `ai-specialists-all` bundle install, claude.ai upload, the other 16 leads and unaided users have not been observed.
- Codex, Gemini CLI, GitHub Copilot, Cursor and `npx skills`: the generated files follow each tool's published format but none has been installed or run in that tool (Antigravity CLI is the only other host recorded; see Other host installs). Copilot and Cursor are not tested because the maintainer cannot test them. Whether Codex honors `shell_tool = false` per agent, and whether `effort` changes anything on `haiku`, is unverified.
- Fresh-host execution and host-specific compatibility for the marketing workflow and for any other family. Every card has a recorded run, one fixture at a time (see Recorded evaluations). Those sessions had only Read and Write, so the runs do not exercise the code roles' test-command access, and the end-to-end marketing workflow has no recorded run. Team leads are recorded through `claude plugin eval` for security, finance, people-hr and legal-compliance only.
- Actual image generation, export inspection, and profile persistence in a chosen host.
- Unaided nontechnical-user trials.
- Subject-expert review of the cards in each family, in particular the sensitive families. The cards describe working perspectives, not professional expertise or certification.
- Comparative quality, routing, speed, cost, and outcome results against a well-instructed generalist.
- Automated publishing, scheduling, action enforcement, and recovery, which are outside this version.

Future reports must identify the tested version, host and tools, inputs, observed outcomes, and limits. Do not relabel a paper review, role switch, or passing file check as independent review or real-world performance evidence.
