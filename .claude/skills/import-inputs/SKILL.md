---
name: import-inputs
description: "Register delivered inputs (customer or stakeholder requirements, system requirements, system architecture and interfaces, or software-level inputs when the scope starts lower) as imported items, unchanged, one item per delivered requirement or element, and prepare their input acceptance review. Use after /aspice-start, when a document was received, or when a new version of an input arrives."
argument-hint: "[path of the delivered document, or the source name of an entry in inputs of project.yaml]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---

# Registering delivered inputs

Turns a delivered document into items the project can trace to: one item per
requirement or element, in the words of the source, with the source's identifier, its
version and the date received. The result is a set of imported items in state `draft`
and a list of queries, ready for an input acceptance review through `/review`.

Today the skill reads the document and writes the item files itself. Structured
import and export (ReqIF, spreadsheets, ALM tools) is not built yet.

The practices are those of SYS.1. With SYS.1 in scope the rows are evidence for it;
without it the same steps are the entry check of the first process in scope, and no
base practice is claimed.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SYS.1.BP1 Obtain stakeholder requirements and requests | registers each delivered requirement or element as one item with source, version, date received and source identifier | imported items; entry in `inputs` of `project.yaml` |
| SYS.1.BP2 Understand stakeholder expectations | collects what is unclear, contradictory or missing as queries to the source; never answers them itself | query list; communication record once the user states that queries were sent or answered |
| SYS.1.BP3 Agree on requirements | prepares the input acceptance review; acceptance is a person's verdict, recorded by `/review` | proposed findings; review record written by `/review` |
| SYS.1.BP4 Establish stakeholder requirements baseline | not done here: `/baseline` | - |
| SYS.1.BP5 Manage stakeholder requirements changes | compares a new version with what is registered, replaces changed items in place under the new version and shows what depends on them; a change to baselined content is decided through `/change-request` | comparison report; items carrying the new `imported.version`; `SUSPECT` and `LINK` findings on what depends on them |
| SYS.1.BP6 Establish customer-supplier query communication mechanism | not done here: the channel to the source is the project's; the toolkit keeps the list and the records | - |

## Before you start

1. If there is no `project.yaml`, stop: "This project has no scope yet. Run
   `/aspice-start` first."
2. Run `python tools/traceability.py status` and `python tools/traceability.py check --all`.
3. Find the delivery in `inputs` of `project.yaml`. If it is not there, ask for level,
   source, version, date received and format; the entry is added under "Writing".
4. Read the document. If it cannot be read as text (an office file, a tool database),
   stop and ask for an export as PDF or plain text. Do not work from a summary or from
   what the user remembers of it.
5. Search the item folders with Grep for the `source` name of the delivery. If items
   of this source exist, a version of it is registered already: read
   `references/new-version.md` now. It adds a comparison after step 1 and says what
   is written for a changed, added or removed object.

## Steps

### 1. Take stock of the delivery
Read the whole document, chapter by chapter if it is large. List every object with its
identifier or place in the source and what it is: requirement, architecture element,
interface, information, heading, definition, reference to another document, project
condition. Show the counts per chapter and ask whether everything is to be registered
or a part the user names. A partial registration is said so in the hand-over.

### 2. Choose the type
Read `references/registering-inputs.md`. The type follows from what the content is for
the first process in scope that uses it, not from the title of the document. Show the
proposed type per kind of content and have it confirmed. If the level of the delivery
is produced by a process in `scope.processes`, explain the consequence given there
before going on.

### 3. Split into items without rewording
- One identified object of the source is one item, even when it states two needs: the
  compound is a query, not a reason to split.
- Without identifiers in the source, split at the smallest unit the source marks
  itself (numbered paragraph, table row) and use its place as `source_id`.
- The text goes in unchanged: wording, values, units, language, also its errors. No
  correction, no translation, no summary. `title` is a label for lists: the source's
  own heading or object name, else words taken from the statement.

### 4. Attributes and links
- Set an attribute only where the source states the value and it maps to an allowed
  value without interpretation. Show each mapping once (source value -> schema value)
  and have it confirmed. What does not map is left out and becomes a query.
- A missing ASIL on a requirement of a safety-relevant product is a query. Do not
  infer it from neighbours.
- Write links between inputs only where the delivery states them. An allocation is
  written where it is stated: as `allocated_to` on the requirement when it comes with
  the requirement, as `fulfils` on the element or interface when it comes with the
  architecture. Not both for one pair. For requirements that are already accepted,
  `fulfils` on the architecture item is the only way: they are not changed.

### 5. Content that is not a requirement
Headings give structure, nothing else. Information, examples and definitions are not
items; where an item needs one to be understood, it refers to it as the source does.
Referenced documents are listed with the question whether they were delivered.
Project and process conditions (dates, deliverables, reporting) are listed for the
user and not registered. Where it is unclear whether a passage is a requirement, ask
the user; if they do not know, it is a query. Nothing is dropped silently: everything
not registered appears in the not-registered list with its reason.

### 6. Queries
Collect what is unclear, contradictory, missing, not verifiable or not feasible, per
item, in the format of `references/queries-and-acceptance.md`. The toolkit never fills
a gap in an input: not with an assumption, not with a typical value, not in a note.
Ask which queries the user can answer from the delivery itself (an answer found in the
source closes the query); all others go to the source.

### 7. Self-check against the acceptance checklist
Apply `.claude/docs/checklists/input-acceptance.md` to the drafts. Each finding is a
proposal for the review, shown with the text it rests on. A draft that differs from
the source is a transcription error and is fixed. Nothing the source wrote is
corrected: such a finding becomes a query or stays a proposed finding.

## Writing

- Show a table of the drafts (source identifier, type, title, mapped attributes,
  links), three items in full, the not-registered list and the queries. Ask: "May I
  write these N items as imported inputs?" For a large delivery ask per chapter.
- IDs: `python tools/record.py next-id <type>` per type, then count upwards. Assign
  all IDs before writing, and write link targets first (elements and interfaces
  before the requirements allocated to them).
- Layout and folders: `references/item-templates.md`. Status `draft`, the `imported`
  block complete, `received` and `version` quoted.
- Until its acceptance review is recorded, an item can be corrected against the
  source: a transcription error or a structural finding is fixed by editing it. From
  then on the write hook refuses any change of what the item says, unless
  `imported.version` changes with it (`references/new-version.md`). An accepted input
  that a baseline other than an internal one lists is replaced or retired only with
  an approved change request that names it: hand over to `/change-request` first.
- An object registered by mistake is not deleted: set `status: rejected` with
  `rejection_reason`, after the user agreed.
- If the delivery is new in `inputs`, show the entry and add it; change nothing else
  in `project.yaml`.

## Checks before you finish

Run `python tools/traceability.py check --all` and `python tools/traceability.py status`.
- `FORMAT`, `SCHEMA` and `LINK` findings on items of this session: fix them, by
  comparing with the source again, not by guessing.
- The counts in `status` must match what was announced; say so with the numbers.
  `python tools/traceability.py list --status draft` names the items.
- `COV-05` on registered system requirements (and `COV-01` on stakeholder
  requirements) is expected when the next process is in scope: nothing is derived
  from them yet. The lines are `info` while the inputs are drafts and are the work
  list of the next skill. `SUSPECT` and `LINK` lines after a new version are quoted in
  the hand-over, not resolved here.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. Registered: source, version, number of items per type, ID ranges; what part of
   the delivery they cover.
3. Not registered, with the reason for each group.
4. Queries, numbered, each with item ID and source identifier, and which of them the
   user says were sent.
5. Proposed findings of the checklist.
6. For a new version: unchanged, changed, added and removed, and the `SUSPECT` and
   `LINK` findings the change produced on what depends on them.
7. Next: `/review` with the checklist `input-acceptance` for the listed IDs. After
   acceptance, the first authoring skill of the scope, for example `/sw-requirements`.

## Do not

- Do not reword, correct, translate, merge or complete what was delivered.
- Do not answer a query yourself, and do not record that one was sent or answered
  unless the user states it, with who and when.
- Do not set a status other than `draft`; `obsolete` or `rejected` only for an input
  the source withdrew or one registered by mistake, after the user agreed. Do not
  write a review record.
- Do not change what an accepted input says, except by registering a new version from
  its source, and do not work around the write hook that protects it.
- Do not register the team's own work as imported, and do not invent a link, an ASIL
  or an identifier the delivery does not contain.
