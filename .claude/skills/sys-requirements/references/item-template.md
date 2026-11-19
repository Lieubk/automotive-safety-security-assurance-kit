# System requirement item

File: `spec/system/requirements/<ID>.md`. Attributes and sections are those of type
`system-requirement` in `schema/items.yaml`; the layout is defined in
`schema/item-format.md`.

```markdown
---
id: SYR-0002
type: system-requirement
title: Reversal after contact with an obstacle
status: draft
kind: functional
priority: must
release: R1.0
asil: B
security_relevant: false
verification_method: test
origin: derived
links:
  derived_from: [STK-0003]
  # relies_on: [SYR-0001]   # only where the statement uses what another requirement defines
---

## Statement

While the window closes automatically, when the glass meets an obstacle, the door module
shall move the glass downwards by at least 50 mm within 200 ms of the contact.

## Verification criteria

A test body with a stiffness of 10 N/mm is placed in the path of the glass at window
openings of 150 mm and 400 mm. After contact, the glass has moved at least 50 mm
downwards within 200 ms in each run, at supply voltages of 9 V, 13.5 V and 16 V.

## Analysis

Reaction time is split between detection, decision and actuation; the shares are
decided in the architecture. The mechanics must permit a direction change without a
stop phase; to be confirmed with the supplier of the window lifter. Neighbours: the
power supply must hold 9 V during reversal; the vehicle network is not involved.
```

Notes:

- `title` is a short name for lists and matrices; the obligation is in `Statement`.
- `release` is required before approval. The fulfilment by elements and interfaces is
  recorded by `/sys-architecture` on the architecture side.
- Add `## Rationale` when `origin` is `internal`, or when a constraint needs its reason.
- `Analysis` is optional; write it when there is a feasibility, environment, cost or
  risk point, and leave it out otherwise rather than writing "none".
- A requirement that applies only to some product variants carries
  `variants: [<variant>, ...]`.
- A system requirement delivered from outside is imported (`imported:` block) and is not
  written with this skill; see `/import-inputs`.
