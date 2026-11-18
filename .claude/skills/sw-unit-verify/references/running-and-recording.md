# Running unit verification and recording the results

A record says: these test cases, on this commit, in this environment, with this
outcome, according to this tool. Every part of that sentence has to be true. This page
gives the sequence that makes it true, the formats involved, and what to do when a
part is missing.

## The sequence, from clean commit to records

Run from the project root. `<source roots>` are `paths.source_roots` of `project.yaml`
(`src` in the example); `host` is the environment name of the strategy.

| No. | Command | Expect | Otherwise |
|---|---|---|---|
| 1 | `git status --porcelain -- <source roots> tests` | no output: code under test, test code and runner are committed | stop and show the output. The user commits or discards; then start again |
| 2 | `git rev-parse --short HEAD` | the commit both records will name | not a repository: stop. A record needs a version it can name |
| 3 | `python tests/unit/run_tests.py --coverage` | one line per test program, a total, the coverage per unit or the reason it was not measured; `build/unit-test-results.json` | exit code 1: a case failed, see "A failing test". Exit code 2: nothing ran, no result file |
| 4 | `python tests/static/run_analysis.py` | the `tool:` line, files analysed, findings; `build/static-analysis-results.json` | exit code 2 and `NOT ASSESSED`: no compiler, or the analyser stopped on a file. No result file |
| 5 | `git status --porcelain -- <source roots> tests` | still no output | something changed during the run: do not record, start again |
| 6 | `python tools/record.py test-run --level unit --results build/unit-test-results.json --item-under-test <commit> --environment host` | `wrote verification/runs/RUN-....md: N passed` | the tool names what is wrong and writes nothing, see "What the recording tool refuses" |
| 7 | `python tools/record.py analysis-run --results build/static-analysis-results.json --item-under-test <commit>` | `wrote verification/runs/SAR-....md: N units, M findings` | as above |
| 8 | `python tools/traceability.py check` and `python tools/traceability.py status` | the findings that remain; `status` names the latest run and its commit | report them as they are |

Rules that go with the sequence:

- Before step 6 and 7 read `executed_at` in each result file. It must be the time of
  the run just made. A result file left in `build/` by an earlier run describes other
  code and is never recorded.
- Both records store `sources`: a hash of every unit source file, and the test run also
  of every test file. That is how `check` later tells whether the code changed
  (`COV-30`). The hashes are taken when the record is written, which is one more reason
  to record straight after the run and from a clean tree.
- `build/` is build output and is not under version control (`.gitignore`). If the
  project does not ignore it yet, propose the entry; do not add it silently.
- For a project in a subfolder of the toolkit, as the worked example, give the folder to
  every command: `python examples/power-window/tests/unit/run_tests.py --coverage`, and
  `python tools/record.py --project examples/power-window test-run --level unit
  --results examples/power-window/build/unit-test-results.json ...`. The `--results`
  path is relative to the current directory; the `evidence` paths inside the file are
  relative to the project root.
- Runs made while developing are not recorded. Record when the user wants the state
  kept as evidence. A run with failed cases may be recorded if the user wants the
  failure on record; it is then the latest run until a newer one exists.
- The records and the copied logs are new files. Committing them is the user's call.

## Result file formats

These are the inputs of `tools/record.py` (see its module text). The example runner and
the example analysis script write them; any other tool's results must be converted
into them. A result file is tool output: it is never typed or corrected by hand.

Unit test results:

```json
{
  "executed_at": "2026-11-18T06:40:15+00:00",
  "compiler": "<compiler, version and options>",
  "results": [
    {"test": "UT-0013", "verdict": "passed", "evidence": "build/test_AntiPinch.log"}
  ],
  "coverage": [
    {"file": "src/antipinch/AntiPinch.c", "statement_percent": 100.0, "branch_percent": 100.0}
  ]
}
```

| Key | Meaning |
|---|---|
| `executed_at` | time of the run; decides which run is the latest |
| `compiler` | optional; appended to the environment name in the record |
| `results[].test` | ID of a `unit-test` item |
| `results[].verdict` | `passed`, `failed`, `blocked` or `not-run`; the last two need a `reason`, or the trace check reports `COV-18` |
| `results[].evidence` | log file, path relative to the project root; copied to `verification/evidence/<record ID>/` |
| `coverage` | optional. A list with one entry per source file, which the tool attributes to the unit that owns the file; or a text that says why coverage was not measured. Every key ending in `_percent` is kept: `statement_percent`, `branch_percent`, and `mcdc_percent` where the coverage tool reports it |

Static analysis results:

```json
{
  "tool": "<analyser, version, mode and rule set>",
  "executed_at": "2026-11-18T06:40:25+00:00",
  "files": ["src/antipinch/AntiPinch.c", "src/windowpos/HallCapture.c"],
  "findings": [
    {"file": "src/antipinch/AntiPinch.c", "line": 120, "rule": "<checker or rule ID>",
     "severity": "warning", "message": "<text of the tool>"}
  ],
  "deviations": [
    {"file": "src/antipinch/AntiPinch.c", "line": 120, "rule": "<checker or rule ID>",
     "justification": "<why the code is acceptable as written>", "accepted_by": "<who>"}
  ],
  "metrics": [
    {"file": "src/antipinch/AntiPinch.c", "name": "<metric>", "value": 9}
  ],
  "evidence": "build/static-analysis.log"
}
```

`files` lists every file that was analysed, with or without findings. `deviations` and
`metrics` are optional. The tool attributes everything to units through `source_files`.
A finding that a deviation matches (same file, rule and line) is recorded under
`deviations` of the unit as justified; every other finding is counted per severity in
`open_findings`.

### What the recording tool refuses

| Message | Cause | What to do |
|---|---|---|
| `UT-.... is not a unit-test item` | a test function has no test case item | write the item (step 3 of the skill) or remove the function; never the other way round to save a review |
| `approved test case UT-.... has no result in the file` | a test case has no test function, or was not run | implement it and run again. A case that cannot run in this environment is a matter for the strategy and for the runner, which then reports it as `not-run` with the reason |
| `coverage reported for ..., which belongs to no software unit` | a source file is not in `source_files` of any unit | a design matter: `/sw-detailed-design` |
| `--deviation needs UNIT=TEXT for a unit that has a coverage entry; no entry for: ...` | a deviation was given for a unit whose coverage was not measured in this run | a deviation explains a measured figure; measure first |
| `analysed file ... belongs to no software unit` | a source file is not in `source_files` of any unit | a design matter: `/sw-detailed-design` |
| `UNT-....: not analysed: ...` | a unit's C file was not given to the analyser | fix the analysis scope and run it again |
| `deviation for ... matches no finding of this run` | the finding is gone or has moved to another line | the deviation list is out of date: the person who accepted it looks at it again |
| `deviation for ... needs a justification and who accepted it` | an incomplete deviation entry | ask the user for what is missing; never fill it in |

In each case nothing is written. Do not work around a refusal by editing the result
file.

## When a tool is missing

| Situation | What the tools say | What to report | What is still recorded |
|---|---|---|---|
| No C compiler | runner: `no C compiler found`, exit code 2; analysis: `NOT ASSESSED: no C compiler found` | build, unit tests, coverage and defect analysis: `NOT ASSESSED - no compiler` | nothing. Test cases and test code can still be written and reviewed |
| Compiler without a coverage tool | `coverage not measured: coverage needs gcc with gcov, found ...` | structural coverage: `NOT ASSESSED`, with that text | the test run; its `coverage` is the text. `COV-28` is reported for every unit with a target |
| A target for a metric the coverage tool does not report (for example `mcdc_percent` with gcov) | `check`: `COV-28 ... mcdc_percent is not reported` | that metric: `NOT ASSESSED - the coverage tool does not measure it` | the test run with the metrics that were measured |
| No guideline analyser | the `tool:` line ends with "no coding-guideline rule set" | coding guideline conformance: `NOT ASSESSED - no guideline analyser ran` | the defect analysis run |
| The analyser stops on a file | `NOT ASSESSED: the analyser failed on ...` | defect analysis: `NOT ASSESSED` for the unit that owns the file | nothing for the analysis; the log is in `build/static-analysis.log` |

Never close such a gap with an estimate ("the tests obviously reach every line"), with a
figure from another commit or another compiler run, or by leaving the part out of the
summary. The remedy is a tool: tell the user which one is needed.

The trace check looks at the **latest** final unit run only. If a run with coverage is
followed by a recorded run from a toolchain without coverage, `COV-28` comes back for
every unit. When two toolchains are used, as in the example (`RUN-0001` without
coverage; `RUN-0002` and `RUN-0003` with gcc and gcov), record the run with coverage
last.

## Static verification: what ran, exactly

| Part | Evidence | It shows | It does not show |
|---|---|---|---|
| Build without warnings | the build section of each test log; the compiler and its options in `environment` of the test run. The runner treats warnings as errors, so a warning makes every case of that test program fail | the unit and its test compile cleanly at that warning level | anything about a different compiler or other options |
| Defect analysis | `static-analysis-run` whose `tool` names a compiler analyser | none of the defects this analyser looks for (for example null dereference, use of an uninitialised value, buffer overrun) was reported | absence of defects; conformance to a coding guideline |
| Coding guideline conformance | `static-analysis-run` whose `tool` names a guideline analyser and its rule set | the rules of that set were checked and what was found | anything, if no such analyser ran |
| Code review | a review record with the unit as subject, recorded by `/review` with the code revision: it carries `item_under_test` and the hashes of the unit's source files (`REV-0007` in the example) | a named person compared this code with the unit design | anything, while `check` reports `CONSISTENCY` ("a review of the code against the design is not evidenced": the design was reviewed, the code was not) or `SUSPECT` ("the code is no longer the code that was reviewed") on the unit |

Quote the `tool` text of the record when reporting. A project that has a guideline
analyser converts its report into the analysis result format, with the rule ID in
`rule`, and records it with `analysis-run` as a run of its own.

A finding is closed by changing the code. A finding that is kept needs a deviation: the
justification and the person who accepted it, in `deviations` of the analysis result
file. The skill does not decide that a finding is a false alarm and does not type a
deviation into a result file. The example analysis script writes no `deviations`. A
project that grants deviations keeps them under version control where its analysis
script, or the script that converts its analyser's report, reads them; propose that
extension to the user like any other change to the verification environment. Until
it exists a kept finding stays in `open_findings`, and the summary says who accepted it
and why.

## Coverage and deviations

`check` reports `COV-28` when the latest final unit run has no coverage entry for a
unit, or a figure below the target the approved strategy sets for the unit's ASIL, or
no figure for a metric that has a target.

Finding out what is not covered: the example runner reports figures only. After a run
with `--coverage`, `gcov -b -c -o build/cov <unit source>` in the project root writes a
listing `<file>.gcov` that marks the lines and branches not reached. Tell the user the
command; the listing is a scratch file and is not committed. This is the one place where
the code is read during test design, and only to answer: which statement of the design
does this code belong to?

| The code that is not reached | Means | Proposal |
|---|---|---|
| implements something the design describes | a test case is missing | derive the case from that design statement and add it |
| implements something the design does not describe | the unit does more than designed | remove the code (`/sw-unit-implement`), or extend the design (`/sw-detailed-design`) and then test it |
| cannot be reached through the interface of the unit (a defensive branch for a value that cannot occur) | no test can reach it without breaking into the unit | restructure so that the branch is shared with reachable code, or a deviation |

The example avoids the third case: the design names a state variable outside its range,
and the code handles it in the same branch as the IDLE state, so no unreachable branch
remains and the unit reaches its target without a deviation.

A deviation is decided by the person the strategy names, never by the skill:

1. Propose the text: which file and which lines or branches, why they cannot be
   reached, which design statement covers them.
2. Ask the user who accepts it and when, and put "accepted by <role or name the user
   gives>, <date>" at the end of the text. Pass what that person states, nothing else.
3. Record the run with the text: add `--deviation <unit ID>=<text>` to the `test-run`
   command of step 6, once per unit with a gap, for example
   `--deviation "UNT-0003=<text>"`. The tool writes it as `deviation` into the unit's
   coverage entry, next to the measured figures.
4. Run `check`: `COV-28` is no longer reported for that unit, and the record shows the
   figure and the reason side by side.

A deviation never changes a figure; the record keeps what was measured. Because the
check reads the latest run only, an accepted deviation is passed again, unchanged, with
every later run for as long as the same gap exists. A gap that has changed needs a new
decision.

## A failing test

A failed case means that design, code and test do not agree. Find out which one is
wrong before anything is changed. Read the verdict line (`UT-0021 FAIL <file>:<line>`),
the test case item, and the design statement it names; then the code.

| What is wrong | How it shows | Where it goes |
|---|---|---|
| The code | item and design agree; the code does something else | `/sw-unit-implement`; then `/review` with the unit as subject and the new code revision named, because the code is no longer the code that was reviewed (`SUSPECT`); then the whole sequence again on the new commit (`COV-30`) |
| The design | the design contradicts itself, a requirement, or what the user says is intended; the test case follows the design | `/sw-detailed-design`. The unit's approval becomes stale; its test cases are re-derived and reviewed again |
| The test case | the item expects something the design does not say | correct the item; its approval becomes stale; `/review`; then the test function |
| The test code | the function does not do what its item says | correct the function; the item is unchanged; run again |
| The test equipment | a test double or a stand-in header behaves differently from the designed service | correct it; say so in the summary, because every case that uses it is affected |

Propose the classification with the texts it rests on; the user confirms. Until then the
case stays failed. Not allowed, whatever the pressure: deleting the case, removing or
loosening a check, setting `regression: false`, recording `not-run` for a case that
failed. Where SUP.9 is in the project's scope, a confirmed defect also needs a
`problem-report` item that names the run in `found_in`; say so in the hand-over.

## A unit without code

A unit can be approved as a design before `/sw-unit-implement` has written its code.
For such a unit `check` reports `COV-12`, `COV-28` and `COV-29` as warnings that end in
"(pending: the unit has no code yet)". Pending means: the rule will apply as soon as
the unit lists source files, and until then nothing is wrong. Report these lines as
"verification pending - no code yet", never as failures and never as passed.

- Test cases are written from the design in this state, and the test functions with
  them; that is when they are most independent of the code. Each function a test case
  names in `verifies` takes its pending `COV-29` line away.
- Nothing can be built, run, measured or analysed, so there is no result file and no
  record. The parts of the summary are `NOT ASSESSED - the unit has no code yet`.
- When the code arrives, registering `source_files` does not change the unit's design
  approval. The pending lines turn into errors until the sequence above has been run
  and recorded, and `check` asks for a review of the code (`CONSISTENCY`).

## Regression

Two tools answer "what is affected": `check` for what has already changed, and
`python tools/traceability.py impact <ID>` for what a planned change will touch. In the
`impact` output, rows of type `unit-test` are test cases; rows of type `software-unit`
marked `(uses <ID>)` are units that call the changed unit.

| What changed | What `check` reports | Test cases to look at again | Run again |
|---|---|---|---|
| The design of a unit | `COV-19` on the unit; `SUSPECT` on each approved test case that verifies it; `COV-29` for a new function no case names | every `unit-test` at distance 1 in `impact <unit ID>`: re-derive against the new design, then `/review` | everything for the unit and for the units that use it |
| The code of a unit, design unchanged | `COV-30` on the unit for the latest test run and analysis run; `SUSPECT` on the unit, because the reviewed code changed. The unit item itself is unchanged and stays approved | none | `/review` with the unit as subject and the code revision named; then build, analysis, all test cases and coverage of the unit, and of the units that use it where the strategy says so |
| An interface | `SUSPECT` on the units that realize or use it; `impact <interface ID>` lists them at distance 1 and their test cases at distance 2 | those whose unit design changes as a result | as for each changed unit |
| A test case item | `COV-19` (stale approval) on it | that item: `/review` | the test program it belongs to |
| A test file, items unchanged | `COV-30` on every test case implemented in that file | none, but the test code is reviewed again | the test program |
| The runner, the assertion header, a stand-in header | nothing: these files are not among the hashes a run stores | none | everything. `git diff --name-only <item_under_test> HEAD -- tests` lists such changes since the recorded commit |
| The strategy | `COV-19` on the plan; `impact` lists nothing for a plan, every unit is concerned | all, against the changed criteria | what the changed criteria ask for; `check` applies new coverage targets once the plan is approved again |
| Compiler or compiler options | nothing | none | everything; the new record names the new environment |

The recorded run is always complete: `record.py test-run` writes nothing unless every
approved test case has a result. With the example runner the whole set runs in seconds,
so "run again" in practice means the whole sequence on the new commit; the table says
which findings to expect and which items need a person again.

`COV-30` is reported until a new run is recorded; it cannot be closed in any other way.
A run written by an older version of the recording tool has no `sources`; `check` then
warns that it cannot tell whether the code changed, and a new run settles it.

## A project without a runner

Look for `tests/unit/run_tests.py`. If the project has no runner and no other test
tool, propose the example harness and ask before copying:

| Copy from `examples/power-window/` | To the same path in the project | Purpose |
|---|---|---|
| `tests/unit/run_tests.py` | `tests/unit/run_tests.py` | builds one test program per `tests/unit/test_<Unit>.c`, runs it, optionally measures coverage, writes the result file |
| `tests/unit/test_support.h` | `tests/unit/test_support.h` | the assertion and verdict macros |
| `tests/static/run_analysis.py` | `tests/static/run_analysis.py` | compiler static analysis over the unit sources; imports the runner, so both are needed |

The scripts find the project from their own location and need no configuration. They
expect:

- the code under `src/`, one C file per unit, and a test file named after it:
  `src/**/<Unit>.c` with `tests/unit/test_<Unit>.c`;
- test functions named `test_UT_<NNNN>_<words>` and verdict lines `UT-<NNNN> PASS`;
- stand-ins for platform headers under `tests/unit/host/` (written per project; they
  are test equipment and are proposed to the user like test code);
- Python 3 and a C compiler: `cc`, `gcc` or `clang` on the path, or the Visual Studio
  compiler on Windows. Coverage needs gcc with gcov, and gives statement and branch
  figures only.

Copy the files unchanged. If the project does not fit (several C files per unit, another
source folder, another compiler, deviations of analysis findings), say what does not
fit and propose the change to the runner as a change the user decides on; the runner is
part of the verification environment the strategy describes. Tell the user that the
scripts are unqualified example tools.

## A project with another test tool

Nothing above depends on the example runner except the file names. The skill needs:

- a way to run the tests that exits with an error when a case fails;
- a result file in the format above, written by a script the project keeps under
  version control, which maps the tool's test names to test case IDs. A case the tool
  did not report must appear as `not-run` with a reason or make the conversion fail; the
  script never supplies a verdict of its own;
- coverage per source file as the coverage tool reported it, in keys ending in
  `_percent`, or the text saying why not.

Ask the user for the commands, quote their output, and record with `tools/record.py` as
above. Do not write a result file by hand from a console log.

## What each record shows, and what it does not

| Record | It shows | It does not show |
|---|---|---|
| `test-run`, level `unit` | the named test cases ran on the named commit with the named compiler and options, with these verdicts; the test programs of passed cases built without warnings; with a `coverage` list, the figures the coverage tool reported per unit, and beside a figure below target the reason a person accepted; in `sources`, which version of each source and test file it was | that the test cases are the right ones (the review shows that); behaviour on the target, with the target compiler, under real timing; coverage, when `coverage` is a text |
| `static-analysis-run` | the named tool analysed the listed files of each unit, in the versions `sources` names, and left this many open findings and these justified deviations | conformance to a coding guideline, unless `tool` names a guideline analyser and rule set; that the code has no defects |
| review record of the test cases (written by `/review`) | a named person compared the test cases, at the recorded hashes, with the unit design at the recorded hashes | that the tests were run, or that they pass |
| review record of a unit that names the code revision (written by `/review`) | a named person compared the code, in the versions `sources` names, with the unit design | that the code was tested. Without `item_under_test` the record covers the design only |

None of the example tools is qualified. A record says what a tool reported; how far that
tool can be trusted is stated in the strategy and decided by the project.

## Summary for the user

The summary is put together from tool output, never from memory: `status`, `check`, and
the latest `test-run` and `static-analysis-run` records read by ID.

Per unit, one row: unit, ASIL, test cases (passed / failed / blocked / not run),
coverage per metric against the target, open analysis findings, deviations.

Per part, one verdict:

| Part | `PASS` | `CONCERNS` | `FAIL` | `NOT ASSESSED` |
|---|---|---|---|---|
| Build without warnings | every test program built | - | a build failed | no compiler |
| Unit tests | every approved case passed in the latest run, and no `COV-30` | a case is `not-run` or `blocked` with a reason | a case failed, or has no verdict | no run, or `COV-30`: the run describes older code |
| Structural coverage | no `COV-28` finding | a gap with a recorded deviation | a gap without one | not measured |
| Defect analysis | 0 open findings, and no `COV-30` | findings recorded as justified deviations | open findings | the analyser did not run, or `COV-30` |
| Coding guideline conformance | a guideline analyser ran and left nothing open | justified deviations | open violations | no guideline analyser ran |
| Code review | the unit's newest approving review names the code revision, and no `SUSPECT` | - | `SUSPECT`: the code changed after the review | `CONSISTENCY`: the design was reviewed, the code was not |

Then: the commit and the record IDs; failed cases with their classification; what was
not assessed and which tool is missing; whether strategy and test cases are approved
(`COV-27`, `COV-19`) and every designed function is named by a test case (`COV-29`).

The summary is for the user. Who else received it, and when, is recorded as a
`communication-record` by `/baseline` when the user says it happened.
