# System interface item

File: `spec/system/architecture/<ID>.md`. Attributes and sections are those of type
`system-interface` in `schema/items.yaml`. A system interface has no structured keys:
its `Definition` is a table of properties. The examples are SYI-0001 and SYI-0003 of
`examples/power-window`, shortened.

## What is needed when

| Attribute or section | Needed | What to write |
|---|---|---|
| `id`, `type`, `title`, `status` | always | `title`: what crosses the boundary |
| `kind` | before review | `hardware-software`, `bus`, `electrical`, `mechanical`, `diagnostic` or `external` |
| `asil`, `security_relevant` | before review | at least that of the most critical function that depends on it |
| `links.fulfils` | before review where a requirement is about the interface | the system requirements it fulfils |
| `Definition` | before review | both end points, then the property table below |
| `Dynamic behavior` | optional | behaviour over time: start, stop, disturbance, loss; or omit |

## Kinds

| `kind` | Crosses | The definition must give at least |
|---|---|---|
| `hardware-software` | between the hardware and the software element: a pin, a peripheral, a register-level signal | the end points, signal type, electrical range, resolution, timing, how software is notified or reads it, fault behaviour |
| `bus` | a network between controllers | bus, message or frame, signal, coding, cycle or event, loss and time-out rules |
| `electrical` | power or signal wiring | voltage and current range, tolerances, protection, connector pins if fixed |
| `mechanical` | a mechanical connection or force | geometry, force or torque range, tolerances, mounting |
| `diagnostic` | to a tester or workshop | services or data, access conditions, response timing |
| `external` | to the environment or a neighbour that is not a controller | what the system may rely on, what it must tolerate |

## Example

```markdown
---
id: SYI-0001
type: system-interface
title: Hall sensor pulse signal
status: draft
kind: hardware-software
asil: B
security_relevant: false
links:
  fulfils: [SYR-0002]
---

## Definition

End points: Hall sensor on the motor shaft (SYE-0002) to the capture input of the
microcontroller timer, read by the window control software (SYE-0001).

| Property | Value |
|---|---|
| Meaning of one rising edge | 0.5 mm of glass travel; no direction information |
| Capture timer | free running, 32 bit, 1 count = 1 us, wraps every 4294.967296 s |
| Notification | the software is called at every rising edge with the captured timer value |
| Edge spacing in steady movement | 2.5 ms (200 mm/s) to 6.25 ms (80 mm/s) |
| Edge spacing below 400 us | not caused by glass travel: a disturbance, carries no travel information |
| Failure | a standing window produces no edges; a stuck level produces none either |

## Dynamic behavior

Edges are spaced further apart while the drive starts, stops or works against an
obstacle.
```

## Rules

- Name both end points by their element IDs, and say which side provides. Every interface
  has two ends; an interface whose partner is not an element has an `external` element
  or is not an interface of this system.
- Every property has a value and a unit; every range has its limits; a coded value has
  the meaning of every code, including the reserved ones and "not available".
- Timing: cycle or event, latency, jitter or tolerance, and what counts as loss.
- Say what each side does when the other fails or sends an invalid value, or state that
  the architecture leaves it to the requirements of the software element. Silence is
  not an answer.
- For `hardware-software`: the software requirements are derived from this definition.
  Anything the software needs to know (initial level, edge polarity, timer resolution,
  noise) is here or is a `query`. Ranges and timing are written as they are on the pin,
  not as the software sees them after conversion.
- Values that also appear in requirements are the same here, or the text refers to the
  requirement.
- Medium and energy count: for `electrical` and `mechanical` kinds the quantities are
  those of physics (volt, ampere, newton metre), with tolerance.
- The fields of a message or the pins of a connector may be a table; the definition of
  a whole bus (all messages) is an imported or referenced document, not repeated: name
  it with its version and list the signals this system uses.
