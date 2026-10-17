# Claude Code notes

@AGENTS.md

Route every task through [REPO-MAP.md](../REPO-MAP.md) and read only the files it names. Cards in `catalog/` are the source of truth; never hand-edit generated files (indexes, registry, packs, module map, `.claude-plugin/`, `plugins/`). A SessionStart hook runs `python3 -B scripts/pack.py check`; if it reports a failure, say so before other work.

Commands: `/new-specialist`, `/review-card`, `/verify`, `/build-plugins`. The Claude Code plugins in `plugins/` ship with the release, but their live-host status stays at "validated and smoke-tested locally" until [eval evidence](../evals/README.md) supports more. To run the card evals, use the `card-evals` skill.
