# Changelog

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
