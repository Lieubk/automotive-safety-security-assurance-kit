# Item definition, assets and damage scenarios

The values below belong to an invented door module of the power window example
(`examples/power-window`). Replace every one with what the project decides.

## Item definition

File `spec/cybersecurity/item/ITM-NNNN.md`, type `item-definition`.

```markdown
---
id: ITM-0001
type: item-definition
title: Power window of the driver door
status: draft
---

## Boundary and functions

The item is the driver door module with its window lifter software, the motor and the
Hall sensor. Outside: the body controller that sends switch requests of the other doors,
the vehicle bus, the diagnostic tester. Functions: open and close on request, one-touch
operation, anti-pinch reversal, end-stop learning.

## Preliminary architecture

Door module (SYE-0002) with the application software (SYE-0003); the motor (SYE-0004);
interfaces: the body bus (SYI-0001) for switch requests of other doors, the diagnostic
access (SYI-0002), the local switch (SYI-0003).

## Operational environment

The body bus reaches the diagnostic port and the telematics unit through the gateway.
Workshops use the diagnostic access with a tester. The vehicle is parked unattended.

## Assumptions

The gateway filters frames from the telematics unit to the body bus (to be confirmed by
the customer: query QRY-0004).
```

Where SYS.3 is in scope, name the system elements and interfaces by ID; `show <ID>`
gives their content. Where it is not, describe the elements in words and say so.

## Assets

Folder `spec/cybersecurity/tara/`, type `asset`, prefix `AST`.

| What to look for | Example in the power window |
|---|---|
| Commands received over an interface that crosses the boundary | close request of another door on the body bus: integrity, authenticity |
| Data the item stores or keeps | learned end-stop position: integrity |
| Software and its configuration | the application image and its calibration: integrity, authenticity |
| Diagnostic and update services | the routine that resets the anti-pinch learning: authorization |
| A function whose loss harms someone | anti-pinch reversal: availability |

```yaml
id: AST-0001
type: asset
title: Close request of another door on the body bus
status: draft
properties: [integrity, authenticity]
links:
  located_in: [SYI-0001]
```

Section `Description`: what the asset is, where it is held, processed or carried.

## Damage scenarios

Type `damage-scenario`, prefix `DMG`. The impact categories are those of the plan's
`tara_method`; the levels are severe, major, moderate, negligible.

```yaml
id: DMG-0001
type: damage-scenario
title: Window closes on an occupant's arm
status: draft
impact: {safety: major, financial: negligible, operational: moderate, privacy: negligible}
```

Sections: `Description` - the consequence for road users and how it comes about;
`Impact rationale` - one reason per rating, in the terms of `impact_meaning`. The safety
rating is the one the person responsible for functional safety gives from the severity
of the matching hazard; write who gave it.
