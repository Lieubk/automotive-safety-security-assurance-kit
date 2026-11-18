# SYS.5 System Qualification Test

## Intent

Test the fully integrated system against the system requirements, so that there is evidence it does what was required and can be handed over for delivery. The testing follows a planned strategy that includes regression, its cases are traceable to the requirements, and its results are recorded and reported.

Scope note: SYS.5 is in the VDA scope; rating rules, recommendations and a rating-consistency diagram are published for it.

## Outcomes

1. A system qualification test strategy, covering regression testing as well and fitting both the release plan and the project plan, exists for testing the integrated system.
2. A system qualification test specification has been derived from that strategy and is capable of showing that the integrated system complies with the system requirements.
3. Test cases are chosen from the specification as the release plan and the test strategy require.
4. The chosen cases are run against the integrated system and the results are recorded.
5. System requirements and qualification test cases agree in content and are linked in both directions, and test cases are linked in both directions to their results.
6. The qualification test results are summarised and have been made known to every affected party.

## Base practices

| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SYS.5.BP1 | Develop system qualification test strategy including regression test strategy | There is a strategy for qualification testing that fits both the release plan and the project plan, and it states how the integrated system is re-tested when a system item changes. Outcome 1. | Test strategy: scope, methods, environments, entry and exit criteria, selection criteria per release, regression rules | SAP.RL.1, SAP.RL.2, SAP.RL.3, SAP.RL.4, APA.RL.8, SYS.5.RL.1, SYS.5.RL.2, SYS.5.RC.2, SWE.1.RC.5, SWE.1.RC.6 |
| SYS.5.BP2 | Develop specification for system qualification test | A test specification exists whose test cases build on the verification criteria of the requirements, follow the test strategy, and are able to demonstrate that the integrated system complies with the system requirements. Outcome 2. | Test cases with ID, covered requirement, underlying verification criterion, preconditions, stimulus, expected result | SYS.5.RL.3, SYS.5.RL.9, SYS.5.RC.3 |
| SYS.5.BP3 | Select test cases | For each release, test cases are picked from the specification so that coverage is adequate for what the release plan and the test strategy demand. Outcome 3. | Selection list per release with the selection criterion and achieved requirement coverage; regression set for changed items | SYS.5.RL.4, SYS.5.RC.1, SYS.5.RL.10, SYS.5.RL.11, SYS.5.RC.4 |
| SYS.5.BP4 | Test integrated system | The selected cases have been executed on the integrated system and both results and logs are recorded. Outcome 4. | Result per executed case with verdict, tested configuration, test environment, date and tester; raw logs; problem reports for failures | SYS.5.RL.5, SYS.5.RL.6, SYS.5.RL.7, SYS.5.RL.8, SYS.5.RL.12 |
| SYS.5.BP5 | Establish bidirectional traceability | System requirements and qualification test cases are linked in both directions, and so are test cases and their results. Outcome 5. | Link data from requirements to test cases and from test cases to results; coverage figures | TAC.RC.1, TAC.RC.2, TAC.RC.3, TAC.RC.4, SYS.5.RC.5 |
| SYS.5.BP6 | Ensure consistency | The content of the test cases has been checked against the system requirements they claim to cover. Outcome 5. | Review record of the test specification against the requirements; findings and their closure | TAC.RL.1, TAC.RC.4, SYS.5.RC.6, CL2.RC.18 |
| SYS.5.BP7 | Summarize and communicate results | The results are condensed into a summary that reaches all affected parties. Outcome 6. | Test summary report per release with counts, open problems and requirement coverage; distribution record | SAC.RC.1, SAC.RC.2, SAC.RC.3, SAC.RC.4, SAC.RC.5, SAC.RC.6, CL2.RC.10 |

Practice notes:

- The verification criteria written during system requirements analysis (SYS.2.BP5) are the basis for the qualification test cases (BP2).
- Deviations found during testing are handled through SUP.9 (BP4).
- Two-way links are what make coverage checks, consistency checks and impact analysis possible (BP5).
- Consistency builds on those links and is typically evidenced by review records (BP6).
- A summary that carries all relevant information from test execution lets other parties judge what the results mean for them (BP7).

The rule (RL) and recommendation (RC) IDs above are identifiers from the VDA rating guideline; only the IDs are recorded here, not their wording. IDs whose prefix is not the process ID (SAP, APA, TAC, SAC, CL2, and SWE.1 for BP1) belong to other parts of that guideline.

## Output work products

| WP ID | Official name | Outcomes | What it should contain |
|---|---|---|---|
| 08-50 | Test specification | 2, 3 | Qualification test cases with covered requirement, preconditions, stimulus and expected result, plus the selection made for each release |
| 08-52 | Test plan | 1 | Qualification test strategy: scope, methods, environments, entry and exit criteria, selection criteria and regression rules |
| 13-04 | Communication record | 6 | Proof that the result summary was sent to the affected parties: what, to whom, when |
| 13-19 | Review record | 5 | Scope reviewed (which test specification and requirement versions), reviewers, consistency findings, decisions and closure |
| 13-22 | Traceability record | 5 | Links between system requirements and test cases and between test cases and results, navigable in both directions, with coverage status |
| 13-50 | Test result | 4, 6 | Verdict and log per executed case with tested configuration and environment, and the summary across the test run |

## Dependencies

Taken from the rating-consistency diagram for SYS.5. "Rule" means the line is drawn solid, "recommendation" means it is drawn dashed. "One-way" means the rating of the practice in the first column depends on the second column. "Two-way" means the line carries an arrowhead at both ends, which indicates that the two ratings depend on each other. "Plain" means the line has no arrowhead.

| Rating of | Depends on | Kind | ID on the line | Arrow | Relation shown |
|---|---|---|---|---|---|
| SYS.5.BP2 | SYS.5.BP1 | rule | SYS.5.RL.8, SYS.5.RL.9 | one-way | according to |
| SYS.5.BP3 | SYS.5.BP1 | rule | SYS.5.RL.8, SYS.5.RL.11 | one-way | according to |
| SYS.5.BP3 | SYS.5.BP2 | rule | SYS.5.RL.10 | one-way | select from |
| SYS.5.BP4 | SYS.5.BP3 | rule | SYS.5.RL.12 | one-way | using |
| SYS.5.BP7 | SYS.5.BP4 | rule (solid line) | none printed | one-way | summarize test results |
| SYS.5.BP5 | SYS.5.BP2 | recommendation (dashed line) | none printed | one-way | establish between |
| SYS.5.BP5 | SYS.5.BP4 | recommendation (dashed line) | none printed | one-way | establish between |
| SYS.5.BP1 | MAN.3 (PA 1.1) and SPL.2 (PA 1.1), drawn as one group | recommendation | SYS.5.RC.2 | plain | consistent with |
| SYS.5.BP3 | MAN.3 (PA 1.1) and SPL.2 (PA 1.1), drawn as one group | recommendation | SYS.5.RC.4 | plain | according to |
| SYS.5.BP2 | SYS.2 (PA 1.1) | recommendation | SYS.5.RC.5 (as printed) | two-way | ensure between |
| SYS.5.BP5 | SYS.2 (PA 1.1) | recommendation | SYS.5.RC.5 | two-way | ensure between |
| SYS.5.BP6 | SYS.2 (PA 1.1) | recommendation | SYS.5.RC.6 | two-way | ensure between |
| SYS.5.BP6 | SYS.5.BP2 | recommendation (dashed line) | branch of the SYS.5.RC.6 line | arrowhead at BP2 | ensure between |
| SYS.5.BP5 | SYS.5.BP2 | recommendation (dashed line) | none; labelled "no RC" | two-way | (no other text) |

Reading it:

- The practices form a chain: test strategy, test specification, selection, execution. The rating of each later practice depends by rule on an earlier one.
- The solid line from BP7 to BP4 carries no rule ID. It is recorded as a rule because it is drawn solid, but no numbered rule can be cited for it.
- MAN.3 stands for the project plan and SPL.2 for the release plan; the strategy (BP1) and the selection (BP3) should be rated in step with them.
- The quality of system requirements analysis (SYS.2) should show in the ratings of BP2, BP5 and BP6.
- BP5 is connected to BP2 twice: by the dashed unnumbered "establish between" line that also runs to BP4, and by a separate dashed line marked "no RC".

Points where the diagram and the per-practice ID lists do not line up (recorded as printed, not resolved):

- SYS.5.RL.8 is printed on both lines into BP1 (from BP2 and from BP3), while the per-practice list places it under BP4.
- The line between BP2 and SYS.2 is labelled RC.5, while the per-practice list gives SYS.5.RC.3 for BP2 and SYS.5.RC.5 for BP5. SYS.5.RC.3 is not printed anywhere on the diagram.
- The links from BP5 to BP2 and BP4 are dashed here, whereas the corresponding links in the SYS.4 diagram are solid.
- SWE.1.RC.5 and SWE.1.RC.6 are listed for BP1 although they carry the prefix of a software process.

## Automation notes

Assumed setting: system requirements with verification criteria, test plan and test specification are structured text with IDs and links in a git repository; qualification tests run on the real ECU on system benches, in the vehicle or in test laboratories the toolkit cannot reach; results come back as exported files.

Deterministic checks a script can run:

- The test plan contains the required parts: scope, methods and environments, entry and exit criteria, selection criteria per release, regression rules.
- Requirement coverage: every agreed system requirement is linked from at least one qualification test case, or carries a documented alternative verification measure; every test case links to at least one existing requirement.
- Each test case references the verification criterion it implements, and that criterion still exists in the current requirement version; a requirement changed after the link was last confirmed marks the test case as suspect.
- Test case schema: ID, preconditions, stimulus, expected result, required environment are filled.
- The selection for a release is a subset of the specification, states its criterion, and its coverage of the requirements planned for that release can be recomputed from the links.
- Regression set: from the diff between two release baselines, list changed requirements and changed system items and, through the trace links, the test cases that must be repeated; flag any that are missing from the selection.
- Result import: every selected case has exactly one current result for the release candidate; every result names the case, verdict, software tag, hardware sample revision, data set, test environment and date; results without a known case and selected cases without a result are flagged.
- Every failed or blocked result links to a problem report; no release summary is generated as "complete" while selected cases are unexecuted without a recorded waiver.
- Generate the summary: counts per verdict, requirement coverage, open problem reports, deviations from the planned selection, tested configuration.

Checks that need semantic judgement (LLM-assisted, human-confirmed):

- Whether a test case really demonstrates the requirement: does the expected result match the verification criterion, are limits, tolerances and negative cases covered.
- Whether the strategy is coherent with project plan and release plan content rather than merely referencing them.
- Drafting test cases from requirements and verification criteria; pointing out requirements whose criteria are too vague to test.
- Reading logs and tester comments to judge whether a deviation is explained, and drafting the narrative part of the summary.

What stays with humans (System Tester, Project Manager, Quality Assurance Engineer) and physical equipment:

- Executing the tests on the real system: system benches, hardware-in-the-loop rigs, vehicle tests, environmental, electrical and endurance testing in laboratories. The toolkit can only ingest exported logs and results; it cannot attest that a test was actually run or run correctly.
- Verdicts that rest on measurements, observation or driver perception.
- Accepting waivers for unexecuted or failed cases, and the decision to release the system for delivery.
- Sign-off of the summary and its communication to the customer.
