# AI Specialists

A library of 124 specialist instruction cards in 17 families, plus a coordinator, for the AI assistant you already have. Describe a task, and the coordinator guides the right specialist perspectives through it. The best-developed path is a small-business marketing campaign.

**Version 1.0 · Materials only · [Validation status](docs/VALIDATION.md)**

These are editable instruction files. One assistant can work through the specialists in a single conversation. No app, installation, account connection, or developer tools are required. Nothing is posted, sent, scheduled, deployed or changed by this pack.

## Start

**Install, no pasting.** In Claude Code: `/plugin marketplace add cyberwiz-io/ai-specialists`, then `/plugin install marketing-growth@ai-specialists` (any family name works). On claude.ai, upload a family's skill ZIP from the [latest release](https://github.com/cyberwiz-io/ai-specialists/releases/latest). Each family is a skill whose specialist cards load only when needed, plus subagents (read-only, apart from two that can run tests) and a team orchestrator in Claude Code (subagents can delegate to each other). See the [install guide](docs/INSTALL.md), including its status: validated and smoke-tested locally in Claude Code, not yet observed through a GitHub install or a claude.ai upload.

**Or paste a pack, in any assistant.**

1. Pick a family below and open its combined pack under `dist/packs/` (select **Raw**), or open [the marketing starter pack](pack/STARTER-PACK.md). Copy it into a new conversation with an AI assistant you trust, or supply the file with that assistant's file feature.
2. Describe your task. For marketing: *Use this starter pack. My business is [short description]. My website is [optional]. Help me create a marketing campaign. First confirm that you can read all eight instruction sections.* For another family: *Use this pack. My task is [description]. Here is the material I can supply: [...]. First confirm that you can read all the sections.*
3. Confirm the plan, review the materials, and accept or revise.

Prefer a download? [Get the release ZIP](https://github.com/cyberwiz-io/ai-specialists/releases/latest) from the latest release, with every card, every combined pack, attribution and licenses, then open `pack/START-HERE.md`.

## Families

Each family has a pasteable combined pack and an index of its specialists. Every pack stays under 32 KB, about 8,000 tokens, so it fits in a 16,000-token context window with room to work; Security is split into two packs to stay under that limit.

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
| Security (sensitive) | 14 | [index](catalog/security/INDEX.md) | Two packs: [engineering](dist/packs/security-engineering.md) (8), [governance and privacy](dist/packs/security-governance.md) (6) |
| Finance (sensitive) | 8 | [index](catalog/finance/INDEX.md) | [pack](dist/packs/finance.md) |
| People and HR (sensitive) | 5 | [index](catalog/people-hr/INDEX.md) | [pack](dist/packs/people-hr.md) |
| Legal and compliance (sensitive) | 8 | [index](catalog/legal-compliance/INDEX.md) | Two packs: [documents](dist/packs/legal-compliance-documents.md) (4), [rules and policies](dist/packs/legal-compliance-rules.md) (4) |

The [marketing Coordinator](pack/COORDINATOR.md) and [marketing workflow](pack/MARKETING-WORKFLOW.md) keep campaign decisions and handoffs consistent; the [family coordinator](pack/FAMILY-COORDINATOR.md) does the same for every other family. You can [customize a specialist](pack/CUSTOM-SPECIALISTS.md) in plain language and preview it before enabling it. A [reviewed business profile](pack/BUSINESS-PROFILE.md) is optional.

## Know the limits

- These are advisory instructions, not an enforced permission system. Your assistant's rules and tools still govern its behavior.
- Security, finance, people and HR, and legal and compliance cards are defensive or educational support for material you supply. They are not professional advice and make no claim of compliance or certification. Consult a qualified person for consequential decisions.
- Research, image generation, file exports, memory, and separate review contexts depend on the host. Missing capabilities should produce a smaller agreed package, not pretend outputs.
- Switching roles in one chat is self-review, not independent multi-agent review.
- No host compatibility, improved performance, or outcome is established. The cards have passed structural checks and a paper review; fresh-host trials and subject-expert review are pending. See [Validation status](docs/VALIDATION.md).
- The project has no accounts, connectors, telemetry, or model service. Your chosen host may process information in the cloud and has its own usage limits and data policies. Never supply credentials or private customer data to this pack.

## Explore and contribute

Humans and AI agents should begin with the [repository map](REPO-MAP.md), which routes each task to the few files that matter. Read [Install](docs/INSTALL.md) and [Start here](pack/START-HERE.md) for setup details, the [card guide](docs/CARD-GUIDE.md) to write a role, the [roadmap](docs/ROADMAP.md) for future work, and [Contributing](CONTRIBUTING.md) to suggest or make changes.

## License

Instructional content, documentation, and examples are licensed under **CC BY 4.0**. Maintenance code and automation are licensed under **Apache-2.0**. See [NOTICE](NOTICE.md) and [license coverage](LICENSE.md) for attribution and exact file coverage.
