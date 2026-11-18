# SYS.4 System Integration and Integration Test

## Intent

Assemble the system items step by step into the complete system in the way the system architecture lays out, and test how the items work together. The tests have to produce evidence that the integrated items, and above all the interfaces between them, behave as the architecture specifies. Results are recorded, traceable to the architecture and reported.

Scope note: SYS.4 is in the VDA scope; rating rules, recommendations and a rating-consistency diagram are published for it.

## Outcomes

1. A system integration strategy exists that matches the system architecture, the release plan and the project plan.
2. A system integration test strategy, covering regression testing as well, exists for testing how the system items interact.
3. A system integration test specification has been derived from that test strategy and is capable of showing that the integrated items comply with the architecture, interfaces included.
4. The system items are integrated, following the integration strategy, until the complete system exists.
5. Test cases are chosen from the specification as the release plan and the test strategy require.
6. The interactions between system items are tested with the chosen cases and the results are recorded.
7. Architecture elements and integration test cases agree in content and are linked in both directions, and test cases are linked in both directions to their results.
8. The integration test results are summarised and have been made known to every affected party.

## Base practices

| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SYS.4.BP1 | Develop system integration strategy | There is a strategy for putting the system items together that fits both the release plan and the project plan; the items are identified from the system architecture and the order of integration is defined. Outcome 1. | Integration strategy section of the test plan: list of items, integration steps and their order, preconditions per step, link to release content | SAP.RL.1, SAP.RL.2, SAP.RL.3, SAP.RL.4, DID.RL.10, SYS.4.RL.1, SYS.4.RC.2, SYS.4.RC.3 |
| SYS.4.BP2 | Develop system integration test strategy including regression test strategy | A strategy exists for how the integrated items are tested; it follows the integration strategy and states how re-testing is done when a system item changes. Outcome 2. | Test strategy: test objects per integration step, methods, environments, entry and exit criteria, regression rules | SAP.RL.1, SAP.RL.2, SAP.RL.3, SAP.RL.4, APA.RL.8, SYS.4.RL.2, SYS.4.RL.3 |
| SYS.4.BP3 | Develop specification for system integration test | A test specification exists with test cases for every integration step, written according to the test strategy and able to demonstrate that the integrated items comply with the architecture. Outcome 3. | Test cases with ID, integration step, addressed interface or interaction, preconditions, stimulus, expected result | SYS.4.RL.4, SYS.4.RL.9, SYS.4.RL.11, SYS.4.RC.4 |
| SYS.4.BP4 | Integrate system items | The items have been assembled into an integrated system in the way the integration strategy prescribes. Outcome 4. | Build and assembly records per integration step: item versions, hardware sample state, software and data versions | SYS.4.RL.12 |
| SYS.4.BP5 | Select test cases | For each integration step or release, test cases are picked from the specification so that coverage is adequate for what the release plan and the test strategy demand. Outcome 5. | Selection list per release with the selection criterion and achieved coverage; regression set for changed items | SYS.4.RL.5, SYS.4.RC.1, SYS.4.RL.9, SYS.4.RL.13, SYS.4.RL.14, SYS.4.RC.5 |
| SYS.4.BP6 | Perform system integration test | The selected cases have been executed and both results and logs are recorded. Outcome 6. | Result per executed case with verdict, tested configuration, test environment, date and tester; raw logs; problem reports for failures | SYS.4.RL.6, SYS.4.RL.7, SYS.4.RL.8, SYS.4.RL.15 |
| SYS.4.BP7 | Establish bidirectional traceability | Architecture elements and integration test cases are linked in both directions, and so are test cases and their results. Outcome 7. | Link data from architecture elements and interfaces to test cases and from test cases to results; coverage figures | TAC.RC.1, TAC.RC.2, TAC.RC.3, TAC.RC.4, SYS.4.RC.6 |
| SYS.4.BP8 | Ensure consistency | The content of the test cases has been checked against the architecture elements they claim to cover. Outcome 7. | Review record of the test specification against the architecture; findings and their closure | TAC.RL.1, TAC.RC.4, SYS.4.RC.7, CL2.RC.18 |
| SYS.4.BP9 | Summarize and communicate results | The results are condensed into a summary that reaches all affected parties. Outcome 8. | Test summary report per release with counts, open problems and coverage; distribution record | SAC.RC.1, SAC.RC.2, SAC.RC.3, SAC.RC.4, SAC.RC.5, SAC.RC.6, CL2.RC.10 |

Practice notes:

- The interface descriptions of the architecture are an input for writing integration test cases (BP3).
- "Compliance with the architecture" means the specified tests are able to prove that the interfaces between items do what the architecture says they do (BP3).
- Integration test cases typically probe four things: does each signal reach the items it should, does it arrive in time and in the right temporal relation to other signals, do all users of an interface read it the same way, and do the items behave correctly together over time (BP3).
- The environment may be simulated, for example with hardware-in-the-loop rigs, vehicle network simulation or a digital mock-up (BP3).
- Integration can proceed in steps, bringing together for instance prototype hardware, peripherals such as sensors and actuators, mechanics and the integrated software until the result matches the architecture (BP4).
- Deviations found during testing are handled through SUP.9 (BP6).
- Two-way links are what make coverage checks, consistency checks and impact analysis possible (BP7).
- Consistency builds on those links and is typically evidenced by review records (BP8).
- A summary that carries all relevant information from test execution lets other parties judge what the results mean for them (BP9).

The rule (RL) and recommendation (RC) IDs above are identifiers from the VDA rating guideline; only the IDs are recorded here, not their wording. IDs whose prefix is not the process ID (SAP, DID, APA, TAC, SAC, CL2) belong to parts of that guideline that are not specific to this process.

## Output work products

| WP ID | Official name | Outcomes | What it should contain |
|---|---|---|---|
| 08-50 | Test specification | 3, 5 | Integration test cases per integration step with addressed interface, preconditions, stimulus and expected result, plus the selection made for each release |
| 08-52 | Test plan | 1, 2 | Integration strategy (items, order, preconditions) and integration test strategy (methods, environments, entry and exit criteria, regression rules) |
| 11-06 | System | 4 | The integrated system itself in an identified configuration: which hardware, software, data and mechanical items in which versions |
| 13-04 | Communication record | 8 | Proof that the result summary was sent to the affected parties: what, to whom, when |
| 13-19 | Review record | 7 | Scope reviewed (which test specification and architecture versions), reviewers, consistency findings, decisions and closure |
| 13-22 | Traceability record | 7 | Links between architecture elements and test cases and between test cases and results, navigable in both directions, with coverage status |
| 13-50 | Test result | 6, 8 | Verdict and log per executed case with tested configuration and environment, and the summary across the test run |

## Dependencies

Taken from the rating-consistency diagram for SYS.4. "Rule" means the line is drawn solid, "recommendation" means it is drawn dashed. "One-way" means the rating of the practice in the first column depends on the second column. "Two-way" means the line carries an arrowhead at both ends, which indicates that the two ratings depend on each other. "Plain" means the line has no arrowhead.

| Rating of | Depends on | Kind | ID on the line | Arrow | Relation shown |
|---|---|---|---|---|---|
| SYS.4.BP2 | SYS.4.BP1 | rule | SYS.4.RL.10 | one-way | according to |
| SYS.4.BP3 | SYS.4.BP2 | rule | SYS.4.RL.9, SYS.4.RL.11 | one-way | according to |
| SYS.4.BP4 | SYS.4.BP1 | rule | SYS.4.RL.12 | one-way | according to |
| SYS.4.BP5 | SYS.4.BP2 | rule | SYS.4.RL.9, SYS.4.RL.14 | one-way | according to |
| SYS.4.BP5 | SYS.4.BP3 | rule | SYS.4.RL.13 | one-way | select from |
| SYS.4.BP6 | SYS.4.BP5 | rule | SYS.4.RL.15 | one-way | using |
| SYS.4.BP7 | SYS.4.BP3 | rule (solid line) | none printed | one-way | establish between |
| SYS.4.BP7 | SYS.4.BP6 | rule (solid line) | none printed | one-way | establish between |
| SYS.4.BP9 | SYS.4.BP6 | rule (solid line) | none printed | one-way | summarize test results |
| SYS.4.BP1 | MAN.3 (PA 1.1) and SPL.2 (PA 1.1), drawn as one group | recommendation | SYS.4.RC.2 | plain | consistent with |
| SYS.4.BP5 | MAN.3 (PA 1.1) and SPL.2 (PA 1.1), drawn as one group | recommendation | SYS.4.RC.5 | plain | according to |
| SYS.4.BP1 | SYS.3 (PA 1.1) | recommendation | SYS.4.RC.3 | two-way | consistent with |
| SYS.4.BP3 | SYS.3 (PA 1.1) | recommendation | SYS.4.RC.4 | two-way | provide evidence for compliance with |
| SYS.4.BP7 | SYS.3 (PA 1.1) | recommendation | SYS.4.RC.6 | two-way | establish between |
| SYS.4.BP8 | SYS.3 (PA 1.1) | recommendation | SYS.4.RC.7 | two-way | ensure between |
| SYS.4.BP7 | SYS.4.BP3 | recommendation (dashed line) | none; labelled "no RC" | two-way | (no other text) |
| SYS.4.BP8 | SYS.4.BP3 | recommendation (dashed line) | none; labelled "no RC" | two-way | (no other text) |

Reading it:

- The practices form a chain: integration strategy, test strategy, test specification, selection, execution. The rating of each later practice depends by rule on an earlier one.
- MAN.3 stands for the project plan and SPL.2 for the release plan; the strategy (BP1) and the selection (BP5) should be rated in step with them.
- The quality of the system architecture (SYS.3) should show in the ratings of BP1, BP3, BP7 and BP8.
- BP7 and BP8 each have two dashed lines: one to SYS.3 that carries a recommendation ID and one to BP3 that is marked "no RC". A plausible reading is that traceability and consistency sit between the architecture and the test specification and that only the architecture end has a numbered recommendation; the diagram does not say more than that.
- BP7 is connected to BP3 twice: once by the solid unnumbered line (test cases to results) and once by the dashed "no RC" line.
- Three solid lines carry no rule ID (BP7 to BP3, BP7 to BP6, BP9 to BP6). They are recorded as rules because they are drawn solid, but no numbered rule can be cited for them.
- SYS.4.RL.10 appears only on the diagram; it is not in the per-practice ID lists for BP1 or BP2.

## Automation notes

Assumed setting: test plan, test specification and architecture are structured text with IDs and links in a git repository; integration and testing happen on prototype hardware and test benches the toolkit cannot reach; results come back as exported files.

Deterministic checks a script can run:

- The test plan contains the required parts: integration items, integration order, preconditions per step, test methods and environments, entry and exit criteria, regression rules.
- Every item named in the integration order exists in the architecture, and every architecture element at integration level appears in the order.
- Every interface defined in the architecture is addressed by at least one integration test case; every test case links to at least one existing architecture element or interface and names its integration step.
- Test case schema: ID, preconditions, stimulus, expected result, required environment are filled.
- The selection for a release is a subset of the specification, states its criterion, and its coverage figure can be recomputed from the links.
- Regression set: from the diff between two baselines, list the changed items and interfaces and, through the trace links, the test cases that must be repeated; flag any that are missing from the selection.
- Result import: every selected case has exactly one current result for the release candidate; every result names the case, verdict, software tag, hardware sample revision, data set, bench and date; results without a known case and selected cases without a result are flagged.
- Every failed or blocked result links to a problem report.
- Generate the summary: counts per verdict, coverage of interfaces, open problem reports, deviations from the planned selection.
- The integrated configuration is recorded as a manifest (item versions) and matches the tag that the results refer to.

Checks that need semantic judgement (LLM-assisted, human-confirmed):

- Whether a test case is really able to demonstrate the interface behaviour it claims to cover: signal flow, timing, interpretation of values on both sides, dynamic interaction.
- Whether the strategy is coherent with the project plan and release plan content rather than merely referencing them.
- Drafting test cases from interface definitions and behaviour descriptions; proposing missing negative and timing cases.
- Reading logs and comments to judge whether a deviation is explained, and drafting the narrative part of the summary.

What stays with humans (System Tester, System Architect, Project Manager) and physical equipment:

- The integration itself: assembling prototype hardware, peripherals and mechanics, flashing software, wiring harnesses and benches.
- Executing tests on hardware-in-the-loop rigs, network simulation set-ups or other benches, and operating measurement equipment. The toolkit can only ingest exported logs and results; it cannot attest that a test was actually run or run correctly.
- Verdicts that rest on analogue measurements, timing captures or observation.
- The decision that integration is good enough to proceed, and sign-off of the summary.
