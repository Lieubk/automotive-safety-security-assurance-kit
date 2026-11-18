---
name: sw-detailed-design
description: "Develop the detailed design of software components from an approved software architecture: one component design per developed component and its software units with function contracts, data, behaviour and trace links (Automotive SPICE SWE.3, BP1 to BP7). Use when a developed component has no detailed design, when a design is to be extended or reworked, or when the trace check reports COV-09 or COV-21."
argument-hint: "[component or unit IDs, or nothing to work on every developed component without a complete design]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---

# Software detailed design (SWE.3.BP1 to BP7)

Turns an approved software architecture into a detailed design that a developer can
implement without taking design decisions of their own and a tester can derive unit
tests from. The result is one `component-design` item per developed component and its
`software-unit` items, in state `draft`, ready for `/review`. No code is written here.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SWE.3.BP1 Develop software detailed design | splits each developed component into units; writes the design concept, the static structure, and purpose, behaviour and error handling of every unit | `component-design` and `software-unit` items |
| SWE.3.BP2 Define interfaces of software units | writes a contract per function and an entry per variable; names the interfaces each unit realizes and uses | `functions`, `data`, `platform`; `realizes` and `uses` links |
| SWE.3.BP3 Describe dynamic behavior | describes how the units work together and the states, contexts and timing of each unit, or says why there is nothing to describe | `Dynamic behavior` sections; `trigger`, `period_ms`, `call_context`, `reentrant`, `protection` |
| SWE.3.BP4 Evaluate software detailed design | assesses the design against the criteria the project uses; records risks with owners and decisions between alternatives | `Design evaluation` section; `design-decision` items of level `detailed-design` |
| SWE.3.BP5 Establish bidirectional traceability | sets `refines`, `part_of`, `realizes`, `uses` and `implements`; names the files each unit will consist of | links; `matrix` output |
| SWE.3.BP6 Ensure consistency | self-checks against the checklist; the evidence itself comes from `/review` | proposed findings; review record written by `/review` |
| SWE.3.BP7 Communicate agreed software detailed design | not done here: `/baseline` records the baseline and who was informed | - |
| SWE.3.BP8 Develop software units | not done here: `/sw-unit-implement` writes the code of approved units | - |

## Before you start

1. If there is no `project.yaml`, stop: "This project has no scope yet. Run
   `/aspice-start` first."
2. If `SWE.3` is not in `scope.processes`, stop: "SWE.3 is out of scope for this project.
   A detailed design delivered from outside is registered with `/import-inputs`."
3. Run `python tools/traceability.py status` and `python tools/traceability.py check --all`.
4. The inputs are the `software-component` to be designed, the `software-interface`
   items it provides and uses, the `software-requirement` items allocated to it and the
   software-level `architecture-view` items that show it: approved, or imported and
   covered by an input acceptance review. If one is missing or not approved, stop and
   name it and its skill: `/sw-architecture` for components, interfaces and views,
   `/sw-requirements` for requirements, `/import-inputs` for delivered inputs.
5. If the check reports `COV-19` or `SUSPECT` on an input you are about to use, say so
   before continuing: a design built on such an input inherits that uncertainty.

## Steps

### 1. Decide what to design
- With arguments: the named components or units. Without: every `COV-09` finding (a
  developed component without design or units), every `COV-21` finding (a provided
  interface no unit realizes), plus the design items still in draft
  (`python tools/traceability.py list --status draft` shows them with their type).
- Design only components with `origin: developed` and a `kind` other than
  `composition`. A `reused` or `supplied` component is not redesigned and gets no
  design item: its design belongs to its source. Changing such a component is a change
  of the architecture item first. Details: `references/designing-units.md`, first section.
- Tell the user the list and ask whether it is the right scope for this session.

### 2. Read the frame the architecture sets
- Run `python tools/traceability.py show <CMP-ID>`: it lists the requirements
  allocated to the component (`allocated_to` or `fulfils`), the interfaces it provides
  and uses, the views and the decisions. Read these items by ID.
- Note what binds the design: `asil`, `execution_context`, `resource_budget`, `model`,
  tasks and call order of the execution model, ranges and error behaviour of the
  interfaces, and what `project.yaml` says under `platform` and `safety`.
- Collect what is missing or contradictory as **queries** to the owner of architecture
  or requirements; do not repair the architecture inside the design. Ask which queries
  the user can answer now. For the rest ask: wait, or go on with an assumption that is
  written into `Design concept` with its owner.

### 3. Design concept and units
- Read `references/designing-units.md` before drafting. Propose the design concept and
  the split into units, each with its reason, and the alternatives you considered. The
  user decides. A choice between real alternatives becomes a `design-decision` (step 8).
- Assign every allocated requirement and every provided interface to a unit.
- Per unit set `asil` (not lower than the component or any requirement it implements;
  a lower value is a decomposition and needs an approved `design-decision`),
  `security_relevant` and `origin`. Name its files by the project's naming convention
  in `Static structure`. `source_files` lists only files that exist: leave it out for
  a unit without code; `/sw-unit-implement` adds it.

### 4. Function contracts and data
- Write `functions`: a complete contract for every function of category `public`,
  `scheduled` or `callback`; name, arguments and return values for every `local`
  function the behaviour description relies on. Write `data` for every variable that
  keeps its value between calls. Rules per key: `references/designing-units.md`.
- State the `type` of every argument and the return type as they will stand in C:
  `COV-22` later compares them with the code.
- Where an interface item fixes an operation, take its name and arguments unchanged.
- AUTOSAR Classic: read `references/autosar-classic.md`. Runnables go into `functions`,
  platform resources into `platform`; the component description stays the source.

### 5. Behaviour and error handling
- Write `Purpose`, `Behavior` and `Error handling` of every unit. Apply both tests of
  `references/designing-units.md` ("How much detail") to every function: no decision
  left to the developer, and expected results derivable for every input class.
- Describe decisions and intent, not statements: text that could only be written by
  reading code is too detailed.

### 6. Dynamic behaviour
- Component design: start-up order, one cycle of every periodic path, every event
  path, what is shared between contexts and how it is protected, one failure path.
  Unit: states and transitions, execution contexts, preemption, timing.
- `Not applicable:` with the reason is correct only where the item itself shows that
  there is nothing to describe. The conditions are in `references/designing-units.md`.

### 7. Trace
- `component-design`: `refines` the component. `software-unit`: exactly one `part_of`;
  `realizes` for every provided interface it serves; `uses` for every interface and
  unit it depends on at run time; `implements` for the requirements it fulfils.
- Check each link in both directions: the unit really does what the target asks, and
  the units together cover the component's requirements and interfaces.

### 8. Evaluate the design
- Read `references/design-evaluation.md`. Ask where the project's evaluation criteria
  and limits are written. If nowhere, propose them and let the user decide.
- Write `Design evaluation` in the component design: the criteria, a result per
  criterion that is specific to this component, and every risk with effect, measure
  and owner. Owners and acceptances are stated by the user, never invented.
- A negative result ends in a design change, a risk with an owner, or an acceptance.
  Draft a `design-decision` with `level: detailed-design` for each choice between
  alternatives; the user takes the decision.

### 9. Self-check
Apply `.claude/docs/checklists/software-detailed-design.md` to the drafts. Show the
findings to the user as proposals, grouped by item, and correct what they accept.

## Writing

- Show a table of the drafts (ID, type, title, ASIL, component, files, requirements) and
  ask: "May I write these N design items to `spec/software/design/`?" Decisions go to
  `spec/decisions/`.
- IDs: `python tools/record.py next-id component-design`, `next-id software-unit` and
  `next-id design-decision`, then count upwards.
- File layout: `references/item-templates.md`. Status `draft`.
- When changing an approved item, say first that its approval becomes stale, that code
  and tests built on it become suspect, and that `python tools/traceability.py impact <ID>`
  lists them. Inside a baseline whose purpose is not internal the change needs an
  approved change request first (`/change-request`).

## Checks before you finish

Run `python tools/traceability.py check --all`.
- `FORMAT`, `SCHEMA` and `LINK` findings on items written in this session: fix them. For
  each draft the check lists what is "still to come before review": add it now.
- `COV-09`, `COV-21`, `COV-23` for the components in scope should be gone; report what remains.
- Expected for a unit without code, and warnings once it is approved: `COV-10`
  "designed but not implemented" until `/sw-unit-implement` has run, and `COV-12`,
  `COV-28`, `COV-29` marked "pending: the unit has no code yet". They do not stand in
  the way of a design baseline. Say so.
- Run `python tools/traceability.py matrix`; quote its `part_of`, `realizes`, `implements` tables.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. Queries for the owners of architecture and requirements, numbered, each with the
   item ID; assumptions the design rests on, each with its owner.
3. Risks from the evaluation that have no owner or no decided measure yet.
4. The remaining findings of the check that concern these items.
5. Next: `/review` for the design items and decisions; `/baseline` to record the agreed
   design and who was informed; `/sw-unit-implement` for the approved units, and
   `/sw-unit-verify` to derive test cases from the approved design: every designed
   function of category public, scheduled or callback needs a test that names it.

## Do not

- Do not set `status` to anything but `draft`, and do not write a review record.
- Do not design reused, supplied or composition components, and do not edit imported items.
- Do not write or change code; a design written after its code says so in `Design notes`.
- Do not change a component, an interface or a requirement to fit the design: query its owner.
- Do not let the design become a second source for names the component description
  defines, and do not invent complexity figures, risk owners or acceptances.
