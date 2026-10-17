# Engineering policy 1.0.0

Source: lewismatlock/ai-home, tools/engineering-policy. The local lock file pins
reviewed bytes; update through a reviewed PR. Do not fetch latest at task startup.

## Execution
- Preserve repository-specific and nested instructions, active ownership and unique work.
  Use isolated branches/checkouts. Explicit user scope and live stops govern actions.
- Load relevant context once. Use deterministic tools first. Keep one checkpoint and
  bounded retry budget; reuse checks only for matching commit, inputs, toolchain,
  environment and check configuration. Never equate reading with compliance.
- Do not resume paused queues, change provider authority, purchase services or increase
  spending. Separate code failures, security findings, billing, permission and capacity
  failures. Stop retrying unchanged infrastructure failures; continue independent work.
- Keep secrets out of output and artifacts. Use host authentication, never print tokens.
  Report unexecuted checks and unresolved findings as pending or failed.

## Verification
- Preserve acceptance and security gates. Scope checks by components AND transitive
  consumers; shared config, contracts, CI and unknown paths trigger conservative coverage.
- Cancel superseded PR validation with workflow/PR-specific concurrency. Do not cancel
  deployments, migrations, signing or publishing. Keep post-merge coverage where useful.
- Stable aggregate acceptance checks must run with always() and inspect every required
  dependency result. Missing, failed, cancelled or unexpectedly skipped work fails.
  Path-filtered workflows are not unconditional required checks.
- Build expensive artifacts once per compatible input/trust boundary. Never reuse
  untrusted PR artifacts in privileged releases. Pin tools/actions, bound timeouts,
  matrices and retention, and key caches by lockfiles/toolchain.
- Secret scanning covers every PR. Move to incremental PR scans only after a reviewed
  full-history baseline and credential remediation; keep scheduled full-history scans.
  Do not suppress live credentials to obtain a green build.
- Dependency vulnerability scans run on a schedule as well as relevant changes.
  Deep AI security review targets sensitive changes and releases, using only an already
  authorized provider/usage route. Missing credentials never mean review passed.
- Run .engineering/check.py before delivery. Its static result does not replace product
  tests, runtime CI, independent review or protection verification.

## Enforcement and updates
- Instructions are guidance, not a security boundary. A check executed from editable
  PR code can be replaced. A GitHub Actions source-app binding alone does not prevent
  workflow spoofing. Use separately controlled required workflows or a dedicated App
  where available; report residual maintainer/agent bypass explicitly.
- Protect policy, checker, locks and workflow changes through reviewable PRs and
  owner review where available, without requiring an unavailable second maintainer.
- New repositories stay pending until policy, workflow execution and protections have
  separate evidence. Daily reconciliation reports drift and prepares update PRs;
  it never silently certifies, activates protections or merges its own updates.
