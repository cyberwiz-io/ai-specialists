# Gemini CLI

The repository root is a Gemini CLI extension. `gemini-extension.json` names it, and Gemini loads every skill in the root `skills/` folder: 124 role skills, 17 family leads and the cross-family `specialists` lead (142 in all). `python3 -B scripts/pack.py build` generates the manifest and the skills; only this README is written by hand.

Tested host: not yet tested.

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
