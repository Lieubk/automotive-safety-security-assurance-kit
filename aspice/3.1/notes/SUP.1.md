# SUP.1 Quality Assurance

## Intent
Quality assurance gives independent and objective evidence that processes and the work products they yield conform to the provisions and plans set for them, and it makes sure deviations are fixed and do not come back. Two things carry the process: a QA function that is not steered by the people whose work it checks, and an escalation path that management actually answers. The process belongs to the VDA scope and has rating-consistency guidance.

## Outcomes
1. A quality assurance strategy is created, applied and kept current.
2. Quality assurance is carried out independently and objectively, free of conflicts of interest.
3. Where a work product, process or activity does not meet the requirements that apply to it, the deviation is recorded, made known to those concerned, followed until resolved, and its recurrence is prevented.
4. It is checked and documented that work products, processes and activities do meet their applicable requirements, and the result is shared with those concerned.
5. Quality assurance is empowered to raise non-conformances to suitable management levels.
6. Management makes sure that escalated non-conformances get resolved.

## Base practices
| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SUP.1.BP1 | Develop a project quality assurance strategy | A project-level strategy states how quality assurance of work products and of processes is carried out with independence and objectivity and without conflict of interest. | QA strategy or quality plan naming scope, methods, cadence, independence arrangement, reporting and escalation path | SAP.RL.1, SAP.RL.2, SAP.RL.3, SAP.RL.4, AGE.RC.10, SUP.1.RL.1, SUP.1.RL.2, SUP.1.RL.3, SUP.1.RL.4, SUP.1.RL.5, SUP.1.RC.1, SUP.1.RC.2, CL2.RC.12 |
| SUP.1.BP2 | Assure quality of work products | Following the strategy and the project schedule, work products are checked against their defined requirements and the result is documented. | Work product QA records; completed checklists; non-conformance entries | AGE.RC.11, APA.RL.7, SUP.1.RL.6, SUP.1.RL.7, SUP.1.RC.3, SUP.1.RC.6, SUP.1.RC.9, CL2.RC.17 |
| SUP.1.BP3 | Assure quality of process activities | Following the strategy and the schedule, it is checked that processes reach their defined goals, and the result is documented. | Process audit records; process compliance checklists; findings | SUP.1.RL.6, SUP.1.RL.7, SUP.1.RC.3, SUP.1.RC.7 |
| SUP.1.BP4 | Summarize and communicate quality assurance activities and results | How quality assurance is performing, which deviations it found and how they trend is reported regularly, as the strategy defines, to those who need to know or have to act. | Periodic QA reports with trend data; distribution evidence | SAC.RC.1, SAC.RC.2, SUP.1.RC.4, SUP.1.RC.5 |
| SUP.1.BP5 | Ensure resolution of non-conformances | Quality assurance findings on products and processes are analysed, followed, corrected and kept from recurring. | Non-conformance records with cause, action, status and closure evidence | SUP.1.RL.8, SUP.1.RL.9, SUP.1.RC.4, SUP.1.RC.5, SUP.1.RC.8 |
| SUP.1.BP6 | Implement an escalation mechanism | An escalation path defined in the strategy lets quality assurance bring problems to suitable management levels and other stakeholders so that they get resolved; the path is kept working. | Documented escalation path; escalation records with management response | DID.RL.9, SUP.1.RC.4, SUP.1.RC.5, SUP.1.RC.8 |

Interpretation hints:
- Independence can be organizational, financial or both.
- Quality assurance may build on results of verification, validation, joint reviews, audits and problem management instead of repeating them.
- Process quality assurance can take the form of audits and assessments, problem analysis, periodic checks of tools, methods, documents and process adherence, and lessons learned carried into later projects.
- For work products the usual means are reviews and problem analysis, with reports and lessons learned feeding improvements of later versions.
- Requirements for work products and goals for processes may stem from applicable standards.
- Non-conformances in work products may be handled through SUP.9; weaknesses in a process definition or in the way it is applied may be handed to PIM.3.

## Output work products
| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 08-13 | Quality plan | 1, 2 | QA scope, objects to check, methods, cadence, independence arrangement, reporting and escalation. |
| 13-04 | Communication record | 3, 4, 5 | Evidence that results, deviations and escalations reached the intended recipients. |
| 13-07 | Problem record | 3, 5 | A non-conformance with description, cause, action, status and escalation state. |
| 13-18 | Quality record | 2, 3, 4 | Result of a QA check: object, criteria, checker, date, conformance verdict, findings. |
| 13-19 | Review record | 2, 3, 4 | What was reviewed, by whom, against which criteria, findings and their disposition. |
| 14-02 | Corrective action register | 3, 5, 6 | Non-conformances with action, owner, due date, status and escalation history. |
| 18-07 | Quality criteria | 1 | The criteria a work product or process must meet to be judged conformant. |

## Dependencies
Rating-consistency relations from the VDA guideline. `A -> B` means the rating of A depends on B; `<->` marks a relation that applies in both directions. All relations recorded for this process are recommendations. Only IDs are recorded here.

| From | To | Kind | ID | Relation |
|---|---|---|---|---|
| SUP.1.BP2 | SUP.1.BP1 | recommendation | SUP.1.RC.6 | Work product QA is performed according to the strategy. |
| SUP.1.BP3 | SUP.1.BP1 | recommendation | SUP.1.RC.7 | Process QA is performed according to the strategy. |
| SUP.1.BP4 | SUP.1.BP1 | recommendation | not established | Reporting follows the strategy. |
| SUP.1.BP6 | SUP.1.BP1 | recommendation | not established | Escalation follows the strategy. |
| SUP.1.BP4 | SUP.1.BP2 | recommendation | SUP.1.RC.4 | Reporting is based on work product QA results. |
| SUP.1.BP4 | SUP.1.BP3 | recommendation | SUP.1.RC.5 | Reporting is based on process QA results. |
| SUP.1.BP5 | SUP.1.BP2 | recommendation | SUP.1.RC.4 | Resolution relates to work product non-conformances. |
| SUP.1.BP5 | SUP.1.BP3 | recommendation | SUP.1.RC.5 | Resolution relates to process non-conformances. |
| SUP.1.BP6 | SUP.1.BP2 | recommendation | SUP.1.RC.4 | Escalation relates to work product non-conformances. |
| SUP.1.BP6 | SUP.1.BP3 | recommendation | SUP.1.RC.5 | Escalation relates to process non-conformances. |
| SUP.1.BP5 | SUP.9 (process performance) | recommendation (<->) | SUP.1.RC.8 | Non-conformances are treated as problems. |
| SUP.1.BP6 | SUP.9 (process performance) | recommendation (<->) | SUP.1.RC.8 | Escalated items are treated as problems. |
| SUP.1.BP2 | SUP.8.BP8 | recommendation (<->) | SUP.1.RC.9 | Work product QA includes aspects of verifying configuration item information. |

## Automation notes
Assumed set-up: work products are text files with status metadata, reviews happen as merge requests or review records with named reviewers, non-conformances are structured records, and the QA strategy lists which checks apply to which work product type and process step.

Script (deterministic):
- For each work product type named in the strategy, the required check exists for every instance before it enters a baseline (review record present, checklist complete, status "released").
- Template conformance: mandatory sections and attributes present, IDs unique, links resolve, traceability coverage above the agreed threshold.
- Process adherence from repository history: every merged change references an approved change request or problem, has a review approval, and passed the required pipeline stages.
- Independence indicator: the person recorded as QA checker or approver is never the author of the checked item, and the QA role is not held by the Project Manager of the same project.
- Non-conformance records have owner, due date and status; overdue ones are flagged for escalation; escalated ones carry a management response before closure.
- Generate the periodic QA report: checks planned versus performed, conformance rate, open and overdue non-conformances, trend against previous periods.

LLM (semantic judgement):
- Judge a work product against content-level quality criteria that a schema cannot express (for example whether a requirement is unambiguous and verifiable, whether a review comment was really addressed).
- Compare what the strategy promises with what the records show and point out silent gaps.
- Cluster non-conformances into recurring causes and draft preventive actions.

Human (accountability):
- The organizational independence of the Quality Assurance Engineer; an automated check that is run by the same agent or person who produced the work product does not count as independent assurance.
- The conformance verdict on audits, the decision to escalate, and the management decision on escalated items.
