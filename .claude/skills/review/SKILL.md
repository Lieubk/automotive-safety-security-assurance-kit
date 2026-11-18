---
name: review
description: "Prepare and record the review of engineering items, plans, imported inputs and the code of software units: script checks, an independent semantic pass against the checklist, findings confirmed by people, and a review record written by tooling with the result of every check (SUP.1.BP2 and the consistency practices of the SYS and SWE processes). Use when items wait in draft or in-review, when the trace check reports COV-19, SUSPECT, CONSISTENCY or UPSTREAM, after code was written or changed, or after an upstream item has changed. It is the only way an item becomes approved."
argument-hint: "[item IDs, an item type, or nothing to review whatever is waiting]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Agent, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---

# Review

Prepares a review so that people can decide on facts, and records what they decided:
script checks, semantic checks against the checklist, findings confirmed by people, a
record written by `tools/record.py`. It covers engineering items and plans, the input
acceptance of imported items, and unit code. Nothing else sets an item to `approved`.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SUP.1.BP2 | has each item checked against a versioned checklist and records the result of every check | `review-record`: checklist, `checks`, reviewers, verdict, findings |
| SYS.2.BP7, SYS.3.BP7, SYS.4.BP8, SYS.5.BP6, SWE.1.BP7, SWE.2.BP8, SWE.3.BP6, SWE.4.BP6, SWE.5.BP8, SWE.6.BP6 (those in scope) | has the subject compared with every upstream item it links to, and a unit with its code, each at a recorded hash | `subject`, `references` and `sources` of the review record |
| SUP.1.BP1, SUP.1.BP3 to SUP.1.BP6 | not done here: the quality assurance strategy is a `plan` of kind `quality-assurance`, reviewed like any plan; process checks, reporting, resolution and escalation lie with the people it names | - |

Whether a review counts as quality assurance depends on who reviewed: the quality
assurance plan says how independent that person must be. The agent is never that person.

## Before you start

1. If there is no `project.yaml`, stop: "This project has no scope yet. Run
   `/aspice-start` first."
2. Every command below takes `--project <dir>` right after the script name when the
   project is not the current directory.
3. Run `python tools/traceability.py status` and `python tools/traceability.py check --all`
   and read both before reading any item. If a command does not run, stop: the review
   preparation is NOT ASSESSED, with the reason, and nothing is recorded.
4. A review is not tied to one process. Reviewed are items whose type belongs to a
   process in `scope.processes` (`supports` of the type in `schema/items.yaml`; for a
   `plan`, its `kind` under `plan_kinds`) and items marked `imported`. For an item that
   is neither, stop: it comes from outside the scope and is registered with
   `/import-inputs`.
5. Change requests, problem reports and queries are not reviewed here; the review of a
   change request's implementation belongs to `/change-request`.
6. If nothing is waiting (step 1), say so and stop.

## Steps

### 1. Decide what is reviewed
- With IDs or a type as argument: those items. Without: collect
  - `python tools/traceability.py list --status draft` and `list --status in-review`,
    engineering items only;
  - `COV-19` findings: approvals that are stale or missing. `left findings open` on a
    draft means the author has not corrected it yet: not ready;
  - `SUSPECT` findings: an upstream item, or the code of a unit, changed after the review;
  - `CONSISTENCY` findings: a review did not record what the item was compared with, or
    the code of a unit was never reviewed against its design;
  - `UPSTREAM` findings: the item named in the message, still in draft or in review.
  For a component, the interfaces that name it as provider or user count as upstream.
- Read `references/scoping.md` and group the items into reviews: one checklist per
  review, what must be read together in one review, small enough to read properly. It
  also says when a unit needs a design review, a review of its code, or both.
- Order the reviews from the top down. The tool refuses to approve an item while an
  item it links to is in draft or in review, unless both are subjects of one review.
- Show the reviews as a table (items, checklist, number of upstream items, open queries
  about them from `list --type query --status open`) and ask which one to run now.
  Steps 2 to 8 are done for one review at a time.

### 2. Pick the checklist
- Imported items: `.claude/docs/checklists/input-acceptance.md`. Otherwise the checklist
  whose `Applies to:` sentence names the item type (Grep it in
  `.claude/docs/checklists/`). Read it. Cite it as `"<file name without .md> v<N>"`,
  with the number of its version line: `software-requirements v2`.
- No checklist for the type: say "Semantic checks: NOT ASSESSED - the toolkit has no
  checklist for <type>". Do not write one on the spot. Ask which criteria the
  reviewers use; the record names them and is written with `--external-criteria`.
  Without stated criteria, stop.

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
- For a unit that has code ask: "Is the code part of this review?" If yes, the user
  names the commit and confirms the working tree is clean at it. `references/scoping.md`,
  "Units and their code", says what follows from each answer.

### 5. Semantic checks
- Two ways; say what each costs and let the user choose. The agent `aspice-reviewer`
  is independent and reads every subject and upstream item in full on a strong model:
  minutes per pass, and the largest share of the cost of a review. Applying the checks
  in this session is cheaper and not independent; it is allowed for at most three
  items, or when the agent is not available (agent definitions load when a session
  starts). Then use the format of `.claude/agents/aspice-reviewer.md` and say, here and
  in the hand-over: "No independent pass took place." Say also when this session
  drafted the items.
- Hand the agent the subject IDs, the path of the checklist, the output of
  `hash --upstream`, and the project folder if it is not the current one. In a
  re-review add the earlier record and, per subject, the output of
  `python tools/traceability.py diff <ID> --since <REV-ID>` (`references/re-review.md`).
  Hand over nothing else: no explanation by the author, no hoped-for result.
- It returns a result for every semantic check - `pass`, `finding` with the text it
  rests on, `not-applicable` or `not-assessed` - with the reason, and its questions.

### 6. Findings and accountable checks
- Read `references/recording.md`. Present one overview, labelled by source:
  script findings (quoted), proposed semantic findings (item, check, severity, quoted
  text, what is wrong, what would fix it), checks not assessed, questions, open queries.
- The user accepts, rejects, changes or adds findings. Only what a person confirms
  becomes a finding. For each one name the three ways on, without recommending one:
  corrected in this sitting, corrected after a `rework` verdict, or closed with a reason
  the reviewers give (`references/recording.md`).
- A problem in an item that is not a subject is not a finding of this review: it
  becomes a query (imported item) or a problem report (item of the project). A question
  nobody can answer yet leaves its check `not-assessed`. Both: `references/recording.md`.
- Ask every `accountable` check of the checklist as a question and note who answered.
  "Yes" is `pass`. "No" is a `finding` that no reviewer's decision closes: the verdict
  is `rework`. "Not yet", or nobody who could answer, is `not-assessed`: do not press
  for it, the items stay `in-review`, nothing is approved, and the review is completed
  when the answer exists. Never answer such a check for the person it concerns.

### 7. Reviewers and verdict
- Ask who is accountable for the verdict. Offer the names under `people` in
  `project.yaml`; if the key is absent or empty, ask, and do not assume anyone. Ask who
  wrote the items: at least one reviewer must be someone else, and more where
  `conventions.review_independence` asks for it. If there is none, stop before
  recording. A model, an agent or a tool is never a reviewer.
- Say what stands against `approved`. The tool refuses it while a finding is open,
  while a check has no result or is `not-assessed`, while an accountable check is
  answered with a finding, while an item the subject builds on is not approved, and
  while an open finding of an earlier review of the same content is not closed; missing
  mandatory content (step 4) stands against it too. Then ask for the verdict,
  `approved` or `rework`. Do not propose one.

### 8. Record, and review again when needed
Record the review and set the status as described under Writing. Read
`references/re-review.md` when findings were corrected after a `rework` verdict, when
code changed, or when an upstream item changed. A re-review reads what changed since
the earlier record, not the whole item again. An item that did not change itself is
confirmed against a new upstream version with `record.py review --reconfirm`, without
the checklist. Findings are closed by a new review, with an entry that names the
earlier finding under `closes`, never by editing the earlier record.

## Writing

- Run `python tools/traceability.py hash <ID> ...` and compare with step 4. A different
  hash means the content changed after the checks: go back to step 4 for that item.
- Write two JSON files outside the item folders, for example under `build/`: the
  confirmed findings, and the results of the checks, as in `recording.md`.
- Ask: "May I record this review: N items, checklist <name and version>, reviewers
  <names>, verdict <verdict>, M findings, K checks not assessed?"
- Run `python tools/record.py review` as `recording.md` shows, with one `--reviewer` per
  person, `--item-under-test <commit>` exactly when the code of the units was part of
  the review, `--external-criteria` only when the user named criteria from outside the
  toolkit. The tool assigns the ID and fills in date, `subject` and `references`.
- When the tool refuses ("no record written"), do not change a finding's state or a
  check's result to get past it; go back to the user.
- Then set the status, changing the `status` line only: `approved` when the verdict is
  approved, `draft` when it is rework (the table in `references/recording.md` has the
  cases where an approved item keeps its status). Record first, status second.
- Propose a commit of the record, the items and any query or problem report written:
  a later re-review finds the reviewed text only in a commit, and a code review names
  one. Commit on the user's yes.

## Checks before you finish

Run `python tools/traceability.py check`.
- `COV-19`, `SUSPECT`, `CONSISTENCY` and `UPSTREAM` on items approved in this session
  are gone. If a line remains, quote it and say what it still asks for; do not edit a
  record or an item to make it disappear.
- A `SCHEMA` error on an item just approved means mandatory content is missing: tell
  the user; correcting it makes the approval stale and needs a new review.
- Other coverage findings on the subject are reported as they are. One that was a
  warning during the review is an error now that the item is approved; say so.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session.
2. Per review: record ID, checklist and version, reviewers as stated, verdict; items
   now `approved`; items back in `draft` with their open findings.
3. Checks not assessed and why, with the answer that is awaited and from whom; whether
   an independent pass took place; proposals the user rejected (count); for units with
   code, whether a review of the code is still owed.
4. Open queries and problem reports by ID, each with the items it is about; for a
   query whom it was put to, or that it is not sent yet.
5. Next: the authoring skill for items in `draft`, then `/review` again; `/baseline`
   when the set is approved; `/trace-check` for what the check still reports.

## Do not

- Do not supply a reviewer's name, and do not decide or suggest the verdict.
- Do not set `approved` without a record that covers the item's current hash.
- Do not edit a final record, not even to close a finding.
- Do not correct items or code under review; that is the work of the authoring skill.
- Do not change the content of an imported item; a problem with it is a query item.
- Do not put unrelated items into one review, and do not improvise a checklist.
