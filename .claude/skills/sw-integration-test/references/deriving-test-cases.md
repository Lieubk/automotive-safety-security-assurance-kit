# Deriving integration test cases and writing their test code

File: `verification/software-integration/<ID>.md`. Attributes and sections are those of
type `software-integration-test` in `schema/items.yaml`. The item is the specification;
the C function named by `script` implements it.

## What an integration test is for

A unit test shows that one unit does what its design says. An integration test shows
that the parts, put together, pass the right things to each other at the right time:
the value, its unit and range, the invalid value, the time-out, the order within a
task, the reaction to an error the other side reports. Its basis is the architecture -
interfaces, the dynamic behaviour of components, views - not the unit designs.

## Where test cases come from

| Architecture item | What to derive | Example case |
|---|---|---|
| `software-interface` with `elements` | each element in its normal range, at `min` and `max`, with `invalid` and after `timeout_ms` where stated; values of different elements that belong together (same cycle) | SIT-0001: Hall edges with their time stamps give position and speed |
| `software-interface` with `operations` | each operation with valid arguments, each argument outside its range, every entry of `returns` | SIT-0005: every return value of the movement command |
| the `Description` of an interface | the stated error behaviour and constraints of use ("after E_NOT_OK the bridge is off and the command is repeated") | SIT-0007 |
| `Dynamic behavior` of a component | modes and their transitions as other components see them | SIT-0004: soft start seen at the bridge |
| `sequence` view | the sequence end to end, with the timing it states | SIT-0006: an obstacle reaches the bridge in the same cycle |
| `state-machine` view | states and transitions that involve more than one component | - |
| `execution-model` view | the order of entries in a task as far as it shows in data passed in one cycle; periods | SIT-0003 |
| `resource-summary` view | only where the environment can measure it; otherwise the strategy assigns it | - |

A case belongs to the first step whose build contains every component it exercises
(`step`). A component that is not integrated yet is played by the double the step
names. `verifies` lists the interfaces, components or views whose behaviour the case
shows; `asil` is the highest ASIL among them (a view has none).

Values come from the items: the range of an element, the return values of an
operation, a constant named in a component's behaviour, a criterion of the requirement
an interface was allocated from. Never from running the integrated code to see what it
does. Where the architecture leaves the result open, that is a question for the
architect, not an expected value.

## The item

```markdown
---
id: SIT-0003
type: software-integration-test
title: An obstacle reaches the motor actuation in the cycle it is detected
status: draft
execution: automated
script: tests/integration/test_detection.c::test_SIT_0003_detection_to_motor
environment: host
asil: B
regression: true
step: detection
links:
  verifies: [IFC-0002, IFC-0003, VIEW-0004]
---

Data flow within one cycle of the 5 ms task. Basis: IFC-0002 (consumers in the 5 ms task
see position and speed of the same cycle), IFC-0003 (MotorDrive reads the reversal
request in the cycle it changes), VIEW-0004 (order WindowPos, AntiPinch, MotorDrive).

## Preconditions

Test program of step detection, ... (what is built, which doubles, what a cycle is,
every term the steps use)

## Steps

1. Referenced; motor state closing; edges every 3333 us (150 mm/s) for 200 cycles.
2. Edges every 3870 us (129 mm/s); 1 cycle.
3. 1 more cycle.

## Expected result

1. AntiPinch state MONITORING; speed handed to MotorDrive 150; reversal request FALSE.
2. Speed handed to MotorDrive 129; reversal request FALSE: first cycle of the drop.
3. AntiPinch state REVERSING; the request handed to MotorDrive in this same cycle TRUE.
```

## The test program of a step

One file per step, `tests/integration/test_<step>.c` in the example, one function per
case named `test_SIT_<NNNN>_<words>`, one `TEST_RUN("SIT-<NNNN>", ...)` per case in
`main`, and the assertion header of the unit tests. The runner reads the case IDs from
the function names; a case that prints no `PASS` line counts as failed.

- **The platform double** plays the basic software: the task bodies of the execution
  model with the entries in the order the view states, the interrupt, the timers, the
  communication stack, the output drivers. It is the only place where the order of the
  entries is written down for the host, so it follows the view line by line, and the
  strategy says where the real configuration is checked against the view.
- **A component double** has the functions of the component's header, publishes values
  the test prepares and records what it is handed. It contains no logic of the
  component. A component that only consumes needs a double that does nothing.
- **The test drives time**: it sets the timer, delivers interrupts with their time
  stamps, and runs the tasks. It reaches the integrated components only through their
  interfaces and through the platform double, never through file-scope data.
- **Expected values are literals** from the item.

In the example: `tests/integration/doubles/Platform_double.c` (the platform, with the
task bodies of VIEW-0004), `MotorDrive_double.c`, `WindowCmd_double.c`;
`tests/integration/test_detection.c` and `test_application.c`.

## When item and function disagree

The item rules. Correct the function, unless the item is wrong: then the item changes
first, its approval becomes stale, and `/review` looks at it again before a run with the
changed case counts.
