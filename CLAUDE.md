# Automotive SPICE toolkit for ECU software

Skills, agents, hooks and deterministic tools for developing automotive ECU software in
line with Automotive SPICE 3.1. Engineering artifacts are text files in this
repository - one item per file - and a trace engine checks them.

## How work is done here

@.claude/docs/working-agreement.md

## Where things are

| Path | Content |
|---|---|
| `project.yaml` | scope of the project: role, processes the team is responsible for, paths. Written by `/aspice-start`. Absent in a fresh copy of the toolkit |
| `plans/`, `spec/`, `verification/`, `records/` | the project's items, in the folders `schema/items.yaml` names |
| `src/`, `tests/` | code and test code |
| `aspice/3.1/` | process catalog (`processes/`) and notes per process (`notes/`) |
| `schema/` | item types, links and coverage rules (`items.yaml`), file layout (`item-format.md`) |
| `tools/` | trace engine, record writer, validators |
| `.claude/skills/`, `.claude/agents/`, `.claude/hooks/` | the toolkit itself |
| `.claude/docs/` | working agreement, command reference (`tools.md`), review checklists, authoring conventions |
| `examples/power-window/` | a complete worked example |

## Skills

| Skill | Process | Use it to |
|---|---|---|
| `/aspice-start` | - | set up or change the project scope |
| `/import-inputs` | boundary of the scope | register what was received and prepare its acceptance |
| `/sw-requirements` | SWE.1 | derive and analyse software requirements |
| `/sw-architecture` | SWE.2 | components, interfaces, views, decisions, allocation |
| `/sw-detailed-design` | SWE.3 | component designs and software units |
| `/sw-unit-implement` | SWE.3 | code for an approved unit design |
| `/sw-unit-verify` | SWE.4 | strategy, unit test cases, tests, static analysis, coverage, records |
| `/review` | all | the only way an item becomes approved |
| `/trace-check` | all | explain what the trace engine reports |
| `/process-gate` | all | readiness of a process, practice by practice |
| `/baseline` | SUP.8 | baselines and their communication |
| `/change-request` | SUP.10 | changes to baselined items |
| `/project-plan` | MAN.3 | scope, life cycle and milestones, feasibility, resources, skills, interfaces, reporting |
| `/work-breakdown` | MAN.3 | work packages, activities, estimates, schedule, dependencies |
| `/project-status` | MAN.3 | progress against the plan, status reports, corrective actions |
| `/next-step` | - | where the project stands and what to do next |

Processes without a skill of their own are still in the catalog and covered by the
schema's rules; say so when the user asks for one.

## Commands worth knowing

```
python tools/traceability.py check              # findings for the project in the current folder
python tools/traceability.py --project examples/power-window check
python tools/traceability.py practices SWE.1    # evidence and open findings per base practice
python -m unittest discover -s tools/tests      # tests of the engine and the hooks
python tools/skill_lint.py                      # mechanical checks of skills, agents, checklists
```

The full command reference is `.claude/docs/tools.md`. Read it before calling a tool
for the first time in a session.

## Changing the toolkit itself

- Follow `.claude/docs/skill-authoring.md` for skills, checklists and agents.
- `schema/items.yaml` is the single definition of items and rules; after a change run
  `python tools/schema_check.py` and the tests.
- Text of Automotive SPICE and of other standards is not reproduced anywhere in this
  repository: identifiers and official names only, descriptions in our own words.
- Before a commit, `python tools/confidentiality_scan.py` must report no finding.
