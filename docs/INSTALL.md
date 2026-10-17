# Install without pasting

You do not have to paste a pack into a chat. Each family is also an installable skill, with the specialist cards loaded only when a task needs them, so a conversation starts small instead of with about 8,000 tokens of pasted text. Pasting a [combined pack](../pack/START-HERE.md) still works in any host.

Nothing here adds a capability. A skill is advisory instructions, and the plugins are materials only: they do not publish, send, schedule, connect or run anything.

## Claude Code

Add the marketplace once, then install the families you want:

```
/plugin marketplace add cyberwiz-io/ai-specialists
/plugin install marketing-growth@ai-specialists
```

Then describe your task, for example "Help me plan a small-business campaign", or invoke the skill by name with `/marketing-growth:marketing-growth`. Install only the families you need: each plugin adds one skill and one subagent per specialist in that family.

The first time a skill reads one of its own specialist cards, Claude Code may ask permission to read that file; allow it. The cards are plain text inside the installed plugin. In non-interactive `claude -p` runs that prompt cannot be answered, so the read is refused unless the plugin folder is the working directory or you pre-approve the read.

The subagents have read-only tools (`Read`, `Grep`, `Glob`). A specialist can read files you point to, and it cannot run commands, edit files, browse or contact anyone. A subagent cannot call another subagent, so a card's handoff line is a recommendation for the main conversation.

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

The plugin manifests, skills and subagents are generated from the cards by the build and checked for structure: names, description limits, links and freshness. `claude plugin validate` accepts the marketplace and the plugins checked (the marketplace plus the marketing-growth, security and software-engineering plugins), and in a local smoke test on Claude Code 2.1.302 a plugin loaded with `--plugin-dir`, its skill and subagents were listed, and invoking the skill read the selected card on demand. That is one developer session, not a trial: no marketplace install from GitHub, no claude.ai upload, no unaided-user trial and no card evaluation run is recorded. Skill triggering on a plain task description, delegation behavior and upload availability may differ from what is described here. Report what you see in a GitHub issue.

The files in `plugins/` and `.claude-plugin/` are generated. To change a specialist, edit its card in `catalog/` and rebuild; see [Contributing](../CONTRIBUTING.md).
