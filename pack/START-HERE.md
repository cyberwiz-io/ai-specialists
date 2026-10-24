# Specialist starter pack

Get finished written materials, plans and reviews from the AI system you already use. The marketing starter below is the best-developed path; 16 other families are in `dist/packs/`. No app, Terminal, Node, account connection or installation is required by this pack.

## Install instead of pasting

You can install a family as a skill and skip the paste. The [install guide](../docs/INSTALL.md) covers Claude Code, claude.ai, Codex, Gemini CLI, GitHub Copilot, Cursor and other Agent Skills hosts. Only Claude Code has been checked; the others are not yet tested. Otherwise, continue below.

## Minimal: one role

If you need only one specialist, paste a single `skills/<family>-<slug>/SKILL.md` into a new conversation, for example `skills/marketing-growth-copywriter/SKILL.md`. That is about 700 to 900 tokens. Then add: **“Use this role. My task is [description].”** You get that one role's perspective, without the team or a separate review.

## Start in one conversation

1. Open **STARTER-PACK.md**, copy its contents, and paste them into a new AI conversation. If you prefer your host's supported file feature, you may supply that file yourself. This pack does not upload or install itself.
2. Add: **“Use this starter pack. My business is [short description]. My website is [optional]. Help me create a marketing campaign.”**
3. Review the recommended goal, then one proposed campaign package. The assistant will ask only missing essentials, one question at a time. Review a sample visual if needed, then the finished materials.

Ask the assistant to confirm that it can read the Coordinator, workflow and four role sections before beginning. If the host cannot retain the whole pack, use a workspace that supports it or provide the relevant separate files as each stage begins, keeping COORDINATOR.md in scope. Do not rely on automatic file discovery.

Nothing is published, scheduled, sent or connected. Finished materials come with manual posting instructions. Use only a host you trust with the business information you provide. No new paid tool or service is required; your existing host's usage limits still apply.

## Other families

Open `dist/packs/<family>.md` for the family you need (for example `finance.md` or `software-engineering.md`), copy it into a new conversation, and add: **“Use this pack. My task is [description]. Here is the material I can supply: [...].”** Each pack includes the family coordinator and every specialist in that family. Security comes in three packs, `security-engineering.md`, `security-operations.md` and `security-governance.md`, and legal and compliance in two, `legal-compliance-documents.md` and `legal-compliance-rules.md`, so each fits smaller context windows. Security, finance, people and HR, and legal and compliance packs give support material, not professional advice; take consequential decisions to a qualified person.

## Make it yours

Say **“Create a specialist that…”** and describe its job. The assistant will explain whether to customize a role or create one, show a sample, and ask before enabling it. You can also ask to save a reviewed business profile, or choose to use the facts for this campaign only.

To pause, say **“Pause and give me a resume note.”** Continue in the same conversation or provide that note and this pack in a new one. Persistent memory depends on your host and must be verified.

## Files for developers and people who want details

- [Coordinator](COORDINATOR.md): shared behavior, permissions and handoffs.
- [Marketing workflow](MARKETING-WORKFLOW.md): the campaign from idea to delivered materials.
- [Family coordinator](FAMILY-COORDINATOR.md): the same shared behavior for every family except marketing.
- [Strategist](../catalog/marketing-growth/marketing-strategist.md), [copywriter](../catalog/marketing-growth/copywriter.md), [designer](../catalog/marketing-growth/graphic-designer.md), [reviewer](../catalog/marketing-growth/quality-reviewer.md): the four core role cards. All 124 cards are in [the repository map](../REPO-MAP.md).
- [Custom specialists](CUSTOM-SPECIALISTS.md): plain-language creation and a role template.
- [Business profiles](BUSINESS-PROFILE.md): optional reviewed reuse and export.

STARTER-PACK.md and the family packs combine those instructions for convenience. They are generated: edit the individual files, run the build, and do not load conflicting copies. A customized role still needs review before enablement. No host-specific agent configuration or executable framework is included.

## What this version does and does not establish

In plain chat one assistant may apply specialist perspectives inline; this does not mean agents ran. Hosts with subagents can delegate suitable independent work. Nontrivial deliverables require review by a different actual model from all authors, bound to a manifest of the exact final versions and byte hashes; changed bytes void review. A fresh same-model context does not qualify; unavailable review is BLOCKED_REVIEW. Research, images, files, storage and review depend on actual host capabilities. Missing capabilities require honest status and a feasible package.

This is a portable instruction pack, not an enforced security boundary or a certified integration with every host. It has been reviewed locally; fresh-host trials, unaided user tests and subject-expert review of the other families remain to be done. No claim of better marketing performance is established. 

Version 1.5, October 24, 2026. Instructional content is licensed under CC BY 4.0. See [attribution and license coverage](../NOTICE.md). This pack does not install itself or enable external actions.
