# Changelog

## Unreleased

- Card evaluation harness: fictional fixtures for all 124 cards plus a boundary fixture per family in `evals/fixtures/`, `scripts/evals.py` (`prepare`, `status`, `report`), and a Claude Code skill and subagents that run each card in a fresh context and grade the reply against the card's own Acceptance line. Reports record version, commit, host, tools, models, inputs, outcomes and limits. The harness is built; no run is recorded yet.
- The release ZIP is no longer committed. Pushing a `v` tag runs the release workflow, which checks, builds and attaches the archive to the GitHub Release. Use `python3 -B scripts/pack.py release` to build it locally.
- Combined packs are capped at 32 KB, about 8,000 tokens, to fit 16,000-token context windows. The 38 KB Security pack is split into Security engineering (8 specialists) and Security governance and privacy (6). Role IDs are unchanged.

## 1.0

- Catalog of 124 specialists in 17 families, each a single card in `catalog/<family>/`, plus a family coordinator. The four original marketing roles keep their `core/` IDs.
- Modular layout for people and AI agents: `REPO-MAP.md` routing, generated family indexes, a one-line-per-specialist registry, a module map with digests, and a `find` command.
- Pasteable combined pack for each family (`dist/packs/`), the marketing starter pack, and one release archive.
- Card guide and a manifest-driven build. Checks now cover card shape, safeguards for sensitive families, restricted wording, named standards, handoff IDs, size limits, generated-file freshness, links, module coverage and the archive.
- Continuous integration runs the checks and tests.
- Sensitive families (security, finance, people and HR, legal and compliance) carry Safeguards paragraphs. No clinical or healthcare roles.

Cards have passed automated structural checks and a paper review of the written instructions. Fresh-host compatibility, unaided usability, comparative quality, and automated publishing are not established. See [Validation](docs/VALIDATION.md).

## 0.1 foundation

- Portable coordinator, marketing workflow, and four specialist cards.
- Combined copy-and-paste pack, guided specialist customization, and optional business-profile template.
- Public roadmap and validation limits.
- Reproducible starter ZIP, maintenance checks, and contribution templates.
- Explicit experimental status and separate content/code licenses.
