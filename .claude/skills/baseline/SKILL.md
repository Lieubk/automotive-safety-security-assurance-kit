---
name: baseline
description: "Create baselines of approved work products, anchor them to a version control tag and record who was informed of them (Automotive SPICE SUP.8, and the communicate practices SWE.1.BP8, SWE.2.BP9, SWE.3.BP7 and SWE.4.BP7). Use for a requirements freeze, design freeze, release candidate or delivery, to write the configuration management plan, to audit a baseline, or when the trace check reports COV-26 or no approved configuration-management plan (COV-27)."
argument-hint: "[a baseline purpose, 'plan', 'communicate <baseline ID>', 'audit <baseline ID>', or nothing to see what is due]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *), Bash(git status *), Bash(git log *), Bash(git tag --list *)
---

# Baselines and their communication (SUP.8)

Freezes a state of the project that others can rely on. A baseline here is three things:
a baseline record that lists the approved items with content hash and status, a version
control tag that the user sets, and a communication record that says who was informed
and what was agreed. That last record is also the evidence that agreed requirements, architecture,
design and verification results were made known.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SUP.8.BP1 Develop a configuration management strategy | writes the plan of kind `configuration-management` with the user when it is missing or has gaps | `plan` item, approved through `/review` (COV-27) |
| SUP.8.BP2 Identify configuration items | no step of its own: item files and their IDs are the identification, the plan's `Scope` names everything else | none that the trace engine counts |
| SUP.8.BP3 Establish a configuration management system | uses the repository as it finds it; does not set it up or inspect its settings | none |
| SUP.8.BP4 Establish branch management | checks only that a baseline is taken on the branch the plan names | none |
| SUP.8.BP5 Control modifications and releases | creates no baseline while the check reports errors; proposes commit and tag and waits for the user; later changes to listed items go through `/change-request` | none that the trace engine counts |
| SUP.8.BP6 Establish baselines | checks the preconditions of the plan, creates the record, proposes commit and tag | `baseline` record; the tag |
| SUP.8.BP7 Report configuration status | reports `status` and `check` for the state that is frozen, and what was left out of the baseline | the `items` list of the `baseline` record; the output passed on with the communication |
| SUP.8.BP8 Verify the information about configured items | audits a baseline with `audit`: the record against the items at the tag | the output of the command in the hand-over; it is an observation, a person keeps it as evidence |
| SUP.8.BP9 Manage the storage of configuration items and baselines | not covered: backup, archiving and restore lie outside the toolkit | none |
| SWE.1.BP8, SWE.2.BP9, SWE.3.BP7 (communicate agreed requirements, architecture, detailed design) | records who was informed of the baseline that holds the approved items, how, and what was agreed, as the user states it | `communication-record` naming the baseline (COV-26) |
| SWE.4.BP7 Summarize and communicate results | records who received the unit verification results; the summary itself comes from `/sw-unit-verify` | `communication-record` naming the baseline and the runs (COV-26) |

For SUP.8.BP2 to SUP.8.BP5, SUP.8.BP8 and SUP.8.BP9 the schema has no evidence
structure. `python tools/traceability.py practices SUP.8` says so, and
`references/evidence-by-people.md` says what a person provides instead.

## Before you start

1. If there is no `project.yaml`, stop: "This project has no scope yet. Run
   `/aspice-start` first."
2. If `SUP.8` is not in `scope.processes`, say: "Configuration management is out of
   scope for this project. I write no plan and create no baseline." Go on only if the
   user wants on record that items or results of a process in scope were made known:
   then do step 7 alone, with item IDs or run IDs as subject.
3. Run `python tools/traceability.py status` and `python tools/traceability.py check`.
   Every command here and in the references takes `--project <dir>` after the script
   name when the project is not the current directory.
4. Find the plan: Grep `kind: configuration-management` in `plans/`. If there is none,
   or the check reports `COV-27` for this kind, do step 1 and stop after it: until the
   plan is approved the tool refuses every baseline that is not an internal one.
5. Run `git status --short --branch`. If the project is not under Git, the checks of
   branch, working tree and tag are `NOT ASSESSED`: say so and ask the user how the
   plan's version control answers them. Do not guess commands of another system.
6. With the argument `plan` go to step 1, with `communicate` to step 7, with `audit`
   to step 6. Otherwise start at step 2.

## Steps

### 1. The plan (only when it is missing, not approved, or the user asks)
- Read `references/cm-plan-template.md`. If a draft of the plan exists, read it and
  work on its gaps only. Ask the questions of the template. Where the user has no
  answer, propose one and label it as a proposal.
- Self-check the draft against the parts "Every plan" and "Kind
  `configuration-management`" of `.claude/docs/checklists/plan.md`.
- Write it as described under Writing. `/review` approves it; stop here until then.

### 2. Decide which baseline
- Read the plan by ID and `references/baseline-procedure.md`.
- With an argument: that purpose. Without: compare `status` with what the plan says
  about when each purpose is due, and tell the user which baseline is due and why.
- Take the purpose and the tag pattern from the plan, character by character. Ask the
  user to confirm purpose, tag, and what the baseline will be used for.
- Say before going on: the record lists the approved plans and engineering items;
  what is not approved is left out, and an approved item that rests on an unapproved
  one stops the tool (`UPSTREAM`). From then on a listed item is changed in content or
  retired only through `/change-request`. An internal purpose lists everything and
  protects nothing.

### 3. Check the preconditions
- Run the checks of the table "Preconditions" in `references/baseline-procedure.md` and
  self-check with `.claude/docs/checklists/baseline.md`. Show one table: check, command,
  the output quoted, and `PASS`, `FAIL` or `NOT ASSESSED`.
- On any `FAIL` or `NOT ASSESSED`, stop. Name what is missing and the skill that
  provides it. Where the plan allows a deviation (an open change request as a known
  open point, an item left out), the user may accept it; note who accepted it for the
  hand-over and for the baseline notice. An error of the trace check cannot be
  accepted away: the tool refuses.

### 4. Create the record
- Ask: "Create the baseline record for tag `<tag>`, purpose `<purpose>`, from the
  working tree as it is now?"
- Run `python tools/record.py baseline --tag <tag> --purpose "<purpose>"` and quote its
  output, including the line that says how many items were left out. If it prints
  `no record written`, quote the findings it lists and stop.

### 5. Commit and tag
- Show the exact commands of section "Commit and tag" of the reference, with the real
  file name, message and tag. Ask whether you shall run them or the user will. Run none
  of them without an explicit yes to the commands shown.
- Afterwards run `git status --short --branch` and `git log -1 --format=%H <tag>`, and
  report commit and tag. Pushing both is the user's step: say so.

### 6. Audit (before a delivery, where the plan asks for it, or on request)
- Follow section "Audit" of `references/baseline-procedure.md`: on the content of the
  tag run `python tools/traceability.py audit <baseline ID>` and `check`. Report `PASS`,
  `FAIL` or `NOT ASSESSED` with the output. A difference stops the delivery; the record
  is never repaired. Say that the output is not a record and who keeps it; the last
  part of that section says how a person puts the checks on record.

### 7. Communicate
- Read `references/communication-record.md`.
- Ask what actually happened: who was informed, through which channel, when, and
  whether something was agreed and by whom. If nothing has happened yet, draft the
  baseline notice of the reference for the user to send, and stop: `COV-26` stays open
  and is reported as open.
- Show the command with the user's words filled in. On a yes run
  `python tools/record.py communication --subject <ID> --audience "<who>" --channel "<how>"`,
  with `--sent-at <YYYY-MM-DD>` when it happened on another day than today (the tool
  refuses any other form), and with
  `--agreement "<what, by whom>"` only when the user states an agreement.
- Propose the commit of the communication record in the same way as in step 5.

### 8. Say what the toolkit does not show
- Run `python tools/traceability.py practices SUP.8` and quote it. For every row with
  `no evidence structure`, name from `references/evidence-by-people.md` what a person
  provides, and ask whether it exists. Do not judge it.

## Writing

- The plan: ID from `python tools/record.py next-id plan`, file `plans/<ID>.md`, status
  `draft`. Show the whole draft and ask: "May I write this configuration management
  plan to `plans/`?"
- Baseline and communication records are written only by `python tools/record.py`,
  never with Write or Edit, and only after the question of step 4 or step 7 was
  answered with yes.
- A review record on a baseline record is written only on the verdict of a person the
  user names, with the checklist cited as `baseline v1`.
- Records are final when written. A record with a mistake is not edited: tell the user
  and supersede it with a new record.

## Checks before you finish

Run `python tools/traceability.py check`.
- `FORMAT`, `SCHEMA` and `LINK` findings on a plan written in this session: fix them.
- `COV-26` for the new baseline is gone once its communication is recorded. If the
  communication has not happened, report the finding as open. Never record a
  communication to make it disappear.
- `COV-27` stays until `/review` has approved the plan. Say so.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. The baseline: record ID, tag, commit, purpose, number of items, items left out; the
   result of each precondition; deviations and who accepted them.
3. Each communication record with its subject, its audience and the practice it serves.
   `practices` counts any communication record for every communicate practice, so be
   exact here about which one was really served.
4. The audit verdict with the output and the commit it ran on, or "not audited".
5. What a person still provides for SUP.8 (step 8); open points such as a tag that is
   not pushed or a notice that is not sent.
6. Next: `/change-request` for every change to a listed item from now on;
   `/process-gate` for the readiness of the processes in scope.

## Do not

- Do not commit, tag or push without the user's explicit yes to the commands shown, and
  never move or delete a tag.
- Do not choose an internal purpose to get past a refused baseline, and do not take a
  baseline from a working tree that is not clean.
- Do not write a communication record for something that has not happened, and do not
  add an audience or an agreement the user did not state.
- Do not write or edit a record by hand, and do not set a plan to `approved`.
- Do not present `evidence present` as a rating, and do not claim the practices that
  have no evidence structure.
