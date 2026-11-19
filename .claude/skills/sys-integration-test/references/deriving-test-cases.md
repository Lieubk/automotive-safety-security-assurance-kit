# Deriving system integration test cases and their bench procedures

File: `verification/system-integration/<ID>.md`. Attributes and sections are those of
type `system-integration-test` in `schema/items.yaml`. The item is the specification;
the bench procedure named by `script` (or the manual instruction) implements it.

## What a system integration test is for

A system qualification test shows that the integrated system meets the system
requirements. An integration test shows something earlier and narrower: that the
elements, put together, work together as the architecture says. Four questions cover
most of it:

- does each signal reach the elements that need it,
- does it arrive in time, and in the right relation in time to other signals,
- do all users of an interface read it in the same way (value, unit, scaling, byte
  order, resolution),
- do the elements behave correctly together over time, in start-up, in operation and
  after a failure.

Its basis is the system architecture - interfaces, element behaviour, views - not the
system requirements; those are the basis of `/sys-qualification-test`.

## Where test cases come from

| Architecture item | What to derive | Example case |
|---|---|---|
| `system-interface` of kind `bus` | each signal in its normal range, at the limits and with the invalid or "not available" value the definition states; cycle time and time-out; the reaction of the receiver to a missing message | SYIT-0001: the window command message reaches the control unit with the stated cycle time |
| `system-interface` of kind `electrical` | levels, thresholds, load and supply conditions the definition states; behaviour at an open or shorted line where the definition says what shall happen | SYIT-0004 |
| `system-interface` of kind `hardware-software` | each signal or register the software reads or writes: range, scaling, resolution, sampling time, and the value the software sees for a given physical input | SYIT-0003: a given sensor frequency becomes the position the software reports |
| `system-interface` of kind `mechanical` or `diagnostic`, or `external` | fit, force, travel, or the services and responses the definition lists; what the other side sends and expects | - |
| `Definition` of an interface | timing, protocol and error behaviour it states ("after a lost message the last value is held for 100 ms") | SYIT-0006 |
| `Dynamic behavior` of an element | modes and transitions as the other elements see them: start-up, shut-down, sleep, wake-up | SYIT-0007 |
| `sequence` view | the sequence end to end across the elements, with the timing it states | SYIT-0008: command to motor movement within the time the chain allows |
| `state-machine` view | states and transitions that involve more than one element | - |
| `fault-reaction` view | each fault of the table, injected on the bench, and the reaction of every element involved | SYIT-0009 |
| `communication` view | message set, cycle times, bus load, as far as the bench can measure them | - |
| `resource-summary` view | only where the bench can measure it (current, supply, thermal); otherwise the strategy assigns it | - |

Write timing as a number with its unit and tolerance taken from the item. Where a
physical quantity has to be set, give the quantity and the means ("the rest-bus
simulation sends ...", "the Hall emulator delivers 150 pulses per second").

A case belongs to the first step whose build contains every element it exercises
(`step`). An element not integrated yet is played by the double the step names. A
neighbouring system (external element) is always simulated, and the case says which
simulation. `verifies` lists the interfaces, elements or views whose behaviour the case
shows; `asil` is the highest ASIL among them (a view has none).

Values come from the items: the range and scaling of a signal, the time-out of a
message, a threshold named in an element's behaviour, a criterion of the requirement an
interface was allocated from. Never from measuring a sample to see what it does. Where
the architecture leaves the result open, that is a question for the architect, not an
expected value.

## The item

```markdown
---
id: SYIT-0003
type: system-integration-test
title: A sensor frequency of 150 Hz is read as 150 mm/s by the software
status: draft
execution: automated
script: bench/procedures/syit_0003_hall_to_speed.py
environment: bench-electronics
asil: B
regression: true
step: software
links:
  verifies: [SYI-0002, SYE-0002, SYE-0005]
---

Signal path from the Hall input to the speed value in the software. Basis: SYI-0002
(Definition: pulse frequency 0 to 1000 Hz, 1 Hz = 1 mm/s, valid after the first
edge), SYE-0005 (Dynamic behavior: speed available after two edges).

## Preconditions

Step software; bench-electronics with the Hall emulator on the sensor input and the rest-bus
simulation for SYE-0003; control unit in mode OPERATION, no fault active; measurement
of the software's speed value by the diagnostic read-out.

## Steps

1. The Hall emulator delivers 150 Hz for 1 s.
2. The Hall emulator delivers 1000 Hz for 1 s.
3. The Hall emulator stops delivering pulses and waits 200 ms.

## Expected result

1. The speed value reads 150 mm/s within the tolerance the interface states.
2. The speed value reads 1000 mm/s.
3. The speed value is marked invalid after the time-out the definition gives.
```

## The bench procedure of a case

How the bench is driven is the project's decision (a script on a test system, a
sequence file, a manual instruction). What the toolkit needs:

- **One verdict per case**, reported under the case ID. The ID appears in the name of
  the test in the bench's report, or in `test` of a result file; a case the report does
  not name has no result.
- **Expected values are literals** from the item, not read back from the sample.
- **The stimulus and the measurement are named** in the procedure: which simulation
  or emulator, which channel, which read-out. The configuration of the bench is part of
  the record (`--environment`) and of the manifest of the build (`tool`).
- **A case sets its own preconditions** or says in `Preconditions` which state the
  bench has; it does not rely on another case having run.
- **A manual case** is written so that another person gets the same verdict; the
  operator and the date reach the record through the bench's report.

## When item and procedure disagree

The item rules. Correct the procedure, unless the item is wrong: then the item changes
first, its approval becomes stale, and `/review` looks at it again before a run with the
changed case counts.
