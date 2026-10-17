# Install without pasting

You do not have to paste a pack into a chat. Each family is also an installable skill, with the specialist cards loaded only when a task needs them, so a conversation starts small instead of with about 8,000 tokens of pasted text. Pasting a [combined pack](../pack/START-HERE.md) still works in any host.

Nothing here adds a capability. A skill is advisory instructions, and the plugins are materials only: they do not publish, send, schedule, connect or run anything.

## Claude Code

Add the marketplace once, then install the families you want:

```
/plugin marketplace add cyberwiz-io/ai-specialists
/plugin install marketing-growth@ai-specialists
```

Then describe your task, for example "Help me plan a small-business campaign", or invoke the skill by name with `/marketing-growth:marketing-growth`. Install only the families you need: each plugin adds one skill, one subagent per specialist in that family, and one team orchestrator (`<family>-orchestrator`).

Each skill declares `allowed-tools: Read Grep Glob`, so reading its own specialist cards inside the installed plugin does not prompt. In non-interactive `claude -p` runs, Claude Code still asks before it calls the skill itself, and that prompt cannot be answered, so allow it up front, for example `claude -p "..." --allowedTools "Skill"`.

The subagents have read-only file tools (`Read`, `Grep`, `Glob`) plus `Agent`. A specialist can read files you point to, and it cannot run commands, edit files, browse or contact anyone. Two roles are the exception: the software-engineering code reviewer and debugging analyst also get `Bash` limited to `git diff`, `git log`, `git show`, `git status` and common test runners (pytest, unittest, npm test, go test, cargo test), so their findings can rest on real test output. Your host's permission prompts still apply, and they cannot edit files or reach the network through any other tool. Subagents also pick a model: writing-focused families (marketing, content, sales, operations, product, education, public sector, career, IT operations) and the software-engineering technical and release-notes writers run on `sonnet`; analysis-heavy and sensitive families, the other software-engineering roles and every orchestrator use `inherit`, the model of your session. Both settings are per role in `catalog/families.json` (`commands`, `model`). Because it has `Agent`, a specialist can hand work to another specialist subagent when its card's Handoff line names one, and Claude Code lets subagents nest up to three layers below the main conversation by default (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` changes the limit, and some managed environments set it lower). At the limit, or when the named role's plugin is not installed, the specialist writes the handoff as a recommendation instead. Subagent types take the plugin prefix, for example `security:security-threat-modeler`.

The orchestrator runs a family's team. Start a session with it as the main thread, for example `claude --agent security:security-orchestrator`, or ask the main conversation to delegate to it. As the main thread its `Agent` tool is limited to that family's specialists. As a delegated subagent, Claude Code ignores that list, so the orchestrator's and every specialist's instructions say never to delegate to a general-purpose agent or any agent with command, edit or network tools. That is an instruction, not a sandbox: to enforce it, add `"permissions": {"deny": ["Agent(general-purpose)"]}` to your settings.

To try a plugin from a downloaded checkout or release folder without the marketplace, run `claude --plugin-dir plugins/marketing-growth`, or add the folder as a marketplace with `/plugin marketplace add ./path/to/folder`.

## Claude.ai and Claude Desktop

Download the skill ZIP for a family from the [latest release](https://github.com/cyberwiz-io/ai-specialists/releases/latest). The files are named `ai-specialists-<version>-skill-<family>.zip`. In Settings, open Capabilities, then Skills, and upload the ZIP. Availability depends on your plan and on skills being enabled for your account or organization. Then describe your task in a new chat.

## Other hosts

Each skill is a folder with a `SKILL.md` and a `references/` folder, which is the open Agent Skills layout. In a host that loads skills from a folder, copy `plugins/<family>/skills/<family>/` into that host's skills folder. This has not been tried in any host other than Claude Code, and it is not claimed to work.

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

Security, finance, people and HR, and legal and compliance give support material, not professional advice. Their cards keep the Safeguards paragraph, and the read-only subagents embed the family's sensitive-domain rules. Take consequential decisions to a qualified person.

## What is and is not established

The plugin manifests, skills and subagents are generated from the cards by the build and checked for structure: names, description limits, links and freshness. `claude plugin validate` accepts the marketplace and the plugins checked (the marketplace plus the marketing-growth, security and software-engineering plugins), and in a local smoke test on Claude Code 2.1.302 a plugin loaded with `--plugin-dir`, its skill and subagents were listed, and invoking the skill read the selected card on demand. A second local smoke test (same version, `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=3`, `claude --agent orchestration:orchestration-orchestrator --plugin-dir plugins/orchestration`) saw the orchestrator delegate to a specialist, and that specialist delegate to another, whose output came back in the result. On 2026-10-17 `claude plugin marketplace add cyberwiz-io/ai-specialists` and `claude plugin install marketing-growth@ai-specialists` (and `orchestration@ai-specialists`) succeeded from GitHub on Claude Code 2.1.302 with a clean config folder, and `claude plugin list` showed both enabled. A headless `claude -p` run from an unrelated folder then used the installed marketing-growth skill: before `allowed-tools` was added, its card reads were denied; after, with only `--allowedTools "Skill"`, it read the strategist card and quoted its Acceptance line with no denials. Each family's skill ZIP was built and listed; its folder holds `SKILL.md` and `references/` at the top level. That is a few developer sessions, not a trial: no claude.ai upload (so whether it accepts the `allowed-tools` line is unobserved), no unaided-user trial and no card evaluation run is recorded. Skill triggering on a plain task description, delegation behavior and upload availability may differ from what is described here. Report what you see in a GitHub issue.

The files in `plugins/` and `.claude-plugin/` are generated. To change a specialist, edit its card in `catalog/` and rebuild; see [Contributing](../CONTRIBUTING.md).
