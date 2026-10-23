# Orchestration and meta

Version: 1.4. Folder `catalog/orchestration/`. 5 specialists. This file is generated; edit the cards or `catalog/families.json`.

Routing work to the right specialists, breaking down plans, packaging handoffs and reviewing across families. The Coordinator itself lives in the pack folder.

## Specialists

| Specialist | ID | Use for |
| --- | --- | --- |
| [Task router](task-router.md) | `orchestration/task-router` | Choosing which specialist roles should handle a request, in what order, and what to leave out. |
| [Plan decomposer](plan-decomposer.md) | `orchestration/plan-decomposer` | Breaking a large or vague goal into ordered, checkable pieces of work that individual specialist roles can take one at a time. |
| [Handoff packager](handoff-packager.md) | `orchestration/handoff-packager` | Assembling the exact packet one role passes to the next, so the next role needs nothing else and sees nothing unneeded. |
| [Specialist builder](specialist-builder.md) | `orchestration/specialist-builder` | Drafting and reviewing a custom role card at the user's request when no existing role fits. |
| [Cross-family reviewer](cross-family-reviewer.md) | `orchestration/cross-family-reviewer` | Reviewing a nontrivial combined result from one or more specialist families against the user's request and the contributing pieces. |

## Typical flow

Route the task, decompose it, package handoffs, run suitable independent work in real subagents when supported, and require different-model review of the exact nontrivial result before calling it ready.

## Shared rules

- [FAMILY-COORDINATOR.md](../../pack/FAMILY-COORDINATOR.md)
- [Card guide](../../docs/CARD-GUIDE.md)
