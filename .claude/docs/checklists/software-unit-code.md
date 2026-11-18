# Software unit code review checklist

Version 1. Applies to: the code of a `software-unit` (the files in its `source_files`),
reviewed against the design the unit item states. Supports: SWE.3.BP5, SWE.3.BP6,
SWE.3.BP8.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

The unit item is the subject of the review. The review counts as a review of the code
only when it is recorded with the code revision (`--item-under-test`): then the record
stores the hash of every file in `source_files` next to the content hash of the item.
A unit is reviewed with this checklist when its code is first registered and after
every later change of the code; the check asks for it with `CONSISTENCY` or `SUSPECT`
on the unit. The unit item itself stays approved throughout: registering code does not
change its content.

The design is the reference. Where code and design differ, the finding is against the
code unless the reviewer shows that the design is wrong; then it is a finding against
the design, which changes through its owner and a review with the design checklist,
never by an edit that makes it fit the code. The code of a unit with `origin:
generated`, `reused` or `third-party` is not read line by line with this checklist:
the script checks and SUC-51 apply to it.

## Preconditions

| ID | Check | How to check | Kind |
|---|---|---|---|
| SUC-01 | The design the code implements is approved at its current content | `check`: no `COV-19` finding on the unit | script |
| SUC-02 | No item the unit links to has changed since the design was reviewed | `check`: no `SUSPECT` finding "suspect link" on the unit | script |
| SUC-03 | The code under review is identified by a commit, and the files read are the files of that commit | ask for the commit; it goes into the record as `--item-under-test`, without which the record does not count as a review of the code | accountable |

## Code against design

| ID | Check | How to check | Kind |
|---|---|---|---|
| SUC-10 | Every file in `source_files` exists, and every file under the source roots belongs to exactly one unit | `check`: no `COV-10` and no `COV-11` finding | script |
| SUC-11 | Every designed function of category public, scheduled or callback is defined; no function without `static` is defined that the design lacks; parameter types and return type equal the design wherever it states them | `check`: no `COV-22` finding | script |
| SUC-12 | What the script does not compare agrees with the design as well: parameter names, the declarations in the header against the definitions, and the signature of any function whose types the design leaves open | read `functions` next to the header and the definitions | semantic |
| SUC-13 | Linkage follows the category: `local` functions are `static` and absent from the header; all others are declared in the header exactly once | read header and source | semantic |
| SUC-14 | Every entry of `data` exists with the designed type, scope and initial value, and the code has no file-scope or global variable beyond them | read `data` next to the source | semantic |
| SUC-15 | Types and constants of the design exist under their designed names with the designed members and values; no literal stands in for a designed constant | read `Behavior` next to header and source | semantic |
| SUC-16 | The code does what `Behavior` describes: every step, formula, rounding, limit, state and transition; the order of checks and updates where the design gives one | read `Behavior` next to the function bodies | semantic |
| SUC-17 | The code does nothing the design does not describe: no extra state, check, output or side effect, and nothing in the header beyond the design | read the header and the function bodies for what has no counterpart in the design | semantic |
| SUC-18 | Every row of `Error handling` and every `errors` entry is implemented at the place the design names, with the designed reaction and report | read the section next to the code | semantic |
| SUC-19 | On every failure path outputs and stored data are left as the postconditions say | follow each failure path to the `return` | semantic |
| SUC-20 | Preconditions the design tells the function to check are checked; the others are not silently assumed to be checked elsewhere | read `preconditions` and `errors` next to the code | semantic |
| SUC-21 | Shared data is accessed only under the designed protection; enter and exit of an exclusive area pair up on every path; nothing inside it calls out of the unit | read `protection` of each `data` entry and `platform` next to the code | semantic |
| SUC-22 | The unit touches only the platform resources and interfaces the design names; its includes match the `uses` links | read `platform`, `uses` and the include lines | semantic |
| SUC-23 | Each file header names the unit item, and the comments of functions, types and constants agree with the design | read the comments next to the item | semantic |
| SUC-24 | File-local helper functions that the design does not name add no behaviour of their own | read each such function and its callers | semantic |

## Coding rules

Rules: the project's coding guideline, and `.claude/rules/c-code.md` where it is silent.
Static analysis and conformance to a guideline set are evidence of unit verification
(`/sw-unit-verify`; `COV-12` and `COV-30` report when it is missing or outdated). This
review reads their results where they exist and does not replace them.

| ID | Check | How to check | Kind |
|---|---|---|---|
| SUC-30 | Every source file of the unit compiles with the project's compiler and options without error or warning | the build output for the reviewed commit: compiler line and result. Without a build the result of this check is `not-assessed` | script |
| SUC-31 | What compiler and analyser have reported for this code so far is corrected, or justified at its place; where no analysis has run yet, the review says so | the build output; the unit's entry in the latest static analysis run, unless a `COV-30` finding says that run describes older code | semantic |
| SUC-33 | The rules no tool checked hold: named constants, bounded loops, single exit, checked return values, range checks before use, results limited to their range | read the code against the rules whose check is `review` | semantic |
| SUC-34 | Functions are inside the project's limits for complexity, nesting depth, parameters and length | metric output of the analyser; without one, count by reading and say so | semantic |
| SUC-35 | Arithmetic cannot overflow or lose range unnoticed; every cast has a visible reason; every intended wrap-around is commented | read each expression with a cast, a subtraction or a multiplication | semantic |
| SUC-36 | No `TODO`, `FIXME`, commented-out code, debug output or test-only branch | search the files for these markers; read what the search cannot find | semantic |
| SUC-37 | Comments explain intent, units and scaling, and none contradicts the code | read the comments | semantic |
| SUC-38 | Every deviation from a coding rule is marked at its place with the rule and the reason | search for the project's deviation marker; compare with the analyser output | semantic |
| SUC-39 | Each deviation was accepted by the person entitled to accept it | ask who accepted which deviation, and when | accountable |

## Units with an ASIL

| ID | Check | How to check | Kind |
|---|---|---|---|
| SUC-40 | Every designed input check sits before the first use of the value and before any stored data changes | follow each argument from the function entry | semantic |
| SUC-41 | A state variable with a value outside its set leads to the designed reaction | read the `default` branches | semantic |
| SUC-42 | The code adds no safety mechanism of its own and leaves none of the designed ones out | compare `Error handling` with the code in both directions | semantic |
| SUC-43 | Defensive branches that a test cannot reach are marked with the reason | read each `default` branch and each check whose condition the callers rule out | semantic |
| SUC-44 | The unit calls no code of a lower ASIL and shares no variable with it, unless the design says so | read the calls and includes against `uses` and the `asil` of the targets | semantic |
| SUC-45 | The review has the form and the independence the project's plans require for this ASIL | ask who reviewed, and compare with the plan | accountable |

## Closing

| ID | Check | How to check | Kind |
|---|---|---|---|
| SUC-50 | Design problems raised while implementing are decided, and none of them leaves the reviewed code resting on an assumption | ask the author for the list and its state | accountable |
| SUC-51 | For a generated, reused or third-party unit: the files are unchanged from what the generator or the source delivered, and their version is stated | ask for the version and how "unchanged" was established | accountable |
| SUC-52 | The reviewer did not write the unit | ask | accountable |
