# Unit verification strategy

File: `plans/<ID>.md`. Type `plan`, `kind: unit-verification`. Attributes and sections
are those of type `plan` in `schema/items.yaml`. A project has one such plan; the trace
check reports `COV-27` until it is approved, and reads `coverage_targets` from it for
`COV-28`.

## Decisions to ask the user before drafting

Ask these, with the options, and write down who decided. Do not fill in a value the user
has not given; a value taken from the template below is a proposal and is shown as one.

| Decision | Typical options | Lands in |
|---|---|---|
| Which units are verified here | every `software-unit` with origin `handwritten`; a named subset | `Scope` |
| What happens to units with origin `generated`, `third-party` or `reused` | verified by their source and taken over with that evidence; verified at the model; analysed but not tested | `Scope`. `COV-12`, `COV-28`, `COV-29` and `COV-30` skip units with origin `generated` or `third-party`, so the plan must name how they are verified instead. A `reused` unit that exists as an item is checked like a handwritten one |
| What unit verification leaves to other levels | timing, stack, interrupt behaviour and anything else the host cannot show | `Scope` |
| Methods and their order | build, static analysis, code review, unit test, structural coverage | `Approach` |
| What is stricter for units with an ASIL | injected failures of called services; branch coverage; a reviewer who did not write the code | `Approach`, `coverage_targets` |
| Static analysis: which analyser, which rule set | compiler defect analysis only; a guideline analyser with a named rule set and rule classification | `Approach`, `Environment and tools`. Without a guideline analyser the limitation is declared in `Scope` |
| Coverage metrics and targets per ASIL | statement, branch and MC/DC percentages; the choice follows what the project's safety standard recommends for the ASIL and is made with the person responsible for functional safety | `coverage_targets`, `Criteria` |
| What counts as an acceptable coverage gap or a justified analysis finding, and who accepts it | code that cannot be reached through the unit's interface; nobody below a named role | `Criteria`, `Responsibilities` |
| Entry, pass and exit criteria | see template | `Criteria` |
| Regression rule | everything of the affected units after every change; a selection rule | `Approach` |
| Environment | host with stand-in headers; simulator; target | `Environment and tools`; the name is used as `environment` of test cases and runs |
| Who writes, reviews, runs, decides | roles, not names of people | `Responsibilities` |

`coverage_targets` holds any of `statement_percent`, `branch_percent` and `mcdc_percent`
per ASIL. An ASIL without an entry has no target, and a unit of that ASIL is not checked
by `COV-28`. Set a target only for a metric the project's coverage tool reports: the
example runner measures statement and branch coverage with gcov, so with an
`mcdc_percent` target and that runner `COV-28` reports the metric as not reported for
every unit. Tell the user before the target is written.

## Template

The values are those of the power window example and are invented. Replace every one of
them with what the user decides.

```markdown
---
id: PLN-0001
type: plan
title: Unit verification strategy
status: draft
kind: unit-verification
coverage_targets:
  QM: {statement_percent: 80}
  A: {statement_percent: 100, branch_percent: 100}
  B: {statement_percent: 100, branch_percent: 100}
---

## Scope

Verified under this strategy: every `software-unit` item with origin `handwritten`. At
present these are the units of window position acquisition and anti-pinch detection.

Not verified here:
- Units of reused components (command logic, motor actuation): verified by the project
  they come from and taken over with that evidence.
- Generated or third-party units: none in this project. If one is added, this section
  names how it is verified before the unit is approved.

Left to later levels: everything that depends on the target, such as execution time,
stack use and interrupt latency. The host tests show the logic of a unit, nothing more.

Declared limitation: no coding guideline analyser is available. Conformance to a
guideline set is therefore not assessed and is reported as such with every analysis run.

## Approach

Every unit goes through these methods, in this order.

| No. | Method | What it shows | How |
|---|---|---|---|
| 1 | Build | the unit compiles without a warning | strictest warning level of the compiler in use, warnings treated as errors |
| 2 | Static analysis | no defect of the kinds the analyser knows | defect analysis of the compiler over every unit source; each finding is removed or justified by a named person |
| 3 | Code review | the code is the design, and only the design | comparison with the unit design: every designed function with its designed interface, nothing implemented that the design does not describe, error handling as designed. The review record names the code revision |
| 4 | Unit test | the unit behaves as designed | test cases derived from the unit design, executed on the host |
| 5 | Structural coverage | the test set reaches the code | measured during the unit test run, per unit |

Test cases are derived from the unit design, never from the code:
- one or more cases per designed function for its normal behaviour;
- the boundary values of every argument and every stored value that has a range;
- every error return and every reaction to an invalid input;
- every state and every transition of a unit that has states;
- for units of ASIL A and higher, the failure of each service the unit calls.

Coverage is a check on the test set. Code the tests do not reach is tested, removed, or
justified as a deviation; no test case is written only to execute a line.

Regression. After a change to a unit's code, to its design, to a unit or interface it
uses, or to its test code, methods 1, 2, 4 and 5 are repeated for the changed unit and
for every unit that uses it, with all their test cases, and method 3 for the changed
code. After a change of compiler, compiler options or test harness they are repeated
for all units. A test case is never removed or weakened so that a run passes; a wrong
test case is corrected and reviewed again.

## Criteria

Entry, per unit: the unit design is approved; the test cases of the unit are approved;
the code is committed.

Pass criterion of a test case: every check in it holds. A test case that reports no
verdict counts as failed.

Exit, per unit:
- the build has no warning;
- the static analysis has no open finding; a finding that is kept is recorded with the
  run as a deviation, with its justification and who accepted it;
- the code was reviewed against the unit design, and has not changed since;
- every approved test case of the unit passed in the latest recorded run;
- structural coverage reaches the target for the unit's ASIL in `coverage_targets`, or
  each gap is recorded as a deviation with the coverage figure in the test run. A
  deviation is acceptable only for code that cannot be reached through the interface of
  the unit; it names that code, the reason and who accepted it;
- the results are recorded as a test run and a static analysis run that name the
  version tested, and neither the code of the unit nor its test code has changed since.

A failed test case, an open finding or an unexplained coverage gap is reported to the
Software Lead with the run; none of them is closed by changing the criteria.

## Environment and tools

- Environment `host`: a development computer, no target hardware. Platform headers the
  units include are replaced by stand-ins under `tests/unit/host/`.
- Test harness: plain C test functions with a small assertion header, one test program
  per unit. `tests/unit/run_tests.py` builds, runs and writes the result file.
- Compiler: any C99 compiler. Structural coverage needs gcc with gcov
  (`run_tests.py --coverage`); a run with another compiler records no coverage.
- Static analysis: `tests/static/run_analysis.py` with the analyser of the compiler.
- Records: written from the result files by `tools/record.py`, never by hand.

None of these tools is qualified. Their results are evidence for the logic of the units
on the host. Where the project has tool confidence requirements, each tool is evaluated
before its results are relied on.

## Responsibilities

| Activity | Responsible | Approves or decides |
|---|---|---|
| Test cases and test code | Software Developer or Software Tester | a reviewer who did not write them |
| Running tests and analysis, recording the runs | Software Developer | - |
| Code review | a reviewer who did not write the code | - |
| Coverage deviations, justified analysis findings | proposed by the Software Developer | Software Lead; for units with an ASIL together with the Functional Safety Engineer |
| Summary of the results | Software Developer | received by Software Lead, Software Integrator and Quality Assurance Engineer |
```

## Notes

- `Scope`, `Approach` and `Criteria` are needed before review, `Environment and tools`
  and `Responsibilities` before approval. Write all five; a strategy without them
  cannot be followed.
- The plan carries no links. Nothing depends on it in the trace data, so
  `python tools/traceability.py impact <plan ID>` lists nothing: a change of the
  strategy concerns every unit, and the next `check` evaluates `COV-28` against the new
  targets once the changed plan is approved again.
- The exit criteria can be read from `check`: `COV-18` (every case has a verdict),
  `COV-28` (coverage), `COV-29` (every designed function has a test case), `COV-30`
  (code and test code unchanged since the runs), `SUSPECT` and `CONSISTENCY` on the unit
  (code review; it counts only when the review was recorded with the code revision).
  Open analysis findings are read from the latest `static-analysis-run`.
- For a unit that is approved but has no code yet, `COV-12`, `COV-28` and `COV-29` are
  warnings marked "pending: the unit has no code yet". Test cases can be written and
  reviewed in that state; the exit criteria cannot be met before the code exists.
- The environment name used here (`host`) is the value of `environment` in the test
  cases and of `--environment` when a run is recorded. Use one spelling.
- Roles are named, people are not. Who holds a role is project organisation and stays
  out of the plan.
- The strategy is approved through `/review` like any other item. Until then `COV-27`
  is reported and no run is recorded.
