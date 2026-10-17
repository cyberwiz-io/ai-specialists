# Contributor guidance

Start with REPO-MAP.md: it routes each task to the few files that matter, so do not scan the whole repository. Read CONTRIBUTING.md and the affected cards or instruction files before changing anything. Keep the user-facing pack portable, readable, and materials-only. Host rules and explicit user restrictions remain authoritative.

Individual cards and instruction files are the source of truth. Generated files (family indexes, `catalog/REGISTRY.jsonl`, `pack/STARTER-PACK.md`, `dist/packs/`, `config/module-map.json`) are never edited by hand. Release ZIPs are never committed; CI builds them for tagged releases. After any change run `python3 -B scripts/pack.py build`, then `python3 -B scripts/pack.py check` and `python3 -B -m unittest discover -s tests`. Find a specialist with `python3 -B scripts/pack.py find <words>`.

Use fictional examples and preserve license coverage. Never commit credentials, private profiles, customer data, generated campaign records, or machine-specific settings. No specialist may enable external actions or promise unavailable capabilities. Sensitive families (security, finance, people and HR, legal and compliance) keep their Safeguards paragraph.

Documentation changes need proportionate checks. Maintenance code changes must exercise success and failure behavior. A new role needs a distinct deliverable, acceptance checks and a manifest entry, per docs/CARD-GUIDE.md. Keep new host integrations outside the shipped pack until their actual capabilities are reviewed.
