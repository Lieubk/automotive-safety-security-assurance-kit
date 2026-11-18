# Power window control with anti-pinch protection - worked example

A small but complete docs-as-code project: the software of a power window control unit
for one door, with one DC motor, one Hall sensor on the motor shaft, an up/down switch
with one-touch closing, and anti-pinch protection (ASIL B; comfort functions QM).
Every engineering artifact is one Markdown file with YAML front matter, following
[schema/item-format.md](../../schema/item-format.md) and
[schema/items.yaml](../../schema/items.yaml).

**All content is invented demonstration data.** The product, the customer documents,
every name, number, threshold and timing are made up for this example. Nothing here is
taken from a real project, and no conformance with any regulation or standard is
claimed.

## What the example shows

The project is a **software supplier**. It receives system requirements, system
architecture elements and system interfaces from its customer (imported, read-only)
and is responsible for:

| Process | In the example |
|---|---|
| SWE.1 Software Requirements Analysis | 9 software requirements with verification criteria and analysis, traced to the imported system items |
| SWE.2 Software Architectural Design | 6 components, 8 interfaces, 5 views (structure, state machine, sequence, execution model, resource summary), 1 design decision |
| SWE.3 Software Detailed Design and Unit Construction | 2 component designs, 3 software units with function contracts, and the C code of these units |
| SWE.4 Software Unit Verification | 20 unit test cases with executable tests |
| SUP.8 Configuration Management | everything is text under version control; baselines are generated from it |

Two of the four application components (window position acquisition and anti-pinch
detection) are developed in the project, down to code and unit tests. The other two
(command logic and motor actuation) are reused from an earlier product and appear at
architecture level only, as does the customer's basic software.

Review records, test runs, static analysis runs, baselines and communication records
are not written by hand. They are generated from tool runs and stored under `records/`
and `verification/runs/`.

## Item files

| Type | Prefix | Folder | Count |
|---|---|---|---|
| System requirement (imported) | SYR | `spec/system/requirements` | 4 |
| System element (imported) | SYE | `spec/system/architecture` | 2 |
| System interface (imported) | SYI | `spec/system/architecture` | 3 |
| Software requirement | SWR | `spec/software/requirements` | 9 |
| Software component | CMP | `spec/software/architecture` | 6 |
| Software interface | IFC | `spec/software/architecture` | 8 |
| Architecture view | VIEW | `spec/views` | 5 |
| Design decision | ADR | `spec/decisions` | 1 |
| Component design | CDS | `spec/software/design` | 2 |
| Software unit | UNT | `spec/software/design` | 3 |
| Unit test case | UT | `verification/unit` | 20 |

A good place to start reading is `spec/views/VIEW-0001.md` (structure), then
`spec/views/VIEW-0003.md` (what happens when the glass meets an obstacle), then
`spec/software/design/UNT-0003.md` with `src/antipinch/AntiPinch.c`.

## Code

| Unit | Files | Tests |
|---|---|---|
| UNT-0001 HallCapture | `src/windowpos/HallCapture.h`, `.c` | `tests/unit/test_HallCapture.c` (UT-0001 to UT-0005) |
| UNT-0002 WindowPos | `src/windowpos/WindowPos.h`, `.c` | `tests/unit/test_WindowPos.c` (UT-0006 to UT-0012) |
| UNT-0003 AntiPinch | `src/antipinch/AntiPinch.h`, `.c` | `tests/unit/test_AntiPinch.c` (UT-0013 to UT-0020) |

The code is C99 without dynamic memory, recursion or floating point. Every file under
`src/` belongs to exactly one software unit. The units include `Std_Types.h` and
`SchM_WindowPos.h`, which on the target come with the customer's basic software;
`tests/unit/host/` holds minimal stand-ins for host builds.

## Build and run the unit tests

Requirements: Python 3.6 or later and a C compiler - `cc`, `gcc` or `clang` on the
path, or Visual Studio with the C++ workload on Windows (found automatically).

```
python tests/unit/run_tests.py
```

The script builds one test program per unit with warnings treated as errors
(`-std=c99 -pedantic -Wall -Wextra -Werror`, or `/std:c11 /W4 /WX` for the Visual
Studio compiler), runs it and prints one line per test file and a total. Results:

| File | Content |
|---|---|
| `build/<test>.log` | compiler output and the verdict lines of the test program (`UT-0001 PASS` or `UT-0001 FAIL <file>:<line>`) |
| `build/unit-test-results.json` | compiler, time of execution and one verdict per test case, ready to be turned into a test run record |

The exit code is 0 only if every test case passed. `build/` is not under version
control.

## Check the traceability

From the root of the toolkit:

```
python tools/traceability.py --project examples/power-window check
python tools/traceability.py --project examples/power-window matrix
```
