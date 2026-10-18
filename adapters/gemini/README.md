# Gemini CLI

The repository root is a Gemini CLI extension. `gemini-extension.json` names it, and Gemini loads every skill in the root `skills/` folder: 124 role skills, 17 family leads and the cross-family `specialists` lead (142 in all). `python3 -B scripts/pack.py build` generates the manifest and the skills; only this README is written by hand.

Tested host: no Gemini CLI install or model run is recorded; Gemini CLI was not installed where this was checked. `gemini extensions validate .` passed on Gemini CLI 0.64.0 in an earlier cloud-container check that installed nothing from GitHub and ran no model. The same extension was installed in Antigravity CLI 1.4.2 and a lead was loaded there (see below).

## Antigravity CLI

On 2026-10-17, Antigravity CLI (`agy`) 1.4.2 on macOS installed this extension from a fresh `git clone` of the `release` branch on GitHub (`agy plugin install <folder>` takes only a local folder and converts a Gemini CLI extension). It reported `142 skills processed`, and `agy plugin list` showed `ai-specialists (enabled, 1.1.0)` with source `gemini-cli`. `agy plugin validate` on the clone fails with "no plugin.json found ... This looks like a Gemini CLI extension: `plugin install` converts it", which is expected for this layout.

A headless run (`agy -p "Use the security-lead skill to draft a one-page threat model for a fictional to-do web app. ..." --mode plan --model gemini-3.8-flash-low`) loaded `security-lead/SKILL.md` and read two cards from its `references/` (`threat-modeler.md` and `cross-family-reviewer.md`). It started no subagent, and it stopped at an implementation plan and asked for confirmation instead of returning the threat model, because plan mode is read-only. A full lead run in a mode that finishes the deliverable was not done. The plugin was uninstalled afterwards.

## Install

```
gemini extensions install https://github.com/cyberwiz-io/ai-specialists
```

The extension must stay at the repository root for this command to find it. No context file is set, so nothing loads into every conversation beyond the skill descriptions.

## Limits

- All 142 skill descriptions are offered to the model, about 27,000 characters (roughly 6,700 tokens). When context is tight, install single skills from `skills/` instead of the whole extension.
- Gemini subagents cannot start other subagents, and this extension ships no Gemini agents. The leads therefore run their roles in turn as perspectives and label the result self-reviewed.
- The Gemini CLI docs say Gemini CLI was replaced by Antigravity CLI for unpaid-tier and Google One users on 2026-06-18, so availability depends on your account.

Formats checked 2026-10-17: https://geminicli.com/docs/extensions/reference/ , https://geminicli.com/docs/extensions/releasing/ and https://geminicli.com/docs/cli/skills/ .
