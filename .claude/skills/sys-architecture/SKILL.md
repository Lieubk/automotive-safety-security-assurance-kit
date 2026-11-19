---
name: sys-architecture
description: "Design the system architecture from approved system requirements (Automotive SPICE SYS.3): system elements (hardware, software, mechanical, external), system interfaces, system-level views, design decisions with alternatives, and the allocation of every system requirement. Use when a system architecture is to be created, extended or reworked, or when the trace check reports system requirements without allocation (COV-03) or system elements without requirements (COV-04)."
argument-hint: "[system requirement IDs, an element or feature name, or nothing to work on all open allocation findings]"
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---

# System architectural design (SYS.3)
> Toolkit root: `${CLAUDE_PLUGIN_ROOT}` - where this shows a placeholder instead of a folder, it is the repository you are in. The `tools/`, `schema/`, `aspice/`, `iso-26262/`, `iso-sae-21434/`, `examples/` and `.claude/docs/` named here and in the references lie in the toolkit root; run its tools from the project folder as `python "<toolkit root>/tools/<script>.py"`.

Turns approved system requirements into an architecture expressed as items: the
elements the system consists of (hardware, software, mechanics, and the external
elements around it), the interfaces between them, views of structure and behaviour,
decisions with their alternatives, and the allocation of every system requirement. The
software element and its hardware-software interfaces are what `/sw-requirements`
(SWE.1) builds on. All items are written in state `draft`, ready for `/review`.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SYS.3.BP1 Develop system architectural design | breaks the system into elements, each with its reason and responsibility | `system-element` items; an `architecture-view` of kind `structure` or `context` |
| SYS.3.BP2 Allocate system requirements | assigns every requirement to the element or interface that fulfils it | `fulfils` links on `system-element` and `system-interface` items |
| SYS.3.BP3 Define interfaces of system elements | defines each interface with both end points, signals or media, ranges, units, timing, protocol | `system-interface` items with a `Definition` |
| SYS.3.BP4 Describe dynamic behavior | describes operating modes, transitions, start-up, shut-down, failure reactions, timing chains | `Dynamic behavior` sections; views of kind `state-machine`, `sequence`, `fault-reaction` |
| SYS.3.BP5 Evaluate alternative system architectures | fixes criteria first and assesses alternatives against them; the user decides | `design-decision` items with `level: system` and `concerns` links |
| SYS.3.BP6 Establish bidirectional traceability | sets `fulfils`, `shows` and `concerns` links and checks both directions | links; `matrix` output |
| SYS.3.BP7 Ensure consistency | self-checks against the checklist; the evidence itself comes from `/review` | proposed findings; review record written by `/review` |
| SYS.3.BP8 Communicate agreed system architectural design | not done here: `/baseline` records the baseline and who was informed | - |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. `SYS.3` not in `scope.processes`: stop. "SYS.3 is out of scope for this project. A
   system architecture delivered from outside is registered with `/import-inputs`."
3. Run `python tools/traceability.py status` and `python tools/traceability.py check --all`
   (every command takes `--project <dir>` when the project is not the current directory).
4. The inputs are `system-requirement` items, approved or imported with an input
   acceptance review. If there are none, stop and name `/sys-requirements` or
   `/import-inputs`.
5. A requirement in `draft` or `in-review`, or with a `COV-19` finding, is not settled.
   Name each one and ask: wait, or design against it at risk. Elements that fulfil it
   stay in `draft` until it is approved: the check reports `UPSTREAM`, and the review
   refuses to approve an item above one that is not approved.
6. `SUSPECT` on an existing element means that a requirement it fulfils changed after
   its review: read the new version first. An open `QUERY` on an input is a question to
   its source that is unanswered: read it before designing on that input.

## Steps

### 1. Decide what to cover
- With arguments: the named requirements, element or feature. Without: every `COV-03`
  (requirement not allocated) and `COV-04` (element without a requirement) finding,
  plus existing draft architecture items.
- Run `python tools/traceability.py matrix`; its `fulfils` and `shows` tables show what
  exists. `python tools/traceability.py list --type system-element` lists the IDs of one
  type. Ask the user whether this is the right scope.
- Drafting may be handed to the agent `system-engineer`: give it the IDs, the criteria
  of step 2 and the decisions already taken. It returns drafts and questions; the
  questions, the choice between alternatives and the queries go through you.

### 2. Find what shapes the architecture
- Read the requirements in scope by ID. List those that constrain structure, interfaces,
  timing, safety, security, cost, installation space or reuse, and add the project goals
  the user names. `references/architecture-guidance.md` lists typical drivers.
- Propose evaluation criteria and ask the user to rank them before any structure is
  drawn. Every `design-decision` uses them (step 7).
- A question the user cannot answer is not design input. About an imported item, or an
  element supplied from outside, it becomes a `query` item (`python tools/record.py
  next-id query`; folder `records/queries`; `to`, `asked_at`, a `Question` section,
  `about` linking the item). About a requirement the project wrote, it goes back to
  `/sys-requirements`.

### 3. Identify the elements
- Read `references/architecture-guidance.md` first. Propose the elements, each with the
  reason it is an element of its own: `kind` hardware, software, mechanical, or
  external for a neighbouring system the system exchanges with and does not design.
- Per element write `Responsibility`: what it does, and what it does not do, in terms of
  what the system needs from it. Levels of hierarchy are shown in a view and named in
  `Responsibility`; `references/element-template.md` says how.
- Software that arrives from outside (platform, basic software, a supplier's library)
  is an element too, with its source named in `Responsibility`. Its inside is the
  concern of the software architecture (`/sw-architecture`), not of this one.

### 4. Define the interfaces
- One `system-interface` per exchange between two elements. `kind` is hardware-software,
  bus, electrical, mechanical, diagnostic or external. Both end points are named in
  `Definition`; `references/interface-template.md` lists what a complete definition holds.
- The hardware-software interfaces are the ones the software requirements depend on:
  give them the same care as the software element itself, with ranges, units, timing,
  and what happens at the boundary on failure.
- Where an exchange crosses into an external element, state what the system may rely on
  and what it must tolerate. What is not known goes to a `query`.

### 5. Describe the dynamic behaviour
- An element's own modes and start-up go into its `Dynamic behavior` section; behaviour
  across elements goes into views. Cover operating modes and their transitions,
  start-up, shut-down, failure reactions and every chain with a timing requirement.
- Write a view for each, or give the reason why none is needed. A system architecture
  usually has a `context` view (the system and its neighbours), a `structure` view
  (elements and interfaces) and a `state-machine` or `sequence` view for the main
  functions. This is guidance, not a rule: the trace engine checks no view kinds at
  system level. `view-templates.md` of `/sw-architecture` shows the form of
  each kind; set `level: system`. Every view links with `shows` to every item in it.

### 6. Limits of the whole system
- Where requirements fix limits (processor load, memory, power, installation space,
  mass, cost), state in each element's `Responsibility` what it is given and where each
  number comes from. No tool adds them: show the user the sums before writing.

### 7. Alternatives
- For each choice that shapes the system (split between hardware and software, make or
  buy, sensor principle, bus or direct wire, home of a safety function) draft a
  `design-decision` with `level: system`: context, the criteria of step 2, at least two
  real alternatives, each assessed against each criterion. The form is
  `decision-template.md` of `/sw-architecture`.
- Present the assessment and ask the user to decide. `Decision` and `Consequences` record
  what the user decided; an undecided draft is listed as open in the hand-over.

### 8. Allocate
- Per requirement choose the responsible element, or for an interface requirement the
  interface, and record it as `fulfils` on that item. Requirements are not edited.
- A requirement shared by several elements is fulfilled by each of them; each
  `Responsibility` says which share. Check both directions with
  `python tools/traceability.py show <ID>`: `Responsibility` covers every requirement of
  the element, and every element has a requirement (`COV-04`).
- A requirement allocated to an element of kind `software` is what `/sw-requirements`
  derives software requirements from (`COV-05`); say so to the user.
- A need that only the design creates goes to `/sys-requirements` as a requirement with
  `origin: internal`; it is not written here.

### 9. ASIL and partitioning
- An element carries the highest ASIL of the requirements allocated to it, an interface
  at least that of its most critical use. `COV-23` reports an element below an allocated
  requirement: raise it or re-allocate. A lower ASIL is a decomposition and needs an
  approved `design-decision` that `concerns` every item whose ASIL is lowered. Never
  lower one on your own.
- Where elements of different ASIL coexist, draft a decision on how the lower ones are
  kept from disturbing the higher ones.

### 10. Self-check
Apply `.claude/docs/checklists/system-architecture.md` to the drafts. `check --all` says
what a draft still needs for review, but not what depends on `kind` nor what approval
needs: walk the "Needed" columns of the templates. Show the findings as proposals;
correct what the user accepts.

## Writing

- Show a table of the drafts (ID, type, title, kind, ASIL, links) and the allocation, and
  ask: "May I write these N items to `spec/system/architecture/`, `spec/views/` and
  `spec/decisions/`?" Queries go to `records/queries/`.
- IDs: `python tools/record.py next-id system-element`, likewise for the other types;
  then count upwards. Status `draft`. Layout: `element-template.md` and
  `interface-template.md` in `references/`; views and decisions as in `/sw-architecture`.
- The allocation is written as `links.fulfils` on the element or interface.
- Before changing an approved item, say that its approval becomes stale and run
  `python tools/traceability.py impact <ID>` to show what depends on it. Change the
  `status` line to `draft` first, then the content; what depends on it is reported as
  `UPSTREAM` and, once the item is approved again, as `SUSPECT`.
- An element the user withdraws becomes `obsolete` with `superseded_by`, after every link
  to it has moved: `LINK` and `COV-24` report links to an obsolete item.
- Inside a baseline, changing or withdrawing an item needs an approved change request
  first (`/change-request`).

## Checks before you finish

Run `python tools/traceability.py check --all` and `python tools/traceability.py matrix`.
- `FORMAT`, `SCHEMA` and `LINK` findings on items written in this session: fix them.
- `COV-03`, `COV-04`, `COV-23` and `COV-24` for the scope of this session should be
  gone. If one remains, report it with the reason. Quote the `fulfils` tables.
- Expected, and to be said: `COV-19` until `/review` has approved the items; `COV-05`
  until `/sw-requirements` has derived software requirements; `COV-15` until
  `/sys-integration-test` has verified the interfaces; `COV-23` until a decomposition
  decision is approved.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. Limits and sums against what the requirements allow; what is `NOT ASSESSED` and why.
3. Decisions the user has not taken; the queries written, by ID; needs handed to
   `/sys-requirements`.
4. The remaining findings of the check that concern these items.
5. Next: `/review` with checklist `system-architecture` v2, top down: requirements
   before the elements that fulfil them, shown items before or together with their
   views. Then `/baseline`; then `/sw-requirements` for the software element, and
   `/sys-integration-test` and `/sys-qualification-test`.

## Do not

- Do not set `status` to anything but `draft` (`open` for a query), or `obsolete` for an
  element the user withdraws, and do not write a review record.
- Do not edit requirements, imported items (a problem with one is a query) or
  `project.yaml`, and do not design the inside of the software or of a hardware element.
- Do not decide between alternatives, lower an ASIL or state a measured value.
