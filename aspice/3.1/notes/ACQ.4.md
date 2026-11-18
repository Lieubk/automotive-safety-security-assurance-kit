# ACQ.4 Supplier Monitoring

## Intent
Supplier monitoring is how the assessed organization, acting as customer, keeps track of what its own supplier delivers and how. Both sides agree on shared processes, interfaces and the information to exchange, meet regularly on technical content and on progress, and correct deviations or renegotiate the agreement when needed. In this process "customer" means the assessed party and "supplier" means the supplier of that party. The process belongs to the VDA scope and has rating-consistency guidance.

## Outcomes
1. Activities that customer and supplier agreed to perform together take place as needed.
2. The information both sides agreed to exchange flows regularly between them.
3. The performance of the supplier is checked against what was agreed.
4. Necessary changes to the agreement are negotiated by both parties and written into it.

## Base practices
| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| ACQ.4.BP1 | Agree on and maintain joint processes, joint interfaces, and information to be exchanged | An agreement with the supplier, kept current, covers shared processes and interfaces, who is responsible for what, which information is exchanged, and the kind and rhythm of meetings, reviews, status reporting and other joint activities. | Collaboration or interface agreement under version control; responsibility matrix; meeting and reporting calendar; list of work products to exchange | TPS.RC.8, TPS.RC.9, TPS.RC.10, TPS.RC.11, TPS.RC.13, ACQ.4.RL.2, ACQ.4.RC.1, ACQ.4.RC.3 |
| ACQ.4.BP2 | Exchange all agreed information | The agreed interfaces are actually used to pass on everything that was agreed, including the relevant work products. | Delivery and receipt records; exchanged status reports; transfer logs | SAC.RC.1, SAC.RC.2, TPS.RC.2, TPS.RC.3, ACQ.4.RL.3 |
| ACQ.4.BP3 | Review technical development with the supplier | Technical reviews with the supplier happen at the agreed rhythm, deal with technical matters, problems and risks, and open items are followed until closed. | Technical review minutes; open-item list with status history | ACQ.4.RL.3, ACQ.4.RL.4 |
| ACQ.4.BP4 | Review progress of the supplier | Supplier progress on schedule, quality and cost is reviewed at the agreed rhythm; open items are closed out and risk mitigation is carried out. | Progress review minutes; supplier status reports compared with plan; supplier risk list | TPS.RC.12, ACQ.4.RL.3, ACQ.4.RL.5 |
| ACQ.4.BP5 | Act to correct deviations | When agreed objectives are missed, action is taken to bring the work back to the agreed plan and to stop the problem recurring; changed objectives are negotiated and written into the agreement. | Corrective action entries; change requests against the agreement; updated agreement version | ACQ.4.RC.2 |

Interpretation hints:
- Shared processes and interfaces normally span quality assurance, configuration and change management, problem resolution, requirements and project management, and acceptance by the customer.
- Which activities are performed jointly has to be agreed by both sides.
- The information to exchange should include every relevant work product.

## Output work products
| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 02-01 | Commitment/agreement | 4 | The agreement between both parties with its amendments, each traceable to a negotiated change. |
| 13-01 | Acceptance record | 3 | Result of accepting a supplier delivery: what was checked, against which criteria, outcome. |
| 13-04 | Communication record | 1, 2 | Evidence of information exchanged and of joint activities held. |
| 13-09 | Meeting support record | 1 | Agenda, participants, material and minutes of joint meetings. |
| 13-14 | Progress status record | 2 | Supplier status against plan at a given date. |
| 13-16 | Change request | 4 | A requested change to the agreement or to agreed objectives with analysis and decision. |
| 13-19 | Review record | 2 | Findings and decisions of technical and progress reviews with the supplier. |
| 14-02 | Corrective action register | 4 | Deviations of the supplier with action, owner, due date and status. |
| 15-01 | Analysis report | 3 | Evaluation of supplier performance or of a specific deviation, with conclusions. |

## Dependencies
Rating-consistency relations from the VDA guideline. `A -> B` means the rating of A depends on B; `A <-> B` means the relation applies in both directions. Only IDs are recorded here.

| From | To | Kind | ID | Relation |
|---|---|---|---|---|
| ACQ.4.BP2 | ACQ.4.BP1 | rule | ACQ.4.RL.3 | Information is exchanged according to what was agreed. |
| ACQ.4.BP3 | ACQ.4.BP1 | rule | ACQ.4.RL.3 | Technical reviews are held according to what was agreed. |
| ACQ.4.BP4 | ACQ.4.BP1 | rule | ACQ.4.RL.3 | Progress reviews are held according to what was agreed. |
| ACQ.4.BP3 | ACQ.4.BP2 | rule | ACQ.4.RL.4 | No wording established. |
| ACQ.4.BP4 | ACQ.4.BP2 | rule | ACQ.4.RL.5 | Progress reviews are based on the exchanged information. |
| ACQ.4.BP5 | ACQ.4.BP2 | recommendation | ACQ.4.RC.2 | Corrective action relates to the exchanged information. |
| ACQ.4.BP5 | ACQ.4.BP3 | recommendation | ACQ.4.RC.2 | Corrective action relates to technical review results. |
| ACQ.4.BP5 | ACQ.4.BP4 | recommendation | ACQ.4.RC.2 | Corrective action relates to progress review results. |
| ACQ.4.BP1 | SUP.10, SYS.1, MAN.3 and every other process in scope | recommendation (<->) | ACQ.4.RC.3 | Joint processes have to be consistent with the processes of the assessed party. |
| ACQ.4.BP5 | SUP.9 (process performance) | recommendation (<->) | ACQ.4.RC.4 | Handling of deviations has to be consistent with problem resolution management. |

## Automation notes
Assumed set-up: the agreement and its annexes (exchange list, meeting calendar, responsibility matrix) are versioned text files; supplier deliveries are checked into a dedicated area and tagged; minutes and open items are structured records.

Script (deterministic):
- The agreement contains the mandatory parts (joint processes, interfaces, responsibilities, exchange list, meeting and reporting rhythm).
- For each agreed periodic meeting or report there is a record inside the period; missing periods are listed.
- Each item on the exchange list has a receipt record with version and date for every due delivery; deliveries are tagged and their checksums match the supplier's delivery note.
- Open items from supplier reviews have owner and due date; overdue or stale items are listed; closed items carry closure evidence.
- Every change to the agreement file is linked to a change request with an approval; corrective actions against the supplier have a status.
- Supplier-reported milestone dates are compared with the agreed dates and slips are flagged.

LLM (semantic judgement):
- Read supplier status reports and minutes, extract deviations, risks and commitments, and compare them with the agreed objectives.
- Check that review minutes actually cover technical matters, problems and risks rather than logistics only.
- Draft the open-item list and the supplier performance summary for the Project Manager.

Human (accountability):
- Negotiating and signing the agreement and its changes, accepting deliveries, deciding corrective action and escalation towards the supplier.
