# Unit test case item and its test function

File: `verification/unit/<ID>.md`. Attributes and sections are those of type `unit-test`
in `schema/items.yaml`; the layout is defined in `schema/item-format.md`. The item is the
specification. The C function named by `script` is its implementation and follows it.

## The item

```markdown
---
id: UT-0021
type: unit-test
title: "AntiPinch - an unconfirmed speed drop does not survive a stop"
status: draft
execution: automated
script: "tests/unit/test_AntiPinch.c::test_UT_0021_unconfirmed_drop_cleared_by_stop"
environment: host
asil: B
regression: true
links:
  verifies: ["UNT-0003#AntiPinch_Step"]
---

State transition MONITORING to IDLE while one drop cycle is counted, and the first drop
cycle of the next closing movement. Design basis: UNT-0003, Behavior, states MONITORING
and IDLE ("Entering IDLE clears reference, counters and target").

## Preconditions

Test program of unit AntiPinch (`tests/unit/test_AntiPinch.c` with
`src/antipinch/AntiPinch.c`); no stubs. A step is written as (position, speed, drive
direction); positions in counts of 0.5 mm, speeds in mm/s. "Monitoring at p / v" means
`AntiPinch_Init` followed by 20 steps (p, v, closing). The status is read with
`AntiPinch_GetStatus` after every step named.

## Steps

1. Monitoring at 600 / 150; 1 step (600, 129, closing).
2. 1 step (600, 129, stopped).
3. 20 steps (600, 129, closing).
4. 1 step (600, 108, closing).
5. 1 more step (600, 108, closing).

## Expected result

1. MONITORING, request FALSE: first cycle of a drop.
2. IDLE, request FALSE, reference speed 0.
3. MONITORING, request FALSE, reference speed 129.
4. MONITORING, request FALSE: the drop cycle counted before the stop is forgotten.
5. REVERSING, request TRUE.
```

How to fill it:

| Part | Rule |
|---|---|
| `title` | unit name, a dash, what is checked. It appears in matrices and in `impact` output |
| `execution` | `automated` for a test the runner executes. A case that cannot be automated on the host is discussed with the user before it is written |
| `script` | `<repository path>::<test function>`. Set it when the function exists: `check` reports `LINK` when the file or the function is missing. Required before approval when `execution` is `automated` |
| `environment` | the environment name the strategy uses, for example `host` |
| `asil` | the highest ASIL of the units in `verifies`; `COV-23` reports a lower one |
| `regression` | `true` unless the strategy gives a reason to leave a case out of the regression set |
| `links.verifies` | `<unit ID>#<function>` for every function whose behaviour the case checks. The trace check rejects an anchor that is not a designed function of that unit, and reports `COV-29` for a function of category `public`, `scheduled` or `callback` that no test case names. A function that is only called to set up or to read back is not listed |
| Text before the first heading | the kind of case (normal, boundary, error, transition, injected failure) and the design basis: unit, section or contract, and a requirement criterion where one fixes the values |
| `Preconditions` | the test program, the test doubles, the start state, and every term the steps use. Complete enough that the case does not depend on another case having run |
| `Steps` | numbered; concrete calls and values with units |
| `Expected result` | the same numbers as the steps; exact values, states and return values, each of them found in or calculated from the design. A short reason after a colon where the value is not obvious |

## The test function

```c
/* UT-0021: an unconfirmed speed drop does not survive a stop */
static void test_UT_0021_unconfirmed_drop_cleared_by_stop(void)
{
  /* Step 1: monitoring at 150 mm/s, then one cycle 21 mm/s below the reference. */
  start_monitoring(600u, 150u);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 129u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);

  /* Step 2: the drive stops before the drop is confirmed. */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 129u, ANTIPINCH_MOTION_STOPPED));
  ASSERT_DETECTOR(ANTIPINCH_STATE_IDLE, FALSE);
  ASSERT_REFERENCE(0u);

  /* Step 3: a new closing movement at 129 mm/s is monitored after 20 cycles. */
  TEST_ASSERT_EQUAL(0u, run_cycles(20u, 600u, 129u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  ASSERT_REFERENCE(129u);

  /* Step 4: its first drop cycle is a first cycle again ... */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 108u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);

  /* Step 5: ... and only the second one makes an obstacle. */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 108u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
}
```

and, in `main` of the same file:

```c
  TEST_RUN("UT-0021", test_UT_0021_unconfirmed_drop_cleared_by_stop);
  return TEST_EXIT_CODE();
```

`start_monitoring`, `run_cycles`, `ASSERT_DETECTOR` and `ASSERT_REFERENCE` are helpers of
`examples/power-window/tests/unit/test_AntiPinch.c`: they read the detector only through
`AntiPinch_GetStatus`, the designed read function.

## Conventions of the test code

These are the conventions of the example harness (`tests/unit/test_support.h`,
`tests/unit/run_tests.py`). The runner depends on the first four.

| Convention | Why |
|---|---|
| One file `tests/unit/test_<Unit>.c` per unit, built together with the one source file `<Unit>.c` found under `src/` | the runner builds one test program per test file and finds the unit by that name |
| One function `static void test_UT_<NNNN>_<words>(void)` per test case | the runner reads the test case IDs from these names; `script` points at the function |
| One `TEST_RUN("UT-<NNNN>", <function>)` per test case in `main`, and `return TEST_EXIT_CODE();` | prints one verdict line per case, `UT-0021 PASS` or `UT-0021 FAIL <file>:<line>`; the exit code is other than 0 when a case failed |
| A test function that exists but prints no `PASS` line counts as failed | a build error, a crash or a forgotten `TEST_RUN` cannot hide a case |
| Checks use `TEST_ASSERT(condition)` and `TEST_ASSERT_EQUAL(expected, actual)` (unsigned values up to 32 bits) | the first failed check ends the test function and its place is in the verdict line |
| Every test function sets up its own start state (initialisation function of the unit, reset of the test doubles) | the verdict does not depend on which cases ran before |
| One block per step of the item, with a comment that names the step | reviewer and reader can lay item and function side by side |
| Expected values are written as the literals of the item | a value computed in the test by the unit's own formula proves nothing |
| The unit is reached only through its designed functions | a test that reads or writes file-scope data tests the implementation, not the design; the unit sources get no test-only code |
| Services the unit calls are defined in the test file as test doubles that return prepared values and count their calls | this is how a failure of a called service is injected and how "was not called" is observed |
| Platform headers the unit includes have stand-ins under `tests/unit/host/` | test equipment, kept apart from product code |

A test double for a called service, as `tests/unit/test_WindowPos.c` of the example has it
for the capture service of UNT-0001:

```c
static HallCapture_SnapshotType stub_snapshot;
static Std_ReturnType stub_result = E_OK;
static unsigned int stub_calls = 0u;

Std_ReturnType HallCapture_GetSnapshot(HallCapture_SnapshotType *snapshot)
{
  stub_calls++;
  if ((stub_result == E_OK) && (snapshot != NULL_PTR))
  {
    *snapshot = stub_snapshot;
  }
  return stub_result;
}
```

Setting `stub_result` to `E_NOT_OK` injects the failure of the service; `stub_calls`
shows whether the unit asked for data at all. The double contains no logic of the unit
it replaces.

## When item and function disagree

The item rules. Correct the function, unless the item itself is wrong: then the item is
changed first, its approval becomes stale, and `/review` looks at it again before a run
with the changed case counts as evidence.

Every change to a test file shows in `check` as `COV-30` on each test case implemented
in that file, until a new run is recorded: the latest run stored a hash of the file as
it was.
