# SUP.9 Problem Resolution Management

## Intent
Problem resolution management makes sure that every problem is captured, understood, acted on and followed until it is resolved, and that the overall problem situation is visible. A strategy defines the status model, responsibilities, the handling of urgent cases and who has to be alerted; each problem then moves through that model with a record of cause, impact, action and closure. The process belongs to the VDA scope and has rating-consistency guidance.

## Outcomes
1. A strategy for managing problem resolution exists.
2. Problems are recorded, each with a unique identifier, and classified.
3. Problems are analysed and assessed so that a suitable solution can be chosen.
4. Resolution of problems is started.
5. Problems are followed until they are closed.
6. Problem status and trends are known.

## Base practices
| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SUP.9.BP1 | Develop a problem resolution management strategy | A strategy defines the resolution activities, a status model, alert notification, responsibilities, the handling of urgent cases and the interfaces to affected parties, and these definitions are kept current. | Problem management plan; status model; severity and urgency definitions; notification and escalation rules | SAP.RL.1, SAP.RL.2, SAP.RL.3, SAP.RL.4, SUP.9.RL.1, SUP.9.RL.2, SUP.9.RL.7, SUP.9.RL.8, SUP.9.RC.1 |
| SUP.9.BP2 | Identify and record the problem | Every problem gets a unique identifier, a description and a record, with enough supporting information to reproduce and diagnose it. | Problem records with identifier, description, reproduction steps, environment, origin and reporter | none (no rule and no recommendation assigned) |
| SUP.9.BP3 | Record the status of problems | Each problem carries a status taken from the status model so that it can be tracked. | Status field and status history per problem | SUP.9.RL.7, SUP.9.RL.8, SUP.9.RC.1, SUP.9.RL.9, SUP.9.RC.2 |
| SUP.9.BP4 | Diagnose the cause and determine the impact of the problem | The problem is investigated for cause and impact so that it can be categorized and suitable actions chosen. | Cause and impact analysis in the record; category or severity assignment | SUP.9.RL.3, SUP.9.RL.4, SUP.9.RL.5, SUP.9.RL.6, SUP.9.RC.3 |
| SUP.9.BP5 | Authorize urgent resolution action | Where the strategy classes a problem as urgent, authorization for immediate action is obtained in the way the strategy prescribes. | Authorization record for urgent fixes with approver and time | SUP.9.RL.9, SUP.9.RL.10 |
| SUP.9.BP6 | Raise alert notifications | Where the strategy classes a problem as strongly affecting other systems or other parties, an alert is issued in the way the strategy prescribes. | Alert notifications with recipients and date, linked to the problem | SUP.9.RL.3, SUP.9.RL.4, SUP.9.RL.5, SUP.9.RL.6, SUP.9.RL.9, SUP.9.RC.4 |
| SUP.9.BP7 | Initiate problem resolution | Actions that resolve the problem are started as the strategy defines and are themselves reviewed, or a change request is raised. | Resolution actions or linked change requests; review of the proposed actions | SUP.9.RL.9, SUP.9.RC.5, SUP.10.RC.16 |
| SUP.9.BP8 | Track problems to closure | Problem status, including that of linked change requests, is followed to closure, and a problem is closed only after an authorized formal acceptance. | Status history through to closed; closure approval record; status of linked change requests | SUP.9.RL.7, SUP.9.RL.8, SUP.9.RC.1, SUP.9.RL.11 |
| SUP.9.BP9 | Analyze problem trends | Problem data are collected and analysed, trends are identified, and project-level actions are started as the strategy defines. | Trend reports by category, origin, detection phase and age; actions derived from trends | SUP.9.RL.9 |

Interpretation hints:
- Resolution activities may differ between stages of the product life cycle, for instance between prototype build and series development.
- Supporting information usually covers where the problem came from, how to reproduce it, the environment and who found it.
- A unique identifier is what makes tracing from a problem to the resulting changes possible.
- Categories (such as A/B/C or light/medium/severe) may reflect severity, impact, criticality, urgency and relevance for the change process.
- Change requests raised from problems are managed in SUP.10. Process improvements that prevent problems belong to PIM.3, generic project management improvements such as lessons learned to MAN.3, and generic improvements to work products to SUP.1.
- Useful trend data per problem: location, detection method and time, and consequences.

## Output work products
| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 08-27 | Problem management plan | 1 | Activities, status model, classification scheme, responsibilities, urgent path, alert rules, interfaces. |
| 13-07 | Problem record | 2, 3, 4, 5 | Identifier, description, reproduction data, classification, cause, impact, actions, status history, closure approval. |
| 15-01 | Analysis report | 3 | Cause and impact analysis of a problem or a group of problems. |
| 15-05 | Evaluation report | 3 | Assessment of candidate solutions and the reason for the chosen one. |
| 15-12 | Problem status report | 6 | Counts by status and category, ageing, trends and resulting actions. |

## Dependencies
Rating-consistency relations from the VDA guideline. `A -> B` means the rating of A depends on B; `<->` marks a relation that applies in both directions. Only IDs are recorded here.

| From | To | Kind | ID | Relation |
|---|---|---|---|---|
| SUP.9.BP3 | SUP.9.BP1 | rule | SUP.9.RL.9 | Status recording follows the strategy. |
| SUP.9.BP5 | SUP.9.BP1 | rule | SUP.9.RL.9 | Urgent authorization follows the strategy. |
| SUP.9.BP6 | SUP.9.BP1 | rule | SUP.9.RL.9 | Alert notification follows the strategy. |
| SUP.9.BP7 | SUP.9.BP1 | rule | SUP.9.RL.9 | Initiation of resolution follows the strategy. |
| SUP.9.BP9 | SUP.9.BP1 | rule | SUP.9.RL.9 | Trend analysis follows the strategy. |
| SUP.9.BP5 | SUP.9.BP4 | rule | SUP.9.RL.10 | Urgent authorization builds on the actions determined in the diagnosis. |
| SUP.9.BP8 | SUP.9.BP3 | rule | SUP.9.RL.11 | Tracking to closure is based on the recorded status. Classified as rule because of its RL identifier; confirm against the guideline. |
| SUP.9.BP3 | SUP.9.BP2 | recommendation | SUP.9.RC.2 | A status is assigned to each recorded problem. |
| SUP.9.BP4 | SUP.9.BP2 | recommendation | SUP.9.RC.3 | The diagnosis investigates the recorded problem. |
| SUP.9.BP6 | SUP.9.BP4 | recommendation | SUP.9.RC.4 | Alerts build on the actions determined in the diagnosis. |
| SUP.9.BP7 | SUP.9.BP4 | recommendation | SUP.9.RC.5 | Resolution builds on the actions determined in the diagnosis. |
| SUP.9.BP7 | SUP.10.BP2 | recommendation (<->) | SUP.9.RC.6 | Resolution may initiate change requests. |
| SUP.9.BP8 | SUP.10.BP7 | recommendation (<->) | SUP.9.RC.7 | Problem tracking includes related change requests. |

Seen from other processes: SUP.1.BP5 and SUP.1.BP6 are related to SUP.9 by SUP.1.RC.8, ACQ.4.BP5 by ACQ.4.RC.4, and SUP.10.BP8 to SUP.9.BP7 by SUP.10.RC.16.

## Automation notes
Assumed set-up: problems are structured records (issue-tracker export or one file per problem) with a status history; the strategy defines the status model, the classification scheme, the urgent path and alert rules as data that a script can read.

Script (deterministic):
- Identifiers are unique; mandatory fields are filled (description, reproduction steps, environment, version or baseline in which the problem was found, origin, reporter, classification).
- Every status is part of the status model and every transition in the history is a permitted one.
- Cause and impact fields are filled before a problem leaves the analysis state; classification values come from the defined scheme.
- A problem flagged urgent has an authorization entry by a permitted role dated before the first related commit.
- A problem above the alert threshold has a notification record naming the recipients required by the strategy.
- A resolved problem links to a change request or commit and to verification evidence; a closed problem has an acceptance entry by an authorized person who is not the implementer; all linked change requests are closed.
- Ageing and overdue lists; counts per status, category, component and detection phase per period for the trend report.

LLM (semantic judgement):
- Is the description sufficient for someone else to reproduce the problem? Does the stated cause explain the symptom, or does it restate it?
- Find duplicates and related problems; cluster problems into recurring causes for the trend analysis.
- Check that the impact analysis considered other variants, releases and affected parties.

Human (accountability):
- Authorizing urgent action, deciding the classification of safety-related or security-related problems, accepting closure.
- Deciding which project-level actions follow from a trend.
