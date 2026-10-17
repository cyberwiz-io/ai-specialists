# Repository map

Start here. Find the smallest set of files for your task and read only those. The shipped product is materials-only instructions; nothing here runs against a user's systems.

## Route by task

| I want to... | Read |
| --- | --- |
| Find a specialist for a job | `python3 -B scripts/pack.py find <words>`, or the table for its family below |
| Read or edit one specialist | `catalog/<family>/<slug>.md` (one card, about 2 KB) |
| Add a specialist | [Card guide](docs/CARD-GUIDE.md), then `catalog/families.json` |
| Change shared behavior or boundaries | [Marketing coordinator](pack/COORDINATOR.md) or [family coordinator](pack/FAMILY-COORDINATOR.md) |
| Change the marketing campaign flow | [Marketing workflow](pack/MARKETING-WORKFLOW.md) |
| Change user setup text | [Start here](pack/START-HERE.md) |
| Change build, checks or tests | [Contributing](CONTRIBUTING.md), then `scripts/packlib/` and `tests/` |
| Understand ownership of files | `config/module-map.json` (modules, guides, interfaces, digests) |
| Check scope, limits and status | [Roadmap](docs/ROADMAP.md), [Validation](docs/VALIDATION.md) |

## Families

Each family folder has a generated `INDEX.md` listing its specialists with one-line summaries. Read the index first, then one card.

| Family | Index |
| --- | --- |
| Security (sensitive) | [catalog/security/INDEX.md](catalog/security/INDEX.md) |
| IT operations | [catalog/it-operations/INDEX.md](catalog/it-operations/INDEX.md) |
| Software engineering | [catalog/software-engineering/INDEX.md](catalog/software-engineering/INDEX.md) |
| AI and machine learning | [catalog/ai-ml/INDEX.md](catalog/ai-ml/INDEX.md) |
| Product and design | [catalog/product-design/INDEX.md](catalog/product-design/INDEX.md) |
| Content and creative | [catalog/content-creative/INDEX.md](catalog/content-creative/INDEX.md) |
| Marketing and growth | [catalog/marketing-growth/INDEX.md](catalog/marketing-growth/INDEX.md) |
| Sales and customer | [catalog/sales-customer/INDEX.md](catalog/sales-customer/INDEX.md) |
| Business operations | [catalog/business-operations/INDEX.md](catalog/business-operations/INDEX.md) |
| Finance (sensitive) | [catalog/finance/INDEX.md](catalog/finance/INDEX.md) |
| Data and research | [catalog/data-research/INDEX.md](catalog/data-research/INDEX.md) |
| People and HR (sensitive) | [catalog/people-hr/INDEX.md](catalog/people-hr/INDEX.md) |
| Legal and compliance (sensitive) | [catalog/legal-compliance/INDEX.md](catalog/legal-compliance/INDEX.md) |
| Education and training | [catalog/education-training/INDEX.md](catalog/education-training/INDEX.md) |
| Public sector and nonprofit | [catalog/public-nonprofit/INDEX.md](catalog/public-nonprofit/INDEX.md) |
| Personal and career | [catalog/personal-career/INDEX.md](catalog/personal-career/INDEX.md) |
| Orchestration and meta | [catalog/orchestration/INDEX.md](catalog/orchestration/INDEX.md) |

## Layout

| Path | Contents | Edit by hand? |
| --- | --- | --- |
| `catalog/<family>/<slug>.md` | One role card each | Yes |
| `catalog/families.json` | Roster: families, roles, slugs, sensitivity | Yes |
| `catalog/<family>/INDEX.md` | Family index | No, generated |
| `catalog/REGISTRY.jsonl` | One line per specialist; grep it | No, generated |
| `pack/*.md` | Coordinators, workflow, templates, start guide | Yes, except `STARTER-PACK.md` |
| `pack/STARTER-PACK.md` | Marketing starter, pasted as one file | No, generated |
| `dist/packs/<family>.md` | Pasteable combined pack per family | No, generated |
| `downloads/*.zip` | Release archive | No, generated |
| `config/modules.json` | Module definitions | Yes |
| `config/module-map.json` | Module map with digests | No, generated |
| `docs/` | Guides, roadmap, validation status | Yes |
| `scripts/`, `tests/` | Build, check, search; their tests | Yes |
| `LICENSES/`, `NOTICE.md`, `LICENSE.md` | License text and coverage | Rarely |

Skip `dist/`, `downloads/` and `LICENSES/` when exploring: they are generated copies or license text.

## Rules that apply everywhere

- Materials only. No role enables an external action or promises a capability the host does not provide.
- Fictional examples only. No credentials, private profiles, customer data or generated campaign records.
- After any change run `python3 -B scripts/pack.py build`, then `python3 -B scripts/pack.py check` and `python3 -B -m unittest discover -s tests`.
