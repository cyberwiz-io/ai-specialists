# AI Specialists

A library of 124 specialist instruction cards in 17 families, plus a coordinator, for the AI assistant you already have. Describe a task, and the coordinator guides the right specialist perspectives through it. The best-developed path is a small-business marketing campaign.

**Version 1.3 candidate · Materials only · [Validation status](docs/VALIDATION.md)**

## Install options

These are candidate install instructions. Current Claude Code and Codex acceptance on macOS and Windows is pending, and no 1.3 release has been published. The download links below are kept for the planned release; usable release downloads will exist only after publication and verification.

| Tool | Command or step |
| --- | --- |
| Claude Code (all families) | `/plugin install ai-specialists-all --marketplace cyberwiz-io/ai-specialists` |
| Claude Code (one family) | `/plugin marketplace add cyberwiz-io/ai-specialists`, then `/plugin install security@ai-specialists` |
| claude.ai and Claude Desktop | Planned: upload `ai-specialists-1.3-skill-<family>.zip` from the [release downloads](https://github.com/cyberwiz-io/ai-specialists/releases/latest) in Settings, Capabilities, Skills (pending publication) |
| Any Agent Skills host | `npx skills add cyberwiz-io/ai-specialists` |
| Codex | `codex plugin marketplace add cyberwiz-io/ai-specialists` |
| Gemini CLI | `gemini extensions install https://github.com/cyberwiz-io/ai-specialists` |
| GitHub Copilot | `mkdir -p .github/agents && cp adapters/copilot/agents/*.agent.md .github/agents/` from a checkout |
| Cursor | Customize, From GitHub Repository, `cyberwiz-io/ai-specialists` |
| Any chat assistant | Paste one file from `dist/packs/` (a whole family) or one `skills/<family>-<slug>/SKILL.md` (one role) |

For Claude Code, a lead can use only the tools and delegation behavior the host actually provides. Its workers have `Read`, `Grep`, and `Glob` only; they have no `Bash` or automatic skill tool. Leads pass any approved methods explicitly in task handoffs. Codex's no-spawn direction is advisory and depends on host controls. See the [install guide](docs/INSTALL.md) and [host acceptance](docs/HOST-ACCEPTANCE.md).

Then give a family's team lead your task, for example `/security:security-lead Review the sign-in flow of my shop app` in Claude Code. The lead picks one to three specialists and uses real subagents for suitable independent work when supported. Nontrivial output needs an adversarial reviewer using a different actual model from every author and checking the exact result version and byte hash; changed bytes void review; otherwise its status is BLOCKED_REVIEW. In plain chat the lead may use role perspectives inline and states which agents and reviews did not run. Per-tool details and limits are in the [install guide](docs/INSTALL.md).

## What you get

These are editable instruction files: one card per specialist, a team lead per family, and a cross-family `/specialists` lead. Nothing is posted, sent, scheduled, deployed or changed by them. In Claude Code each specialist is a read-only subagent with a default model tier (haiku, sonnet or opus); the lead uses host-observed capability and available cost evidence for selection, preferring eligible local only on a known total-cost tie; if cost is unknown, it reports BLOCKED_MODEL/COST and does not claim ready or complete. Only leads start subagents. Fixed tiers do not prove lowest cost, and no new charge is authorized by this pack. Claude Code workers have only `Read`, `Grep`, and `Glob`, with no `Bash` or automatic skill tool. Leads pass approved methods explicitly in handoffs. Codex workers inherit the parent model; no-spawn instructions are advisory and depend on parent controls.

**Paste a pack, in any assistant.**

1. Pick a family below and open its combined pack under `dist/packs/` (select **Raw**), or open [the marketing starter pack](pack/STARTER-PACK.md). Copy it into a new conversation with an AI assistant you trust, or supply the file with that assistant's file feature. Need only one role? Paste its `skills/<family>-<slug>/SKILL.md` instead, about a tenth of the size.
2. Describe your task. For marketing: *Use this starter pack. My business is [short description]. My website is [optional]. Help me create a marketing campaign. First confirm that you can read all eight instruction sections.* For another family: *Use this pack. My task is [description]. Here is the material I can supply: [...]. First confirm that you can read all the sections.*
3. Confirm the plan, review the materials, and accept or revise.

Prefer a download? The planned [release downloads](https://github.com/cyberwiz-io/ai-specialists/releases/latest) will contain a ZIP with every card, pack, skill and install file, attribution and licenses after publication and checksum verification. No current 1.3 download is available; open `pack/START-HERE.md` in this candidate checkout.

## Families

Each family has a pasteable combined pack and an index of its specialists. Every pack stays under 32 KB, about 8,000 tokens, so it fits in a 16,000-token context window with room to work; Security is split into three packs and legal and compliance into two to stay under that limit.

| Family | Specialists | Index | Combined pack |
| --- | --- | --- | --- |
| Marketing and growth | 10 | [index](catalog/marketing-growth/INDEX.md) | [pack](dist/packs/marketing-growth.md) |
| Content and creative | 8 | [index](catalog/content-creative/INDEX.md) | [pack](dist/packs/content-creative.md) |
| Sales and customer | 8 | [index](catalog/sales-customer/INDEX.md) | [pack](dist/packs/sales-customer.md) |
| Business operations | 8 | [index](catalog/business-operations/INDEX.md) | [pack](dist/packs/business-operations.md) |
| Product and design | 7 | [index](catalog/product-design/INDEX.md) | [pack](dist/packs/product-design.md) |
| Software engineering | 11 | [index](catalog/software-engineering/INDEX.md) | [pack](dist/packs/software-engineering.md) |
| AI and machine learning | 3 | [index](catalog/ai-ml/INDEX.md) | [pack](dist/packs/ai-ml.md) |
| IT operations | 5 | [index](catalog/it-operations/INDEX.md) | [pack](dist/packs/it-operations.md) |
| Data and research | 8 | [index](catalog/data-research/INDEX.md) | [pack](dist/packs/data-research.md) |
| Education and training | 6 | [index](catalog/education-training/INDEX.md) | [pack](dist/packs/education-training.md) |
| Public sector and nonprofit | 5 | [index](catalog/public-nonprofit/INDEX.md) | [pack](dist/packs/public-nonprofit.md) |
| Personal and career | 5 | [index](catalog/personal-career/INDEX.md) | [pack](dist/packs/personal-career.md) |
| Orchestration and meta | 5 | [index](catalog/orchestration/INDEX.md) | [pack](dist/packs/orchestration.md) |
| Security (sensitive) | 14 | [index](catalog/security/INDEX.md) | Three packs: [engineering](dist/packs/security-engineering.md) (5), [operations](dist/packs/security-operations.md) (3), [governance and privacy](dist/packs/security-governance.md) (6) |
| Finance (sensitive) | 8 | [index](catalog/finance/INDEX.md) | [pack](dist/packs/finance.md) |
| People and HR (sensitive) | 5 | [index](catalog/people-hr/INDEX.md) | [pack](dist/packs/people-hr.md) |
| Legal and compliance (sensitive) | 8 | [index](catalog/legal-compliance/INDEX.md) | Two packs: [documents](dist/packs/legal-compliance-documents.md) (4), [rules and policies](dist/packs/legal-compliance-rules.md) (4) |

The [marketing Coordinator](pack/COORDINATOR.md) and [marketing workflow](pack/MARKETING-WORKFLOW.md) keep campaign decisions and handoffs consistent; the [family coordinator](pack/FAMILY-COORDINATOR.md) does the same for every other family. You can [customize a specialist](pack/CUSTOM-SPECIALISTS.md) in plain language and preview it before enabling it. A [reviewed business profile](pack/BUSINESS-PROFILE.md) is optional.

## Explore and contribute

Humans and AI agents should begin with the [repository map](REPO-MAP.md), which routes each task to the few files that matter. Read [Install](docs/INSTALL.md) and [Start here](pack/START-HERE.md) for setup details, the [card guide](docs/CARD-GUIDE.md) to write a role, the [roadmap](docs/ROADMAP.md) for future work, and [Contributing](CONTRIBUTING.md) to suggest or make changes.

## Know the limits

- These are advisory instructions, not an enforced permission system. Your assistant's rules and tools still govern its behavior. Lead routing instructions are advisory. Claude applies configured worker defaults unless a supported task override takes precedence; Codex inherits the parent model. Record the model the host actually reports.
- Security, finance, people and HR, and legal and compliance cards are defensive or educational support for material you supply. They are not professional advice and make no claim of compliance or certification. Consult a qualified person for consequential decisions.
- Research, image generation, file exports, memory, and separate review contexts depend on the host. Missing capabilities should produce a smaller agreed package, not pretend outputs.
- Switching roles or starting a fresh context with the same actual model does not provide independent review. Nontrivial results need a different actual reviewer model and an exact artifact/version; otherwise report BLOCKED_REVIEW.
- Current acceptance for Claude Code and Codex on macOS and Windows is pending. Older smoke tests, evaluations, and other-host observations are historical evidence only and do not establish current support. No release has been published for this candidate. See [Validation status](docs/VALIDATION.md).
- The project has no accounts, connectors, telemetry, or model service. Your chosen host may process information in the cloud and has its own usage limits and data policies. Never supply credentials or private customer data to this pack.

## License

Instructional content, documentation, and examples are licensed under **CC BY 4.0**. Maintenance code and automation are licensed under **Apache-2.0**. See [NOTICE](NOTICE.md) and [license coverage](LICENSE.md) for attribution and exact file coverage.
