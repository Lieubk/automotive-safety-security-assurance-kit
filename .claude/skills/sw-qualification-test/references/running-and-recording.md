# Running qualification tests and recording the results

## On the host (software-in-the-loop)

| No. | Command | Expect | Otherwise |
|---|---|---|---|
| 1 | `git status --porcelain` for sources, components taken over, `tests` | no output | stop and show it |
| 2 | `git rev-parse --short HEAD` | the commit | stop |
| 3 | `python tools/traceability.py status` | a line "latest build of step '<last step>' BLD-.... on <commit>: succeeded" for this commit | no such build: `/sw-integration-test` first |
| 4 | `python tests/qualification/run_tests.py` | build result, cases passed; `build/qualification/results.json` and `run.log` | exit code 2: nothing built; report it |
| 5 | `python tools/record.py test-run --level software-qualification --results build/qualification/results.json --build <BLD-ID> --item-under-test <commit> --environment software-in-the-loop --selection "<rule>"` | `wrote verification/runs/RUN-....md: N passed` | the tool names the problem and writes nothing |
| 6 | `python tools/traceability.py check` | no `COV-18` or `COV-38` for these cases | report what remains |

The example runner builds exactly the files the last integration step contains (it
asks the integration runner), adds the test program, and runs it. The build record
named in step 5 is the evidence of what was integrated; the run is evidence of what that
software did.

## From a test bench

A bench of the project or of the customer writes its own report. The toolkit reads JUnit
XML, which most bench tools export:

```
python tools/record.py test-run --level software-qualification --results <report>.xml
       --build <BLD-ID> --item-under-test <commit or tag of the flashed software>
       --environment "<bench name>" --selection "<rule>"
```

- Each `<testcase>` must carry the case ID in its name or class name (`SQT-0004 ...`).
  A test name without an ID stops the command: map the names in the bench project,
  not by editing the report.
- `<failure>` or `<error>` gives `failed`; `<skipped>` gives `not-run` with its
  message as reason - a skip without a message is reported by `COV-18` until a run with
  a reason exists.
- The report's `timestamp` is the time of the run; without one, pass `--executed-at`.
- The report file is kept as evidence of every result.
- The item under test is what was flashed: the commit or tag the build record names.
  If the bench tested another version, its results are not results of this build.

## What the recording tool refuses

| Message | Cause | What to do |
|---|---|---|
| `the project has an approved software-integration plan: name the build ...` | `--build` missing | name the build of the last step |
| `... is a build of step '<x>'; the software is qualified on a build of the last step` | an earlier step's build | build the last step |
| `... was built from <a>, not from <b>` | build and tested software differ | qualify the build that was tested, or build again |
| `approved test case ... has no result in the file` | a case was not run | run it, or let the runner or bench report it as `not-run` with the reason |
| `... is not a software-qualification-test item` | a test name maps to no case | write the item or correct the name in the bench project |

## A failing test

| What is wrong | Where it goes |
|---|---|
| the software does not meet the requirement | find the component with the integration and unit evidence; `/sw-detailed-design`, `/sw-unit-implement`, or a problem report to whoever delivered a component taken over |
| the requirement or its criterion is wrong or not testable as written | `/sw-requirements` |
| the case expects something the requirement does not say | correct the item; its approval becomes stale; `/review` |
| the test code, the double or the bench does not do what the item says | correct it; name every case it affects |

The user confirms. Where SUP.9 is in scope a confirmed defect gets a `problem-report`.

## A project without a runner

Look for `tests/qualification/run_tests.py`. If there is none, propose the example's
and ask before copying; it needs the integration runner and its configuration. Tell
the user that it is an unqualified example tool.

## Summary for the user

From tool output only. Per requirement: its cases and their verdicts in the latest run,
criteria shown at another level and where; the build and commit qualified, the
environment; cases not run and why; failed cases and where they go; whether strategy and
cases are approved. Who else was told is recorded by `/baseline` as a
`communication-record` with `--practice SWE.6.BP7`.
