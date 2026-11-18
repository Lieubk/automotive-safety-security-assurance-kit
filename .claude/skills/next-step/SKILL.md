---
name: next-step
description: "Say where the project stands and which skill to run next, from the state of the items, the open findings of the trace check and the evidence per base practice, in the order of the processes in scope. Recommends only; changes nothing. Use at the start of a session, after any skill has finished, or whenever it is unclear what to do next."
argument-hint: "[nothing, or one process ID of the scope to look at only that process]"
allowed-tools: Read, Glob, Grep, Bash(python tools/traceability.py *)
context: fork
model: haiku
effort: medium
background: false
---

# Where the project stands and what comes next

Reads the facts the tools give - items per type and state, findings of the trace
check, evidence per base practice - and turns them into one recommendation: the skill
to run next, with the items it concerns, and what follows after it. It works through
the processes in scope from the boundary downwards, because work built on an input
that is not settled inherits that uncertainty. It recommends; it does not act.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| none | performs no practice of any process: it reports the state per base practice as `practices` prints it and names the skill that addresses each open point | nothing: no item, no record, no file is written |

The report is input for whoever steers the project. It is not a progress report in the
sense of MAN.3 and not a statement about capability.

## Before you start

1. If there is no `project.yaml`, say: "This project has no scope yet. Run
   `/aspice-start` first." That is the whole recommendation; stop.
2. Read `project.yaml`: `scope.processes`, `scope.assessment_scope`, `inputs`,
   `aspice.target_level`. If one of these keys is missing, say that it is not
   recorded and point to `/aspice-start`; do not assume a target level, an
   assessment scope or that nothing was received.
3. Run `python tools/traceability.py status`,
   `python tools/traceability.py check --all` and
   `python tools/traceability.py practices`. Every command of this skill takes
   `--project <dir>` after the script name when the project is not the current
   directory.
4. If a command does not run (a missing Python package, a broken `project.yaml`),
   report `NOT ASSESSED` with the message of the tool, recommend repairing that, and
   stop. Do not describe the state of a project the tools could not read.

## Steps

### 1. State the facts
Quote the summary line of `check`, the table of `status`, and from `practices` every
row whose state is not `evidence present`. With a process ID as argument, run
`python tools/traceability.py practices <PROCESS>` and restrict the report to it; if
the tool answers that the process is not in scope, say that and stop.

### 2. Walk the stops in order
Read `references/situations.md`. Go through its stops from top to bottom and note what
is open at each: scope, structure, boundary inputs, plans, then every process in scope
in the order of the V, then the evidence that follows approval. The first stop with
something open decides the recommendation. Keep walking: everything open further down
goes into the report as "also open".

The table gives the short form. `references/situations.md` has every rule, the checks
that need Grep or `list`, and what to do where no authoring skill exists.

| Situation | How it shows | Recommend |
|---|---|---|
| No scope | no `project.yaml` | `/aspice-start` |
| Inputs not registered | an entry of `inputs` whose `source` appears in no item | `/import-inputs` |
| Inputs not accepted | `list --imported --status draft` or `--status in-review` prints items | `/review`; it applies the checklist `input-acceptance` |
| A question to a source is open | `QUERY` on an approved item; `list --type query --status open` | the user chases the answer; `/import-inputs <QRY-ID>` records it |
| A plan the scope needs is missing | `COV-27` | the skill of the process: `/sw-unit-verify`, `/baseline`, `/change-request`; by hand for the other plan kinds |
| System requirements not refined | `COV-05` | `/sw-requirements` |
| Requirements not allocated | `COV-07`; also `COV-08`, `COV-24`, `COV-25` | `/sw-architecture` |
| Components without design | `COV-09`, `COV-21` | `/sw-detailed-design` |
| Units without code | `COV-10`, `COV-22` | `/sw-unit-implement` |
| Units not verified | `COV-12`, `COV-18`, `COV-28`, `COV-29`, `COV-30`; `COV-17` on unit tests | `/sw-unit-verify` |
| Drafts not complete | `still to come before review: ...` in `check --all` | the authoring skill of the item |
| A review left findings open on a draft | `COV-19` with `left findings open` on an item in `draft` or `in-review` | the authoring skill of the item, then `/review`; for an input: the query its finding cites |
| Approved above something that is not | `UPSTREAM` | `/review` of the upstream item named in the message; work is approved from the top down |
| Drafts and stale approvals | items in `draft` or `in-review`; `COV-19` | `/review` |
| An item builds on a retired one | `LINK` with `target <ID> is obsolete` or `is rejected` | the authoring skill of the linking item |
| Suspect links, among them a new version of an input | `SUSPECT` | `python tools/traceability.py impact <changed ID>`, then `/review` |
| Consistency not evidenced | `CONSISTENCY` | `/review` |
| Change request names nothing | `COV-20` | `/change-request` |
| Baseline nobody was told about | `COV-26` | `/baseline` |
| Everything clean | no finding; no open state in `practices` beyond what a baseline closes | `/process-gate`, then `/baseline` |

### 3. Choose one recommendation
- Name one skill, the items or the process it should be run on, and the findings that
  lead to it, quoted. `python tools/traceability.py list --type <type> --status <state>`
  gives the IDs behind a count of `status`.
- Before recommending a skill, check with Glob that `.claude/skills/<name>/SKILL.md`
  exists. If it does not, say that the toolkit has no skill for this step and what has
  to be done by hand instead.
- For a suspect link, run `impact` on the item that changed and show the result
  before recommending the review: the user must see how far the change reaches.
- Where two orders are sound (review the requirements first, or draft the
  architecture first), recommend the upstream one and name the other as an option.

### 4. Add what the checks cannot see
- For every process in `assessment_scope` that is not in `processes`, repeat the
  warning: nothing of it is checked, and an assessment will ask for it.
- With a target level above 1, say once that the checks cover level 1 evidence only:
  planning, monitoring and resources of each process are not looked at by any tool
  here.
- Practices in state `no evidence structure` are listed as outside the toolkit: the
  schema holds nothing for them, so only a person can show that they are performed.

## Writing

Nothing is written. This skill has no write tools.

## Checks before you finish

- Every figure, state and finding in the report comes from a command run in this
  session. If something was changed since, run the commands again.
- Every recommended skill is installed, or the report says that it is not.
- Nothing is reported as done that the tools only show as present: `evidence present`
  means items exist, are approved or final, and no rule objects. Whether a practice is
  performed well is for people to judge.

## Hand-over

Report in this order, with the kind of each statement kept apart: tool output is
quoted, your reading of it is marked as such, and nothing is stated on behalf of a
person.
1. Where the project stands: scope and active rules, items per type and state, number
   of errors, warnings and findings on drafts.
2. What is open, in working order, grouped by stop; per group the rule, the count and
   the item IDs.
3. Recommendation: the next skill and its arguments, and why.
4. After that: the two or three steps that follow if the recommendation is taken.
5. Not checked or outside the toolkit: the points of step 4, and anything that was
   `NOT ASSESSED`.

## Do not

- Do not run another skill, edit an item, or fix a finding. Recommend.
- Do not state a count, a status or a link from memory or from an earlier session.
- Do not recommend work for a process that is not in `scope.processes`.
- Do not call a process finished, a project ready for an assessment, or a level
  reached. `/process-gate` reports per process; an assessment rates.
- Do not leave out a finding because it is inconvenient or old.
