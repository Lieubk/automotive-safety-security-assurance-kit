# Problem resolution strategy

File: `plans/<ID>.md`. Type `plan`, `kind: problem-resolution`. It answers SUP.9.BP1;
the trace check reports `COV-27` until it is approved, and reads `urgent_severities` and
`alerts` from it for `COV-39` and `COV-40`.

## Decisions to ask the user before drafting

| Decision | Typical options | Lands in |
|---|---|---|
| What counts as a problem here | every deviation found after an item was approved; findings of reviews on items that were not the subject; every failed test case; reports of customers and suppliers | `Scope` |
| Who may report, who is informed | everyone in the project; the customer; suppliers of components taken over | `Scope`, `Responsibilities` |
| Severity classes | `critical`: safety or security affected, or a delivery stopped; `major`: a requirement not met; `minor`: everything else. The values are fixed by the schema; the criteria are the project's | `Criteria` |
| Urgent severities | `critical` | `urgent_severities`; `Approach` says who may authorise the immediate action and within what time |
| Alerts | per severity: the parties to tell and how fast - for example `critical` to the customer and the functional safety manager within 1 day | `alerts` (a list of `{severity, audience, within_days, channel}`) |
| Routes to a resolution | correction through the authoring skill; a change request once the item is in a baseline; a report to the supplier of a component taken over | `Approach`; it agrees with the change request management plan |
| Closure | who accepts; what evidence: the exposing test case passed again, or a review of the correction | `Criteria`, `Responsibilities` |
| Trend analysis | how often (with each status report, per release), by what (origin, detection, severity, age), who decides the actions | `Approach`, `Responsibilities` |

## Template

The values are those of the power window example (`plans/PLN-0006.md`) and are invented.

```markdown
---
id: PLN-0006
type: plan
title: Problem resolution strategy
status: draft
kind: problem-resolution
urgent_severities: [critical]
alerts:
  - {severity: critical, audience: [Customer, Software lead], within_days: 1, channel: mail}
  - {severity: major, audience: [Software lead], within_days: 2, channel: mail}
---

## Scope
What a problem is here, who reports, who is told; what is left to the customer.

## Approach
The states of the schema (open, analysed, in-resolution, resolved, closed, rejected) and
what each one needs; who authorises an urgent action; the routes to a resolution; the
trend analysis.

## Criteria
The criteria of each severity; closure: who accepts and with which evidence.

## Environment and tools
Problem reports as items in `records/problems/`; `traceability.py problems` and
`history`; `record.py communication` and `problem-trends`.

## Responsibilities
Who records, analyses, decides urgent actions, alerts, accepts closure, analyses trends.
```

Write each section out for the project; the example's plan is a model, not a form.

## Notes

- The audiences in `alerts` are matched, ignoring case, against `audience` of the
  communication records about the problem: write them the same way in both places.
- A severity not named under `alerts` needs no alert; say in `Approach` that this is
  intended.
