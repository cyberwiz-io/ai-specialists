# Contributing

Help make the pack easier to use, more accurate, or more useful. Small, concrete changes are welcome.

## Report a problem or propose a specialist

Open a GitHub issue using the problem or role-suggestion template. Describe the outcome you wanted, what happened, and the smallest useful improvement. Use fictional or redacted examples. Never include tokens, private business profiles, customer information, or full private conversations.

A specialist proposal should explain its distinct deliverable, when to use it, required capabilities, acceptance checks, and a realistic example. A different writing style may fit an existing role rather than require a new one. Listing a role never establishes expertise or certification.

## Edit the files

Start with [REPO-MAP.md](REPO-MAP.md); it routes each kind of change to the few files involved. Role cards in `catalog/<family>/`, the roster in `catalog/families.json`, and the instructions in `pack/` are authoritative. Family indexes, `catalog/REGISTRY.jsonl`, `pack/STARTER-PACK.md`, `dist/packs/` and `config/module-map.json` are generated; never edit them by hand. Edit the sources, then rebuild. Preserve the materials-only boundary, explicit user decisions, evidence requirements, and honest host limitations.

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

`.claude/` also holds a SessionStart hook that runs the check, and the commands `/new-specialist`, `/review-card`, `/verify` and `/build-plugins`. The build also generates the Claude Code marketplace (`.claude-plugin/marketplace.json`) and one plugin per family in `plugins/`: a skill with the cards as references, a subagent per card (read-only plus `Agent` so specialists can delegate; `commands` and `model` in `catalog/families.json` opt a role into an allowlisted test runner or a cheaper model), and a `<family>-orchestrator` agent that runs the team. The release archive includes them, plus one upload-ready skill ZIP per family for claude.ai. Never edit them by hand; they change when a card, a coordinator or `scripts/packlib/plugin.py` changes.

## Release

The release ZIP is not kept in Git, because every committed version would stay in the history. To release, update `VERSION` and the changelog, merge, then push a tag named `v` plus the version, such as `v1.1`. The release workflow runs the check and tests, builds the archive with `python3 -B scripts/pack.py release --tag v1.1`, and attaches it to the GitHub Release for that tag. Run the same command locally to inspect the archive; it is written to the ignored `work/release/` folder.

Public content is organized in `catalog/`, `pack/` and `docs/`. Maintenance code lives in `scripts/` (the `packlib` package, one module per concern) and its checks in `tests/`. `config/modules.json` defines the modules that `config/module-map.json` reports. Keep any contributed examples fictional. Add no runtime framework, host dependency, or installation step for users of the pack.

## Submit a change

Use a branch and a pull request. Explain the problem, the resulting behavior, the checks you ran, and any unchecked assumptions. Update the changelog for user-visible changes. Run the build, check and tests before submitting; continuous integration repeats the check and tests. Claims about compatibility, usability, or performance need actual evidence and must identify their limits.

By contributing, you agree to license your changes under the license applying to the affected files. Preserve attribution for reused material and disclose its origin and license.
