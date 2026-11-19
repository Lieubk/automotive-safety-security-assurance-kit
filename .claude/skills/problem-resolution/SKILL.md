---
name: problem-resolution
description: "Record, analyse, resolve and close problems, and analyse their trends (Automotive SPICE SUP.9): the problem resolution strategy with urgent and alert rules, problem reports with cause, impact and origin, authorised urgent actions, alert notifications, the route to a correction or a change request, closure accepted by a named person with evidence, and problem trend reports. Use when a test fails, a review finds a defect in an item that was not its subject, a customer or supplier reports a problem, when the trace check reports PROBLEM or COV-39 to COV-42, at the trend analysis dates of the strategy, or when no approved problem-resolution plan exists (COV-27)."
argument-hint: "['strategy', 'record', a PRB ID to take further, 'trends', or nothing for the open problems]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *), Bash(git status *), Bash(git log *)
---

# Problem resolution (SUP.9)
> Toolkit root: `${CLAUDE_PLUGIN_ROOT}` - where this shows a placeholder instead of a folder, it is the repository you are in. The `tools/`, `schema/`, `aspice/`, `iso-26262/`, `iso-sae-21434/`, `examples/` and `.claude/docs/` named here and in the references lie in the toolkit root; run its tools from the project folder as `python "<toolkit root>/tools/<script>.py"`.

Takes a problem from the moment someone sees it to the moment a named person accepts
that it is gone, and keeps the overall picture visible. The result is a `plan` of kind
`problem-resolution`, `problem-report` items moving through their states, communication
records for alerts, and `problem-trend-report` records.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SUP.9.BP1 Develop a problem resolution management strategy | writes the strategy with the user: states, severity classes, urgent and alert rules, routes, closure, trend analysis | `plan` with `urgent_severities` and `alerts` |
| SUP.9.BP2 Identify and record the problem | writes a problem report with what happens, how to reproduce it, where and by whom it was found | `problem-report` in state `open` |
| SUP.9.BP3 Record the status of problems | moves the report through the states of the schema; reads the history from git | `status`; `history <ID>` |
| SUP.9.BP4 (cause, impact) | proposes cause, impact and origin from the items and the evidence; the user confirms the classification | sections `Cause and impact`; `origin`, `severity`; state `analysed` |
| SUP.9.BP5 Authorize urgent resolution action | asks for the decision on an urgent problem and records who authorised what, and when | `urgent_action` (COV-39) |
| SUP.9.BP6 Raise alert notifications | names who has to be alerted; records the alert when the user states it was sent | `communication-record` (COV-40) |
| SUP.9.BP7 Initiate problem resolution | chooses the route with the user: correction by the authoring skill, a change request, a report to a supplier, or rejection | section `Resolution`; `resolves` link of a change request (COV-41) |
| SUP.9.BP8 Track problems to closure | follows the resolution; records the closure a named person accepts, with the evidence that it works | `closure` (COV-42); state `closed` |
| SUP.9.BP9 Analyze problem trends | reads the figures of `problems`, proposes a reading; the analyst decides the actions | `problem-trend-report` |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. `SUP.9` not in `scope.processes`: say so. A problem report may still be written - other
   skills route defects here - but the rules of SUP.9 are not checked; tell the user.
3. Run `python tools/traceability.py problems` and `python tools/traceability.py check`.
   Read the `PROBLEM` warnings and `COV-39` to `COV-42`.
4. `COV-27` for kind `problem-resolution`: do step 1 first. Problems found before the
   strategy exists are recorded anyway; urgency and alerts are decided case by case
   and the decision is written into the report.

## Steps

### 1. Strategy (BP1)
- Search `plans/` for `kind: problem-resolution`. If there is none or only a draft, read
  `references/strategy-template.md`, ask the user the decisions listed there and draft
  the plan. Severity classes, the urgent severities, who is alerted and who accepts a
  closure are the user's decisions.

### 2. Record the problem (BP2, BP3)
- Read `references/problem-record.md`. Before writing, compare with the problems
  `problems` lists: a duplicate is not recorded twice; name the existing one.
- Fill in what is known now: what happens against what was expected, how to reproduce
  it, the environment, `found_in` (commit and the run or review that showed it),
  `detected_by`, `reported_by`, `reported_at`, a provisional `severity`, and `affects`
  for the items it is seen in. State `open`.
- **Urgent (BP5)**: the severity is one of `urgent_severities` of the strategy. Ask who
  decides the immediate action (containment, a stop of deliveries, or "none" with the
  reason) and record it in `urgent_action` with that person and the date, as stated.
- **Alert (BP6)**: an alert rule of the strategy covers the severity. Say whom to tell.
  When the user states that it was done, record it:
  `python tools/record.py communication --subject <PRB-ID> --audience <party> ...
  --channel <how> --sent-at <date> --practice SUP.9.BP6`.

### 3. Diagnose (BP4)
- Find the cause from the items and the evidence: the failing case and its log, the
  item it rests on, the design, the code. `python tools/traceability.py impact <ID>` for
  each affected item shows what else depends on it; consider variants, releases and
  other users of the same component.
- Write `Cause and impact`, set `origin`, confirm or change `severity` and `affects`.
  The cause and the classification are proposals until the user confirms them. State
  `analysed`. A new severity may make steps 2 (urgent, alert) apply now.

### 4. Initiate the resolution (BP7)
- Propose the route; the user decides:
  - items not in a baseline: the authoring skill of each item corrects it, and `/review`
    approves the correction;
  - items in a baseline whose purpose is not internal: `/change-request`, with
    `resolves: [<PRB-ID>]` on the change request (`COV-41`);
  - a component taken over or an imported input: a report to whoever delivered it (a
    `query` for an input, a communication record otherwise) and the containment decided
    meanwhile;
  - not a problem, or a duplicate: state `rejected` with `rejection_reason` (and
    `superseded_by` for a duplicate).
- Write `Resolution` with the actions and who carries them out. State `in-resolution`.

### 5. Track to closure (BP8)
- `resolved` when the actions are carried out: corrected items approved again, a change
  request implemented.
- `closed` only when a named person accepts it, with evidence that the problem is gone:
  a final test run in which the exposing case passes, or a final review record of the
  corrected item. Record `closure` with who accepted it, when and that evidence. Every
  change request that resolves the problem is closed first.
- `python tools/traceability.py history <PRB-ID>` shows the states the report had.

### 6. Trends (BP9)
- At the dates of the strategy: read `references/tracking-and-trends.md`, run
  `python tools/traceability.py problems --as-of <date>`, and propose a reading: recurring
  origins, problems found late that an earlier activity should have found, ageing.
- The analyst decides what follows: a corrective action (`/project-status`), a change of
  a checklist or strategy, nothing. Write the assessment in their words to a file and
  record: `python tools/record.py problem-trends --reported-by <name> --assessment <file>
  --as-of <date> --period <text>`.

## Writing

- Show the problem report before writing it and ask: "May I record PRB-NNNN in
  `records/problems/`?" Ask again before each change of state.
- IDs: `python tools/record.py next-id problem-report`. A problem report is never
  deleted; a wrong one is `rejected` with the reason.
- Names in `reported_by`, `urgent_action`, `closure` and audiences are what the user
  states, never invented.

## Checks before you finish

Run `python tools/traceability.py check`.
- `FORMAT`, `SCHEMA`, `LINK` on reports written in this session: fix them.
- `COV-39` to `COV-42`: report each with what closes it - a decision, an alert, a change
  request, a closure with evidence. Only people close them.
- `PROBLEM` warnings name the approved items an unresolved problem affects; they stay
  until the problem is resolved.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. Per problem touched: state, severity, origin, route, the next action and who owns it.
3. Decisions still owed by people: urgent actions, alerts, classification, closure.
4. The figures of `problems` and, at a trend date, the record written.
5. Next: the authoring skill or `/change-request` for the resolution; `/review` for
   corrected items; the test skill to run the exposing case again.

## Do not

- Do not authorise an urgent action, send an alert, accept a closure or classify a
  safety- or security-relevant problem in anyone's name.
- Do not correct an item from here: the authoring skill does that, and `/review`
  approves it.
- Do not close a problem without evidence that the exposing case now passes or the
  correction was reviewed, or while a change request that resolves it is open.
- Do not delete a problem report or edit a final record.
