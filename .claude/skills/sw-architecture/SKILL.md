---
name: sw-architecture
description: "Design the software architecture from approved software requirements (Automotive SPICE SWE.2): components, interfaces, dynamic and resource views, design decisions, and the allocation of every requirement. Use when an architecture is to be created, extended or reworked, or when the trace check reports requirements without allocation (COV-07), components without requirements (COV-08) or missing architecture views (COV-25)."
argument-hint: "[software requirement IDs, a component or feature name, or nothing to work on all open allocation and view findings]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---

# Software architectural design (SWE.2)

Turns approved software requirements into an architecture expressed as items: components
in a hierarchy, interfaces precise enough to implement and integrate against, views of
structure, behaviour, execution and resources, and decisions with their alternatives.
Every requirement is allocated. All items are written in state `draft`, ready for `/review`.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SWE.2.BP1 Develop software architectural design | decomposes the software into components over as many levels as needed, each with its reason | `software-component` items with `part_of`, `kind`, `layer`, `origin`; an `architecture-view` of kind `structure` |
| SWE.2.BP2 Allocate software requirements | assigns every requirement to the element responsible and checks the result in both directions | `fulfils` links on the `software-component` and `software-interface` items |
| SWE.2.BP3 Define interfaces of software elements | defines each interface with structured data elements or operations, provider, users and error behaviour | `software-interface` items; `realizes` links to `system-interface` items |
| SWE.2.BP4 Describe dynamic behavior | describes modes, start-up, shut-down, error handling, timing chains, tasks and interrupts | `Dynamic behavior` sections; views of kind `state-machine`, `sequence`, `execution-model` |
| SWE.2.BP5 Define resource consumption objectives | sets budgets per component and totals for the ECU that add up | `resource_budget`; a view of kind `resource-summary` |
| SWE.2.BP6 Evaluate alternative software architectures | fixes criteria first and assesses alternatives against them; the user decides | `design-decision` items with `concerns` links |
| SWE.2.BP7 Establish bidirectional traceability | sets `fulfils`, `realizes`, `shows`, `concerns` and `part_of` links | links; `matrix` output |
| SWE.2.BP8 Ensure consistency | self-checks against the checklist; the evidence itself comes from `/review` | proposed findings; review record written by `/review` |
| SWE.2.BP9 Communicate agreed software architectural design | not done here: `/baseline` records the baseline and who was informed | - |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. `SWE.2` not in `scope.processes`: stop. "SWE.2 is out of scope for this project. An
   architecture delivered from outside is registered with `/import-inputs`."
3. Run `python tools/traceability.py status` and `python tools/traceability.py check --all`
   (every command takes `--project <dir>` when the project is not the current directory).
4. The inputs are `software-requirement` items, approved or imported with an input
   acceptance review. If there are none, stop and name `/sw-requirements` or
   `/import-inputs`.
5. A requirement in `draft` or `in-review`, or with a `COV-19` finding, is not settled.
   Name each one and ask: wait, or design against it at risk. Elements that fulfil it
   stay in `draft` until it is approved: the check reports `UPSTREAM`, and the review
   refuses to approve an item above one that is not approved.
6. `SUSPECT` on an existing element means that a requirement it fulfils changed after
   its review: read the new version first. An open `QUERY` on an input means a question
   to its source is unanswered: read the query before designing on that input.

## Steps

### 1. Decide what to cover
- With arguments: the named requirements, component or feature. Without: every `COV-07`
  (requirement not allocated), `COV-08` (component without a requirement) and `COV-25`
  (required view kind missing) finding, plus existing draft architecture items.
- Run `python tools/traceability.py matrix`; its `fulfils`, `part_of`, `realizes` and
  `shows` tables show what exists. For the IDs of one type run
  `python tools/traceability.py list --type software-component`. Ask the user whether the
  list is the right scope.

### 2. Find what shapes the architecture
- Read the requirements in scope by ID. List those that constrain structure, interfaces,
  timing, resources, safety or reuse, and add the project goals the user names.
- Propose evaluation criteria from this list and ask the user to rank them before any
  structure is drawn. Every `design-decision` uses them (step 8).
- A question the user cannot answer is not design input. About an imported item it
  becomes a `query` item (`python tools/record.py next-id query`; folder
  `records/queries`; `to`, `asked_at`, a `Question` section, `about` linking the item).
  About a requirement the project wrote, it goes back to `/sw-requirements`.

### 3. Decompose
- Read `references/architecture-guidance.md` first. Propose the components, each with
  the reason it is an element of its own. `part_of` gives the hierarchy; a `composition`
  has parts and no behaviour of its own. Units belong to `/sw-detailed-design`.
- Per component set `kind`, `layer`, `origin` and `execution_context`; write `Purpose`
  (why it exists) and `Responsibility` (what it does, and what it does not do).
- Supplied, reused and basic software are component items too, with `supplier` (source,
  version, form of delivery, ASIL developed to) and a `Purpose` saying why they are
  present. They take part in interfaces, execution model and budgets like the rest.

### 4. AUTOSAR Classic
- `kind` and `layer` follow the layered architecture; the mapping is in the guidance.
- Where a component description file exists, set `model` to its path and read ports,
  port interfaces and runnables from it. Never retype them into the component item or
  invent a name: the model stays the source, and what it lacks is a change to the model.
- No tool compares model and items: report that comparison as `NOT ASSESSED`.

### 5. Define the interfaces
- One `software-interface` per exchange between components, with one `provided_by` and
  all `used_by`. `kind` decides whether `elements` or `operations` are filled;
  `references/interface-template.md` lists what a complete definition holds.
- `Description`: what a user may rely on, what each side does in an error case,
  constraints on use. Set `realizes` where the interface carries the software side of a
  `system-interface`, and compare ranges and timing with that item.

### 6. Describe the dynamic behaviour
- A component's own modes, activation and state after initialisation go into its
  `Dynamic behavior` section; behaviour across components goes into views.
- Cover the operating modes of the ECU, start-up, shut-down, error handling and every
  chain with a timing requirement: a view for each, or the reason why none is needed.
  `references/view-templates.md` says what each view kind must show. Every view links
  with `shows` to every item that appears in it.

### 7. Execution model and resource budgets
- One view of kind `execution-model`: a `tasks` row per task and interrupt, every entry
  function of every component in exactly one row, in calling order. `Description` gives
  priorities, preemption, protection of shared data and the resulting processor load.
- Give every component a `resource_budget`, or `not_relevant` with the reason, and say
  where each number comes from. Ask the user for capacities and the reserve to keep.
- One view of kind `resource-summary` with a `resource-totals` row per resource. No tool
  adds the numbers: show the user the sums before writing - parts to composition, entries
  to task budget, tasks to processor load, objective against capacity less reserve.

### 8. Alternatives
- For each choice that shapes the structure (the decomposition or the adoption of a
  given one, task model, make or reuse, partitioning) draft a `design-decision`: context,
  the criteria of step 2, at least two real alternatives, each assessed against each one.
- Present the assessment and ask the user to decide. `Decision` and `Consequences` record
  what the user decided; an undecided draft is listed as open in the hand-over.

### 9. Allocate
- Per requirement choose the responsible component, or for `kind: interface` the
  interface, and record it as `fulfils` on that element. Requirements are not edited.
- Check both directions with `python tools/traceability.py show <ID>`: `Responsibility`
  covers every requirement of the element, and every element has a requirement or a
  recorded reason (`COV-08`).
- A need that only the design creates goes to `/sw-requirements` as a requirement with
  `origin: internal`; it is not written here.

### 10. ASIL and partitioning
- An element carries the highest ASIL of the requirements allocated to it, a composition
  the highest of its parts, an interface at least that of its most critical use.
- `COV-23` reports an element below an allocated requirement: raise it or re-allocate.
  A lower ASIL is a decomposition and needs a `design-decision` that `concerns` every
  item whose ASIL is lowered, approved through `/review`. Never lower one on your own.
- Where elements of different ASIL coexist, draft a decision on how the lower ones are
  kept from disturbing the higher ones (memory, timing, exchanged data).

### 11. Self-check
Apply `.claude/docs/checklists/software-architecture.md` to the drafts. `check --all` says
what a draft still needs for review, but not what depends on `kind` or `origin` nor what
approval needs: walk the "Needed" column of the templates for those. Show the findings as
proposals; correct what the user accepts.

## Writing

- Show a table of the drafts (ID, type, title, kind, ASIL, links) and the allocation, and
  ask: "May I write these N items to `spec/software/architecture/`, `spec/views/` and
  `spec/decisions/`?" Queries go to `records/queries/`.
- IDs: `python tools/record.py next-id software-component`, likewise for the other
  types; then count upwards. Status `draft`. File layout: `component-template.md`,
  `interface-template.md`, `view-templates.md` and `decision-template.md` in `references/`.
- The allocation is written as `links.fulfils` on the element; no requirement is edited.
- Before changing an approved architecture item, say that its approval becomes stale
  and run `python tools/traceability.py impact <ID>` to show what depends on it.
- An element the user withdraws becomes `obsolete` with `superseded_by`, after every
  link to it has moved: `LINK` and `COV-24` report links to an obsolete item.
- Inside a baseline, changing or withdrawing an item needs an approved change request
  first (`/change-request`).

## Checks before you finish

Run `python tools/traceability.py check --all` and `python tools/traceability.py matrix`.
- `FORMAT`, `SCHEMA` and `LINK` findings on items written in this session: fix them.
- `COV-07`, `COV-08`, `COV-23` and `COV-24` for the scope of this session should be
  gone. If one remains, report it with the reason. Quote the `fulfils` tables.
- Expected, and to be said: `COV-25` until `/review` has approved the views; `COV-23`
  until a decomposition decision is approved; `COV-09` and `COV-21` until the detailed
  design exists.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. The budget sums against capacity and reserve; what is `NOT ASSESSED` and why.
3. Decisions the user has not taken; the queries written, by ID; needs and questions
   handed to `/sw-requirements`.
4. The remaining findings of the check that concern these items.
5. Next: `/review`, top down: requirements before the elements that fulfil them, shown
   items before or together with their views. Then `/baseline`, then
   `/sw-detailed-design`.

## Do not

- Do not set `status` to anything but `draft` (`open` for a query), or `obsolete` for an
  element the user withdraws, and do not write a review record.
- Do not edit requirements, imported items (a problem with one is a query) or
  `project.yaml`, and do not design units.
- Do not decide between alternatives, lower an ASIL or state a measured value.
