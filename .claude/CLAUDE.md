# Claude Code notes

@AGENTS.md

Route every task through [REPO-MAP.md](../REPO-MAP.md) and read only the files it names. Cards in `catalog/` are the source of truth; never hand-edit generated files (indexes, registry, packs, module map, `adapters/claude-code/agents/`). A SessionStart hook runs `python3 -B scripts/pack.py check`; if it reports a failure, say so before other work.

Commands: `/new-specialist`, `/review-card`, `/verify`, `/build-adapter`. The Claude Code adapter in `adapters/claude-code/` is experimental and stays outside the shipped pack until [eval evidence](../evals/README.md) supports it. To run the card evals, use the `card-evals` skill.
