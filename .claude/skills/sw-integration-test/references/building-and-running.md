# Building the integration steps, running the tests, recording both

A build record says: this step of the strategy, from this commit, with this tool,
contained these components - these units from the project's sources, these components
as received, these doubles - and these files at these hashes. A run record says: these
test cases ran on that build, with this outcome. Both are written by
`tools/record.py` from files a tool wrote, never by hand.

## The sequence

Run from the project root (for the example: give `--project examples/power-window` to
the toolkit commands and call the runner by its path inside the example).

| No. | Command | Expect | Otherwise |
|---|---|---|---|
| 1 | `git status --porcelain` for the source roots, the folders of components taken over, `tests` | no output | stop and show it; the user commits or discards |
| 2 | `git rev-parse --short HEAD` | the commit every record will name | stop: a record needs a version |
| 3 | `python tests/integration/run_tests.py` (or `--step <name>`) | per step: build result, cases passed; under `build/integration/<step>/` the files `manifest.json`, `build.log`, `results.json`, `run.log` | exit code 2: nothing could be built (no compiler, no plan, a component without code or double); report it |
| 4 | `git status --porcelain` as in 1 | still no output | something changed during the run: do not record |
| 5 | `python tools/record.py build --step <name> --manifest build/integration/<name>/manifest.json --item-under-test <commit>`, once per step | `wrote verification/builds/BLD-....md: step '<name>', succeeded, N components (...)`; a line "not in this build" names what the step should contain but lacks | the tool names the problem and writes nothing (see below) |
| 6 | `python tools/record.py test-run --level software-integration --results build/integration/<name>/results.json --build <BLD-ID of step 5> --item-under-test <commit> --environment host --selection "<rule>"`, once per step | `wrote verification/runs/RUN-....md: N passed` | as above |
| 7 | `python tools/traceability.py check` and `status` | `status` names the latest build per step; `check` the findings that remain | report them as they are |

Rules:
- Read `executed_at` in the manifest and the result file first: they must be the times
  of the run just made. Files left in `build/` describe other code.
- A failed build is recorded only when the user wants the failure on record; nothing can
  be tested on it, and `test-run` refuses it.
- `--selection` names the strategy's rule that chose the cases: "all test cases of the
  step", "regression set", "impact of CR-0004". Cases of the step that were not run are
  in the result file as `not-run` with a reason; cases of earlier steps may be added as
  regression; cases of later steps are refused.
- The records and the copied logs are new files; committing them is the user's call.

## The manifest

```json
{
  "executed_at": "2026-11-19T09:00:00+00:00",
  "tool": "<compiler, version and options>",
  "result": "succeeded",
  "files": ["src/windowpos/HallCapture.c", "src/windowpos/WindowPos.c", "src/antipinch/AntiPinch.c"],
  "delivered": [{"component": "CMP-0005", "version": "window lifter platform 3.2.0, MotorDrive",
                 "files": ["reused/motordrive/MotorDrive.c"]}],
  "doubles": [{"component": "CMP-0006", "file": "tests/integration/doubles/Platform_double.c"}],
  "evidence": "build/integration/application/build.log"
}
```

| Key | Meaning |
|---|---|
| `files` | the project's source files built into the software; each must belong to a live unit (or match the generated or third-party patterns of `project.yaml`). The tool groups the units by component |
| `delivered` | components integrated as received, with the version and their files; they have no units in this project |
| `doubles` | the stand-ins of the step, with the component each one replaces |
| `evidence` | the build log; copied to `verification/evidence/<BLD-ID>/` |

The test program itself is not part of the software and is not listed.

The example runner writes this file from the plan and the items: the step's components
up to it come from `integration_steps`, their units' files from `source_files`, the
files of delivered components and of the doubles from
`tests/integration/integration.yaml`. A project with its own build system writes the
manifest from that build instead - from the linker map or the list of objects, never
from memory.

## What the tools refuse, and what `check` reports

| Message | Cause | What to do |
|---|---|---|
| `no approved software-integration plan` | the strategy is not approved | `/review` the strategy first |
| `... has no step '<name>'` | the step name differs from the plan | use the plan's name; renaming a step is a change of the strategy |
| `built file ... belongs to no software unit` | a source file no unit lists, or code of a component taken over that is not listed under `delivered` | a design matter (`/sw-detailed-design`), or the build configuration |
| `a software integration run needs --build` | no build named | record the build first (step 5) |
| `... belongs to step '<later>'` | a case of a later step in the results | remove it from this step's program; it runs on the later build |
| `... was built from <commit>, not from <commit>` | build and run made from different commits | build and run again from one commit |
| `COV-36 ... has no final build record` | a step was never built and recorded | steps 3 and 5 |
| `COV-36 ... changed after build` | a file of the step changed since the build | the build describes older software: steps 3 to 6 again |
| `COV-36 ... does not contain` | the build lacks a component or a unit with code | the build configuration or the step; build again |
| `COV-38 ... the run does not describe it` | a newer build of the step exists than the one the latest run tested | run the step's cases on the newer build |
| `COV-37` | a case names an unknown step, or a step has no case | correct the case, or derive cases for the step |

Never edit a manifest or a result file to get past a refusal.

## A failing test

Read the verdict line (`SIT-0006 FAIL <file>:<line>`), the item, the interface or view
it rests on, then the code of both sides of the interface. Propose with the texts:

| What is wrong | Where it goes |
|---|---|
| one side of the interface does not do what the interface says | the unit's design or code: `/sw-detailed-design` or `/sw-unit-implement`; a component taken over: a problem report to whoever delivered it |
| the interface itself is unclear or contradicts a requirement | `/sw-architecture` |
| the case expects something the architecture does not say | correct the item; its approval becomes stale; `/review` |
| the test code or a double does not do what the item says | correct it; say so in the summary: every case that uses the double is affected |

The user confirms. Until then the case stays failed. Not allowed: deleting or weakening
the case, replacing an integrated component by a double, recording `not-run` for a case
that failed. Where SUP.9 is in scope a confirmed defect also gets a `problem-report`,
recorded by `/problem-resolution`.

## Regression

| What changed | What `check` reports | Build and run again |
|---|---|---|
| code of a unit, or a file of a delivered component | `COV-36` for every step whose build contains the file; `COV-30` and `SUSPECT` at unit level | every such step, after unit verification and code review are current |
| a double or the platform double | `COV-36` for every step whose build contains it | those steps |
| a test program | nothing at this level: run files are not hashed per case | that step; tell the user |
| an interface, component or view | `SUSPECT` on the cases that verify it | review the cases against the new version, then run the step |
| the strategy's steps | `COV-35`, `COV-37` and `COV-36` as far as the steps no longer fit | build every changed step again |

## A project without a runner

Look for `tests/integration/run_tests.py`. If there is none, propose the example's and
ask before copying: `tests/integration/run_tests.py`, `integration.yaml` (to be written
for the project) and the doubles as models; the runner imports the unit test runner for
the compiler and reads the plan with the toolkit's trace engine. Tell the user that it is
an unqualified example tool.

## Summary for the user

From tool output only (`status`, `check`, the records by ID). Per step: build record,
result, components and doubles, run record, verdicts. Then failed cases and where they
go, cases not run and why, and whether strategy and cases are approved (`COV-27`,
`COV-19`). Who else was told is recorded by `/baseline` as a `communication-record`
with `--practice SWE.5.BP9`.
