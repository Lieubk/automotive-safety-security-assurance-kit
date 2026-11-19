# The problem report

File: `records/problems/<ID>.md`. Type `problem-report`, lifecycle `problem-report` in
`schema/items.yaml`. A problem report is not reviewed like an engineering item; it is
moved through its states, and each state needs what the table says.

| State | Means | Needs (the check reports what is missing) |
|---|---|---|
| `open` | recorded, not yet understood | `title`, `severity`, `reported_by`, `reported_at`, `detected_by`, `found_in`, section `Description`; `affects` for the items it is seen in |
| `analysed` | cause and impact known | `origin`, section `Cause and impact` |
| `in-resolution` | the route is chosen and started | section `Resolution`; a change request that `resolves` it when an affected item is in a baseline (`COV-41`) |
| `resolved` | the resolution is carried out | the corrected items approved again; the change request implemented |
| `closed` | a named person accepted the closure | `closure` with `accepted_by`, `accepted_at`, `evidence`; every change request that resolves it closed (`COV-42`) |
| `rejected` | not a problem, or a duplicate | `rejection_reason`; `superseded_by` for a duplicate |

Independent of the state: a severity the strategy names as urgent needs `urgent_action`
(`COV-39`); a severity an alert rule covers needs a communication record to every party
it names (`COV-40`). While a report is open, analysed or in resolution, every approved
item it affects shows a `PROBLEM` warning.

## Example

```markdown
---
id: PRB-0001
type: problem-report
title: Automatic closing ends 20 ms before the window has stood still for 200 ms
status: closed
severity: major
reported_by: Software tester
reported_at: '2026-06-16'
detected_by: qualification-test
found_in: "qualification test program on the software of step application, before RUN-0004 was recorded"
origin: code
closure: {accepted_by: Software lead, accepted_at: '2026-06-22', evidence: RUN-0004}
links:
  affects: [CMP-0002]
---

## Description
What happens and what was expected, with the values; how to reproduce it (case, step,
build); the environment.

## Cause and impact
The cause, shown in the item or the code; what else is affected - other items, other
releases or variants, other users of the same component; why the severity is what it is.

## Resolution
The route and the actions: who corrects what, through which skill or change request;
for a component taken over, what was reported to whom and what was done meanwhile.
```

## Fields

| Field | Rule |
|---|---|
| `severity` | a value of the schema, by the criteria of the strategy. A change of severity is written in `Cause and impact` with the reason |
| `detected_by` | the activity that exposed it: `review`, `static-analysis`, `unit-test`, `integration-test`, `qualification-test`, `system-test`, `customer`, `field`, `other` |
| `origin` | the work product the cause lies in: `input`, `requirements`, `architecture`, `design`, `code`, `test-specification`, `test-environment`, `tool`, `other`. Together with `detected_by` it shows in the trends which activity let the problem through |
| `found_in` | the commit, tag or baseline, and the run or review that showed it; a run that was not recorded is named as what it was |
| `affects` | the items the problem is in or touches; a component taken over is named by its component item |
| `urgent_action` | `{action, authorised_by, authorised_at}`; `action` may be "none" with the reason - that is a decision too |
| `closure` | `{accepted_by, accepted_at, evidence}`; evidence is the ID of a final test run or review record (a list is allowed) |

The dates are the dates the user states. Who is named is who the user names.
