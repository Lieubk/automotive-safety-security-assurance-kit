---
name: sw-unit-implement
description: "Write the C99 code of software units from their approved unit design, exactly as designed, for AUTOSAR Classic targets (Automotive SPICE SWE.3.BP8). Use when an approved software unit is reported as designed but not implemented, when the trace check reports COV-10 or COV-22 for a unit, or when a defect in the code or an approved design change has to be carried into the code."
argument-hint: "[unit IDs, or nothing to work on every approved unit whose code is missing or differs from its design]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *)
---

# Software unit implementation (SWE.3.BP8)
> Toolkit root: `${CLAUDE_PLUGIN_ROOT}` - where this shows a placeholder instead of a folder, it is the repository you are in. The `tools/`, `schema/`, `aspice/`, `iso-26262/`, `iso-sae-21434/`, `examples/` and `.claude/docs/` named here and in the references lie in the toolkit root; run its tools from the project folder as `python "<toolkit root>/tools/<script>.py"`.

Writes header and source of a software unit from its approved `software-unit` item, so
that every designed function exists with the designed name and signature and nothing
exists that the design does not contain. The design is the specification: this skill
adds no behaviour and never changes what a design item says. The one thing it enters
into the unit item is `source_files`, the list of the files it wrote; that entry is not
part of the content the design approval covers.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SWE.3.BP1 Develop software detailed design | not done here: `/sw-detailed-design` | - |
| SWE.3.BP2 Define interfaces of software units | not done here: `/sw-detailed-design`; the header is written from the designed contracts | - |
| SWE.3.BP3 Describe dynamic behavior | not done here: `/sw-detailed-design` | - |
| SWE.3.BP4 Evaluate software detailed design | not done here; code that breaks a limit of the evaluation is reported back to the design | - |
| SWE.3.BP5 Establish bidirectional traceability | creates the files the design names, registers them in `source_files`, names the unit item in every file header | `source_files`; no `COV-10` or `COV-11` finding for the unit |
| SWE.3.BP6 Ensure consistency | compares code and design element by element and self-checks against the checklist; the evidence itself comes from `/review` with the unit as subject and the code revision named | no `COV-22` finding; comparison table in the hand-over; review record with the hashes of the code, written by `/review` |
| SWE.3.BP7 Communicate agreed software detailed design | not done here: `/baseline` | - |
| SWE.3.BP8 Develop software units | writes header and source of each approved unit and builds them without warnings | the source files; the build output |

## Before you start

1. If there is no `project.yaml`, stop: "This project has no scope yet. Run
   `/aspice-start` first."
2. If `SWE.3` is not in `scope.processes`, stop: "SWE.3 is out of scope for this
   project. Units delivered from outside are registered with `/import-inputs`."
3. Run `python tools/traceability.py status` and `python tools/traceability.py check --all`.
   Every command of this skill takes `--project <dir>` when the project is not the
   current directory.
4. For every unit to implement, the `software-unit` item must have `status: approved`,
   and the check must report neither `COV-19`, `UPSTREAM` nor a `SUSPECT` "suspect
   link" for it.
   Otherwise stop for that unit: "UNT-0004 is not approved (<status, or the finding>).
   Code is written from an approved unit design only. `/sw-detailed-design` produces
   the design, `/review` approves it." Do not start "in advance" and do not offer to
   approve.
5. A `SUSPECT` line that names a source file ("the code is no longer the code that was
   reviewed") and `COV-30` mean that the code was changed after it was reviewed or
   verified. That does not stop the work; review and verification follow it again.
6. If the `component-design` of the unit's component is not approved, say so and ask
   whether to continue: the place of the unit in the component is not agreed yet.
7. `origin` of the unit must be `handwritten`. For `generated`, `reused` and
   `third-party` units read `references/special-code-and-safety.md` and write no code.
8. Read `platform` and `toolchain` in `project.yaml` (language, coding guideline,
   compiler) and ask where the project's coding guideline and naming convention are.
   They take precedence over `.claude/rules/c-code.md`, which loads when a file under
   `src/` is edited and applies where the project is silent.

## Steps

### 1. Decide what to implement
- With arguments: the named units, for example to correct a defect that a unit test,
  the analysis or a code review found. Without: approved handwritten units for which
  the check reports `COV-10` (designed but not implemented, or a listed file missing)
  or `COV-22` (design and code differ).
- Tell the user the list and ask whether it is the right scope for this session.

### 2. Read the design
- Read the unit item by ID and run `python tools/traceability.py show <UNT-ID>`.
- Read by ID: the interfaces it `realizes` and `uses`, the units it `uses` (their
  `functions`), the `component-design` of its component (`show <CMP-ID>` names it),
  the decisions that concern it. Read the requirements under `implements` for intent
  only: the unit item is the specification.
- The files: those in `source_files`; for a unit without code, those the
  `Static structure` of the component design names for it. If neither names them, that
  is a gap in the design (step 3).
- List what has to exist: files, functions with category, variables, types,
  constants, platform resources. Everything in the code comes from this list.

### 3. Check that nothing is left to decide
- Go through every function: can it be written without choosing anything that changes
  a result, an error reaction, a stored value or a signature?
- If not, or if design, interface and requirement contradict each other, do not fill
  the gap. Follow `references/design-problems.md`: stop work on the affected part,
  state the problem with the design element (`UNT-0003#AntiPinch_Step`), and take it
  to the owner of the design through the user. Unaffected functions may go on.

### 4. Write the header, then the source
- Read `references/from-design-to-code.md` before writing.
- Header: what the design makes visible to other units, and nothing else. Every
  function of category `public`, `scheduled` or `callback` is declared with exactly
  the designed name, return type and arguments.
- Source: every designed function defined, `local` ones as `static`; every entry of
  `data` with its designed type, scope and initial value; behaviour, error handling
  and protection as the sections of the unit item state them.
- A file the design does not name, a function another unit could call, or a global
  variable beyond the design is a design change, not an implementation detail: step 3.

### 5. Register the files
- A unit whose `source_files` already lists exactly the files written is left alone.
- Otherwise ask, then add `source_files` to the unit item and change nothing else in
  it: not the status, not a word of the design. `source_files` is not part of the
  content hash, so the design approval stays valid, and a unit inside a baseline needs
  no change request for this entry.
- From now on the check compares the design with the code and expects the code to be
  reviewed and verified.

### 6. Compare code and design
- Run `python tools/traceability.py check --all`. For a registered unit `COV-22`
  reports a designed function that is not defined, a function without `static` that
  the design lacks, and parameter types or a return type that differ from the design
  wherever the design states them. Correct every such finding in the code.
- The check does not compare parameter names, linkage against category, the header
  against the definitions, variables, types, constants or behaviour. Compare these by
  reading and write the table of `references/from-design-to-code.md` ("Comparison").
- If the code is right and the design is not, that is a design problem (step 3),
  never an edit of the item.

### 7. Build
- Read `references/build-and-report.md`. Take compiler and options from the project
  (`toolchain.compiler` in `project.yaml`, its build scripts, the approved `plan` of
  kind `unit-verification`), or ask. Do not choose weaker options than the project's.
- Build every file written. A warning is fixed in the code, not silenced.
- If no compiler is available, or the project's build cannot run here, the build is
  `NOT ASSESSED`: say which step did not run and why. Never report "builds" from
  reading the code.

### 8. Self-check
Apply `.claude/docs/checklists/software-unit-code.md` to the code. For a unit with an
ASIL also `references/special-code-and-safety.md` ("Units with an ASIL"). Show the
findings to the user as proposals and correct what they accept.

## Writing

- Show the list of files with, per file, the functions and variables it will hold,
  and ask: "May I write these N files for UNT-0004?" Ask separately before step 5.
- Paths: exactly those the design names. In an item, only `source_files` is written;
  its status stays as it is.
- When changing code that already exists, say first that the review of that code and
  the test and analysis runs describe the old code and have to be repeated.
- No commit, tag or baseline unless the user asks for it. Say that the review and the
  runs that follow name a commit, so the code has to be committed before them.

## Checks before you finish

Run `python tools/traceability.py check --all`.
- `COV-10`, `COV-11` and `COV-22` for the units of this session should be gone. If one
  remains, report it with the reason.
- Expected until `/review` has covered the code: `CONSISTENCY` "a review of the code
  against the design is not evidenced" for code registered for the first time,
  `SUSPECT` "the code is no longer the code that was reviewed" for changed code. Say so.
- Expected until `/sw-unit-verify` has run: `COV-12`, `COV-28`, `COV-29` (no test, no
  analysis, no coverage, a designed function no test names) and `COV-30` (the latest
  runs do not describe the present code). Say so.
- State the build verdict per unit and build: `PASS`, `CONCERNS`, `FAIL` or
  `NOT ASSESSED`, with the compiler, its version and the options, or what was missing.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. Per unit: the files written and registered, the comparison table, the build verdict.
3. Design problems raised, numbered, each with the design element, the proposed
   options and who has to decide; the functions that wait for the answer.
4. Deviations from the coding rules that need a justification a person accepts, and
   file-local helper functions the design does not name.
5. The remaining findings of the check that concern these units.
6. Next, after every change to the code, in the order the unit verification strategy
   gives: `/sw-unit-verify` for a test of every designed function and for test and
   analysis runs of the present code; `/review` with the unit as subject, the checklist
   `.claude/docs/checklists/software-unit-code.md` (cited as `software-unit-code v2`)
   and the commit named. Only a review recorded with the code revision counts as a
   review of the code: its record stores the hash of every source file. A person
   gives the verdict.

## Do not

- Do not write code for a unit whose design is not approved or whose approval is stale.
- Do not change anything in a `software-unit` item except `source_files`, nothing at
  all in a `component-design`, and do not set a status.
- Do not patch a design gap or a design error silently in code, and do not leave a
  `TODO` in its place.
- Do not add a public function, a global variable or a file the design does not name.
- Do not silence a warning with a cast, a pragma or a changed option.
- Do not edit generated or third-party files by hand.
- Do not write unit tests here, and do not call the unit tested, reviewed or verified.
