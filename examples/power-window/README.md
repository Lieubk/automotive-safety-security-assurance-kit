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

**Documents:** [documents/](documents/) holds 31 documents generated from these items -
specifications, architecture and design, test specifications and reports, traceability,
TARA, safety and cybersecurity plans and cases - as PDF, HTML, Word and Excel.

## What the example shows

The project is a **software supplier**. It receives system requirements, system
architecture elements and system interfaces from its customer (imported, read-only)
and is responsible for:

| Process | In the example |
|---|---|
| SWE.1 Software Requirements Analysis | 9 software requirements with verification criteria and analysis, traced to the imported system items |
| SWE.2 Software Architectural Design | 6 components, 8 interfaces, 5 views (structure, state machine, sequence, execution model, resource summary), 1 design decision |
| SWE.3 Software Detailed Design and Unit Construction | 2 component designs, 3 software units with function contracts, and the C code of these units |
| SWE.4 Software Unit Verification | a unit verification strategy with coverage targets per ASIL, 20 unit test cases with executable tests, a test run with measured coverage, a static analysis run |
| SWE.5 Software Integration and Integration Test | an integration strategy in two steps, 7 integration test cases with executable tests and doubles, a build record and a test run per step |
| SWE.6 Software Qualification Test | a qualification test strategy, 9 test cases - one per software requirement, every verification criterion a step - and a test run on the build of the last integration step |
| SUP.1 Quality Assurance | a quality assurance plan with two checks before the release candidate; a work product sample and a process audit with their findings and corrective actions, a quality report, an escalation |
| SUP.8 Configuration Management | a configuration management plan; everything is text under version control |
| SUP.9 Problem Resolution Management | a problem resolution strategy with urgent and alert rules; one problem report from recording to closure - a defect the qualification test found in a component taken over - with its alert and a trend report |
| MAN.3 Project Management | a project plan with four milestones, twelve work packages that deliver every item the project wrote, and one status report |

It also carries the cybersecurity of its part under ISO/SAE 21434, for the clauses
`scope.cybersecurity` names in `project.yaml`:

| Clause | In the example |
|---|---|
| 6 Project dependent cybersecurity management | a cybersecurity plan (`PLN-0008`) with a decision for every subclause of clauses 6 and 15, the reasons for what is tailored or left to the customer, and the TARA method: impact categories, attack-vector feasibility, a risk matrix of the project's own, `retain_up_to` 2; a cybersecurity case (`CSE-0001`) |
| 15 Threat analysis and risk assessment methods | on the customer's item definition (`ITM-0001`, imported): 2 assets, 3 damage scenarios, 3 threat scenarios with attack paths; one risk reduced by a cybersecurity goal (`CSG-0001`), one retained by a named decision and one shared with the customer, each argued in a claim (`CLM-0001`, `CLM-0002`); the hand-over to the customer (`CMR-0004`) |

Functional safety under ISO 26262 at ASIL B covers parts 2, 6, 8 and 9 (`scope.safety`):

| Part | In the example |
|---|---|
| 2 Management of functional safety | a safety plan (`PLN-0010`) with a decision per clause, the methods per table of parts 6 and 8 and where they are applied, two confirmation reviews (`CFM-0001`, `CFM-0002`), a safety case (`SFC-0001`) |
| 6 Software | the software requirements, architecture, units and verification already in the example, carrying ASIL B; testing on the target is the customer's |
| 8 Supporting processes | a development interface agreement with the customer (`PLN-0012`), a change management plan (`PLN-0011`), tool evaluations of the compilers and coverage tool (`TEV-0001`, `TEV-0002`) |
| 9 Analyses | an FMEA of the ASIL B components (`SAN-0001`) and a dependent failures analysis of WindowCmd (QM) next to them (`SAN-0002`) |

The hazard analysis, the safety goals and everything at system and vehicle level are the
customer's: the system requirements it delivered carry their ASIL.

The check reports one warning on purpose: the safety plan states no tool confidence
determination, because the toolkit does not carry the tables of the standard; a real
project types the one it applies, and `COV-71` then checks the tool evaluations against it.

The item, its cybersecurity concept, validation and everything after development are
the customer's: clauses 9 and 11 to 14 are not in scope, so the goal goes to the
customer instead of being refined here, and the software items carry
`security_relevant: false` as before.

Two of the four application components (window position acquisition and anti-pinch
detection) are developed in the project, down to code and unit tests. The other two
(command logic and motor actuation) are taken over unchanged from an earlier platform
release: their source is under `reused/`, they have no design items in this project, and
they enter the integration as received. The customer's basic software appears at
architecture level only; in the tests a double stands in for it.

Review records, build records, test runs and static analysis runs are not written by
hand. They are generated by `tools/record.py` from tool output and stored under
`records/`, `verification/builds/` and `verification/runs/`, with the tool output itself
under `verification/evidence/`.

## What the evidence is, and what it is not

| Record | What really happened | What it does not show |
|---|---|---|
| `RUN-0001` | 20 unit tests built warning-free with gcc and passed; gcov measured 100 % statement and 100 % branch coverage of all three units. The record stores a hash of every unit source and test file, so a later change of the code shows up in the trace check | behaviour on a target |
| `SAR-0001` | the defect analysis of the Visual Studio compiler ran over the three units and reported nothing | conformance to a coding guideline set such as MISRA C: no guideline analyser ran |
| `BLD-0001`, `BLD-0002` | the two integration steps were built with the Visual Studio compiler from the files the records list, with the hashes they list | that the customer's basic software and its configuration fit: the platform is a double |
| `RUN-0002`, `RUN-0003` | the integration tests of each step ran on the build of that step and passed | timing on the target |
| `RUN-0004` | the qualification tests ran on the software of the last step, on the host with the platform double, and passed | the software on the control unit; the qualification on the customer's bench |
| `PRB-0001` | while the qualification tests were written, the case of SWR-0008 failed on the command logic taken over: it ended the automatic closing 20 ms early. The code was corrected and the run recorded afterwards (`RUN-0004`) | the people, dates, the platform team and its release 3.2.1 are invented around that fact; the failing run was not recorded |
| `CMR-0001`, `PTR-0001` | written by `record.py communication` and `record.py problem-trends` | an alert anybody sent, an analysis anybody made: their texts say so |
| `QAR-0001` to `QAR-0003`, `CA-0001`, `CA-0002`, `CMR-0002`, `CMR-0003` | written by `record.py quality-check`, `quality-report` and `communication`; the facts in the quality records are what the tools showed at the time. The findings are true of the example: its reviews are fixtures (CA-0001), and no integration or qualification result was communicated (CA-0002) | a check by a quality engineer, an answer of a project lead: the texts say they are demonstration data |
| `PSR-0001` | written by `record.py status-report` from `progress` and `check` as of 2026-06-05; the planned and actual dates and efforts in the work packages are invented | an assessment by a person: its text says it is demonstration data |
| `CFM-0001`, `CFM-0002`, `SFC-0001` | written by `record.py confirmation-measure` and `safety-case` | a confirmation review or an argument by a person: their texts say they are demonstration data |
| `CSE-0001`, `CMR-0004` | written by `record.py cybersecurity-case` and `communication`; the case lists per work product of clauses 6 and 15 the items and their hashes as the tools showed them | an argument or an agreement of a person: their texts say they are demonstration data |
| `REV-0001` to `REV-0014` | nothing: they are fixtures that bind each item to a content hash, and the units to the hashes of their code, so that the trace check can be demonstrated. They are recorded as "external criteria: demonstration fixture" | a review. No person reviewed these items, no checklist was applied, and the records say so |

A real project replaces the review fixtures with reviews by named people against the
checklists under `.claude/docs/checklists/`, and adds the guideline check its coding
standard requires.

`python tools/traceability.py --project examples/power-window practices` shows what the
example does not have at all: no baseline exists, so the "communicate" practices of the
SWE processes are reported as `no evidence yet`. SUP.9.BP5 shows `evidence present`
although no problem was urgent and nothing had to be authorised: no rule objects, and
whether that is enough is for a person to judge.

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
| Software integration test case | SIT | `verification/software-integration` | 7 |
| Software qualification test case | SQT | `verification/software-qualification` | 9 |
| Plan | PLN | `plans` | 12 |
| Work package | WP | `plans/work-packages` | 12 |
| Safety analysis | SAN | `spec/safety/analyses` | 2 |
| Tool evaluation | TEV | `plans/tools` | 2 |
| Confirmation measure, safety case | CFM, SFC | `records/safety` | 2, 1 |
| Item definition (imported) | ITM | `spec/cybersecurity/item` | 1 |
| Asset, damage scenario, threat scenario | AST, DMG, THR | `spec/cybersecurity/tara` | 2, 3, 3 |
| Cybersecurity goal, claim | CSG, CLM | `spec/cybersecurity/goals` | 1, 2 |
| Cybersecurity case | CSE | `records/cybersecurity` | 1 |
| Project status report | PSR | `records/status` | 1 |
| Problem report | PRB | `records/problems` | 1 |
| Problem trend report | PTR | `records/problem-trends` | 1 |
| Communication record | CMR | `records/communication` | 4 |
| Quality record | QAR | `records/quality` | 3 |
| Corrective action | CA | `records/actions` | 2 |
| Build record | BLD | `verification/builds` | 2 |
| Test run, static analysis run | RUN, SAR | `verification/runs` | 4, 1 |
| Review record | REV | `records/reviews` | 14 |

A good place to start reading is `spec/views/VIEW-0001.md` (structure), then
`spec/views/VIEW-0003.md` (what happens when the glass meets an obstacle), then
`spec/software/design/UNT-0003.md` with `src/antipinch/AntiPinch.c`.

## Code

| Unit | Files | Tests |
|---|---|---|
| UNT-0001 HallCapture | `src/windowpos/HallCapture.h`, `.c` | `tests/unit/test_HallCapture.c` (UT-0001 to UT-0005) |
| UNT-0002 WindowPos | `src/windowpos/WindowPos.h`, `.c` | `tests/unit/test_WindowPos.c` (UT-0006 to UT-0012) |
| UNT-0003 AntiPinch | `src/antipinch/AntiPinch.h`, `.c` | `tests/unit/test_AntiPinch.c` (UT-0013 to UT-0020) |

| Component taken over | Files | Integrated in step |
|---|---|---|
| CMP-0002 WindowCmd | `reused/windowcmd/WindowCmd.h`, `.c` | application |
| CMP-0005 MotorDrive | `reused/motordrive/MotorDrive.h`, `.c` | application |

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

With gcc, `python tests/unit/run_tests.py --coverage` also measures statement and
branch coverage of each unit with gcov. `python tests/static/run_analysis.py` runs the
compiler's static analysis over the unit sources.

## Integrate and run the integration and qualification tests

```
python tests/integration/run_tests.py
python tests/qualification/run_tests.py
```

The integration runner reads the steps of `plans/PLN-0004.md` and the units' source
files with the toolkit's trace engine (it needs PyYAML; when a copy of this project
lives outside the toolkit, set the environment variable `TOOLKIT_DIR` to the toolkit's
folder), takes the files of the
components taken over and of the doubles from `tests/integration/integration.yaml`,
and builds one test program per step. Under `build/integration/<step>/` it writes the
build manifest (`manifest.json`, the input of `tools/record.py build`), the build log,
the run log and `results.json`. The qualification runner builds the software of the
last step with `tests/qualification/test_qualification.c` and writes
`build/qualification/results.json`.

The double of the customer's basic software, `tests/integration/doubles/Platform_double.c`,
runs the task bodies of the execution model (VIEW-0004) in the order stated there. The
qualification tests drive the Hall signal as a pulse train and the switch request as
the communication stack delivers it, and read the results at the bridge output and at
the measurement points PLN-0005 names.

## Check the traceability

From the root of the toolkit:

```
python tools/traceability.py --project examples/power-window check
python tools/traceability.py --project examples/power-window matrix
python tools/traceability.py --project examples/power-window progress --as-of 2026-06-05
python tools/traceability.py --project examples/power-window tara
python tools/traceability.py --project examples/power-window clauses
python tools/traceability.py --project examples/power-window safety
```

`tara` lists the threat scenarios by risk value with the impact and feasibility they
rest on, the value of the plan's matrix and the goal or claim that answers them.
`clauses` shows, per subclause of clauses 6 and 15, the decision of the cybersecurity
plan and the items that provide each work product; the assessment report and the
release for post-development stay empty, as the plan decided.

`progress` reports two milestones as missed: they are marked by baselines, and the
example records none. Without `--as-of` it measures against today, and every milestone
of the plan has passed.
