# SWE.5 Software Integration and Integration Test

## Intent

Assemble software units into progressively larger software items until the complete integrated software exists, in a planned order that fits the architecture and the project and release planning. Test the integrated items to show that they behave as the architecture specifies, above all at the interfaces between units and between items. Keep test cases, architecture and results traceable and report what was found.

Scope marker: VDA scope, with rating-consistency guidance.

## Outcomes

1. An integration strategy for the software items exists and is aligned with project planning, release planning and the architecture.
2. A strategy for integration testing, regression testing included, exists and targets the interactions between units and between items.
3. An integration test specification derived from that test strategy exists and is fit to show that integrated items comply with the architecture, including unit-to-unit and item-to-item interfaces.
4. Units and items have been integrated step by step, as the integration strategy prescribes, until the complete integrated software exists.
5. Test cases have been chosen from the specification as the test strategy and the release plan require.
6. Integrated items have been tested with the chosen test cases, and the results are on record.
7. Architecture elements and integration test cases, and test cases and their results, are consistent and linked in both directions.
8. Integration test results have been summarised and passed to all affected parties.

## Base practices

| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SWE.5.BP1 | Develop software integration strategy | A strategy for integrating the software items exists and fits project and release planning. The items are identified from the architecture and an integration order is defined. Outcome 1. | Integration strategy or plan: list of software items derived from the architecture, integration steps and their order (for example by layer: microcontroller abstraction, basic software, runtime environment, application components), mapping of steps to releases, entry criteria for items (unit verification done), handling of supplier deliveries and generated configuration, build environment, responsibilities. | SAP.RL.1, SAP.RL.2, SAP.RL.3, SAP.RL.4, AGE.RC.8, DID.RL.10, SWE.5.RL.1, SWE.5.RC.2, SWE.5.RC.3 |
| SWE.5.BP2 | Develop software integration test strategy including regression test strategy | A test strategy for the integrated items exists and follows the integration strategy. It includes what is re-tested when an item changes. Outcome 2. | Integration test strategy or plan: test steps aligned with the integration order, methods (interface, data flow, timing, resource tests), environments (software-in-the-loop, processor-in-the-loop, target with debugger, hardware-in-the-loop), coverage goals (interfaces, calls), entry / exit criteria, regression rules, tooling. | SAP.RL.1, SAP.RL.2, SAP.RL.3, SAP.RL.4, APA.RL.8, SWE.5.RL.2, SWE.5.RL.3; from the diagram: SWE.5.RL.10 |
| SWE.5.BP3 | Develop specification for software integration test | For each integrated item a test specification with test cases exists, built as the test strategy requires and fit to show compliance with the architecture; that is, able to prove that interfaces between units and between items do what the architecture specifies. Test cases typically look at: correct data flow between items; timeliness and timing dependencies of that data flow; identical interpretation of the data by every item using an interface; dynamic interaction between items; interfaces staying within their resource consumption objectives. Outcome 3. | Integration test specification: test cases per integrated item, each with ID, linked architecture element (interface, sequence, resource objective), preconditions, stimulation, expected result, environment; cases checking scaling, units and invalid values across an interface, call sequences and timing, start-up and shutdown interplay, memory and stack budgets. | TPS.RC.11, SWE.5.RL.4, SWE.5.RL.9, SWE.5.RL.11, SWE.5.RC.4 |
| SWE.5.BP4 | Integrate software units and software items | Units are combined into items and items into the integrated software in the way the integration strategy lays down. Outcome 4. | Build per integration step (binary / hex file, map file) from a reproducible build; build list or manifest naming every item with its version; build log; integration log with problems met; baseline tag of the integrated software. | SWE.5.RL.12 |
| SWE.5.BP5 | Select test cases | For each test run, test cases are picked from the integration test specification so that coverage is sufficient for what the release plan and the test strategy demand. Outcome 5. | Test selection list per integration step or release with the reason for each group (new, changed, regression) and a coverage statement against the strategy. | SWE.5.RL.5, SWE.5.RC.1, SWE.5.RL.9, SWE.5.RL.13, SWE.5.RL.14, SWE.5.RC.5 |
| SWE.5.BP6 | Perform software integration test | The selected test cases are executed; results and logs are recorded. Non-conformances go to problem resolution (SUP.9). Debug access to the hardware, or simulation (for example software-in-the-loop), may support the testing. Outcome 6. | Test log and result per test case with verdict, build identification, environment and tool versions, tester, date; measurement traces (timing, stack usage); problem records for failures. | TPS.RC.12, SWE.5.RL.6, SWE.5.RL.7, SWE.5.RL.8, SWE.5.RL.15 |
| SWE.5.BP7 | Establish bidirectional traceability | Links exist, navigable both ways, between architecture elements and integration test cases and between those test cases and their results. Outcome 7. | Test cases referencing architecture element IDs; results keyed by test case ID and build; generated coverage report (interfaces without test case, test cases without architecture element, test cases without result). | TAC.RC.1, TAC.RC.2, TAC.RC.3, TAC.RC.4, SWE.5.RC.6 |
| SWE.5.BP8 | Ensure consistency | The integration test cases agree in content with the architecture elements they address. Traceability supports this; review records demonstrate it. Outcome 7. | Review record of the integration test specification against the architecture, with reviewed revisions, findings and closure; re-review entries after architecture changes. | TAC.RL.1, TAC.RC.4, SWE.5.RC.7, CL2.RC.18 |
| SWE.5.BP9 | Summarize and communicate results | Integration test results are condensed into a summary that lets recipients judge the consequences, and it is passed to all affected parties. Outcome 8. | Integration test summary per release: scope and build, executed / passed / failed / blocked, interface coverage, open problems, assessment; distribution record to Software Lead, Software Testers, Project Manager and Quality Assurance Engineer. | SAC.RC.1, SAC.RC.2, SAC.RC.3, SAC.RC.4, SAC.RC.5, SAC.RC.6, SAC.RL.2, CL2.RC.10 |

## Output work products

| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 01-03 | Software item | 4 | An integrated part of the software (several units or smaller items combined), identifiable by version. |
| 01-50 | Integrated software | 4 | The complete software built from all items for a release: binaries plus the identification of everything that went in. |
| 08-50 | Test specification | 3, 5 | Integration test cases per integrated item with the architecture element each addresses, and the selection made for each run. |
| 08-52 | Test plan | 1, 2 | The integration strategy (items, order, release mapping) and the integration test strategy (methods, environments, coverage, regression). |
| 13-04 | Communication record | 8 | Proof that the result summary was distributed: version, recipients, date. |
| 13-19 | Review record | 7 | Review of the integration test specification against the architecture: revisions, reviewers, findings, closure. |
| 13-22 | Traceability record | 7 | Links architecture element to test case and test case to result, readable in both directions. |
| 13-50 | Test result | 6, 8 | Verdict and log per executed test case with build and environment identification; summary figures. |
| 17-02 | Build list | 4, 7 | Per build: every unit / item / configuration file with its version, and the tool chain used, so the build can be reproduced and results attributed to it. |

## Dependencies

Reading convention: "A depends on B" means the rating of A is tied to the rating of B. "Rule" comes from a solid line in the rating-consistency diagram, "recommendation" from a dashed line. External targets are the PA 1.1 (process performance) rating of the named process.

| From | Depends on | Kind | ID on the diagram | Relationship shown |
|---|---|---|---|---|
| SWE.5.BP4 | SWE.5.BP1 | rule | SWE.5.RL.12 | integration is done according to the integration strategy |
| SWE.5.BP2 | SWE.5.BP1 | rule | SWE.5.RL.10 | the test strategy follows the integration strategy |
| SWE.5.BP3 | SWE.5.BP2 | rule | SWE.5.RL.9, SWE.5.RL.11 | the test specification follows the test strategy |
| SWE.5.BP5 | SWE.5.BP2 | rule | SWE.5.RL.9, SWE.5.RL.14 | selection follows the test strategy |
| SWE.5.BP5 | SWE.5.BP3 | rule | SWE.5.RL.13, SWE.5.RL.14 | test cases are selected from the specification |
| SWE.5.BP6 | SWE.5.BP5 | rule | SWE.5.RL.15 | testing uses the selected test cases |
| SWE.5.BP9 | SWE.5.BP6 | rule (solid line) | no ID shown | the summary covers the test results |
| SWE.5.BP7 | SWE.5.BP6 | rule (solid line) | no ID shown | test results are one end of the traceability |
| SWE.5.BP7 | SWE.5.BP3 | rule (solid line) | no ID shown | test cases are one end of the traceability; a dashed branch of the RC.6 line reaches BP3 as well |
| SWE.5.BP1 | MAN.3 (PA 1.1) and SPL.2 (PA 1.1) | recommendation | SWE.5.RC.2 | the integration strategy is consistent with project plan and release plan |
| SWE.5.BP1 | SWE.2 (PA 1.1) | recommendation | SWE.5.RC.3 | the integration strategy is consistent with the architecture |
| SWE.5.BP3 | SWE.2 (PA 1.1) | recommendation | SWE.5.RC.4 | the test specification provides evidence of compliance with the architecture |
| SWE.5.BP5 | MAN.3 (PA 1.1) and SPL.2 (PA 1.1) | recommendation | SWE.5.RC.5 | selection follows the plans; the line attaches to the frame around MAN.3 and SPL.2, while the practice text itself names only the release plan |
| SWE.5.BP7 | SWE.2 (PA 1.1) | recommendation | SWE.5.RC.6 | traceability to architecture elements |
| SWE.5.BP8 | SWE.2 (PA 1.1) | recommendation | SWE.5.RC.7 | consistency with the architecture |
| SWE.5.BP8 | SWE.5.BP3 | recommendation | SWE.5.RC.7 | the test specification is the other end of the consistency check |

Additional observations from the diagram:
- There are two chains: integration (BP1 then BP4) and testing (BP1, BP2, BP3, BP5, BP6, then BP9 and BP7).
- Three solid lines (BP9 to BP6, BP7 to BP6, BP7 to BP3) carry no rule number; the per-practice ID lists contain no SWE.5 rule for BP7 or BP9 either. They are recorded as "rule" because of the line style, but no guideline ID can be attached.
- `SWE.5.RL.10` appears only in the diagram, not in the per-practice ID list of BP2.
- The RC.5 line is drawn with its arrowhead at BP5, opposite to the reading convention; it is recorded here in the only direction that makes sense (BP5 depends on the plans).
- Cross-reference in the practice notes: SUP.9 for handling non-conformances found in BP6.

## Automation notes

Assumed setting: one repository (or a manifest of repositories) holds code, AUTOSAR configuration, architecture items with IDs, integration test cases with IDs and links, and build scripts; continuous integration builds each integration step and runs the automatable tests; test bench runs export machine-readable results; baselines are tags.

Deterministic checks a script can do:
- Strategy completeness: mandatory sections present in the integration strategy (items, order, release mapping, entry criteria) and in the test strategy (methods, environments, coverage goals, regression rules, exit criteria); every architecture component appears in exactly one integration step.
- Build list integrity: the manifest for a tag lists every item with version or commit; the listed versions equal what the tag actually contains (submodules, generated configuration, tool chain versions); a clean rebuild from the tag reproduces the binary checksum.
- Entry criteria: each unit entering an integration step has passing unit verification results for the integrated revision.
- Specification coverage: every interface, connection and dynamic scenario of the architecture marked integration-relevant is linked from at least one test case; every test case links to an existing architecture element; every test case has preconditions, steps, expected result and environment.
- Selection: a selection list exists for each integration step and release; it contains at least all test cases linked to components changed since the previous baseline and to their direct interface partners (computable from diff plus link graph), plus the regression set the strategy defines.
- Results: every selected test case has a result for the tagged build with verdict, build checksum, environment and tool version; any verdict other than "passed" links to a problem record; logs are archived.
- Resource objectives: compare sizes from the linker map file and reported stack / CPU load figures with the budgets set in the architecture.
- Records: review record of the test specification for the baselined revision with no open finding; suspect flag when a linked architecture element changed after the link was confirmed; generated summary and its distribution record.

Needs semantic judgement (LLM-assisted, human-confirmed):
- Does a test case really exercise the interface (data interpretation, scaling, validity, timing, error signalling, call sequence), or is it a requirements test under another name?
- Does the expected result follow from the architecture description?
- Is the integration order sensible for the architecture (stubs and drivers needed, risk first), and does the test strategy match it?
- Is the selection rationale convincing for the content of the release?
- Does the summary reflect the results fairly, including what was not tested?

Stays with a human or with the test bench:
- Execution on target hardware or hardware-in-the-loop bench, including timing and resource measurements; a script can only verify that results were reported for the right build.
- Use of debug interfaces and judgement about intermittent or timing-dependent failures.
- Deciding integration order against delivery dates and supplier deliveries.
- Accepting open failures for a release and the accountability for that decision.
