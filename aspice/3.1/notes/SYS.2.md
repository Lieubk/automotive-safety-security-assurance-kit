# SYS.2 System Requirements Analysis

## Intent

Convert the agreed stakeholder requirements into system requirements for the ECU-level product that system design can work from. The resulting set has to be structured, examined for correctness, feasibility and verifiability, assessed for its effect on the surroundings the system operates in and on cost and schedule, kept linked to its stakeholder sources, and agreed with and distributed to everyone who builds on it.

Scope note: SYS.2 is in the VDA scope; rating rules, recommendations and a rating-consistency diagram are published for it.

## Outcomes

1. The system requirements exist as a defined set.
2. The system requirements are categorised and have been examined for correctness and verifiability.
3. The effect of the system requirements on the operating environment has been analysed.
4. Priorities for implementing the system requirements are set.
5. The system requirements are revised whenever that becomes necessary.
6. Stakeholder requirements and system requirements agree in content and are linked in both directions.
7. The consequences of the system requirements for cost, schedule and the technical solution have been evaluated.
8. Agreement on the system requirements has been reached and every affected party has been informed of them.

## Base practices

| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SYS.2.BP1 | Specify system requirements | The functions and capabilities the system needs are derived from the stakeholder requirements and from changes to them, and are written down as functional and non-functional items in a system requirements specification. Outcomes 1, 5, 7. | Specification with uniquely identified functional and non-functional requirements, including application parameters that shape behaviour; change history showing updates that follow stakeholder changes | APA.RL.1, APA.RL.3, SYS.2.RL.1, SYS.2.RL.2, SYS.2.RL.3, SYS.2.RC.5 |
| SYS.2.BP2 | Structure system requirements | The specification is organised in a way that serves the project, for example by clustering related items, putting them in a sensible order, categorising them on criteria the project cares about and ranking them by stakeholder need. Outcomes 2, 4. | Category, priority and target-release attributes on each item; chapter or cluster structure; mapping of content to releases | SYS.2.RL.4, SYS.2.RL.5, SYS.2.RC.1, SYS.2.RL.9 |
| SYS.2.BP3 | Analyze system requirements | Each requirement, and the dependencies among requirements, has been examined for correctness, technical feasibility and verifiability. The analysis feeds risk identification and states the consequences for cost, schedule and the technical solution. Outcomes 1, 2, 7. | Analysis result per requirement or cluster (feasibility, verifiability, risk, effort and schedule effect); review record; inputs handed over to project estimation | AGE.RC.3, SYS.2.RL.6, SYS.2.RC.2, SYS.2.RL.9 |
| SYS.2.BP4 | Analyze the impact on the operating environment | The interfaces between the system and its neighbours in the operating environment are identified, and it has been worked out what the system requirements mean for those interfaces and for the environment as a whole. Outcomes 3, 7. | System context or boundary description; interface requirements; documented impact analysis per neighbouring element | SYS.2.RC.3, SYS.2.RC.4, SYS.2.RL.9 |
| SYS.2.BP5 | Develop verification criteria | Every system requirement carries verification criteria that state, in qualitative and quantitative terms, how its fulfilment will be checked. Outcomes 2, 7. | Verification-criteria attribute or linked item per requirement (method, pass condition, tolerances); system test cases that visibly build on those criteria | VEC.RL.1, VEC.RL.2, SYS.2.RL.7, SYS.2.RL.9 |
| SYS.2.BP6 | Establish bidirectional traceability | Stakeholder requirements and system requirements are linked so that the relation can be followed from either side. Outcome 6. | Link data or trace matrix; coverage figures in both directions; list of unlinked items with justification | TAC.RC.1, TAC.RC.2, TAC.RC.3, TAC.RC.4, TAC.RL.2, TAC.RL.3, SYS.2.RL.9, SYS.2.RC.8 |
| SYS.2.BP7 | Ensure consistency | The content of the system requirements has been checked against the stakeholder requirements they come from: nothing contradicts, nothing is lost, nothing is added without reason. Outcome 6. | Review record that covers the content of linked pairs; findings and their closure | TAC.RL.1, TAC.RL.2, TAC.RL.3, TAC.RC.4, SYS.2.RL.8, SYS.2.RL.9, SYS.2.RC.9, CL2.RC.18 |
| SYS.2.BP8 | Communicate agreed system requirements | The agreed requirement set, and each later update of it, reaches all parties who need it. Outcome 8. | Release note or notification per baseline; distribution list; acknowledgement from system architecture, software, hardware and test | SAC.RL.1, SAC.RC.4, SAC.RC.5, SAC.RC.6, SYS.2.RL.9, CL2.RC.9 |

Practice notes:

- Application parameters that affect functions or capabilities count as system requirements (BP1).
- Changes to stakeholder requirements are processed through SUP.10 (BP1).
- Prioritisation normally includes mapping functional content to the planned releases; SPL.2.BP1 is the related practice (BP2).
- Cost and schedule findings are an input for adjusting project estimates; MAN.3.BP5 is the related practice (BP3).
- Verification criteria show that a requirement can be verified inside the agreed constraints, and they usually serve as the starting point for system test cases or for other verification measures (BP5).
- Verification that testing cannot deliver is handled under SUP.2 (BP5).
- Two-way links are what make coverage checks, consistency checks and impact analysis possible (BP6).
- Consistency builds on those links and is typically evidenced by review records (BP7).

The rule (RL) and recommendation (RC) IDs above are identifiers from the VDA rating guideline; only the IDs are recorded here, not their wording. IDs whose prefix is not the process ID (TAC, SAC, VEC, APA, AGE, CL2) belong to parts of that guideline that are not specific to this process.

## Output work products

| WP ID | Official name | Outcomes | What it should contain |
|---|---|---|---|
| 13-04 | Communication record | 8 | Proof that each agreed baseline and each update was sent to the affected parties: what, to whom, when |
| 13-19 | Review record | 6 | Scope reviewed (which requirement versions), reviewers, findings on consistency with stakeholder requirements, decisions and closure |
| 13-21 | Change control record | 1 | Per change to the requirement set: trigger, affected items, analysis, decision and resulting version |
| 13-22 | Traceability record | 6 | The links between stakeholder and system requirements, navigable in both directions, with coverage status |
| 15-01 | Analysis report | 2, 3, 4, 7 | Results of the correctness, feasibility, verifiability, operating-environment, priority and cost/schedule/technical analyses, with conclusions and risks |
| 17-08 | Interface requirements specification | 1, 3 | Requirements on the interfaces between the system and its environment: partners, exchanged data or energy, electrical, timing and protocol properties |
| 17-12 | System requirements specification | 1, 5 | Functional and non-functional system requirements with IDs, attributes (category, priority, release, status) and version history |
| 17-50 | Verification criteria | 2 | Per requirement: how fulfilment is demonstrated, with measurable pass conditions |

## Dependencies

Taken from the rating-consistency diagram for SYS.2. "Rule" means the line is drawn solid, "recommendation" means it is drawn dashed. "One-way" means the rating of the practice in the first column depends on the second column. "Two-way" means the line carries an arrowhead at both ends, which indicates that the two ratings depend on each other.

| Rating of | Depends on | Kind | ID on the line | Arrow | Relation shown |
|---|---|---|---|---|---|
| SYS.2.BP2 | SYS.2.BP1 | rule | SYS.2.RL.9 | one-way | structures |
| SYS.2.BP3 | SYS.2.BP1 | rule | SYS.2.RL.9 | one-way | analyzes |
| SYS.2.BP4 | SYS.2.BP1 | rule | SYS.2.RL.9 | one-way | analyzes the impact |
| SYS.2.BP5 | SYS.2.BP1 | rule | SYS.2.RL.9 | one-way | uses |
| SYS.2.BP6 | SYS.2.BP1 | rule | SYS.2.RL.9 | one-way | uses |
| SYS.2.BP7 | SYS.2.BP1 | rule | SYS.2.RL.9 | one-way | uses |
| SYS.2.BP8 | SYS.2.BP1 | rule | SYS.2.RL.9 | one-way | communicates |
| SYS.2.BP3 | MAN.3.BP5 | recommendation | SYS.2.RC.6 | two-way | uses |
| SYS.2.BP3 | MAN.5.BP3 | recommendation | SYS.2.RC.7 | two-way | uses |
| SYS.2.BP1 | SYS.1 (PA 1.1) | recommendation | SYS.2.RC.5 | two-way | uses |
| SYS.2.BP6 | SYS.1 (PA 1.1) | recommendation | SYS.2.RC.8 | two-way | establish between |
| SYS.2.BP7 | SYS.1 (PA 1.1) | recommendation | SYS.2.RC.9 | two-way | ensure between |

Reading it:

- BP1 is the anchor: the rating of every other base practice of the process depends on it by rule.
- The quality of elicitation (SYS.1) should show in the ratings of BP1, BP6 and BP7.
- Requirement analysis (BP3) should be rated in step with project estimation (MAN.3.BP5 Define, monitor and adjust project estimates and resources) and risk identification (MAN.5.BP3 Identify risks).
- SYS.2.RC.6 and SYS.2.RC.7 appear only on the diagram; they are not in the per-practice ID list for BP3.

## Automation notes

Assumed setting: stakeholder and system requirements are structured text items with IDs and typed links in a git repository; baselines are tags; reviews are recorded as files or merge-request approvals.

Deterministic checks a script can run:

- Schema: every system requirement has a unique ID, a type (functional or non-functional), category, priority, target release, status, and a non-empty verification-criteria field or link.
- Upward coverage: every system requirement links to at least one stakeholder requirement, or is marked as derived with a rationale. Downward coverage: every agreed stakeholder requirement is linked from at least one system requirement or carries a documented "not applicable to the system" disposition.
- Link hygiene: no link points at a missing, rejected or superseded item; a stakeholder item changed after the link was last confirmed marks the link as suspect.
- Interface requirements name a partner that exists in the system context description.
- Every change to the specification after a baseline tag references a change request; the baseline tag has a review record whose scope covers the tagged commit.
- A notification or release note exists for each baseline, and the distribution list is not empty.
- Report: coverage in both directions, items without priority or release, requirements whose analysis attributes (feasibility, verifiability, risk) are still empty.

Checks that need semantic judgement (LLM-assisted, human-confirmed):

- Wording quality: one requirement per item, unambiguous, free of untestable terms, no hidden design decisions.
- Whether each system requirement really refines or satisfies the stakeholder items it is linked to, and whether anything in the parent is left uncovered despite a link being present.
- Contradictions, duplicates and undeclared dependencies between requirements.
- Whether the verification criteria are measurable and match the requirement they belong to.
- Drafting a first operating-environment impact analysis from the interface list, and proposing missing non-functional requirements.

What stays with humans (System Requirements Engineer, Project Manager, Customer):

- Technical feasibility verdicts, cost and schedule evaluation, and the hand-over of those results to project estimation and risk management.
- Prioritisation and release assignment negotiated with stakeholders.
- Agreement and approval of the specification, and the decision that a review finding is closed.
