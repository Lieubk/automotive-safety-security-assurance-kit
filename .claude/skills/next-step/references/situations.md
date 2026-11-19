# Stops, rules and skills

The walk has seven stops. At each one, collect what is open. The first stop with
something open gives the recommendation; the others go into "also open". A finding
line of `check` reads `level  rule  item  message  [base practices]`.

## Stop 1: scope

| Shows as | Meaning | Recommend |
|---|---|---|
| summary line of `check` says `scope: all processes` | `scope.processes` is missing or empty; every rule runs | `/aspice-start` |
| `practices` prints `process is not in the catalog` for an ID | the scope names a process the catalog does not have | `/aspice-start` |
| `inputs` is missing in `project.yaml` | what was received is not recorded | `/aspice-start inputs`; do not conclude that nothing was received |
| `aspice.target_level` or `scope.assessment_scope` is missing | target and assessment scope are not recorded | say so and ask the user; do not assume level 1 or "no assessment" |
| a process in `assessment_scope` that is not in `processes` | rated, but not checked | a warning in the report, not a stop |

## Stop 2: structure

`FORMAT`, `SCHEMA` and `LINK` findings mean an item file cannot be relied on. They
come before everything else, because coverage results for a broken item are not
trustworthy.

| Finding on | Recommend |
|---|---|
| an item of the team | the authoring skill of its type (table under stop 5) |
| an imported item | `/import-inputs`: it corrects the item against the source while no acceptance review covers it, and retires and registers it again afterwards |
| a final record | records are not edited; the skill that wrote it writes a new one |

Two `LINK` messages say more than "broken":

| Message | Meaning | Recommend |
|---|---|---|
| `<role> target <ID> is obsolete` or `is rejected` | a live item still builds on a retired one | the authoring skill of the linking item, to move or remove the link; for a retired input the hand-over of `/import-inputs` names the successor, if there is one |
| `script names ..., which does not exist` | a test case points at a test file or function that is not there | `/sw-unit-verify` |

## Stop 3: boundary inputs

Whether an input was registered and accepted is looked up; the tools report the rest.

1. Registered? For each entry of `inputs` whose `level` is not `code`, Grep the item
   folders for the `source` name of the entry. An item that carries it in its
   `imported` block (or in `source_document`) was registered from that input. No
   such item: the input is not registered. Recommend `/import-inputs` with that
   source.
2. Accepted? Run `python tools/traceability.py list --imported --status draft` and
   `python tools/traceability.py list --imported --status in-review`. Every item they
   print is an input without acceptance: newly registered, or replaced by a new
   version. Recommend `/review` with the checklist `input-acceptance` and those IDs.
   `COV-19` on an imported item means the same: its acceptance review is missing or
   no longer covers its content.
3. Changed or retired? A new version of an input shows as `UPSTREAM` and `SUSPECT`
   on the items derived from it (stop 5, question 3), a withdrawn input as the `LINK`
   message of stop 2. Nothing has to be looked up for either.
4. Questions open? `python tools/traceability.py list --type query --status open`
   names the open queries, `show <QRY-ID>` the inputs each is about. An input whose
   acceptance review ended in rework because of a query waits for the answer: the
   recommendation is to the user, to get it from the source, and then
   `/import-inputs <QRY-ID>` to record it. `--status answered` names the queries whose
   answer is recorded but not yet carried into the items: `/import-inputs` when the
   answer came as a new version, otherwise `/review` of the input, which closes the
   finding.

## Stop 4: plans

`COV-27` names each plan kind the scope needs and has no approved plan for.

| Plan kind in the message | Process | Recommend |
|---|---|---|
| `unit-verification` | SWE.4 | `/sw-unit-verify` |
| `configuration-management` | SUP.8 | `/baseline` |
| `change-request-management` | SUP.10 | `/change-request` |
| `project` | MAN.3 | `/project-plan` |
| `software-integration` | SWE.5 | `/sw-integration-test` |
| `software-qualification-test` | SWE.6 | `/sw-qualification-test` |
| `problem-resolution` | SUP.9 | `/problem-resolution` |
| `quality-assurance` | SUP.1 | `/quality-assurance` |
| `risk-management` | MAN.5 | `/risk-management` |
| `system-integration` | SYS.4 | `/sys-integration-test` |
| `system-qualification-test` | SYS.5 | `/sys-qualification-test` |

These skills draft the plan of their process; their base practice tables say so.
If one of them is not installed, its plan is written by hand like the others. A plan
in `draft` or `in-review` goes to `/review`. A plan written by hand follows the type
`plan` in `schema/items.yaml` and the notes of its process under `aspice/3.1/notes/`.

## Stop 5: the processes in scope, in the order of the V

Order: SYS.1, SYS.2, SYS.3, SWE.1, SWE.2, SWE.3, SWE.4, SWE.5, SWE.6, SYS.4, SYS.5.
Skip what is not in scope. For each process ask three questions, in this order:

1. Is work of this process missing? (rules of the first table)
2. Are its items still in `draft` or `in-review`? (`status`, by item type)
3. Is an approval stale or resting on something unapproved, a link suspect,
   consistency not evidenced, a review finding or a query open?
   (`COV-19`, `UPSTREAM`, `SUSPECT`, `CONSISTENCY`, `QUERY` on its items)

Findings on items in `draft` are printed at level `info`; they are real, and they are
the reason `check --all` is used here. For every draft that is not complete,
`check --all` also prints `still to come before review: ...` with the attributes and
sections that are missing. Such a draft goes back to its authoring skill, not to
`/review`.

| Process | Rule | The message means | Recommend |
|---|---|---|---|
| SYS.2 | `COV-01` | an accepted stakeholder requirement has no system requirement | `/sys-requirements` |
| SYS.2 | `COV-02` | a system requirement has neither a parent nor a rationale for having none | `/sys-requirements` |
| SYS.3 | `COV-03`, `COV-04` | a system requirement is not allocated; an element has nothing allocated | `/sys-architecture` |
| SWE.1 | `COV-05` | a system requirement allocated to software has no software requirement | `/sw-requirements` |
| SWE.1 | `COV-06` | a software requirement has neither a parent nor a rationale | `/sw-requirements` |
| SWE.2 | `COV-07` | a software requirement is not allocated | `/sw-architecture` |
| SWE.2 | `COV-08` | a component has no requirement allocated | `/sw-architecture` |
| SWE.2 | `COV-24`, `COV-25` | a view shows nothing valid; a view kind the project needs is missing | `/sw-architecture` |
| SWE.3 | `COV-09` | a developed component has no detailed design or no unit | `/sw-detailed-design` |
| SWE.3 | `COV-21` | no unit of the providing component realizes an interface | `/sw-detailed-design` |
| SWE.3 | `COV-10` | `designed but not implemented` (a warning: the unit lists no source files yet), or a named source file does not exist; or a unit does not belong to exactly one component | `/sw-unit-implement` for the code; `/sw-detailed-design` for the `part_of` link |
| SWE.3 | `COV-22` | designed functions and code differ: a function missing on either side, or parameter or return types that are not those of the design | `/sw-unit-implement`; `/sw-detailed-design` when the design is what has to change |
| SWE.3 | `COV-11` | a file under a source root belongs to no unit, or to several | `/sw-detailed-design`; `/aspice-start paths` when the file is generated or third-party code |
| SWE.4 | `COV-12`, `COV-28`, `COV-29` | a unit has no unit test, no static analysis entry, coverage below target, or a designed function no test names | `/sw-unit-verify` |
| SWE.4 | `COV-17`, `COV-18` on unit tests | a test verifies nothing valid; a test has no verdict in the latest run | `/sw-unit-verify` |
| SWE.4 | `COV-30` | code or test files changed after the latest run, or the run does not record what it ran on | `/sw-unit-verify`, to run again |
| SWE.5 | `COV-13`; `COV-17`, `COV-18` on its tests | an interface has no integration test; a test has no verdict on a build of its step | `/sw-integration-test` |
| SWE.5 | `COV-35`, `COV-37` | a component is in no step of the strategy, or in two; a step has no test, or a test names an unknown step | `/sw-integration-test` |
| SWE.5 | `COV-36`, `COV-38` | a step has no current successful build, or its latest run tested an older build | `/sw-integration-test`, to build and run again |
| SWE.6 | `COV-14`; `COV-17`, `COV-18`, `COV-38` on its tests and runs | a software requirement has no qualification test or review; a test has no verdict; the run tested an older build | `/sw-qualification-test` |
| SYS.4 | `COV-15`; `COV-17`, `COV-18` on its tests | a system interface has no integration test; a test has no verdict on a build of its step | `/sys-integration-test` |
| SYS.4 | `COV-46` to `COV-49` | an element in no step or two; a step without a current system build, or whose build holds older software; a step without tests; a run on an older build | `/sys-integration-test` |
| SYS.5 | `COV-16`; `COV-17`, `COV-18`, `COV-49` on its tests and runs | a system requirement has no qualification test or review; the run tested an older system build | `/sys-qualification-test` |
| any | `COV-23` | an item has a lower ASIL than what it depends on; a test case lower than what it verifies | the authoring skill of the item; a decomposition needs an approved `design-decision` |
| MAN.3 | `COV-31`, `COV-33`, `COV-34` | the work breakdown has a cycle, lacks a category, or dates that do not fit | `/work-breakdown` |
| MAN.3 | `COV-32` | an item no work package delivers | `/work-breakdown link` |
| MAN.3 | - | `progress` shows a package late, a milestone missed or at risk, a corrective action overdue, or no status report since the last reporting date of the plan | `/project-status` |

`COV-05` asks for a software requirement per system requirement that is allocated to
software. If `trace.derive_via_elements` is `true` in `project.yaml`, a software
requirement derived from the software element is enough for all requirements
allocated to that element; say so in the report whenever `COV-05` is silent for that
reason, because single system requirements can then be uncovered without a finding.
An allocation is the `fulfils` link of an element or interface. A system requirement
that no element of kind `software` fulfils is not looked at by `COV-05` at all; for
imported requirements that is a question for `/import-inputs`.

Question 2, by type:

| Item type in `status` | Process | Authoring skill | Then |
|---|---|---|---|
| `stakeholder-requirement` | SYS.1 | `/import-inputs` registers; assessment by people | `/review` |
| `system-requirement` | SYS.2 | `/sys-requirements` | `/review` |
| `system-element`, `system-interface` | SYS.3 | `/sys-architecture` | `/review` |
| `software-requirement` | SWE.1 | `/sw-requirements` | `/review` |
| `software-component`, `software-interface`, `architecture-view`, `design-decision` | SWE.2 (views and decisions of level `system`: SYS.3; decisions of level `detailed-design`: SWE.3) | `/sw-architecture` | `/review` |
| `component-design`, `software-unit` | SWE.3 | `/sw-detailed-design`; code: `/sw-unit-implement` | `/review` |
| `unit-test` | SWE.4 | `/sw-unit-verify` | `/review` |
| `software-integration-test` | SWE.5 | `/sw-integration-test` | `/review` |
| `software-qualification-test` | SWE.6 | `/sw-qualification-test` | `/review` |
| `system-integration-test` | SYS.4 | `/sys-integration-test` | `/review` |
| `system-qualification-test` | SYS.5 | `/sys-qualification-test` | `/review` |
| `plan` | the process of its `kind` (stop 4) | see stop 4 | `/review` |
| `change-request` | SUP.10 | `/change-request` | - |
| `work-package` | MAN.3 | `/work-breakdown` | `/review` |
| `corrective-action` | MAN.3 | `/project-status` | - |
| `problem-report` | SUP.9 | `/problem-resolution` | - |
| `supplier-agreement` | ACQ.4 | `/supplier-monitoring` | `/review` |
| `risk` | MAN.5 | `/risk-management` | - |

To name the IDs behind a count, run
`python tools/traceability.py list --type <type> --status <state>`.
An imported item belongs to stop 3, whatever its type.

Question 3:

| Rule | The message says | Recommend |
|---|---|---|
| `UPSTREAM` | `approved, but <target> (<role>) is in state draft` or `in-review` | the item rests on something not approved. Recommend `/review` of the target first; if the target is an input, its acceptance review. The tool refuses to approve anything above it until then |
| `QUERY` | `open query <QRY-ID> is about this approved item` | a question to the source is open. The item stays approved; say what waits for the answer. The user gets the answer; `/import-inputs <QRY-ID>` records it. With "(not put to its source yet)": the question still has to be sent; the user adds `asked_at` when it is |
| `PROBLEM` | `problem report <PRB-ID> (...) concerns this approved item` | a known problem in the item is not resolved. Recommend `/problem-resolution <PRB-ID>`: it chooses the route - the authoring skill of the item and `/review`, inside a baseline `/change-request` first |
| `COV-19` | `review ... left findings open: ...` on an item in `draft` or `in-review` | the last review of the item ended in rework. Recommend the authoring skill to work on the findings, then `/review`; for an imported input the finding cites a query, and the next step is the answer to it |
| `COV-19` | `stale approval: content changed since review ...` or `approved, but no final review record covers it` | `/review` |
| `COV-19` | `review ... still has open findings`, or an earlier finding on the same content `open and not closed by a later finding entry` | the authoring skill to rework the item, then `/review`, which closes the earlier finding explicitly |
| `SUSPECT` | `suspect link: <target> (<role>) changed after review ...` | run `python tools/traceability.py impact <target>` and show it; then `/review` of the suspect item against the new content; the authoring skill first if the item itself has to change |
| `SUSPECT` | `<file> changed after review ...: the code is no longer ...` | the code of a unit changed after the unit was reviewed: `/review` with the unit as subject; `/sw-unit-verify` if `COV-30` shows as well |
| `CONSISTENCY` | `review ... does not record <target> as a reference` | `/review`, so that the comparison is on record |
| `CONSISTENCY` | `review ... does not record <file>: a review of the code ...` | the unit has code that no review compared with its design: `/review` with the unit as subject |

The newest final review of an item's current content decides. A dependent that is
still right after its upstream changed needs no rework: `/review` records a
reconfirmation against the new upstream version, which clears the `SUSPECT` line.

"By hand" means: the toolkit has the item type, the rules and the review, but no skill
that drafts. The item is written following `schema/items.yaml`, `schema/item-format.md`
and the notes of the process under `aspice/3.1/notes/`, and then goes to `/review`.

## Stop 6: evidence that follows approval

| Shows as | Meaning | Recommend |
|---|---|---|
| `COV-26` | a final baseline has no communication record | `/baseline` |
| `no evidence yet` in `practices` for a "communicate" or "summarize and communicate" practice, or for SUP.8.BP6 | no baseline or no communication record exists yet | `/baseline`, when the items are approved |
| `COV-20` | a change request past `submitted` names no affected item | `/change-request` |
| `change-request` items in a state other than `closed` or `rejected` in `status` | changes under way | `/change-request` |
| `problem-report` items not `closed` or `rejected` | problems open; `python tools/traceability.py problems` lists them with their age | `/problem-resolution` |
| `COV-39`, `COV-40` | an urgent problem without an authorised action; a problem not alerted to the parties the strategy names | `/problem-resolution <PRB-ID>`: the decision and the alert come from people |
| `COV-50`, `COV-51`, `COV-52` | a risk rated outside the scales or with an unknown category; a risk above the threshold neither treated nor accepted by a named person; a risk in treatment without an indicator | `/risk-management <RSK-ID>` |
| `COV-43` | a baseline was made without the quality check the quality assurance plan asks for before it | `/quality-assurance`; the next quality report names it |
| `COV-44`, `COV-45` | a finding of quality assurance without an existing action; a quality report not communicated | `/quality-assurance` |
| `COV-41`, `COV-42` | a problem in a baselined item without a change request; a closed problem without accepted closure, evidence, or with a change request still open | `/problem-resolution <PRB-ID>`; `/change-request` |

## Stop 7: nothing open

When `check --all` prints no finding and every item of the engineering types is
`approved`: recommend `/process-gate` for each process in scope, in the order of the
V, then `/baseline`. The toolkit keeps no record that a gate was run, so ask the user
which gates have been held instead of assuming. When an assessment is planned
(`scope.assessment_scope`), recommend `/mock-assessment` after the gates.

## States printed by `practices`

| State | Read it as | Goes into the report as |
|---|---|---|
| `evidence present` | items exist, are approved or final, no rule objects | present; not a judgement of quality |
| `evidence not settled` | items exist, some are not approved or final | stop 5, question 2 |
| `findings open` | errors of rules that support the practice | stop 5, questions 1 and 3 |
| `warnings open` | warnings only | stop 5, question 3 |
| `no evidence yet` | the schema has a place for the evidence, the project has none | stop 5 or stop 6 |
| `no evidence structure` | the schema has no place for this practice | outside the toolkit: a person shows it |
| `not assessed` | the process is not in the catalog | stop 1 |

## Example

A software supplier with the scope of `examples/power-window` (SWE.1 to SWE.4 and
SUP.8). Every engineering item is approved, the summary line of `check --all` ends
with `0 errors, 0 warnings, 0 on drafts`, no baseline exists, and `practices` prints
among others:

```
SWE.1.BP8   no evidence yet           ...  Communicate agreed software requirements
SUP.8.BP6   no evidence yet           ...  Establish baselines
SUP.8.BP2   no evidence structure     ...  Identify configuration items
```

The report then says:

- Stands: the summary line of `check --all` and the table of `status`, quoted.
- Open: stops 1 to 5 nothing; `list --imported` shows every input as approved.
  Stop 6: no baseline and no communication record exist, so SWE.1.BP8, SWE.2.BP9,
  SWE.3.BP7, SWE.4.BP7, SUP.8.BP6 and SUP.8.BP7 show `no evidence yet`.
- Recommendation: `/process-gate` for SWE.1, because nothing is open and SWE.1 is the
  first process in scope.
- After that: the gates of SWE.2, SWE.3 and SWE.4, then `/baseline`, which also
  records who was informed.
- Outside the toolkit: SUP.8.BP2 to SUP.8.BP5, SUP.8.BP8 and SUP.8.BP9 have no
  evidence structure in the schema.

Had the summary line ended with `0 errors, 2 warnings` because of two `COV-30` lines,
the walk would stop at SWE.4 instead, and the recommendation would be
`/sw-unit-verify` to run the unit verification again.
