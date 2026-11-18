# Rules of the trace check

Every rule name `python tools/traceability.py check` can print, derived from
`schema/items.yaml` (`coverage`, `conditions`, `links`, `derived`). If the schema and
this page disagree, the schema is right: say so and report the difference.

## Reading a line

```
error   COV-19      SWR-0003   stale approval: content changed since review REV-0002 (current hash 4d166521ec6e)  [SWE.1.BP7]
level   rule        item       message                                                                             base practices
```

| Level | Means |
|---|---|
| `error` | the item is approved (or the record final) and breaks the rule, or the structure is wrong whatever the state. `check` ends with exit code 1 |
| `warning` | the item is in review and does not meet the rule yet; or evidence of a comparison is missing; or an attribute is not known to the schema |
| `info` | the item is a draft, or the line is a preview; shown only with `--all`, counted as "on drafts" in the summary line |

The same gap is an `info` on a draft, a `warning` in review and an `error` once the item
is approved. Rules on the project as a whole (`COV-25`, `COV-27`), on source files
(`COV-11`), on baselines (`COV-26`) and on change requests (`COV-20`) are always errors.
A message that ends in `(pending: the unit has no code yet)` is a `warning` even on an
approved unit: verification cannot exist before the code does. It becomes an `error`
as soon as source files are listed.

The bracket lists the base practices the finding counts for. For a finding on an item
these are the practices of the process that produces the item, as far as that process
is in scope. A line without a bracket counts for no practice of the project: typically a
finding on an imported item whose process lies outside the scope. It is still a finding.

With `--all` the check also prints, per item that has not reached its next state,
`SCHEMA ... still to come before review: ...` or `... before approval: ...`: the
attributes and sections that state will require. These are previews, not violations.

The same line can be printed several times, for example once per function of a unit
that a test case links to. Count items, not lines.

## Why a finding matters

| The bracket names a practice about | While the finding stands |
|---|---|
| traceability (for example SWE.1.BP6, SWE.3.BP5) | for this item it cannot be shown where it comes from or what carries it on; coverage and the effect of a change cannot be worked out there |
| consistency (for example SWE.1.BP7, SWE.4.BP6) | nothing shows that the present content was compared with what it depends on |
| allocation and design (for example SWE.2.BP2, SWE.2.BP4, SWE.3.BP2) | a part of the design is missing: a requirement nobody is responsible for, an interface nothing realises, a view that does not exist |
| a strategy (for example SWE.4.BP1, SUP.8.BP1) | the process runs without an approved plan, so its results cannot be judged against what was intended |
| verification (for example SWE.4.BP2, SWE.4.BP3, SWE.4.BP4) | the criteria or the results the plan asks for are not there for this unit or test case, or they describe code that has changed since |
| communication (for example SWE.1.BP8, SWE.4.BP7) | the content exists, but nothing shows that those who depend on it were informed |
| quality assurance (SUP.1.BP2) | the work product was not checked against its criteria at its present content |

## Who resolves what

Check with Glob `.claude/skills/*/SKILL.md` that a skill is installed before naming it.

| Work | Skill |
|---|---|
| Scope, paths and people in `project.yaml` | `/aspice-start` |
| Inputs received from outside the scope | `/import-inputs` |
| Software requirements (SWE.1) | `/sw-requirements` |
| Software architecture (SWE.2) | `/sw-architecture` |
| Detailed design (SWE.3, design part) | `/sw-detailed-design` |
| Unit code (SWE.3.BP8) | `/sw-unit-implement` |
| Unit verification (SWE.4), including its plan | `/sw-unit-verify` |
| Approval, stale approvals, suspect links, code reviews | `/review` |
| Baselines and what was communicated | `/baseline` |
| Change requests | `/change-request` |
| Any other process | no skill is named here; `/next-step` says where the project stands, and the people responsible for the process act |

## Structure rules

Always evaluated. A coverage result on an item with a structure error is not reliable:
resolve these first.

| Rule | Means | Typical cause | Resolved by | Can it be accepted? |
|---|---|---|---|---|
| `FORMAT` | The file is not a valid item file: no front matter, front matter that is not valid YAML, no `id`, an ID used twice, a file name or folder that does not match ID and type, an ID prefix of another type | file created by hand or copied; item moved to the wrong folder | the authoring skill of the type; layout in `schema/item-format.md` | No |
| `SCHEMA` | The content does not match the type: unknown type or status; an attribute or section that is required at this stage is missing; a value outside the allowed list; a structured entry (`functions`, `elements`, `table`, ...) without a mandatory key; a condition of the schema not met (for example `Rationale` when `origin` is `internal`, `decision` on a change request from state approved or rejected on); `imported` without `source` and `version`; a record entry in the wrong shape. As `warning`: an attribute or key the schema does not know. As `info`: the preview described above | status raised before the content for that stage was written; a misspelt attribute | the authoring skill of the type. For a record: not by hand - the tool that writes it produces a new one | No |
| `LINK` | A reference cannot be followed or is not allowed: unknown link role; a role the type may not carry; a target that does not exist or has the wrong type; a link from a live item to an item that is rejected or obsolete (views: see `COV-24`; retiring an item that is in a baseline needs an approved change request that names it); `<ID>#<name>` naming a function the unit does not design; `provided_by` or `used_by` that is not a software component; `script` of a test case naming a file or a test function that does not exist; `superseded_by` or a record naming an item that does not exist | target renamed, withdrawn or not yet written; test code not written yet or renamed; link set in the wrong direction (links live on the downstream item) | the authoring skill of the item that carries the reference; `/sw-unit-verify` for `script`; `/change-request` first when a baselined item is to be retired | No |

## Approval and consistency

| Rule | Means | Typical cause | Base practices | Resolved by | Can it be accepted? |
|---|---|---|---|---|---|
| `COV-19` | An approved engineering item is not backed by its reviews. Four messages: "stale approval: content changed since review ..."; "approved, but no final review record covers it"; "review ... still has open findings"; "approved by ... although findings of an earlier review of the same content are open and not closed by a later finding entry" | the item was edited after its review; the status was set by hand; a review of the same content ended in rework and its findings were never closed | SUP.1.BP2, SYS.2.BP7, SYS.3.BP7, SYS.4.BP8, SYS.5.BP6, SWE.1.BP7, SWE.2.BP8, SWE.3.BP6, SWE.4.BP6, SWE.5.BP8, SWE.6.BP6 | `/review`; the authoring skill first when findings are open | No. Only a new review restores an approval; an open finding is closed by an entry with `closes` in a later review |
| `SUSPECT` | What the newest approving review of an approved item compared is no longer what is there. Two forms: "suspect link: <item> (<role>) changed after review ..." - an item it links to has changed; "<file> changed after review ...: the code is no longer the code that was reviewed" - a source file of a unit has changed | an upstream item was changed or a new version of an input was imported; code was changed after its review | the practices of the link pair, see "Link roles"; SWE.3.BP6 for code | `/review` against the new version, or of the changed code with the unit as subject and the commit named; `impact <ID>` lists what else depends on a changed item | No |
| `CONSISTENCY` | Nothing shows that a comparison took place. Two forms: "review ... does not record <item> (<role>) as a reference" - the newest approving record lists an item the subject links to neither as reference nor as subject; "review ... does not record <file>: a review of the code against the design is not evidenced" - a unit has source files, and its newest approving record names no code revision or does not list the file | the record was not written by `tools/record.py` or predates the link; code was written after the design was approved and has not been reviewed yet, which is the normal state in between; a later review of the design alone became the newest record | the practices of the link pair; SWE.3.BP6 for code | `/review`; for code a review that names the commit under review | No |

The newest final review record of an item's present content decides. `SUSPECT` and
`CONSISTENCY` are evaluated for approved items that are not imported, and only for link
roles whose practices belong to a process in scope; the two forms about code need SWE.3
in scope.

## Coverage rules

`COV-01` to `COV-30`; `COV-19` is listed above. A rule is active only when at least one
process in the column "Processes" is in `scope.processes`. "Accept" names the waiver the
schema allows. A waiver is content of an item or of `project.yaml`; it is written by
the authoring skill and reviewed like everything else. This skill does not apply
waivers. "Allocated" means: `allocated_to` on the requirement or `fulfils` on the
element; either one counts.

| Rule | Checked on | Expects | Typical cause | Base practices | Processes | Resolved by | Accept |
|---|---|---|---|---|---|---|---|
| `COV-01` | stakeholder requirement with `assessment` accepted or accepted-with-deviation; an imported one without `assessment` counts as accepted | at least one system requirement is `derived_from` it | accepted but not yet analysed; link forgotten on the system requirement | SYS.2.BP6 | SYS.2 | those responsible for SYS.2 | Yes: `assessment: rejected` with an `agreement`; the rule then does not apply |
| `COV-02` | system requirement | at least one `derived_from` link | requirement written without naming its source | SYS.2.BP6 | SYS.2 | those responsible for SYS.2 | Yes: `origin: internal` with a `Rationale` section |
| `COV-03` | system requirement | allocated to at least one system element or system interface | architecture not yet covering the requirement | SYS.3.BP2, SYS.3.BP6 | SYS.3 | those responsible for SYS.3 | Yes: `kind: constraint` with a `Rationale` section |
| `COV-04` | system element | at least one system requirement is allocated to it | element without a job, or allocation forgotten | SYS.3.BP6 | SYS.3 | those responsible for SYS.3 | No |
| `COV-05` | system requirement allocated to an element of kind software | at least one software requirement is `derived_from` that requirement | software requirements not yet written for this input; a software requirement that names only the element as its source | SWE.1.BP6 | SWE.1 | `/sw-requirements` | Yes: `trace.derive_via_elements` in `project.yaml`; a software requirement derived from the element is then enough |
| `COV-06` | software requirement | at least one `derived_from` link | requirement invented without a parent; parent link forgotten | SWE.1.BP6 | SWE.1 | `/sw-requirements` | Yes: `origin: internal` with a `Rationale` section |
| `COV-07` | software requirement | allocated to at least one software component or software interface | architecture not yet written; expected until then | SWE.2.BP2, SWE.2.BP7 | SWE.2 | `/sw-architecture`, which sets `fulfils` on the element | Yes: `kind: constraint` with a `Rationale` section |
| `COV-08` | software component | a software requirement is allocated to it or to a component that is `part_of` it | component added for technical reasons without a requirement | SWE.2.BP7 | SWE.2 | `/sw-architecture` | Yes: `origin` supplied or generated, with the reason for its presence in `Purpose` |
| `COV-09` | software component with `origin: developed` that is not a composition | exactly one component design `refines` it and at least one software unit is `part_of` it | detailed design not started | SWE.3.BP5 | SWE.3 | `/sw-detailed-design` | No |
| `COV-10` | software unit | exactly one `part_of` link, and every file under `source_files` exists. A unit that lists no file is reported as "designed but not implemented": a `warning` when approved, an `info` before. Listing the files later does not change the unit's content hash, so its approval stays valid | code not written yet; file renamed | SWE.3.BP5, SWE.3.BP8 | SWE.3 | `/sw-detailed-design` for the link, `/sw-unit-implement` for the code | No. The warning for a unit without code is expected between design and implementation |
| `COV-11` | every file under `paths.source_roots` (the item column shows the path) | listed under `source_files` of exactly one software unit | file added without a design; file listed by two units | SWE.3.BP5 | SWE.3 | `/sw-detailed-design` to give the file an owner; `/aspice-start` for the patterns | Yes: the path matches a pattern under `paths.generated` or `paths.third_party` in `project.yaml` |
| `COV-12` | software unit | at least one unit test `verifies` it, and the latest final static analysis run has an entry for it | unit verification not done, or the analysis ran before the unit existed; pending while the unit has no code | SWE.4.BP5 | SWE.4 | `/sw-unit-verify` | Yes: `origin` generated or third-party, with the other verification named in the unit verification plan |
| `COV-13` | software interface | at least one software integration test `verifies` it | integration tests not specified | SWE.5.BP7 | SWE.5 | those responsible for SWE.5 | No |
| `COV-14` | software requirement | with `verification_method: test`: at least one software qualification test `verifies` it; otherwise a final approving review record covers its present content | qualification tests not specified | SWE.6.BP5 | SWE.6 | those responsible for SWE.6; `/review` for the second case | No |
| `COV-15` | system interface | at least one system integration test `verifies` it | integration tests not specified | SYS.4.BP7 | SYS.4 | those responsible for SYS.4 | No |
| `COV-16` | system requirement | with `verification_method: test`: at least one system qualification test `verifies` it; otherwise a final approving review record covers its present content | qualification tests not specified | SYS.5.BP5 | SYS.5 | those responsible for SYS.5; `/review` for the second case | No |
| `COV-17` | test case of a level whose process is in scope | at least one `verifies` link to an item that is not rejected or obsolete | the verified item was withdrawn; test case written without a link | SWE.4.BP5, SWE.5.BP7, SWE.6.BP5, SYS.4.BP7, SYS.5.BP5 | SWE.4, SWE.5, SWE.6, SYS.4, SYS.5 | `/sw-unit-verify` at unit level; otherwise those responsible for the test level | No |
| `COV-18` | test case of a level whose process is in scope | a verdict in the latest final test run of its level | test case added after the last run; no run recorded yet | SWE.4.BP5, SWE.5.BP7, SWE.6.BP5, SYS.4.BP7, SYS.5.BP5 | SWE.4, SWE.5, SWE.6, SYS.4, SYS.5 | `/sw-unit-verify` at unit level; otherwise those responsible for the test level | Yes: recorded in the run as not-run with a `reason` (the engine takes blocked with a reason as well); the schema asks that the test summary accepts the reason |
| `COV-20` | change request from state `analysed` on | at least one `affects` link | impact analysis not carried into links | SUP.10.BP8 | SUP.10 | `/change-request` | No |
| `COV-21` | software interface provided by a component with `origin: developed` | at least one software unit of that component `realizes` it | unit design incomplete; interface realised in the wrong component | SWE.3.BP2, SWE.3.BP5 | SWE.3 | `/sw-detailed-design` | No |
| `COV-22` | software unit with C source files | every function of category public, scheduled or callback is defined in the source files; no function is defined there without a design entry; and wherever the design states types, the parameter types and the return type equal those in the code | code and design drifted apart | SWE.3.BP5, SWE.3.BP8 | SWE.3 | `/sw-unit-implement` when the code is behind, `/sw-detailed-design` when the design is | Yes: `origin` generated or third-party |
| `COV-23` | any item with an `asil` that is not imported | not lower than the ASIL of what it is `derived_from`, `implements` or `verifies`; a unit not lower than its component; a component or interface not lower than a requirement allocated to it | ASIL lowered silently, or not carried along | SWE.2.BP8, SWE.3.BP6 | SWE.2, SWE.3 | the authoring skill of the item | Yes: an approved `design-decision` that documents the decomposition `concerns` the item |
| `COV-24` | architecture view | at least one `shows` link, and nothing shown is rejected or obsolete | view not linked to what it shows; a shown element was withdrawn | SWE.2.BP4, SYS.3.BP4 | SWE.2, SYS.3 | `/sw-architecture` for software-level views | No |
| `COV-25` | the project | at software level an approved view of each kind structure, execution-model and resource-summary, and one of kind state-machine or sequence | architecture not complete or not yet approved | SWE.2.BP1, SWE.2.BP4, SWE.2.BP5 | SWE.2 | `/sw-architecture`, then `/review` | Yes: the kind is listed under `trace.views_not_applicable` in `project.yaml` with the reason |
| `COV-26` | final baseline | at least one final communication record names it as subject | baseline drawn, nobody informed | SYS.2.BP8, SYS.3.BP8, SYS.4.BP9, SYS.5.BP7, SWE.1.BP8, SWE.2.BP9, SWE.3.BP7, SWE.4.BP7, SWE.5.BP9, SWE.6.BP7 | SYS.2, SYS.3, SYS.4, SYS.5, SWE.1 to SWE.6 | `/baseline` | Yes: the baseline's purpose is listed under `trace.internal_baselines` in `project.yaml` |
| `COV-27` | the project | for every process in scope an approved plan of each kind that `plan_kinds` maps to one of its practices | plan not written, or written but not yet approved | SWE.4.BP1, SWE.5.BP1, SWE.5.BP2, SWE.6.BP1, SYS.4.BP1, SYS.4.BP2, SYS.5.BP1, SUP.1.BP1, SUP.8.BP1, SUP.9.BP1, SUP.10.BP1 | SWE.4, SWE.5, SWE.6, SYS.4, SYS.5, SUP.1, SUP.8, SUP.9, SUP.10 | the skill of the process, then `/review`: `/sw-unit-verify` for kind unit-verification, `/baseline` for configuration-management, `/change-request` for change-request-management; for the other kinds those responsible for the process | No |
| `COV-28` | software unit whose ASIL has a target in the approved unit verification plan | the latest final unit test run reports structural coverage of the unit that reaches the target. As `warning` on the plan: it sets no `coverage_targets` at all | coverage not measured in the latest run; tests do not reach all code; pending while the unit has no code | SWE.4.BP2, SWE.4.BP4 | SWE.4 | `/sw-unit-verify` | Yes: `origin` generated or third-party; or a deviation recorded with the coverage entry of the run, with the reason a person accepted |
| `COV-29` | software unit | every designed function of category public, scheduled or callback is named by at least one unit test (`verifies` with `<unit>#<function>`) | test cases link to the unit as a whole; a function was added to the design after the tests; pending while the unit has no code | SWE.4.BP2, SWE.4.BP5 | SWE.4 | `/sw-unit-verify` | Yes: `origin` generated or third-party |
| `COV-30` | software unit and unit test | the unit's source files and the test files of its test cases are unchanged since the latest final unit test run and the latest final static analysis run recorded them. As `warning` on a run: it records no source hashes, so a later change cannot be told | code or test code changed after the run; a run written by an older tool version | SWE.4.BP3, SWE.4.BP4 | SWE.4 | `/sw-unit-verify`: run again and record | No |

## Link roles and the practices behind `SUSPECT` and `CONSISTENCY`

| Link | From | To | Base practices |
|---|---|---|---|
| `derived_from` | system requirement | stakeholder requirement | SYS.2.BP6, SYS.2.BP7 |
| `derived_from` | software requirement | system requirement, system element, system interface | SWE.1.BP6, SWE.1.BP7 |
| `allocated_to` | system requirement | system element, system interface | SYS.3.BP2, SYS.3.BP6, SYS.3.BP7 |
| `allocated_to` | software requirement | software component, software interface | SWE.2.BP2, SWE.2.BP7, SWE.2.BP8 |
| `fulfils` | system element, system interface | system requirement | SYS.3.BP2, SYS.3.BP6, SYS.3.BP7 |
| `fulfils` | software component, software interface | software requirement | SWE.2.BP2, SWE.2.BP7, SWE.2.BP8 |
| `part_of` | software component | software component | SWE.2.BP1 |
| `part_of` | software unit | software component | SWE.3.BP5, SWE.3.BP6 |
| `refines` | component design | software component | SWE.3.BP5, SWE.3.BP6 |
| `realizes` | software interface | system interface | SWE.2.BP3 |
| `realizes` | software unit | software interface | SWE.3.BP2, SWE.3.BP5 |
| `uses` | software unit | software interface, software unit | SWE.3.BP2 |
| `implements` | software unit | software requirement | SWE.3.BP5, SWE.3.BP6 |
| `shows` | architecture view | system element, system interface, software component, software interface | SYS.3.BP4, SWE.2.BP4 |
| `verifies` | unit test | software unit | SWE.4.BP5, SWE.4.BP6 |
| `verifies` | software integration test | software component, software interface, architecture view | SWE.5.BP7, SWE.5.BP8 |
| `verifies` | software qualification test | software requirement | SWE.6.BP5, SWE.6.BP6 |
| `verifies` | system integration test | system element, system interface, architecture view | SYS.4.BP7, SYS.4.BP8 |
| `verifies` | system qualification test | system requirement | SYS.5.BP5, SYS.5.BP6 |
| `concerns` | design decision | requirements, elements, interfaces, views, component designs, units | SYS.3.BP5, SWE.2.BP6, SWE.3.BP4 |
| `affects` | change request, problem report | any item | SUP.10.BP8, SUP.9.BP4 |
| `resolves` | change request | problem report | SUP.10.BP8 |

`allocated_to` and `fulfils` state the same allocation from the two ends. Architecture
work uses `fulfils`, so that allocating does not change a requirement that is already
approved or imported.

## What no rule checks

- Whether the content is right. A link can exist between two items that contradict
  each other; that is what reviews are for.
- Base practices for which the schema has no item type, link or rule. `/process-gate`
  lists them as NOT ASSESSED by the toolkit.
- Anything that lives outside the repository: schedules, meetings, tools of other teams.
