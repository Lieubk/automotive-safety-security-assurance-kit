# System architecture review checklist

Version 2. Applies to: `system-element`, `system-interface`, `architecture-view` of
level `system`, and `design-decision` of level `system`. Supports: SYS.3.BP1, SYS.3.BP2,
SYS.3.BP3, SYS.3.BP4, SYS.3.BP5, SYS.3.BP6, SYS.3.BP7.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

A check that does not apply to the items under review - a check for another item type
or view kind, or `SYA-32` before system integration tests exist - is recorded as
`not-applicable` with the reason.

The review ends with the verdict of its reviewers. Making the approved architecture
known to those who build on it - hardware, software, mechanics, test, the customer - and
an agreement reached with them, is not a condition of the approval: it follows it and is
recorded with the baseline that carries the architecture (`/baseline`, communication
record; SYS.3.BP8).

Review an element together with its interfaces and the views that show it, after the
system requirements it fulfils are approved. `python tools/traceability.py hash
--upstream <ID>...` lists subjects and references; the requirements an item names under
`fulfils` are among the references. `python tools/traceability.py show <ID>` lists the
requirements an element or interface fulfils. `check` means
`python tools/traceability.py check --all`.

## Each element

| ID | Check | How to check | Kind |
|---|---|---|---|
| SYA-01 | Mandatory attributes and sections for its state are present and values are allowed | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| SYA-02 | It fulfils at least one system requirement | `check`: no `COV-04` finding | script |
| SYA-03 | Its ASIL is not lower than that of any requirement allocated to it, or an approved decision documents the decomposition | `check`: no `COV-23` finding | script |
| SYA-04 | `Responsibility` says what the element does for the system and what it does not do, and covers every requirement allocated to it | read the section against the requirements listed by `show <ID>` | semantic |
| SYA-05 | The element has one coherent duty and one discipline that builds it; nothing in it belongs to a neighbour, and no neighbour holds part of its duty | read `Responsibility` of the element and of its neighbours | semantic |
| SYA-06 | `kind` fits the content: a `software` element is the software of the system and describes no components; a `hardware` or `mechanical` element names no part numbers unless a requirement fixes them; an `external` element states what is assumed of it | read attribute and section | semantic |
| SYA-07 | Resources, budgets and limits given to the element in `Responsibility` come from a requirement or a named source, and no two elements are given the same resource twice | read the sections side by side with the requirements | semantic |
| SYA-08 | `Dynamic behavior` gives modes, start-up, the state after reset, and the timing objective, and agrees with the views that show the element; or states `Not applicable:` with the reason | compare the section with the views | semantic |
| SYA-09 | An element supplied from outside names its source and what the project uses of it | read `Responsibility` | semantic |
| SYA-10 | An element of kind `software` is the one `/sw-requirements` can derive from: the requirements allocated to it are about software, not about hardware or mechanics | read the requirements listed by `show <ID>` | semantic |
| SYA-11 | An `external` element exists because a requirement is allocated to it, and what is assumed of it is agreed with its owner or is an open `query` | read `Responsibility` and `list --type query --status open` | accountable |

## Each interface

| ID | Check | How to check | Kind |
|---|---|---|---|
| SYA-20 | Mandatory attributes and sections for its state are present and values are allowed; `Definition` exists | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| SYA-21 | No link of the item points to a rejected, obsolete or missing item | `check`: no `LINK` finding on the item | script |
| SYA-22 | Its ASIL is not lower than that of any requirement allocated to it | `check`: no `COV-23` finding | script |
| SYA-23 | Its ASIL is not lower than the most critical function that depends on it; a lower value is argued in `Definition` or in a decision | read `Definition` against the elements at its ends and their requirements | semantic |
| SYA-24 | Both end points are named, each an element of the architecture, and the provider is stated | read `Definition` against the element list | semantic |
| SYA-25 | Every property has a value and a unit; a range has its limits; a coded value has the meaning of every code, including reserved ones and "not available"; a physical quantity has a tolerance | read the table | semantic |
| SYA-26 | The two ends agree: what one element declares as output the partner declares as input, with the same type, unit, range and timing | read the interface with the `Responsibility` of both elements; no tool compares | semantic |
| SYA-27 | Timing is stated: cycle or event, latency, tolerance, and what counts as loss | read the table | semantic |
| SYA-28 | What each end does with an invalid value, a loss or a failure is stated, or stated to be left to the requirements of an element | read `Definition` and `Dynamic behavior` | semantic |
| SYA-29 | For `hardware-software`: a software developer could write requirements from the item alone (polarity, ranges, resolution, timing, state after reset, notification) | read it as the developer of the software element | semantic |
| SYA-30 | Values that also appear in requirements (ranges, times, thresholds) are the same here | compare with the requirements the interface fulfils and those of its elements | semantic |
| SYA-31 | A definition kept in another document (a bus description) is named with its version, and the signals this system uses are listed | read `Definition` | semantic |
| SYA-32 | Once system integration tests exist: at least one verifies the interface | `check`: no `COV-15` finding | script |

## Each view

| ID | Check | How to check | Kind |
|---|---|---|---|
| SYA-40 | `level`, `kind` and `Description` are present; `Diagram` or `table` exists as the kind requires, with the mandatory keys of its rows | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| SYA-41 | It shows at least one item, and no shown item is rejected or obsolete | `check`: no `COV-24` finding | script |
| SYA-42 | Every element or interface with an ID in the diagram or table is named in `shows` under the name its item has, and everything in `shows` appears in the view | compare diagram, table and `show <ID>` | semantic |
| SYA-43 | Description and diagram agree, and the description says what to read from the view | read both | semantic |
| SYA-44 | Context: the boundary of the system is clear; every neighbour that exchanges something with the system is shown with the interface that crosses | read diagram against the interface items | semantic |
| SYA-45 | Structure: every element of the architecture is present with its kind; every connection is an interface item; the end points in the picture equal those in `Definition`; the meaning of an arrow is stated | compare with the element and interface items | semantic |
| SYA-46 | State machine: an initial state exists; every transition has a trigger or condition in words; every state can be left or is deliberately final; what the elements do in each state is stated | read diagram and state table | semantic |
| SYA-47 | Sequence: the scenario and its starting condition are stated; participants are elements; messages are interfaces; the time of each step is visible | read diagram against the interface items | semantic |
| SYA-48 | Sequence with a timing requirement: the time spent per step adds up to no more than the requirement allows, and the requirement is named | recompute the time table | semantic |
| SYA-49 | The failure side is described: what happens when a step fails, an input is invalid or a time runs out; or the view says why this cannot happen | read description and diagram | semantic |

## Each design decision

| ID | Check | How to check | Kind |
|---|---|---|---|
| SYA-60 | `level` and the sections for its state are present | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| SYA-61 | It concerns at least one existing element, interface or view; a decomposition also concerns every item whose ASIL is lowered | `check`: no `LINK` finding; `show <ID>` lists the `concerns` targets | script |
| SYA-62 | The context states the question and what forces it, with the IDs of the requirements or other items | read `Context` | semantic |
| SYA-63 | The criteria can be decided for each alternative, come from requirements or named project goals, and carry a weight or rank | read `Evaluation criteria` | semantic |
| SYA-64 | At least two alternatives that could really have been chosen are described, and each is assessed against each criterion with a reason | read `Alternatives` | semantic |
| SYA-65 | The decision follows from the assessment; consequences name what the choice costs, what others have to do, and assumptions someone has to confirm | read `Decision` and `Consequences` | semantic |
| SYA-66 | Each consequence is reflected in the items the decision concerns | read those items | semantic |
| SYA-67 | The assessment of cost, supply, feasibility and robustness of hardware and mechanical alternatives comes from people who know them | ask who judged, and on which basis; the note names them | accountable |
| SYA-68 | The decision was taken by the people entitled to take it; for an ASIL decomposition or a coexistence argument, by those responsible for functional safety | ask who decided, and when | accountable |

## The architecture as a set

| ID | Check | How to check | Kind |
|---|---|---|---|
| SYA-70 | Every system requirement is fulfilled by an element or interface, or is a constraint with a rationale | `check`: no `COV-03` finding; the `fulfils` tables of `matrix` | script |
| SYA-71 | The views cover what the requirements make necessary: the context and structure of the system, and the main functions and operating modes over time; or the omission has a stated reason | walk the requirements against the views; this is guidance, the engine checks no view kinds at system level | semantic |
| SYA-72 | No item under review has a stale approval, a suspect link, missing consistency evidence, or a link to an item that is still in draft or in review and not a subject of this review | `check`: no `COV-19`, `SUSPECT`, `CONSISTENCY` or `UPSTREAM` finding; `python tools/traceability.py list --status draft` and `--status in-review` name none of the references | script |
| SYA-73 | Each requirement is allocated to the element that can fulfil it; where several share one, each share is named | read each requirement with its elements (`show <requirement ID>`) | semantic |
| SYA-74 | Non-functional requirements (timing, safety, security, resources, robustness, diagnosability) are answered by a mechanism that can be pointed to in an element, interface or view | walk the non-functional requirements against the items | semantic |
| SYA-75 | The architecture neither contradicts nor omits what the requirements demand; no requirement is weakened by its allocation | read requirements and elements side by side | semantic |
| SYA-76 | No two elements exchange anything outside an interface item; every interface has two end points that are elements | compare `Responsibility` texts and views with the interface items | semantic |
| SYA-77 | Operating modes, start-up, shut-down, failure reactions and every timing requirement are covered by a view or an element section, or are left out with a stated reason | walk the list against views and `Dynamic behavior` sections | semantic |
| SYA-78 | The numbers agree across items: time chains add up over the elements, resources given to elements do not exceed what the hardware offers | recompute; differences are explained in a view | semantic |
| SYA-79 | Where elements of different ASIL coexist, it is stated what keeps the lower from disturbing the higher; otherwise all are at the highest ASIL | read structure view and the decision | semantic |
| SYA-80 | One term, one name and one value for one thing in all elements, interfaces and views | read the items side by side | semantic |
| SYA-81 | Every choice that shaped the system has a decision item, including the adoption of a given platform or architecture | ask which alternatives were discussed; compare with the decisions | semantic |
| SYA-82 | The elements allocated software can be handed to software development: each requirement allocated to a `software` element is one that software requirements can be derived from | read the allocation; later `COV-05` shows the derivation | semantic |
| SYA-83 | The architecture can be built with the available disciplines, suppliers, cost and time | ask the system lead and the leads of hardware, software and mechanics (`people` in `project.yaml`); the note names who states it. Where a discipline has no lead in the project, the person who speaks for it is named; `not-assessed` only while nobody can be named | accountable |
| SYA-84 | Where safety requirements are allocated: the safety analyses that are due at system architecture level by now exist, and their results are reflected in requirements and elements | ask the person responsible for functional safety which analyses are due at this point and whether they exist. `not-applicable` only when no subject carries an ASIL. Where nobody holds that role, the check cannot be answered: `not-assessed`. Without an allocated safety requirement (no ASIL above QM in the architecture) the check is `not-applicable` with that reason; with one and no person responsible for functional safety named in `project.yaml`, the finding is that the role is missing | accountable |
| SYA-85 | Open questions to the source of an input are `query` items, and no open one invalidates an item under review | `python tools/traceability.py list --type query --status open`; go through each with the author | accountable |
