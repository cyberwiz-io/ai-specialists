# AI Specialists

A library of 124 specialist instruction cards in 17 families, plus a coordinator, for the AI assistant you already have. Describe a task, and the coordinator guides the right specialist perspectives through it. The best-developed path is a small-business marketing campaign.

**Version 1.1 · Materials only · [Validation status](docs/VALIDATION.md)**

## Install in 30 seconds

Pick your tool and copy one command. Only Claude Code has been checked; the other paths follow each tool's published format and are not yet tested.

| Tool | Command or step |
| --- | --- |
| Claude Code (all families) | `/plugin install ai-specialists-all --marketplace cyberwiz-io/ai-specialists` |
| Claude Code (one family) | `/plugin marketplace add cyberwiz-io/ai-specialists`, then `/plugin install security@ai-specialists` |
| claude.ai and Claude Desktop | Upload `ai-specialists-1.1-skill-<family>.zip` from the [latest release](https://github.com/cyberwiz-io/ai-specialists/releases/latest) in Settings, Capabilities, Skills |
| Any Agent Skills host | `npx skills add cyberwiz-io/ai-specialists` |
| Codex | `codex plugin marketplace add cyberwiz-io/ai-specialists` |
| Gemini CLI | `gemini extensions install https://github.com/cyberwiz-io/ai-specialists` |
| GitHub Copilot | `mkdir -p .github/agents && cp adapters/copilot/agents/*.agent.md .github/agents/` from a checkout |
| Cursor | Customize, From GitHub Repository, `cyberwiz-io/ai-specialists` |
| Any chat assistant | Paste one file from `dist/packs/` (a whole family) or one `skills/<family>-<slug>/SKILL.md` (one role) |

Then give a family's team lead your task, for example `/security:security-lead Review the sign-in flow of my shop app` in Claude Code. The lead picks one to three specialists, runs them as parallel subagents, has a fresh reviewer check the merged result, and returns one deliverable. In plain chat the same lead works through the roles itself and says the result is self-reviewed. Per-tool details and limits are in the [install guide](docs/INSTALL.md).

## What you get

These are editable instruction files: one card per specialist, a team lead per family, and a cross-family `/specialists` lead. Nothing is posted, sent, scheduled, deployed or changed by them. In Claude Code each specialist is a read-only subagent on a model sized to the job (haiku for writing, sonnet by default, opus for architects and reviewers), and only the leads start subagents.

**Paste a pack, in any assistant.**

1. Pick a family below and open its combined pack under `dist/packs/` (select **Raw**), or open [the marketing starter pack](pack/STARTER-PACK.md). Copy it into a new conversation with an AI assistant you trust, or supply the file with that assistant's file feature. Need only one role? Paste its `skills/<family>-<slug>/SKILL.md` instead, about a tenth of the size.
2. Describe your task. For marketing: *Use this starter pack. My business is [short description]. My website is [optional]. Help me create a marketing campaign. First confirm that you can read all eight instruction sections.* For another family: *Use this pack. My task is [description]. Here is the material I can supply: [...]. First confirm that you can read all the sections.*
3. Confirm the plan, review the materials, and accept or revise.

Prefer a download? The [latest release](https://github.com/cyberwiz-io/ai-specialists/releases/latest) has a ZIP with every card, pack, skill and install file, attribution and licenses; open `pack/START-HERE.md`.

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

- These are advisory instructions, not an enforced permission system. Your assistant's rules and tools still govern its behavior.
- Security, finance, people and HR, and legal and compliance cards are defensive or educational support for material you supply. They are not professional advice and make no claim of compliance or certification. Consult a qualified person for consequential decisions.
- Research, image generation, file exports, memory, and separate review contexts depend on the host. Missing capabilities should produce a smaller agreed package, not pretend outputs.
- Switching roles in one chat is self-review, not independent multi-agent review. Independent review needs a host with subagents, such as Claude Code with the plugins.
- Only Claude Code is checked: `claude plugin validate --strict` passes and one local team-lead run and one security eval pilot are recorded. A GitHub marketplace install was observed for the 1.0 plugins only. Codex, Gemini CLI, Copilot and Cursor are not yet tested, and no claude.ai upload is recorded. In the eval pilot the security plugin was picked up on 3 of 7 plain prompts, so name the lead (for example `/security:security-lead`) when you want the team. No improved performance or outcome is established; subject-expert review is pending. See [Validation status](docs/VALIDATION.md).
- The project has no accounts, connectors, telemetry, or model service. Your chosen host may process information in the cloud and has its own usage limits and data policies. Never supply credentials or private customer data to this pack.

## License

Instructional content, documentation, and examples are licensed under **CC BY 4.0**. Maintenance code and automation are licensed under **Apache-2.0**. See [NOTICE](NOTICE.md) and [license coverage](LICENSE.md) for attribution and exact file coverage.
