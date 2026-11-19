---
name: sw-integration-test
description: "Integrate the software step by step and test it against the software architecture (Automotive SPICE SWE.5): integration strategy with its steps and regression rules, integration test cases derived from interfaces, components and views, test code and doubles, a build record per step, test runs on those builds, and the traceability between them. Use when components are to be integrated or integrated again after a change, or when the trace check reports COV-13, COV-17, COV-18, COV-35, COV-36, COV-37, COV-38 or no approved software-integration plan (COV-27)."
argument-hint: "[step names, interface IDs, 'strategy', 'build', 'run', or nothing to work on every open integration finding]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *), Bash(python tests/integration/run_tests.py *), Bash(git status *), Bash(git rev-parse *), Bash(git diff *)
---

# Software integration and integration test (SWE.5)

Puts the software together in the order the strategy gives, step by step, and shows at
each step that the parts work together as the architecture says. The result is a `plan`
with its `integration_steps` and `software-integration-test` items in state `draft`,
ready for `/review`; test code and doubles; a final `build-record` per step and final
`test-run` records on those builds.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SWE.5.BP1 Develop software integration strategy | writes the strategy with the user: the steps, what each adds, what stands in for the rest | `plan` of kind `software-integration` with `integration_steps` |
| SWE.5.BP2 Develop software integration test strategy including regression test strategy | in the same plan: what is tested per step, by which method, and what is repeated after a change | sections `Approach` and `Criteria` |
| SWE.5.BP3 Develop specification for software integration test | derives test cases from interfaces, component behaviour and views, each assigned to a step | `software-integration-test` items |
| SWE.5.BP4 Integrate software units and software items | builds each step from the code the units list and the components delivered as received | `build-record` per step |
| SWE.5.BP5 Select test cases | chooses the cases of a run by the strategy's rules, and says how | `selection` and `not-run` reasons in the run |
| SWE.5.BP6 Perform software integration test | runs the cases on the build of their step | `test-run` of level `software-integration` naming the build |
| SWE.5.BP7 Establish bidirectional traceability | `verifies` links, `step`, and run records keyed by test case and build | links; `matrix` and `show` output |
| SWE.5.BP8 Ensure consistency | self-checks against the checklist; the evidence comes from `/review` | proposed findings; review record written by `/review` |
| SWE.5.BP9 Summarize and communicate results | summarizes from tool output; `/baseline` records who was told | summary; `communication-record` |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. `SWE.5` not in `scope.processes`: stop. "SWE.5 is out of scope for this project."
3. Run `python tools/traceability.py status` and `python tools/traceability.py check --all`
   (every command takes `--project <dir>`; runners are called by their path inside the
   project).
4. Test cases need an approved architecture: `list --type software-interface --status
   approved`, and the same for `software-component`. Name and leave out what is in draft
   or in review: its cases could not be approved (`UPSTREAM`).
5. Builds need code. A developed component whose units have no code yet cannot be
   built; `COV-36` is then a warning ending in "(pending: no unit of the step has code
   yet)". Write strategy and test cases now; building and running wait.
6. If the check reports `COV-30`, `SUSPECT` or `CONSISTENCY` on a unit that a step
   integrates, say so first: the code is not verified as it is, and an integration on
   top of it inherits that.
7. `COV-27` for kind `software-integration`: do step 1 first. No build and no run is
   recorded before the strategy is approved; `record.py build` refuses.

## Steps

### 1. Strategy (BP1, BP2)
- Search `plans/` for `kind: software-integration`. An approved strategy rules every
  step below; where the project cannot follow it, say so.
- If there is none, read `references/strategy-template.md`, ask the user the decisions
  listed there, and draft the plan. The order of the steps, the components left to
  others, the environments and the regression rules are the user's decisions.
- `check` reports `COV-35` for a component that no step integrates and that is not a
  double of the last step, for one integrated twice, and for a double named after its
  component was integrated.

### 2. Decide what to work on
- With arguments: the named steps or interfaces. Without: every finding of `COV-13`,
  `COV-17`, `COV-18`, `COV-35` to `COV-38` and every `SUSPECT` on an integration test.
- `python tools/traceability.py matrix`, table `verifies: software-integration-test ->
  ...`. After a change, `impact <ID>` of the changed item and "Regression" in
  `references/building-and-running.md`.
- Tell the user the list and ask whether it is the scope of this session.

### 3. Derive the test cases (BP3)
- Read `references/deriving-test-cases.md`. Work from the items, never from the code:
  `elements` and `operations` of each interface with their ranges, `invalid`,
  `timeout_ms` and returns; `Dynamic behavior` of the components; the `sequence`,
  `state-machine` and `execution-model` views.
- Assign each case the first step whose build contains everything it needs (`step`).
  `verifies` names the interfaces, components or views whose behaviour it shows; `asil`
  is the highest of those.
- Where the architecture does not say what shall happen at an interface, list a
  question for the architect (`/sw-architecture`); for an imported item write a `query`.

### 4. Write test code and doubles (BP3, BP6)
- If the project has no integration runner, read "A project without a runner" in
  `references/building-and-running.md` and ask before copying anything.
- One test function per case, named after its ID, in the test program of its step. A
  double stands only for a component the step names under `doubles`; it has the
  interface's signatures and returns prepared values.
- Set `script` once the function exists.

### 5. Build each step (BP4)
Follow the sequence in `references/building-and-running.md`.
- The tree is clean (`git status --porcelain`) and `git rev-parse --short HEAD` gives the
  commit; otherwise stop and show the output.
- `python tools/record.py build --step <name> --manifest <file> --item-under-test
  <commit>` writes the record from the manifest the build wrote. A failed build is
  recorded too when the user wants it on record; nothing is tested on it.
- The tool prints components the step should contain but the build lacks. Report them.

### 6. Select and run (BP5, BP6)
- Select by the strategy: all cases of the step, the regression set, or the cases
  `impact` names for a change. Cases of earlier steps may run again as regression;
  cases of later steps cannot run on this build.
- Record with `python tools/record.py test-run --level software-integration --results
  <file> --build <BLD-ID> --item-under-test <commit> --environment <name> --selection
  "<rule of the strategy>"`. A case not run is `not-run` with its reason in the results.
- A failing test is information: report it with its log line and propose where it goes
  ("A failing test" in `references/building-and-running.md`); the user decides. Never
  weaken, delete or skip a case to get a pass.

### 7. Trace, self-check, summarize (BP7, BP8, BP9)
- `show <ID>` gives the links of a case or an interface in both directions; the run
  records tie each result to its case and to the build.
- Apply `.claude/docs/checklists/software-integration-test.md` to the cases and their
  code, and `.claude/docs/checklists/plan.md` to a drafted strategy. Show findings as
  proposals; correct what the user accepts.
- `/review` cites `software-integration-test v1`; before builds and runs exist the part
  "Builds and results" is `not-applicable`.
- Summarize as "Summary for the user" in `references/building-and-running.md` says.

## Writing

- Show the derivation table and ask, for example: "May I write these N integration test
  cases to `verification/software-integration/` and their functions to
  `tests/integration/test_detection.c`?" Ask separately before writing a plan, a double
  or a change to the runner.
- IDs: `python tools/record.py next-id software-integration-test` or `next-id plan`.
  Status `draft`. Before changing an approved item, say that its approval becomes stale.

## Checks before you finish

Run `python tools/traceability.py check --all`.
- `FORMAT`, `SCHEMA` and `LINK` findings on items written in this session: fix them.
- `COV-13`, `COV-17`, `COV-18`, `COV-35` to `COV-38` for the steps in scope: report
  each as it is, with what would close it. A pending `COV-36` is "waits for the code".
- `COV-36` "changed after build" and `COV-38` "the run does not describe it" mean the
  records describe older software: build and run again. Do not explain them away.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. Per step: build record and result, run record, verdicts, cases not run with reasons -
   or `NOT ASSESSED` and why.
3. Failed cases and where each goes; questions for the architect; `query` items written.
4. The remaining findings of the check that concern these items.
5. Next: `/review` for strategy and test cases; `/sw-unit-implement`, `/sw-detailed-design`
   or `/sw-architecture` for defects; `/sw-qualification-test` on the build of the last
   step; `/baseline` to record who was told the results.

## Do not

- Do not set `status` to anything but `draft`, and do not write a review record.
- Do not type or edit a build record, a run record, a manifest or a result file.
- Do not take an expected result from the code, and do not change a case to match it.
- Do not replace an integrated component by a double, or leave a case out, to get a
  step through.
- Do not change the code under test, and do not copy or adapt a runner without asking.
