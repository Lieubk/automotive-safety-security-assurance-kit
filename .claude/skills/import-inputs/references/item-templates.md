# Imported items

Layout as in `schema/item-format.md`: one item per file, named `<ID>.md`, in the
folder of its type. The examples are inputs of the power window project as this skill
writes them: in state `draft`, before the input acceptance review. The template of a
`query` item is in `queries-and-acceptance.md`.

## Types, folders and sections

| Type | Prefix | Folder | Sections of the type |
|---|---|---|---|
| `stakeholder-requirement` | STK | `spec/stakeholder` | `Statement`, `Assessment notes` |
| `system-requirement` | SYR | `spec/system/requirements` | `Statement`, `Rationale`, `Verification criteria`, `Analysis` |
| `system-element` | SYE | `spec/system/architecture` | `Responsibility`, `Dynamic behavior` |
| `system-interface` | SYI | `spec/system/architecture` | `Definition`, `Dynamic behavior` |
| `software-requirement` | SWR | `spec/software/requirements` | `Statement`, `Rationale`, `Verification criteria`, `Analysis` |
| `software-component` | CMP | `spec/software/architecture` | `Purpose`, `Responsibility`, `Dynamic behavior` |
| `software-interface` | IFC | `spec/software/architecture` | `Description` |
| `architecture-view` | VIEW | `spec/views` | `Description`, `Diagram` |
| `component-design` | CDS | `spec/software/design` | `Design concept`, `Static structure`, `Dynamic behavior`, `Design evaluation` |
| `software-unit` | UNT | `spec/software/design` | `Purpose`, `Behavior`, `Error handling`, `Dynamic behavior`, `Design notes` |

Read the type in `schema/items.yaml` before the first item of a type is written: the
allowed values of its attributes are checked on imported items too.

## System requirement

File: `spec/system/requirements/SYR-0001.md`

```markdown
---
id: SYR-0001
type: system-requirement
title: Limitation of the closing force
status: draft
kind: functional
priority: must
release: R1.0
asil: B
security_relevant: false
verification_method: test
origin: derived
imported:
  source: Front Door Module - System Requirements Specification
  version: "2.1"
  received: "2026-03-02"
  source_id: DM-SYS-041
---

## Statement

While the window closes with a window opening of more than 5 mm, the door module shall
keep the force on an obstacle in the path of the glass at or below 80 N.

## Verification criteria

A test body with a stiffness of 10 N/mm is placed on the upper edge of the glass at
window openings of 10 mm, 150 mm and 400 mm, at supply voltages of 9 V, 13.5 V and
16 V. The peak force in each of the nine runs is at most 80 N.
```

Notes:

- `kind` to `origin` are there because this source gives them per requirement. A
  source that gives none of them yields an item with `id`, `type`, `title`, `status`,
  `imported` and the statement, and that is a complete imported item.
- A requirement carries no allocation link. Its allocation is the `fulfils` link of
  the element that answers it (next template).
- Where the text of a requirement names another object of the delivery, the name
  stays as the source wrote it, for example "the test body of DM-SYS-041". The
  registered item is found through its `imported.source_id`.

## System element

File: `spec/system/architecture/SYE-0001.md`

```markdown
---
id: SYE-0001
type: system-element
title: Window control software
status: draft
kind: software
asil: B
security_relevant: false
imported:
  source: Front Door Module - System Architecture Description
  version: "1.4"
  received: "2026-03-02"
  source_id: "4.1"
links:
  fulfils: [SYR-0001, SYR-0002, SYR-0003, SYR-0004]
---

## Responsibility

The application software of the door module that moves the window. It evaluates the
switch request and the Hall sensor pulses and commands the motor. It tracks the window
opening and the window speed, detects an obstacle during closing and reverses the
window.

## Dynamic behavior

- Cycle times: 5 ms for position, speed, obstacle detection and motor command; 20 ms
  for the evaluation of the switch request.
- Start-up: the element is ready 50 ms after the reset is released, with the motor
  stopped.
```

Notes:

- `fulfils` is the allocation: the delivery says that this element answers
  DM-SYS-041 to DM-SYS-044, registered as SYR-0001 to SYR-0004. The link names item
  IDs; the text of the item keeps the source's identifiers.
- `kind` matters: rule COV-05 asks for a software requirement derived from each system
  requirement that an element of kind `software` fulfils. The other values are
  `hardware`, `mechanical` and `external`.
- The requirements are written before the element, so that the link has its targets,
  and they are accepted before it: an element cannot be approved while a requirement
  it fulfils is still in draft or in review.
- The text is shortened here. A registered item holds everything the source says about
  the element.

## System interface

File: `spec/system/architecture/SYI-0002.md`

```markdown
---
id: SYI-0002
type: system-interface
title: Motor command to the bridge driver
status: draft
kind: hardware-software
asil: B
security_relevant: false
imported:
  source: Front Door Module - System Architecture Description
  version: "1.4"
  received: "2026-03-02"
  source_id: "5.2"
---

## Definition

Control inputs of the H-bridge driver, set by the software.

| Signal | Values | Effect |
|---|---|---|
| Direction | off, opening, closing | off connects both motor terminals to ground (brake) |
| Duty cycle | 0 % to 100 % in steps of 1 % | share of the supply voltage applied to the motor; pulse width modulation at 20 kHz |

A new command takes effect at the motor terminals within 1 ms.

## Dynamic behavior

The bridge driver switches itself off on over-temperature and reports this as a fault
with the acknowledgement of the next command.
```

Notes:

- This source gives its elements and interfaces no identifiers, so `source_id` is the
  place in the document: here the chapter that defines the interface. A query then
  asks the source for identifiers.
- An interface may carry `fulfils` as well, when the delivery allocates a requirement
  to the interface rather than to an element.

## Stakeholder requirement

File: `spec/stakeholder/STK-0007.md`

```markdown
---
id: STK-0007
type: stakeholder-requirement
title: No trapping during automatic closing
status: draft
source_document: Front Door Module - Customer Requirements Specification, version 3.0
source_id: DM-CUS-017
imported:
  source: Front Door Module - Customer Requirements Specification
  version: "3.0"
  received: "2026-02-10"
  source_id: DM-CUS-017
---

## Statement

The window shall not trap body parts when it closes automatically.
```

Notes:

- `source_document` is always required for this type, imported or not. An `imported`
  block always names `source` and `version`; the check reports one that does not.
- With SYS.1 in scope the `imported` block is left out: the item is the team's own
  record of a received requirement, and `assessment`, `agreement` and
  `Assessment notes` are added as the team works on it. An imported one without
  `assessment` counts as accepted for rule COV-01.
- The statement is vague, and it stays vague. What "trap" means in newtons and
  millimetres is a query to the stakeholder, and the answer shows up in the system
  requirements, not in this item.
