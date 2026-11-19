---
name: change-request
description: "Record, analyse, have decided, steer the implementation of, verify and close a change to items that are in a baseline (Automotive SPICE SUP.10). Use when an item inside a final baseline is to change, when a new version of an imported input arrives, when a problem report needs a change, when the write hook refuses an edit because the item is part of a baseline, or when the trace check reports COV-20 or no approved change-request-management plan (COV-27)."
argument-hint: "[a change request ID to continue, or the item IDs, problem report or input the change concerns; 'plan' for the strategy]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Agent, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---

# Change request management (SUP.10)
> Toolkit root: `${CLAUDE_PLUGIN_ROOT}` - where this shows a placeholder instead of a folder, it is the repository you are in. The `tools/`, `schema/`, `aspice/`, `iso-26262/`, `iso-sae-21434/`, `examples/` and `.claude/docs/` named here and in the references lie in the toolkit root; run its tools from the project folder as `python "<toolkit root>/tools/<script>.py"`.

Makes sure that a baselined item does not change informally. Every change is recorded as
a `change-request` item, analysed for what it touches, decided by the people entitled to
decide, implemented by the skills that own the affected items, verified, and followed
until the requester knows the result. This skill writes and moves the change request. It
does not change the affected items itself.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SUP.10.BP1 Develop a change request management strategy | writes the plan of kind `change-request-management` with the user when it is missing | `plan` item, approved through `/review` (COV-27) |
| SUP.10.BP2 Identify and record the change requests | writes one item per request: who asks, what, why, from which source | `change-request` item with `requester` and `Description` |
| SUP.10.BP3 Record the status of change requests | moves `status` along the lifecycle only when the condition of the step is shown; no tool checks the steps | `status`; its history is the version control history of the file, the item has no history attribute |
| SUP.10.BP4 Analyze and assess change requests | finds the affected items with `impact`, `show` and by reading; states effort, schedule, risk, regression scope, dependencies and confirmation criteria | `Impact analysis` section; `affects` links |
| SUP.10.BP5 Approve change requests before implementation | prepares the request for the deciding body and records its decision as the user states it; no affected item is touched before | `decision` (demanded by the schema from `approved` or `rejected` on); the state |
| SUP.10.BP6 Review the implementation of change requests | checks that the affected items are approved again and the affected tests ran; has the implementation reviewed against the confirmation criteria and records the verdict people give | review records of the affected items (by `/review`); a `review-record` whose subject is the change request; `test-run` records |
| SUP.10.BP7 Track change requests to closure | says for every open request what it waits for; records that the requester was informed, as the user states it | states up to `closed`; `communication-record` naming the change request |
| SUP.10.BP8 Establish bidirectional traceability | links the request to every affected item, to the problem report it resolves and to the query that raised it | `affects` and `resolves` links (COV-20); `show` output |

## Before you start

1. If there is no `project.yaml`, stop: "This project has no scope yet. Run
   `/aspice-start` first."
2. Look at `scope.processes`.
   - `SUP.10` is in scope: work in full.
   - `SUP.10` is not in scope: say "SUP.10 is out of scope for this project. I keep the
     change request only as the record that lets a baselined item change. No strategy
     is demanded, `COV-20` is not active, and nothing I write is evidence for SUP.10."
     Then work in the reduced way of `references/lifecycle.md`. If in addition no
     baseline other than internal ones exists (`python tools/traceability.py list --type baseline`,
     then the `purpose` of each record), stop: nothing is protected, items change with
     their authoring skill and are reviewed again.
3. Run `python tools/traceability.py status` and `python tools/traceability.py check`.
   Every command here and in the references takes `--project <dir>` after the script
   name when the project is not the current directory.
4. In full mode: if the check reports `COV-27` for kind change-request-management, do
   step 1 first. A request that cannot wait is recorded as `submitted` meanwhile.
5. Decide whether a change request is needed at all, with the table "When a change
   request is needed" in `references/lifecycle.md`. If it is not, say why and name the
   authoring skill. With a change request ID as argument, read that item and continue
   at the step its state calls for.

## Steps

### 1. The strategy (full mode, only when the plan is missing or not approved)
- Read `references/plan-template.md`. Ask its questions, draft the plan, self-check it
  against the parts "Every plan" and "Kind `change-request-management`" of
  `.claude/docs/checklists/plan.md`. `/review` approves it.

### 2. Record the request
- Ask: who requests the change (role or party), what is to change, why, where it comes
  from (document and version, problem report, meeting), and for which release it is
  wanted. Do not fill in a reason the user has not given.
- If a `problem-report` item is the trigger, read it by ID; the request will carry
  `resolves`. If the problem exists only in words, say that no problem report is linked.
- If an answered `query` item is the trigger, read it by ID; the request will name it
  under `affects` and cite it in `Description`.
- Run `python tools/traceability.py impact <ID>` for each item the request names: a
  change request that already affects it is listed there.
  `python tools/traceability.py list --type change-request` shows all requests with
  their states. Name related ones to the user.
- Write the item with `Description`, state `submitted` (see Writing).

### 3. Analyse the impact
- Read `references/impact-analysis.md` and follow it: the trace graph first, then the
  search for what links cannot know, then reading every candidate by ID.
- Show the user three lists: items that change, items that are reviewed again without
  change, items looked at and not affected, each with the reason. Ask for effort,
  schedule and risk; a figure you propose is labelled as a proposal.
- Write `Impact analysis` with regression scope and confirmation criteria, and set
  `links.affects`. Apply part A of `.claude/docs/checklists/change-request.md` and show
  the findings as proposals. Then ask: "Is CR-nnnn ready to be decided? May I set it to
  `analysed`?"

### 4. Have it decided
- Give the user the one-page summary of `references/lifecycle.md` for the deciding body.
- Ask what was decided: by whom, when, the result, priority, target release,
  conditions. Record it in `decision` in the user's words and set `approved` or
  `rejected` (with `rejection_reason`). If the user has no decision yet, or says "just
  do it" without saying who decided, stop at `analysed` and say what is missing. The
  check demands `decision` in these states; it cannot tell whether the text is true.

### 5. Steer the implementation
- Only in state `approved`. Go through the affected items in the order of
  `references/lifecycle.md`, upstream first. Name for each the owning skill; the user
  runs it, then `/review`. This skill edits none of them.
- After each step run `python tools/traceability.py check` and quote the `COV-19`,
  `UPSTREAM`, `SUSPECT` and `COV-30` lines: they are the work still to do. Changed code of a unit
  goes through `/review` with the unit as subject and the code revision.
- If an item turns out to be affected that the analysis did not name, stop. Add it to
  `Impact analysis` and `affects`, and ask whether the decision covers it or the
  deciding body has to look again.
- When every item under `affects` is `approved` or `obsolete` and no `COV-19`,
  `SUSPECT` or `CONSISTENCY` line names an item of the analysis, ask to set
  `implemented`.

### 6. Verify
- Affected tests: the latest run has to describe the changed code. `check` shows no
  `COV-30` line for the changed units and their test cases, and
  `python tools/traceability.py status` names that run. Otherwise `/sw-unit-verify` first.
- Go through the confirmation criteria one by one, each with the record that shows it.
- Review of the implementation: part B of the checklist. Follow section "Review of the
  implementation" in `references/lifecycle.md`: semantic checks by the agent
  `aspice-reviewer`, findings confirmed by the user, verdict and reviewers stated by the
  user, record written by `python tools/record.py review` with the checklist cited as
  `change-request v2` and a result for every one of its checks. On `approved` ask to
  set `verified`.

### 7. Close
- Ask whether the requester was informed of the result, by whom, how and when. Only
  then run `python tools/record.py communication --subject <CR-ID> --audience "<requester>" --channel "<how>"`
  (with `--sent-at <YYYY-MM-DD>` for another day than today) and ask to set `closed`.
  Name the problem report it resolves: its owner can move it on.

## Writing

- ID: `python tools/record.py next-id change-request`. File `records/changes/<ID>.md`,
  layout in `references/item-template.md`, first state `submitted`.
- Show the item and ask: "May I write CR-nnnn to `records/changes/`?" Ask again before
  every change of state, and say which condition was shown by which command.
- The plan: `python tools/record.py next-id plan`, `plans/<ID>.md`, status `draft`.
- Tell the user that the status history exists only in version control: one commit per
  change of state keeps it. Propose the commit; commit only when the user asks.

## Checks before you finish

Run `python tools/traceability.py check --all`.
- `FORMAT`, `SCHEMA` and `LINK` findings on the change request or the plan: fix them.
- `COV-20` must not appear. In the reduced mode the rule is not active: run
  `python tools/traceability.py show <CR-ID>` and check the `affects` lines yourself.
- `COV-19`, `UPSTREAM`, `SUSPECT` and `COV-30` findings caused by the change are
  reported as open work, not explained away.

## Hand-over

Report, in this order:
1. The base practice table with what was done and what is open; in the reduced mode the
   sentence of "Before you start" instead of any claim for SUP.10.
2. The change request: ID, state, what it waits for and from whom.
3. The affected items with their present status; items waiting for review.
4. Questions to the requester; related change requests.
5. Next: the owning skill of the next affected item, `/review`, or `/baseline` once the
   change is closed and a new baseline is due.

## Do not

- Do not decide, and do not record a decision, a priority or a reviewer nobody stated.
- Do not change an affected item here, and let none be changed before `approved`.
- Do not edit an imported item; its new version comes through `/import-inputs`.
- Do not set a changed item back to `approved`; `/review` does that.
- Do not skip a state, and do not close a request whose requester was not informed.
  No tool checks the order of the states; this skill is the check.
- Do not widen an approved request silently, and do not bundle unrelated changes.
