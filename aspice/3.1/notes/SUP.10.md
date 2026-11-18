# SUP.10 Change Request Management

## Intent
Change request management makes sure that no change to an agreed work product happens informally: each request is recorded, analysed for impact, decided by an authorized body, implemented, checked and followed until closed. Links between a change request, the work products it touches and, where applicable, the problem that caused it make the change auditable. The process belongs to the VDA scope and has rating-consistency guidance.

## Outcomes
1. A strategy for managing change requests exists.
2. Requests for change are recorded and can be identified.
3. Relationships and dependencies between change requests are known.
4. Criteria that confirm a change request has been implemented are set.
5. Change requests are analysed and the resources they need are estimated.
6. Approval and priority of changes rest on the analysis results and the resources available.
7. Changes that were approved get implemented and are followed until closed.
8. The status of every change request is known.
9. Change requests and the work products they affect are linked in both directions.

## Base practices
| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SUP.10.BP1 | Develop a change request management strategy | A strategy defines the change request activities, a status model, the criteria used in analysis, responsibilities and the interfaces to affected parties, and is kept current. | Change management plan; status model; analysis criteria; definition of the deciding body | SAP.RL.1, SAP.RL.2, SAP.RL.3, SAP.RL.4, APA.RL.6, SUP.10.RL.1 |
| SUP.10.BP2 | Identify and record the change requests | Every change request gets a unique identifier, a description and a record as the strategy defines, naming who raised it and why. | Change request records with identifier, initiator, reason and description | SUP.9.RC.6, SUP.10.RL.8, CL2.RC.16 |
| SUP.10.BP3 | Record the status of change requests | Each change request carries a status taken from the status model so that it can be tracked. | Status field and status history per change request | SUP.10.RL.6, SUP.10.RL.7, SUP.10.RL.8, SUP.10.RC.7, SUP.10.RC.8, SUP.10.RC.9, SUP.10.RC.10, CL2.RC.16 |
| SUP.10.BP4 | Analyze and assess change requests | Following the strategy, each request is analysed, including how it depends on affected work products and on other requests; its impact is assessed and criteria that will confirm its implementation are defined. | Impact analysis with affected items, effort estimate, risks and dependencies; confirmation criteria in the record | PLS.RC.6, APA.RL.5, SUP.10.RL.4, SUP.10.RL.5, SUP.10.RC.5, SUP.10.RC.6, SUP.10.RL.8, SUP.10.RC.11, SUP.10.RC.12 |
| SUP.10.BP5 | Approve change requests before implementation | Before any implementation starts, requests are prioritized from the analysis results and resource availability and approved as the strategy defines. | Decision record of the Change Control Board with date, priority and target release | SUP.10.RL.3, SUP.10.RC.4, SUP.10.RL.8, SUP.10.RL.9 |
| SUP.10.BP6 | Review the implementation of change requests | Before a request is closed, its implementation is reviewed to confirm that the confirmation criteria are met and that every relevant process was applied. | Review record per change request; evidence that affected work products were updated and re-verified | SUP.10.RL.4, SUP.10.RL.5, SUP.10.RC.5, SUP.10.RC.6, SUP.10.RC.13 |
| SUP.10.BP7 | Track change requests to closure | Requests are followed until closed and the initiator is told the result. | Status history through to closed; feedback to the initiator | SUP.9.RC.7, SUP.10.RL.6, SUP.10.RL.7, SUP.10.RC.7, SUP.10.RL.10, CL2.RC.16 |
| SUP.10.BP8 | Establish bidirectional traceability | Links exist in both directions between a change request and the work products it affects, and between a change request and the problem reports that caused it, where a problem was the trigger. | Trace links from change request to changed items and back; links between change requests and problem records | TAC.RC.1, TAC.RC.2, TAC.RC.3, SUP.10.RL.11 |

Interpretation hints:
- Example states for a status model: open, in analysis, approved, assigned, implemented, fixed, closed.
- Analysis criteria usually include resource needs, effects on the schedule, risks and benefits.
- The activities as a whole should guarantee that requests are identified, described, recorded, analysed, implemented and managed in a systematic way.
- The strategy may prescribe different handling at different stages of the product life cycle, for instance prototype build versus series development.
- A Change Control Board is the usual approval mechanism; assigning requests to releases is one way to prioritize them.
- Bidirectional links are what make consistency checks, completeness checks and impact analysis possible.
- The identifier list for BP3 contains a range that is read here as SUP.10.RL.6 to SUP.10.RL.8; confirm against the guideline.

## Output work products
| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 08-28 | Change management plan | 1 | Activities, status model, analysis criteria, responsibilities, deciding body, interfaces. |
| 13-16 | Change request | 2, 3, 4, 5, 6, 7 | Identifier, initiator, reason, description, related requests, impact analysis, confirmation criteria, decision, priority, implementation references. |
| 13-19 | Review record | 7 | Review of the implemented change against its confirmation criteria, with findings and verdict. |
| 13-21 | Change control record | 8, 9 | Status history of the request and the links to affected work products and problem records. |

## Dependencies
Rating-consistency relations from the VDA guideline. `A -> B` means the rating of A depends on B; `<->` marks a relation that applies in both directions. Only IDs are recorded here.

| From | To | Kind | ID | Relation |
|---|---|---|---|---|
| SUP.10.BP2 | SUP.10.BP1 | rule | SUP.10.RL.8 | Recording follows the strategy. |
| SUP.10.BP3 | SUP.10.BP1 | rule | SUP.10.RL.8 | Status recording follows the strategy. |
| SUP.10.BP4 | SUP.10.BP1 | rule | SUP.10.RL.8 | Analysis follows the strategy. |
| SUP.10.BP5 | SUP.10.BP1 | rule | SUP.10.RL.8 | Approval follows the strategy. |
| SUP.10.BP5 | SUP.10.BP4 | rule | SUP.10.RL.9 | Approval is based on the analysis. |
| SUP.10.BP7 | SUP.10.BP3 | rule | SUP.10.RL.10 | Tracking is based on the recorded status. |
| SUP.10.BP8 | SUP.10.BP2 | rule | SUP.10.RL.11 | Traceability is established for the recorded change requests. |
| SUP.10.BP3 | SUP.10.BP1 | recommendation | SUP.10.RC.8 | No wording established. |
| SUP.10.BP3 | SUP.10.BP2 | recommendation | SUP.10.RC.9 | A status is assigned to each recorded change request. |
| SUP.10.BP4 | SUP.10.BP3 | recommendation | SUP.10.RC.11 | Relation worded as "based on" between analysis and recorded status. |
| SUP.10.BP4 | SUP.10.BP8 | recommendation | SUP.10.RC.12 | Analysis uses the dependencies held in the trace links. |
| SUP.10.BP4 | SUP.10.BP2 | recommendation | not established | Analysis covers dependencies to other recorded change requests. |
| SUP.10.BP6 | SUP.10.BP4 | recommendation | SUP.10.RC.13 | The review checks the confirmation criteria set in the analysis. |
| SUP.10.BP4 | process performance of the processes owning affected work products | recommendation (<->) | SUP.10.RC.14 | Analysis covers dependencies to affected work products. |
| SUP.10.BP6 | process performance of all relevant processes | recommendation (<->) | SUP.10.RC.15 | The review ensures the relevant processes were applied. |
| SUP.10.BP8 | SUP.9.BP7 | recommendation (<->) | SUP.10.RC.16 | Traceability to the corresponding problem reports. |
| SUP.10.BP8 | process performance of the processes owning affected work products | recommendation | SUP.10.RC.17 | Traceability to the affected work products. |

Seen from other processes: SUP.9.BP7 relates to SUP.10.BP2 by SUP.9.RC.6 and SUP.9.BP8 to SUP.10.BP7 by SUP.9.RC.7; ACQ.4.BP1 relates to SUP.10 as a whole by ACQ.4.RC.3.

## Automation notes
Assumed set-up: change requests are structured records with a status history; every commit and merge request names the change request (or problem) it serves; work products carry IDs, so links can be checked mechanically; the strategy defines the status model and the approval roles as data.

Script (deterministic):
- Identifiers are unique; mandatory fields are filled (initiator, reason, description); every status belongs to the status model and every transition in the history is permitted.
- Before a request reaches the approved state it has an impact analysis listing affected item IDs that exist, an effort estimate, links to related requests and confirmation criteria.
- Approval is recorded by the Change Control Board or another permitted role and is dated before the first commit that references the request; commits without a valid reference, or referencing an unapproved request, are rejected by a hook or reported.
- Bidirectional links: every item changed by the referenced commits appears in the list of affected items, every listed item was actually changed or is explicitly marked "no change needed", and each changed item points back to the request in its change history.
- A request triggered by a problem links to the problem record and the problem links back.
- Before closure: a review record exists, linked verification evidence is newer than the last related commit, and the initiator was notified.
- Status overview: counts per state, age, target release, requests blocked by dependencies.

LLM (semantic judgement):
- Walk the trace graph from the items named in a request and propose further affected items the analysis missed (dependent requirements, design elements, tests, documents).
- Judge whether the confirmation criteria are specific enough to be decided and whether the implementation review actually addressed them.
- Summarize a request and its impact for the Change Control Board.

Human (accountability):
- The decision to approve, reject or defer, the priority and the target release; acceptance of closure.
