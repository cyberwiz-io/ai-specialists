# Roadmap

The current foundation is a portable marketing instruction pack, version 0.1. All items below are planned work, not promises of implemented capabilities or release dates.

## Validate the current pack

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

Add an adapter only when a selected host needs one. Document the exact tested host/version, setup path, capabilities, limitations, and evidence. Native delegation, reliable persistence, and independent review require their own checks.

Status: an experimental [Claude Code adapter](../adapters/claude-code/README.md) generates read-only subagents from the cards. It is untested in a live host and is not part of the pack or the release archive. The [fixture evals](../evals/README.md) are keyword smoke tests, not the evidence this section asks for.

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
