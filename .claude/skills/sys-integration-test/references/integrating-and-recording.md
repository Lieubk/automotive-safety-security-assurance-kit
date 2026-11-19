# Integrating the system steps, running the tests on the bench, recording both

A system build record says: this step of the strategy, in this configuration, on this
bench and setup, contained these system elements - at these versions, with this software
build - and these doubles stood in for the rest. A run record says: these test cases ran
on that build, with this outcome. Both are written by `tools/record.py` from files the
integrator or the bench wrote, never by hand. The toolkit does not reach hardware: the
step is assembled and the tests are executed on the bench; what comes back is a manifest
and a report.

## The sequence

Run from the project root (for an example, give `--project <dir>` to the toolkit
commands).

| No. | Who, command | Expect | Otherwise |
|---|---|---|---|
| 1 | the user: the software build the step contains is a final record | `python tools/traceability.py status` shows the latest build of the last software integration step | no software build: the software element waits for `/sw-integration-test`; a step without software can go on |
| 2 | the integrator assembles the step: samples, mechanics, software flashed, simulations running | the configuration is identified: sample numbers, drawing or tag, software build | stop: nothing is recorded for a configuration nobody can name |
| 3 | the integrator writes the manifest (see below) | one file, with the times of the integration just made | do not fill a manifest from the plan |
| 4 | the bench runs the cases of the step | a report of the bench: JUnit XML or a JSON result file, one verdict per case | the user supplies it; without it the step has a build and no run |
| 5 | `python tools/record.py build --level system --step <name> --manifest <file> --item-under-test <configuration>`, once per step | `wrote verification/builds/BLD-....md: step '<name>', succeeded, N elements (...)`; a line "not in this build" names what the step should contain but lacks | the tool names the problem and writes nothing (see below) |
| 6 | `python tools/record.py test-run --level system-integration --results <report> --build <BLD-ID of step 5> --item-under-test <configuration> --environment <bench> --selection "<rule>"`, once per step | `wrote verification/runs/RUN-....md: N passed` | as above |
| 7 | `python tools/traceability.py check` and `status` | `status` names the latest build per step; `check` the findings that remain | report them as they are |

Rules:
- Read `executed_at` in the manifest and the report first: they must be the times of the
  integration and the run just made. A report left on the bench's disk describes other
  samples.
- `--item-under-test` names the configuration: the baseline, tag or release of the
  system that was assembled. Build and run of one step name the same.
- A failed build is recorded only when the user wants the failure on record; nothing can
  be tested on it, and `test-run` refuses it.
- `--selection` names the strategy's rule that chose the cases: "all test cases of the
  step", "regression set", "impact of CR-0004". Cases of the step that were not run are
  in the report as skipped or in the result file as `not-run` with a reason; cases of
  earlier steps may be added as regression; cases of later steps are refused.
- The records and the copied logs are new files; committing them is the user's call.

## The manifest

```json
{
  "executed_at": "2026-11-19T09:00:00+00:00",
  "tool": "bench-electronics, test system release 4.2, setup of 2026-11-18",
  "result": "succeeded",
  "elements": [
    {"element": "SYE-0002", "version": "control unit sample B-04, hardware revision C"},
    {"element": "SYE-0005", "version": "software release candidate 3.2", "build": "BLD-0007"}
  ],
  "doubles": [
    {"element": "SYE-0003", "description": "rest-bus simulation of the door module and the vehicle network, database 2026-10"},
    {"element": "SYE-0001", "description": "load emulation of the motor, 12 V, 8 A"}
  ],
  "evidence": "bench/logs/software-step-2026-11-19.txt"
}
```

| Key | Meaning |
|---|---|
| `tool` | the bench and its setup: test system, release, configuration |
| `result` | `succeeded` when the step was assembled as planned, `failed` when it could not be |
| `elements` | every system element integrated up to this step, with the version of the sample, tag or drawing; for a software element, `build` is the build record of the software that was flashed - it must be final |
| `doubles` | what stood in for the elements not integrated in this step, with a description of the simulation or stand-in |
| `evidence` | the integration log or protocol; copied to `verification/evidence/<BLD-ID>/` |

A step contains everything integrated up to it: list the elements of earlier steps again.

## What the tools refuse, and what `check` reports

| Message | Cause | What to do |
|---|---|---|
| `no approved system-integration plan` | the strategy is not approved | `/review` the strategy first |
| `... has no step '<name>'` | the step name differs from the plan | use the plan's name; renaming a step is a change of the strategy |
| `a system integration run needs --build` | no build named | record the build first (step 5) |
| `... belongs to step '<later>'` | a case of a later step in the report | remove it from this report; it runs on the later build |
| `... was built from <configuration>, not from <configuration>` | build and run name different configurations | integrate and run again, or correct what was named |
| `COV-46` | an element that is not external is integrated in no step or in two, an element named does not exist, a step name is repeated, a double is named after its element was integrated. External elements are not required in any step; the check does not stop one from being listed under `components`, but the strategy should name them as doubles | correct the strategy, review it again |
| `COV-47 ... has no final build record` | a step was never recorded | steps 2, 3 and 5 |
| `COV-47 ... does not contain` | the build lacks an element the step integrates | integrate and record again |
| `COV-47 ... the system build is older than the software` | the software build in the manifest is no longer the latest of the last software integration step | flash the newer software build; record the step and the later ones again; run again |
| `COV-48` | a case names an unknown step, or a step has no case | correct the case, or derive cases for the step |
| `COV-49 ... the run does not describe it` | a newer build of the step exists than the one the latest run tested | run the step's cases on the newer build |
| `COV-15` | a system interface no case verifies | derive cases for it |

JUnit reports: a `<testcase>` is matched by the test case ID in its `name`;
`<failure>` or `<error>` makes it `failed`; `<skipped>` makes it `not-run`, with the
message as the reason. A case ID the report does not contain has no verdict and `COV-18`
reports it.

Never edit a manifest or a report to get past a refusal.

## A failing test

Read the verdict (`SYIT-0006 failed`, with the log line of the bench), the item, the
interface or view it rests on, then the definitions on both sides of the interface.
Propose with the texts:

| What is wrong | Where it goes |
|---|---|
| one element does not do what the interface says | the element's owner: hardware design, `/sw-requirements` or `/sw-integration-test` for the software; an element delivered by others: a problem report to whoever delivered it |
| the interface itself is unclear, incomplete or contradicts a requirement | `/sys-architecture` |
| the case expects something the architecture does not say | correct the item; its approval becomes stale; `/review` |
| the bench, a simulation or a procedure does not do what the item says | correct it; say so in the summary: every case that uses it is affected |
| the sample is not as the manifest says (wrong revision, wiring) | integrate again; record again |

The user confirms. Until then the case stays failed. Not allowed: deleting or weakening
the case, replacing an integrated element by a double, recording `not-run` for a case
that failed. A confirmed defect is recorded as a `problem-report` through
`/problem-resolution`.

## Regression

| What changed | What `check` reports | Integrate and run again |
|---|---|---|
| a system element (new sample, hardware revision, drawing) | `SUSPECT` on cases that verify it; the step's build describes the old version | every step that contains it and every later one |
| the software of the system (a newer software build) | `COV-47` "the system build is older than the software" | every step that contains the software element and every later one |
| a simulation or a double | nothing at this level: it is named in the manifest, not hashed | the steps that use it; tell the user |
| a bench procedure | nothing at this level | that step; tell the user |
| an interface or view of the architecture | `SUSPECT` on the cases that verify it | review the cases against the new version, then run the step |
| the strategy's steps | `COV-46`, `COV-47`, `COV-48` as far as the steps no longer fit | record every changed step again |

## Summary for the user

From tool output only (`status`, `check`, the records by ID, the bench's report). Per
step: build record, result, elements and doubles, run record, verdicts. Then failed
cases and where they go, cases not run and why, system interfaces without a verdict
(`COV-15`, `COV-18`), and whether strategy and cases are approved (`COV-27`, `COV-19`).
Who else was told is recorded by `/baseline` as a `communication-record` with
`--practice SYS.4.BP9`.
