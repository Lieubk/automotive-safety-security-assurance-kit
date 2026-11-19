# Deriving system qualification test cases

File: `verification/system-qualification/<ID>.md`. Attributes and sections are those of
type `system-qualification-test` in `schema/items.yaml`.

## From requirement to case

Work requirement by requirement. For each one, build a row per verification criterion:

| Requirement | Criterion | Stimulus | Observed at | Expected | Case and step |
|---|---|---|---|---|---|
| SYR-0007 | 1: reaction within 100 ms of the request at 9 V and at 16 V supply | request on the bus at 9.0 V, then 16.0 V | output signal | change within 100 ms | SYQT-0007, steps 1 and 2 |
| SYR-0007 | 3: at -40 C the reaction is not slower than 150 ms | cold soak, then request | output signal | change within 150 ms | SYQT-0008, step 1 |

(The values are placeholders for the layout only.)

- The expected result is the criterion: its value with its tolerance, and the time by
  which it holds. Translate units once, in the case, so that a reviewer can recalculate.
- Every value comes from the system requirement. A value taken from the architecture, a
  design or from watching the system run is not a qualification criterion.
- Cover the operating conditions the requirement names: supply range, temperature,
  variants, modes, and the boundary and error conditions it states.
- One case per requirement is the usual grain; a requirement with many criteria, or with
  several operating conditions, may need several cases. `verifies` names every
  requirement whose criterion the case shows. `asil` is the highest ASIL among them.
- Stimulate at the interfaces the strategy names; observe outputs and named measurement
  points. If a criterion is about a quantity inside the system, observe it where the
  system publishes it (a diagnostic value, a bus signal).
- Where a criterion cannot be reached on the integrated system - the bench cannot
  produce the condition, a quantity cannot be measured without changing the system - the
  case says so in its text and names the method or level that shows the criterion (an
  analysis, a review, a test at another level, a test by the customer), and the strategy
  allows that. Say what can be shown, and raise it with the requirement's author if the
  criterion needs a different form.

## The item

```markdown
---
id: SYQT-0007
type: system-qualification-test
title: Reaction time over the supply range
status: draft
execution: manual
environment: system-bench
asil: B
regression: true
links:
  verifies: [SYR-0007]
---

Criteria 1 and 2 of SYR-0007. (Then what cannot be shown here, why, and where it is shown.)

## Preconditions

The test object and its configuration, the bench set-up, the variant, the start state,
the stimuli and the terms the steps use.

## Steps

1. Supply 9.0 V; send the request; log the output.
2. Supply 16.0 V; repeat.

## Expected result

1. Output changes within 100 ms of the request.
2. As step 1.
```

`execution: automated` needs `script` before approval, in the form
`<repository path>::<test name>`; a bench that reports its own results names its script
or procedure there, and the test name in its report carries the case ID. A manual case
has `Steps` a tester can follow without asking.

## Procedures

The procedure of a case lives with the bench or the vehicle test set-up, in the
repository or in the bench's own tool. It does what the item says, step by step, and
reports one verdict per case under a name that contains the case ID. The toolkit does
not write or run it.
