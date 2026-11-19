# System qualification test specification review checklist

Version 1. Applies to: `system-qualification-test`, and the procedure its `script` names.
Supports: SYS.5.BP2, SYS.5.BP3, SYS.5.BP4, SYS.5.BP5, SYS.5.BP6.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

Review the test cases with the system requirements open beside them, above all their
`Verification criteria`, and with the system qualification test strategy. Qualification
tests show that the integrated system meets its requirements; they look at it from
outside, through its interfaces to the environment.

Apply the parts that have something to look at:

- "Each test case" and "The set of test cases": always.
- "The procedure": once it exists. An automated case needs `script` before approval; a
  manual case is reviewed through its `Steps`.
- "Results": once a run is recorded.

A review record cites this checklist as `system-qualification-test v1`, and a review that
approves needs a result for every check. A check of a part that has nothing to look at
yet is recorded as `not-applicable` with the reason - "no recorded run yet" for every
check of "Results" - and never as passed.

## Each test case

| ID | Check | How to check | Kind |
|---|---|---|---|
| SQS-01 | Mandatory attributes and sections for its state are present, values are allowed | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| SQS-02 | It verifies at least one system requirement that is still valid | `check`: no `COV-17` finding and no `LINK` finding about `verifies` on the item | script |
| SQS-03 | `asil` is not lower than the ASIL of any requirement verified | `check`: no `COV-23` finding on the item | script |
| SQS-04 | The expected result is the requirement's verification criterion - its values, tolerances and times - and nothing in it is taken from the architecture, the design or the code | read the item beside `Statement` and `Verification criteria` of each requirement | semantic |
| SQS-05 | The case stimulates the system only at the interfaces the strategy names, and observes it at its outputs and at the measurement points the strategy names, never at internal values that only a debugger reaches | read `Preconditions` and `Steps` beside `Approach` of the strategy | semantic |
| SQS-06 | `Preconditions` give the environment, the system configuration and variant, the start state, the operating conditions and the stimulus or plant model; the case does not rely on another case having run | read the section | semantic |
| SQS-07 | `Steps` are numbered and concrete; `Expected result` has an exact entry per step, with tolerance and the time by which it must hold | read both sections side by side | semantic |
| SQS-08 | `environment` agrees with the strategy; where a bench or simulation stands in for the vehicle, the strategy gives the reason and says what is left for the vehicle | compare with the system qualification test plan | semantic |
| SQS-09 | `verifies` names every requirement whose criterion the case shows, and no other | read the case against its links | semantic |

## The set of test cases

| ID | Check | How to check | Kind |
|---|---|---|---|
| SQS-20 | Every system requirement verified by test has at least one case; one verified otherwise has its review | `check`: no `COV-16` finding | script |
| SQS-21 | Every part of every verification criterion is covered: each value, limit and time, and the boundary, error and operating conditions the requirement states | walk `Verification criteria` of each requirement against the cases | semantic |
| SQS-22 | The cases cover the requirements of the release under test, as `release` of the requirements and the strategy assign them | compare `release` with the cases and the strategy | semantic |
| SQS-23 | Requirements on timing, supply, temperature and other non-functional properties are tested in an environment that can show them, or the strategy says where they are shown instead | read the non-functional requirements beside the cases and the strategy | semantic |
| SQS-24 | The cases were compared with the current, approved requirements | `check`: no `SUSPECT` or `UPSTREAM` on the cases and no `COV-19` on the requirements | script |
| SQS-25 | No case lacks a requirement as its basis, and no two cases check the same thing | read the set | semantic |
| SQS-26 | The testers are as independent of the developers as the strategy requires | read `Responsibilities` of the strategy; ask who specified and who runs the cases | accountable |
| SQS-27 | The reviewer did not write the test cases and is as independent as `conventions.review_independence` in `project.yaml` asks | ask who wrote and who reviews; compare | accountable |

## The procedure

| ID | Check | How to check | Kind |
|---|---|---|---|
| SQS-40 | An automated case has `script`, and the file and the test it names exist | `check`: no `SCHEMA` finding about `script` and no `LINK` finding "script names ..." on the item | script |
| SQS-41 | The bench procedure or script does what the item says, step by step | read it beside the item | semantic |
| SQS-42 | Every entry of `Expected result` is checked with the tolerance the item gives, at the time it gives | read the procedure; count the checks against the entries | semantic |
| SQS-43 | The system under test is the build the strategy names (for an integrated project, a system build of the last integration step); a plant or environment model contains no logic of the system under test | compare the test setup with the build record and the strategy | semantic |
| SQS-44 | The bench reports one verdict per case under a name that carries the case ID, and a failed check cannot end in a pass | read the reporting part and a sample report | semantic |

## Results

| ID | Check | How to check | Kind |
|---|---|---|---|
| SQS-60 | Every case has a verdict in the latest qualification run; a `not-run` or `blocked` verdict carries a reason | `check`: no `COV-18` finding on the cases | script |
| SQS-61 | The run names the latest system build of the last integration step, made from its item under test, or no integration plan exists because the system comes from outside the scope | `check`: no `COV-49` finding | script |
| SQS-62 | The run's `selection` and its `not-run` reasons agree with what the strategy asks for this release and after the changes since the previous run | read `selection` and the reasons beside the strategy | semantic |
| SQS-63 | Every failed case has a problem report with an `affects` link, or a decision recorded for it | compare the failed verdicts with the `problem-report` items | semantic |
| SQS-64 | Cases not run and failures left open were accepted by the person the strategy names before the system is released | ask who accepted them, and when | accountable |
