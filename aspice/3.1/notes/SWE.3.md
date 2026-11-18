# SWE.3 Software Detailed Design and Unit Construction

## Intent

For every software component, produce a detailed design that defines the software units, their interfaces and, where it matters, their dynamic behaviour; judge that design against quality aspects; then implement the units as designed. Requirements, architecture, detailed design and code are kept mutually consistent and traceable, and the design is agreed with those who implement, verify and integrate.

Scope marker: VDA scope, with rating-consistency guidance.

## Outcomes

1. A detailed design exists in which the software units are described.
2. Every software unit has its interfaces specified.
3. How the software units behave at runtime is specified.
4. Consistency and two-way traceability hold along three relations: software requirements to units, architecture to detailed design, and detailed design to units.
5. The detailed design, and how it relates to the architecture, has been agreed and made known to all affected parties.
6. The units described by the detailed design have been built.

## Base practices

| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SWE.3.BP1 | Develop software detailed design | Each component named in the architecture has a detailed design, and that design specifies all of the component's units with regard to functional and non-functional requirements. Outcome 1. | Per-component design file listing the units (ID, purpose, source files) and describing algorithms, state machines, data structures, calibration parameters and error handling; for model-based units the model plus an explanatory description; enough detail that the unit can be coded and unit tests derived without guessing. | APA.RL.2, SWE.3.RL.1, SWE.3.RL.2, SWE.3.RC.2, SWE.3.RC.3 |
| SWE.3.BP2 | Define interfaces of software units | Every unit has its interfaces determined, specified and written down. Outcome 2. | Function prototypes with description of each parameter and return value (type, unit, range, resolution); definitions of shared data with access rules; pre- and postconditions; header files with structured comments that match the design. | SWE.3.RL.3, SWE.3.RL.7 |
| SWE.3.BP3 | Describe dynamic behavior | The runtime behaviour of the relevant units and the way they interact are evaluated and documented. Units without behaviour worth describing may be left out. Outcome 3. | State charts, sequence or activity diagrams, call graph; statement of call context (task, interrupt), re-entrancy and protection of shared data; explicit "not applicable" mark with reason for stateless units. | SWE.3.RL.4, SWE.3.RL.7 |
| SWE.3.BP4 | Evaluate software detailed design | The design is assessed against six aspects: interaction, interoperability, criticality, technical complexity, testability and risks. The result can steer how units are verified. Outcomes 1, 2, 3, 4. | Design evaluation record or checklist addressing those six aspects; complexity metrics (cyclomatic complexity, nesting depth, fan-in / fan-out) against agreed limits; criticality classification per unit used to set verification depth; list of risks and testability problems with actions. | SWE.3.RL.5, SWE.3.RC.1, SWE.3.RL.7 |
| SWE.3.BP5 | Establish bidirectional traceability | Links exist, navigable both ways, for three relations: software requirements to units, architecture to detailed design, detailed design to units. The relations are combined so that no redundant linking is needed. Outcome 4. | Trace references in design elements to component and requirement IDs; trace tags in source file or function comments pointing to design element IDs; generated trace matrix with coverage in both directions. | TAC.RC.1, TAC.RC.2, TAC.RC.3, TAC.RC.4, TAC.RL.2, TAC.RL.3, SWE.3.RL.7, SWE.3.RC.4, SWE.3.RC.5 |
| SWE.3.BP6 | Ensure consistency | Units agree in content with the software requirements; architecture, detailed design and units agree with each other. Traceability supports this; review records demonstrate it. Outcome 4. | Design review record (design against architecture and requirements) and code review record (code against design), each with reviewed revision, findings and closure; automated report comparing designed and implemented function signatures. | TAC.RL.1, TAC.RC.4, TAC.RL.2, TAC.RL.3, MBD.RL.6, SWE.3.RL.7, SWE.3.RC.6, SWE.3.RC.7, CL2.RC.18 |
| SWE.3.BP7 | Communicate agreed software detailed design | The agreed detailed design and each update of it reach all parties that need them. Outcome 5. | Baselined design (tag); notification to Software Developers, Verification Engineers, Software Testers and the Software Integrator; minutes of the design review in which it was agreed. | SAC.RL.1, SAC.RC.4, SAC.RC.5, SAC.RC.6, SWE.3.RL.7, CL2.RC.9 |
| SWE.3.BP8 | Develop software units | The executable form of every unit (source code, or model with generated code) is produced and documented in line with the detailed design. Outcome 6. | C source and header files under version control that build without warnings using the project compiler settings and follow the coding guidelines; for generated code the generator version and configuration; commits linked to the work item or change request that caused them. | SWE.3.RL.6, SWE.3.RL.7 |

## Output work products

| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 04-05 | Software detailed design | 1, 2, 3 | Per component: the units, what each does and how (algorithms, data, states), unit interfaces, dynamic behaviour where relevant, and the references to architecture and requirements. |
| 11-05 | Software unit | 6 | The implemented unit: source and header files or model plus generated code, identifiable by version and attributable to a design element. |
| 13-04 | Communication record | 5 | Proof that the agreed detailed design and its updates were distributed: version, recipients, date, feedback. |
| 13-19 | Review record | 4 | Reviewed revision of design or code, what it was checked against, reviewers, findings and their closure. |
| 13-22 | Traceability record | 4 | Links requirement to unit, architecture element to design element, design element to code, readable in both directions with gaps visible. |

## Dependencies

Reading convention: "A depends on B" means the rating of A is tied to the rating of B. "Rule" comes from a solid line in the rating-consistency diagram, "recommendation" from a dashed line. External targets are the PA 1.1 (process performance) rating of the named process.

| From | Depends on | Kind | ID on the diagram | Relationship shown |
|---|---|---|---|---|
| SWE.3.BP2 | SWE.3.BP1 | rule | SWE.3.RL.7 | unit interfaces build on the detailed design |
| SWE.3.BP3 | SWE.3.BP1 | rule | SWE.3.RL.7 | dynamic behaviour builds on the detailed design |
| SWE.3.BP4 | SWE.3.BP1 | rule | SWE.3.RL.7 | the evaluation is of the detailed design |
| SWE.3.BP5 | SWE.3.BP1 | rule | SWE.3.RL.7 | traceability has the detailed design as one end |
| SWE.3.BP6 | SWE.3.BP1 | rule | SWE.3.RL.7 | consistency has the detailed design as one end |
| SWE.3.BP7 | SWE.3.BP1 | rule | SWE.3.RL.7 | what is communicated is the detailed design |
| SWE.3.BP8 | SWE.3.BP1 | rule | SWE.3.RL.7 | units are developed according to the detailed design |
| SWE.3.BP1 | SWE.1 (PA 1.1) and SWE.2 (PA 1.1) | recommendation | SWE.3.RC.2, SWE.3.RC.3 | the detailed design is based on software requirements and architecture; both IDs sit on one line to the SWE.1 / SWE.2 group, with no split shown |
| SWE.3.BP5 | SWE.1 (PA 1.1) | recommendation | SWE.3.RC.4 | traceability to software requirements |
| SWE.3.BP5 | SWE.2 (PA 1.1) | recommendation | SWE.3.RC.5 | traceability to the architecture |
| SWE.3.BP6 | SWE.1 (PA 1.1) | recommendation | SWE.3.RC.6 | consistency with software requirements |
| SWE.3.BP6 | SWE.2 (PA 1.1) | recommendation | SWE.3.RC.7 | consistency with the architecture |

Additional observations from the diagram:
- BP1 is the hub: all seven other practices depend on it through `SWE.3.RL.7`.
- BP5 and BP6 each have one more dashed line to BP1 that is explicitly marked as having no recommendation ID; the pair is already covered by the rule above.
- The recommendation lines to SWE.1 / SWE.2 are drawn with arrowheads at both ends.

## Automation notes

Assumed setting: detailed design is structured text per component with unit entries that carry IDs and links; code is C with trace tags in comments; headers carry structured documentation comments; baselines are tags; reviews are merge-request approvals or review record files.

Deterministic checks a script can do:
- Completeness: every component of the architecture has a detailed design file; every unit entry has ID, purpose, interface section, and a dynamic-behaviour section or an explicit "not applicable" with reason.
- Design-to-code mapping both ways: each unit entry names source files that exist; each source file in the build belongs to exactly one declared unit; no file or exported function without a design element; no design element without code at baseline.
- Signature agreement: function names, parameter lists, types and return types documented in the design equal those parsed from headers and sources (compiler front end or tag generator); documented global data matches declarations.
- Trace coverage both ways for all three relations: requirement to unit, architecture element to design element, design element to code. Report orphans and percentages; flag suspect links when the upstream item changed after the link was confirmed.
- Metrics against thresholds from the design evaluation criteria: cyclomatic complexity, function length, nesting depth, number of parameters, fan-out; list units exceeding limits without a recorded justification.
- Build hygiene: project compiles with the agreed warning level and zero warnings; no unresolved "TODO / FIXME" markers in baselined units; generated code matches a re-run of the generator with the recorded configuration.
- Records: design evaluation record exists per component and has an entry for each of the six evaluation aspects; design and code review records exist for the baselined revision with no open finding; a communication record exists per design tag.
- Change discipline: a commit that changes a unit's interface without changing its design entry (or the reverse) is flagged.

Needs semantic judgement (LLM-assisted, human-confirmed):
- Does the code do what the design says (algorithm, state transitions, error handling, boundary behaviour), and is nothing implemented that the design does not mention?
- Is the design detailed enough to implement and to derive unit tests from, or does it merely restate the requirement?
- Does the design element really satisfy the requirements and the component responsibility it is linked to?
- Is the described dynamic behaviour (call context, re-entrancy, shared data) consistent with what the code and the task mapping show?
- Is the design evaluation substantive: are criticality and testability conclusions supported by the design?
- Do comments and documentation still match the behaviour after a change?

Stays with a human:
- Design decisions, criticality classification and acceptance of metric overruns or guideline deviations.
- Adequacy of safety mechanisms and defensive measures inside units.
- Review accountability and sign-off of the agreed design.
