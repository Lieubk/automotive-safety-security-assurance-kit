# Automotive Safety & Security Assurance Kit

Skills, agents, hooks and deterministic tools for developing automotive ECU software in
line with Automotive SPICE 3.1 (4.0 from its draft), ISO 26262 and ISO/SAE 21434.
Engineering artifacts are text files in this repository - one item per file - and a
trace engine checks them.

## How work is done here

@.claude/docs/working-agreement.md

## Where things are

| Path | Content |
|---|---|
| `project.yaml` | scope of the project: role, processes the team is responsible for, paths. Written by `/aspice-start`. Absent in a fresh copy of the toolkit |
| `plans/`, `spec/`, `verification/`, `records/` | the project's items, in the folders `schema/items.yaml` names |
| `src/`, `tests/` | code and test code |
| `aspice/3.1/` | process catalog (`processes/`) and notes per process (`notes/`) |
| `aspice/4.0/` | catalog of Automotive SPICE 4.0 built from the draft 3.991, each practice mapped to 3.1 (`maps_to`); chosen by `aspice.version` in `project.yaml` |
| `iso-26262/2018/` | catalog of ISO 26262: parts, clauses, requirement numbers, work products, table titles, purposes in our words |
| `iso-sae-21434/2021/` | catalog of ISO/SAE 21434: clauses, subclauses, requirement and work product identifiers, objectives in our words |
| `schema/` | item types, links and coverage rules (`items.yaml`), file layout (`item-format.md`), generated documents (`documents.yaml`) |
| `tools/` | trace engine, record writer, validators |
| `.claude/skills/`, `.claude/agents/`, `.claude/hooks/` | the toolkit itself |
| `.claude/docs/` | working agreement, command reference (`tools.md`), review checklists, authoring conventions |
| `examples/power-window/` | worked example of a software supplier (SWE.1 to SWE.6, ISO 26262 at ASIL B, a TARA) |
| `examples/door-control-unit/` | worked example of a system supplier (SYS.2 to SYS.5, supplier, risks, vulnerability monitoring, release) |
| `.claude-plugin/`, `hooks/hooks.json` | the packaging as a Claude Code plugin: manifest, marketplace, the hooks run from the plugin |

## Skills

| Skill | Process | Use it to |
|---|---|---|
| `/aspice-start` | - | set up or change the project scope |
| `/import-inputs` | boundary of the scope | register what was received and prepare its acceptance |
| `/sys-requirements` | SYS.2 | derive and analyse system requirements from stakeholder requirements |
| `/sys-architecture` | SYS.3 | system elements, interfaces, views, decisions, allocation |
| `/sw-requirements` | SWE.1 | derive and analyse software requirements |
| `/sw-architecture` | SWE.2 | components, interfaces, views, decisions, allocation |
| `/sw-detailed-design` | SWE.3 | component designs and software units |
| `/sw-unit-implement` | SWE.3 | code for an approved unit design |
| `/sw-unit-verify` | SWE.4 | strategy, unit test cases, tests, static analysis, coverage, records |
| `/sw-integration-test` | SWE.5 | integration strategy and steps, integration test cases, builds, runs |
| `/sw-qualification-test` | SWE.6 | qualification strategy, test cases from requirements, runs, bench reports |
| `/sys-integration-test` | SYS.4 | system integration strategy and steps, integration tests, system builds and bench runs |
| `/sys-qualification-test` | SYS.5 | system qualification strategy, test cases from system requirements, bench and vehicle runs |
| `/review` | all | the only way an item becomes approved |
| `/trace-check` | all | explain what the trace engine reports |
| `/process-gate` | all | readiness of a process practice by practice, or of ISO 26262 and ISO/SAE 21434 clause by clause |
| `/mock-assessment` | all | rehearsal of an assessment: evidence pack, questions, ratings by named people, consistency |
| `/baseline` | SUP.8 | baselines and their communication |
| `/change-request` | SUP.10 | changes to baselined items |
| `/problem-resolution` | SUP.9 | problems from recording to closure, urgent actions, alerts, trends |
| `/supplier-monitoring` | ACQ.4 | supplier agreements, technical and progress reviews with suppliers, exchanged information, deviations |
| `/quality-assurance` | SUP.1 | quality assurance plan, checks of work products and processes, non-conformances, escalation, quality reports |
| `/project-plan` | MAN.3 | scope, life cycle and milestones, feasibility, resources, skills, interfaces, reporting |
| `/work-breakdown` | MAN.3 | work packages, activities, estimates, schedule, dependencies |
| `/risk-management` | MAN.5 | risk management plan, risks rated, treated, monitored, accepted, corrective actions |
| `/project-status` | MAN.3 | progress against the plan, status reports, corrective actions |
| `/cybersecurity-plan` | ISO/SAE 21434 cl. 6, 7, 12-14 | cybersecurity plan with tailoring and TARA method, interface agreement, post-development plans, cybersecurity case, assessment record |
| `/tara` | ISO/SAE 21434 cl. 9.3, 9.4, 15 | item definition, assets, damage and threat scenarios, attack paths, ratings, risk values, treatment, goals and claims |
| `/cybersecurity-concept` | ISO/SAE 21434 cl. 9.5, 10, 11 | requirements derived from goals, security relevance down the levels, verification and validation |
| `/vulnerability-management` | ISO/SAE 21434 cl. 8 | monitoring plan, events, weaknesses, vulnerability analysis and treatment |
| `/safety-plan` | ISO 26262-2, 8 | safety plan with a decision per clause, methods per table, determinations, confirmation measures, tool evaluation, safety case |
| `/hara` | ISO 26262-3 | item definition, hazardous events classified, ASIL, safety goals |
| `/safety-concept` | ISO 26262-3, 4, 6, 9 | functional, technical and software safety requirements, ASIL inheritance, decomposition, validation |
| `/safety-analysis` | ISO 26262-9, 6, 4 | FMEA, FTA, DFA with findings carried into requirements or design |
| `/component-qualification` | ISO 26262-8 | qualification of supplied or reused software components of ASIL A to D, or a proven in use argument from field data |
| `/release` | SPL.2, ISO 26262-2, ISO/SAE 21434 6.4.9 | release plan, release record from a baseline with approval and release note, delivery and receipt |
| `/documents` | all | 40 kinds of documents from the items - specifications, SAD, SDD, test specifications and reports, traceability, release, QA, problem, project, risk, TARA and cybersecurity reports - as HTML, PDF, Word or Excel, neutral or in the customer's template |
| `/next-step` | - | where the project stands and what to do next |

Processes without a skill of their own are still in the catalog and covered by the
schema's rules; say so when the user asks for one.

## Commands worth knowing

```
python tools/traceability.py check              # findings for the project in the current folder
python tools/traceability.py --project examples/power-window check
python tools/traceability.py practices SWE.1    # evidence and open findings per base practice
python tools/traceability.py clauses           # ISO/SAE 21434: decision, evidence and findings per subclause
python tools/traceability.py safety            # ISO 26262: decision, evidence and findings per clause
python tools/document.py build software-architecture-description --format docx   # documents from the items
python tools/xlsx.py sheets inputs/delivery.xlsx    # Excel exchange; tools/alm.py for Polarion, codebeamer, Jama
python -m unittest discover -s tools/tests      # tests of the engine and the hooks
python tools/skill_lint.py                      # mechanical checks of skills, agents, checklists
```

The full command reference is `.claude/docs/tools.md`. Read it before calling a tool
for the first time in a session.

## Changing the toolkit itself

- Follow `.claude/docs/skill-authoring.md` for skills, checklists and agents. A new agent is
  also listed in `.claude-plugin/plugin.json`; a hook change is made in `.claude/settings.json`
  and in `hooks/hooks.json` (`tools/tests/test_plugin.py` compares them).
- `schema/items.yaml` is the single definition of items and rules; after a change run
  `python tools/schema_check.py` and the tests.
- Text of Automotive SPICE and of other standards (ISO/SAE 21434 and ISO 26262 included,
  with their annexes, example tables and normative tables) is not reproduced anywhere in this repository:
  identifiers and official names only, descriptions in our own words.
- Before a commit, `python tools/confidentiality_scan.py` must report no finding.
