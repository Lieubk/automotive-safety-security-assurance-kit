# SWE.4 Software Unit Verification

## Intent

Demonstrate, unit by unit, that what was implemented matches its detailed design and satisfies the non-functional software requirements. This is done with a planned mix of static verification and unit testing: the approach is decided first (including what is repeated after a change), the criteria are defined, the verification is run and recorded, everything stays traceable, and the results are reported.

Scope marker: VDA scope, with rating-consistency guidance.

## Outcomes

1. A strategy for verifying the units exists and says how changed units are re-verified.
2. Verification criteria have been derived from that strategy and are fit to show that units comply with the detailed design and the non-functional software requirements.
3. Units have been verified as the strategy and the criteria prescribe, and the results are on record.
4. Units, verification criteria and verification results are consistent and linked to each other in both directions.
5. A summary of the unit verification results has been given to all affected parties.

## Base practices

| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SWE.4.BP1 | Develop software unit verification strategy including regression strategy | A strategy states how compliance of the units with the detailed design and the non-functional requirements will be shown, and what is re-verified when a unit changes. Static and dynamic analysis, code review and unit testing are typical techniques to choose from. Outcome 1. | Unit verification strategy or plan covering: methods per unit class or ASIL, test design methods, coverage metric and target values, static analysis tool and rule set, code review rules, entry / exit and pass / fail criteria, test environment (host, simulator, target), regression rules, treatment of generated and third-party code. | SAP.RL.1, SAP.RL.2, SAP.RL.3, SAP.RL.4, AGE.RC.7, APA.RL.8, SWE.4.RL.1, SWE.4.RL.2 |
| SWE.4.BP2 | Develop criteria for unit verification | Criteria are defined, as the strategy requires, that can prove compliance of the units, and of their interplay inside the component, with the detailed design and the non-functional requirements. For unit testing the criteria live in a unit test specification, which may itself be an executable script on an automated test bench. Test cases, test data, static checks, coverage goals and coding standards (for example the MISRA rules) are typical criteria. Outcome 2. | Unit test specification with test cases (ID, linked design element, preconditions, inputs, expected results, derivation method such as equivalence classes or boundary values) and test data; coverage goal per unit; selected coding standard with the project's rule classification; static analysis configuration file; code review checklist. | SWE.4.RL.7, SWE.4.RC.1, SWE.4.RC.2 |
| SWE.4.BP3 | Perform static verification of software units | Units are checked for correctness against the defined criteria by static means (static analysis, code review, conformance checks for coding standards or guidelines, other techniques) and the results are recorded. Non-conformances are handled through problem resolution (SUP.9). Outcome 3. | Static analysis report for the verified revision (rule violations, metrics); deviation records with rule number, rationale and approver; code review records with findings and closure; compiler warning log; problem records for confirmed defects. | MBD.RL.7, MBD.RL.8, MBD.RL.10, AGE.RC.11, SWE.4.RL.3, SWE.4.RL.4, SWE.4.RL.5, SWE.4.RL.6, SWE.4.RL.8 |
| SWE.4.BP4 | Test software units | Units are tested with the unit test specification in the way the strategy prescribes; results and logs are recorded. Non-conformances are handled through problem resolution (SUP.9). Outcome 3. | Unit test report and log per unit (verdict per test case, unit revision, date, environment and tool versions); structural coverage report (statement, branch, MC/DC as the strategy demands) with figures per unit; justification for code left uncovered; problem records for failed tests. | MBD.RL.9, MBD.RL.11, SWE.4.RL.3, SWE.4.RL.4, SWE.4.RL.5, SWE.4.RL.6, SWE.4.RL.7, SWE.4.RL.9 |
| SWE.4.BP5 | Establish bidirectional traceability | Links exist, navigable both ways, for three relations: units to static verification results, detailed design to unit test specification, unit test specification to unit test results. Outcome 4. | Test cases that reference design element IDs; result files keyed by test case ID and unit revision; static analysis and review results keyed by file / unit and revision; generated trace and coverage report. | TAC.RC.1, TAC.RC.2, TAC.RC.3, TAC.RC.4, SWE.4.RC.3 |
| SWE.4.BP6 | Ensure consistency | The unit test specification agrees in content with the detailed design. Traceability supports this; review records demonstrate it. Outcome 4. | Review record of the unit test specification against the detailed design, with reviewed revisions, findings and closure; re-review entries after design changes. | TAC.RL.1, TAC.RC.4, SWE.4.RC.4, CL2.RC.18 |
| SWE.4.BP7 | Summarize and communicate results | The results of static verification and of unit testing are condensed into a summary and passed to all affected parties, with enough information from the execution that the recipients can judge the consequences. Outcome 5. | Unit verification summary per release: per unit the tests passed / failed / not run, coverage achieved against target, open static findings, deviations granted, open problems; distribution record to Software Lead, Software Integrator and Quality Assurance Engineer. | SAC.RC.1, SAC.RC.2, SAC.RC.3, SAC.RC.4, SAC.RC.5, SAC.RC.6, SWE.4.RL.10, SWE.4.RL.11, CL2.RC.10 |

## Output work products

| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 08-50 | Test specification | 2 | Unit test cases with inputs, expected results and the design element each one verifies; test data; may be held as executable test scripts. |
| 08-52 | Test plan | 1 | The unit verification strategy: methods, criteria, coverage targets, environments, regression rules. |
| 13-04 | Communication record | 5 | Proof that the result summary was distributed: version, recipients, date. |
| 13-19 | Review record | 3, 4 | Code review results per unit, and the review of the unit test specification against the design; findings and closure. |
| 13-22 | Traceability record | 4 | Links design element to test case, test case to result, unit to static verification result, readable in both directions. |
| 13-25 | Verification results | 3, 5 | Outcome of the static verification per unit and revision, including deviations and their approval. |
| 13-50 | Test result | 3, 5 | Verdict and log per executed unit test case, with tested revision and environment; coverage achieved. |
| 15-01 | Analysis report | 3 | Output of static analysis and coverage analysis, with the assessment of findings. |

## Dependencies

Reading convention: "A depends on B" means the rating of A is tied to the rating of B. "Rule" comes from a solid line in the rating-consistency diagram, "recommendation" from a dashed line. External targets are the PA 1.1 (process performance) rating of the named process.

| From | Depends on | Kind | ID on the diagram | Relationship shown |
|---|---|---|---|---|
| SWE.4.BP2 | SWE.4.BP1 | rule | SWE.4.RL.7 | criteria are developed according to the strategy |
| SWE.4.BP4 | SWE.4.BP1 | rule | SWE.4.RL.7 | unit testing follows the strategy |
| SWE.4.BP3 | SWE.4.BP2 | rule | SWE.4.RL.8 | static verification uses the criteria |
| SWE.4.BP4 | SWE.4.BP2 | rule | SWE.4.RL.9 | unit testing uses the criteria (unit test specification) |
| SWE.4.BP7 | SWE.4.BP3 | rule | SWE.4.RL.10 | the summary covers static verification results |
| SWE.4.BP7 | SWE.4.BP4 | rule | SWE.4.RL.11 | the summary covers unit test results |
| SWE.4.BP2 | SWE.1 (PA 1.1) | recommendation | SWE.4.RC.1 | criteria show compliance with the non-functional software requirements |
| SWE.4.BP2 | SWE.3 (PA 1.1) | recommendation | SWE.4.RC.2 | criteria show compliance with the detailed design |
| SWE.4.BP5 | SWE.3 (PA 1.1) | recommendation | SWE.4.RC.3 | traceability reaches into units and detailed design |
| SWE.4.BP6 | SWE.3 (PA 1.1) | recommendation | SWE.4.RC.4 | consistency with the detailed design |
| SWE.4.BP5 | SWE.4.BP3 | dashed line, marked as having no recommendation ID | none | static verification results are one end of the traceability |
| SWE.4.BP5 | SWE.4.BP2 | dashed line, marked as having no recommendation ID | none | the unit test specification is one end of the traceability |
| SWE.4.BP5 | SWE.4.BP4 | dashed line, marked as having no recommendation ID | none | unit test results are one end of the traceability |
| SWE.4.BP6 | SWE.4.BP2 | dashed line, marked as having no recommendation ID | none | the unit test specification is one end of the consistency check |

Additional observations from the diagram:
- Unlike SWE.1 to SWE.3 there is no single hub. The chain is strategy (BP1), then criteria (BP2), then execution (BP3, BP4), then summary (BP7).
- BP5 and BP6 have no rule at all; they are tied to the rest only by recommendations and by the four dashed lines without ID listed above. In the catalog fragment those four are stored as kind "recommendation" with a comment, because the fragment format knows only two kinds.
- The recommendation lines to SWE.1 and SWE.3 are drawn with arrowheads at both ends.
- Cross-reference in the practice notes: SUP.9 for handling non-conformances found in BP3 and BP4.

## Automation notes

Assumed setting: unit tests and their specification live in the repository next to the code (test cases carry IDs and links to design elements); continuous integration runs static analysis, unit tests and coverage and stores machine-readable reports per commit; deviations are structured records; baselines are tags.

Deterministic checks a script can do:
- Strategy completeness: the strategy file has the mandatory sections (methods per unit class / ASIL, coverage metric and targets, static rule set, review rules, pass / fail and exit criteria, environment and tool versions, regression rules).
- Criteria coverage: every unit in the build has at least one linked test case or an explicit entry in the strategy saying why not (for example verified by review only); every design element marked testable is linked from at least one test case; every test case links to an existing design element.
- Result completeness: every specified test case has a result for the baselined revision of its unit, with verdict, commit hash, tool and environment version; no verdict other than "passed" without a linked problem record.
- Coverage thresholds: parse the coverage report and compare statement / branch / MC/DC figures per unit with the target the strategy sets for that unit's classification; each uncovered item needs a justification record.
- Static verification: an analysis report exists for exactly the baselined commit and the agreed tool configuration; zero findings in mandatory rule categories without a deviation record; each deviation record has rule number, scope, rationale, approver and is referenced from the code location; in-code suppressions without a deviation ID are rejected; compiler runs with warnings treated as errors.
- Review existence: each unit changed since the previous baseline has a code review record (or approved merge request) by someone other than the author, with all findings closed.
- Regression rule: for every unit whose source, design element or test specification changed since the last baseline, static analysis, unit tests and coverage results are newer than the change; unchanged units keep valid results only if the strategy allows it.
- Traceability both ways: design element to test case, test case to result, unit to static result; report gaps and percentages.
- Summary: generate the per-release summary (counts, coverage against target, open findings, deviations, linked problems) and check that a distribution record exists.

Needs semantic judgement (LLM-assisted, human-confirmed):
- Are the test cases adequate for the design: equivalence classes, boundary values, error paths, state transitions, interface value ranges?
- Do expected results come from the design rather than mirroring the code, and do the assertions actually check them?
- Does the test specification still match the design after a change (content, not just link presence)?
- Is each deviation rationale technically valid and specific to the code location?
- Is the justification for uncovered code sound (defensive code, unreachable by design) or a sign of missing tests or dead code?
- Are code review findings substantive, and is the strategy appropriate for the criticality of the units?

Stays with a human or with the target:
- Choosing methods and coverage targets, approving deviations, accepting residual risk.
- Confirming that results obtained on a host or simulator are representative for the target compiler and processor, and running tests on target where they are not.
- Confidence in the verification tools themselves (tool classification and qualification).
- Deciding what a failed verification means for the release.
