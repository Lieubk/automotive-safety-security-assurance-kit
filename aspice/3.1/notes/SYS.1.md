# SYS.1 Requirements Elicitation

## Intent

Keep a managed, continuous exchange with the customer and other stakeholders so that their needs and requests are collected, read the same way on both sides, explicitly agreed, and frozen as a baseline on which all later engineering work rests. Once that baseline exists, every change to it goes through a controlled path that weighs impact and risk, and the requester can always see what became of a request.

Scope note: SYS.1 belongs to the extended VDA scope rather than the basic VDA scope, and no rating rules, recommendations or rating-consistency diagram are published for it.

## Outcomes

1. A standing communication channel with the stakeholders exists and is in use.
2. Stakeholder requirements have been agreed with the parties concerned, written down and put under a baseline.
3. A change mechanism is in place that assesses changes driven by shifting stakeholder needs and folds the accepted ones into the baselined requirement set.
4. Stakeholder needs are watched continuously through a defined mechanism.
5. A customer can find out with little effort where each of its requests stands and what was decided about it.
6. Changes caused by new technology or by evolving stakeholder needs are detected, their risks are evaluated and their effects are kept under control.

## Base practices

| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SYS.1.BP1 | Obtain stakeholder requirements and requests | Requirements and requests are actively gathered: by asking the customer directly and by working through every document that shapes them (customer specifications, the commercial proposal where relevant, descriptions of the target operating and hardware environment). The origin of each item is recorded. Outcomes 1, 4. | Imported customer specifications with one ID per item and a source reference; intake log of requests; minutes of elicitation sessions | none published |
| SYS.1.BP2 | Understand stakeholder expectations | Customer and supplier interpret every requirement identically; ambiguous or unclear items were clarified together and the clarification is on record. Outcome 2. | Clarification or question-and-answer list with answers; joint review record | none published |
| SYS.1.BP3 | Agree on requirements | Every party concerned has given explicit consent to the requirement set the project will work to. Outcome 2. | Acceptance status per requirement (accepted, rejected, in clarification); signed or otherwise attributable agreement record | none published |
| SYS.1.BP4 | Establish stakeholder requirements baseline | The agreed requirements are formalised and frozen as the reference for project work and for tracking against stakeholder needs. Requirements the stakeholder never voiced but which the specified and intended use demands are worked out by the supplier and added before freezing. Outcomes 2, 3. | Identified baseline (tag or labelled version) of the stakeholder requirements; list of supplier-added implicit requirements with rationale | none published |
| SYS.1.BP5 | Manage stakeholder requirements changes | Every change is handled relative to the baseline. Improvements arising from new technology or new needs are recognised, and the people affected get the chance to judge impact and risk and to start change control and mitigation. Outcomes 3, 6. | Change requests that name the affected baseline items; impact and risk assessment per change; decision record; successor baseline | none published |
| SYS.1.BP6 | Establish customer-supplier query communication mechanism | The customer has a way to see the state and outcome of the changes it requested, and the supplier is able to deliver the necessary information and data in the language and format the customer asked for. Outcome 5. | Shared query or request tracker with status and decision per entry; agreed exchange formats; minutes of status meetings | none published |

Practice notes:

- Elicitation is a joint activity; people from both the customer and the supplier side may take part (BP1).
- Feasibility studies and cost or schedule analyses are legitimate inputs both for agreeing requirements and for judging a requested change (BP1, BP3, BP5).
- For each customer requirement, capture the data needed to trace it later, such as source document, version and location (BP1).
- Walking through requirements and requests together with the customer improves shared understanding; SUP.4 Joint Review is the related process (BP2). The same instrument, or formal written status reporting, serves the status communication under BP6.
- Change triggers are diverse: technology moves on, stakeholder needs shift, legal constraints change (BP5).
- A dedicated repository or information management system may be necessary to store, find and reference everything learned while defining the agreed requirements (BP5).
- Tell the customer about a change before it is implemented, so that its effect on schedule, cost and functionality can be judged first (BP6).
- Information handed to the customer may have to be supplied as CAD data or through electronic data interchange (BP6).

## Output work products

| WP ID | Official name | Outcomes | What it should contain |
|---|---|---|---|
| 08-19 | Risk management plan | 6 | How risks that come from changing technology or stakeholder needs are identified, rated, assigned to an owner and tracked, including escalation thresholds |
| 08-20 | Risk mitigation plan | 6 | For each significant change-related risk: chosen response, concrete actions, owner, due date and the condition that triggers a fallback |
| 13-04 | Communication record | 1, 4 | Dated evidence of exchanges with stakeholders: minutes, query logs, status reports, data transmitted and to whom |
| 13-19 | Review record | 4, 5 | What was reviewed with the stakeholder, participants, findings, decisions and open points with owners |
| 13-21 | Change control record | 3, 4 | Per change request: originator, affected baseline items, impact and risk assessment, decision, current status and the baseline that absorbed it |
| 15-01 | Analysis report | 2, 3, 6 | Feasibility, cost, schedule and impact analyses that back the agreement of requirements and the evaluation of changes, with conclusions |
| 17-03 | Stakeholder Requirements | 1, 2 | The agreed requirement set with unique IDs, origin of each item, agreement status and the implicit requirements added by the supplier, held under a baseline |

## Dependencies

- No rating-consistency diagram and no rule or recommendation IDs exist for SYS.1, so there are no formal rating dependencies to record for its own base practices.
- SYS.1 as a whole (its process performance, PA 1.1) is a dependency target for SYS.2: recommendations SYS.2.RC.5, SYS.2.RC.8 and SYS.2.RC.9 tie SYS.2.BP1, SYS.2.BP6 and SYS.2.BP7 to it. Weak elicitation results therefore have to be reflected when system requirements analysis is rated.
- Content references (not rating dependencies): SUP.4 Joint Review supports BP2 and BP6.

## Automation notes

Assumed setting: stakeholder requirements live in the repository as structured text items with IDs, change requests are tracked as files or tracker issues, baselines are tags.

Deterministic checks a script can run:

- Every stakeholder requirement item has a unique ID, a source reference (document, version, section), an agreement status and an owner; no item in a tagged baseline is still "in clarification" without a recorded exception.
- A baseline tag for the stakeholder requirements exists, and the tagged content is identical to what downstream links point at.
- Any commit that touches stakeholder requirement files after the baseline tag references a change request ID; change requests have impact, risk, decision and status fields filled before they are closed.
- When the customer delivers a new specification release: import it, diff it item by item against the baseline and list added, changed and removed items as candidate change requests.
- Generate the customer-facing status list (request, state, decision, target baseline) straight from the tracker data; flag requests with no movement beyond an agreed age.
- Open clarification questions older than a threshold; requirements marked "accepted" without a linked agreement record.

Checks that need semantic judgement (LLM-assisted, human-confirmed):

- Spotting ambiguous, incomplete or contradictory wording in customer text and drafting clarification questions.
- Proposing implicit requirements the customer did not state but the intended use, legislation or applicable standards imply.
- Classifying incoming requests (new requirement, change, question) and summarising the likely impact of a specification diff.
- Reading meeting minutes to judge whether agreement was actually reached or merely discussed.

What stays with humans (Project Manager, System Requirements Engineer, Customer):

- The agreement itself: commitment by customer and supplier, commercial and feasibility decisions, risk acceptance.
- Negotiation of priorities and scope, and all direct communication with the customer; the repository can only hold the record of it.
- Deciding which stakeholders are relevant and whether the communication mechanism is actually working for them.
