# Software architecture review checklist

Version 1. Applies to: `software-component`, `software-interface`, `architecture-view`
of level `software`, and `design-decision` of level `software`. Supports: SWE.2.BP1,
SWE.2.BP2, SWE.2.BP3, SWE.2.BP4, SWE.2.BP5, SWE.2.BP6, SWE.2.BP7, SWE.2.BP8.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

Review a component together with its interfaces and the views that show it.
`python tools/traceability.py hash --upstream <ID>...` lists subjects and references;
the requirements an element names under `fulfils` are among the references. Where the
allocation is stated on a requirement instead (`allocated_to`), the element does not
name it; read those requirements all the same.
`python tools/traceability.py show <ID>` lists what is allocated to an element,
whichever side states it, and the interfaces a component provides and uses.
`check` means `python tools/traceability.py check --all`.

## Each component

| ID | Check | How to check | Kind |
|---|---|---|---|
| ARC-01 | Mandatory attributes and sections for its state are present, values are allowed, `supplier` is given for a supplied or reused component | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| ARC-02 | A requirement is allocated to it or to one of its parts (`fulfils` on the element or `allocated_to` on the requirement), or it is supplied or generated and `Purpose` says why it is present | `check`: no `COV-08` finding | script |
| ARC-03 | Its ASIL is not lower than that of any requirement allocated to it, or an approved decision documents the decomposition | `check`: no `COV-23` finding | script |
| ARC-04 | `Purpose` says why the component exists as an element of its own and does not only repeat the title | read the section | semantic |
| ARC-05 | `Responsibility` says what the component does and what it does not do, and covers every requirement allocated to it | read the section against the requirements listed by `show <ID>` | semantic |
| ARC-06 | The component has one coherent duty; nothing in it belongs to a neighbour, and no neighbour holds part of its duty | read `Responsibility` of the component and of its neighbours | semantic |
| ARC-07 | `kind`, `layer` and `origin` fit the content and each other; a composition has parts and no behaviour of its own; a complex driver states why the standard path does not serve | read attributes, `Purpose`, and the `part_of` table of `matrix` | semantic |
| ARC-08 | `Dynamic behavior` gives activation, own states, the state after initialisation and the timing objective, and agrees with the execution model view | compare the section with the `tasks` row of the component's entries | semantic |
| ARC-09 | `resource_budget` has objectives for the resources that matter, their origin is recognisable, and `wcet_us` equals the timing objective in the text; or `not_relevant` names who budgets the component instead | read attribute and section | semantic |
| ARC-10 | `supplier` names source, version and form of delivery, and for a component with safety requirements the ASIL it was developed to | read the attribute | semantic |
| ARC-11 | A reused or supplied component that carries safety requirements is fit for them: the evidence named in `supplier` exists and was accepted | ask who accepted it, and on which evidence | accountable |
| ARC-12 | `model`, where set, names an existing component description, and the item contradicts it in no name of a port, interface or runnable | open the file and compare; no tool does | semantic |
| ARC-13 | `execution_context` agrees with the execution model and with the partitioning argument for elements of different ASIL | compare with the views and the decision that concern the component | semantic |

## Each interface

| ID | Check | How to check | Kind |
|---|---|---|---|
| ARC-20 | Mandatory attributes and sections for its state are present; `elements` or `operations` exist as its `kind` requires, with the mandatory keys | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| ARC-21 | `provided_by` and every entry of `used_by` name a software component; `realizes` names a system interface; no link points to a rejected or obsolete item | `check`: no `LINK` finding on the item | script |
| ARC-22 | Its ASIL is not lower than that of any requirement allocated to it | `check`: no `COV-23` finding | script |
| ARC-23 | Its ASIL is not lower than the most critical function that depends on it; a lower value is argued in `Description` or in a decision | compare with `asil` of the components in `used_by` and their requirements | semantic |
| ARC-24 | Every data element has type and direction; a physical quantity has unit, range and resolution; a coded value has the meaning of every code | read `elements` | semantic |
| ARC-25 | Every data element has an initial value, an invalid value or the statement that there is none, an update period or event, and a time-out where data can be lost | read `elements` and `Description` | semantic |
| ARC-26 | Every operation has its arguments with direction, type and range, every distinguishable return value with its meaning, call context, re-entrancy and blocking behaviour | read `operations` | semantic |
| ARC-27 | `Description` states what a user may rely on, what the provider does without a valid value or with an invalid argument, and what each user does with an invalid value, a time-out or a failed call | read the section | semantic |
| ARC-28 | Constraints on use are stated: who may call or read, from which task or interrupt, after which initialisation, how often | read the section | semantic |
| ARC-29 | Provider and user could be implemented by people who never talk to each other, and an integration test could be derived from the item alone | read the item as an implementer of each side | semantic |
| ARC-30 | An interface that carries the software side of a system interface has a `realizes` link, and its ranges, units and timing agree with that system interface | `realizes` table of `matrix`; read both items | semantic |
| ARC-31 | Values that also appear in requirements (ranges, times, thresholds) are the same here | compare with the requirements of provider and users | semantic |
| ARC-32 | Once the detailed design exists: a unit of the providing component realizes the interface | `check`: no `COV-21` finding | script |

## Each view

| ID | Check | How to check | Kind |
|---|---|---|---|
| ARC-40 | `level`, `kind` and `Description` are present; `Diagram` or `table` exists as the kind requires, with the mandatory keys of its rows | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| ARC-41 | It shows at least one item, and no shown item is rejected or obsolete | `check`: no `COV-24` finding | script |
| ARC-42 | Every element with an ID in the diagram or table is named in `shows` under the name its item has, and everything in `shows` appears in the view | compare diagram, table and `show <ID>` | semantic |
| ARC-43 | Description and diagram agree, and the description says what to read from the view | read both | semantic |
| ARC-44 | Structure: every component of the level is present with origin and ASIL; every connection is an interface item; provider and users in the picture equal `provided_by` and `used_by`; the meaning of an arrow is stated | compare with the component and interface items | semantic |
| ARC-45 | State machine: an initial state exists; every transition has a trigger or condition in words; every state can be left or is deliberately final; what the components do in each state is stated | read diagram and state table | semantic |
| ARC-46 | Sequence: the scenario and its starting condition are stated; participants are components; messages are operations or elements of interface items; the task cycle or interrupt of each part is visible | read diagram against the interface items | semantic |
| ARC-47 | Sequence with a timing requirement: the time spent per step adds up to no more than the requirement allows, and the requirement is named | recompute the time table | semantic |
| ARC-48 | The failure side is described: what happens when a step fails, an input is invalid or a time runs out; or the view says why this cannot happen | read description and diagram | semantic |
| ARC-49 | Execution model: every entry function of every component is in exactly one row; every periodic row has a period; every row has a budget and a stack size | compare `table` with `Dynamic behavior` of the components | semantic |
| ARC-50 | Execution model: priority convention, order of entries, preemption, protection of shared data and the worst delay of time-critical rows are explained | read `Description` | semantic |
| ARC-51 | Resource summary: every objective is the sum of the component budgets, with the sum written out; every objective is at most capacity less reserve; every capacity has a source | recompute from `resource_budget` of the components | semantic |
| ARC-52 | `measured` values, where present, come from a named map file or measurement of a named software version | ask who measured, what and when | accountable |

## Each design decision

| ID | Check | How to check | Kind |
|---|---|---|---|
| ARC-60 | `level` and the sections for its state are present | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| ARC-61 | It concerns at least one existing component, interface or view; a decomposition also concerns every requirement whose ASIL is lowered | `check`: no `LINK` finding; `show <ID>` lists the `concerns` targets | script |
| ARC-62 | The context states the question and what forces it, with the IDs of the requirements or system items | read `Context` | semantic |
| ARC-63 | The criteria can be decided for each alternative, come from requirements or named project goals, and carry a weight or rank | read `Evaluation criteria` | semantic |
| ARC-64 | At least two alternatives that could really have been chosen are described, and each is assessed against each criterion with a reason | read `Alternatives` | semantic |
| ARC-65 | The decision follows from the assessment; consequences name what the choice costs, what others have to do, and assumptions someone has to confirm | read `Decision` and `Consequences` | semantic |
| ARC-66 | Each consequence is reflected in the items the decision concerns | read those items | semantic |
| ARC-67 | The decision was taken by the people entitled to take it; for an ASIL decomposition or a coexistence argument, by those responsible for functional safety | ask who decided, and when | accountable |

## The architecture as a set

| ID | Check | How to check | Kind |
|---|---|---|---|
| ARC-70 | Every software requirement is allocated to a component or interface, or is a constraint with a rationale | `check`: no `COV-07` finding; the `allocated_to` and `fulfils` tables of `matrix` | script |
| ARC-71 | A view of each of the kinds `structure`, `execution-model` and `resource-summary` and at least one of kind `state-machine` or `sequence` exists, or the kind is declared not applicable with a reason | `check`: `COV-25` names the kinds without an approved view; each named kind is among the views under review | script |
| ARC-72 | No item under review has a stale approval, a suspect link or missing consistency evidence | `check`: no `COV-19`, `SUSPECT` or `CONSISTENCY` finding | script |
| ARC-73 | Each requirement is allocated to the element that can fulfil it; where several share one, each share is named; no allocation is stated on both sides | read each requirement with its elements (`show <requirement ID>`) | semantic |
| ARC-74 | Non-functional requirements (timing, resources, safety, robustness, diagnosability) are answered by a mechanism that can be pointed to in a component, interface or view | walk the non-functional requirements against the items | semantic |
| ARC-75 | The hierarchy is a tree: every component is part of at most one composition, no composition contains itself, and every component appears in a structure view | `part_of` and `shows` tables of `matrix` | semantic |
| ARC-76 | No component exchanges data with another outside an interface item; every interface has a provider and at least one user | compare `Responsibility` texts and views with `provided_by` and `used_by` | semantic |
| ARC-77 | Supplied, reused and basic software are present as components and take part in interfaces, execution model and budgets | compare the component list with what is built into the software | semantic |
| ARC-78 | Operating modes, start-up, shut-down, error handling and every timing requirement are covered by a view or a component section, or are left out with a stated reason | walk the list against views and `Dynamic behavior` sections | semantic |
| ARC-79 | The numbers agree across items: composition and parts, task budgets and entry objectives, processor load and task budgets, summary and component budgets | recompute; differences are explained in a view | semantic |
| ARC-80 | Where elements of different ASIL coexist, it is stated for memory, timing and exchanged data what keeps the lower from disturbing the higher; otherwise all are at the highest ASIL | read structure view, `execution_context` and the decision | semantic |
| ARC-81 | One term, one name and one value for one thing in all components, interfaces and views | read the items side by side | semantic |
| ARC-82 | Every choice that shaped the structure has a decision item, including the adoption of a given platform or architecture | ask which alternatives were discussed; compare with the decisions | semantic |
| ARC-83 | The architecture can be built on the target with the given team and time, and the developers who build on it agree | ask who was consulted, and when | accountable |
| ARC-84 | Capacities and reserves are the ones agreed with the owner of the hardware | ask who agreed, and when | accountable |
| ARC-85 | Where safety requirements are allocated: the analyses the safety plan asks for at architecture level exist, and their results are reflected in requirements and elements | ask the person responsible for functional safety | accountable |
| ARC-86 | Open queries to requirement authors, suppliers and the customer are recorded, and none of them invalidates an item under review | ask the author | accountable |
