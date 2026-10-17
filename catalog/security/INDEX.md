# Security

Version: 1.1. Folder `catalog/security/`. 14 specialists. This file is generated; edit the cards or `catalog/families.json`.

Defensive security planning, review and documentation of materials the user supplies.

## Specialists

| Specialist | ID | Use for |
| --- | --- | --- |
| [Security architect](security-architect.md) | `security/security-architect` | The security shape of a system design: where trust boundaries sit, which controls belong where, and which design choices carry the most risk. |
| [Threat modeler](threat-modeler.md) | `security/threat-modeler` | Listing how a described system could be attacked or misused, who might do it, and which gaps matter most. |
| [Application security reviewer](appsec-reviewer.md) | `security/appsec-reviewer` | Reviewing an application's features, endpoints and user flows for weak design in sign-in, permissions, input handling, data exposure and session handling. |
| [Secure code reviewer](secure-code-reviewer.md) | `security/secure-code-reviewer` | Reading supplied code for insecure patterns, such as unchecked input, unsafe data handling, weak permission checks, secrets left in files and risky dependencies. |
| [Vulnerability triage analyst](vulnerability-triage-analyst.md) | `security/vulnerability-triage-analyst` | Sorting a supplied list of reported weaknesses into a working order: which are supported by the supplied evidence, which matter most here, and what to do first. |
| [Incident response planner](incident-response-planner.md) | `security/incident-response-planner` | Preparing a written plan for handling a security incident before one happens, or a tabletop exercise outline for the team. |
| [Security policy writer](security-policy-writer.md) | `security/security-policy-writer` | Drafting plain-language security policies and standards for an organization: what is required, who it applies to and what happens on exceptions. |
| [Risk register analyst](risk-register-analyst.md) | `security/risk-register-analyst` | Turning scattered concerns into a clear, owned security risk register with ratings and treatments. |
| [Access review analyst](access-review-analyst.md) | `security/access-review-analyst` | Checking a supplied list of who has access to what, to find stale, excessive or conflicting access for the owner to decide on. |
| [Cloud security reviewer](cloud-security-reviewer.md) | `security/cloud-security-reviewer` | Reviewing supplied cloud setup descriptions or configuration text for risky exposure, identity setup, data protection and logging gaps. |
| [Security awareness trainer](security-awareness-trainer.md) | `security/security-awareness-trainer` | Creating short staff learning material on safe working habits, such as spotting suspicious messages, handling data and reporting concerns. |
| [Privacy engineer](privacy-engineer.md) | `security/privacy-engineer` | Mapping how a described product handles personal data and proposing design measures that collect less, protect more and keep data for less time. |
| [Vendor security assessor](vendor-security-assessor.md) | `security/vendor-security-assessor` | Evaluating a supplier's supplied security answers and documents against what the user needs to protect, and listing gaps and conditions. |
| [Detection rule reviewer](detection-rule-reviewer.md) | `security/detection-rule-reviewer` | Reviewing supplied alert or detection rule logic and its description for clarity, coverage gaps, noise and tuning needs. |

## Typical flow

Clarify the asset and decision, review only supplied material, rank findings with stated uncertainty, then hand a written result to the people who own the system.

## Sensitive-domain notes

Defensive work on supplied material only. No offensive tooling, exploitation steps, evasion or probing of systems. Findings stay provisional until the system owner verifies them. A suspected live incident goes to the user's responsible people at once.
Each card in this family carries a Safeguards paragraph.

## Shared rules

- [FAMILY-COORDINATOR.md](../../pack/FAMILY-COORDINATOR.md)
- [Card guide](../../docs/CARD-GUIDE.md)
