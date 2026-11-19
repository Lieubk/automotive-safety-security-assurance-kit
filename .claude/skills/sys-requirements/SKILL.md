---
name: sys-requirements
description: "Derive, write and analyse system requirements from stakeholder requirements (Automotive SPICE SYS.2). Use when system requirements are to be created, extended or reworked, or when the trace check reports stakeholder requirements not covered by system requirements (COV-01)."
argument-hint: "[stakeholder requirement IDs, a feature name, or nothing to work on all uncovered inputs]"
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---

# System requirements analysis (SYS.2)

Turns the accepted stakeholder requirements into system requirements that each state
one need of the system as a whole, can be verified, and are traced to their source. The
system is the product with its mechanics, electronics and software in its vehicle
environment; which of these fulfils a requirement is decided later, in `/sys-architecture`.
The result is a set of `system-requirement` items in state `draft`, ready for `/review`.
Drafting may be handed to the agent `system-engineer`; the questions to the user stay
with this skill.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SYS.2.BP1 Specify system requirements | derives functional and non-functional requirements, including parameters that shape behaviour | `system-requirement` items with a `Statement` section |
| SYS.2.BP2 Structure system requirements | sets `kind`, `priority` and `release` on every item | those attributes |
| SYS.2.BP3 Analyze system requirements | checks correctness, feasibility and verifiability; notes cost, schedule and risk | `Analysis` section; findings reported to the user |
| SYS.2.BP4 Analyze the impact on the operating environment | examines what each requirement means for the neighbours of the system and the vehicle | `Analysis` section; queries to the stakeholder |
| SYS.2.BP5 Develop verification criteria | writes measurable criteria and sets `verification_method` | `Verification criteria` section |
| SYS.2.BP6 Establish bidirectional traceability | sets `derived_from` links to the stakeholder requirements | links; `matrix` output |
| SYS.2.BP7 Ensure consistency | self-checks against the checklist; the evidence itself comes from `/review` | proposed findings; review record written by `/review` |
| SYS.2.BP8 Communicate agreed system requirements | not done here: `/baseline` records the baseline and who was informed | - |

## Before you start

1. If there is no `project.yaml`, stop: "This project has no scope yet. Run
   `/aspice-start` first."
2. If `SYS.2` is not in `scope.processes`, stop: "SYS.2 is out of scope for this
   project. System requirements delivered from outside are registered with
   `/import-inputs`."
3. Run `python tools/traceability.py status` and `python tools/traceability.py check --all`
   (every command takes `--project <dir>` when the project is not the current directory).
4. The inputs are `stakeholder-requirement` items, registered with `/import-inputs` and
   covered by an input acceptance review, or the team's own. If there are none, stop and
   say: `/import-inputs` registers what was delivered.
5. An input that is not approved - in `draft` or `in-review`, or carrying `COV-19` - is
   not settled. Name each such input and ask the user: wait for its acceptance, or draft
   against it at risk. Drafting at risk is allowed; the requirements derived from it stay
   in `draft` until the input is approved, because the check reports `UPSTREAM` and the
   review refuses to approve an item above something that is not approved.
6. A stakeholder requirement with `assessment` rejected needs no system requirement.
   `needs-clarification` means a question is open: read its query before deriving.
7. `SUSPECT` on an existing system requirement means its input changed after the last
   review: read the input's new version and decide with the user whether the requirement
   changes. An open `QUERY` on an input means a question to the stakeholder is unanswered.

## Steps

### 1. Decide what to cover
- With arguments: the named inputs or feature. Without: every `COV-01` finding
  (accepted stakeholder requirements without a system requirement), plus existing draft
  system requirements.
- Run `python tools/traceability.py matrix` and read the `derived_from` table. Tell the
  user the list and ask whether it is the right scope for this session.

### 2. Understand each input
- Read the input items by ID. For each one answer: what must the *system* do or
  guarantee for this to hold, seen from outside? What does it demand of the vehicle
  environment? Leave open which element - hardware, software, mechanics - does it.
- What is unclear, contradictory or not verifiable in an input is a question to the
  stakeholder. Do not guess. Ask the user which questions they can answer now. Each of
  the rest becomes a `query` item (`python tools/record.py next-id query`; folder
  `records/queries`; `to`, `asked_at`, a `Question` section, and `about` linking the
  input), written with the other items of this session. A requirement that depends on
  an open query says so in its `Analysis` section, by the query's ID.

### 3. Draft the requirements
- Read `references/writing-requirements.md` before drafting.
- One need per item. A parent may need several children; several parents may share one.
- Parameters that shape behaviour (thresholds, calibratable values, variant options) are
  requirements too: state them with their range and default.
- System-internal needs that have no parent (plausibility, diagnostics, a safe state)
  get `origin: internal` and a `Rationale` section. Before drafting one, read the
  existing requirements on the same behaviour
  (`python tools/traceability.py list --type system-requirement`, then by ID): it must
  neither repeat nor contradict one of them. Name the ones you compared it with.
- `asil` and `security_relevant` are inherited from the parent. A lower ASIL than the
  parent is a decomposition and needs an approved `design-decision` that `concerns` the
  requirement; do not lower it on your own. An internal requirement inherits nothing:
  propose the ASIL of the most critical requirement that relies on it (QM if none
  does), give the reasoning in `Rationale`, and have the user decide.
- A change of a stakeholder requirement that is in a baseline goes through
  `/change-request`; derive from the new version once it is accepted.

### 4. Structure
- `kind`: functional, non-functional, interface or constraint.
- `priority`: must or should. `release`: ask the user for the release plan; if none
  exists, propose one release and say so.

### 5. Analyse
For each draft, write the `Analysis` section when there is something to say:
- feasibility with the technology in view (timing, accuracy, power, temperature, cost
  of materials), and what is not yet known;
- the effect on the operating environment (SYS.2.BP4): the neighbours of the system
  (vehicle network, power supply, other ECUs, mechanics, the user), what each is asked
  to provide or tolerate;
- interdependencies and conflicts with other requirements;
- effect on cost and schedule that the user should know about; risks.
Report conflicts and risks to the user as a list; they decide what happens with them.

### 6. Verification criteria
- For every requirement write what will be observed and what counts as fulfilled, with
  values and tolerances, at the boundary of the system. If the statement already carries
  them, say that and restate the pass condition. They are the starting point of
  `/sys-qualification-test`.
- Set `verification_method`. `test` unless the user agrees that analysis, review or
  inspection is the appropriate method, with the reason in the section.

### 7. Trace
- `links.derived_from`: every stakeholder requirement it follows from, by ID. Check each
  link in both directions: the child follows from the parent, and together the children
  cover the parent.
- `links.relies_on`: every system requirement whose term, value or behaviour this one
  uses.
- Do not allocate here. `/sys-architecture` records which elements and interfaces
  fulfil a requirement (`fulfils`), so that approved requirements stay untouched.

### 8. Self-check
Apply `.claude/docs/checklists/system-requirements.md` to the drafts. Show the findings
to the user as proposals, grouped by item, and correct what they accept.

## Writing

- Show a table of the drafts (title, kind, ASIL, parents, verification method) and
  ask: "May I write these N system requirements to `spec/system/requirements/`?"
- IDs: `python tools/record.py next-id system-requirement`, then count upwards.
- File layout: `references/item-template.md`. Status `draft`.
- When changing an existing approved item, say first that its approval becomes stale
  and that `python tools/traceability.py impact <ID>` lists what depends on it. Write
  the changed item with `status: draft`.

## Checks before you finish

Run `python tools/traceability.py check --all`.
- `FORMAT`, `SCHEMA` and `LINK` findings on items written in this session: fix them.
- `COV-01` and `COV-02` for the inputs in scope of this session should be gone. If one
  remains, report it with the reason.
- `COV-03` (not fulfilled by an element or interface) and `COV-16` (no system
  qualification test) are expected until `/sys-architecture` and `/sys-qualification-test`
  have run. Say so.
- `UPSTREAM` is expected for nothing written here: the new items are drafts. If it
  appears on an existing approved requirement, its input went back to draft or review.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. The query items written in this session, each with the input it is about, and who
   the user wants to send them to.
3. Conflicts and risks the user has not decided; cost and schedule effects the project
   plan should take up.
4. The remaining findings of the check that concern these items.
5. Next: `/review` with checklist `system-requirements v1`; then `/baseline` to record
   the baseline and who was informed (SYS.2.BP8; an agreement with the customer is
   recorded only when the user states that it happened, with who and when);
   `/sys-architecture` to derive elements and interfaces.

## Do not

- Do not set `status` to anything but `draft`, and do not write a review record.
- Do not edit imported items. A problem with an input is a query.
- Do not allocate to hardware or software, and do not put design into a requirement:
  say what the system must do, not how it is built.
- Do not invent a parent to make a requirement look derived.
