# Software interface item

File: `spec/software/architecture/<ID>.md`. Attributes and sections are those of type
`software-interface` in `schema/items.yaml`; the record keys of `elements` and
`operations` are those of the structures `data-elements` and `operations`. The two
examples are IFC-0002 and IFC-0008 of `examples/power-window`, as drafts.

## Data-oriented interface: `elements`

```markdown
---
id: IFC-0002
type: software-interface
title: Window motion
status: draft
asil: B
security_relevant: false
kind: sender-receiver
provided_by: CMP-0003
used_by: [CMP-0002, CMP-0004, CMP-0005]
elements:
  - {name: position, direction: out, type: uint16, unit: mm, min: 0, max: 480, resolution: 0.5, initial: 65535, invalid: 65535, period_ms: 5, description: "window opening measured from the fully closed end stop; transported as raw value 0..960 in counts of 0.5 mm; initial and invalid are raw values and mean: not referenced since reset"}
  - {name: speed, direction: out, type: uint16, unit: mm/s, min: 0, max: 500, resolution: 1, initial: 0, period_ms: 5, description: "speed of the glass without sign; 0 below 10 mm/s; faster pulse trains are reported as 500; has no invalid value"}
---

## Description

Position and speed of the glass for every component that needs them. Both elements are
updated together, once per 5 ms cycle, by `WindowPos_Step`, and read through
`WindowPos_GetPosition` and `WindowPos_GetSpeed`.

- Consumers in the 5 ms task run after the provider and see the values of the same
  cycle. The consumer in the 20 ms task sees the values of the last completed 5 ms
  cycle; tasks do not preempt each other, so position and speed always belong together.
- The position is "not referenced" from reset until the window has rested on the fully
  open end stop (SWR-0002). `WindowPos_GetPosition` then returns `E_NOT_OK` and the
  invalid value. Each consumer states what it does in this case: AntiPinch treats the
  whole travel as protected zone, WindowCmd refuses automatic closing.
- The speed carries no direction. The direction of the movement is the applied
  direction of IFC-0005.
- No time-out supervision: provider and consumers run in the same control unit and the
  values are read by function call.
```

## Operation-oriented interface: `operations`

```markdown
---
id: IFC-0008
type: software-interface
title: Bridge output
status: draft
asil: B
security_relevant: false
kind: function-call
provided_by: CMP-0006
used_by: [CMP-0005]
operations:
  - name: BridgeOutput_Set
    description: "writes direction and duty cycle to the bridge driver"
    arguments:
      - {name: direction, direction: in, type: uint8, min: 0, max: 2, description: "0 off (motor terminals to ground), 1 opening, 2 closing"}
      - {name: duty_percent, direction: in, type: uint8, unit: "%", min: 0, max: 100, resolution: 1, description: "share of the supply voltage applied to the motor; ignored for off"}
    returns:
      - {type: Std_ReturnType, value: E_OK, meaning: "the outputs are set; effective at the motor terminals within 1 ms"}
      - {type: Std_ReturnType, value: E_NOT_OK, meaning: "an argument is out of range or the bridge driver reports a fault; the bridge is off"}
    call_context: task
    reentrant: false
    blocking: false
links:
  realizes: [SYI-0002]
---

## Description

The software side of the motor command (SYI-0002), provided by the output driver of
the basic software. MotorDrive is its only user and calls it once per 5 ms cycle, with
the complete command, also when nothing has changed.

Error behavior: after `E_NOT_OK` the bridge is off. MotorDrive publishes "stopped" on
IFC-0005 and repeats the command in the next cycle. The fault itself is stored by the
basic software; the application does not handle it further.

The operation name is the one of the customer's basic software release named in
CMP-0006.
```

## What is needed when

| Attribute or section | Needed | What to write |
|---|---|---|
| `id`, `type`, `title`, `status` | always | `title`: what is exchanged, not who exchanges it |
| `asil`, `security_relevant` | before review | at least the ASIL of the most critical use of the data or operation |
| `kind` | before review | see the table below |
| `provided_by` | before review | the one component that owns the interface |
| `elements` | before review for `sender-receiver`, `mode-switch`, `parameter`, `non-volatile-data` | one record per data element |
| `operations` | before review for `client-server`, `function-call` | one record per operation |
| `Description` | before review | purpose, guarantees, error behaviour, constraints on use |
| `used_by` | before approval | every component that reads the data or calls the operation |
| `links.realizes` | when the interface carries the software side of a `system-interface` | that system interface |
| `links.fulfils` | when a requirement is allocated to the interface | the software requirements the interface is responsible for, usually of `kind: interface` |

`provided_by` and `used_by` are attributes of the interface, and the trace commands
follow them. `python tools/traceability.py show <interface ID>` lists the components
that use the interface, and `impact <interface ID>` adds the units and views that depend
on it. `show <component ID>` lists the interfaces a component provides (`provided_by`)
and the interfaces it uses (`uses`).

## Choosing `kind`

| `kind` | Use for | Filled |
|---|---|---|
| `sender-receiver` | data one component publishes and others read | `elements` |
| `client-server` | an operation one component offers to others, with arguments and a result | `operations` |
| `mode-switch` | a mode that one component manages and others have to follow | `elements`: the mode, with its values in `description` |
| `parameter` | calibration or coding data that components read and do not change | `elements` |
| `non-volatile-data` | data that survives a reset or power-off | `elements` |
| `trigger` | an event that activates the user, without data | `Description`; `elements` only if a value travels with the event |
| `function-call` | a C function called directly across the boundary to basic software or a driver: a service, a callback, a notification from an interrupt | `operations` |
| `debug` | measurement, trace or calibration access for development | whichever fits; say in which builds it exists |
| `other` | anything else, with the reason in `Description` | whichever fits |

## A complete data element

| Key | Rule |
|---|---|
| `name` | the name used in code or model |
| `direction` | `in`, `out` or `inout`, seen from the providing component: `out` is written by the provider |
| `type` | the type as implemented (`uint16`, `boolean`, a named type) |
| `unit`, `min`, `max`, `resolution` | given for every physical quantity; for a coded value, `min` and `max` of the code and the meaning of each code in `description` |
| `initial` | the value from start-up until the first update |
| `invalid` | the value that means "not available", or a sentence in `description` that there is none |
| `period_ms` | how often the provider updates it; left out for event-driven data, with the event named in `Description` |
| `timeout_ms` | after which time without update the data counts as lost; left out when loss is impossible, with the reason in `Description` |
| `description` | meaning, scaling between raw and physical value, coding of enumerations |

Quote values that YAML would read as something else: `initial: "FALSE"`, `unit: "%"`.

## A complete operation

| Key | Rule |
|---|---|
| `name` | the function or operation name as it will be called |
| `description` | what the operation does for its caller, in one sentence |
| `arguments` | a list of data element records; every argument has `name`, `direction`, `type`, and range and unit where it is a quantity |
| `returns` | one `{type, value, meaning}` record per result the caller can tell apart: success and every failure. An operation that returns nothing leaves `returns` out, or says so in one record (`{type: void, meaning: "no return value"}`, as IFC-0001 of the example does) |
| `call_context` | `task`, `interrupt` or `both`: where it may be called from |
| `reentrant` | `true` only if concurrent calls are allowed |
| `blocking` | `true` if the call can wait for something; then `Description` gives the longest wait |

## The `Description` section

A reader who implements one side must find here everything the structured part cannot
say:

- what the interface is for, and which elements or operations belong together;
- what a user may rely on: age of the data seen by each user, consistency between
  elements, the order of calls, effects that outlast the call;
- error behaviour of both sides: what the provider delivers when it has no valid value
  or gets an invalid argument, and what each user does with an invalid value, a
  time-out or a failed call. "No substitute value" is a valid answer if it is stated;
- constraints on use: from which task or interrupt, not before which initialisation,
  how often, by whom;
- what is deliberately absent, with the reason (no time-out supervision, no invalid
  value).

Test of completeness: provider and user could be written by two people who never talk
to each other, and a software integration test could be derived from the item alone.

## Notes

- One interface per subject, not one per connection: three users of the window motion
  are three entries in `used_by`, not three interfaces.
- An interface between supplied software and a developed component is defined to the
  same depth as one between two developed components. Names come from the supplied
  release; say so, as IFC-0008 does.
- Where the interfaces are defined in an AUTOSAR model, take names, types and ranges
  from the port interface definitions as they are, and add what the model does not
  hold: meaning, validity, error behaviour, constraints. Where item and model disagree,
  the model is right and the item is corrected.
- A requirement of `kind: interface` is allocated to the interface that fulfils it, with
  `fulfils` on the interface item. The interface then carries at least the ASIL of that
  requirement (`COV-23`).
- An interface that is withdrawn or replaced is not deleted. Move `used_by`, `realizes`
  and `shows` references to its successor first: `LINK` and `COV-24` report every link
  from a live item to an obsolete one.
