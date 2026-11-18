---
name: project-status
description: "Measure progress against the plan and report it (Automotive SPICE MAN.3.BP10, with the monitoring parts of BP4, BP5, BP7 and BP8): collect what the owners state, read the figures of `traceability.py progress`, write the project status report with the reporter's assessment, and record and follow up corrective actions. Use at every reporting date of the project plan, when a package is late or a milestone at risk, or when a corrective action is due."
argument-hint: "[nothing for a report as of today, a date YYYY-MM-DD, or a corrective action ID to follow up]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---

# Project status and corrective actions (MAN.3)

Compares what the plan says with what the items show, and puts the result on record.
The figures come from the tools: the state of each work package is read from the items
it delivers, lateness from its dates, milestones from the baselines. What people add -
the effort spent, that a package is finished, the reading of the figures, the actions
decided - is recorded as theirs. Nothing here changes the plan; a re-plan goes to
`/work-breakdown` or `/project-plan`.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| MAN.3.BP10 Review and report progress of the project | the status report with figures and the reporter's assessment; corrective actions with owner and due date, followed to closure | `project-status-report` record; `corrective-action` items |
| MAN.3.BP4, MAN.3.BP5, MAN.3.BP8 (monitor) | records the owners' statements of effort, start and completion; shows late packages and effort against estimate | `progress` of the work packages; the report |
| MAN.3.BP7 (monitor) | shows the commitments of the plan that fall due in the period | the report's assessment |
| MAN.3.BP9 Ensure consistency | shows a completion that the deliverables contradict, and milestones that the package dates no longer reach | the report |
| MAN.3.BP1 to BP3, BP6 | not here: `/project-plan` | - |

## Before you start

1. If there is no `project.yaml`, stop: "This project has no scope yet. Run
   `/aspice-start` first."
2. If `MAN.3` is not in `scope.processes`, stop: "Project management is out of scope
   for this project. I write no status report."
3. Find the plan of kind `project` and read `Reporting`: cadence, audience, thresholds.
   Without a plan, stop and name `/project-plan`; without work packages, name
   `/work-breakdown`.
4. Run `python tools/traceability.py check` and
   `python tools/traceability.py progress --as-of <date>`, the date being the argument
   or today. Every command takes `--project <dir>` after the script name when the
   project is not the current directory. Keep both outputs: they are the figures.
5. With a corrective action ID as argument, go to step 5 alone.

## Steps

### 1. What the owners state
For every package that is in progress, late or late to start, ask its owner (through
the user) for the effort spent up to the date, the actual start, and whether it is
finished. Record the answers under `progress` of the package - `actual_start`,
`actual_effort`, `as_of`, `completed_on` - with Edit; this is tracking and needs no
review. Record only what is stated; an unanswered question stays open and the report
says so. Run `progress` again.

### 2. Read the figures
From the output, list:
- packages `late`, `late to start`, and `done as stated, contradicted` with the items
  that are not settled;
- effort against estimate per package where both exist, and against the thresholds of
  `Reporting`;
- milestones `missed`, or `due` while packages they need are late; `reached ... (late)`;
- corrective actions open, and those `OVERDUE`;
- commitments under `Interfaces and commitments` of the plan that fall due in the period;
- the summary line of `check`: errors on items a package delivers hold its completion back.

### 3. The assessment
Read `references/status-and-actions.md`. Draft a short reading of the figures for the
reporter: what is on track, what is not and why as far as the items show it, what is
at risk, what is to be decided. Label it as a draft. The reporter changes it into their
own words and confirms it; the report carries their text and their name, never the draft.

### 4. Corrective actions
For each deviation above a threshold of the plan, ask whether an action is decided.
If yes: owner, due date, what is done, how the cause is kept from coming back - as the
reporter or the person who decided states it. Write it as a `corrective-action` item
that `addresses` the work packages or items concerned. A deviation without a decided
action is named in the assessment as open.

### 5. Follow up earlier actions
For each open action: ask its owner whether it was carried out (`done`). For each
action `done`: does the report show the effect - the package back on plan, the
milestone reachable? Then `closed` with the evidence in `Effect`. If not, back to
`open`, and say so. Never close an action on the strength of it being done alone.

### 6. Re-planning
Where the reporter decides to move dates, change estimates or scope, name the skill:
`/work-breakdown` for packages, `/project-plan` for milestones and commitments. A
changed approved package or plan is reviewed again; that review is the evidence of
the adjustment.

## Writing

- Write the reporter's assessment to a text file outside the item folders, for example
  `build/status-assessment.txt`. Ask: "May I record the status report as of <date>,
  reported by <name>, with N packages, M late, K corrective actions open?"
- Run `python tools/record.py status-report --as-of <date> --reported-by "<name>"
  --assessment build/status-assessment.txt [--period "<period>"]`. The tool writes the
  figures itself from `progress` and `check`; it refuses without an assessment.
- Corrective actions: ID from `python tools/record.py next-id corrective-action`,
  folder `records/actions/`, layout in `references/status-and-actions.md`, status `open`.
- Then propose to record who received the report, as `Reporting` names the audience:
  `python tools/record.py communication --subject <PSR-ID> --audience "<role>" --channel
  "<how>"`, only once the user states that it was sent.

## Checks before you finish

Run `python tools/traceability.py check` and `progress` again.
- `FORMAT`, `SCHEMA`, `LINK` on packages or actions changed in this session: fix them.
- The report lists the same figures `progress` printed for the date. Say if the check
  reported errors on delivered items: the report counts them.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session.
2. The report ID and its figures in one line each: packages, late, milestones,
   corrective actions open and overdue.
3. Statements still missing from owners; deviations without a decided action.
4. Next: the re-planning skill where dates or scope change; the next reporting date.

## Do not

- Do not state effort, a start or a completion an owner has not stated.
- Do not write the assessment in the reporter's name, and do not soften figures in it.
- Do not decide a corrective action, its owner or its due date.
- Do not close an action whose effect is not shown.
- Do not change the plan or the work packages' plan content here.
