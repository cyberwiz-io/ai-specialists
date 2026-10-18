# GitHub Copilot

`python3 -B scripts/pack.py build` generates `agents/*.agent.md` from the cards; only this README is written by hand. There are 142 custom agents: one per role, one per family team lead and the cross-family `specialists` lead.

Tested host: not tested. The maintainer cannot test Copilot, so these agents have not run in Copilot.

## Install

Copy the agents into a repository, from a clone of this one:

```
mkdir -p .github/agents && cp adapters/copilot/agents/*.agent.md .github/agents/
```

For Copilot CLI, copy them into `~/.copilot/agents/` instead.

For skills, use `copilot skill add`, or copy `skills/<name>/` from the repository root into `.github/skills/`.

Submitting agents to github/awesome-copilot is a later manual step for the maintainer.

## Limits

- No model is set, so Copilot uses its default.
- Role agents get only `read` and `search`. Copilot cannot limit shell commands to an allowlist, so the code roles are read-only here too. Leads and `specialists` also get `agent`.
- The Copilot cloud agent ignores some frontmatter fields.
- Leads do not link their cards, since the agent files sit outside any skill folder.
- Copilot CLI can also read the Claude Code plugins in `plugins/` (its legacy plugin format reads `.claude-plugin/plugin.json`). That is untested.

Format checked 2026-10-17: https://docs.github.com/en/copilot/reference/custom-agents-configuration .
