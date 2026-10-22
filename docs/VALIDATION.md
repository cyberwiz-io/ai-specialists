# Validation status

This repository ships advisory instruction materials. Structural checks and card evaluations do not establish that a host discovers, routes, delegates to, or safely runs them. The current 1.1 candidate has no published release. Current host acceptance for Claude Code and Codex on macOS and Windows is pending in all four combinations.

## Current host acceptance

| Device and client | Inventory | Acceptance |
| --- | --- | --- |
| macOS, Claude Code | 2.1.308 | Pending |
| macOS, Codex | 0.163.0 | Pending |
| Windows 11 build 26300, Claude Code | 2.1.304 | Pending |
| Windows 11 build 26300, Codex | 0.163.0 | Pending |

These versions are inventory observations, not test results. Follow [the host acceptance procedure](HOST-ACCEPTANCE.md) for each row. Acceptance requires observed installation, discovery, lead invocation, worker identity and handoff, expected behavior, permission boundaries, actual model reporting, update, and owned-only removal. A missing device or unobservable criterion stays pending. Historical trials on other versions or devices do not establish current acceptance.

The generated adapters express intended host configuration. Claude Code workers are configured with exactly `Read`, `Grep`, and `Glob`; they have no `Bash` or automatic skill tool. Leads pass approved methods explicitly in task handoffs. Codex's no-spawn direction is advisory; do not describe it as host enforcement. Role routing is advisory and separate from a task-specific cheapest-suitable model override that a host may support. Claude worker frontmatter retains role-specific model and effort defaults; the host applies these unless an explicit task override takes precedence. Codex workers inherit the parent model. Lead routing instructions are advisory, not a dynamic routing engine.

## Automated and historical evidence

Repository checks validate card structure, safeguards, links, generated-file freshness, adapter formats, fixtures and archive contents. These checks do not prove host behavior. Follow [Contributing](../CONTRIBUTING.md) for the current commands and [the release procedure](RELEASE.md) for the reviewed candidate and publication gates.

The reports in [evals/reports](../evals/reports/README.md) are historical, single-run evidence on fictional inputs. The 2026-10-17 catalog run recorded 78 pass, 59 partial and 4 fail across 141 fixtures; later reruns and plugin evaluations cover only their stated roles and cases. They are not acceptance runs for the current candidate. Model-graded fixture results do not establish subject expertise, real-world outcomes, host compatibility, or comparative quality.

Historical host observations are retained in adapter guides and earlier records: Claude Code 2.1.302 had strict plugin validation and local smoke evidence, and a GitHub marketplace install of the prior 1.0 layout was observed. An Antigravity CLI 1.4.2 plan-mode run loaded a lead from a clone but did not complete the requested task. A Codex attempt was blocked before installation by a local wrapper; another local-checkout install ran no model. These observations are not current acceptance. No 1.1 GitHub installation, current four-device acceptance run, claude.ai upload, or published 1.1 download is recorded.

## Release evaluation readiness

Release evaluation has separate gates; passing card checks alone is insufficient:

- Calibration cases are not adjudicated. Before using them, an independent reviewer must establish reference verdicts; require at least 90% exact agreement with no missed critical violation, then adjudicate every disagreement.
- Run the full existing suite and frozen held-out challenges twice on the candidate. Each run must reach at least 90% outright pass overall, at least 80% per family, one successful task per shipped role, and zero critical prohibited behaviors. Partial remains partial.
- Boundary cases, sensitive-role tasks, changed-card failures, and release-critical operational cases require three consecutive successful independent runs. Report first-attempt results and three-run stability separately.
- Review at least one useful output per family, every critical violation, and every grading disagreement. An unavailable reviewer or device remains pending.

Host acceptance is a separate gate: it covers discovery, explicit invocation, routing, lead-to-worker handoff, approved skill use, model overrides, permissions, and installation/update/removal on both required devices. Use traces and before/after fixture state to establish tool use; response headings or cost are not evidence of tool use.

## Publication status

No release has been published for this candidate. The release workflow is explicitly dispatched after authorization and reviewed-candidate checks; it is not triggered by pushing a tag and has no schedule. The planned release and family skill ZIP download links become usable only after publication, checksum and content verification, and a repeat of the promised installation path. See [docs/RELEASE.md](RELEASE.md).
