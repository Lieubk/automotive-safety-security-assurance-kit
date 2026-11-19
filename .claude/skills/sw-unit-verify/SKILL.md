---
name: sw-unit-verify
description: "Verify software units against their detailed design (Automotive SPICE SWE.4): unit verification strategy, unit test cases derived from the design, test code, static verification, structural coverage, and run records written from tool output. Use when units are to be verified or re-verified after a change, or when the trace check reports COV-12, COV-17, COV-18, COV-28, COV-29, COV-30 or no approved unit-verification plan (COV-27)."
argument-hint: "[unit IDs, 'strategy', 'run', or nothing to work on every unit with open verification findings]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *), Bash(python tests/unit/run_tests.py *), Bash(python tests/static/run_analysis.py *), Bash(git status *), Bash(git rev-parse *), Bash(git diff *)
---

# Software unit verification (SWE.4)
> Toolkit root: `${CLAUDE_PLUGIN_ROOT}` - where this shows a placeholder instead of a folder, it is the repository you are in. The `tools/`, `schema/`, `aspice/`, `iso-26262/`, `iso-sae-21434/`, `examples/` and `.claude/docs/` named here and in the references lie in the toolkit root; run its tools from the project folder as `python "<toolkit root>/tools/<script>.py"`.

Shows, unit by unit, that the code does what its detailed design says: a strategy first,
test cases derived from the design, static verification, executed tests with measured
coverage, and records that tooling writes from tool output. The result is a `plan` and
`unit-test` items in state `draft`, ready for `/review`, the test code, and final
`test-run` and `static-analysis-run` records.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SWE.4.BP1 Develop software unit verification strategy including regression strategy | writes the strategy with the user: methods and their order, what depends on ASIL, regression rule, criteria, environment, responsibilities | `plan` item of kind `unit-verification` with `coverage_targets` |
| SWE.4.BP2 Develop criteria for unit verification | derives test cases from the unit design; coverage targets and static criteria come from the strategy | `unit-test` items with `Steps` and `Expected result` |
| SWE.4.BP3 Perform static verification of software units | builds without warnings, runs the analyser that is available and reports which kind of analyser it was; the code review goes through `/review`, recorded with the code revision | `static-analysis-run` record; build log kept with the test evidence |
| SWE.4.BP4 Test software units | writes test code one to one with the test cases, runs it, measures structural coverage where the toolchain can | `test-run` record with verdicts, `coverage` and source hashes; logs under `verification/evidence/` |
| SWE.4.BP5 Establish bidirectional traceability | sets `verifies` with function anchors and `script`; the recording tool keys results by test case and by unit | links; `matrix` and `show` output; run records |
| SWE.4.BP6 Ensure consistency | self-checks against the checklist; the evidence itself comes from `/review` | proposed findings; review record written by `/review` |
| SWE.4.BP7 Summarize and communicate results | summarizes the results for the user from tool output; `/baseline` records who was informed | summary in the hand-over; `communication-record` written by `/baseline` |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. `SWE.4` not in `scope.processes`: stop. "SWE.4 is out of scope for this project."
3. Run `python tools/traceability.py status` and `python tools/traceability.py check --all`
   (every command takes `--project <dir>` when the project is not the current directory;
   the runner and the analysis script are called by their path inside the project).
4. Everything after step 1 needs approved units:
   `python tools/traceability.py list --type software-unit --status approved`. If there
   are none, stop after the strategy: `/sw-detailed-design` writes the unit design. Name
   and leave out a unit in draft or in review: its test cases could not be approved
   (`UPSTREAM`), because approval goes from the top down.
5. A unit may be approved before it has code. `check` then prints `COV-12`, `COV-28` and
   `COV-29` for it as warnings ending in "(pending: the unit has no code yet)": the rule
   applies once the code exists, nothing is wrong yet. Write the test cases now (steps 3
   and 4); running and recording wait for `/sw-unit-implement`. Say which units are pending.
6. If the check reports `COV-19`, `SUSPECT` or `CONSISTENCY` on a unit you are about to
   verify, say so first: its design is unreviewed or has changed, or its code is not the
   code that was reviewed. Test cases and runs inherit that doubt.
7. `COV-27` for kind `unit-verification` means there is no approved strategy: do step 1
   first. Test cases may be drafted against a strategy the user agreed in this session;
   no run is recorded before the strategy is approved.

## Steps

### 1. Strategy (BP1)
- Search `plans/` for `kind: unit-verification` and read that plan. An approved strategy
  rules every step below. Where the project cannot follow it (a coverage target but no
  tool that measures it), say so; do not work around it.
- If there is none, or only a draft, read `references/strategy-template.md`, ask the user
  the decisions listed there, and draft the plan. Methods, coverage targets, the treatment
  of generated and third-party units and who accepts deviations are the user's decisions.

### 2. Decide what to verify
- With arguments: the named units. Without: every unit with a `COV-12`, `COV-28`,
  `COV-29` or `COV-30` finding and every test case with `COV-17`, `COV-18`, `COV-30` or
  `SUSPECT`.
- Run `python tools/traceability.py matrix` and read the table `verifies: unit-test ->
  software-unit`. After a change, run `python tools/traceability.py impact <ID>` for the
  changed item and apply "Regression" in `references/running-and-recording.md`.
- Tell the user the list and ask whether it is the right scope for this session.

### 3. Derive the test cases (BP2)
- Read each unit by ID: the contracts in `functions`, the ranges in `data`, and the
  sections `Behavior`, `Error handling` and `Dynamic behavior`. An expected result comes
  from the design. Do not open the unit's `.c` file to find out what the unit should do.
- Read `references/deriving-test-cases.md` and build the derivation table per unit: one
  or more cases per designed function, boundary values, every error return, every state
  and transition, and for units with an ASIL the failure of each called service.
- Where the design does not say what shall happen, list a question for the designer
  (`/sw-detailed-design`); for an imported unit write a `query` item about it. Do not
  fill the gap from the code.
- Set `verifies` to `<unit ID>#<function>` for every function the case checks (`COV-29`
  reports a public, scheduled or callback function no case names) and `asil` to the
  highest ASIL of the units verified (`COV-23` reports a lower one).

### 4. Write the test code (BP4)
- If the project has no test runner, read "A project without a runner" in
  `references/running-and-recording.md` and ask before copying anything.
- Follow `references/test-case-template.md`: one test function per test case, named
  after the case ID; one verdict line per case; an exit code other than 0 when a case
  fails; test doubles for called services inside the test file.
- Set `script` to `<path>::<test function>` once the function exists; `check` reports
  `LINK` for a `script` whose file or function is missing.
- The function follows its item step by step. To change what a test checks, change the
  item first (its approval becomes stale), then the code.

### 5. Static verification (BP3)
Report these parts, each with its own verdict ("Static verification: what ran, exactly"
in `references/running-and-recording.md`):
- **Build without warnings**: the runner compiles with warnings treated as errors.
- **Defect analysis**: run `python tests/static/run_analysis.py`; quote its `tool:` line
  and its finding count.
- **Coding guideline conformance**: shown only by a guideline analyser with a named rule
  set, never by the defect analysis of a compiler. If none ran, report "Coding guideline
  conformance: NOT ASSESSED - no guideline analyser ran".
- **Code review**: held through `/review`, not here. It counts as a review of the code
  only when recorded with the code revision. Quote what `check` says about the unit:
  `CONSISTENCY` when the design was reviewed and the code was not, `SUSPECT` when the
  code changed after its review.
- A finding is removed in the code (`/sw-unit-implement`) or stays open in the record.
  Keeping one as a justified deviation is decided by the person the strategy names and
  reaches the record through the analysis result file; do not justify it yourself.

### 6. Run and record (BP3, BP4)
Follow the command sequence in `references/running-and-recording.md` exactly.
- The code under test is committed and clean: `git status --porcelain -- <source roots>
  tests` prints nothing, and `git rev-parse --short HEAD` gives the commit the records
  will name. If the tree is not clean, stop and show the output; do not record.
- A record exists only when `python tools/record.py test-run --level unit --results
  <file> --item-under-test <commit> --environment <name>` or `python tools/record.py
  analysis-run --results <file> --item-under-test <commit>` wrote it from a tool's file.
- A tool is missing (compiler, coverage tool, guideline analyser): that part is
  `NOT ASSESSED`, named with the reason. Record what did run. Never fill the gap with an
  estimate or with a figure measured on another commit.
- A failing test is information. Report it with its log line, read design, test case
  and code, propose which is wrong, and let the user decide: code -> `/sw-unit-implement`;
  design -> `/sw-detailed-design`; test case -> correct the item and have it reviewed
  again. Never weaken or delete a test case to make a run pass.
- After a code change that a failing test caused: first `/review` with the unit as
  subject and the new code revision named (`SUSPECT` until then), then the sequence
  again on the new commit (`COV-30` until then).

### 7. Structural coverage (BP4)
- `check` compares the `coverage` of the latest final unit run with `coverage_targets`
  of the approved strategy and reports `COV-28` per unit.
- For each gap propose one of three: a test case for designed behaviour not yet tested;
  removal of code the design does not ask for (`/sw-unit-implement`); a deviation that
  says why the code cannot be reached. The person the strategy names decides. What that
  person states is recorded with `--deviation <unit ID>=<text>` on `test-run`: read
  "Coverage and deviations" in `references/running-and-recording.md` first.

### 8. Trace, self-check, summarize (BP5, BP6, BP7)
- `python tools/traceability.py show <ID>` shows the links of a unit or a test case in
  both directions; the run records tie each result to its test case and unit.
- Apply `.claude/docs/checklists/unit-test-specification.md` to the test cases and their
  test code, and `.claude/docs/checklists/plan.md` to a drafted strategy. Show the
  findings as proposals and correct what the user accepts.
- `/review` adds a named reviewer's verdict and the hashes of the unit design the test
  cases were compared with; a later design change shows as `SUSPECT`. It cites
  `unit-test-specification v2` and needs a result for every check; before runs exist the
  checks of the part on results are `not-applicable`.
- Summarize as "Summary for the user" in `references/running-and-recording.md` says.

## Writing

- Show the derivation table and ask, for example: "May I write these N unit test cases
  to `verification/unit/` and their test functions to `tests/unit/test_AntiPinch.c`?"
  Ask separately before writing a plan to `plans/`.
- IDs: `python tools/record.py next-id unit-test` or `next-id plan`, then count upwards.
  Status `draft`. Before changing an approved item, say that its approval becomes stale.
- A `query` item: `python tools/record.py next-id query`, folder `records/queries`,
  status `open`; layout in `references/deriving-test-cases.md`.

## Checks before you finish

Run `python tools/traceability.py check --all`.
- `FORMAT`, `SCHEMA` and `LINK` findings on items written in this session: fix them.
- `COV-12`, `COV-17`, `COV-18`, `COV-28` and `COV-29` for the units in scope: report each
  as it is, with what would close it. A line marked pending is reported as "waits for
  the code", not as a defect; a pending `COV-29` still names a function without a test
  case. `COV-27` and `COV-19` stay until `/review` has approved the strategy and the
  test cases. Say so.
- `COV-30` means a unit source or a test file changed after the latest run: say that the
  records describe older code and that the sequence has to be run again. Do not explain
  it away.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. The verdict per part - build, unit tests, structural coverage, defect analysis, coding
   guideline conformance, code review - each with record ID and commit, or
   `NOT ASSESSED` and why.
3. Failed cases and where each goes; questions for the designer and `query` items
   written; deviations proposed and who has to decide.
4. The remaining findings of the check that concern these items.
5. Next: `/review` for the strategy and the test cases, and, with the code revision
   named, for any unit whose code changed; `/sw-unit-implement` or `/sw-detailed-design`
   for defects; `/baseline` to record who was told the results.

## Do not

- Do not set `status` to anything but `draft`, and do not write a review record.
- Do not type or edit a run record or a result file. What a person accepted reaches a
  record through `--deviation` or through the project's analysis script, never by hand.
- Do not take an expected result from the code or change a test case to match the code.
- Do not weaken, skip or delete a test case, or mark it `not-run`, to get a pass.
- Do not state a verdict, coverage figure or finding count no tool reported for the commit.
- Do not accept a deviation or justify a finding in your own name, and do not present
  compiler analysis as conformance to a coding guideline.
- Do not change the code under test, and do not copy or adapt a runner without asking.
