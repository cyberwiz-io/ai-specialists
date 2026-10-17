# Contributing

Help make the pack easier to use, more accurate, or more useful. Small, concrete changes are welcome.

## Report a problem or propose a specialist

Open a GitHub issue using the problem or role-suggestion template. Describe the outcome you wanted, what happened, and the smallest useful improvement. Use fictional or redacted examples. Never include tokens, private business profiles, customer information, or full private conversations.

A specialist proposal should explain its distinct deliverable, when to use it, required capabilities, acceptance checks, and a realistic example. A different writing style may fit an existing role rather than require a new one. Listing a role never establishes expertise or certification.

## Edit the files

Start with [REPO-MAP.md](REPO-MAP.md); it routes each kind of change to the few files involved. Role cards in `catalog/<family>/`, the roster in `catalog/families.json`, and the instructions in `pack/` are authoritative. Family indexes, `catalog/REGISTRY.jsonl`, `pack/STARTER-PACK.md`, `dist/packs/`, `config/module-map.json`, `skills/`, `plugins/`, `adapters/` (except each `README.md`) and the root host manifests (`.claude-plugin/`, `.cursor-plugin/`, `.agents/plugins/marketplace.json`, `gemini-extension.json`) are generated; never edit them by hand. Edit the sources, then rebuild. Preserve the materials-only boundary, explicit user decisions, evidence requirements, and honest host limitations.

For maintenance, use Python 3.9 or newer. No packages need to be installed. From the repository root:

```sh
python3 -B scripts/pack.py build
python3 -B scripts/pack.py check
python3 -B -m unittest discover -s tests
```

To find a specialist, run `python3 -B scripts/pack.py find <words>`. To add or change a role, follow the [card guide](docs/CARD-GUIDE.md). The build computes every generated file before writing any of them. The check covers the roster, card shape and wording rules, safeguards for sensitive families, handoff IDs, size limits, generated-file freshness, local links, module coverage, and that no archive is committed. Each combined pack must stay under 32 KB (about 8,000 tokens); a larger family lists `packs` in `catalog/families.json` to split into parts. Tests exercise failures as well as the successful build. Generated archives are reproducible from the same file bytes.

## Evaluate cards

Every card has a fictional task fixture in `evals/fixtures/<family>.json`, and every family has a boundary fixture; the check enforces both. When you add or change a role, add or update its fixture. To run the evaluations, ask Claude Code to run the card evals (the `card-evals` skill), or follow [evals/README.md](evals/README.md). A run spawns a fresh subagent per reply and per grade, writes everything under the ignored `work/evals/` folder, and produces a report. Commit a report to `evals/reports/` only after reviewing it, and keep its Limits section.

## Claude Code

`.claude/` also holds a SessionStart hook that runs the check, and the commands `/new-specialist`, `/review-card`, `/verify` and `/build-plugins`. The build also generates the Claude Code marketplace (`.claude-plugin/marketplace.json`) and one plugin per family in `plugins/`: a team lead skill with the cards as references, the role skills, and a worker agent per card. Workers are read-only and cannot start other agents; only the lead, in the main conversation, starts them. `commands`, `model` and the tier in `catalog/families.json` opt a role into an allowlisted test runner and set its model and effort. The build also writes the root `skills/` folder, the files in `adapters/` (except each `README.md`, which is written by hand) and the root manifests for other hosts (`.agents/plugins/marketplace.json`, `.cursor-plugin/marketplace.json`, `gemini-extension.json`). The release archive includes them, plus one upload-ready skill ZIP per family for claude.ai. Never edit them by hand; they change when a card, a coordinator or a module in `scripts/packlib/` changes. `python3 -B scripts/pack.py stats` estimates their token cost.

## Security checks

Checks and scans run on pull requests only, not on pushes to `main` or on a schedule, so a change is checked once, before it merges. Each pull request runs:

- `check`: the pack check, the unit tests and `claude plugin validate --strict`.
- `codeql`: CodeQL for Python and for the workflows.
- `security`: Gitleaks for secrets in the pull request's commits, on every pull request; Semgrep Community Edition for risky code in `scripts/`, `tests/` and the workflows, and Trivy for vulnerable dependencies and configuration mistakes, both skipped when only prose changed; and a targeted AI security review when the change touches the security, finance, people-hr or legal-compliance cards, the workflows, `.claude/`, `scripts/`, `config/` or release settings. The AI review needs the `ANTHROPIC_API_KEY` repository secret and is skipped without it.

These tools cover different things: CodeQL and Semgrep look at code patterns, Gitleaks at secrets, Trivy at dependencies and configuration, and the AI review at intent and at the wording of sensitive cards. None of them alone shows that the project is secure, and passing all of them does not either; they catch known kinds of mistakes cheaply. Pin every downloaded tool by version and checksum, as `security.yml` does.

## Release

The release ZIP is not kept in Git, because every committed version would stay in the history. To release:

1. Set `VERSION` and give the changelog a `## <version>` section holding the notes (move entries out of `## Unreleased`). That section becomes the GitHub Release text, and the workflow fails if it is missing.
2. Run `python3 -B scripts/pack.py build`, `check` and the tests, and `python3 -B scripts/pack.py release --tag v<version>` to inspect the archive.
3. Open a pull request, confirm the check workflow is green on it, and merge to `main`. Checks and CodeQL run on pull requests only, not on pushes to `main` or on a schedule.
4. Push a tag named `v` plus the version, such as `v1.1`.
5. Confirm the release workflow attached the archive and one skill ZIP per family to the GitHub Release.

The release workflow runs the check and tests, builds the archive with `python3 -B scripts/pack.py release --tag v1.1`, and attaches it to the GitHub Release for that tag. Every action in `.github/workflows/` must be pinned to a full commit SHA, which the organization requires; with a tag or branch reference the run fails at startup. Run the same command locally to inspect the archive; it is written to the ignored `work/release/` folder.

Public content is organized in `catalog/`, `pack/` and `docs/`. Maintenance code lives in `scripts/` (the `packlib` package, one module per concern) and its checks in `tests/`. `config/modules.json` defines the modules that `config/module-map.json` reports. Keep any contributed examples fictional. Add no runtime framework, host dependency, or installation step for users of the pack.

## Submit a change

Use a branch and a pull request. Explain the problem, the resulting behavior, the checks you ran, and any unchecked assumptions. Update the changelog for user-visible changes. Run the build, check and tests before submitting; continuous integration repeats the check and tests. Claims about compatibility, usability, or performance need actual evidence and must identify their limits.

By contributing, you agree to license your changes under the license applying to the affected files. Preserve attribution for reused material and disclose its origin and license.

## Engineering policy validation
Pack build/test tooling remains standard-library only. Before delivery, create a
separate venv with Python 3.9+ and install PyYAML==6.0.3. Use that environment to run
python .engineering/check.py and python -m unittest discover -s .engineering -p 'test_*.py'.
Do not commit the environment. GitHub's Engineering policy workflow performs both.
