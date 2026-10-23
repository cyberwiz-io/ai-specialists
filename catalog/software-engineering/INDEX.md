# Software engineering

Version: 1.3. Folder `catalog/software-engineering/`. 11 specialists. This file is generated; edit the cards or `catalog/families.json`.

Planning, review and documentation of software changes from supplied code, requirements and notes.

## Specialists

| Specialist | ID | Use for |
| --- | --- | --- |
| [Requirements analyst](requirements-analyst.md) | `software-engineering/requirements-analyst` | Turning rough requests, tickets, meeting notes and user complaints into clear, testable requirements for a software change. |
| [Software architect](software-architect.md) | `software-engineering/software-architect` | Comparing design options for a system or a significant change and recording a recommended direction. |
| [Feature change planner](feature-change-planner.md) | `software-engineering/feature-change-planner` | Breaking one feature or fix into the smallest ordered steps a developer can follow in the supplied code. |
| [Code reviewer](code-reviewer.md) | `software-engineering/code-reviewer` | Reviewing code or a change the user supplies for correctness, clarity, maintainability and risk. |
| [Test designer](test-designer.md) | `software-engineering/test-designer` | Designing test cases and a coverage argument for supplied requirements or code. |
| [Refactoring planner](refactoring-planner.md) | `software-engineering/refactoring-planner` | Planning a safe, step-by-step cleanup of supplied code that keeps its behavior the same. |
| [API designer](api-designer.md) | `software-engineering/api-designer` | Designing the contract of an interface between pieces of software, such as a web service, library or message format. |
| [Debugging analyst](debugging-analyst.md) | `software-engineering/debugging-analyst` | Finding the likely cause of a defect from the error text, logs, code and symptoms the user supplies. |
| [Technical writer](technical-writer.md) | `software-engineering/technical-writer` | Writing or improving developer and user documentation for software from supplied code, notes and specifications. |
| [Release notes writer](release-notes-writer.md) | `software-engineering/release-notes-writer` | Turning a supplied list of changes into clear notes for people who use the software. |
| [Schema reviewer](schema-reviewer.md) | `software-engineering/schema-reviewer` | Reviewing a supplied data model, table definitions or change script for correctness, integrity and migration risk. |

## Typical flow

Pin down the requirement, plan the smallest change, review supplied code or tests, then document the result. Nothing is run or changed in the user's systems by these instructions.

## Shared rules

- [FAMILY-COORDINATOR.md](../../pack/FAMILY-COORDINATOR.md)
- [Card guide](../../docs/CARD-GUIDE.md)
