---
name: sys-qualification-test
description: "Test the integrated system against the system requirements (Automotive SPICE SYS.5): system qualification test strategy with regression rules, test cases derived from the system requirements and their verification criteria, bench or vehicle procedures, runs on the system build of the last integration step recorded from the bench's report, and the traceability between requirements, cases and results. Use when the system is to be qualified for a release or again after a change, or when the trace check reports COV-16, COV-17, COV-18, COV-49 or no approved system-qualification-test plan (COV-27)."
argument-hint: "[system requirement IDs, 'strategy', 'run', a bench report to record, or nothing to work on every open qualification finding]"
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *), Bash(git status *), Bash(git rev-parse *)
---

# System qualification test (SYS.5)

Shows that the integrated system meets its system requirements, looked at from outside:
stimuli at the system's interfaces to its environment, results at its outputs and at the
measurement points the strategy names. The result is a `plan` and
`system-qualification-test` items in state `draft`, ready for `/review`; bench or vehicle
procedures; final `test-run` records of level `system-qualification` on the system build
of the last integration step. The toolkit does not reach hardware: cases are specified
and traced here, executed on a bench, a test vehicle or the target in its environment, and
the results arrive as the bench's report. The agent `system-test-engineer` may draft
cases and turn bench reports into records; the questions to the user stay with this skill.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SYS.5.BP1 Develop system qualification test strategy including regression test strategy | writes the strategy with the user: test object, environment, stimuli and measurement points, regression | `plan` of kind `system-qualification-test` |
| SYS.5.BP2 Develop specification for system qualification test | derives cases from each requirement and its verification criteria | `system-qualification-test` items |
| SYS.5.BP3 Select test cases | chooses the cases of a run by the strategy and the release, and says how | `selection` and `not-run` reasons in the run |
| SYS.5.BP4 Test integrated system | records the bench's report of the cases run on the build of the last integration step | `test-run` naming the build |
| SYS.5.BP5 Establish bidirectional traceability | `verifies` links to requirements; results keyed by case | links; `matrix`, `show` output |
| SYS.5.BP6 Ensure consistency | self-checks against the checklist; the evidence comes from `/review` | proposed findings; review record |
| SYS.5.BP7 Summarize and communicate results | summarizes from tool output; `/baseline` records who was told | summary; `communication-record` |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. `SYS.5` not in `scope.processes`: stop. "SYS.5 is out of scope for this project."
3. Run `python tools/traceability.py status` and `python tools/traceability.py check --all`.
4. Cases need approved system requirements: `list --type system-requirement --status
   approved`. Name and leave out a requirement in draft or in review (`UPSTREAM`).
5. Runs need the integrated system. With SYS.4 in scope that is a successful system build
   of the last step of the approved system-integration plan: `status` names it; `COV-49`
   on a run means it tested an older build - `/sys-integration-test` first. Without
   SYS.4, the strategy names where the integrated system comes from.
6. `COV-27` for kind `system-qualification-test`: do step 1 first. Cases may be drafted
   against a strategy the user agreed in this session; no run is recorded before the
   strategy is approved.

## Steps

### 1. Strategy (BP1)
- Search `plans/` for `kind: system-qualification-test`. An approved strategy rules every
  step below.
- If there is none, read `references/strategy-template.md`, ask the user the decisions
  listed there, and draft the plan. Environment, stimuli, measurement points, what is
  left to the vehicle, and tester independence are the user's decisions.

### 2. Decide what to work on
- With arguments: the named requirements. Without: every `COV-16`, `COV-17`, `COV-18`
  and `COV-49` finding and every `SUSPECT` on a qualification test.
- `python tools/traceability.py matrix`, table `verifies: system-qualification-test ->
  system-requirement`. After a change, `impact <ID>` of the changed item.
- Tell the user the list and ask whether it is the scope of this session.

### 3. Derive the test cases (BP2)
- Read `references/deriving-test-cases.md`. Read each requirement: `Statement`,
  `Verification criteria`, `Analysis`, `release`, `asil`. Every criterion becomes at
  least one step with its values and times as the expected result.
- A requirement whose `verification_method` is not `test` gets no case; `COV-16` asks for
  its review instead.
- Where a criterion cannot be stimulated on the integrated system, say why in the case
  and name the level or the method that shows it; never drop the criterion silently.
- Where a criterion is not testable as written, that is a question for
  `/sys-requirements`, not a guess.

### 4. Bench or vehicle procedures (BP2, BP4)
- A case run on a bench or in a vehicle has `execution: manual` or names the bench's
  script in `script`; its procedure lives with the bench. Do not write code for hardware
  the project does not have; ask where the procedure is kept.
- Stimuli only at the interfaces the strategy names; observation only at outputs and at
  named measurement points.

### 5. Select and record (BP3, BP4)
Follow the sequence in `references/running-and-recording.md`.
- Clean tree, commit or tag named; the system build record of the last integration step
  made from it exists (`status`).
- Record with `python tools/record.py test-run --level system-qualification --results
  <file> --build <BLD-ID> --item-under-test <configuration> --environment <bench or
  vehicle> --selection "<rule>"`. The bench's JUnit XML report is recorded the same way
  with `--results <report>.xml`; the cases are found by their IDs in the test names.
- A failing case is information: report it with its log line and propose where it goes;
  the user decides. Never weaken, delete or skip a case to get a pass.

### 6. Trace, self-check, summarize (BP5, BP6, BP7)
- `show <SYR-ID>` lists the cases that verify a requirement; the run record ties each
  result to its case and to the build.
- Apply `.claude/docs/checklists/system-qualification-test.md` to the cases and their
  procedures, and `.claude/docs/checklists/plan.md` to a drafted strategy. Show findings
  as proposals; correct what the user accepts.
- `/review` cites `system-qualification-test v1`; before a run exists the part "Results"
  is `not-applicable`.
- Summarize as "Summary for the user" in `references/running-and-recording.md` says.

## Writing

- Show the derivation table (requirement, criterion, case and step) and ask, for
  example: "May I write these N qualification test cases to
  `verification/system-qualification/`?" Ask separately before writing a plan.
- IDs: `python tools/record.py next-id system-qualification-test` or `next-id plan`.
  Status `draft`. Before changing an approved item, say that its approval becomes stale.

## Checks before you finish

Run `python tools/traceability.py check --all`.
- `FORMAT`, `SCHEMA` and `LINK` findings on items written in this session: fix them.
- `COV-16`, `COV-17`, `COV-18` and `COV-49`: report each as it is, with what would
  close it.
- `COV-49` "tested an older build" means the system changed after the run: qualify the
  new build. Do not explain it away.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. Per requirement: cases, verdicts in the latest run, criteria shown elsewhere and
   where; the build and configuration qualified, and the environment - or `NOT ASSESSED`
   and why.
3. Failed cases and where each goes; questions about requirements.
4. The remaining findings of the check that concern these items.
5. Next: `/review` for strategy and cases; `/problem-resolution` for failed cases;
   `/sys-requirements`, `/sys-integration-test` or `/sys-architecture` for defects;
   `/baseline` for the release and to record who was told the results.

## Do not

- Do not set `status` to anything but `draft`, and do not write a review record.
- Do not type or edit a run record or a result file, and do not write a bench result
  you did not receive as the bench's own report.
- Do not take an expected result from the architecture, the design or the code.
- Do not require a measurement point the strategy does not name, and do not read
  internal variables of an element in a test.
- Do not change the system under test.
