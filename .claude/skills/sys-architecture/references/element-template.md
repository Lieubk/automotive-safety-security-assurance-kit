# System element item

File: `spec/system/architecture/<ID>.md`. Attributes and sections are those of type
`system-element` in `schema/items.yaml`. The examples are SYE-0001 and SYE-0002 of
`examples/power-window` (there imported; in a project that owns SYS.3 they are drafts
you write).

## What is needed when

| Attribute or section | Needed | What to write |
|---|---|---|
| `id`, `type`, `title`, `status` | always | `title`: the name of the element as everyone calls it |
| `kind` | before review | `hardware`, `software`, `mechanical` or `external` |
| `asil`, `security_relevant` | before review | the highest of the requirements allocated; see step 9 of the skill |
| `links.fulfils` | before review | every system requirement the element is responsible for (`COV-03`, `COV-04`) |
| `Responsibility` | before review | what the element does for the system, what it does not do, and what it is given |
| `Dynamic behavior` | before approval | modes, start-up, reaction time, state after reset; or `Not applicable:` with the reason |

## Kinds

| `kind` | Use it for | Notes |
|---|---|---|
| `hardware` | electronics: controller, drivers, sensors, power supply | resources it offers to software are stated here |
| `software` | the software of the system as delivered into the hardware | what `/sw-requirements` builds on; its inside is not described here |
| `mechanical` | housing, gear, mounting, anything moved or held | |
| `external` | a neighbouring system, the environment, a user, a supplier's platform that the project does not design | state what is assumed of it |

## Example

```markdown
---
id: SYE-0001
type: system-element
title: Window control software
status: draft
kind: software
asil: B
security_relevant: false
links:
  fulfils: [SYR-0001, SYR-0002, SYR-0003, SYR-0004]
---

## Responsibility

The application software of the door module that moves the window. It evaluates the
switch request on the body network and the Hall sensor pulse signal and commands the
motor through the bridge driver. It detects an obstacle during closing and reverses.

Not part of this element: network management, diagnostics, supply monitoring and the
drivers of the microcontroller; they belong to the basic software of the customer.

Resources given to this element on the microcontroller: 16384 bytes of program flash,
1024 bytes of static RAM, 10 % of the processor time (source: SYR-0009).

## Dynamic behavior

- Cycle times: 5 ms for position, speed and motor command; 20 ms for the switch request.
- Obstacle reaction: at most 20 ms from the speed drop to the changed motor command.
- Start-up: ready 50 ms after reset is released, with the motor stopped.
```

## Rules

- `Responsibility` says what the system needs from the element, not how it is built.
  A software element does not list components; a hardware element does not list
  part numbers unless a requirement fixes them.
- Name the boundary: what a reader might expect here and finds elsewhere is stated as
  "Not part of this element", with the element that has it.
- Sub-elements: where one element has parts that others refer to separately (a sensor
  inside a drive unit), make each part an element of its own, name the parent in the
  `Responsibility` of both, and show the nesting in the `structure` view. The
  `fulfils` link stays on the element that carries the requirement.
- `COV-04` has no waiver: every element, an `external` one too, fulfils at least one
  requirement. Model a neighbour as an element only when a requirement is allocated to
  it, normally one that states what the system assumes of it (supply voltage range,
  message cycle of another controller). A neighbour no requirement is about appears in
  the `context` view as text, not as an item. Do not write requirements for it here.
- Numbers that also appear in requirements are the same here, or the text refers to the
  requirement.
- One element, one ASIL: if a part has another, make it an element.
