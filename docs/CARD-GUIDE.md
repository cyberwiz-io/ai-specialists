# Specialist card guide

How to write or edit a role card in `catalog/<family>/<slug>.md`. The family roster lives in [`catalog/families.json`](../catalog/families.json); `python3 -B scripts/pack.py check` enforces the rules below.

## Shape

```markdown
# Role name

ID: family/slug. Version: 1.4.

**Use for:** the task this role does, then what it is not for.

**Inputs:** what it needs, and what to ask for when missing.

**Method:** the few instructions that change how the work is done.

**Deliver:** the concrete output, its format, and what is marked unresolved.

**Acceptance:** observable checks that the work is complete and supported.

**Safeguards:** (required in sensitive families, optional elsewhere) sources, uncertainty, authorization, escalation.

**Handoff:** what the next role needs. All Coordinator boundaries apply; <one role-specific limit>.
```

- Line 1 is `# Name` in sentence case, matching the manifest name. Line 3 is `ID: <prefix>/<slug>. Version: <VERSION>.` The prefix is the family id.
- Labels appear in the order shown. Each is a bold label followed by a colon, one paragraph each.
- Keep a card to about 1.4 to 2.4 KB (hard limit 3.5 KB). Write for a person who is not technical.

## Content rules

1. **Materials only.** Every role produces documents, plans, drafts, analyses or reviews of material the user supplies. A role never acts on external systems, contacts anyone, accesses accounts, installs or runs anything, or claims it did.
2. **Distinct deliverable.** The `Deliver` paragraph must differ from every sibling role. If two roles would produce the same artifact, they are one role.
3. **Honest capability.** Use only capabilities the host actually provides in the conversation. Say what was not checked. Never claim tests, scans or lookups were run unless the output is shown.
4. **Evidence and uncertainty.** Separate supplied facts, sourced facts and assumptions. Unsupported claims are marked, not smoothed over.
5. **No invented specifics.** No real people, companies, customers, prices or statistics. Fictional examples are allowed when short and clearly fictional.
6. **No certification or standards claims.** Do not name regulations or industry standards or frameworks. Refer to "the user's chosen framework" or "the rules the user supplies". Never imply a result is certified, compliant, guaranteed or approved.
7. **Handoffs use real IDs.** Refer to other roles in backticks by full ID, such as `software-engineering/code-reviewer`. Every such ID must exist in the manifest.
8. **Coordinator boundaries.** The `Handoff` paragraph includes the sentence "All Coordinator boundaries apply" plus one limit specific to the role.

## Wording the checker enforces

A paragraph that contains any of these words must also contain a negation cue (`not`, `never`, `no`, `without`, `cannot`, `don't`, `outside`, `unless`), so the role can only mention them to rule them out: publish, deploy, credential, password, token, api key, connect, install, upload, log in, execute, exploit, payload, malware, evade or evasion, certified or certification, guarantee, compliant.

Use plain alternatives: "timeline" instead of "schedule", "carry out" instead of "execute", "length limit" instead of "token limit". The words "publish", "schedule" and "deploy" are reserved for stating that the role does not do them.

## Sensitive families

Security, Finance, People and HR, and Legal and compliance cards add a `Safeguards` paragraph that names all four of: where information comes from (**source**), what is **uncertain**, who must give **authorization** to act, and when to **escalate** to a qualified person. It also says plainly that the output is not professional advice. Security cards are defensive and cover supplied material only: no exploit steps, evasion, scanning or offensive tooling.

## Adding a role

Add it to the manifest (and to one of the family's `packs`, if it lists any), write the card, add a fictional task fixture for it to `evals/fixtures/<family>.json` (maintainers only; see `evals/README.md` in the repository), then run `python3 -B scripts/pack.py build` and `check`. New roles need a distinct deliverable and acceptance checks, per [Contributing](../CONTRIBUTING.md).
