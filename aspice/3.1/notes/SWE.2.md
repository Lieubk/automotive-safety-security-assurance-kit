# SWE.2 Software Architectural Design

## Intent

Define the structure of the software: which elements exist down to component level, what each one is responsible for, how they connect, how they behave over time and which resource limits they must respect. Every software requirement is assigned to the elements that realise it, the chosen structure is justified against explicit criteria, and the result is kept consistent and traceable to the requirements and agreed with those who build on it.

Scope marker: VDA scope, with rating-consistency guidance.

## Outcomes

1. An architecture for the software exists and names the elements the software is made of.
2. Each software requirement has been assigned to software elements.
3. For every software element the interfaces are specified.
4. Runtime behaviour of the elements and targets for their resource usage are specified.
5. Requirements and architecture are consistent with each other and linked in both directions.
6. The architecture has been agreed, and all affected parties know it.

## Base practices

| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SWE.2.BP1 | Develop software architectural design | A documented architecture identifies the software elements and addresses both the functional and the non-functional requirements. The software is broken down over as many hierarchy levels as make sense until software components are reached; components are the lowest architectural level and are refined only in the detailed design. Outcome 1. | Static view (layer and component diagram: application components, runtime environment, basic software modules, complex drivers) with a component list giving ID, responsibility, ASIL, origin (developed, reused, third-party, generated); AUTOSAR software component descriptions under version control; description of mechanisms that answer non-functional requirements (memory partitioning, monitoring, diagnostic concept, non-volatile memory strategy). | AGE.RC.5, AGE.RC.6, TPS.RC.4, TPS.RC.6, PLS.RC.2, SWE.2.RL.1, SWE.2.RL.2, SWE.2.RC.3 |
| SWE.2.BP2 | Allocate software requirements | Each software requirement is assigned to the architecture element or elements responsible for fulfilling it. Outcome 2. | Allocation link or attribute on every requirement naming component IDs; allocation matrix generated from the links; list of requirements without allocation is empty at baseline. | SWE.2.RL.3, SWE.2.RL.8 |
| SWE.2.BP3 | Define interfaces of software elements | Every element has its interfaces determined and fully described. Outcome 3. | Component interface table (port or function name, direction, data type, unit, range, resolution, initial and invalid value, update rate, provider, consumers); port interface definitions in the AUTOSAR description; C header / API description for non-AUTOSAR modules; conventions for error signalling and return codes. | TPS.RC.5, SWE.2.RL.4, SWE.2.RL.8 |
| SWE.2.BP4 | Describe dynamic behavior | Timing and runtime interplay of the elements are evaluated and documented so that the dynamic behaviour required at system level can be met. The description covers operating modes (start-up, shutdown, normal operation, calibration, diagnosis and similar) and the execution model: tasks or processes and how they communicate, time slices, interrupts. The evaluation takes the target platform and the load expected on it into account. Outcome 4. | Task and runnable mapping table (task, period, priority, preemption, execution order); sequence diagrams for the main signal chains and for start-up, shutdown, sleep and wake-up; mode / state machine description; interrupt list with priority and maximum duration; timing analysis (end-to-end latency budget, execution time estimates, CPU load or schedulability calculation); concept for protecting shared data. | SWE.2.RL.5, SWE.2.RL.8 |
| SWE.2.BP5 | Define resource consumption objectives | Targets for resource usage are set and documented for all relevant elements at a sensible hierarchy level. Typical resources: program and data memory (ROM, RAM, EEPROM or data flash) and CPU load. Outcome 4. | Resource budget table per component or partition (flash, RAM, stack per task, non-volatile memory, CPU share) with ECU totals and a reserve target; the same table later carrying measured values from map file and runtime measurement. | SWE.2.RL.6, SWE.2.RL.8 |
| SWE.2.BP6 | Evaluate alternative software architectures | Criteria for judging the architecture are defined, alternative designs are assessed against them, and the reason for the choice is recorded. Criteria can be quality attributes (such as modularity, maintainability, scalability, expandability, reliability, usability and how well security is realised) and the outcome of a make / buy / reuse analysis. Outcomes 1, 2, 3, 4, 5. | Architecture decision records, each with the question, the options considered, the criteria and their weighting, the assessment and the selected option with rationale; a trade study for major choices such as task model, partitioning or reuse of an existing platform. | SWE.2.RC.1, SWE.2.RL.8 |
| SWE.2.BP7 | Establish bidirectional traceability | Links between software requirements and architecture elements exist and can be followed both ways; they include the allocation from BP2. They enable coverage, consistency and impact analysis. Outcome 5. | Typed links in the requirements management tool or in the text files; generated report listing requirements without element and elements without requirement (the latter with a justification, for example infrastructure components). | TAC.RC.1, TAC.RC.2, TAC.RC.3, TAC.RC.4, TAC.RL.2, TAC.RL.3, SWE.2.RL.8, SWE.2.RL.9, SWE.2.RC.4 |
| SWE.2.BP8 | Ensure consistency | The architecture agrees in content with the software requirements. Traceability supports this; review records demonstrate it. Outcomes 1, 2, 5, 6. | Architecture review record with checklist, participants, reviewed version, findings and closure; re-review entries after requirement changes; automated comparison of the architecture description with the AUTOSAR model and the code interfaces. | TAC.RL.1, TAC.RC.4, TAC.RL.2, TAC.RL.3, SWE.2.RL.8, SWE.2.RC.5, CL2.RC.18 |
| SWE.2.BP9 | Communicate agreed software architectural design | The agreed architecture and each update of it reach all parties that need them. Outcome 6. | Approved baseline (tag) of the architecture; notification naming baseline and recipients (Software Developers, Software Integrator, Software Testers, System Architect, Functional Safety Engineer); minutes of the walkthrough in which it was agreed. | SAC.RL.1, SAC.RC.4, SAC.RC.5, SAC.RC.6, CL2.RC.9; from the diagram: SWE.2.RL.8 |

## Output work products

| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 04-04 | Software architectural design | 1, 2, 3, 4, 5 | Element hierarchy down to components with responsibilities, requirement allocation, interfaces, dynamic views (modes, tasks, sequences, timing), resource budgets, and the design decisions with their rationale. |
| 13-04 | Communication record | 6 | Proof that the agreed architecture and its updates were distributed: version, recipients, date, feedback. |
| 13-19 | Review record | 5 | Reviewed version, inputs and checklist used, reviewers, findings and their closure. |
| 13-22 | Traceability record | 5 | Requirement-to-element links readable in both directions, with coverage gaps visible. |
| 17-08 | Interface requirements specification | 3 | Definition of each interface between software elements and towards the outside: data, types, units, ranges, timing, error behaviour, provider and consumers. |

## Dependencies

Reading convention: "A depends on B" means the rating of A is tied to the rating of B. "Rule" comes from a solid line in the rating-consistency diagram, "recommendation" from a dashed line. External targets are the PA 1.1 (process performance) rating of the named process.

| From | Depends on | Kind | ID on the diagram | Relationship shown |
|---|---|---|---|---|
| SWE.2.BP2 | SWE.2.BP1 | rule | SWE.2.RL.8 | requirements are allocated to the elements BP1 defined |
| SWE.2.BP3 | SWE.2.BP1 | rule | SWE.2.RL.8 | interfaces build on the elements |
| SWE.2.BP4 | SWE.2.BP1 | rule | SWE.2.RL.8 | dynamic behaviour builds on the elements |
| SWE.2.BP5 | SWE.2.BP1 | rule | SWE.2.RL.8 | resource objectives build on the elements |
| SWE.2.BP6 | SWE.2.BP1 | rule | SWE.2.RL.8 | the architecture is evaluated against the defined criteria |
| SWE.2.BP7 | SWE.2.BP1 | rule | SWE.2.RL.8 | traceability has the elements as one end |
| SWE.2.BP8 | SWE.2.BP1 | rule | SWE.2.RL.8 | consistency has the architecture as one end |
| SWE.2.BP9 | SWE.2.BP1 | rule | SWE.2.RL.8 | what is communicated is the architecture |
| SWE.2.BP7 | SWE.2.BP2 | rule | SWE.2.RL.9 | traceability and allocation are related to each other |
| SWE.2.BP1 | SWE.1 (PA 1.1) | recommendation | SWE.2.RC.3 | the architecture is developed with respect to the software requirements |
| SWE.2.BP7 | SWE.1 (PA 1.1) | recommendation | SWE.2.RC.4 | traceability to the software requirements |
| SWE.2.BP8 | SWE.1 (PA 1.1) | recommendation | SWE.2.RC.5 | consistency with the software requirements |

Additional observations from the diagram:
- BP1 is the hub: all eight other practices depend on it through `SWE.2.RL.8`.
- The lines for RC.3 and RC.4 carry arrowheads at both ends; the RC.5 line points only towards SWE.1.

## Automation notes

Assumed setting: the architecture is kept as structured text (component descriptions, interface tables, diagrams as text, decision records) next to the AUTOSAR descriptions and the C code; requirements carry allocation links; baselines are tags.

Deterministic checks a script can do:
- Structure: every architecture element has a unique ID, a parent (well-formed tree whose leaves are components), a responsibility text, a safety classification and an origin attribute.
- Allocation and traceability both ways: each agreed software requirement is linked to at least one element; each component is linked from at least one requirement or carries a justification; links never point at missing or obsolete items. Report orphans and coverage percentage.
- Interface completeness: every interface entry has name, direction, data type, unit, range, resolution, initial value, provider and at least one consumer; no provided interface without consumer and no required interface without provider; data type and unit agree on both ends of a connection.
- Model and code agreement: port and interface names, types and connections in the architecture text equal those in the AUTOSAR description; exported C declarations in public headers equal the documented interface (parse headers); include / call dependencies extracted from the code stay within the dependencies the architecture allows (layer and partition rules).
- Dynamic view presence: every runnable or entry function is mapped to a task or interrupt; every task has period, priority and a stack budget; each operating mode named in the requirements has a behavioural description file or section.
- Resource budgets: every component has budget entries; sums stay within the ECU limits minus the reserve target; compare budgets with sizes parsed from the linker map file and with stack / CPU load figures from measurement reports, and flag overruns.
- Decision records: required sections present (question, options, criteria, assessment, decision, rationale); each record referenced from the architecture.
- Gates: review record exists for the baseline revision with no open finding; suspect flags raised when a linked requirement changed after the link was confirmed; a communication record exists for each architecture tag.

Needs semantic judgement (LLM-assisted, human-confirmed):
- Is each requirement allocated to the right component, and can the allocated components together really fulfil it?
- Is the decomposition sound (clear responsibilities, cohesion, limited coupling), and does it actually answer the non-functional requirements?
- Are interface semantics described well enough to implement and to integrate against (meaning of values, validity, timing, error cases)?
- Is the dynamic description complete for start-up, shutdown, degraded and diagnostic modes, and do diagrams and prose say the same thing?
- Are the alternatives in a decision record genuine options, and does the stated rationale follow from the criteria?
- Is the timing or resource analysis plausible given the stated assumptions?

Stays with a human or with the target:
- The architectural decisions and trade-offs themselves, including partitioning for safety and security.
- Measured execution times, CPU load, stack and memory usage on the target hardware; a script can only compare reported numbers.
- Agreement with system, safety, test and integration stakeholders, and sign-off of the baseline.
