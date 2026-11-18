# SUP.2 Verification

## Intent
Verification establishes, work product by work product, that what was produced matches the requirements specified for it. It is planned through a strategy, performed against explicit criteria, and its findings are tracked as problems and reported. The process belongs to the extended VDA scope; no rating-consistency guidance is attached to it.

## Outcomes
1. A verification strategy is created, applied and kept current.
2. Verification criteria exist for every work product that has to be verified.
3. The verification activities that are required are carried out.
4. Defects are found, recorded and followed up.
5. The customer and the other parties involved have access to the verification results.

## Base practices
| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SUP.2.BP1 | Develop a verification strategy | A strategy, put into effect through a plan, names the verification activities with their methods, techniques and tools, what is verified, how independent the verifier must be, and when each activity takes place. | Verification strategy and plan; schedule entries for verification activities | none |
| SUP.2.BP2 | Develop criteria for verification | For each technical work product that must be verified, criteria state what counts as verified. | Checklists, review criteria and pass/fail criteria per work product type | none |
| SUP.2.BP3 | Conduct verification | The identified work products are verified following the strategy and against the criteria, confirming that they meet what was specified for them, and the results are recorded. | Verification results; review records; analysis reports | none |
| SUP.2.BP4 | Determine and track actions for verification results | Findings from verification are handed to problem resolution management (SUP.9) and followed there until closed. | Problem records linked to verification findings; closure evidence | none |
| SUP.2.BP5 | Report verification results | Everyone affected receives the verification results. | Verification report; distribution evidence | none |

Interpretation hints:
- Methods in use include inspections, walkthroughs, peer reviews (see SUP.4), audits and analysis.
- Verification of system and software is expected to give objective proof that what a life cycle phase produced (requirements, design, implementation, test) satisfies everything specified for that phase.

## Output work products
| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 13-04 | Communication record | 5 | Evidence that results were passed to the customer and other parties. |
| 13-07 | Problem record | 3, 4, 5 | A defect found by verification with description, classification, status and resolution. |
| 13-25 | Verification results | 2, 3, 4, 5 | Per verified item: version, criteria applied, method, verdict, findings, verifier and date. |
| 14-02 | Corrective action register | 4 | Actions arising from findings with owner, due date and status. |
| 18-07 | Quality criteria | 2 | The verification criteria per work product type. |
| 19-10 | Verification strategy | 1 | Objects, methods, tools, independence levels, schedule and reporting of verification. |

## Dependencies
No rating-consistency relations are recorded for this process.

Related processes by content: findings are handled through SUP.9 (BP4); peer reviews as a verification method connect to SUP.4.

## Automation notes
Assumed set-up: the verification strategy maps each work product type to a method (review, static analysis, test, analysis), a criteria set (checklist file or rule set) and an independence level; results are stored per item version.

Script (deterministic):
- Every work product type in the work product list has a method and a criteria set in the strategy; every criteria file referenced exists.
- For each item in a baseline, a verification result exists for exactly that version (commit hash or revision), with verdict, verifier and date; results for outdated versions are flagged.
- The independence level is met: the verifier differs from the author, and for higher levels belongs to a different team as defined in the strategy.
- Every failed criterion or open finding links to a problem record; no item is marked verified while linked problems are open.
- Run the tool-based parts directly (static analysis, schema and link checks, unit tests) and store their output as verification results.
- Generate the verification report: coverage of planned verification, verdicts, open findings.

LLM (semantic judgement):
- Apply review checklists whose questions need understanding of content (completeness, consistency with the parent item, ambiguity) and propose findings for a human reviewer to confirm.
- Check that the criteria fit the work product type and are specific enough to be decided.

Human (accountability):
- Setting the independence levels, confirming review verdicts, and accepting that verification of a baseline is complete.
