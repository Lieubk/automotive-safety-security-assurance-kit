# Deriving qualification test cases

File: `verification/software-qualification/<ID>.md`. Attributes and sections are those
of type `software-qualification-test` in `schema/items.yaml`.

## From requirement to case

Work requirement by requirement. For each one, build a row per verification criterion:

| Requirement | Criterion | Stimulus | Observed at | Expected | Case and step |
|---|---|---|---|---|---|
| SWR-0004 | 1: speed 129 mm/s after 1 s closing at 150 mm/s, 300 mm | Hall pulse train 3333 us, then 3870 us; switch CLOSE | detection status | request within 10 ms | SQT-0004, step 1 |
| SWR-0004 | 4: at 5.0 mm no request, at 5.5 mm request | cannot hold the opening while the speed drops in the integrated software | - | shown at 5.0 mm and 8.0 mm; boundary by UT-0016 | SQT-0004, step 4 |

- The expected result is the criterion: its value with its tolerance, and the time by
  which it holds. Translate units once, in the case ("129 mm/s: a pulse every 3870 us"),
  so that a reviewer can recalculate.
- Every value comes from the requirement. A value taken from the design (a constant of
  a unit) or from running the software is not a qualification criterion.
- Stimulate the inputs the strategy names; observe outputs and named measurement points.
  If a criterion is about a value inside the software, observe it where the software
  publishes it.
- One case per requirement is the usual grain; a requirement with many criteria may
  need several cases. `verifies` names every requirement whose criterion the case
  shows. `asil` is the highest ASIL among them.
- Where a criterion cannot be reached through the inputs - the integrated software never
  produces the input values, or two quantities come from the same stimulus - the case
  says so in its text, and either injects the value as the strategy allows or names the
  level that shows the criterion (for example a unit test by ID).
- Interactions inside the software (a stall supervision of another component, a filter
  time) can make a criterion unreachable in the form written. Say which one, show what
  can be shown, and raise it with the requirement's author if the criterion needs a
  different form.

## The item

```markdown
---
id: SQT-0004
type: software-qualification-test
title: Obstacle detection during closing
status: draft
execution: automated
script: tests/qualification/test_qualification.c::test_SQT_0004_detection
environment: software-in-the-loop
asil: B
regression: true
links:
  verifies: [SWR-0004]
---

Criteria 1 to 5 of SWR-0004. (Then what cannot be shown here, why, and where it is shown.)

## Preconditions

The test object, the environment, the stimuli and the terms the steps use.

## Steps

1. Referenced; CLOSE with pulses at 150 mm/s until the position is 600 (300.0 mm) or less; then pulses at 129 mm/s.
...

## Expected result

1. Reversal request set within 2 cycles (10 ms).
...
```

## The test program

In the example: `tests/qualification/test_qualification.c`, one function
`test_SQT_<NNNN>_<words>` per case and `TEST_RUN("SQT-<NNNN>", ...)` in `main`. The
helpers there show the pattern:
- time advances in 5 ms cycles; the 20 ms task follows every fourth;
- the Hall signal is a pulse train whose period the test sets (a signal generator,
  open loop);
- the switch request and a bridge driver fault are set through the platform double;
- results are read at the bridge output and through the read functions the interfaces
  define, and the movement command through the measurement access of MotorDrive.

A case run on a bench is written the same way as an item; its procedure lives with the
bench, and `script` names it there if the bench's report uses that name.
