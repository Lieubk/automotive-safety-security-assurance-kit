# SWE.6 Software Qualification Test

## Intent

Show by testing the integrated software that it meets the software requirements. The tests are planned (regression included) in line with project and release planning, test cases are specified from the requirements' verification criteria, the cases to run are chosen for each release, execution is recorded, requirement-to-test-to-result links are kept, and the outcome is reported.

Scope marker: VDA scope, with rating-consistency guidance.

## Outcomes

1. A qualification test strategy for the integrated software exists, includes regression testing, and fits project and release planning.
2. A qualification test specification derived from that strategy exists and is fit to show that the integrated software meets the software requirements.
3. Test cases have been chosen from the specification as the strategy and the release plan require.
4. The integrated software has been tested with the chosen test cases, and the results are on record.
5. Software requirements and qualification test cases, and test cases and their results, are consistent and linked in both directions.
6. Qualification test results have been summarised and passed to all affected parties.

## Base practices

| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SWE.6.BP1 | Develop software qualification test strategy including regression test strategy | A strategy for qualification testing exists and fits project and release planning. It includes what is re-tested on the integrated software when an item changes. Outcome 1. | Qualification test strategy or plan: test objects and scope per release, test methods and test design techniques, environments (hardware-in-the-loop, ECU on a bench, software-in-the-loop where justified), entry / exit and pass / fail criteria, regression rules, schedule tied to the release plan, roles and tester independence, defect handling. | SAP.RL.1, SAP.RL.2, SAP.RL.3, SAP.RL.4, AGE.RC.9, PLS.RC.7, APA.RL.8, SWE.6.RL.1, SWE.6.RL.2, SWE.6.RC.2 |
| SWE.6.BP2 | Develop specification for software qualification test | A test specification exists whose test cases are derived from the verification criteria of the requirements, built as the test strategy requires, and fit to show that the integrated software complies with the software requirements. Outcome 2. | Test specification with test cases, each having ID, linked requirement(s), reference to the verification criteria it implements, preconditions, steps, expected results with tolerances, environment; cases for non-functional requirements as well (timing, memory, robustness, fault reaction, diagnostics). | SWE.6.RL.3, SWE.6.RL.8, SWE.6.RL.9, SWE.6.RC.3 |
| SWE.6.BP3 | Select test cases | For each test run, test cases are picked from the specification so that coverage is sufficient for what the release plan and the test strategy demand. Outcome 3. | Test selection list per release with coverage rationale: requirements in the release, changed functions, regression set; statement of what is deliberately not tested and why. | SWE.6.RL.4, SWE.6.RC.1, SWE.6.RL.8, SWE.6.RL.10, SWE.6.RL.11, SWE.6.RC.4 |
| SWE.6.BP4 | Test integrated software | The selected test cases are executed on the integrated software; results and logs are recorded. Non-conformances go to problem resolution (SUP.9). Outcome 4. | Test log and result per test case with verdict, identification of the tested software (version, checksum), hardware sample revision, environment and tool versions, tester, date; problem records for failures. | SWE.6.RL.5, SWE.6.RL.6, SWE.6.RL.7, SWE.6.RL.12 |
| SWE.6.BP5 | Establish bidirectional traceability | Links exist, navigable both ways, between software requirements and qualification test cases and between those test cases and their results. Outcome 5. | Test cases referencing requirement IDs; results keyed by test case ID and software version; generated coverage report (requirements without test case, test cases without requirement, test cases without result) with a per-requirement verdict roll-up. | TAC.RC.1, TAC.RC.2, TAC.RC.3, TAC.RC.4, SWE.6.RC.5 |
| SWE.6.BP6 | Ensure consistency | The qualification test cases agree in content with the software requirements they verify. Traceability supports this; review records demonstrate it. Outcome 5. | Review record of the test specification against the requirements, with reviewed revisions, findings and closure; re-review entries after requirement changes. | TAC.RL.1, TAC.RC.4, SWE.6.RC.6, CL2.RC.18 |
| SWE.6.BP7 | Summarize and communicate results | Qualification test results are condensed into a summary that lets recipients judge the consequences, and it is passed to all affected parties. Outcome 6. | Qualification test report per release: requirement coverage, passed / failed / not tested, open defects with severity, deviations from the strategy, recommendation; distribution record to Project Manager, Software Lead, Quality Assurance Engineer and, where agreed, the Customer. | SAC.RC.1, SAC.RC.2, SAC.RC.3, SAC.RC.4, SAC.RC.5, SAC.RC.6, CL2.RC.10 |

## Output work products

| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 08-50 | Test specification | 2, 3 | Qualification test cases with the requirement each verifies, steps and expected results, and the selection made for each release. |
| 08-52 | Test plan | 1 | The qualification test strategy: scope, methods, environments, criteria, regression rules, schedule. |
| 13-04 | Communication record | 6 | Proof that the test report was distributed: version, recipients, date. |
| 13-19 | Review record | 5 | Review of the test specification against the software requirements: revisions, reviewers, findings, closure. |
| 13-22 | Traceability record | 5 | Links requirement to test case and test case to result, readable in both directions with gaps visible. |
| 13-50 | Test result | 4, 6 | Verdict and log per executed test case with identification of software, hardware and environment; summary figures. |

## Dependencies

Reading convention: "A depends on B" means the rating of A is tied to the rating of B. "Rule" comes from a solid line in the rating-consistency diagram, "recommendation" from a dashed line. External targets are the PA 1.1 (process performance) rating of the named process.

| From | Depends on | Kind | ID on the diagram | Relationship shown |
|---|---|---|---|---|
| SWE.6.BP2 | SWE.6.BP1 | rule | SWE.6.RL.8, SWE.6.RL.9 | the test specification follows the strategy |
| SWE.6.BP3 | SWE.6.BP1 | rule | SWE.6.RL.8, SWE.6.RL.11 | selection follows the strategy |
| SWE.6.BP3 | SWE.6.BP2 | rule | SWE.6.RL.10 | test cases are selected from the specification |
| SWE.6.BP4 | SWE.6.BP3 | rule | SWE.6.RL.12 | testing uses the selected test cases |
| SWE.6.BP7 | SWE.6.BP4 | rule (solid line) | no ID shown | the summary covers the test results |
| SWE.6.BP1 | MAN.3 (PA 1.1) and SPL.2 (PA 1.1) | recommendation | SWE.6.RC.2 | the strategy is consistent with project plan and release plan |
| SWE.6.BP2 | SWE.1 (PA 1.1) | recommendation | SWE.6.RC.3 (see note) | the test specification is based on the software requirements |
| SWE.6.BP3 | MAN.3 (PA 1.1) and SPL.2 (PA 1.1) | recommendation | SWE.6.RC.4 | selection follows the plans; the line attaches to the frame around MAN.3 and SPL.2, while the practice text itself names only the release plan |
| SWE.6.BP5 | SWE.1 (PA 1.1) | recommendation | SWE.6.RC.5 | traceability to the software requirements |
| SWE.6.BP6 | SWE.1 (PA 1.1) | recommendation | SWE.6.RC.6 | consistency with the software requirements |
| SWE.6.BP6 | SWE.6.BP2 | recommendation (dashed line) | see note | the test specification is the other end of the consistency check |
| SWE.6.BP5 | SWE.6.BP2 | recommendation (dashed line) | no ID shown | test cases are one end of the traceability |
| SWE.6.BP5 | SWE.6.BP4 | recommendation (dashed line) | no ID shown | test results are one end of the traceability |

Note on RC.3: the per-practice ID lists assign `SWE.6.RC.3` to BP2 and `SWE.6.RC.6` to BP6. In the diagram the line from BP2 to SWE.1 carries only the words "based on", and the label "RC.3: ensure between" sits next to the dashed branch that joins BP6 to BP2. The table follows the per-practice ID lists; the placement of the RC.3 label in the diagram is ambiguous.

Additional observations from the diagram:
- The chain is strategy (BP1), specification (BP2), selection (BP3), execution (BP4), summary (BP7).
- The solid line from BP7 to BP4 has no rule number, and the per-practice ID list of BP7 contains no SWE.6 rule. It is recorded as "rule" because of the line style only.
- BP5 and BP6 are tied to the rest by recommendations and dashed lines only.
- The RC.5 and RC.6 lines are drawn with arrowheads at both ends; the RC.2 and RC.4 lines have none.
- Cross-reference in the practice notes: SUP.9 for handling non-conformances found in BP4.

## Automation notes

Assumed setting: software requirements and qualification test cases are structured text items with IDs and links in the repository; requirements carry verification criteria, verification method and target release; test bench or simulation runs export machine-readable results that name the tested build; baselines are tags.

Deterministic checks a script can do:
- Strategy completeness: mandatory sections present (scope per release, methods, environments, entry / exit and pass / fail criteria, regression rules, schedule reference to the release plan, roles).
- Requirement coverage both ways: every agreed requirement whose verification method is "test" is linked from at least one test case; requirements with another method point to the alternative evidence; every test case links to at least one existing, non-obsolete requirement.
- Test case schema: ID, linked requirement, reference to the verification criteria, preconditions, steps, expected result, environment, status "reviewed" at baseline.
- Criteria linkage: a test case may not link to a requirement whose verification criteria are empty; flag test cases unchanged since their requirement or its criteria changed (suspect link).
- Selection per release: every requirement assigned to the release has at least one selected test case; the selection contains the regression set defined by the strategy and all test cases linked to requirements changed since the previous release.
- Result completeness: every selected test case has a result for exactly the tagged build (version and checksum match the build list), with verdict, hardware revision, environment and tool versions; verdicts other than "passed" link to a problem record.
- Roll-up: compute a verdict per requirement and per release (passed, failed, not tested) and the coverage percentage; compare against the exit criteria in the strategy.
- Records: review record of the test specification for the baselined revision with no open finding; generated test report and its distribution record.

Needs semantic judgement (LLM-assisted, human-confirmed):
- Does the test case really verify the requirement and its verification criteria: right stimulus, right observation point, expected values and tolerances taken from the requirement?
- Is the test black-box against the requirement, or does it only confirm the implementation?
- Are several test cases together sufficient for a requirement with multiple conditions, ranges or modes; are negative and boundary cases present?
- Are non-functional requirements (timing, robustness, resource limits) covered by suitable test methods?
- Is the selection rationale convincing for the release content, and does the report state fairly what was not tested?
- Plausibility of results: verdict consistent with the logged measurements.

Stays with a human or with the test bench:
- Execution on the target ECU or hardware-in-the-loop bench and the validity of that environment (calibration, models, tool versions).
- Analysis of failures and the decision whether they are software, test or environment problems.
- Tester independence, release recommendation and acceptance of open defects or untested requirements.
- Agreement of the strategy with project and release planning and with the Customer where required.
