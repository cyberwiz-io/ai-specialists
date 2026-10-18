# Cursor

Cursor reuses the Claude Code family plugin folders in `plugins/`. Each folder gets a `.cursor-plugin/plugin.json`, and the repository root gets `.cursor-plugin/marketplace.json` listing the 17 family plugins. Cursor finds `skills/<name>/SKILL.md` and `agents/*.md` in each plugin by default. `python3 -B scripts/pack.py build` generates these files; only this README is written by hand.

Tested host: not tested. The maintainer cannot test Cursor, so these files have not been loaded in Cursor.

## Install

- In Cursor, open Customize, choose From GitHub Repository and enter `cyberwiz-io/ai-specialists`. The repository carries `.cursor-plugin/marketplace.json`, so Cursor can list the family plugins.
- Or copy a family folder such as `plugins/security` into `~/.cursor/plugins/local` to try it locally.

## Limits

- The agent files use Claude Code frontmatter (`tools`, `disallowedTools`, model aliases such as `sonnet`). Cursor documents only `name` and `description` for plugin agents, so it may ignore the rest, including the read-only tool limits.
- Nesting in Cursor stops at grandchildren.
- These plugins are not in the Cursor marketplace. Submitting them is a later manual step.

Formats checked 2026-10-17: https://cursor.com/docs/plugins , https://cursor.com/docs/reference/plugins and https://github.com/cursor/plugin-template .
