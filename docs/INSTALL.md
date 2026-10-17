# Install without pasting

You do not have to paste a pack into a chat. Each family is also an installable team lead skill, with the specialist cards loaded only when a task needs them. Each specialist is also its own skill. Pasting a [combined pack](../pack/START-HERE.md) still works in any host.

Nothing here adds a capability. A skill is advisory instructions, and the plugins are materials only: they do not publish, send, schedule, connect or run anything.

Pick your tool below. Claude Code is the only host where these files have been checked; every other path is generated to that host's published format but not yet tested.

## What gets installed

- **Role skills.** The root `skills/` folder has one skill per specialist, `skills/<family>-<slug>/`, 124 in all. They use only the open Agent Skills fields, so they can also be uploaded to claude.ai.
- **Team leads.** `skills/<family>-lead/` runs one family's team, with that family's cards in `references/`. `skills/specialists/` is the cross-family lead.
- **Worker agents.** In hosts with subagents, each card is also a worker agent. Workers do one role's job and cannot start other agents. Only the lead, running in the main conversation, starts them.

A lead reads the roster and picks one to three roles. It writes a handoff packet for each, starts them as parallel subagents, and sends the merged result to the cross-family reviewer in a fresh subagent. You get one deliverable that says what was reviewed. Without subagents, as in plain chat or claude.ai, the lead reads the cards from `references/` itself and labels the result "specialist perspectives, self-reviewed".

## Claude Code

Add the marketplace once, then install one family or all of them:

```
/plugin marketplace add cyberwiz-io/ai-specialists
/plugin install security@ai-specialists
/plugin install ai-specialists-all@ai-specialists
```

Claude Code 2.1.275 or later can do it in one step: `/plugin install ai-specialists-all --marketplace cyberwiz-io/ai-specialists`.

Then run a family lead with your task, for example `/security:security-lead Review the login flow of my shop app`. Each family plugin has its lead skill, its role skills, one worker agent per card and a copy of the cross-family reviewer. The role skills start only when you call them by name, so they do not crowd the skill list. The `ai-specialists-all` bundle lists the 17 leads, `specialists` and all 124 worker agents.

Skills declare `allowed-tools` (`Read Grep Glob`, plus `Agent` for the leads), and each lead carries its roster's Acceptance lines in its own body, so a team run does not need to open the cards. With `allowed-tools`, reading a skill's own cards inside the installed plugin does not prompt. In non-interactive `claude -p` runs, Claude Code still asks before it calls the skill itself, and that prompt cannot be answered, so allow it up front, for example `claude -p "..." --allowedTools "Skill"`.

Worker agents have read-only file tools (`Read`, `Grep`, `Glob`) and `disallowedTools: Agent`. A worker can read files you point to. It cannot run commands, edit files, browse, contact anyone or start other agents. Four code roles are the exception for commands: the code reviewer, debugging analyst, test designer and secure code reviewer also get `Bash` limited to `git diff`, `git log`, `git show`, `git status` and common test runners, so their findings can rest on real test output. Your host's permission prompts still apply.

Each worker also has a model and effort. Most use `sonnet`. Writing and formatting roles use `haiku`, never in the four sensitive families. Architects, the threat modeler and the reviewers, including the cross-family reviewer, use `opus`. Effort follows the role's tier: low, medium or high. Both are set per role in `catalog/families.json`.

To try a plugin from a downloaded checkout without the marketplace, run `claude --plugin-dir plugins/security`. Details: [Claude Code adapter](../adapters/claude-code/README.md).

## Claude.ai and Claude Desktop

Download the skill ZIP for a family from the [latest release](https://github.com/cyberwiz-io/ai-specialists/releases/latest). The files are named `ai-specialists-<version>-skill-<family>.zip`, and each holds the lead skill folder `<family>-lead/` with its cards. In Settings, open Capabilities, then Skills, and upload the ZIP. Then describe your task in a new chat. To add a single role, zip its folder `skills/<family>-<slug>/` and upload that.

Availability depends on your plan and on skills being enabled for your account or organization. claude.ai has no subagents here, so the lead labels its result "specialist perspectives, self-reviewed".

## Other Agent Skills hosts

Hosts that read the open Agent Skills layout can add the root `skills/` folder:

```
npx skills add cyberwiz-io/ai-specialists
```

Or copy one `skills/<name>/` folder into your host's skills folder. Not yet tested.

## Codex

```
codex plugin marketplace add cyberwiz-io/ai-specialists
```

Then enable the `ai-specialists` plugin. It carries the 17 leads and `specialists`. For worker agents, copy the TOML files from a clone into your project: `cp adapters/codex/agents/*.toml .codex/agents/`. Not yet tested. Details: [Codex adapter](../adapters/codex/README.md).

## Gemini CLI

```
gemini extensions install https://github.com/cyberwiz-io/ai-specialists
```

The repository root is the extension (`gemini-extension.json`), and it loads the root `skills/`. Not yet tested. Details: [Gemini CLI adapter](../adapters/gemini/README.md).

## GitHub Copilot

From a clone, copy the agents into your repository: `cp adapters/copilot/agents/*.agent.md .github/agents/`. Not yet tested. Details: [Copilot adapter](../adapters/copilot/README.md).

## Cursor

In Cursor, open Customize, choose From GitHub Repository and enter `cyberwiz-io/ai-specialists`. The root `.cursor-plugin/marketplace.json` lists the family plugins in `plugins/<family>/`. Not yet tested. Details: [Cursor adapter](../adapters/cursor/README.md).

## Plain chat

Paste `dist/packs/<family>.md` into a new conversation; see [Start here](../pack/START-HERE.md). If you need only one role, paste a single `skills/<family>-<slug>/SKILL.md` instead. That is about 700 to 900 tokens.

## Family names

| Family | Plugin and skill name |
| --- | --- |
| Marketing and growth | `marketing-growth` |
| Content and creative | `content-creative` |
| Sales and customer | `sales-customer` |
| Business operations | `business-operations` |
| Product and design | `product-design` |
| Software engineering | `software-engineering` |
| AI and machine learning | `ai-ml` |
| IT operations | `it-operations` |
| Data and research | `data-research` |
| Education and training | `education-training` |
| Public sector and nonprofit | `public-nonprofit` |
| Personal and career | `personal-career` |
| Orchestration and meta | `orchestration` |
| Security (sensitive) | `security` |
| Finance (sensitive) | `finance` |
| People and HR (sensitive) | `people-hr` |
| Legal and compliance (sensitive) | `legal-compliance` |

The lead skill for a family is `<family>-lead`, for example `security-lead`. Security, finance, people and HR, and legal and compliance give support material, not professional advice. Their cards keep the Safeguards paragraph, and the workers embed the family's sensitive-domain rules. Take consequential decisions to a qualified person.

## What is and is not established

All the files above are generated from the cards by the build and checked for structure: names, description limits, links and freshness. `python3 -B scripts/pack.py stats` estimates the tokens each output and plugin adds.

On 2026-10-17, with the 1.0 layout on Claude Code 2.1.302 and a clean config folder, `claude plugin marketplace add cyberwiz-io/ai-specialists` and `claude plugin install marketing-growth@ai-specialists` (and `orchestration@ai-specialists`) succeeded from GitHub, and a headless `claude -p` run with only `--allowedTools "Skill"` read a card from the installed plugin with no denials once `allowed-tools` was added. The 1.1 layout (leads, role skills, bundle) has not yet been installed from GitHub; that needs this branch on the default branch.

Only Claude Code has been checked. On Claude Code 2.1.302, `claude plugin validate --strict` passes for the marketplace, all 17 plugins, `skills/` and `adapters/codex`. A local `--plugin-dir` lead run is recorded separately; see [Validation](VALIDATION.md).

Not yet tested: Codex, Gemini CLI, GitHub Copilot, Cursor and other Agent Skills hosts. No host for them was available. No 1.1 install from GitHub, no claude.ai upload, no `npx skills` run, no unaided-user trial and no card evaluation run is recorded. Release links work only after the maintainer tags v1.1. Skill triggering, how a lead picks roles and upload availability may differ from what is described here. Report what you see in a GitHub issue.

The files in `skills/`, `plugins/`, `adapters/` (except each README), `.claude-plugin/`, `.cursor-plugin/`, `.agents/plugins/` and `gemini-extension.json` are generated. To change a specialist, edit its card in `catalog/` and rebuild; see [Contributing](../CONTRIBUTING.md).
