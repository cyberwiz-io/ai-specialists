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

These are structural checks of the written instructions.

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

## Pending evidence

- Fresh-host execution and host-specific compatibility for the marketing workflow and for any other family.
- Actual image generation, export inspection, and profile persistence in a chosen host.
- Unaided nontechnical-user trials.
- Subject-expert review of the cards in each family, in particular the sensitive families. The cards describe working perspectives, not professional expertise or certification.
- Comparative quality, routing, speed, cost, and outcome results against a well-instructed generalist.
- Automated publishing, scheduling, action enforcement, and recovery, which are outside this version.

Future reports must identify the tested version, host and tools, inputs, observed outcomes, and limits. Do not relabel a paper review, role switch, or passing file check as independent review or real-world performance evidence.
