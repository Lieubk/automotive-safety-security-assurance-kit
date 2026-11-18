# Change request management plan

File: `plans/<ID>.md`. Type `plan`, `kind: change-request-management`. Attributes and
sections are those of type `plan` in `schema/items.yaml`. A project with SUP.10 in scope
has one such plan; the trace check reports `COV-27` until it is approved. A project
without SUP.10 in scope needs none: the configuration management plan then says who
decides on changes to baselined items.

The plan is the strategy (SUP.10.BP1). The states are not for the plan to invent: they
are the `change-request` lifecycle of `schema/items.yaml`. The plan says what the
project does in each state, by which criteria a request is analysed, and who decides.

## Decisions to ask the user before drafting

Ask these, with the options, and write down the answers. Do not fill in a value the user
has not given; a value taken from the template below is a proposal and is shown as one.

| Decision | Typical options | Lands in |
|---|---|---|
| Which changes need a change request | every change to the content of an item that is in a baseline; retiring such an item; new versions of imported inputs; changes that resolve a problem report | `Scope`; has to agree with the change control rule of the configuration management plan |
| What does not | items that are in no baseline; corrections of records (they are superseded) | `Scope` |
| Who may request a change | the customer through a named contact; every project member; quality assurance | `Scope` |
| What each state means here and who moves the request on | per state of the lifecycle: the activity and the role | `Approach` |
| What an impact analysis covers | affected items from the trace graph and from reading; code and tests; effort; schedule; risk; ASIL; regression scope; confirmation criteria; other open requests | `Criteria` |
| Who decides | a Change Control Board with named roles; the project lead alone below a limit; the customer for changes to delivered inputs | `Approach`, `Responsibilities` |
| On what basis and with which priorities | necessity, benefit, effort, capacity of the release, risk; priority classes and what each means | `Criteria` |
| How an urgent change is handled | decided by one named role between meetings and confirmed by the board afterwards; no shortcut at all | `Approach` |
| How the implementation is confirmed | affected items approved again; affected tests run on the changed state; implementation reviewed by someone who did not implement it | `Criteria` |
| How open requests are followed | at every board meeting; weekly by the Configuration Manager; from which overview | `Approach` |
| How the requester is informed | of the decision and of the closure, through which channel | `Approach` |
| Does handling differ by project phase | before the first baseline no change requests; stricter after a delivery | `Approach` |
| Who does what | roles, not names of people | `Responsibilities` |
| When the plan is updated | change of the deciding body, of the scope, of the customer interface | `Scope` |

## Template

The values are those of the power window example and are invented. Replace every one of
them with what the user decides. The example project itself has SUP.10 out of scope and
therefore no such plan.

```markdown
---
id: PLN-0003
type: plan
title: Change request management plan
status: draft
kind: change-request-management
---

## Scope

Covered: every change to the content of an item that is listed in a baseline other than
a working baseline (rule of PLN-0002), the retiring of such an item, every new version
of an input received from the customer, and every change that resolves a problem report.

Not covered: items that are in no baseline; they change with their authoring activity
and are reviewed again. Records are never changed; a wrong record is superseded.

A change may be requested by the customer's system engineering through the project
lead, by every member of the project team, and by quality assurance.

Declared limitations: the status history of a change request is its version control
history, so every change of state is committed on its own. No tool checks that the
states are passed in order; the Configuration Manager does.

This plan is revised when the Change Control Board changes, when the process scope in
`project.yaml` changes, and when the customer changes the way inputs are delivered.

## Approach

| State | What happens | Who |
|---|---|---|
| submitted | the request is recorded as a change request item: requester, request, reason, source, wanted release | Configuration Manager, from what the requester states |
| analysed | affected items are found and linked; effort, schedule, risk, regression scope and confirmation criteria are written | owners of the affected items, coordinated by the Configuration Manager |
| approved or rejected | the board decides; who decided, when, priority and target release are recorded in `decision`; a rejection carries its reason | Change Control Board |
| implemented | every affected item is changed on a branch named after the change request and approved again | owners of the affected items |
| verified | the affected tests have run on the changed state; the implementation is reviewed against the confirmation criteria | unit verification; a reviewer who did not implement the change |
| closed | the requester is told the result; a communication record names the change request | project lead |

No affected item is changed before the state is approved. A request that is put off
stays analysed, with a note in `decision` until when.

Urgent changes: the project lead and the software architect may decide together between
two meetings. The decision is recorded like any other and confirmed at the next meeting.

Related requests and problems: a request that resolves a problem report links to it.
Requests that affect the same item name each other and are decided in one meeting.

Following up: the board meets every two weeks. The Configuration Manager brings the
state of every open request (`python tools/traceability.py status`, and the open items
themselves) and what each one waits for.

The requester is informed of the decision and of the closure by the project lead.

## Criteria

An impact analysis is complete when it names:
- the items that change, found with `python tools/traceability.py impact` and `show`
  and by reading, each with what changes; code and test files;
- the items that are reviewed again without change, and those looked at and not
  affected, each with the reason;
- the highest ASIL among the items that change, and whether the person responsible for
  functional safety has to be involved;
- the regression scope by test case, following the regression rule of the plan of that
  test level;
- effort and effect on the release schedule, with who estimated;
- risks, other open requests on the same items, and open questions to the requester;
- confirmation criteria that can each be decided from a record or a command output.

The board decides on: necessity for the customer or for safety, benefit, effort,
capacity of the target release, and risk. Priorities: high (next release, before other
work), medium (planned release), low (when capacity allows).

A change request is verified when every affected item is approved again, every unit
whose code changed is reviewed again, every test case of the regression scope has
passed in a run on the changed state, every confirmation criterion is shown, and a
review of the implementation by someone who did not implement it has the verdict
approved.

## Environment and tools

- Change requests are item files under `records/changes/`, in the project repository.
- `tools/traceability.py` for impact, links and state counts; `tools/record.py` for the
  review record of the implementation and the communication record of the closure.
- The write protection of baselined items works inside a session of the toolkit only,
  and covers the content of items and their retiring. A change made with another
  editor, and a change of code, is found afterwards by the trace check.

## Responsibilities

| Activity | Performs | Checks or approves |
|---|---|---|
| Recording requests, keeping their state, bringing them to the board | Configuration Manager | project lead |
| Impact analysis | owners of the affected items | Configuration Manager for completeness |
| Decision, priority, target release | Change Control Board: project lead (chair), software architect, unit verification; the safety manager when an item with an ASIL is affected | - |
| Implementation | owners of the affected items | reviewers of those items |
| Review of the implementation | a team member who did not implement the change | - |
| Informing the requester | project lead | - |
```

## Notes

- The five sections are those the schema demands of a `plan`. `Scope`, `Approach` and
  `Criteria` are needed before review, the other two before approval.
- Keep the plan and the configuration management plan in step: both say from when a
  change needs a change request and who decides. They are compared in the plan review.
- State names in the plan are those of the lifecycle. A project that wants more states
  cannot have them without a change of the schema; say so instead of writing them into
  the plan.
- After its first baseline the plan itself changes only through a change request.
