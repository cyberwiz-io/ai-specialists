# Changelog

## Unreleased

- Host install checks recorded: Antigravity CLI 1.4.2 installed the extension from a GitHub clone and loaded the security lead in one headless run. The Codex install was blocked by a local wrapper, Gemini CLI was not installed, and Copilot and Cursor are marked not tested because the maintainer cannot test them. See "Other host installs" in docs/VALIDATION.md.
- Checks and scans run on pull requests only. A new `security` workflow runs Gitleaks, Semgrep CE, Trivy and, for sensitive paths, an AI security review; CodeQL moves from default setup to a pull-request-only workflow. See "Security checks" in CONTRIBUTING.md.
- Card fixes from the first full-catalog eval: the graphic designer delivers captions, build sheets and provisional alt text when the host cannot make images; the task router names only enabled role IDs; the storyteller adds no unsupplied framing and meets the length from supplied moments; the cover letter writer uses a bracketed recipient and reaches the length without stock openings; the meeting facilitator's agenda checks apply only to agendas; the contract reader gives no example dates; the privacy policy drafter waits for confirmed practices before drafting.
- A text-only third review of the sensitive-family cards: about 70 wording fixes, no new rules.
- Team lead descriptions say which requests should start them, from a new `triggers` field per family in `catalog/families.json`; the lead description limit is 400 characters. Leads send review fixes back to the owning role and list choices a specialist left to the user as decisions.
- Security is split into three combined packs: engineering (5), operations (3) and governance and privacy (6).
- Plugin eval suites for finance, people-hr and legal-compliance, each with a team task that chains three specialists; team tasks may set `min_agents`.
- The first full-catalog eval run (141 fixtures on claude-opus-5-5) and its re-runs are recorded, and `evals/baseline.json` holds every card. `evals.py baseline` accepts several `--run` values, and `scripts/evals_headless.sh` carries out a prepared run with one fresh `claude -p` session per reply and per grade.
- The Codex plugin's `interface.shortDescription` fits the documented 30 characters, and the check enforces it.

## 1.1

One-command install across the major AI tools, smaller always-loaded text, and specialists that work as a team through subagents.

- Agent Skills: `skills/<family>-<slug>/SKILL.md` for all 124 cards, plus `skills/<family>-lead/` for each family and `skills/specialists/`. Frontmatter uses only the six fields in the Agent Skills specification; descriptions start from the card's Use for line and stay near 200 characters. Install with `npx skills add cyberwiz-io/ai-specialists`.
- Claude Code plugins: each family plugin now holds a team lead skill (`/<family>:<family>-lead`), one role skill per card (invoked by name only, `disable-model-invocation: true`), one worker agent per card and a copy of the cross-family reviewer. The marketplace adds an `ai-specialists-all` bundle with the 17 leads, `/specialists` and all 124 workers. The per-family orchestrator agents are replaced by the lead skills.
- Team leads read the roster, pick one to three roles by the task-router rules, write handoff packets in the handoff-packager format, run the specialists as parallel subagents, send the merged result to a fresh cross-family reviewer subagent, and return one deliverable that names what was reviewed. Without subagents they label the result "specialist perspectives, self-reviewed". The orchestration cards and coordinators now separate independent review from self-review, and the claim that subagents cannot start subagents is gone.
- Per-role model and effort: `haiku` and low effort for 24 writing and formatting roles, `sonnet` and medium by default, `opus` and high for architects, the threat modeler and reviewers. Workers get read-only tools and `disallowedTools: Agent`; the code reviewer, debugging analyst, test designer and secure code reviewer also get allowlisted `git` and test commands.
- Shorter worker preamble: about 350 characters instead of about 1,300 (sensitive families about 760 instead of about 2,400). `python3 -B scripts/pack.py stats` reports always-loaded and on-demand size per output, estimated as characters divided by 4.
- Other tools, generated from the same cards and not yet tested: a Codex plugin (`adapters/codex/` with `.codex-plugin/plugin.json`, skills and agent TOML, listed in `.agents/plugins/marketplace.json`), a Gemini CLI extension (`gemini-extension.json`), GitHub Copilot custom agents (`adapters/copilot/agents/*.agent.md`) and Cursor plugins (`.cursor-plugin/` manifests). Each adapter README states its tested status, install command and limits.
- START-HERE offers a one-role minimal paste: one `SKILL.md`, about a tenth of a family pack.
- Checks cover skill names and description limits, the allowed frontmatter fields, marketplace and plugin manifest basics, real paths for every plugin entry, no `core-` prefix, no Agent tool on any worker, the bundle's description budget, and freshness of every new generated file. CI also runs `claude plugin validate --strict` on the marketplace, every plugin, `skills/` and the Codex plugin.
- A `claude plugin eval` suite for the security plugin (`evals/plugin/security.json`, generated into `plugins/security/evals/`): five tasks, a boundary case and one `/security:security-lead` team task, each with a no-plugin baseline.
- README opens with a one-command install table per tool; the limits section moved lower.
- Skills declare `allowed-tools` (`Read Grep Glob`, plus `Agent` for leads), so a skill reading its own cards no longer prompts or fails in headless runs; the check requires it. A marketplace install from GitHub of the 1.0 layout was observed working (see `docs/INSTALL.md`); the claude.ai upload is still unobserved.

## 1.0

First published release. Install a family as a Claude Code plugin or a claude.ai skill, or download the release archive and open `pack/START-HERE.md`.

- Catalog of 124 specialists in 17 families, each a single card in `catalog/<family>/`, plus a family coordinator. The four original marketing roles had `core/` IDs; they now use `marketing-growth/` like every other role.
- Subagents choose a model per family or role (`model` in `catalog/families.json`): writing-focused families run on `sonnet`, analysis-heavy and sensitive ones and every orchestrator inherit the session model. The software-engineering code reviewer and debugging analyst can also run `git diff/log/show/status` and common test runners (`commands: true`); every other subagent stays read-only. The marketing roles that had a `core/` ID are now `marketing-growth/` (agents `marketing-growth-copywriter` and so on), and the manifest `prefix` option is gone.
- Modular layout for people and AI agents: `REPO-MAP.md` routing, generated family indexes, a one-line-per-specialist registry, a module map with digests, and a `find` command.
- Pasteable combined pack for each family (`dist/packs/`), the marketing starter pack, and one release archive.
- Card guide and a manifest-driven build. Checks now cover card shape, safeguards for sensitive families, restricted wording, named standards, handoff IDs, size limits, generated-file freshness, links, module coverage and the archive.
- Continuous integration runs the checks and tests.
- Sensitive families (security, finance, people and HR, legal and compliance) carry Safeguards paragraphs. No clinical or healthcare roles.
- Native install path, so users no longer paste an 8,000-token pack. The build generates a Claude Code marketplace (`.claude-plugin/marketplace.json`) and one plugin per family in `plugins/`: a `SKILL.md` whose coordinator rules load first and whose cards load on demand from `references/`, and a read-only subagent per card. Install with `/plugin marketplace add cyberwiz-io/ai-specialists` and `/plugin install <family>@ai-specialists`. See `docs/INSTALL.md`.
- The release includes `plugins/` and `.claude-plugin/` and attaches one upload-ready skill ZIP per family (`ai-specialists-<version>-skill-<family>.zip`) for claude.ai. `claude plugin validate` passes and a local smoke test loaded a plugin and read a card on demand; marketplace install from GitHub and the claude.ai upload are not yet observed, and the docs say so.
- Card evaluation harness: fictional fixtures for all 124 cards plus a boundary fixture per family in `evals/fixtures/`, `scripts/evals.py` (`prepare`, `status`, `report`), and a Claude Code skill and subagents that run each card in a fresh context and grade the reply against the card's own Acceptance line. Reports record version, commit, host, tools, models, inputs, outcomes and limits. The harness is built; one run (marketing-growth) is recorded as the first baseline, and other families have none yet.
- The release ZIP is no longer committed. Pushing a `v` tag runs the release workflow, which checks, builds and attaches the archive to the GitHub Release. Use `python3 -B scripts/pack.py release` to build it locally.
- Combined packs are capped at 32 KB, about 8,000 tokens, to fit 16,000-token context windows. The 38 KB Security pack is split into Security engineering (8 specialists) and Security governance and privacy (6). Role IDs are unchanged.
- Claude Code support for maintainers: `.claude/` with a SessionStart hook that runs the pack check, the commands `/new-specialist`, `/review-card`, `/verify` and `/build-plugins`, and a card-reviewer subagent.

Cards have passed automated structural checks and a paper review of the written instructions. Fresh-host compatibility, unaided usability, comparative quality, and automated publishing are not established. See [Validation](docs/VALIDATION.md).

## 0.1 foundation

- Portable coordinator, marketing workflow, and four specialist cards.
- Combined copy-and-paste pack, guided specialist customization, and optional business-profile template.
- Public roadmap and validation limits.
- Reproducible starter ZIP, maintenance checks, and contribution templates.
- Explicit experimental status and separate content/code licenses.
