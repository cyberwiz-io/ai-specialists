# Contributing

Help make the pack easier to use, more accurate, or more useful. Small, concrete changes are welcome.

## Report a problem or propose a specialist

Open a GitHub issue using the problem or role-suggestion template. Describe the outcome you wanted, what happened, and the smallest useful improvement. Use fictional or redacted examples. Never include tokens, private business profiles, customer information, or full private conversations.

A specialist proposal should explain its distinct deliverable, when to use it, required capabilities, acceptance checks, and a realistic example. A different writing style may fit an existing role rather than require a new one. Listing a role never establishes expertise or certification.

## Edit the files

Start with [REPO-MAP.md](REPO-MAP.md); it routes each kind of change to the few files involved. Role cards in `catalog/<family>/`, the roster in `catalog/families.json`, and the instructions in `pack/` are authoritative. Family indexes, `catalog/REGISTRY.jsonl`, `pack/STARTER-PACK.md`, `dist/packs/`, the ZIP in `downloads/` and `config/module-map.json` are generated; never edit them by hand. Edit the sources, then rebuild. Preserve the materials-only boundary, explicit user decisions, evidence requirements, and honest host limitations.

For maintenance, use Python 3.9 or newer. No packages need to be installed. From the repository root:

```sh
python3 -B scripts/pack.py build
python3 -B scripts/pack.py check
python3 -B -m unittest discover -s tests
```

To find a specialist, run `python3 -B scripts/pack.py find <words>`. To add or change a role, follow the [card guide](docs/CARD-GUIDE.md). The build computes every generated file before writing any of them. The check covers the roster, card shape and wording rules, safeguards for sensitive families, handoff IDs, size limits, generated-file freshness, local links, module coverage and the ZIP's contents. Tests exercise failures as well as the successful build. Generated archives are reproducible from the same file bytes.

Public content is organized in `catalog/`, `pack/` and `docs/`. Maintenance code lives in `scripts/` (the `packlib` package, one module per concern) and its checks in `tests/`. `config/modules.json` defines the modules that `config/module-map.json` reports. Keep any contributed examples fictional. Add no runtime framework, host dependency, or installation step for users of the pack.

## Submit a change

Use a branch and a pull request. Explain the problem, the resulting behavior, the checks you ran, and any unchecked assumptions. Update the changelog for user-visible changes. Run the build, check and tests before submitting; continuous integration repeats the check and tests. Claims about compatibility, usability, or performance need actual evidence and must identify their limits.

By contributing, you agree to license your changes under the license applying to the affected files. Preserve attribution for reused material and disclose its origin and license.
