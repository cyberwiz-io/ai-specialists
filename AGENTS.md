# Contributor guidance

Start with REPO-MAP.md: it routes each task to the few files that matter, so do not scan the whole repository. Read CONTRIBUTING.md and the affected cards or instruction files before changing anything. Keep the user-facing pack portable, readable, and materials-only. Host rules and explicit user restrictions remain authoritative.

Individual cards and instruction files are the source of truth. Generated files (family indexes, `catalog/REGISTRY.jsonl`, `pack/STARTER-PACK.md`, `dist/packs/`, `config/module-map.json`, `skills/`, `plugins/`, `adapters/` except each `README.md`, and the root host manifests `.claude-plugin/`, `.cursor-plugin/`, `.agents/plugins/marketplace.json` and `gemini-extension.json`) are never edited by hand. In the generated plugins, worker agents cannot start other agents; only the leads do. Release ZIPs are never committed; CI builds them for tagged releases. After any change run `python3 -B scripts/pack.py build`, then `python3 -B scripts/pack.py check` and `python3 -B -m unittest discover -s tests`. Find a specialist with `python3 -B scripts/pack.py find <words>`.

Use fictional examples and preserve license coverage. Never commit credentials, private profiles, customer data, generated campaign records, or machine-specific settings. No specialist may enable external actions or promise unavailable capabilities. Sensitive families (security, finance, people and HR, legal and compliance) keep their Safeguards paragraph.

Documentation changes need proportionate checks. Maintenance code changes must exercise success and failure behavior. A new role needs a distinct deliverable, acceptance checks, a manifest entry and an eval fixture in `evals/fixtures/`, per docs/CARD-GUIDE.md. Run the card evaluations (evals/README.md) only when asked, and commit only reviewed reports. A host integration (the Claude Code plugins in `plugins/`) may ship so that users need not paste a pack, but its docs must state only what has been observed: state exactly what was observed (currently local smoke tests, `claude plugin validate` and a marketplace install from GitHub on Claude Code; not the claude.ai upload) until an eval or trial is recorded, and never claim compatibility with a host that was not tried.

## Branch naming

Name every branch you create after the work it contains, in lowercase kebab-case with a type prefix, such as `fix/login-redirect-loop`, `feat/export-csv` or `docs/branch-naming-rule`. Never use random, opaque or tool-generated names such as `ccr-58c0cebc-iezwgg`, `claude/abc123`, `agent-42` or `temp`. If a session or tool assigns a name like that, rename the branch before pushing when that is allowed; if the user or host requires the assigned name, use it and say so. Give pull requests a title that describes the change, and delete a temporary branch once it is merged.

## Working autonomously

When the user asks for a task to be finished, choose the most complete reasonable answer, state the default you picked, and carry the work through to done, including the follow-up steps it implies (build, checks, PR, merge, cleanup). Ask only about a blocker that needs the user, such as missing access, an irreversible or outward-facing action nobody has authorized, or a choice that changes their goal. Report what is unverified instead of claiming it passed.

Never push a release tag, publish to a package registry, or submit to a marketplace or directory yourself unless the owner has asked for that step; do the work up to it and list the remaining steps. Every action in `.github/workflows/` must be GitHub-owned or Marketplace-verified and pinned to a full commit SHA, or the organization's policy ends the run in `startup_failure`.

Before claiming an install path works, run it: add the marketplace from GitHub with a clean `CLAUDE_CONFIG_DIR`, install a plugin, and exercise the skill with `claude -p`. Record only what you saw in `docs/INSTALL.md` and `docs/VALIDATION.md`.
