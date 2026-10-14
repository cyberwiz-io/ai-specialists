# Contributor guidance

Read CONTRIBUTING.md and the affected instruction files before changing this project. Keep the user-facing pack portable, readable, and materials-only. Host rules and explicit user restrictions remain authoritative.

Individual instruction files are the source of truth. Rebuild the combined pack and ZIP with `python3 -B scripts/pack.py build`; check with `python3 -B scripts/pack.py check` and `python3 -B -m unittest discover -s tests`.

Use fictional examples and preserve license coverage. Never commit credentials, private profiles, customer data, generated campaign records, or machine-specific settings. No specialist may enable external actions or promise unavailable capabilities.

Documentation changes need proportionate checks. Maintenance code changes must exercise success and failure behavior. Keep new roles and host integrations outside the shipped pack until their distinct deliverables and actual capabilities are reviewed.
