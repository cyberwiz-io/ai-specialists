# Roadmap

Version 1.2 builds on the 1.0 catalog of 124 specialists in 17 families: pasteable packs, Agent Skills, Claude Code plugins with team leads, claude.ai skill ZIPs and generated install files for Codex, Copilot, Gemini CLI and Cursor. It grew out of the 0.1 marketing instruction pack. All items below are planned work, not promises of implemented capabilities or release dates.

## Validate the current release

- Run a fictional campaign in a fresh conversation with an existing host. Record research, image, file-export, profile-storage, and review capabilities actually observed.
- Test one custom-specialist preview and enablement, and a profile export or verified save.
- Observe unaided nontechnical users completing setup and receiving materials. Record confusion and correct the instructions.
- Compare the workflow with a well-instructed generalist using comparable tools, inputs, and usage budgets before making quality, speed, or cost claims.

## Catalog status

Version 1.0 ships the full planned catalog: 124 specialists and a family coordinator in 17 families. See [Repository map](../REPO-MAP.md). Every card is written and structurally checked. None has been tested in a fresh host, reviewed by a subject expert, or compared with a well-instructed generalist. Treat them as working perspectives.

## Expand only where useful

New roles are added only when they produce distinct useful deliverables and acceptance checks, following the [card guide](CARD-GUIDE.md). Sensitive domains need their own source, uncertainty, authorization and escalation checks before a role can ship. No clinical or healthcare roles are included. The catalog claims no certification or verified standards crosswalk. Keep experimental additions outside the default pack until reviewed.

Candidate next steps, after validation: a bounded developer feature-change workflow that links the software engineering roles, and family workflows beyond marketing.

## Consider host-specific support

Add host support only when a selected host needs it. Document the exact tested host/version, setup path, capabilities, limitations, and evidence. Native delegation, reliable persistence, and independent review require their own checks.

Status: the build generates install files from the cards. Claude Code gets a marketplace, family leads and workers limited to `Read`, `Grep` and `Glob`. Leads supply approved methods in handoffs. Codex no-spawn directions depend on host controls. The root `skills/` folder and generated adapters provide other installation materials; local builds also produce upload-ready skill archives. No 1.2 release is published or verified. Historical Claude Code format validation, local smoke tests and a GitHub marketplace installation are recorded in [Validation](VALIDATION.md); they do not establish current support. Current Claude Code and Codex acceptance on macOS and Windows remains pending in all four combinations. The historical card evaluation baseline lacks the hashes needed for current regression comparisons. Complete the [release evaluation protocol](../evals/README.md), [native trials](HOST-ACCEPTANCE.md) and publication checks before updating these claims or submitting to a directory. The claude.ai upload, unaided user trials and current trials in other hosts remain unobserved.

## External actions remain future work

Publishing, scheduling, monitoring, paid advertising, and account connections are outside this pack. A future edition would require authenticated approval bound to exact artifacts and destinations, host-enforced permissions, spending limits, durable state, uncertain-action reconciliation, cancellation, and live provider verification. Prompt instructions alone cannot establish those guarantees.

## Catalog inventory

| Family | Specialists |
| --- | --- |
| Security | 14 |
| IT operations | 5 |
| Software engineering | 11 |
| AI and machine learning | 3 |
| Product and design | 7 |
| Content and creative | 8 |
| Marketing and growth | 10 |
| Sales and customer | 8 |
| Business operations | 8 |
| Finance | 8 |
| Data and research | 8 |
| People and HR | 5 |
| Legal and compliance | 8 |
| Education and training | 6 |
| Public sector and nonprofit | 5 |
| Personal and career | 5 |
| Orchestration and meta | 5 |

The Coordinator lives in `pack/` and is not counted above.
