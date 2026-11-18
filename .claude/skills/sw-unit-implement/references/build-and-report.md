# Building the unit and reporting the result

A unit is not handed over as "written" before a compiler has seen it. This page says
which build counts, how to run it, and what to report when it could not run.

## Which build

"Builds without warnings" means: every source file of the unit compiles with the
compiler and the options the project uses for the product, and the output holds no
error and no warning. Find them in this order:

1. `project.yaml`: `toolchain.compiler` names compiler and version, `platform.language`
   the language standard, `platform.coding_guideline` the guideline set.
2. The project's build or test scripts and their options. In the worked example
   `tests/unit/run_tests.py` compiles each unit with warnings treated as errors
   (`-std=c99 -pedantic -Wall -Wextra -Werror` for gcc and clang, `/std:c11 /W4 /WX`
   for the Visual Studio compiler) and prints the compiler it used.
3. The approved `plan` of kind `unit-verification`, section `Environment and tools`.
4. If none of these says it, ask the user. Do not pick a compiler and options and
   call them the project's.

Two builds are often possible, and they are reported separately:

| Build | Shows | Does not show |
|---|---|---|
| Target build: the project's cross compiler with the product's options | the code is accepted by the compiler that produces the product | - |
| Host build: a compiler on the development computer, strict options | the code is valid C for that compiler and free of its warnings | that the target compiler accepts it; sizes, alignment and byte order of the target |

Headers that the basic software provides on the target (`Std_Types.h`, the header with
the exclusive area services) are replaced on a host by stand-ins. Stand-ins are test
equipment: in the worked example they are kept in `tests/unit/host/`, never under
`src/`. If a host build needs a stand-in that does not exist, say so and ask; it
belongs to the test environment that `/sw-unit-verify` sets up.

## How to run it

- Prefer the project's own build or test script. It uses the agreed options and keeps
  the output.
- Where there is only a compiler, compile each source file of the unit without
  linking, with the include paths the unit needs and with warnings as errors. With
  gcc or clang, for example:
  `gcc -std=c99 -pedantic -Wall -Wextra -Werror -fsyntax-only -I<include dir> <file>.c`
  Adapt compiler, standard and options to the project; never drop an option the
  project uses.
- Check that the header stands alone: compile a source file that contains nothing but
  the include of the header.
- First check that the compiler is there (`<compiler> --version`). The shell asks the
  user for permission the first time a build command runs; that is intended.
- Keep the complete output. Quote the compiler's version line and the result in the
  hand-over.

## When the compiler reports something

- An error or a warning is a defect in the code until shown otherwise. Fix the cause:
  the missing prototype, the narrowing conversion, the unused variable.
- Never make a warning disappear with a cast that only silences it, a pragma, a
  changed or removed option, or an extra pair of parentheses nobody understands.
- A warning you consider wrong or unavoidable stays visible. Report it with the line,
  the message and your reason; whether it is accepted as a deviation is decided by the
  person the project names for that, not by this skill.
- A warning in a header you did not write (platform, another unit) is reported to the
  user with its origin. Do not edit that header.

## The verdict

One line per unit and per build, in the vocabulary of the working agreement:

| Verdict | When |
|---|---|
| `PASS` | every source file of the unit was compiled with the stated compiler and options; no error, no warning |
| `CONCERNS` | it was compiled, and warnings remain that a person may accept with a reason; each is listed |
| `FAIL` | an error remains, or a warning under options that treat warnings as errors |
| `NOT ASSESSED` | the build did not run: no compiler, a missing header or stand-in, a script that did not start. Nothing was established |

Always give the facts with the verdict: compiler and version as the tool printed them,
the options, the files compiled, and where the output is. The form of the report
(the values are placeholders, not results):

```
UNT-0003 AntiPinch
  Host build:   PASS - <compiler and version line>, -std=c99 -pedantic -Wall -Wextra
                -Werror, src/antipinch/AntiPinch.c, header compiled alone; log <path>
  Target build: NOT ASSESSED - the target compiler is the customer's and is not
                installed here; to be built at integration
```

## What to report when no compiler is available

`NOT ASSESSED` is a result, and it is reported as prominently as a failure:

1. which build did not run, for which units and files;
2. why: the tool that was looked for and not found, the header that is missing, the
   first lines of the script's error output;
3. what was done instead: nothing. Reading code is not a build, and no statement such
   as "should compile" or "syntactically correct" replaces one;
4. what is needed to close it: the tool to install, or the exact command for the user
   to run where the compiler exists;
5. what follows: the build check of the code checklist stays open, and the unit is
   handed over as written but not built.

`/sw-unit-verify` compiles the unit again with warnings as errors before it runs any
test, and keeps the compiler output with the test evidence. That log, attached to a
final run record that names the commit and stores the hash of every source file, is
the recorded evidence of the warning-free build. This skill writes no record of its
own. When the code changes afterwards, `COV-30` reports that the run no longer
describes it.

## What this skill does not establish

- Conformance to a coding guideline set. That needs the analyser and rule set the
  project names; following `.claude/rules/c-code.md` does not show it.
- Absence of run-time errors, and correct behaviour. Static analysis, unit tests and
  coverage belong to `/sw-unit-verify`.
- Timing, stack and memory use on the target.
