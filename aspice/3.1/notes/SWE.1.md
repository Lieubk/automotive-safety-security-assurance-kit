# SWE.1 Software Requirements Analysis

## Intent

Turn the software-relevant share of the system requirements and of the system architecture into a complete, structured and verifiable set of software requirements. The set is analysed (correctness, feasibility, effect on the hardware and basic software around it, cost and schedule), linked upward in both directions, kept current under change, and agreed with everyone who designs, builds or tests against it.

Scope marker: VDA scope, with rating-consistency guidance.

## Outcomes

1. The requirements that the software elements of the system have to fulfil are defined, together with the software's interfaces.
2. Requirements are sorted into categories and have been checked for being correct and verifiable.
3. It is understood how the software requirements affect the environment the software runs in.
4. An implementation priority exists for the requirements.
5. The requirement set is revised whenever a change makes that necessary.
6. Software requirements are consistent with the system requirements and with the system architectural design, and traceable to each of them in both directions.
7. Cost, schedule and technical consequences of the requirements have been assessed.
8. The requirements are agreed, and every affected party has been informed of them.

## Base practices

| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SWE.1.BP1 | Specify software requirements | Functional and non-functional software requirements are derived from the system requirements, the system architecture and later changes to either, and are recorded as individual items in a software requirements specification. Application (calibration / configuration) parameters that shape behaviour are treated as requirement input coming from the system level. In a software-only project the "system" is a given operating environment and the stakeholder requirements take the place of the system-level inputs. Outcomes 1, 5, 7. | Requirement items with a unique ID, a single "shall" statement, a type attribute (functional, timing, memory, diagnostic, safety, security, interface) and an ASIL / QM attribute; interface requirement items covering the hardware-software interface, bus signals from the communication matrix, diagnostic services, non-volatile data and calibration parameters with range and default; item history showing updates that follow upstream change requests. | PLS.RC.4, PLS.RC.5, APA.RL.1, APA.RL.3, SWE.1.RL.1, SWE.1.RL.2, SWE.1.RL.3; from the diagram: SWE.1.RC.5, SWE.1.RC.6 |
| SWE.1.BP2 | Structure software requirements | The specification is organised so the project can work with it: items are clustered, ordered, categorised by criteria the project chose, and prioritised by stakeholder need. Prioritising normally means assigning each item to a planned release (see SPL.2.BP1). Outcomes 2, 4. | Chapter or folder structure by feature / function group; category attribute with a defined value list; priority and target-release attribute on every item; a release-content view generated from those attributes. | SWE.1.RL.4, SWE.1.RL.5, SWE.1.RC.1, SWE.1.RL.10 |
| SWE.1.BP3 | Analyze software requirements | The specified items, including how they depend on each other, are examined for correctness, verifiability and technical feasibility, and the examination feeds risk identification. Effects on cost, schedule and technical solution are assessed; the cost and schedule part is an input for re-estimating the project (see MAN.3.BP5). Outcomes 2, 7. | Requirement review or analysis record with a checklist (atomic, unambiguous, feasible, verifiable, conflict-free); feasibility notes such as a timing or memory estimate or a prototype result; impact analysis attached to each change request with effort and schedule effect; risks entered in the project risk list with a reference to the requirement. | AGE.RC.3, SWE.1.RL.6, SWE.1.RC.2, SWE.1.RL.10 |
| SWE.1.BP4 | Analyze the impact on the operating environment | It is analysed what the requirements mean for the interfaces of other system elements and for the environment in which the software executes (hardware, operating system and the like). Outcomes 3, 7. | Analysis notes on microcontroller resources, peripheral usage, hardware-software interface, basic software configuration (OS tasks, communication stack, memory services, diagnostics) and bus load; open points raised to the System Architect or Hardware Architect; resulting updates to interface requirement items. | SWE.1.RC.3, SWE.1.RC.4, SWE.1.RL.10 |
| SWE.1.BP5 | Develop verification criteria | Every requirement carries criteria that state, in qualitative and quantitative terms, how its fulfilment will be judged. The criteria show the requirement can be verified within the agreed constraints and are the starting point for software test cases and for any other verification measure. Requirements that cannot be verified by test are verified by other means (SUP.2). Outcomes 2, 7. | A verification-criteria attribute per item with measurable pass / fail conditions (values, tolerances, timing, preconditions); a verification-method attribute (test, analysis, review, inspection); list of items marked "not testable" with the alternative measure named. | VEC.RL.1, VEC.RL.2, PLS.RC.8, SWE.1.RL.7, SWE.1.RL.10 |
| SWE.1.BP6 | Establish bidirectional traceability | Software requirements are linked, navigable both ways, to system requirements and to system architecture elements. The two link sets are combined so that no redundant linking is needed. The links are what makes coverage, consistency and impact analysis possible. Outcome 6. | Link records on each software requirement pointing to system requirement and / or system architecture element IDs; a generated coverage report in both directions (system items allocated to software without child, software items without parent); a justification attribute on software requirements that legitimately have no parent. | TAC.RC.1, TAC.RC.2, TAC.RC.3, TAC.RC.4, TAC.RL.2, TAC.RL.3, SWE.1.RL.8, SWE.1.RL.9, SWE.1.RL.10, SWE.1.RC.9, SWE.1.RC.10 |
| SWE.1.BP7 | Ensure consistency | The content of the software requirements agrees with the system requirements and with the system architecture. Traceability supports this; review records demonstrate it. In a software-only project consistency and traceability are ensured against the stakeholder requirements instead. Outcome 6. | Review record of the software requirements against their system-level parents, with reviewers, reviewed version, findings and closure; a "suspect link" list raised after upstream changes and worked off; re-review entries after change requests. | TAC.RL.1, TAC.RL.4, TAC.RL.2, TAC.RL.3, SWE.1.RL.8, SWE.1.RL.9, SWE.1.RL.10, SWE.1.RL.11, SWE.1.RL.12 (see note below), CL2.RC.18; from the diagram: SWE.1.RC.11, SWE.1.RC.12 |
| SWE.1.BP8 | Communicate agreed software requirements | The agreed requirement set and each later update reach all parties that need them. Outcome 8. | Approved baseline (tag) of the specification; release note or notification naming the baseline and the recipients (Software Architect, Software Developers, Software Testers, System Requirements Engineer, Functional Safety Engineer, Customer where applicable); minutes or sign-off showing agreement; change notifications for updates. | SAC.RL.1, SAC.RC.4, SAC.RC.5, SAC.RC.6, TPS.RC.2, TPS.RC.3, SWE.1.RL.10, CL2.RC.9 |

Note on BP7 rule IDs: the per-practice ID list for BP7 gives the range `SWE.1.RL.8` to `SWE.1.RL.12`, while the rating-consistency diagram labels the corresponding BP7 dependencies `RC.11` and `RC.12` and shows no rule number above 10 anywhere. `SWE.1.RL.11` and `SWE.1.RL.12` are therefore kept but unconfirmed; they may stand for `SWE.1.RC.11` and `SWE.1.RC.12`. Check against the VDA guideline before relying on them.

## Output work products

| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 13-04 | Communication record | 8 | Proof that the agreed requirements and their updates were distributed: what version, to whom, when, and any agreement or objection that came back. |
| 13-19 | Review record | 6 | What was reviewed (items and version), against which parents and checklist, by whom, the findings, and how each finding was closed. |
| 13-21 | Change control record | 5, 7 | For each change to agreed requirements: the triggering request, the affected items, the assessed impact (cost, schedule, technical) and the decision. |
| 13-22 | Traceability record | 1, 6 | The link set between software requirements and system requirements / system architecture elements, readable in both directions, with coverage gaps visible. |
| 15-01 | Analysis report | 2, 3, 4, 7 | Results of analysing the requirements: correctness, feasibility and verifiability findings, effect on the operating environment, prioritisation rationale, cost / schedule / technical impact. |
| 17-08 | Interface requirements specification | 1, 3 | Requirements on the software's external interfaces: hardware-software interface, bus and diagnostic communication, data exchanged with other system elements, including types, ranges, timing and error behaviour. |
| 17-11 | Software requirements specification | 1 | The structured set of functional and non-functional software requirement items with their attributes. |
| 17-50 | Verification criteria | 2 | Per requirement, the measurable conditions under which it counts as fulfilled and the method by which that will be checked. |

## Dependencies

Reading convention: "A depends on B" means the rating of A is tied to the rating of B. "Rule" comes from a solid line in the rating-consistency diagram, "recommendation" from a dashed line. External targets are the PA 1.1 (process performance) rating of the named process, not a single practice.

| From | Depends on | Kind | ID on the diagram | Relationship shown |
|---|---|---|---|---|
| SWE.1.BP2 | SWE.1.BP1 | rule | SWE.1.RL.10 | structuring works on what BP1 specified |
| SWE.1.BP3 | SWE.1.BP1 | rule | SWE.1.RL.10 | analysis works on what BP1 specified |
| SWE.1.BP4 | SWE.1.BP1 | rule | SWE.1.RL.10 | environment impact is analysed for what BP1 specified |
| SWE.1.BP5 | SWE.1.BP1 | rule | SWE.1.RL.10 | verification criteria use what BP1 specified |
| SWE.1.BP6 | SWE.1.BP1 | rule | SWE.1.RL.10 | traceability has the BP1 output as one end |
| SWE.1.BP7 | SWE.1.BP1 | rule | SWE.1.RL.10 | consistency has the BP1 output as one end |
| SWE.1.BP8 | SWE.1.BP1 | rule | SWE.1.RL.10 | what is communicated is the BP1 output |
| SWE.1.BP1 | SYS.2 (PA 1.1) and SYS.3 (PA 1.1) | recommendation | SWE.1.RC.5, SWE.1.RC.6 | BP1 uses system requirements and system architecture; the diagram gives both IDs on one line to the SYS.2 / SYS.3 group and does not say which ID belongs to which process |
| SWE.1.BP6 | SYS.2 (PA 1.1) | recommendation | SWE.1.RC.9 | traceability to system requirements |
| SWE.1.BP6 | SYS.3 (PA 1.1) | recommendation | SWE.1.RC.10 | traceability to system architecture |
| SWE.1.BP7 | SYS.2 (PA 1.1) | recommendation | SWE.1.RC.11 | consistency with system requirements |
| SWE.1.BP7 | SYS.3 (PA 1.1) | recommendation | SWE.1.RC.12 | consistency with system architecture |

Additional observations from the diagram:
- BP1 is the hub: every other practice of the process depends on it through the single rule `SWE.1.RL.10`.
- The recommendation lines to SYS.2 / SYS.3 are drawn with arrowheads at both ends.
- BP6 and BP7 each have one more dashed line running to BP1 with no ID of its own (the other end of "establish between" / "ensure between"); the pair BP6 / BP7 to BP1 is already covered by the rule above.
- Cross-references in the practice notes: SPL.2.BP1 (release assignment, from BP2), MAN.3.BP5 (estimates, from BP3), SUP.2 (verification that is not test, from BP5).

## Automation notes

Assumed setting: requirements are structured text items in the repository (one item per block or file) with IDs, attributes and typed links; system-level items are available in the same form or as an export; baselines are tags; reviews are merge-request approvals or review record files.

Deterministic checks a script can do:
- Schema: every item has a unique, stable ID and the mandatory attributes with values from the allowed lists: type / category, status (for example draft, in review, agreed, rejected, obsolete), priority or target release, verification criteria (non-empty), verification method, safety classification, owner.
- Link integrity: no link to a missing, rejected or obsolete item; link types used only between the allowed levels.
- Coverage both ways: each software requirement links to at least one system requirement or system architecture element, or carries a filled "no parent" justification; each system requirement or architecture element allocated to software is linked from at least one software requirement. Report orphans in each direction and a coverage percentage.
- Suspect links: flag a link when the parent's content hash or last-changed commit is newer than the revision recorded when the link was last confirmed.
- Baseline gate: at a release tag every in-scope item has status "agreed"; a review record exists that names the reviewed revision, reviewers and findings, and no finding is open; a communication record (tag annotation, release note with recipients) exists for the tag.
- Change discipline: any diff touching an item with status "agreed" must reference a change request ID in the commit trailer, and an impact analysis record must exist for that ID.
- Release content: every item has a target release that exists in the release plan; produce the per-release requirement list.
- Lint heuristics: weak or unbounded words, "TBD / TBC", more than one "shall" in an item, numeric values without unit or tolerance, empty or copy-of-the-requirement verification criteria. These produce candidates, not verdicts.

Needs semantic judgement (LLM-assisted, human-confirmed):
- Does the software requirement really cover the intent of each linked parent (complete, partial, exceeding)? Are system requirements split across several children covered in sum?
- Is the item atomic, unambiguous, free of hidden design decisions and verifiable? Do the verification criteria actually define an observable pass / fail with quantities and conditions?
- Contradictions, duplicates and unstated interdependencies across the set.
- Plausibility of categorisation, and completeness of interface requirements against the hardware-software interface and communication descriptions.
- Whether the operating-environment analysis addresses the obvious consequences (resources, basic software configuration, other ECUs).
- Drafting support: proposing child requirements, verification criteria and impact-analysis text for a human to accept or reject.

Stays with a human:
- Agreement with stakeholders and the Customer, and resolving conflicts between them.
- Priority and release assignment decisions; accepting cost and schedule impact; feeding estimates into project planning.
- Feasibility judgement that depends on the real hardware, on supplier constraints or on experience with the product.
- Final sign-off of the baseline and accountability for review findings.
