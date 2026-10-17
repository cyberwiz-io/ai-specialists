# Codex

`python3 -B scripts/pack.py build` generates everything here from the cards; only this README is written by hand.

- `.codex-plugin/plugin.json` and `skills/`: the `ai-specialists` Codex plugin. It holds the 17 family team leads (each with its cards in `references/`) and the cross-family `specialists` lead.
- `agents/*.toml`: 142 Codex custom agents, one per role, one per team lead and `specialists`.
- `.agents/plugins/marketplace.json` at the repository root: the marketplace that points Codex at this plugin.

Tested host: not yet tested. No Codex host is available where this was built, so neither the plugin nor the agents have run in Codex.

## Install

Add the marketplace, then enable the `ai-specialists` plugin in Codex:

```
codex plugin marketplace add cyberwiz-io/ai-specialists
```

Copy the agent files from a clone of this repository, into a project or into your home folder:

```
mkdir -p .codex/agents && cp adapters/codex/agents/*.toml .codex/agents/
mkdir -p ~/.codex/agents && cp adapters/codex/agents/*.toml ~/.codex/agents/
```

For single-role skills, run `npx skills add cyberwiz-io/ai-specialists`, or copy `skills/<name>/` from the repository root into `.agents/skills/`.

## Limits

- The plugin carries only the 18 leads. Codex budgets its skill list at about 2% of context (8,000 characters when it does not know the size), and all 142 descriptions would not fit.
- Codex plugins do not carry custom agents, so the agent files must be copied by hand.
- The Codex docs do not say whether a custom agent can start other agents. If it cannot, a lead says so and stops, and the root `skills/` lead can run the roles in turn as perspectives instead.
- No model is set, so Codex uses its default. Reasoning effort comes from the manifest; leads use `medium`.
- Read-only roles set `shell_tool = false`. The four code roles keep the shell tool, and only their instructions limit them to git and test commands. Codex sandbox settings are not set per agent.

Formats checked 2026-10-17: https://developers.openai.com/codex/plugins/build , https://learn.chatgpt.com/docs/build-skills and https://learn.chatgpt.com/codex/agent-configuration/subagents .
