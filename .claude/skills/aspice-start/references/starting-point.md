# Deriving the starting point

Step 10 turns the answers into four things: where engineering starts, what has to be
registered at the boundary, which plans the scope needs, and in which order to work.
Everything here follows from `scope.processes` and `inputs`; nothing is assumed.

## 1. The first process, and every other boundary

Engineering runs down the left side of the V and up the right side:

`SYS.1, SYS.2, SYS.3, SWE.1, SWE.2, SWE.3, SWE.4, SWE.5, SWE.6, SYS.4, SYS.5`

The first process of this row that is in scope is where the team starts. It is not
the only boundary: every process in scope whose reference comes from a process out of
scope has one. A test process whose requirements or design process is out of scope is
the common case (a test package without the specification work).

## 2. Inputs each boundary needs

For each process in scope, look at the processes in the second column. If at least
one of them is out of scope, the process needs the input of the third column from
outside.

| Process in scope | Its reference is produced by | Needs from outside (`level` in `inputs`) | `/import-inputs` registers it as |
|---|---|---|---|
| SYS.1 | the customer and other stakeholders | `stakeholder requirements`: the documents as delivered | `stakeholder-requirement` (the team's own items) |
| SYS.2 | SYS.1 | `stakeholder requirements`, agreed | `stakeholder-requirement` |
| SYS.3 | SYS.2 | `system requirements` | `system-requirement` |
| SWE.1 | SYS.2, SYS.3 | `system requirements` and `system architecture` with the hardware-software interface; for a software-only delivery, the requirements on the software as a whole | `system-requirement`, `system-element`, `system-interface` |
| SWE.2 | SWE.1 | `software requirements` | `software-requirement` |
| SWE.3 | SWE.2 | `software architecture`: components, interfaces, behaviour; `software requirements` where units implement them directly | `software-component`, `software-interface`, `architecture-view`, `software-requirement` |
| SWE.4 | SWE.3 | `detailed design` and `code` | `component-design`, `software-unit` |
| SWE.5 | SWE.2, SWE.3 | `software architecture`, and the units to integrate | `software-component`, `software-interface`, `architecture-view` |
| SWE.6 | SWE.1 | `software requirements` | `software-requirement` |
| SYS.4 | SYS.3 | `system architecture`, and the items to integrate | `system-element`, `system-interface`, `architecture-view` |
| SYS.5 | SYS.2 | `system requirements` | `system-requirement` |

Compare the needs with what step 2 recorded and sort every case into one of three:

- Needed and received: to be registered with `/import-inputs`, then accepted through
  an input acceptance review recorded by `/review`. Work that builds on an input which
  is not accepted inherits that uncertainty.
- Needed and not received: a gap. Name it. The user decides whether to ask the source
  for it or to take the producing process into scope. The skill does neither.
- Received but produced by a process that is in scope (the customer delivers software
  requirements and SWE.1 is in scope): not a contradiction. For the team the delivery
  is the set to analyse, and it is registered one level up. Say so here; the type is
  confirmed in `/import-inputs`.

Supporting and management processes have no engineering input of this kind. If the
client's configuration, change or problem management is used, those processes are out
of scope and the team's work in them is evidence at the client.

## 3. Plans the scope needs

Read `plan_kinds` in `schema/items.yaml`; this table is its state at the time of
writing. For every process in scope, rule COV-27 expects an approved `plan` item of
each kind listed, and reports each missing one as an error from the first check on.

| Process in scope | Plan kind | Answers |
|---|---|---|
| SWE.4 | `unit-verification` | SWE.4.BP1 |
| SWE.5 | `software-integration` | SWE.5.BP1, SWE.5.BP2 |
| SWE.6 | `software-qualification-test` | SWE.6.BP1 |
| SYS.4 | `system-integration` | SYS.4.BP1, SYS.4.BP2 |
| SYS.5 | `system-qualification-test` | SYS.5.BP1 |
| SUP.1 | `quality-assurance` | SUP.1.BP1 |
| SUP.8 | `configuration-management` | SUP.8.BP1 |
| SUP.9 | `problem-resolution` | SUP.9.BP1 |
| SUP.10 | `change-request-management` | SUP.10.BP1 |

Tell the user which plans that makes, and that a plan is an item like any other: it
is drafted, reviewed and approved through `/review`. The base practice table of the
skill that owns the process says whether that skill drafts the plan; today
`/sw-unit-verify`, `/baseline` and `/change-request` do so for their processes. Where
no skill does, the plan is written by hand with the sections the type `plan` has in
the schema.

## 4. Order of work

Give the order for the processes in scope only, and name the skill for each step.

1. Plans that later steps depend on: the configuration management plan before the
   first baseline, each verification strategy before its test cases are written.
2. Boundary inputs: `/import-inputs`, then `/review` with the checklist
   `input-acceptance`.
3. Left side, top down. Each step is drafted, reviewed, and only then built upon; the
   tools hold to this order and refuse to approve an item above one that is not
   approved:
   SYS.2 and SYS.3 (by hand today), SWE.1 `/sw-requirements`, SWE.2
   `/sw-architecture`, SWE.3 `/sw-detailed-design` and then `/sw-unit-implement`.
4. Right side, bottom up: SWE.4 `/sw-unit-verify`, then SWE.5, SWE.6, SYS.4 and SYS.5
   (by hand today). A test specification can be written as soon as its reference is
   approved: qualification tests from the requirements, integration tests from the
   architecture of the same level.
5. At any time: `/review` for drafts, `/trace-check` for the state of the links,
   `/next-step` for what to do next.
6. When the items of a process are approved: `/process-gate`. At the points agreed in
   the configuration management plan: `/baseline`. Once a baseline exists whose
   purpose is not an internal one, a change to what it contains starts with
   `/change-request`.

Leave out the steps whose process is not in scope, and say for each remaining step
without an authoring skill that the toolkit checks the result but does not draft it.

## 5. Worked example

Answers of the worked example `examples/power-window`: software supplier; received
are a system requirements specification (version 2.1) and a system architecture
description (version 1.4) of a front door module; the team is responsible for SWE.1,
SWE.2, SWE.3, SWE.4 and SUP.8; highest ASIL B.

What step 10 says:

- First process: SWE.1. Its references come from SYS.2 and SYS.3, both out of scope.
  No other process in scope has a boundary: SWE.2, SWE.3 and SWE.4 build on what the
  team itself produces.
- Trace route: the default. Each of the four system requirements is allocated to the
  software element, so each needs a software requirement derived from it (COV-05).
- Boundary inputs, both received: the system requirements (to be registered as
  `system-requirement` items) and the system architecture (as `system-element` and
  `system-interface` items). Next: `/import-inputs` for each document, then the input
  acceptance review.
- Plans: `unit-verification` for SWE.4 and `configuration-management` for SUP.8. The
  first check reports both under COV-27 until they are approved.
- Order: plans; inputs; `/sw-requirements`; `/sw-architecture`;
  `/sw-detailed-design`; `/sw-unit-implement`; `/sw-unit-verify`; reviews after each;
  `/process-gate` per process; `/baseline`.
- Not in scope and therefore not checked: integration of the software, its
  qualification test, change and problem management. If the user had said that an
  assessment will also rate SWE.5 and SWE.6, the hand-over would carry the warning of
  step 4 for both, and `assessment_scope` would list all six software processes and
  SUP.8.
