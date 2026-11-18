# Software integration test specification review checklist

Version 1. Applies to: `software-integration-test`, and the test code its `script` names.
Supports: SWE.5.BP3, SWE.5.BP5, SWE.5.BP6, SWE.5.BP7, SWE.5.BP8.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

Review the test cases with the architecture open beside them: the interfaces they
verify, the components that provide and use those interfaces, the architecture views,
and the integration strategy with its steps. Integration tests show that the parts work
together as the architecture says; what a single unit does was shown at unit level.

Test cases are written from the architecture and may be reviewed before any build
exists. Apply the parts that have something to look at:

- "Each test case" and "The set of test cases": always.
- "The test code behind a test case": once the test functions exist. An automated case
  needs `script` before approval, so a review that approves includes this part.
- "Builds and results": once a build record and a run on it are recorded.

A review record cites this checklist as `software-integration-test v1`, and a review
that approves needs a result for every check. A check of a part that has nothing to
look at yet is recorded as `not-applicable` with the reason - "no recorded build or run
yet" for every check of "Builds and results" - and never as passed.

A test case cannot be approved while an item it verifies is in draft or in review: the
record tool refuses, and `check` reports `UPSTREAM` on a test case approved earlier.

## Each test case

| ID | Check | How to check | Kind |
|---|---|---|---|
| SIT-01 | Mandatory attributes and sections for its state are present, values are allowed | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| SIT-02 | It verifies at least one component, interface or view that is still valid | `check`: no `COV-17` finding and no `LINK` finding about `verifies` on the item | script |
| SIT-03 | `step` names a step of the approved integration strategy | `check`: no `COV-37` finding on the item | script |
| SIT-04 | `asil` is not lower than the ASIL of any item verified | `check`: no `COV-23` finding on the item | script |
| SIT-05 | The case tests the interplay of parts - data passed across an interface, ranges and units, timing, order of calls, the propagation of an error - and not the inside of one unit | read `Steps` and `Expected result` beside the interface and the unit tests of the units involved | semantic |
| SIT-06 | Every expected value comes from an interface item (elements, ranges, `timeout_ms`, `invalid`, operations and their returns), from the `Dynamic behavior` of a component, or from a view; none is there only because the integrated code produces it | read the item beside the items it verifies; recalculate one value per case | semantic |
| SIT-07 | The build of its step contains every component the case needs; whatever is not integrated yet is stood in for by a double the step names | compare the components the case exercises with `integration_steps` of the strategy | semantic |
| SIT-08 | `Preconditions` give the step, the doubles and their prepared answers, the start state and every term the steps use; the case does not rely on another case having run | read the section | semantic |
| SIT-09 | `Steps` are numbered and concrete (calls, signal values with units, number of cycles); `Expected result` has an exact entry for every step | read both sections side by side | semantic |
| SIT-10 | `environment` and `regression` agree with the strategy; a case left out of the regression set has a reason | compare with the software integration plan | semantic |
| SIT-11 | `verifies` names every interface, component or view whose behaviour the case shows, and nothing it only passes through | read the case against its links | semantic |

## The set of test cases

| ID | Check | How to check | Kind |
|---|---|---|---|
| SIT-20 | Every software interface is verified by at least one case | `check`: no `COV-13` finding | script |
| SIT-21 | Every step of the strategy has at least one case | `check`: no `COV-37` finding on the plan | script |
| SIT-22 | For every interface: each data element or operation is exercised in its normal range, at the limits the interface states, and with the invalid value or the time-out where it states one; for an operation, each return value | walk `elements` and `operations` of each interface against the cases | semantic |
| SIT-23 | The sequences and state machines of the views are walked through across the components involved, including the error paths they show | walk each `sequence` and `state-machine` view against the cases | semantic |
| SIT-24 | Timing that the interfaces and the execution model state (periods, time-outs, order of entries in a task) is tested where the environment can show it, or the strategy assigns it to a step on the target | compare `period_ms`, `timeout_ms` and the `execution-model` view with the cases and the strategy | semantic |
| SIT-25 | Resource use that the resource summary sets objectives for is measured where the strategy plans it | compare the `resource-summary` view with the strategy and the cases | semantic |
| SIT-26 | The cases were compared with the current, approved architecture | `check`: no `SUSPECT` or `UPSTREAM` on the cases and no `COV-19` on the items they verify | script |
| SIT-27 | No case lacks a basis in the architecture, and no two cases check the same thing | read the set | semantic |
| SIT-28 | The reviewer did not write the test cases and is as independent as `conventions.review_independence` in `project.yaml` or `Responsibilities` of the strategy asks | ask who wrote and who reviews; compare | accountable |

## The test code behind a test case

| ID | Check | How to check | Kind |
|---|---|---|---|
| SIT-40 | `script` is set, and the file and the function it names exist | `check`: no `SCHEMA` finding about `script` and no `LINK` finding "script names ..." on the item | script |
| SIT-41 | The function does what the item says, step by step: same calls, same values, same order | read function and item side by side | semantic |
| SIT-42 | Every entry of `Expected result` is asserted; no check is commented out, widened to a range the item does not give, or placed where it cannot fail | read the function; count the checks against the entries | semantic |
| SIT-43 | The integrated components are built from their real sources, as the build of the step lists them; only the components the step names as doubles are replaced, and the sources contain no test switch | compare the build's `contents` and `doubles` with the files the test program is linked from | semantic |
| SIT-44 | A double has the signatures and types of the interface it stands for, returns prepared values and counts calls; it contains no logic of the component it replaces | read the doubles beside the interface items | semantic |
| SIT-45 | The test program reports one verdict per case, and a failed check cannot end in a pass | read `main` and the use of the assertion macros | semantic |

## Builds and results

| ID | Check | How to check | Kind |
|---|---|---|---|
| SIT-60 | Every step has a successful build that contains what the step integrates, made from the present code | `check`: no `COV-36` finding | script |
| SIT-61 | Every case has a verdict in the latest run on a build of its step; a `not-run` or `blocked` verdict carries a reason | `check`: no `COV-18` finding on the cases | script |
| SIT-62 | The latest run of each step names the latest build of that step, made from the run's item under test | `check`: no `COV-38` finding | script |
| SIT-63 | The run's `selection` and its `not-run` reasons agree with the regression rules of the strategy for what changed since the previous run | read `selection` and the reasons beside the strategy and `impact` of the changed items | semantic |
| SIT-64 | Every failed case has a problem report with an `affects` link, or a decision recorded for it | compare the failed verdicts with the `problem-report` items | semantic |
| SIT-65 | Cases not run and failures left open were accepted by the person the strategy names | ask who accepted them, and when | accountable |
