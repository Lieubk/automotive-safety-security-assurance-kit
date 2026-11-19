---
name: sys-integration-test
description: "Integrate the system step by step and test it against the system architecture (Automotive SPICE SYS.4): system integration strategy with its steps and regression rules, integration test cases derived from system interfaces, elements and views, a build record per step, test runs on those builds from the bench's reports, and the traceability between them. Use when system elements are to be integrated or integrated again after a change, or when the trace check reports COV-15, COV-17, COV-18, COV-46, COV-47, COV-48, COV-49 or no approved system-integration plan (COV-27)."
argument-hint: "[step names, system interface IDs, 'strategy', 'build', 'run', or nothing to work on every open system integration finding]"
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *), Bash(git status *), Bash(git rev-parse *)
---

# System integration and integration test (SYS.4)

Puts the system together in the order the strategy gives - hardware samples, mechanical
parts, the software of the system - and shows at each step that the integrated elements
work together as the system architecture says. The result is a `plan` with its
`integration_steps` and `system-integration-test` items in state `draft`, ready for
`/review`; a final `build-record` of level `system` per step and final `test-run`
records on those builds. Integration and tests are carried out on benches and samples
this toolkit does not reach: they are specified, traced and recorded here, and executed
there. Their results arrive as the bench's report.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SYS.4.BP1 Develop system integration strategy | writes the strategy with the user: the steps, which elements each adds, what stands in for the rest | `plan` of kind `system-integration` with `integration_steps` |
| SYS.4.BP2 Develop system integration test strategy including regression test strategy | in the same plan: what is tested per step, on which bench, by which method, and what is repeated after a change | sections `Approach` and `Criteria` |
| SYS.4.BP3 Develop specification for system integration test | derives test cases from system interfaces, element behaviour and views, each assigned to a step | `system-integration-test` items |
| SYS.4.BP4 Integrate system items | records each step's configuration from the manifest the integrator provides: element versions, the software build, the doubles | `build-record` of level `system` per step |
| SYS.4.BP5 Select test cases | chooses the cases of a run by the strategy's rules, and says how | `selection` and `not-run` reasons in the run |
| SYS.4.BP6 Perform system integration test | turns the bench's report into a run on the build of the step; the bench executes | `test-run` of level `system-integration` naming the build |
| SYS.4.BP7 Establish bidirectional traceability | `verifies` links, `step`, and run records keyed by test case and build | links; `matrix` and `show` output |
| SYS.4.BP8 Ensure consistency | self-checks against the checklist; the evidence comes from `/review` | proposed findings; review record written by `/review` |
| SYS.4.BP9 Summarize and communicate results | summarizes from tool output; `/baseline` records who was told | summary; `communication-record` |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. `SYS.4` not in `scope.processes`: stop. "SYS.4 is out of scope for this project."
3. Run `python tools/traceability.py status` and `python tools/traceability.py check --all`
   (every command takes `--project <dir>`).
4. Test cases need an approved architecture: `list --type system-interface --status
   approved`, and the same for `system-element` and for `architecture-view` of level
   system. Name and leave out what is in draft or in review: its cases could not be
   approved (`UPSTREAM`).
5. A system build needs the integrated elements. Where the system has a software
   element, its software build must exist first: the last step of `/sw-integration-test`
   with a final, successful build. Strategy and test cases can be written before;
   recording builds and runs waits. Samples and benches are the user's: ask what exists.
6. If the check reports `SUSPECT` or `CONSISTENCY` on an element or interface that a
   step integrates, say so first: tests on top of it inherit the doubt.
7. `COV-27` for kind `system-integration`: do step 1 first. No build and no run is
   recorded before the strategy is approved; `record.py build` refuses.

## Steps

### 1. Strategy (BP1, BP2)
- Search `plans/` for `kind: system-integration`. An approved strategy rules every step
  below; where the project cannot follow it, say so.
- If there is none, read `references/strategy-template.md`, ask the user the decisions
  listed there, and draft the plan. The order of the steps, the elements left to others,
  the benches and the regression rules are the user's decisions.
- `check` reports `COV-46` for an element that no step integrates and that is not a
  double of the last step, for one integrated twice, for an element a step names that
  does not exist, and for duplicate step names. External elements are never integrated.

### 2. Decide what to work on
- With arguments: the named steps or interfaces. Without: every finding of `COV-15`,
  `COV-17`, `COV-18`, `COV-46` to `COV-49` and every `SUSPECT` on an integration test.
- `python tools/traceability.py matrix`, table `verifies: system-integration-test ->
  ...`. After a change, `impact <ID>` of the changed item and "Regression" in
  `references/integrating-and-recording.md`.
- Tell the user the list and ask whether it is the scope of this session.

### 3. Derive the test cases (BP3)
- Read `references/deriving-test-cases.md`. Work from the items, never from the
  behaviour of a sample: the `Definition` of each system interface (signals, ranges,
  units, timing, protocol), the `Dynamic behavior` of the elements, the `sequence`,
  `state-machine`, `fault-reaction` and `communication` views.
- Assign each case the first step whose configuration contains everything it needs
  (`step`). `verifies` names the interfaces, elements or views whose behaviour it shows;
  `asil` is the highest of those.
- Where the architecture does not say what shall happen at an interface, list a question
  for the architect (`/sys-architecture`); for an imported item write a `query`.
- The `system-test-engineer` agent may draft the cases and the bench procedures; what it
  returns is a proposal that the user confirms.

### 4. Bench procedures and simulations (BP3, BP6)
- A case with `execution: automated` names a `script` the bench runs; a case the bench
  operator carries out by hand is `manual`. Both are specified here, neither is run here.
- Ask the user which bench or rig each step uses, how an external element is simulated
  (rest-bus, load, vehicle, environment), and what the bench reports per case. The test
  case ID must appear in the report, so that the result can be found.
- Set `script` once the bench procedure exists.

### 5. Record each integration step (BP4)
Follow the sequence in `references/integrating-and-recording.md`.
- The integrator assembles the step and writes the manifest: sample, tag or drawing of
  each element, the software build, the doubles. Never write a manifest from memory or
  from the architecture.
- `python tools/record.py build --level system --step <name> --manifest <file>
  --item-under-test <configuration>` writes the record. A failed build is recorded when
  the user wants it on record; nothing is tested on it.
- The tool prints elements the step should contain but the build lacks. Report them.

### 6. Select and record the run (BP5, BP6)
- Select by the strategy: all cases of the step, the regression set, or the cases
  `impact` names for a change. Cases of earlier steps may be in the run as regression;
  cases of later steps cannot.
- The bench executes. Record its report with `python tools/record.py test-run --level
  system-integration --results <file.json or report.xml> --build <BLD-ID>
  --item-under-test <configuration> --environment <bench> --selection "<rule>"`. A case
  not run is `not-run` with its reason.
- A failing test is information: report it with the bench's log line and propose where
  it goes ("A failing test" in `references/integrating-and-recording.md`); the user
  decides. Never weaken, delete or skip a case to get a pass.

### 7. Trace, self-check, summarize (BP7, BP8, BP9)
- `show <ID>` gives the links of a case or an interface in both directions; the run
  records tie each result to its case and to the build.
- Apply `.claude/docs/checklists/system-integration-test.md` to the cases and bench
  procedures, and `.claude/docs/checklists/plan.md` to a drafted strategy. Show findings
  as proposals; correct what the user accepts.
- `/review` cites `system-integration-test v1`; before builds and runs exist the part
  "Builds and results" is `not-applicable`.
- Summarize as "Summary for the user" in `references/integrating-and-recording.md` says.

## Writing

- Show the derivation table and ask, for example: "May I write these N integration test
  cases to `verification/system-integration/`?" Ask separately before writing a plan or
  a bench procedure.
- IDs: `python tools/record.py next-id system-integration-test` or `next-id plan`.
  Status `draft`. Before changing an approved item, say that its approval becomes stale.

## Checks before you finish

Run `python tools/traceability.py check --all`.
- `FORMAT`, `SCHEMA` and `LINK` findings on items written in this session: fix them.
- `COV-15`, `COV-17`, `COV-18`, `COV-46` to `COV-49` for the steps in scope: report each
  as it is, with what would close it. A step without a bench report "waits for the bench".
- `COV-47` "the system build is older than the software" and `COV-49` (a newer build of
  the step exists than the one the latest run tested) mean the records describe older
  configurations: integrate, record and run again. Do not explain them away.
- `COV-47` compares with software builds only where SWE.5 is in scope, because only then
  does this repository record them. Where the software comes from elsewhere, the system
  build names the delivered software version in its manifest, and a newer delivery is
  seen through `/import-inputs` or `/supplier-monitoring`, not by the trace check: say so
  in the hand-over.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. Per step: build record and result, run record, verdicts, cases not run with reasons -
   or `NOT ASSESSED` and why (no bench report yet, no sample).
3. Failed cases and where each goes; questions for the architect; `query` items written.
4. The remaining findings of the check that concern these items.
5. Next: `/review` for strategy and test cases; `/problem-resolution` for confirmed
   defects; `/sw-integration-test`, `/sys-architecture` or `/sw-requirements` as the
   defect requires; `/sys-qualification-test` on the build of the last step; `/baseline`
   to record who was told the results (`--practice SYS.4.BP9`).

## Do not

- Do not set `status` to anything but `draft`, and do not write a review record.
- Do not type or edit a build record, a run record, a manifest or a result file, and do
  not state that a test was executed that nobody ran on a bench.
- Do not take an expected result from the behaviour of a sample, and do not change a
  case to match it.
- Do not integrate an external element, do not replace an integrated element by a
  double, and do not leave a case out to get a step through.
- Do not change the elements under test and do not run a bench: this toolkit does not
  reach hardware.
