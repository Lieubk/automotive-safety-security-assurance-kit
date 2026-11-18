# REU.2 Reuse Program Management

## Intent
An organization-level process that runs reuse as a managed programme: it decides where reuse pays off, checks how ready the organization is, vets proposed reusable assets before they are used, and watches whether the programme delivers. It is part of neither the VDA scope nor the extended VDA scope, and no rating-consistency guidance is attached to it.

## Outcomes
1. A reuse strategy exists that states why, where and to what end the organization reuses.
2. Every domain has been examined for how much reuse it can offer.
3. The domains where reuse will be explored or practised are selected.
4. The ability of the organization to reuse systematically has been assessed.
5. Proposed reuse is evaluated to confirm the reused product fits the application it is intended for.
6. Reuse is carried out in line with the strategy.
7. Channels for feedback, communication and notification between the parties involved are set up and working.
8. The reuse programme is monitored and evaluated.

## Base practices
| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| REU.2.BP1 | Define organizational reuse strategy | The reuse programme and the infrastructure it needs are defined for the organization. | Reuse strategy and policy; description of the asset repository and its governance | none |
| REU.2.BP2 | Identify domains for potential reuse | Groups of systems and their components that share properties are identified, such that reusable assets could be collected for building systems in that domain. | Domain list; domain model; domain architecture | none |
| REU.2.BP3 | Assess domains for potential reuse | Each domain is examined for where reusable components and products could be used and applied. | Domain assessment report naming reuse candidates | none |
| REU.2.BP4 | Assess reuse maturity | The readiness of the organization for reuse is understood, giving a starting baseline and success criteria for running the programme. | Reuse maturity assessment; baseline metrics and targets | none |
| REU.2.BP5 | Evaluate reuse proposals | Offered reusable components and products are evaluated for fitness for the use that is proposed. | Reuse proposal with evaluation result and decision | none |
| REU.2.BP6 | Implement the reuse program | The activities the programme defines are carried out. | Reuse plan with completed activities; assets published in the repository; projects consuming them | none |
| REU.2.BP7 | Get feedback from reuse | Mechanisms for feedback, assessment, communication and notification between the parties involved exist and are used to steer the programme. | Feedback records from consuming projects; notifications about asset changes or defects | none |
| REU.2.BP8 | Monitor reuse | Programme implementation is checked periodically and judged against actual needs. | Reuse evaluation reports; reuse metrics over time | none |

Interpretation hints:
- Parties involved typically include developers, domain engineers, asset managers, programme administrators, operators and maintenance groups.
- Quality requirements for reusable work products should be defined.
- BP2 maps to outcome 2 and BP3 to outcome 3 in the process model, although the wording of the two outcomes suggests the reverse pairing; the mapping is kept as the model defines it.

## Output work products
| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 04-02 | Domain architecture | 2 | Common structure of the systems in a domain, showing fixed and variable parts. |
| 04-03 | Domain model | 2 | Shared concepts, features and variability of a domain. |
| 08-17 | Reuse plan | 5, 6 | Programme activities, responsibilities, schedule and resources. |
| 09-03 | Reuse policy | 1 | Organizational commitment and rules for reuse. |
| 12-03 | Reuse proposal | 4 | A proposed reuse case: asset, target use, expected benefit, constraints. |
| 13-04 | Communication record | 7 | Evidence of feedback and notifications exchanged between asset providers and users. |
| 15-07 | Reuse evaluation report | 5, 6, 8 | Suitability evaluation of an asset or evaluation of the programme against its goals. |
| 15-13 | Assessment/audit report | 3, 4 | Results of the domain assessment and of the reuse maturity assessment. |
| 19-05 | Reuse strategy | 1 | Purpose, scope, goals and objectives of reuse and the supporting infrastructure. |

## Dependencies
No rating-consistency relations are recorded for this process.

## Automation notes
Assumed set-up: reusable assets live in their own repositories or packages; each carries a manifest (ID, version, owner, intended domain, assumptions and constraints of use, quality status, known defects) and consuming projects declare the assets they use with pinned versions.

Script (deterministic):
- Every asset has a complete manifest; every asset used by a project is taken from the catalogue at a pinned, released version.
- The list of consumers per asset is derived from dependency declarations, so a defect or new version of an asset can be notified to exactly the projects that use it.
- A reuse proposal record exists, with decision, for each asset a project consumes.
- Reuse metrics: number of reused versus newly developed components per project, age of consumed versions, open defects in consumed assets.

LLM (semantic judgement):
- Compare the assumptions and constraints stated in an asset manifest with the requirements and architecture of the target project and list mismatches for the suitability evaluation.
- Summarize feedback from consuming projects into improvement candidates for the asset owner.

Human (accountability):
- The reuse strategy, the selection of domains and the decision to accept a reuse proposal.
- The suitability argument for reused components in safety-related or security-related functions, which the Functional Safety Engineer or Cybersecurity Engineer has to own.
