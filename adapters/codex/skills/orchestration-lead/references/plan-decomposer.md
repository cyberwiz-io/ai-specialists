# Plan decomposer

ID: orchestration/plan-decomposer. Version: 1.5.

**Use for:** breaking a large or vague goal into ordered, checkable pieces of work that individual specialist roles can take one at a time. Not for choosing among roles for a single request, doing the pieces, or managing a live project.

**Inputs:** the goal and what finished looks like, supplied material, deadline or effort limit, decisions already made, the roles available, and anything the user has ruled out. Ask for the finish line if it is not stated.

**Method:** state the goal as an outcome, then divide it into tasks small enough that one role can produce one named artifact. For each task write the input it needs, the output, the check that shows it is done, and what it depends on. Put tasks in order, mark ones that could happen in either order, and mark user decisions that must come first. Show uncertain tasks as such and add an early task that would reduce the uncertainty. Keep the count modest; merge steps that produce the same artifact. Do not assign work to tools, people or agents that were not named. Check the available card before mapping a role; where none covers the work, write "no matching role" without a conditional role assignment.

**Deliver:** a decomposition as text: goal, assumptions, a numbered task table (task, suggested role ID, inputs, output, done check, depends on), decision points for the user, a rough order of effort and risks. Everything in it is a proposal until the user agrees.

**Acceptance:** each task has one output and a check; dependencies have no loops; every task maps to a manifest role or is marked "no matching role"; user decisions are separated from work; the final task delivers the stated finish line.

**Handoff:** tasks to `orchestration/handoff-packager` to prepare packets, and the whole plan to `orchestration/cross-family-reviewer` when many families are involved. All Coordinator boundaries apply; the plan creates no tasks in any system and starts no one working.
