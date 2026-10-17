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
- each family's plugin has a valid skill name and description length, working links from its `SKILL.md` to its references, one read-only subagent per card, and an entry in the marketplace and the install guide; the release also writes and verifies one upload-ready skill ZIP per family.

These are structural checks of the written instructions.

## Evaluation harness

The [card evaluation harness](../evals/README.md) produces the reports this page asks for. Every card has at least one fictional task fixture, and every family has a boundary fixture that asks for an external action. Claude Code runs each fixture in a fresh subagent, using the shipped combined pack. A separate fresh subagent then grades the reply against the card's own Acceptance line and the fixture's expected traits. `python3 -B scripts/evals.py report` writes a report with the tested version and commit, host and tools, models, inputs, outcomes and limits.

## Recorded evaluations

None yet. The harness is built, but no run has been recorded, so the fresh-host evidence below is still pending. Reviewed reports go in [evals/reports](../evals/reports/README.md) and are linked here.

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

- Live installation of the Claude Code plugins and the claude.ai skill upload: whether the skills trigger on a plain task description, whether cards load on demand, and whether subagents are chosen by name. Only a local smoke test is recorded (Claude Code 2.1.302, `--plugin-dir`, plugin loaded and a card read on demand); marketplace install from GitHub, claude.ai upload and unaided users have not been observed.
- Fresh-host execution and host-specific compatibility for the marketing workflow and for any other family. The evaluation harness can now produce this evidence, but no run is recorded.
- Actual image generation, export inspection, and profile persistence in a chosen host.
- Unaided nontechnical-user trials.
- Subject-expert review of the cards in each family, in particular the sensitive families. The cards describe working perspectives, not professional expertise or certification.
- Comparative quality, routing, speed, cost, and outcome results against a well-instructed generalist.
- Automated publishing, scheduling, action enforcement, and recovery, which are outside this version.

Future reports must identify the tested version, host and tools, inputs, observed outcomes, and limits. Do not relabel a paper review, role switch, or passing file check as independent review or real-world performance evidence.
