# Software requirement item

File: `spec/software/requirements/<ID>.md`. Attributes and sections are those of type
`software-requirement` in `schema/items.yaml`; the layout is defined in
`schema/item-format.md`.

```markdown
---
id: SWR-0010
type: software-requirement
title: Reversal command after a reported obstacle
status: draft
kind: functional
priority: must
release: R1.0
asil: B
security_relevant: false
verification_method: test
origin: derived
links:
  derived_from: [SYR-0002]
---

## Statement

While the window closes automatically, when an obstacle is reported the software shall
command motor reversal no later than 10 ms after the report.

## Verification criteria

With the obstacle report set in cycle n of the 5 ms task during automatic closing, the
motor command is "open" no later than cycle n + 2. Checked at the lowest and the
highest closing speed.

## Analysis

Needs the motor actuation to accept a direction change without a stop phase; to be
confirmed with the source of SYI-0002. Reaction time budget: 5 ms detection cycle plus
one cycle for the command.
```

Notes:

- `title` is a short name for lists and matrices; the obligation is in `Statement`.
- `release` is required before approval; `allocated_to` is added by `/sw-architecture`.
- Add `## Rationale` when `origin` is `internal`, or when a constraint needs its reason.
- `Analysis` is optional; write it when there is a feasibility, environment, cost or
  risk point, and leave it out otherwise rather than writing "none".
- A requirement that applies only to some product variants carries
  `variants: [<variant>, ...]`.
