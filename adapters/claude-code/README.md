# Claude Code

`python3 -B scripts/pack.py build` generates the Claude Code marketplace and plugins; only this README is written by hand.

- `.claude-plugin/marketplace.json` at the root lists 17 family plugins plus the `ai-specialists-all` bundle.
- Each `plugins/<family>/` holds:
  - `.claude-plugin/plugin.json`;
  - its role skills under `skills/<family>-<slug>/`, marked `disable-model-invocation: true` so they do not fill the skill listing;
  - the lead skill `skills/<family>-lead/`, with the cards in `references/`;
  - one worker agent per card in `agents/`, with read-only tools, `disallowedTools: Agent`, and a per-role `model` and `effort`;
  - a copy of `orchestration-cross-family-reviewer`.
- The orchestration plugin also has `/specialists`, the cross-family lead.
- The bundle uses the repository root as its source. It lists the 17 leads, `specialists` and every worker agent, with no copies.

Tested host: Claude Code 2.1.302: `claude plugin validate --strict` and a local `--plugin-dir` smoke test (details in [docs/VALIDATION.md](../../docs/VALIDATION.md)); marketplace install from GitHub not yet tested.

## Install

```
/plugin marketplace add cyberwiz-io/ai-specialists
/plugin install security@ai-specialists
```

Or install everything with `/plugin install ai-specialists-all@ai-specialists`. To try one family locally, run `claude --plugin-dir plugins/security`. Run a lead with `/security:security-lead <task>`.

## Limits

- The agent models are aliases (`haiku`, `sonnet`, `opus`). Your plan needs access to them.
- The leads grant tools through `allowed-tools`.
- A lead's parallel subagents each cost tokens.
- The nesting depth (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, default 3) does not matter for leads, because workers cannot start subagents.
- The instructions are not a sandbox. To stop a lead from reaching for a general agent, add this to your settings: `"permissions": {"deny": ["Agent(general-purpose)"]}`.

References: https://code.claude.com/docs/en/plugins-reference.md , https://code.claude.com/docs/en/plugin-marketplaces.md , https://code.claude.com/docs/en/sub-agents.md and https://code.claude.com/docs/en/skills.md .
