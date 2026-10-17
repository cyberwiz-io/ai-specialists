# Contributor guidance

Start with REPO-MAP.md: it routes each task to the few files that matter, so do not scan the whole repository. Read CONTRIBUTING.md and the affected cards or instruction files before changing anything. Keep the user-facing pack portable, readable, and materials-only. Host rules and explicit user restrictions remain authoritative.

Individual cards and instruction files are the source of truth. Generated files (family indexes, `catalog/REGISTRY.jsonl`, `pack/STARTER-PACK.md`, `dist/packs/`, `.claude-plugin/marketplace.json`, `plugins/`, `config/module-map.json`) are never edited by hand. Release ZIPs are never committed; CI builds them for tagged releases. After any change run `python3 -B scripts/pack.py build`, then `python3 -B scripts/pack.py check` and `python3 -B -m unittest discover -s tests`. Find a specialist with `python3 -B scripts/pack.py find <words>`.

Use fictional examples and preserve license coverage. Never commit credentials, private profiles, customer data, generated campaign records, or machine-specific settings. No specialist may enable external actions or promise unavailable capabilities. Sensitive families (security, finance, people and HR, legal and compliance) keep their Safeguards paragraph.

Documentation changes need proportionate checks. Maintenance code changes must exercise success and failure behavior. A new role needs a distinct deliverable, acceptance checks, a manifest entry and an eval fixture in `evals/fixtures/`, per docs/CARD-GUIDE.md. Run the card evaluations (evals/README.md) only when asked, and commit only reviewed reports. A host integration (the Claude Code plugins in `plugins/`) may ship so that users need not paste a pack, but its docs must state only what has been observed: state exactly what was observed (currently local smoke tests, `claude plugin validate` and a marketplace install from GitHub on Claude Code; not the claude.ai upload) until an eval or trial is recorded, and never claim compatibility with a host that was not tried.

## Branch naming

Name every branch you create after the work it contains, in lowercase kebab-case with a type prefix, such as `fix/login-redirect-loop`, `feat/export-csv` or `docs/branch-naming-rule`. Never use random, opaque or tool-generated names such as `ccr-58c0cebc-iezwgg`, `claude/abc123`, `agent-42` or `temp`. If a session or tool assigns a name like that, rename the branch before pushing when that is allowed; if the user or host requires the assigned name, use it and say so. Give pull requests a title that describes the change.

## Working autonomy and release limits

The owner has asked agents to take each task to completion with the best available answer rather than stopping for approval. Decide, act, verify and report. Stop and ask only for a genuine blocker that needs the owner, such as a credential, an account setting or an irreversible external step. Open a pull request for your work and drive it to green CI; do not push to `main` directly.

Never push a release tag, publish to a package registry, or submit to a marketplace or directory yourself. Do the work up to that point and list the remaining steps for the owner. Every action in `.github/workflows/` must be GitHub-owned or Marketplace-verified and pinned to a full commit SHA, or the organization's policy ends the run in `startup_failure`.

Before claiming an install path works, run it: add the marketplace from GitHub with a clean `CLAUDE_CONFIG_DIR`, install a plugin, and exercise the skill with `claude -p`. Record only what you saw in `docs/INSTALL.md` and `docs/VALIDATION.md`.
