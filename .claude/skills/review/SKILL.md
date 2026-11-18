---
name: review
description: "Prepare and record the review of engineering items, plans, imported inputs and the code of software units: script checks, an independent semantic pass against the checklist, findings confirmed by people, and a review record written by tooling with the result of every check (SUP.1.BP2 and the consistency practices of the SYS and SWE processes). Use when items wait in draft or in-review, when the trace check reports COV-19, SUSPECT or CONSISTENCY, after code was written or changed, or after an upstream item has changed. It is the only way an item becomes approved."
argument-hint: "[item IDs, an item type, or nothing to review whatever is waiting]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Agent, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---

# Review

Prepares a review so that people can decide on facts, and records what they decided.
The skill runs the script checks, has the semantic checks of the checklist applied by a
reviewing agent that cannot write, puts findings and open questions before the user,
and writes the review record with `tools/record.py` once named people have given a
verdict. It covers every item type of the `engineering` lifecycle, plans included, the
input acceptance review of imported items, and the review of unit code against its
design. Nothing else sets an item to `approved`.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SUP.1.BP2 | has each item checked against a versioned checklist and records the result of every check | `review-record`: checklist, `checks`, reviewers, verdict, findings |
| SYS.2.BP7, SYS.3.BP7, SYS.4.BP8, SYS.5.BP6, SWE.1.BP7, SWE.2.BP8, SWE.3.BP6, SWE.4.BP6, SWE.5.BP8, SWE.6.BP6 (those in scope) | has the subject compared with every upstream item it links to, and a unit with its code, each at a recorded hash | `subject`, `references` and `sources` of the review record |
| SUP.1.BP1 | not done here: the quality assurance strategy is a `plan` of kind `quality-assurance`; this skill reviews it like any plan | - |
| SUP.1.BP3, SUP.1.BP4, SUP.1.BP5, SUP.1.BP6 | not done here: checks of process activities, reporting, resolution of deviations and escalation lie with the people that plan names | - |

Whether a review counts as quality assurance depends on who reviewed: the quality
assurance plan says how independent that person must be. The agent is never that person.

## Before you start

1. If there is no `project.yaml`, stop: "This project has no scope yet. Run
   `/aspice-start` first."
2. Run `python tools/traceability.py status` and `python tools/traceability.py check --all`
   and read both before reading any item (`--project <dir>` when the project is not the
   current directory). If a command does not run, stop: the review preparation is NOT
   ASSESSED, with the reason, and nothing is recorded.
3. A review is not tied to one process. Reviewed are items whose type belongs to a
   process in `scope.processes` (`supports` of the type in `schema/items.yaml`; for a
   `plan`, its `kind` under `plan_kinds`) and items marked `imported`. For an item that
   is neither, stop: it comes from outside the scope and is registered with
   `/import-inputs`.
4. Change requests and problem reports are not reviewed here, although the tool would
   take their IDs: their states are decisions of their own lifecycles. The review of a
   change request's implementation is prepared and recorded by `/change-request`.
5. If nothing is waiting (step 1), say so and stop.

## Steps

### 1. Decide what is reviewed
- With IDs or a type as argument: those items. Without: collect
  - `python tools/traceability.py list --status draft` and `list --status in-review`,
    engineering items only;
  - `COV-19` findings: approvals that are stale, missing, or carry open findings;
  - `SUSPECT` findings: an upstream item, or the code of a unit, changed after the review;
  - `CONSISTENCY` findings: a review did not record what the item was compared with, or
    the code of a unit was never reviewed against its design.
- Read `references/scoping.md` and group the items into reviews: one checklist per
  review, what must be read together in one review, small enough to read properly. It
  also says when a unit needs a design review, a review of its code, or both.
- Show the reviews as a table (items, checklist, number of upstream items) and ask
  which one to run now. Steps 2 to 8 are done for one review at a time.

### 2. Pick the checklist
- Imported items: `.claude/docs/checklists/input-acceptance.md`. Otherwise the checklist
  whose `Applies to:` sentence names the item type (Grep it in
  `.claude/docs/checklists/`). Read it; cite it as `references/scoping.md` says.
- No checklist for the type: say "Semantic checks: NOT ASSESSED - the toolkit has no
  checklist for <type>". Do not write one on the spot. Ask which criteria the
  reviewers use; the record cites what the user names. Without stated criteria, stop.

### 3. Set the items to in-review
- Ask: "May I set these N items to `in-review`?" Then change the `status` line only.
- An approved item keeps its status when it is here only because of `SUSPECT` or
  `CONSISTENCY`, or for a code review: its own content has not changed.
- From now on the content is frozen; an item that changes starts again at step 4.

### 4. Script checks
- Run `python tools/traceability.py check --all`. Quote every finding whose item is a
  subject.
- A subject with a `FORMAT`, `SCHEMA` or `LINK` error is not ready for review: take it
  out, ask to set it back to `draft`, and name the authoring skill.
- Answer each `script` check of the checklist from that output: pass, or the finding.
- An `info` line `still to come before approval: ...` on a subject names content that
  approval requires and that is missing. It blocks an `approved` verdict. Read the
  `conditions` of the schema for the type as well; the preview does not cover them.
- Run `python tools/traceability.py hash --upstream <ID> ...` and keep the output:
  `references` is the list of items the subject has to be compared with.
- For a unit that has code (files under `source_files` exist) ask: "Is the code part of
  this review?" If yes: the code checklist applies, the unit must already be approved,
  and the user names the commit and confirms that the working tree is clean at it. If
  no: say that the record covers the design only and that `check` keeps a
  `CONSISTENCY` warning on the unit until a review of the code follows.

### 5. Semantic checks
- Delegate to the agent `aspice-reviewer`. Hand over the subject IDs, the path of the
  checklist, the output of `hash --upstream`, and the project folder if it is not the
  current one. Hand over nothing else: no explanation by the author, no hoped-for result.
- It returns a result for every semantic check - `pass`, `finding` with the text it
  rests on, or `not-assessed` with the reason.
- For a review of up to three items you may apply the semantic checks yourself, in the
  format of `.claude/agents/aspice-reviewer.md`. Then tell the user, and repeat in the
  hand-over: "No independent pass took place." Say also when this session drafted the
  items.

### 6. Findings and accountable checks
- Read `references/recording.md`. Present one overview, labelled by source:
  script findings (quoted), proposed semantic findings (item, check, severity, quoted
  text, what is wrong, what would fix it), checks not assessed.
- The user accepts, rejects, changes or adds findings. Only what a person confirms
  becomes a finding.
- Ask every `accountable` check of the checklist as a question and note who answered.
  "No" or "not yet" is a finding. An unanswered check is `not-assessed`.

### 7. Reviewers and verdict
- Ask who is accountable for the verdict. Offer the names under `people` in
  `project.yaml` if there are any; otherwise the user states them. Ask who wrote the
  items: at least one reviewer must be someone else. If there is none, stop before
  recording. A model, an agent or a tool is never a reviewer.
- Say what stands against `approved`. The tool refuses it while a finding is open,
  while a check is `not-assessed`, and while an open finding of an earlier review of the
  same content is not closed; missing mandatory content (step 4) stands against it too.
  Then ask for the verdict, `approved` or `rework`. Do not propose one.

### 8. Record
Record the review and set the status as described under Writing.

### 9. Reviewing again
Read `references/re-review.md` when findings were corrected after a `rework` verdict,
when code changed, or when an upstream item changed (`python tools/traceability.py
impact <ID>` lists what depends on it). Findings are closed by a new review, with an
entry that names the earlier finding under `closes`, never by editing the earlier record.

## Writing

- Run `python tools/traceability.py hash <ID> ...` and compare with step 4. A different
  hash means the content changed after the checks: go back to step 4 for that item.
- Write two JSON files outside the item folders, for example under `build/`: the
  confirmed findings, and the result of every check of the checklist (`pass`, `finding`
  or `not-assessed`, with a note). Formats: `references/recording.md`.
- Ask: "May I record this review: N items, checklist <name and version>, reviewers
  <names>, verdict <verdict>, M findings, K checks not assessed?"
- Run `python tools/record.py review --checklist "<name> v<N>" --reviewer "<name>"
  --verdict approved|rework --checks FILE [--findings FILE] [--item-under-test REF]
  <ID> ...`, with one `--reviewer` per person. Pass `--item-under-test <commit>` exactly
  when the code of the units was part of the review: only then does the tool store the
  hashes of their source files. It assigns the ID and fills in the date, `subject` and
  `references`.
- When the tool refuses ("no record written"), do not change a finding's state or a
  check's result to get past it; go back to the user.
- Then set the status, changing the `status` line only: `approved` when the verdict is
  approved, `draft` when it is rework (the table in `references/recording.md` has the
  cases where an approved item keeps its status). Record first, status second.

## Checks before you finish

Run `python tools/traceability.py check`.
- `COV-19`, `SUSPECT` and `CONSISTENCY` on items approved in this session are gone. If
  a line remains, quote it and say what it still asks for; do not edit a record or an
  item to make it disappear.
- A `SCHEMA` error on an item just approved means mandatory content is missing: tell
  the user; correcting it makes the approval stale and needs a new review.
- Other coverage findings on the subject are reported as they are. One that was a
  warning during the review is an error now that the item is approved; say so.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session.
2. Per review: record ID, checklist and version, reviewers as stated, verdict; items
   now `approved`; items back in `draft` with their open findings.
3. Checks not assessed and why; whether an independent pass took place; proposals the
   user rejected (count); for units with code, whether a code review is still owed.
4. Findings on imported items as queries for the source of the input.
5. Next: the authoring skill for items in `draft`, then `/review` again; `/baseline`
   when the set is approved; `/trace-check` for what the check still reports.

## Do not

- Do not supply a reviewer's name, and do not decide or suggest the verdict.
- Do not set `approved` without a record that covers the item's current hash.
- Do not edit a final record, not even to close a finding.
- Do not correct the items or the code under review. Corrections belong to the
  authoring skill.
- Do not change the content of an imported item; a problem with it is a query.
- Do not put unrelated items into one review, and do not improvise a checklist.
