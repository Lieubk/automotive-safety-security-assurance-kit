---
name: sw-qualification-test
description: "Test the integrated software against the software requirements (Automotive SPICE SWE.6): qualification test strategy with regression rules, test cases derived from the requirements and their verification criteria, test code or bench procedures, runs on the build of the last integration step - from the host or from a test bench's JUnit report - and the traceability between requirements, cases and results. Use when the software is to be qualified for a release or again after a change, or when the trace check reports COV-14, COV-17, COV-18, COV-38 or no approved software-qualification-test plan (COV-27)."
argument-hint: "[requirement IDs, 'strategy', 'run', a JUnit report to record, or nothing to work on every open qualification finding]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *), Bash(python tests/qualification/run_tests.py *), Bash(git status *), Bash(git rev-parse *), Bash(git diff *)
---

# Software qualification test (SWE.6)
> Toolkit root: `${CLAUDE_PLUGIN_ROOT}` - where this shows a placeholder instead of a folder, it is the repository you are in. The `tools/`, `schema/`, `aspice/`, `iso-26262/`, `iso-sae-21434/`, `examples/` and `.claude/docs/` named here and in the references lie in the toolkit root; run its tools from the project folder as `python "<toolkit root>/tools/<script>.py"`.

Shows that the integrated software meets its requirements, looked at from outside:
stimuli at its inputs, results at its outputs and at the measurement points the strategy
names. The result is a `plan` and `software-qualification-test` items in state `draft`,
ready for `/review`; test code or bench procedures; final `test-run` records of level
`software-qualification` on the build of the last integration step.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SWE.6.BP1 Develop software qualification test strategy including regression test strategy | writes the strategy with the user: test object, environment, stimuli and measurement points, regression | `plan` of kind `software-qualification-test` |
| SWE.6.BP2 Develop specification for software qualification test | derives cases from each requirement and its verification criteria | `software-qualification-test` items |
| SWE.6.BP3 Select test cases | chooses the cases of a run by the strategy and the release, and says how | `selection` and `not-run` reasons in the run |
| SWE.6.BP4 Test integrated software | runs the cases on the build of the last integration step, or records a bench's report | `test-run` naming the build |
| SWE.6.BP5 Establish bidirectional traceability | `verifies` links to requirements; results keyed by case | links; `matrix`, `show` output |
| SWE.6.BP6 Ensure consistency | self-checks against the checklist; the evidence comes from `/review` | proposed findings; review record |
| SWE.6.BP7 Summarize and communicate results | summarizes from tool output; `/baseline` records who was told | summary; `communication-record` |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. `SWE.6` not in `scope.processes`: stop. "SWE.6 is out of scope for this project."
3. Run `python tools/traceability.py status` and `python tools/traceability.py check --all`.
4. Cases need approved requirements: `list --type software-requirement --status
   approved`. Name and leave out a requirement in draft or in review (`UPSTREAM`).
5. Runs need the integrated software. With SWE.5 in scope that is a successful build of
   the last integration step: `status` names it; `COV-36` or `COV-38` on that step means
   it does not describe the present code - `/sw-integration-test` first. Without SWE.5,
   the strategy names where the integrated software comes from.
6. `COV-27` for kind `software-qualification-test`: do step 1 first. Cases may be
   drafted against a strategy the user agreed in this session; no run is recorded
   before the strategy is approved.

## Steps

### 1. Strategy (BP1)
- Search `plans/` for `kind: software-qualification-test`. An approved strategy rules
  every step below.
- If there is none, read `references/strategy-template.md`, ask the user the decisions
  listed there, and draft the plan. Environment, stimuli, measurement points, what is
  left to the target or to system level, and tester independence are the user's
  decisions.

### 2. Decide what to work on
- With arguments: the named requirements. Without: every `COV-14`, `COV-17`, `COV-18`
  and `COV-38` finding and every `SUSPECT` on a qualification test.
- `python tools/traceability.py matrix`, table `verifies: software-qualification-test
  -> software-requirement`. After a change, `impact <ID>` of the changed item.
- Tell the user the list and ask whether it is the scope of this session.

### 3. Derive the test cases (BP2)
- Read `references/deriving-test-cases.md`. Read each requirement: `Statement`,
  `Verification criteria`, `Analysis`, `release`, `asil`. Every criterion becomes at
  least one step with its values and times as the expected result.
- A requirement whose `verification_method` is not `test` gets no case; `COV-14` asks
  for its review instead.
- Where a criterion cannot be stimulated in the integrated software, say why in the case
  and name the level that shows it; never drop the criterion silently.
- Where a criterion is not testable as written, that is a question for
  `/sw-requirements`, not a guess.

### 4. Write test code or bench procedures (BP2, BP4)
- If the project has no qualification runner, read "A project without a runner" in
  `references/running-and-recording.md` and ask before copying anything.
- One test function per case, named after its ID. Stimuli only at the inputs the
  strategy names; observation only at outputs and named measurement points.
- A case run on a bench has `execution: manual` or names the bench's script; its result
  comes back as the bench's report.

### 5. Select and run (BP3, BP4)
Follow the sequence in `references/running-and-recording.md`.
- Clean tree, commit named; the build record of the last integration step made from
  that commit exists (`status`).
- Record with `python tools/record.py test-run --level software-qualification --results
  <file> --build <BLD-ID> --item-under-test <commit> --environment <name> --selection
  "<rule>"`. A bench's JUnit XML report is recorded the same way with `--results
  <report>.xml`; the cases are found by their IDs in the test names.
- A failing test is information: report it with its log line and propose where it goes;
  the user decides. Never weaken, delete or skip a case to get a pass.

### 6. Trace, self-check, summarize (BP5, BP6, BP7)
- `show <SWR-ID>` lists the cases that verify a requirement; the run record ties each
  result to its case and to the build.
- Apply `.claude/docs/checklists/software-qualification-test.md` to the cases and their
  code, and `.claude/docs/checklists/plan.md` to a drafted strategy. Show findings as
  proposals; correct what the user accepts.
- `/review` cites `software-qualification-test v1`; before a run exists the part
  "Results" is `not-applicable`.
- Summarize as "Summary for the user" in `references/running-and-recording.md` says.

## Writing

- Show the derivation table (requirement, criterion, case and step) and ask, for
  example: "May I write these N qualification test cases to
  `verification/software-qualification/` and their functions to
  `tests/qualification/test_qualification.c`?" Ask separately before writing a plan.
- IDs: `python tools/record.py next-id software-qualification-test` or `next-id plan`.
  Status `draft`. Before changing an approved item, say that its approval becomes stale.

## Checks before you finish

Run `python tools/traceability.py check --all`.
- `FORMAT`, `SCHEMA` and `LINK` findings on items written in this session: fix them.
- `COV-14`, `COV-17`, `COV-18` and `COV-38`: report each as it is, with what would
  close it.
- `COV-38` "the run does not describe it" means the software changed after the run:
  qualify the new build. Do not explain it away.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. Per requirement: cases, verdicts in the latest run, criteria shown elsewhere and
   where; the build and commit qualified - or `NOT ASSESSED` and why.
3. Failed cases and where each goes; questions about requirements.
4. The remaining findings of the check that concern these items.
5. Next: `/review` for strategy and cases; `/sw-requirements`, `/sw-integration-test`
   or the design skills for defects; `/baseline` for the release and to record who was
   told the results.

## Do not

- Do not set `status` to anything but `draft`, and do not write a review record.
- Do not type or edit a run record or a result file, and do not write a bench result
  you did not receive as the bench's own report.
- Do not take an expected result from the design or the code.
- Do not read or set internal variables of a unit in a test; use the measurement points
  the strategy names.
- Do not change the software under test, and do not copy or adapt a runner without asking.
