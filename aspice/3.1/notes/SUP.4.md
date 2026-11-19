# SUP.4 Joint Review

## Intent
Joint reviews keep the project and its stakeholders aligned on how far the work has come against the agreed objectives and on what still has to happen for the product to satisfy them. They take place at management level and at technical level and recur over the whole project. The process belongs to the extended VDA scope; no rating-consistency guidance is attached to it.

## Outcomes
1. Management reviews and technical reviews take place as the project needs them.
2. Stakeholders jointly assess the status and the results of process activities in these reviews.
3. Everyone affected learns the review results.
4. Action items from reviews are followed until closed.
5. Problems that surface are captured in a record.

General expectations:
- Joint reviews are tied to defined milestones of project or product development. Their scope and goals shift with the phase: early reviews tend to be conceptual and look at customer requirements, later ones look at the implementation.
- Reviews should examine varying aspects, for example use of hardware resources, newly introduced requirements or technologies, changes in team structure and technology changes.

## Base practices
| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SUP.4.BP1 | Define review elements | Driven by project needs, it is settled when management reviews and technical reviews happen, what they cover and who takes part; the resources they need (people, place, facilities) are agreed, and criteria for identifying problems, resolving them and reaching agreement are set. | Review plan or calendar; participant lists; review criteria | none |
| SUP.4.BP2 | Establish a mechanism to handle review outcomes | A defined mechanism makes sure results reach all affected parties, detected problems are recorded, and action items are logged for follow-up. | Minutes template and distribution rule; action and problem tracking set-up | none |
| SUP.4.BP3 | Prepare joint review | Review material is collected, planned, prepared and sent out ahead of the review as appropriate. | Invitation with agenda and material; entry criteria check | none |
| SUP.4.BP4 | Conduct joint reviews | Reviews at management level and at technical level take place as planned, and what they yield is recorded. | Review records or minutes with attendance | none |
| SUP.4.BP5 | Distribute the results | Results are documented and sent to all affected parties. | Minutes distribution evidence | none |
| SUP.4.BP6 | Determine actions for review results | Results are analysed, resolution actions are proposed and their priority is set. | Action list with priority and owner | none |
| SUP.4.BP7 | Track actions for review results | Actions that resolve problems found in a review are followed until closed. | Action status history; closure evidence | none |
| SUP.4.BP8 | Identify and record problems | Problems detected in reviews are identified and recorded through the established mechanism. | Problem records that reference the review | none |

Interpretation hints for review preparation (BP3): purpose and scope; products and problems under review; entry and exit criteria; agenda; roles, participants and responsibilities; distribution list; resources and facilities; supporting tools such as checklists or scenarios for perspective-based reading.

## Output work products
| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 13-04 | Communication record | 3 | Evidence that review results were distributed. |
| 13-05 | Contract review record | 1, 2, 3 | Result of reviewing agreement content with the stakeholders: scope, findings, decisions. |
| 13-07 | Problem record | 3, 5 | A problem raised in a review with description, status and resolution. |
| 13-09 | Meeting support record | 1, 2 | Agenda, participants, material and minutes. |
| 13-19 | Review record | all (1-5) | Object and version reviewed, participants, criteria, findings, decisions, actions. |
| 14-02 | Corrective action register | 3, 4, 5 | Actions from reviews with owner, priority, due date and status. |
| 14-08 | Tracking system | 3, 4, 5 | The tool or list in which review actions and problems are followed. |
| 15-01 | Analysis report | 3, 5 | Analysis of review results or of a specific problem raised in review. |
| 15-13 | Assessment/audit report | 1, 2 | Result of an assessment or audit performed as a joint review. |
| 15-16 | Improvement opportunity | 3, 4 | A suggested improvement arising from a review with rationale and proposed action. |

## Dependencies
No rating-consistency relations are recorded for this process.

Related processes by content: SUP.2 points to this process for peer reviews used as a verification method.

## Evidence in this toolkit
| BP | Carried by | Left to people |
|---|---|---|
| BP1 | the project plan (reviews with the customer under its reporting and interfaces) and the `meetings` of supplier agreements | - |
| BP2 | supplier agreements (`exchanges`, open items of their reviews) and problem resolution | - |
| BP3 | none: preparation of a joint review is not recorded as an item | material sent ahead, the agenda |
| BP4 | review records with participants of both sides; supplier reviews | - |
| BP5 | communication records with `--practice SUP.4.BP5` | - |
| BP6, BP7 | review findings; open items of supplier reviews with owner and state, followed to `closes` | priorities of actions |
| BP8 | problem reports; open items of supplier reviews | - |

## Automation notes
Assumed set-up: the review plan is a data file listing each planned joint review (milestone, type, scope, participants), and each held review produces a structured record (object versions, attendees, findings, decisions, actions).

Script (deterministic):
- For every milestone in the schedule that requires a joint review, a review record exists and is dated before the milestone was declared reached.
- The record lists reviewed objects with exact versions (tag or commit), attendees covering the required roles, and a decision.
- Material was distributed in advance: the invitation timestamp precedes the review by the agreed lead time.
- Each finding is typed as action or problem; actions have owner, priority and due date; problems link to a problem record; open and overdue actions are listed.
- Minutes were distributed to the distribution list within the agreed time after the review.

LLM (semantic judgement):
- Turn meeting notes into structured findings, actions and decisions for the participants to confirm.
- Check that the review scope fits the project phase and that the discussion covered the planned scope rather than a subset.
- Prepare a pre-review digest of changes since the last review from repository history.

Human (accountability):
- Holding the review, reaching agreement between the parties, setting priorities and accepting closure of actions.
