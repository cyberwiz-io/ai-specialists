# Reviewed release procedure

Release readiness has three separate results: code checks, real client/device acceptance, and publication. A green workflow does not demonstrate host behavior. Record remaining device or behavioral blockers in the delivery handoff before claiming support.

## Independent review evidence

Use an already authorized subscription or local reviewer outside the implementing agent. Do not enable API billing to satisfy CI. Give the reviewer the exact candidate diff, generated permission declarations, archive contents and acceptance requirements. Resolve blockers and repeat affected review after edits.

An authorized delivery coordinator posts a PR comment beginning exactly `AI-SPECIALISTS-REVIEW: ` followed by a JSON object with these fields:

| Field | Required value |
| --- | --- |
| `head` | Full reviewed PR head commit SHA |
| `tree` | That commit's Git tree SHA |
| `reviewer` | Observed separate reviewer identity and model/provider; disclose any identity limitation |
| `report` | Sanitized independent report text, including scope, findings, dispositions and limitations |
| `report_sha256` | SHA-256 of the exact UTF-8 `report` string |
| `verdict` | `PASS` only after every blocking finding is resolved |
| `blocking_findings` | Empty array for acceptance |

The gate reads comments directly from GitHub, verifies the commenter's current repository write, maintain or admin permission, and verifies the exact commit/tree and report hash. The newest authorized attestation wins; a newer invalid or blocking attestation cannot fall back to an earlier pass. The coordinator may be the PR author: they attest to a **separate review**, and are not represented as a human reviewer. A generated self-review or fabricated report is not acceptable evidence.

This trust model relies on the authorized coordinator truthfully recording the external review. Hashes bind the recorded report; they do not establish model identity or reviewer independence. Editable repository workflows and an authorized maintainer can change these controls. Independently controlled checks and remote protections require separate owner configuration; this workflow does not create them.

Validate an attestation with `python3 -B scripts/release_gate.py review --repo cyberwiz-io/ai-specialists --pr NUMBER --sha FULL_PR_HEAD` using existing GitHub authentication. Missing access, missing evidence, mismatched content and unresolved findings fail closed. CI never starts a paid model call.

## Candidate and publication

1. Update VERSION and the matching changelog section, regenerate, and run the documented product, policy, security, host and behavioral acceptance. Record exact commands/results and limitations. Build artifacts with `python3 -B scripts/pack.py release --tag vVERSION --out work/release`, then run `python3 -B scripts/verify_release.py work/release`.
2. Obtain the separate review and coordinator attestation on the final PR head. Changes invalidate the binding. Merge only through the authorized reviewed delivery path. The merged commit must have exactly the reviewed tree; if integration changes its contents, review the new candidate through a new PR.
3. After explicit delivery authorization, create the matching tag on that merged main commit. Dispatch the `release` workflow at that exact commit/tag ref with its full SHA, tag and merged PR number. The dispatch ref's SHA must equal the supplied candidate SHA. Pushing a tag alone never publishes.
4. The workflow proves main ancestry, merged PR mapping, exact reviewed tree, tag/version agreement and absence of an existing release. It reruns native Linux/macOS/Windows product checks, pinned Claude validation, policy tests, secret/static/dependency scans and review evidence verification. Before publication, the gate requires successful GitHub Actions checks for that exact SHA: `acceptance`, `policy-compliance`, `security-acceptance`, `Analyze (python)` and `Analyze (actions)`. Missing CodeQL execution is a blocker, not a pass. Reusable-workflow job prefixes are accepted only for the named candidate jobs.
5. Only the final publication job receives contents-write permission. It rebuilds the exact candidate, verifies the artifacts, and creates a release with ZIPs, SHA256SUMS and RELEASE.json. It never uploads over existing assets or replaces notes. A failed partial publication requires owner inspection; rerunning refuses an existing release.
6. Download the published assets through their public release URLs into a clean location, verify checksums and extracted contents, and repeat the promised installation path. Only then record working downloads and published-release acceptance.

Do not use untrusted PR artifacts in privileged publication. All action/tool pins remain in source. Review remote required-check and tag protections independently; the repository's main protection does not itself prove that a tag originated from reviewed history. New remote settings, provider charges and changes to personal installations require their own authorization.

## Local verification of controls

`python3 -B -m unittest discover -s tests -p test_release_gate.py` exercises valid and invalid attestation bindings, trusted comment selection, latest-review revocation, exact-SHA checks, check identity, failed/skipped checks and merged-PR provenance. Full CI and actual release execution provide separate evidence; local unit tests do not certify GitHub enforcement.
