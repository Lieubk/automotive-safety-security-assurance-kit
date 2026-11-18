# SYS.3 System Architectural Design

## Intent

Define how the system is built up: which elements it consists of, which system requirement lands on which element, how the elements connect and how they interact over time. The design is judged against explicit criteria, including a comparison of alternatives, stays consistent with and traceable to the system requirements, and is agreed with and distributed to the disciplines that implement it.

Scope note: SYS.3 is in the VDA scope; rating rules, recommendations and a rating-consistency diagram are published for it.

## Outcomes

1. A system architectural design exists that names the elements the system is made of.
2. Each system requirement is assigned to system elements.
3. For every system element the interfaces are specified.
4. How the system elements behave dynamically is specified.
5. System requirements and the architectural design agree in content and are linked in both directions.
6. The architectural design is agreed and has been made known to every affected party.

## Base practices

| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SYS.3.BP1 | Develop system architectural design | A documented architecture identifies the system's elements and shows how they answer both the functional and the non-functional system requirements. Outcome 1. | Architecture description with uniquely identified elements over one or more hierarchy levels (structure views, element responsibilities) | SYS.3.RL.1, SYS.3.RL.2, SYS.3.RC.2 |
| SYS.3.BP2 | Allocate system requirements | Every system requirement is assigned to the architecture element or elements that have to fulfil it. Outcome 2. | Allocation attribute or link per requirement; list of requirements per element | SYS.3.RL.3, SYS.3.RL.7 |
| SYS.3.BP3 | Define interfaces of system elements | For each element, its interfaces are identified, worked out and written down. Outcome 3. | Interface definitions with both end points and the exchanged signals, energy or media, including electrical, timing and protocol properties | SYS.3.RL.4, SYS.3.RL.7 |
| SYS.3.BP4 | Describe dynamic behavior | How the elements interact over time has been evaluated and is documented. Outcome 4. | Sequence, state or timing descriptions per operating mode; mode transition descriptions | SYS.3.RL.5, SYS.3.RL.7 |
| SYS.3.BP5 | Evaluate alternative system architectures | Evaluation criteria for the architecture are defined, alternative designs have been compared against them, and the reasons for the selected design are on record. Outcome 1. | Decision record listing criteria, alternatives considered, assessment per alternative and rationale for the choice | SYS.3.RL.6, SYS.3.RL.7, SYS.3.RC.1 |
| SYS.3.BP6 | Establish bidirectional traceability | System requirements and architecture elements are linked so the relation can be followed from either side. Outcome 5. | Link data or trace matrix between requirements and elements; coverage figures in both directions | TAC.RC.1, TAC.RC.2, TAC.RC.3, TAC.RC.4, TAC.RL.2, TAC.RL.3, SYS.3.RL.7, SYS.3.RL.8, SYS.3.RC.3 |
| SYS.3.BP7 | Ensure consistency | The content of the architecture has been checked against the system requirements: the design neither contradicts nor omits what is required. Outcomes 1, 2, 5, 6. | Review record of the architecture against the requirements; findings and their closure | TAC.RL.1, TAC.RC.4, TAC.RL.2, TAC.RL.3, SYS.3.RL.7, SYS.3.RC.4, CL2.RC.18 |
| SYS.3.BP8 | Communicate agreed system architectural design | The agreed design, and each later update of it, reaches all parties who need it. Outcome 6. | Release note or notification per architecture baseline; distribution list; acknowledgement from hardware, software, mechanics and test | SAC.RL.1, SAC.RC.4, SAC.RC.5, SAC.RC.6, SYS.3.RL.7, CL2.RC.9 |

Practice notes:

- Developing the architecture normally means breaking the system down into elements over as many hierarchy levels as the product needs (BP1).
- Operating modes drive dynamic behaviour: typical ones are start-up, shutdown, normal operation, calibration and diagnosis (BP4).
- Evaluation criteria can be quality characteristics (for example reliability, maintainability, modularity, scalability, room for extension, usability and the way security is realised) and the outcome of a make-buy-reuse analysis (BP5).
- The trace links of BP6 include the allocation made under BP2; they are also what enables coverage checks, consistency checks and impact analysis.
- Consistency builds on those links and is typically evidenced by review records (BP7).
- System requirements usually contain requirements on the architecture itself; these connect BP7 to the evaluation under BP5.

The rule (RL) and recommendation (RC) IDs above are identifiers from the VDA rating guideline; only the IDs are recorded here, not their wording. IDs whose prefix is not the process ID (TAC, SAC, CL2) belong to parts of that guideline that are not specific to this process.

## Output work products

| WP ID | Official name | Outcomes | What it should contain |
|---|---|---|---|
| 04-06 | System architectural design | 1, 2, 3, 4, 5 | Element structure, responsibility of each element, requirement allocation, interfaces, dynamic behaviour per operating mode, and the rationale for the chosen design |
| 13-04 | Communication record | 6 | Proof that each agreed architecture baseline and each update was sent to the affected parties: what, to whom, when |
| 13-19 | Review record | 5 | Scope reviewed (which architecture and requirement versions), reviewers, consistency findings, decisions and closure |
| 13-22 | Traceability record | 5 | The links between system requirements and architecture elements, navigable in both directions, with coverage status |
| 17-08 | Interface requirements specification | 3 | Requirements on each interface between system elements: partners, exchanged items, value ranges, timing and protocol properties |

## Dependencies

Taken from the rating-consistency diagram for SYS.3. "Rule" means the line is drawn solid, "recommendation" means it is drawn dashed. "One-way" means the rating of the practice in the first column depends on the second column. "Two-way" means the line carries an arrowhead at both ends, which indicates that the two ratings depend on each other.

| Rating of | Depends on | Kind | ID on the line | Arrow | Relation shown |
|---|---|---|---|---|---|
| SYS.3.BP2 | SYS.3.BP1 | rule | SYS.3.RL.7 | one-way | allocates to |
| SYS.3.BP3 | SYS.3.BP1 | rule | SYS.3.RL.7 | one-way | based on |
| SYS.3.BP4 | SYS.3.BP1 | rule | SYS.3.RL.7 | one-way | based on |
| SYS.3.BP5 | SYS.3.BP1 | rule | SYS.3.RL.7 | one-way | according to defined criteria |
| SYS.3.BP6 | SYS.3.BP1 | rule | SYS.3.RL.7 | one-way | (no text) |
| SYS.3.BP7 | SYS.3.BP1 | rule | SYS.3.RL.7 | one-way | (no text) |
| SYS.3.BP8 | SYS.3.BP1 | rule | SYS.3.RL.7 | one-way | communicate |
| SYS.3.BP6 | SYS.3.BP2 | rule (solid line) | none printed | one-way | related to each other |
| SYS.3.BP1 | SYS.2 (PA 1.1) | recommendation | SYS.3.RC.2 | two-way | with respect to |
| SYS.3.BP6 | SYS.2 (PA 1.1) | recommendation | SYS.3.RC.3 | two-way | establish between |
| SYS.3.BP7 | SYS.2 (PA 1.1) | recommendation | SYS.3.RC.4 | two-way | ensure between |

Reading it:

- BP1 is the anchor: the rating of every other base practice of the process depends on it by rule.
- Traceability (BP6) and allocation (BP2) are tied together by a solid line that carries no ID. SYS.3.RL.8 is listed for BP6 but is not printed on any line of the diagram; whether it is the rule behind that line cannot be told from the diagram alone.
- The quality of system requirements analysis (SYS.2) should show in the ratings of BP1, BP6 and BP7.

## Automation notes

Assumed setting: the architecture is kept as structured text (element and interface definitions with IDs, diagrams as text-based models) next to the requirements in a git repository; baselines are tags.

Deterministic checks a script can run:

- Schema: every element has a unique ID, a kind (for example hardware, software, mechanical), a parent and a stated responsibility; every interface has an ID, two existing end points and a non-empty data definition (name, direction, unit, range, timing).
- Allocation coverage: every agreed system requirement is allocated to at least one element; every leaf element has at least one requirement or a recorded reason for having none.
- Trace hygiene: no link points at a missing or superseded item; a requirement changed after its allocation was last confirmed marks the link as suspect.
- Interface symmetry: what one element declares as output is declared as input by its partner, with matching type, unit and range.
- Dynamic behaviour: for each operating mode named in the architecture there is at least one behaviour description file, and it references only existing elements and interfaces.
- An architecture decision record exists, names evaluation criteria, at least two alternatives and a rationale.
- Each baseline tag has a review record whose scope covers the tagged commit, and a notification with a non-empty distribution list.

Checks that need semantic judgement (LLM-assisted, human-confirmed):

- Whether a requirement's content actually fits the responsibility of the element it is allocated to, and whether non-functional requirements (timing, safety, security, resource limits) are visibly addressed by the design.
- Whether the behaviour descriptions cover the modes and transitions the requirements imply, including error and degraded modes.
- Whether the recorded rationale is a real comparison or a justification after the fact.
- Contradictions between architecture statements and requirement text; drafting review findings.

What stays with humans (System Architect, Hardware Architect, Mechanical Engineer, Functional Safety Engineer, Cybersecurity Engineer):

- The architectural decisions and trade-offs themselves, including make-buy-reuse and hardware or mechanical feasibility.
- Decomposition decisions that carry safety or cybersecurity weight.
- Agreement and approval of the design across disciplines, and the decision that a review finding is closed.
