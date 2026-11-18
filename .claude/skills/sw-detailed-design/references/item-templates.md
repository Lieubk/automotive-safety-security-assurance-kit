# Detailed design items

Files: `spec/software/design/<ID>.md` for `component-design` (prefix CDS) and
`software-unit` (prefix UNT), `spec/decisions/<ID>.md` for `design-decision` (prefix
ADR). Attributes, sections and structures are those of `schema/items.yaml`; the layout
is defined in `schema/item-format.md`. The examples below are shortened from the worked
example; the full items are in `examples/power-window/spec/software/design/`.

## Component design

One per developed component. It holds what belongs to the component as a whole and to
no single unit.

```markdown
---
id: CDS-0002
type: component-design
title: Detailed design of AntiPinch
status: draft
links:
  refines: [CMP-0004]
---

## Design concept

One unit, AntiPinch (UNT-0003), built as a state machine with four states that is
stepped once per 5 ms cycle. It has no dependency: position, speed and drive direction
of the cycle are the three arguments of the step function, the result is read as one
record.

Decisions taken here:

- **Speed drop against a reference of its own.** The unit compares the speed with a
  low-pass filtered copy of it. Slow changes move the reference along and are not
  obstacles; a fall faster than the filter can follow is one.
- **Fail to "open".** Arguments outside their range during closing start a reversal
  that is limited by time only (SWR-0006).

## Static structure

| Unit | Files | Visible to other components | Uses |
|---|---|---|---|
| UNT-0003 AntiPinch | `src/antipinch/AntiPinch.h`, `.c` | `AntiPinch_Init`, `AntiPinch_Step`, `AntiPinch_GetStatus` (IFC-0003) | IFC-0002, IFC-0005 as arguments |

Eight file-local functions carry one state or one transition each; all data is
file-local. The unit includes `Std_Types.h` only.

## Dynamic behavior

The component is its unit; the state machine with every transition is in UNT-0003.
Seen from outside:

- `AntiPinch_Step` is called once per 5 ms cycle, after `WindowPos_Step` and before
  `MotorDrive_Step` (VIEW-0004).
- `AntiPinch_GetStatus` is called by MotorDrive in the same cycle and by WindowCmd in
  the 20 ms task. Tasks do not preempt each other, so nothing needs protection.

## Design evaluation

Limits as in CDS-0001.

| Aspect | Result |
|---|---|
| Interaction | Two functions called by others, no call to any other unit, no shared data. |
| Interoperability | Depends on `Std_Types.h` only. Repeats the value ranges of two interfaces as constants; a change of IFC-0002 or IFC-0005 has to be followed here by hand. |
| Criticality | ASIL B, the unit that decides whether the window reverses. Full unit verification of the project; in addition every comparison limit has a unit test on both sides. |
| Technical complexity | Highest cyclomatic complexity 6 (`AntiPinch_StepMonitoring`), nesting depth at most 3, at most 3 parameters. Within the limits. |
| Testability | No stub needed. Every state is reachable by argument sequences, every output is in the status record. Time is counted in calls. |
| Risks | See below. |

| Risk | Effect | Measure | Owner |
|---|---|---|---|
| Thresholds come from the system analysis of the customer and are not confirmed on a door | false reversals or forces above the limit of SYR-0001 | constants in one place in the header; values confirmed or changed by change request after the customer's force measurements | software project lead |
```

Notes:

- `Design concept`: the approach, why it was chosen, the constraints it obeys, the
  assumptions it makes. Choices without a real alternative are listed as "Decisions
  taken here"; a choice between real alternatives is a `design-decision` and is
  referred to by ID.
- `Static structure`: every unit of the component with its files, what other
  components may call, and what it uses. With more than one unit add a diagram of who
  calls whom (CDS-0001). The table must agree with the `part_of`, `realizes` and
  `uses` links of the units. For a unit that has no code yet, the `Files` column is
  where its file names are decided.
- `Dynamic behavior`: see `designing-units.md`.
- `Design evaluation`: see `design-evaluation.md`. The schema asks for the section
  only before approval; write it before the review all the same, because the review
  is where it is judged.

## Software unit

```markdown
---
id: UNT-0001
type: software-unit
title: HallCapture - capture of the Hall sensor edges
status: draft
asil: B
security_relevant: false
origin: handwritten
resource_budget: {rom_bytes: 512, ram_bytes: 16, stack_bytes: 32, wcet_us: 10}
platform:
  exclusive_areas:
    - "HallData: locks Isr_HallCapture; entered and left by HallCapture_GetSnapshot through SchM_Enter_WindowPos_HallData and SchM_Exit_WindowPos_HallData (header SchM_WindowPos.h of the basic software)"
  interrupts:
    - "Isr_HallCapture calls HallCapture_OnEdge (VIEW-0004)"
functions:
  - name: HallCapture_Init
    category: public
    call_context: task
    reentrant: false
    arguments: []
    returns:
      - {type: void, meaning: "no return value"}
    preconditions:
      - "Isr_HallCapture is disabled"
    postconditions:
      - "pulse counter, rejected counter, last edge time and period are 0"
      - "the next edge is treated as the first edge"
    errors: []
  - name: HallCapture_OnEdge
    category: callback
    trigger: "rising edge of the Hall sensor signal (IFC-0001)"
    call_context: interrupt
    reentrant: false
    arguments:
      - {name: timestamp_us, direction: in, type: uint32, unit: us, min: 0, max: 4294967295, resolution: 1, description: "capture time of the edge, free running, wraps at 2^32"}
    returns:
      - {type: void, meaning: "no return value"}
    preconditions:
      - "HallCapture_Init has run"
      - "called from Isr_HallCapture only, never nested"
    postconditions:
      - "accepted edge: pulse counter incremented modulo 65536, last edge time = timestamp_us, period = interval to the previous accepted edge (unchanged for the first edge)"
      - "rejected edge: rejected counter incremented up to 65535, nothing else changed"
    errors:
      - {condition: "interval to the last accepted edge below 400 us (modulo 2^32)", reaction: "edge rejected and counted; no report to the caller"}
  - name: HallCapture_GetSnapshot
    category: public
    call_context: task
    reentrant: false
    arguments:
      - {name: snapshot, direction: out, type: "HallCapture_SnapshotType *", description: "receives pulse_count, rejected_count, last_edge_us and period_us as they were at one instant"}
    returns:
      - {type: Std_ReturnType, value: E_OK, meaning: "the snapshot was written"}
      - {type: Std_ReturnType, value: E_NOT_OK, meaning: "snapshot is a null pointer"}
    preconditions:
      - "HallCapture_Init has run"
      - "called at task level, not from Isr_HallCapture"
    postconditions:
      - "E_OK: all four members of *snapshot are written; exclusive area HallData was entered once and left again"
      - "the capture data itself is unchanged"
    errors:
      - {condition: "snapshot is a null pointer", reaction: "returns E_NOT_OK, writes nothing, does not enter the exclusive area"}
data:
  - {name: HallCapture_PulseCount, type: uint16, scope: file, unit: pulses, min: 0, max: 65535, initial: 0, protection: "exclusive area HallData; written in Isr_HallCapture"}
  - {name: HallCapture_EdgeSeen, type: boolean, scope: file, initial: "FALSE", protection: "none needed: read and written in Isr_HallCapture only, cleared by HallCapture_Init while the interrupt is disabled"}
links:
  part_of: [CMP-0003]
  realizes: [IFC-0001]
  implements: [SWR-0001]
---

## Purpose

Turns the edges of the Hall sensor signal into three numbers the rest of the component
can work with at task level: how many pulses were accepted, when the last one came,
and how far apart the last two were. It is the only code of the component that runs at
interrupt level.

## Behavior

Constants:

| Name | Value | Meaning |
|---|---|---|
| `HALLCAPTURE_MIN_INTERVAL_US` | 400 us | shortest interval between two accepted edges |

`HallCapture_OnEdge(timestamp_us)`:

1. First edge since initialisation: accept it. Store the time stamp and increment the
   pulse counter. The period stays 0.
2. Any later edge: interval = `timestamp_us` minus the stored time stamp, as unsigned
   32 bit subtraction. Below 400 us: reject and count. Otherwise accept: period =
   interval, store the time stamp, increment the pulse counter (65535 is followed by 0).

## Error handling

| Error | Detected by | Reaction | Reported |
|---|---|---|---|
| Edge too close to the previous one | `HallCapture_OnEdge`, interval check | edge ignored for count and period | `rejected_count` in the snapshot |
| Null pointer | `HallCapture_GetSnapshot` | nothing written, exclusive area not entered | return value `E_NOT_OK` |

Not detectable here: edges that are never delivered.

## Dynamic behavior

Two contexts: `HallCapture_OnEdge` in `Isr_HallCapture`, `HallCapture_GetSnapshot` in
`OsTask_Control_5ms`. The interrupt can interrupt the task at any point except inside
the exclusive area. The exclusive area is held for four assignments.

## Design notes

- The pulse counter wraps on purpose. Its user takes differences modulo 65536.
```

Notes:

- `title`: the C module name, a dash, what the unit is. `asil`, `security_relevant`,
  `origin` and `functions` are required before review.
- `source_files` is not in the draft of a new unit: it lists files that exist. The
  files the unit will consist of are named in `Static structure` of the component
  design; `/sw-unit-implement` creates exactly these and adds `source_files` to the
  unit, which does not change its content hash or its approval. The approved UNT-0001
  of the worked example carries
  `source_files: [src/windowpos/HallCapture.h, src/windowpos/HallCapture.c]` because
  its code exists.
- `origin`: `handwritten`, `generated` (then `generated_from` names the model or
  configuration), `reused` or `third-party`. A unit that is not handwritten still has
  `functions` for what others call, but its behaviour is described by its source.
- `resource_budget`: objectives, not measurements, inside the budget of the component.
  Leave it out when the component's budget needs no split.
- `platform`: only the keys the unit needs, each a list of one-line statements. Keys
  and their content: `autosar-classic.md`.
- `functions`, `data`: key by key in `designing-units.md`. Flow style (`{...}`) for
  arguments and data keeps one element on one line; quote every text that holds `:`,
  `*` or `#`. Every argument has a `type`, and every `returns` entry of a function the
  same `type`: these are compared with the code (`COV-22`).
- `links`: `part_of` exactly one component; `realizes` and `uses` may name interfaces,
  `uses` also other units; `implements` names requirements. With several units in a
  component, `implements` says which unit fulfils which requirement; with a single
  unit the path through the component already says it and the link is optional.
- `Design notes` is optional. Leave it out when there is nothing to note.
- An item that applies only to some product variants carries `variants: [...]`.

## Design decision at detailed-design level

Write one when the design chooses between alternatives that differ in something others
care about: an algorithm, a number representation, a protection mechanism, a cut
between units. The example is an illustration and not part of the worked example.

```markdown
---
id: ADR-0002
type: design-decision
title: Consistent read of the pulse data - exclusive area or repeated read
status: draft
level: detailed-design
links:
  concerns: [CDS-0001, UNT-0001]
---

## Context

The capture interrupt writes four values that the 5 ms task has to read as they were
at one instant (CDS-0001). The interrupt may be locked for 5 us at most (VIEW-0004).

## Evaluation criteria

1. Time for which the capture interrupt is locked.
2. Upper bound of the execution time of the read at task level.
3. Testability on a host.
4. What the basic software has to provide.

## Alternatives

**A - Exclusive area.** The task copies the four values inside an exclusive area that
locks the interrupt.

**B - Repeated read.** The task reads the values, reads the pulse counter again and
repeats until it has not changed.

| Criterion | A - exclusive area | B - repeated read |
|---|---|---|
| 1 Interrupt lock | four assignments, well below 5 us | none |
| 2 Bound of the read | fixed | depends on the pulse rate; needs a retry limit and a reaction when it is hit |
| 3 Testability | enter and exit are counted by a stub | the retry path needs an edge injected between two reads |
| 4 Basic software | one exclusive area to configure | nothing |

## Decision

Alternative A: the lock is far inside its budget, and B adds a path that can fail.

## Consequences

- UNT-0001 names the exclusive area in `platform`; the customer configures it.
- The lock time has to be measured on the door module.
```

Notes:

- `level: detailed-design`; `concerns` names the component designs and units the
  decision shapes. The engine accepts an approved decision that concerns an item as
  the waiver for a lower ASIL (`COV-23`); such a decision documents the decomposition.
- Every alternative is assessed against every criterion, including the one that lost.
- `Decision` and `Consequences` are required before approval. The decision is taken
  by the user; write into `Decision` what they decided and why, not what you prefer.
