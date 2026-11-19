# Software qualification test specification review checklist

Version 1. Applies to: `software-qualification-test`, and the test code or procedure its
`script` names. Supports: SWE.6.BP2, SWE.6.BP3, SWE.6.BP4, SWE.6.BP5, SWE.6.BP6.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

Review the test cases with the software requirements open beside them, above all their
`Verification criteria`, and with the qualification test strategy. Qualification tests
show that the integrated software meets its requirements; they look at it from outside,
through the interfaces the software has to its platform and to the system.

Apply the parts that have something to look at:

- "Each test case" and "The set of test cases": always.
- "The test code or procedure": once it exists. An automated case needs `script` before
  approval; a manual case is reviewed through its `Steps`.
- "Results": once a run is recorded.

A review record cites this checklist as `software-qualification-test v1`, and a review
that approves needs a result for every check. A check of a part that has nothing to look
at yet is recorded as `not-applicable` with the reason - "no recorded run yet" for every
check of "Results" - and never as passed.

## Each test case

| ID | Check | How to check | Kind |
|---|---|---|---|
| SQT-01 | Mandatory attributes and sections for its state are present, values are allowed | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| SQT-02 | It verifies at least one software requirement that is still valid | `check`: no `COV-17` finding and no `LINK` finding about `verifies` on the item | script |
| SQT-03 | `asil` is not lower than the ASIL of any requirement verified | `check`: no `COV-23` finding on the item | script |
| SQT-04 | The expected result is the requirement's verification criterion - its values, tolerances and times - and nothing in it is taken from the design or the code | read the item beside `Statement` and `Verification criteria` of each requirement | semantic |
| SQT-05 | The case stimulates the software only at the inputs the strategy names, and observes it at its outputs and at the measurement points the strategy names - values the software publishes, as a measurement tool reads them on the control unit - never at internal variables of a unit | read `Preconditions` and `Steps` beside `Approach` of the strategy | semantic |
| SQT-06 | `Preconditions` give the environment, the software build and configuration, the variant, the start state and the stimulus or plant model; the case does not rely on another case having run | read the section | semantic |
| SQT-07 | `Steps` are numbered and concrete; `Expected result` has an exact entry per step, with tolerance and the time by which it must hold | read both sections side by side | semantic |
| SQT-08 | `environment` agrees with the strategy; where simulation stands in for the control unit, the strategy gives the reason and says what is left for the target | compare with the software qualification test plan | semantic |
| SQT-09 | `verifies` names every requirement whose criterion the case shows, and no other | read the case against its links | semantic |

## The set of test cases

| ID | Check | How to check | Kind |
|---|---|---|---|
| SQT-20 | Every software requirement verified by test has at least one case; one verified otherwise has its review | `check`: no `COV-14` finding | script |
| SQT-21 | Every part of every verification criterion is covered: each value, limit and time, and the boundary and error conditions the requirement states | walk `Verification criteria` of each requirement against the cases | semantic |
| SQT-22 | The cases cover the requirements of the release under test, as `release` of the requirements and the strategy assign them | compare `release` with the cases and the strategy | semantic |
| SQT-23 | Requirements on timing and resources are tested on an environment that can show them, or the strategy says where they are shown instead | read the non-functional requirements beside the cases and the strategy | semantic |
| SQT-24 | The cases were compared with the current, approved requirements | `check`: no `SUSPECT` or `UPSTREAM` on the cases and no `COV-19` on the requirements | script |
| SQT-25 | No case lacks a requirement as its basis, and no two cases check the same thing | read the set | semantic |
| SQT-26 | The testers are as independent of the developers as the strategy requires | read `Responsibilities` of the strategy; ask who specified and who runs the cases | accountable |
| SQT-27 | The reviewer did not write the test cases and is as independent as `conventions.review_independence` in `project.yaml` asks | ask who wrote and who reviews; compare | accountable |

## The test code or procedure

| ID | Check | How to check | Kind |
|---|---|---|---|
| SQT-40 | An automated case has `script`, and the file and the function it names exist | `check`: no `SCHEMA` finding about `script` and no `LINK` finding "script names ..." on the item | script |
| SQT-41 | The test function or bench procedure does what the item says, step by step | read it beside the item | semantic |
| SQT-42 | Every entry of `Expected result` is checked with the tolerance the item gives, at the time it gives | read the function or procedure; count the checks against the entries | semantic |
| SQT-43 | The software under test is the build the strategy names (for an integrated project, a build of the last integration step); a plant or environment model contains no logic of the software under test | compare the test setup with the build record and the strategy | semantic |
| SQT-44 | The test program or bench reports one verdict per case, and a failed check cannot end in a pass | read the reporting part | semantic |

## Results

| ID | Check | How to check | Kind |
|---|---|---|---|
| SQT-60 | Every case has a verdict in the latest qualification run; a `not-run` or `blocked` verdict carries a reason | `check`: no `COV-18` finding on the cases | script |
| SQT-61 | The run names the latest build of the last integration step, made from its item under test, or no integration plan exists because the software comes from outside the scope | `check`: no `COV-38` finding | script |
| SQT-62 | The run's `selection` and its `not-run` reasons agree with what the strategy asks for this release and after the changes since the previous run | read `selection` and the reasons beside the strategy | semantic |
| SQT-63 | Every failed case has a problem report with an `affects` link, or a decision recorded for it | compare the failed verdicts with the `problem-report` items | semantic |
| SQT-64 | Cases not run and failures left open were accepted by the person the strategy names before the software is released | ask who accepted them, and when | accountable |
