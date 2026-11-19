---
name: quality-assurance
description: "Prepare and record the independent quality assurance of a project (Automotive SPICE SUP.1): the quality assurance plan with its checks and escalation path, checks of work products and of process activities that build on reviews, records and the process gate, quality records with the checker's verdict, non-conformances as corrective actions or problem reports followed to closure, escalation of overdue ones, and the periodic quality report. Use at the check dates of the plan, before a baseline the plan names, when the trace check reports COV-43 to COV-45 or no approved quality-assurance or verification plan (COV-27), or when a non-conformance is overdue."
argument-hint: "['plan', 'check <item or process IDs>', 'follow-up', 'report', or nothing for what is due]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Agent, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---

# Quality assurance (SUP.1)

Quality assurance gives an independent view: do the work products meet their criteria,
and are the processes carried out as planned. It builds on what the project already
holds - reviews, records, the trace check, the process gate - instead of repeating it,
and adds the judgement of a person who did not do the work. The toolkit prepares the
checks and records them; the person in the quality assurance role gives every verdict.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SUP.1.BP1 Develop a project quality assurance strategy | writes the plan with the user: checks, criteria, independence, reporting, escalation | `plan` with `quality_checks` and `escalation` |
| SUP.1.BP2 Assure quality of work products | prepares a check of a sample of items against their criteria; the checker decides | `quality-record` of kind `work-product` |
| SUP.1.BP3 Assure quality of process activities | prepares a check of a process: what the plan promises against what the records show, with the process gate as input; the checker decides | `quality-record` of kind `process` |
| SUP.1.BP4 Summarize and communicate quality assurance activities and results | prepares the periodic report from `quality`; records who received it | `quality-record` of kind `summary`; `communication-record` (COV-45) |
| SUP.1.BP5 Ensure resolution of non-conformances | drafts the action for every finding and follows it | `corrective-action` or `problem-report`, named by the finding (COV-44) |
| SUP.1.BP6 Implement an escalation mechanism | names what is due for escalation; records the escalation and the management's answer as stated | `communication-record` with `--practice SUP.1.BP6` and `--agreement` |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. `SUP.1` not in `scope.processes`: say so and stop; quality assurance outside the
   project is the organisation's.
3. Ask who holds the quality assurance role in this project, and say: the verdicts in
   the records are that person's. Someone who wrote or approved what is checked does not
   check it. A check this toolkit prepares is input for that person, not an independent
   check by itself.
4. Run `python tools/traceability.py quality` and `python tools/traceability.py check`.
5. `COV-27` for kind `quality-assurance`: do step 1 first; `record.py quality-check`
   refuses without an approved plan.

## Steps

### 1. Plan (BP1)
- Search `plans/` for `kind: quality-assurance`. If there is none or only a draft, read
  `references/strategy-template.md`, ask the decisions listed there, and draft it.
  Independence, the checks, the escalation path and who answers an escalation are the
  user's decisions.
- When SUP.2 is in scope, draft the verification strategy too (plan of kind
  `verification`, part "Kind verification" of `plan.md`): which work products are
  verified by which method and checklist, the criteria, the independence, where findings
  go. Reviews and their records stay with `/review`.

### 2. Decide what is due
- `quality` lists the checks of the plan with their last record; `check` reports
  `COV-43` for a baseline that a planned check did not precede. Before a baseline whose
  purpose a check names under `before`, that check is due now.
- Tell the user what is due and ask what to do in this session.

### 3. Check work products (BP2)
- Read `references/checks.md`, "Work products". Choose the sample with the checker:
  the types the check names, risk first (ASIL, changed since the last check, findings
  before).
- Facts first: state, approving review, checklist and reviewers (`show <ID>`, the review
  record), open findings of `check` on the item.
- Content: apply the checklist of the type to the sample, or have the `aspice-reviewer`
  agent read it against the checklist as a second view. Its findings are proposals.
- The checker decides the result: `conforms`, `conforms-with-findings`,
  `does-not-conform`.

### 4. Check process activities (BP3)
- Read `references/checks.md`, "Process activities". Facts: `practices <PROCESS>`, the
  process gate report if one was made (`/process-gate`), `progress` for the packages of
  the process, `problems` for its problems.
- Compare what the plan of the process promises (methods, order, criteria,
  responsibilities, independence) with what its records show; sample records.
- The checker decides the result.

### 5. Record, with actions for findings (BP2, BP3, BP5)
- For every finding the checker confirms, an action exists first: a `corrective-action`
  with owner, due date and `raised_in: <QAR to be written>`, or a `problem-report`
  through `/problem-resolution` when a work product is wrong. Ask before writing each.
- Write the summary in the checker's words to a file; findings as JSON
  `[{"id", "text", "action", "severity"}]`.
- `python tools/record.py quality-check --kind work-product|process --check "<name>"
  --subject <ID> ... --criteria "<checklist or plan>" --checked-by "<name>" --result
  <result> --summary <file> [--findings <file>] [--checked-at <date>]`.

### 6. Follow up and escalate (BP5, BP6)
- `quality --as-of <date>` lists each finding with the state of its action, how far it
  is overdue, and the escalation due by the plan's rules.
- An action done: its owner states it; the effect is shown in a later check or report,
  then the action is closed (`/project-status` keeps the register).
- An escalation due: say to whom. When the user states it happened and what management
  answered, record `python tools/record.py communication --subject <CA-ID> --audience
  <level> --channel <how> --agreement "<the answer, as stated>" --practice SUP.1.BP6`.

### 7. Report (BP4)
- At the cadence of the plan: `quality`, then a draft reading for the checker; the
  checker's text goes to a file. `python tools/record.py quality-report --checked-by
  "<name>" --result <result> --summary <file> --as-of <date> --period "<text>"`.
- When the user states who received it: `python tools/record.py communication --subject
  <QAR-ID> --audience ... --practice SUP.1.BP4` (`COV-45`).

## Writing

- Show each record's content and ask before running the command that writes it; show
  each action item before writing it to `records/actions/`.
- IDs: `next-id corrective-action`, `next-id problem-report`. Records are written only by
  `record.py`.
- Names of checkers, owners and managers are what the user states.

## Checks before you finish

Run `python tools/traceability.py check` and `quality`.
- `COV-43`: a baseline the plan's check did not precede; say so - a later check does not
  repair the order, it is reported in the next quality report.
- `COV-44`, `COV-45`: an action missing, a report not communicated.
- Overdue findings and escalations due from `quality`, by name.

## Hand-over

1. The base practice table with what was done in this session and what is open.
2. Per check: record ID, subject, criteria, checker, result, findings with their actions.
3. Open and overdue non-conformances, escalations due and recorded, answers received.
4. Decisions owed by people: results, actions, escalations, the report's reading.
5. Next: the owners' work on the actions; `/problem-resolution` for problems raised;
   the next check date of the plan.

## Do not

- Do not give a verdict, accept an action as effective or escalate in anyone's name.
- Do not present a check prepared by the toolkit, or by the people whose work it is, as
  independent quality assurance.
- Do not correct a work product from here; the finding's action does that.
- Do not edit a final record; a wrong one is superseded by a new check.
