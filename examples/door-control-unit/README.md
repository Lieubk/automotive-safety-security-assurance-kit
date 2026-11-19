# Front door control unit DCU-F - worked example of a system supplier

A small but complete docs-as-code project: the **system supplier** of a front door control
unit - electronics, software and window lift motor as one unit - that takes the OEM's
requirements to system requirements and a system architecture, integrates hardware, the
released software of its own software department and a supplied motor, tests the system on
a bench, manages its risks and its supplier, watches for vulnerabilities, releases the
unit as B-sample B1 to the OEM and rehearses an assessment. Every engineering artifact is
one Markdown file with YAML front matter, following
[schema/item-format.md](../../schema/item-format.md) and
[schema/items.yaml](../../schema/items.yaml). It is the second worked example next to
[power-window](../power-window/README.md), which shows a software supplier.

**All content is invented demonstration data.** The product, the OEM's document, the motor
supplier, every name, number, threshold, date and bench report are made up for this
example. People appear by role-like names (L. Leader, E. Engineer). Nothing here is taken
from a real project, and no conformance with any regulation or standard is claimed.

## What the example shows

| Process | In the example |
|---|---|
| SYS.1 (not in scope) | the OEM's document "Front door control unit - requirements" 1.0 is registered as 5 imported stakeholder requirements and accepted in an input acceptance review; one is accepted with a deviation agreed with the OEM (`CMR-0001`) |
| SYS.2 System Requirements Analysis | 10 system requirements with verification criteria and analysis, traced to the stakeholder requirements |
| SYS.3 System Architectural Design | 4 system elements (hardware, software, motor, the OEM's switch panel), 4 interfaces, a structure view, a sequence view of one-touch closing with reversal, 1 design decision with two alternatives, every requirement allocated |
| SYS.4 System Integration and Integration Test | an integration strategy with two steps, 8 integration test cases, 3 system build records, 3 runs from the bench's reports |
| SYS.5 System Qualification Test | a qualification strategy, 10 test cases, 2 runs: the first fails on the one-touch closing time, the second passes after a calibration change of the software element |
| ACQ.4 Supplier Monitoring | an agreement with the motor supplier, one delivery of samples, two technical reviews that open and close one item |
| MAN.3 Project Management | a project plan with three milestones, 8 work packages that deliver every item, one status report |
| MAN.5 Risk Management | a risk plan with a 3 by 3 scale, 3 risks: one accepted, two treated |
| SUP.8 Configuration Management | a configuration management plan, one baseline (release candidate B1, tag `dcu-f-b1-rc`) and its communication |
| SPL.2 Product Release | a release plan, release B1 from the baseline with its note, delivery and receipt |

The **software** of the unit is the released element "power window software" of the
software department (see [power-window](../power-window/README.md)). It is integrated as
received and named by its version in the manifest of each system build; the SWE
processes are the department's, not this project's.

Functional safety: the OEM's safety concept rates the window lift of this vehicle line QM,
so no part of ISO 26262 is in scope and every item carries ASIL QM. Cybersecurity: of
ISO/SAE 21434 the project is responsible for clauses 6 and 8 only.

| Clause | In the example |
|---|---|
| 6 Project dependent cybersecurity management | a cybersecurity plan (`PLN-0005`) with a decision per subclause, three not-applicable entries with their reasons, the method of the OEM's TARA as the project applies it to a vulnerability; a cybersecurity case (`CSE-0001`) |
| 8 Continual cybersecurity activities | a monitoring plan (`PLN-0006`); one event (`CEV-0001`), the bulletin about a weak seed-key algorithm in the bootloader, triaged relevant; one weakness (`WKN-0001`) analysed as a vulnerability of low feasibility; treatment retain until B2 with a claim (`CLM-0001`); the OEM told as information sharing (`CMR-0003`) |

The TARA, the cybersecurity goals and the concept are the OEM's; the OEM's TARA was not
delivered, which is why the weakness is rated with the highest impact as an assumption.

## What the evidence is, and what it is not

| Record | What really happened | What it does not show |
|---|---|---|
| `REV-0001` to `REV-0017` | written by `record.py review` with a result for every check of the checklist, for the reviewer named; the semantic checks were applied in the session and no independent pass took place, and the records say so | an independent review by people: the answers of the accountable checks are demonstration data |
| `BLD-0001` to `BLD-0003`, `RUN-0001` to `RUN-0005` | written by `record.py build` and `record.py test-run` from the manifests and JUnit reports under `inputs/bench/` | a bench: the reports are invented. The failing closing time (4.4 s against 4.0 s) and its correction are part of the story, not of a measurement |
| `PRB-0001` | the failed case, its cause in a calibration value, closure with the passing run | a software department or a calibration |
| `SRV-0001`, `SRV-0002`, `CMR-0002` | written by `record.py supplier-review` and `communication` from minutes and a delivery that are stated, not observed | a supplier |
| `BL-0001`, `REL-0001`, `CMR-0004`, `CMR-0005` | written by `record.py baseline`, `release` and `communication`; the tag is set on the commit that holds the baseline record | a delivery of samples |
| `SAS-0001` | written by `record.py self-assessment` from the ratings of two assessors and their notes; one flag (SYS.2.BP4 rated P against an observation of evidence present) carries its reason | an assessment; no capability level follows |
| `PSR-0001`, `CSE-0001` | written by `record.py status-report` and `cybersecurity-case`; the words of the assessment and the argument are demonstration data | a project lead or a cybersecurity lead |

The example was built in a repository of its own; the tag `dcu-f-b1-rc` and the commits
the records name are in that repository, not in the toolkit's. `audit BL-0001` compares
the content hashes and works here too.

The date inside a review, communication, baseline or release record is the day the tool
ran, not the day the story gives for the event; where the story gives a date (the bench
runs, the supplier reviews, the delivery), the record carries it.

## What the check reports, and why

`python tools/traceability.py --project <this folder> check --all` reports no error and no
warning. Observations that remain by design, and are not defects:

| Observation | Where | Why |
|---|---|---|
| `progress`: two milestones "not assessed: no baseline purpose named" | "System requirements agreed", "System architecture frozen" | no baseline marks them; `Criteria` of the project plan says they are decided by the review of their items |
| `practices`: ACQ.4.BP4, ACQ.4.BP5, MAN.5.BP7 "no evidence yet" | supplier, risks | no progress review with the motor supplier, no missed objective and no stalled treatment happened in the story |
| `practices`: MAN.5.BP3 to BP6 "evidence not settled" | risks | risks are not approved, they move through their states; two are in treatment |
| `clauses`: 21434:8.3 to 8.6 "evidence not settled" | `WKN-0001` | the weakness stays in resolution until the corrected bootloader is in B2 |
| `suppliers`: progress review agreed monthly, held 0 times | `SAG-0001` | the story holds technical reviews only |
| `release`: 1 open problem | `REL-0001` | the weakness above; it is named in the release note as a known issue |

## Item files

| Type | Prefix | Folder | Count |
|---|---|---|---|
| Stakeholder requirement (imported) | STK | `spec/stakeholder` | 5 |
| System requirement | SYR | `spec/system/requirements` | 10 |
| System element | SYE | `spec/system/architecture` | 4 |
| System interface | SYI | `spec/system/architecture` | 4 |
| Architecture view | VIEW | `spec/views` | 2 |
| Design decision | ADR | `spec/decisions` | 1 |
| System integration test case | SYIT | `verification/system-integration` | 8 |
| System qualification test case | SYQT | `verification/system-qualification` | 10 |
| Plan | PLN | `plans` | 8 |
| Work package | WP | `plans/work-packages` | 8 |
| Supplier agreement | SAG | `plans/suppliers` | 1 |
| Cybersecurity claim | CLM | `spec/cybersecurity/goals` | 1 |
| Risk | RSK | `records/risks` | 3 |
| Problem report | PRB | `records/problems` | 1 |
| Cybersecurity event, weakness, case | CEV, WKN, CSE | `records/cybersecurity` | 1, 1, 1 |
| Review record | REV | `records/reviews` | 17 |
| Communication record | CMR | `records/communication` | 5 |
| Supplier review | SRV | `records/suppliers` | 2 |
| Project status report | PSR | `records/status` | 1 |
| Self-assessment | SAS | `records/assessments` | 1 |
| Baseline, release | BL, REL | `records/baselines`, `records/releases` | 1, 1 |
| Build record | BLD | `verification/builds` | 3 |
| Test run | RUN | `verification/runs` | 5 |

Besides the items: `inputs/` holds the OEM's document and, under `inputs/bench/`, the
manifests, logs and JUnit reports of the bench; `project.yaml` the scope.

A good place to start reading is `spec/views/VIEW-0001.md` (structure), then
`spec/views/VIEW-0002.md` (what happens when the glass meets an obstacle), then
`spec/decisions/ADR-0001.md`, then `verification/runs/RUN-0003.md` (the failing
qualification run) with `records/problems/PRB-0001.md`, and `records/releases/REL-0001.md`.

## Check the traceability

From the root of the toolkit, with this folder as the project:

```
python tools/traceability.py --project <this folder> check --all
python tools/traceability.py --project <this folder> matrix
python tools/traceability.py --project <this folder> progress
python tools/traceability.py --project <this folder> suppliers
python tools/traceability.py --project <this folder> risks
python tools/traceability.py --project <this folder> clauses
python tools/traceability.py --project <this folder> audit BL-0001
```

`audit BL-0001` reports no difference at the tagged commit; later it shows what moved on
since the baseline.

## Documents

`python tools/document.py --project <this folder> build <kind>` generates the documents.
Of the 40 kinds, 24 show items of this project (for example the system requirements
specification, the system architecture description, the integration and qualification
test specifications and reports, the project plan, the risk, supplier and release
documents, the cybersecurity plan and case, the traceability and review reports); the 16
that show none belong to processes this project is not responsible for (software
processes, safety, quality assurance, change requests) and say so with a warning. The
`build/` folder is not under version control.
