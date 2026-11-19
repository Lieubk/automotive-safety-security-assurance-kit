# Safety requirements in the items

The example continues the power window. Values are invented.

## The levels and their links

| Level | Type | Links | ASIL |
|---|---|---|---|
| safety goal | `safety-goal` | `addresses` hazardous events | the highest of its events |
| functional safety requirement | `system-requirement` | `derived_from` the goal | not lower than the goal (COV-23) |
| technical safety requirement | `system-requirement` | `derived_from` a functional one; fulfilled by system elements (`fulfils` on the element, or `allocated_to` on the requirement when the element was received from outside the scope) | not lower than its source |
| software safety requirement | `software-requirement` | `derived_from` a technical one, a system element, or the goal | not lower than its source |
| component, interface, unit | `software-component`, `software-interface`, `software-unit` | `fulfils`, `part_of` | not lower than what is allocated (COV-23) |

`check` follows the ASIL through these links (`COV-23`); a lower ASIL needs an approved
decomposition decision.

## A functional safety requirement

```yaml
id: SYR-0011
type: system-requirement
title: Reversal at an obstacle within the fault tolerant time
status: draft
asil: B
security_relevant: false
kind: functional
priority: must
release: R1
verification_method: test
origin: derived
links:
  derived_from: [SG-0001]
```

```markdown
## Statement

When the closing window meets an obstacle with a force above the limit, the window
control shall stop the window and reverse it within 300 ms.

## Verification criteria

On the bench, with the reference obstacle of the customer's test specification, the
window reverses within 300 ms in every closing speed.
```

`kind` stays what the requirement is (functional, non-functional, interface, constraint);
whether it is a functional or a technical safety requirement shows from what it derives
from: the goal, or a functional safety requirement.

## A decomposition decision

```yaml
id: ADR-0005
type: design-decision
title: Obstacle detection split into speed and current monitoring
status: draft
level: software
decomposition:
  requirement: SWR-0004
  into: [SWR-0021, SWR-0022]
  independence: SAN-0003
links:
  concerns: [SWR-0004, CMP-0004]
```

`SAN-0003` is a dependent failures analysis (`method: dfa`) of the two detections; the
scheme applied is named in `Decision`, as the user chose it from the standard.
