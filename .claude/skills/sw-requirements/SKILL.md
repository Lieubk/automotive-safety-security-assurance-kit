---
name: sw-requirements
description: "Derive, write and analyse software requirements from system requirements and system architecture (Automotive SPICE SWE.1). Use when software requirements are to be created, extended or reworked, or when the trace check reports system requirements not covered by software requirements."
argument-hint: "[system requirement IDs, a feature name, or nothing to work on all uncovered inputs]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---

# Software requirements analysis (SWE.1)

Turns the software-relevant content of system requirements and system architecture
into software requirements that each state one need, can be verified, and are traced
to their source. The result is a set of `software-requirement` items in state `draft`,
ready for `/review`.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SWE.1.BP1 Specify software requirements | derives functional and non-functional requirements from the inputs | `software-requirement` items with a `Statement` section |
| SWE.1.BP2 Structure software requirements | sets `kind`, `priority` and `release` on every item | those attributes |
| SWE.1.BP3 Analyze software requirements | checks correctness, feasibility and verifiability; notes cost and schedule effects | `Analysis` section; findings reported to the user |
| SWE.1.BP4 Analyze the impact on the operating environment | examines what each requirement asks of hardware, basic software and other elements | `Analysis` section; queries to the source of the inputs |
| SWE.1.BP5 Develop verification criteria | writes measurable criteria and sets `verification_method` | `Verification criteria` section |
| SWE.1.BP6 Establish bidirectional traceability | sets `derived_from` links; the allocation follows in `/sw-architecture` | links; `matrix` output |
| SWE.1.BP7 Ensure consistency | self-checks against the checklist; the evidence itself comes from `/review` | proposed findings; review record written by `/review` |
| SWE.1.BP8 Communicate agreed software requirements | not done here: `/baseline` records the baseline and who was informed | - |

## Before you start

1. If there is no `project.yaml`, stop: "This project has no scope yet. Run
   `/aspice-start` first."
2. If `SWE.1` is not in `scope.processes`, stop: "SWE.1 is out of scope for this
   project. Software requirements delivered from outside are registered with
   `/import-inputs`."
3. Run `python tools/traceability.py status` and `python tools/traceability.py check --all`
   (every command takes `--project <dir>` when the project is not the current directory).
4. The inputs are `system-requirement`, `system-element` and `system-interface` items,
   either produced by the project (approved) or imported (covered by an input
   acceptance review). If there are none, stop and say which skill provides them:
   `/import-inputs` for delivered inputs, the system-level skills otherwise.
5. An input that is not approved - in `draft` or `in-review`, or carrying `COV-19` - is
   not settled. Name each such input and ask the user: wait for its acceptance, or draft
   against it at risk. Drafting at risk is allowed; the requirements derived from it stay
   in `draft` until the input is approved, because the check reports `UPSTREAM` and the
   review refuses to approve an item above something that is not approved.
6. `SUSPECT` on an existing software requirement means its input changed after the last
   review: read the input's new version and decide with the user whether the requirement
   changes. An open `QUERY` on an input means a question to its source is unanswered:
   read the query before deriving from that input.

## Steps

### 1. Decide what to cover
- With arguments: the named inputs or feature. Without: every `COV-05` finding (system
  requirements allocated to software that no software requirement refines), plus
  existing draft software requirements.
- Run `python tools/traceability.py matrix` and read the `derived_from` table to see
  what is already covered. Tell the user the list and ask whether it is the right
  scope for this session.

### 2. Understand each input
- Read the input items by ID. For each one answer: what must the *software* do or
  guarantee for this to hold? What is left to hardware or to other elements?
- What is unclear, contradictory or not verifiable in an input is a question to its
  source. Do not guess. Ask the user which questions they can answer now. Each of the
  rest becomes a `query` item (`python tools/record.py next-id query`; folder
  `records/queries`; `to`, `asked_at`, a `Question` section, and `about` linking the
  input), written with the other items of this session. A requirement that depends on
  an open query says so in its `Analysis` section, by the query's ID.

### 3. Draft the requirements
- Read `references/writing-requirements.md` before drafting.
- One need per item. A parent may need several children; several parents may share one.
- Software-internal needs that have no parent (defensive measures, diagnostics the
  architecture will need) get `origin: internal` and a `Rationale` section. Before
  drafting one, read the existing requirements on the same behaviour
  (`python tools/traceability.py list --type software-requirement`, then by ID): it must
  neither repeat nor contradict one of them. Name the ones you compared it with.
- `asil` and `security_relevant` are inherited from the parent. A lower ASIL than the
  parent is a decomposition and needs an approved `design-decision` that `concerns` the
  requirement; do not lower it on your own. An internal requirement inherits nothing:
  propose the ASIL of the most critical requirement that relies on it (QM if none
  does), give the reasoning in `Rationale`, and have the user decide.

### 4. Structure
- `kind`: functional, non-functional, interface or constraint.
- `priority`: must or should. `release`: ask the user for the release plan; if none
  exists, propose one release and say so.

### 5. Analyse
For each draft, write the `Analysis` section when there is something to say:
- feasibility on the given hardware and platform (timing, memory, resolution);
- what it demands of the operating environment: hardware-software interface, basic
  software services and their configuration, other system elements;
- interdependencies and conflicts with other requirements;
- effect on cost and schedule that the user should know about; risks.
Report conflicts and risks to the user as a list; they decide what happens with them.

### 6. Verification criteria
- For every requirement write what will be observed and what counts as fulfilled, with
  values and tolerances. If the statement already carries them, say that and restate
  the pass condition.
- Set `verification_method`. `test` unless the user agrees that analysis, review or
  inspection is the appropriate method, with the reason in the section.

### 7. Trace
- `links.derived_from`: every parent, by ID. Check each link in both directions:
  the child follows from the parent, and together the children cover the parent.
- `links.relies_on`: every software requirement whose term, value or behaviour this one
  uses ("the report of SWR-0010", "the closing movement as SWR-0006 defines it").
- Do not allocate here. `/sw-architecture` records the allocation on the architecture
  side (`fulfils`), so that it does not change requirements that are already approved.

### 8. Self-check
Apply `.claude/docs/checklists/software-requirements.md` to the drafts. Show the
findings to the user as proposals, grouped by item, and correct what they accept.

## Writing

- Show a table of the drafts (title, kind, ASIL, parents, verification method) and
  ask: "May I write these N software requirements to `spec/software/requirements/`?"
- IDs: `python tools/record.py next-id software-requirement`, then count upwards.
- File layout: `references/item-template.md`. Status `draft`.
- When changing an existing approved item, say first that its approval becomes stale
  and that `python tools/traceability.py impact <ID>` lists what depends on it. Write
  the changed item with `status: draft`.

## Checks before you finish

Run `python tools/traceability.py check --all`.
- `FORMAT`, `SCHEMA` and `LINK` findings on items written in this session: fix them.
- `COV-05` and `COV-06` for the inputs in scope of this session should be gone. If one
  remains, report it with the reason.
- `COV-07` (not allocated) is expected until the architecture exists. Say so.
- `UPSTREAM` is expected for nothing written here: the new items are drafts. If it
  appears on an existing approved requirement, its input went back to draft or review.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. The query items written in this session, each with the input it is about, and who
   the user wants to send them to.
3. Conflicts and risks the user has not decided.
4. The remaining findings of the check that concern these items.
5. Next: `/review` for the new requirements; `/sw-architecture` to allocate them.

## Do not

- Do not set `status` to anything but `draft`, and do not write a review record.
- Do not edit imported items. A problem with an input is a query.
- Do not put design into a requirement: say what is needed, not how it is built.
- Do not invent a parent to make a requirement look derived.
