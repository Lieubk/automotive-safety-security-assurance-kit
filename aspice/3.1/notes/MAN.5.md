# MAN.5 Risk Management

## Intent
Risk management looks ahead for events that could damage the project, ranks them, decides how to deal with each one and keeps checking whether the treatment is working. It runs for the whole project and is not a list written once at kick-off. The process belongs to the extended VDA scope; no rating-consistency guidance is attached to it.

## Outcomes
1. It is decided what risk management has to cover.
2. Fitting strategies for managing risk are defined and put into practice.
3. Risks are spotted as they emerge over the course of the project.
4. Risks are analysed and ranked so that treatment effort goes where it matters most.
5. Measures for risks are defined, applied and evaluated, showing how risk status changes and how far treatment has come.
6. Risks are treated according to their priority, likelihood and consequence, or another defined threshold, so that their impact is corrected or avoided.

## Base practices
| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| MAN.5.BP1 | Establish risk management scope | It is decided which kinds of risk the project manages, in line with the risk policy of the organization. | Scope section of the risk management plan; reference to the organizational risk policy | none |
| MAN.5.BP2 | Define risk management strategies | The way risks are found and mitigated is defined, together with the level at which a risk or a group of risks is acceptable, for the project and for the organization. | Risk management plan with identification method, rating scales, acceptance thresholds and review cadence | none |
| MAN.5.BP3 | Identify risks | Risks are collected when the project strategy is set up and again whenever technical or managerial decisions are taken; the search for risk factors never stops. | Risk register entries created throughout the project; risk review minutes; risks raised from change requests or design decisions | none |
| MAN.5.BP4 | Analyze risks | Each risk is rated so that mitigation resources can be assigned in order of priority. | Rated and ranked risk register; risk analysis report | none |
| MAN.5.BP5 | Define risk treatment actions | Each risk, alone or in a group, gets actions that hold it at or bring it down to an acceptable level are chosen, carried out and tracked. | Mitigation actions with owner, due date and status, each linked to a risk | none |
| MAN.5.BP6 | Monitor risks | Indicators are defined per risk or group of risks, applied and evaluated to see whether the risk status changes and whether mitigation advances. | Risk status reports with trend; indicator values over time; evidence that major risks were reported upward | none |
| MAN.5.BP7 | Take corrective action | When mitigation does not progress as expected, further action is taken to shrink or avoid the impact. | Corrective action entries linked to risks; revised mitigation plan | none |

Interpretation hints:
- Risk kinds to consider include technical, commercial and timing risks.
- Areas usually scanned for risk sources: cost, schedule, effort, resources and technology.
- Typical risk factors: trade-offs (settled or still open), a decision to drop a feature, design changes, resources that fail to materialize.
- Rating normally uses likelihood, consequence and severity.
- Analysis techniques that expose risks in the system itself include functional analysis, simulation, FMEA and FTA.
- Major risks may need visibility and monitoring at higher management levels.
- Corrective action can mean a new mitigation strategy or an adjusted one.

## Output work products
| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 07-07 | Risk measure | 5 | Definition of an indicator for a risk: what is measured, how, threshold and reporting interval. |
| 08-14 | Recovery plan | 4, 6 | What to do if a risk materializes: trigger, steps, responsibilities, resources. |
| 08-19 | Risk management plan | all (1-6) | Scope, strategy, rating scales, acceptance levels, roles, cadence, reporting and escalation. |
| 08-20 | Risk mitigation plan | 3, 4, 5, 6 | Per risk: chosen treatment, actions, owners, dates and expected residual risk. |
| 13-20 | Risk action request | 1, 2, 6 | A request to act on a risk with reason, proposed action and decision. |
| 14-02 | Corrective action register | 6 | Actions taken when mitigation falls short, with owner, due date and status. |
| 14-08 | Tracking system | 5, 6 | The register or tool in which risks and their actions are recorded and followed. |
| 15-08 | Risk analysis report | 4 | Identified risks with rating, ranking and rationale. |
| 15-09 | Risk status report | 4, 5 | Current exposure, changes since the last report and mitigation progress. |

## Dependencies
No rating-consistency relations are recorded for this process.

Related processes by content: risk information can feed project estimation in MAN.3.BP5.

## Automation notes
Assumed set-up: the risk register is a structured file (one record per risk with ID, description, category, likelihood, impact, priority, owner, treatment, indicator, status, last review date), kept under version control.

Script (deterministic):
- Mandatory fields are present; rating values come from the scales defined in the risk management plan; recorded priority equals the value computed from likelihood and impact.
- Every risk above the acceptance threshold has at least one treatment action with owner and due date; overdue actions are listed.
- The last review date of each open risk is within the review cadence; closed risks carry a closure rationale.
- Risks link to existing work packages, change requests or requirements where a link is given.
- Register history from version control shows that risks are added and re-rated during the project, not only at the start.
- Generate the risk status report (counts by priority, trend since last baseline, top risks).

LLM (semantic judgement):
- Propose candidate risks from new change requests, schedule slips, design decisions and open problems.
- Check whether a mitigation action addresses the stated cause or only the symptom; detect duplicate or overlapping risks.
- Check whether an indicator is able to show a change in the risk it belongs to.

Human (accountability):
- Setting acceptance thresholds, accepting residual risk, deciding escalation to higher management.
- Rating risks whose context lies outside the repository (supplier situation, staffing, commercial matters).
