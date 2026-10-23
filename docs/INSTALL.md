# Install without pasting

You do not have to paste a pack into a chat. Each family is also an installable team lead skill, with the specialist cards loaded only when a task needs them. Each specialist is also its own skill. Pasting a [combined pack](../pack/START-HERE.md) still works in any host.

Nothing here adds a capability. A skill is advisory instructions, and the plugins are materials only: they do not publish, send, schedule, connect or run anything.

The commands below describe candidate install paths. Current host acceptance for Claude Code and Codex on macOS and Windows is pending, and no 1.2 release has been published. The release download links are retained for the planned assets; working downloads require actual publication and post-publication verification. Older trials below are historical evidence only.

## What gets installed

- **Role skills.** The root `skills/` folder has one skill per specialist, `skills/<family>-<slug>/`, 124 in all. They use only the open Agent Skills fields, so they can also be uploaded to claude.ai.
- **Team leads.** `skills/<family>-lead/` runs one family's team, with that family's cards in `references/`. `skills/specialists/` is the cross-family lead.
- **Worker agents.** In hosts with subagents, each card is also a worker agent. In Claude Code, workers receive exactly `Read`, `Grep`, and `Glob`, with no `Bash` or automatic skill tool. Leads pass approved methods explicitly in task handoffs. Do not treat written limits as host enforcement without observing the host enforce them. Codex no-spawn directions are advisory.

A lead reads the roster, picks one to three roles and packages each handoff. It uses real subagents for suitable independent work where supported. For nontrivial results, the reviewer must use a different actual model from all authors and inspect the exact artifact/version. A fresh same-model subagent does not qualify. The lead must pass model IDs observed from the host; it cannot rely on a worker's self-report. Fixed plugin tiers may select the same model for authors and reviewer: use a supported per-call model override or another authorized reviewer route, or report BLOCKED_REVIEW. If cost is unavailable, report BLOCKED_MODEL/COST; do not claim ready or complete. Without supported subagents, the lead can apply cards inline as perspectives and state the limit. If different-model review cannot run, it reports BLOCKED_REVIEW and does not call the work ready. Role routing and supported model overrides remain advisory instructions, not a dynamic routing engine.

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

Workers receive exactly the read tools `Read`, `Grep`, and `Glob`; they have no `Bash` or automatic skill tool. Approved methods are passed explicitly by leads in task handoffs. These are configured instructions, not proof that the host enforces a boundary. Verify actual tools and permissions during host acceptance.

Partial candidate trials on macOS and Windows installed the business-operations plugin from the GitHub candidate branch and verified its cached commit. They traced real workers but exposed behavioral and review gaps; update and removal acceptance remains pending. See the exact source ref and limitations in [Validation](VALIDATION.md). These observations do not establish the default-branch commands above for the unpublished 1.2 candidate.

To try a plugin from a downloaded checkout without the marketplace, run `claude --plugin-dir plugins/security`. Details: [Claude Code adapter](../adapters/claude-code/README.md).

## Claude.ai and Claude Desktop

After publication and download verification, get a family skill ZIP from the [release downloads](https://github.com/cyberwiz-io/ai-specialists/releases/latest). Planned files are named `ai-specialists-<version>-skill-<family>.zip`, each holding the lead skill folder `<family>-lead/` with its cards. In Settings, open Capabilities, then Skills, and upload the ZIP. The 1.2 candidate's ZIP is not currently available. To add a single role from a checkout, zip its folder `skills/<family>-<slug>/` and upload that.

Availability depends on your plan and on skills being enabled for your account or organization. This claude.ai path has no subagents here; the lead states that role perspectives ran inline and marks nontrivial output BLOCKED_REVIEW unless an authorized different-model review actually ran.

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

Then enable the `ai-specialists` plugin. It carries the 17 leads and `specialists`. For worker agents, copy the TOML files from a clone into your project: `cp adapters/codex/agents/*.toml .codex/agents/`. Not tested: the local attempt was blocked before the install ran. Details: [Codex adapter](../adapters/codex/README.md).

## Gemini CLI

```
gemini extensions install https://github.com/cyberwiz-io/ai-specialists
```

The repository root is the extension (`gemini-extension.json`), and it loads the root `skills/`. Gemini CLI itself is not tested. The same extension installed in Antigravity CLI 1.4.2, where a plan-mode run loaded a lead (clone the repository, then `agy plugin install <folder>`). Details: [Gemini CLI adapter](../adapters/gemini/README.md).

## GitHub Copilot

From a clone, copy the agents into your repository: `cp adapters/copilot/agents/*.agent.md .github/agents/`. Not tested; the maintainer cannot test Copilot. Details: [Copilot adapter](../adapters/copilot/README.md).

## Cursor

In Cursor, open Customize, choose From GitHub Repository and enter `cyberwiz-io/ai-specialists`. The root `.cursor-plugin/marketplace.json` lists the family plugins in `plugins/<family>/`. Not tested; the maintainer cannot test Cursor. Details: [Cursor adapter](../adapters/cursor/README.md).

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

Current acceptance is pending for Claude Code and Codex on both required devices (macOS and Windows); see [host acceptance](HOST-ACCEPTANCE.md). Inventory versions are not test results. Historical 1.0 Claude Code marketplace installs, Claude Code 2.1.302 validation and local smoke tests, the Antigravity CLI plan-mode run, and earlier Codex attempts are described in [Validation](VALIDATION.md); none establishes current acceptance. No 1.2 release, release download, claude.ai upload, or unaided-user trial is recorded. Other hosts remain unaccepted. Report observed behavior with the exact host, version, device and source ref.

The files in `skills/`, `plugins/`, `adapters/` (except each README), `.claude-plugin/`, `.cursor-plugin/`, `.agents/plugins/` and `gemini-extension.json` are generated. To change a specialist, edit its card in `catalog/` and rebuild; see [Contributing](../CONTRIBUTING.md).
