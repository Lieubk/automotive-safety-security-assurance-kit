# Work package item

Type `work-package` in `schema/items.yaml`, folder `plans/work-packages/`, prefix `WP`.
Reviewed with `.claude/docs/checklists/work-breakdown.md`.

```markdown
---
id: WP-0004
type: work-package
title: Detailed design and code of WindowPos
status: draft
owner: Software developer
category: engineering
process: SWE.3
release: R1.0
estimate: 12
planned_start: "2026-04-20"
planned_finish: "2026-05-08"
activities:
  - {name: Unit designs UNT-0001 and UNT-0002, owner: Software developer, estimate: 4, planned_finish: "2026-04-24", skill: AUTOSAR Classic}
  - {name: Design review, owner: Software lead, estimate: 1, planned_finish: "2026-04-28"}
  - {name: Code of both units, owner: Software developer, estimate: 5, planned_finish: "2026-05-06", skill: coding guideline}
  - {name: Code review, owner: Software lead, estimate: 2, planned_finish: "2026-05-08"}
links:
  part_of: [WP-0001]
  depends_on: [WP-0003]
  delivers: [CDS-0001, UNT-0001, UNT-0002]
progress:
  actual_start: "2026-04-20"
  actual_effort: 7
  as_of: "2026-04-30"
---

## Description

The detailed design of the component WindowPos and the code of its two units, each
reviewed. Not included: unit tests (WP-0005).

## Deliverables

CDS-0001; UNT-0001 and UNT-0002 with their source files; the review records of design
and code.

## Estimate basis

Expert estimate of the software developer with the software lead: 2 days per unit
design, 2.5 days per unit of code at the size of the architecture's budgets, 3 days of
reviews. AntiPinch, a unit of similar size, took 11 days.
```

## Fields

| Field | Needed | Content |
|---|---|---|
| `owner` | always | the role or person who answers for the package |
| `category` | always | `engineering`, `management` or `support`; COV-33 wants all three |
| `process`, `release` | optional | the process the work serves; the release it belongs to |
| `estimate` | before review | effort in the unit of the project plan, normally person-days |
| `planned_start`, `planned_finish` | before review | dates, quoted, `YYYY-MM-DD` |
| `activities` | optional | steps with owner, estimate, planned finish and the skill they need; quote a name that holds a comma or a colon, or YAML splits it |
| `links.part_of` | below the top | the one package it belongs to (COV-31) |
| `links.depends_on` | where it waits | the packages that must finish before it starts (COV-34) |
| `links.delivers` | once items exist | the items it produces; tracking, not plan |
| `progress` | once work started | stated by the owner: `actual_start`, `actual_effort` up to `as_of`, `completed_on`; tracking, not plan |
| `Description` | always | the work and its boundary |
| `Deliverables` | before review | what it produces, also what does not exist yet |
| `Estimate basis` | before review | the method of the project plan applied, and the figures |

## What is plan and what is tracking

The content hash covers the plan: title, owner, category, estimate, dates, activities,
`part_of`, `depends_on` and the sections. Changing any of them makes an approved package
stale; it is reviewed again - that review is the evidence that the plan was adjusted
(MAN.3.BP4, BP5, BP8). `progress` and `delivers` are left out of the hash: an owner
records progress and links new items without a review.

## How progress is read

`python tools/traceability.py progress` gives each package one state:

| State | When |
|---|---|
| `not started` | nothing delivered, no `actual_start`, no part started |
| `in progress` | something delivered or started, and no `completed_on` |
| `done` | `completed_on` stated, every delivered item settled (engineering items approved, records final, queries and change requests closed), every part done |
| `done as stated, contradicted` | `completed_on` stated, but an item or a part is not settled; the line names them |

A package is `late` when it is not done and its planned finish has passed, `late to
start` when it has not started and its planned start has passed.

## Size and structure

- Top: one package per release or feature; below it, one per process or component.
- Management and support work are packages of their own: planning and reporting,
  configuration management, change control, quality assurance.
- A package is small enough when its state can change within one reporting period.
- A package delivers what one owner can answer for. Shared work is split, or one owner
  is named and the others appear in `activities`.
