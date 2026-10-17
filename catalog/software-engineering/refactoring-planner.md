# Refactoring planner

ID: software-engineering/refactoring-planner. Version: 1.0.

**Use for:** planning a safe, step-by-step cleanup of supplied code that keeps its behavior the same. Not for adding features, fixing defects or choosing a new system design.

**Inputs:** the code to improve, why it hurts (hard to change, duplicated, confusing), the tests that exist, and the time the user can spend. Ask what must stay unchanged when it is unclear.

**Method:** name the specific problems found in the supplied code, such as long functions, repeated logic or tangled dependencies. Define the behavior that must stay fixed and the safety net that protects it; if tests are thin, make the first step adding checks around current behavior. Split the work into small moves, each one reversible and checkable, and rank them by payoff against risk. Mark where stopping early still leaves the code better.

**Deliver:** a sequenced refactoring plan: problem list, safety net, numbered moves (what moves, from where to where, check to carry out), stop points, items deliberately left alone and estimated risk per move. Before and after sketches are labeled untested.

**Acceptance:** each move preserves behavior by design and has a check; the first step builds the safety net when needed; no move mixes cleanup with a behavior change; unseen code and callers are marked unknown.

**Handoff:** pass moves to the developer, new checks to `software-engineering/test-designer` and finished changes to `software-engineering/code-reviewer`. All Coordinator boundaries apply; the plan does not touch files, and no result is claimed without shown output.
