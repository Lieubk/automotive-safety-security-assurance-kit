# Running system qualification tests and recording the results

Qualification of the system is done on a bench, a test vehicle or the target in its
environment. The toolkit does not run it: it specifies the cases, and records what the
bench reports.

## Before the bench run

| No. | Command | Expect | Otherwise |
|---|---|---|---|
| 1 | `git status --porcelain`, `git rev-parse --short HEAD` | clean tree for what is tested; the commit or tag the system was built from | stop and show it |
| 2 | `python tools/traceability.py status` | a latest system build of the last integration step, successful, made from this commit | none: `/sys-integration-test` first |
| 3 | tell the bench team which cases are selected, by the strategy and the release | an agreed selection rule | ask the user |

The system flashed or assembled for the bench must be the one the build record names:
give the bench team the build ID and the configuration.

## Recording the bench's report

```
python tools/record.py test-run --level system-qualification --results <file>
       --build <system BLD-ID> --item-under-test <configuration>
       --environment "<bench or vehicle>" --selection "<rule>"
```

`<file>` is a result file of the tool's own format or the bench's JUnit XML report.

- Each `<testcase>` must carry the case ID in its name or class name (`SYQT-0007 ...`).
  A test name without an ID stops the command: map the names in the bench project, not
  by editing the report.
- `<failure>` or `<error>` gives `failed`; `<skipped>` gives `not-run` with its message
  as reason - a skip without a message is reported by `COV-18` until a run with a reason
  exists.
- The report's `timestamp` is the time of the run; without one, pass `--executed-at`.
- The report file is kept as evidence of every result.
- The item under test is what was tested: the configuration the build record names. If
  the bench tested another version, its results are not results of this build.
- Once an approved system-integration plan exists, the run needs `--build` of the last
  step; `COV-49` also reports a run that tested an older build.

## What the recording tool refuses

| Cause | What to do |
|---|---|
| `--build` missing although an approved system-integration plan exists | name the system build of the last step |
| the build belongs to an earlier step | build the last step |
| build and tested item differ | qualify the build that was tested, or build again |
| an approved test case has no result in the file | run it, or let the bench report it as skipped with the reason |
| a test name maps to no system-qualification-test item | write the item or correct the name in the bench project |

Read the tool's own message; it names the problem and writes nothing.

## A failing test

| What is wrong | Where it goes |
|---|---|
| the system does not meet the requirement | find the element with the integration evidence; `/sys-architecture`, the software skills, or a problem report to whoever delivered an element taken over |
| the requirement or its criterion is wrong or not testable as written | `/sys-requirements` |
| the case expects something the requirement does not say | correct the item; its approval becomes stale; `/review` |
| the procedure, the bench or its set-up does not do what the item says | correct it; name every case it affects |

The user confirms. Where SUP.9 is in scope a confirmed defect gets a `problem-report`,
recorded by `/problem-resolution`.

## Summary for the user

From tool output only. Per requirement: its cases and their verdicts in the latest run,
criteria shown by another method and where; the system build and configuration
qualified, the environment; cases not run and why; failed cases and where they go;
whether strategy and cases are approved. Who else was told is recorded by `/baseline` as
a `communication-record` with `--practice SYS.5.BP7`.
