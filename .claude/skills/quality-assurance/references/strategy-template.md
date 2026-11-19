# Quality assurance plan

File: `plans/<ID>.md`. Type `plan`, `kind: quality-assurance`. It answers SUP.1.BP1. The
trace check reports `COV-27` until it is approved, reads `quality_checks` for `COV-43`,
and `quality` reads `escalation`.

## Decisions to ask the user before drafting

| Decision | Typical options | Lands in |
|---|---|---|
| Who holds the role, and what makes them independent | a quality engineer from the quality department, reporting outside the project; never the project lead or an author of what is checked | `Responsibilities`, `Approach` |
| Which work products are checked, how many, against what | per type a sample, risk first; against the type's checklist | `quality_checks` (kind `work-product`), `Approach` |
| Which processes are checked, against what | the processes in scope; against their plans and the evidence `practices` and the process gate show | `quality_checks` (kind `process`) |
| When | before a baseline of a named purpose (`before`), monthly, per release (`when`) | `quality_checks` |
| What tools and models contribute | `check`, `practices`, the process gate and a model's reading are input; the verdict is the checker's | `Approach` |
| Non-conformances | a corrective action with owner and due date; a problem report when a work product is wrong; effect shown in a later check | `Approach`, `Criteria` |
| Escalation | overdue by more than N days to the project lead, by more than M days to the head of development; how the answer is recorded | `escalation`, `Approach` |
| Reporting | a quality report per month or per release, to the project lead and the customer's quality contact | `Approach` |

## Template

The values are those of the power window example (`plans/PLN-0007.md`) and are invented.

```markdown
---
id: PLN-0007
type: plan
title: Quality assurance plan
status: draft
kind: quality-assurance
quality_checks:
  - {name: work product sample, kind: work-product, scope: [software-requirement, software-unit, software-qualification-test], before: [release candidate], criteria: "checklist of the type"}
  - {name: process audit, kind: process, scope: [SWE.4, SWE.5, SWE.6], before: [release candidate], criteria: "the strategy of the process"}
escalation:
  - {after_days: 7, to: [Project lead]}
  - {after_days: 21, to: [Head of development]}
---

## Scope
## Approach
## Criteria
## Environment and tools
## Responsibilities
```

Write each section out for the project, as `plans/PLN-0007.md` of the example does.

## Notes

- `before` names baseline purposes exactly as the configuration management plan writes
  them; `COV-43` compares them with `purpose` of the baselines.
- Parties under `escalation` are matched, ignoring case, against the audience of the
  communication records that record an escalation.
