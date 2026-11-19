# System integration test specification review checklist

Version 1. Applies to: `system-integration-test`, and the bench procedure its `script`
names. Supports: SYS.4.BP3, SYS.4.BP5, SYS.4.BP6, SYS.4.BP7, SYS.4.BP8.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

Review the test cases with the system architecture open beside them: the system
interfaces they verify, the system elements that provide and use those interfaces, the
system-level views, and the system integration strategy with its steps. Integration
tests show that the elements work together as the architecture says; whether the system
meets the system requirements is shown by the qualification tests.

Test cases are written from the architecture and may be reviewed before any build
exists. Apply the parts that have something to look at:

- "Each test case" and "The set of test cases": always.
- "The bench procedure behind a test case": once the procedures exist. An automated case
  needs `script` before approval, so a review that approves includes this part.
- "Builds and results": once a system build record and a run on it are recorded.

A review record cites this checklist as `system-integration-test v1`, and a review that
approves needs a result for every check. A check of a part that has nothing to look at
yet is recorded as `not-applicable` with the reason - "no recorded build or run yet" for
every check of "Builds and results" - and never as passed.

A test case cannot be approved while an item it verifies is in draft or in review: the
record tool refuses, and `check` reports `UPSTREAM` on a test case approved earlier.

## Each test case

| ID | Check | How to check | Kind |
|---|---|---|---|
| SIN-01 | Mandatory attributes and sections for its state are present, values are allowed | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| SIN-02 | It verifies at least one system element, system interface or system-level view that is still valid | `check`: no `COV-17` finding and no `LINK` finding about `verifies` on the item | script |
| SIN-03 | `step` names a step of the approved system integration strategy | `check`: no `COV-48` finding on the item | script |
| SIN-04 | `asil` is not lower than the ASIL of any item verified | `check`: no `COV-23` finding on the item | script |
| SIN-05 | The case tests the interplay of elements - signals across an interface, ranges, units and scaling, timing, order, the propagation of a fault - and not the inside of one element | read `Steps` and `Expected result` beside the interface and the element | semantic |
| SIN-06 | Every expected value comes from a system interface (`Definition`: signals, ranges, units, timing, protocol), from the `Dynamic behavior` of an element, or from a view; none is there only because a sample produced it | read the item beside the items it verifies; recalculate one value per case | semantic |
| SIN-07 | The configuration of its step contains every element the case needs; whatever is not integrated yet, and every external element, is stood in for by a simulation or double the step names | compare the elements the case exercises with `integration_steps` of the strategy | semantic |
| SIN-08 | `Preconditions` give the step, the bench and its simulations, the start state of the system and every term the steps use; the case does not rely on another case having run | read the section | semantic |
| SIN-09 | `Steps` are numbered and concrete (stimulus with value, unit and duration; the measurement and its tolerance); `Expected result` has an exact entry for every step | read both sections side by side | semantic |
| SIN-10 | `environment` and `regression` agree with the strategy; a case left out of the regression set has a reason | compare with the system integration plan | semantic |
| SIN-11 | `verifies` names every interface, element or view whose behaviour the case shows, and nothing it only passes through | read the case against its links | semantic |

## The set of test cases

| ID | Check | How to check | Kind |
|---|---|---|---|
| SIN-20 | Every system interface is verified by at least one case | `check`: no `COV-15` finding | script |
| SIN-21 | Every step of the strategy has at least one case | `check`: no `COV-48` finding on the plan | script |
| SIN-22 | For every interface: each signal or service is exercised in its normal range, at the limits the definition states, with the invalid or "not available" value, and with the time-out or loss of the message where it states one | walk the `Definition` of each interface against the cases | semantic |
| SIN-23 | The cases probe the four things an integration test shows: that each signal reaches its receivers, that it arrives in time and in the stated relation to other signals, that all users read it alike, and that the elements behave together over time | walk the interfaces and the cases and name which case covers which | semantic |
| SIN-24 | The sequences, state machines and fault reactions of the views are walked through across the elements involved, including the fault paths they show | walk each `sequence`, `state-machine` and `fault-reaction` view against the cases | semantic |
| SIN-25 | Timing that the interfaces and views state (cycle times, time-outs, reaction times) is tested where the bench can measure it, or the strategy assigns it to a step on another bench or to the vehicle | compare the timing stated in the items with the cases and the strategy | semantic |
| SIN-26 | The cases were compared with the current, approved architecture | `check`: no `SUSPECT` or `UPSTREAM` on the cases and no `COV-19` on the items they verify | script |
| SIN-27 | No case lacks a basis in the architecture, and no two cases check the same thing | read the set | semantic |
| SIN-28 | The reviewer did not write the test cases and is as independent as `conventions.review_independence` in `project.yaml` or `Responsibilities` of the strategy asks | ask who wrote and who reviews; compare | accountable |

## The bench procedure behind a test case

| ID | Check | How to check | Kind |
|---|---|---|---|
| SIN-40 | `script` is set for an automated case, and the file or sequence it names exists; a manual case has a written instruction another person can follow | `check`: no `SCHEMA` finding about `script` and no `LINK` finding "script names ..." on the item; read the instruction | script |
| SIN-41 | The procedure does what the item says, step by step: same stimulus, same values, same order | read procedure and item side by side | semantic |
| SIN-42 | Every entry of `Expected result` is checked; no check is disabled, widened to a tolerance the item does not give, or placed where it cannot fail | read the procedure; count the checks against the entries | semantic |
| SIN-43 | The simulations and emulations represent the external and not yet integrated elements as their interfaces define them, and contain no behaviour the item does not state | read the simulation setup beside the interface items | semantic |
| SIN-44 | The bench reports one verdict per case under the case ID, and a failed check cannot end in a pass | read the procedure and one report | semantic |
| SIN-45 | The bench, its measurement chain and its calibration are identified, and fit the tolerance the cases demand | ask who runs the bench; read the setup record | accountable |

## Builds and results

| ID | Check | How to check | Kind |
|---|---|---|---|
| SIN-60 | Every step has a successful system build that contains the elements the step integrates, and the software build it names is the latest of the last software integration step | `check`: no `COV-47` finding | script |
| SIN-61 | Every case has a verdict in the latest run on a build of its step; a `not-run` or `blocked` verdict carries a reason | `check`: no `COV-18` finding on the cases | script |
| SIN-62 | The latest run of each step names the latest build of that step, made from the run's item under test | `check`: no `COV-49` finding | script |
| SIN-63 | The elements and doubles of each build match the strategy's step; the manifest names samples, tags or drawings, not only "latest" | read the build record beside the strategy | semantic |
| SIN-64 | The run's `selection` and its `not-run` reasons agree with the regression rules of the strategy for what changed since the previous run | read `selection` and the reasons beside the strategy and `impact` of the changed items | semantic |
| SIN-65 | Every failed case has a problem report with an `affects` link, or a decision recorded for it | compare the failed verdicts with the `problem-report` items | semantic |
| SIN-66 | The person who ran the bench is named in the bench's report or the record, and the configuration run is the one the build describes | ask who ran it; compare the report with the manifest | accountable |
| SIN-67 | Cases not run and failures left open were accepted by the person the strategy names | ask who accepted them, and when | accountable |
