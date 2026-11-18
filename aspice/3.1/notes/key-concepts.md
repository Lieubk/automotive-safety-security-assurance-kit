# Automotive SPICE 3.1 key concepts

This note covers the structure of the model and the cross-process ideas that every
engineering, management and support process relies on. Individual processes and the
capability-level practices are described in their own notes.

## 1. What the model is for

Automotive SPICE is a framework for evaluating and improving the development processes
behind mechatronic products. It prescribes what a process has to achieve, not how the work
is organized, so it can be applied to plan-driven and to agile development alike, and it
supports products with safety or security relevance.

Typical uses:

- A Customer rates the process-related risk of a Supplier.
- An organization rates its own development risks and capabilities.
- Projects or organizational units are benchmarked for strengths and improvement potential.
- The effect of a process change is evaluated.
- Responsibilities inside the development are made explicit and trackable.

Improvement itself follows a plan-do-check-act loop in which every gain is consolidated
into the standard way of working: set the goal and analyse the current state, define the
process interfaces and work out the solution together with the people who do the work,
pilot it step by step and correct process and templates, then train and roll out.

## 2. The two dimensions

Capability is determined on a two-dimensional grid.

| Dimension | Contains |
|---|---|
| Process dimension | Domain and scope of the model; the processes, each defined by a purpose and a numbered list of outcomes |
| Capability dimension | Capability levels, process attributes, the rating scale, the rating method, the aggregation method and the rule that turns attribute ratings into a level |

A rating is always made per process: one process, rated against the process attributes of
the levels in scope.

Capability levels and their process attributes:

| Level | Name | Process attributes | Short meaning |
|---|---|---|---|
| 0 | Incomplete | none | Results are missing or not adequate |
| 1 | Performed | PA 1.1 Process performance | The outcomes of the process are achieved |
| 2 | Managed | PA 2.1 Performance management, PA 2.2 Work product management | Execution is planned, monitored and adjusted; it is clear who is responsible; results are checked for quality and kept under control |
| 3 | Established | PA 3.1 Process definition, PA 3.2 Process deployment | The project works from organization-wide standard processes, and the organization learns by improving those standards |
| 4 | Predictable | PA 4.1 Quantitative analysis, PA 4.2 Quantitative control | Process performance is measured and analysed statistically so that decisions rest on data |
| 5 | Innovating | PA 5.1 Process innovation, PA 5.2 Process innovation implementation | Improvement is driven by organization-wide quantitative feedback and causal analysis |

Practitioner experience attached to this scale: level 3 is regarded as the first stable
level. A level below 3 tends to drift, upward or downward, within roughly a year and a half.

## 3. Anatomy of a process description

Every process is described with the same four elements. Each element answers one question
when the model is used for improvement and a different one when it is used in an assessment.

| Element | Improvement view | Assessment view |
|---|---|---|
| Purpose | What is this process good for? | How far is the purpose achieved? |
| Outcomes | What results should appear? | Is there enough evidence that the results exist? |
| Output work products | Which artefacts typically carry the results? | Do the work products hold complete information? |
| Base practices | Which activities lead to the purpose? | How effectively are these activities carried out? |

Base practices and output work products are indicators. They point to outcome achievement;
they are not a mandatory activity list or document list.

## 4. Process groups and scope

### 4.1 Processes in the model

| Category | Group | Processes |
|---|---|---|
| Primary life cycle | ACQ Acquisition | ACQ.3 Contract Agreement, ACQ.4 Supplier Monitoring, ACQ.11 Technical Requirements, ACQ.12 Legal and Administrative Requirements, ACQ.13 Project Requirements, ACQ.14 Request for Proposals, ACQ.15 Supplier Qualification |
| Primary life cycle | SPL Supply | SPL.1 Supplier Tendering, SPL.2 Product Release |
| Primary life cycle | SYS System Engineering | SYS.1 Requirements Elicitation, SYS.2 System Requirements Analysis, SYS.3 System Architectural Design, SYS.4 System Integration and Integration Test, SYS.5 System Qualification Test |
| Primary life cycle | SWE Software Engineering | SWE.1 Software Requirements Analysis, SWE.2 Software Architectural Design, SWE.3 Software Detailed Design and Unit Construction, SWE.4 Software Unit Verification, SWE.5 Software Integration and Integration Test, SWE.6 Software Qualification Test |
| Supporting life cycle | SUP Supporting | SUP.1 Quality Assurance, SUP.2 Verification, SUP.4 Joint Review, SUP.7 Documentation, SUP.8 Configuration Management, SUP.9 Problem Resolution Management, SUP.10 Change Request Management |
| Organizational life cycle | MAN Management | MAN.3 Project Management, MAN.5 Risk Management, MAN.6 Measurement |
| Organizational life cycle | REU Reuse | REU.2 Reuse Program Management |
| Organizational life cycle | PIM Process Improvement | PIM.3 Process Improvement |

### 4.2 VDA scope and extended scope

| Scope class | Processes | Count |
|---|---|---|
| VDA scope (the basic process set) | MAN.3, ACQ.4, SUP.1, SUP.8, SUP.9, SUP.10, SYS.2, SYS.3, SYS.4, SYS.5, SWE.1, SWE.2, SWE.3, SWE.4, SWE.5, SWE.6 | 16 |
| Extended VDA scope | MAN.5, SUP.2, SUP.4, SUP.7, SPL.2, SYS.1 | 6 |
| Other (in the model, outside both sets) | REU.2, MAN.6, PIM.3, ACQ.3, ACQ.11, ACQ.12, ACQ.13, ACQ.14, ACQ.15, SPL.1 | 10 |

Rating-consistency guidance (rules and recommendations with IDs, plus dependency diagrams)
is available for the 16 VDA-scope processes and for the process attributes of levels 2 and
3. None is recorded for the extended-scope processes.

### 4.3 Process sets for organizational maturity

Besides rating single processes in a project, a whole organization can be rated across
several process instances. The result is an organizational maturity level derived from
capability levels, using the staging scheme of ISO/IEC 15504-7. The process sets are:

| Set | Processes |
|---|---|
| Basic set | The VDA scope (see above) |
| Extended set, level 2 | SYS.1, MAN.5, MAN.6, ACQ.3, SUP.4, SPL.2 |
| Extended set, level 3 | ORG.1 Process Establishment, ORG.4 Skill development, PIM.3 Process Improvement, REU.2 Reuse Program Management (recommended) |
| Extended set, upper levels | For level 4: QNT.1 Quantitative Performance Management. For level 5: QNT.2 Quantitative Process Improvement |

Reading of the staging: maturity level 1 needs the basic set at capability level 1;
maturity level 2 needs the basic set plus the level-2 set at capability level 2; maturity
level 3 needs those plus the level-3 set at capability level 3; for maturity levels 4 and 5
only selected processes have to reach capability level 4 or 5. Note that the level-2 set
here is not the same list as the extended VDA scope in 4.2.

## 5. The plug-in concept

The model is built as nested V-shapes. The system level is always present; below it,
domain-specific engineering models are plugged in. Software is part of the core model;
hardware and mechanical engineering come from separately published add-on models that
follow the same structure.

| Level | System | Software (core model) | Hardware (add-on model) | Mechanical (add-on model) |
|---|---|---|---|---|
| System | SYS.1 to SYS.5 | | | |
| Domain / sub-system | | SWE.1, SWE.2 (left) and SWE.5, SWE.6 (right) | HWE.1, HWE.2 (left) and HWE.3, HWE.4 (right) | MSE.1, MSE.2 (left) and MSE.3, MSE.4 (right) |
| Component / unit | | SWE.3 (left) and SWE.4 (right) | | MCE.1, MCE.2 (left), MCE.3 (bottom, unit level), MCE.4, MCE.5 (right) |

HWE = Hardware Engineering, MSE = Mechanical System Engineering, MCE = Mechanical Component
Engineering.

Management, reuse, acquisition and supporting processes (MAN.3, MAN.5, REU.2, ACQ.4, SUP.1,
SUP.4, SUP.7, SUP.8, SUP.9, SUP.10) are not tied to one level. They span the system level and
every plugged-in domain.

Consequence for a toolkit: the system-level artefacts (system requirements, system
architecture) are the docking points. Every domain V takes its input from them and returns
integrated, tested items to system integration.

## 6. Four working principles

1. Qualified input, qualified output. Each contributor works from input that has been
   checked and hands over output that has been checked. Practical hints: cut work into
   small tasks (for example below 40 hours), finish tasks one after another, review and
   approve work products continuously instead of at the end, and use explicit criteria and
   lean methods for that check.
2. Agree and summarize. In engineering processes, requirements and designs are agreed, and
   the results of each verification step are summarized. In management and support
   processes, strategies, plans and schedules are agreed, and results are summarized and
   reported to the parties that need them.
3. Divide and control. At every level (system, domain, sub-domain, component) the same
   pattern repeats: specify and design the solution; hand the parts down to the next level
   or, at unit level, implement them; integrate the parts and verify the integration against
   the design; only then qualify the result against the specification.
4. Traceability. Every item - requirement, design element, implementation, test case, test
   result, finding, scheduled activity - refers to where it came from and to how it is
   verified. The links are used for three things: checking consistency, analysing the
   impact of a change, and showing completeness.

## 7. Qualification test versus integration test

Processes on the same height of the V have a similar purpose and differ only in level of
detail. On the left side, a requirements process states the problem and a design process
states the planned solution (structural elements, interfaces, dynamic behaviour). On the
right side there are two kinds of test, and each has exactly one reference on the left:

- Integration test checks the integrated object against the design of the same level
  (interfaces and dynamic behaviour).
- Qualification test checks the object against the requirements specification of the same
  level.

| Level | Requirements (problem) | Design (solution) | Integration and integration test, against the design | Qualification test, against the requirements |
|---|---|---|---|---|
| System | SYS.2 | SYS.3 | SYS.4 | SYS.5 |
| Domain: software | SWE.1 | SWE.2 | SWE.5 | SWE.6 |
| Domain: hardware | HWE.1 | HWE.2 | HWE.3 | HWE.4 |
| Domain: mechanical | MSE.1 | MSE.2 | MSE.3 | MSE.4 |
| Software component and unit | SWE.3 | SWE.3 | SWE.4 | SWE.4 |

Software component and unit level in more detail (an interpretation aid, since version 3.1
folds both levels into SWE.3 and SWE.4):

| Content | Covered by |
|---|---|
| Component-level specification, detailed design and unit-level specification | SWE.3.BP1 |
| Detailed design (interfaces, dynamic behaviour, evaluation, communication) | SWE.3.BP2, SWE.3.BP3, SWE.3.BP4, SWE.3.BP7 |
| Links between component specification, detailed design, unit specification and implementation | SWE.3.BP5, SWE.3.BP6 |
| Implementation of the units | SWE.3.BP8 |
| Check of the component against the detailed design | expressed through SWE.4.BP2 in version 3.1 |
| Verification of the unit against its specification | SWE.4.BP1 to SWE.4.BP7 |

Consequence for test design: integration test cases are derived from the design of their
level (its interfaces and dynamic behaviour), qualification test cases from the
requirements of their level. The two test kinds are not interchangeable.

## 8. Bidirectional traceability and consistency

### 8.1 Two different obligations

| | Bidirectional traceability | Consistency |
|---|---|---|
| What it is | Explicit links between related items that can be followed in both directions | Agreement in content and meaning between the linked items |
| Question answered | Is every item connected to its source and to its verification? What is affected if this item changes? | Does the lower-level item really implement, refine or verify the upper-level item, without contradiction or gap? |
| Typical evidence | Link data in the requirements management tool or ALM tool, trace matrices, coverage reports | Review records that show the linked content was compared and found in agreement |
| Nature of the check | Structural, can be computed | Semantic, needs judgement; a script can only confirm that a review record exists |
| Relation | Enables coverage, consistency and impact analysis | Is supported by traceability but not proven by it |

A complete link set with wrong content is traceable but not consistent. A reviewed,
correct document set without links may be consistent today but is not traceable, and its
consistency cannot be maintained under change.

Each engineering process owns two separate base practices for this: one
`Establish bidirectional traceability` practice and one `Ensure consistency` practice.
The second covers fewer artefact pairs than the first (see the table).

### 8.2 Link pairs across the V

`Left artifact` is the upstream or reference side, `Right artifact` the derived or verifying
side. All links are bidirectional. `-` means the model defines no consistency practice for
that pair.

| Link | Left artifact | Right artifact | Traceability BP | Consistency BP | Kind |
|---|---|---|---|---|---|
| L01 | Stakeholder requirements | System requirements | SYS.2.BP6 | SYS.2.BP7 | Refinement |
| L02 | System requirements | System architecture (its elements) | SYS.3.BP6 | SYS.3.BP7 | Refinement |
| L03 | System requirements | Software requirements | SWE.1.BP6 | SWE.1.BP7 | Refinement |
| L04 | System architecture | Software requirements | SWE.1.BP6 | SWE.1.BP7 | Refinement |
| L05 | Software requirements | Software architecture (its elements) | SWE.2.BP7 | SWE.2.BP8 | Refinement |
| L06 | Software architecture | Software detailed design | SWE.3.BP5 | SWE.3.BP6 | Refinement |
| L07 | Software detailed design | Software units | SWE.3.BP5 | SWE.3.BP6 | Refinement |
| L08 | Software requirements | Software units | SWE.3.BP5 | SWE.3.BP6 | Refinement |
| L09 | System requirements | System qualification test specification (test cases) | SYS.5.BP5 | SYS.5.BP6 | Verification |
| L10 | System qualification test specification (test cases) | System qualification test results | SYS.5.BP5 | - | Result |
| L11 | System architecture (its elements) | System integration test specification (test cases) | SYS.4.BP7 | SYS.4.BP8 | Verification |
| L12 | System integration test specification (test cases) | System integration test results | SYS.4.BP7 | - | Result |
| L13 | Software requirements | Software qualification test specification (test cases) | SWE.6.BP5 | SWE.6.BP6 | Verification |
| L14 | Software qualification test specification (test cases) | Software qualification test results | SWE.6.BP5 | - | Result |
| L15 | Software architecture (its elements) | Software integration test specification (test cases) | SWE.5.BP7 | SWE.5.BP8 | Verification |
| L16 | Software integration test specification (test cases) | Software integration test results | SWE.5.BP7 | - | Result |
| L17 | Software detailed design | Unit test specification | SWE.4.BP5 | SWE.4.BP6 | Verification |
| L18 | Unit test specification | Unit test results | SWE.4.BP5 | - | Result |
| L19 | Software units | Static verification results | SWE.4.BP5 | - | Result |
| L20 | Change requests | Work products affected by the change | SUP.10.BP8 | - | Change |
| L21 | Change requests | Problem reports (only when a problem triggered the change) | SUP.10.BP8 | - | Change |

Notes for implementers:

- Granularity on the test side is the individual test case, not the test document; on the
  architecture side it is the architectural element.
- L03 and L04 belong to the same practice, as do L06, L07 and L08. Where one practice names
  several upstream sources, the project may choose a combination of routes that covers its
  needs; duplicating every link over every route is not required. A toolkit needs the
  chosen routing as an explicit setting so that coverage can be computed against it.
- In the model, test results are linked to test cases, not directly to requirements.
  Requirement coverage by results is computed transitively (for example L09 then L10).
- Static verification results (L19) hang on the software units themselves, not on the
  detailed design.
- Rating rules and recommendations for this topic use the ID prefix `TAC`.

### 8.3 Checks a toolkit can derive from the table

- Downward: every left item has at least one right item, or a recorded reason why none is needed.
- Upward: every right item has at least one left item, or is flagged as having no parent
  (for example a design decision or a derived requirement) with a reason.
- Result: every executed test case has a result linked to the tested version.
- Change: every change request names the work product versions it touched.
- Consistency: for every pair with a consistency practice, a review record exists that
  covers the linked content in its current version.

## 9. Agree, summarize and communicate

Two phrases recur in the practice names and are often over-interpreted.

| Phrase | Side of the V | Meaning | Practices |
|---|---|---|---|
| Communicate agreed ... | Left: SYS.2, SYS.3, SWE.1, SWE.2, SWE.3 | The parties affected share one understanding of what the content of the work product means | SYS.2.BP8, SYS.3.BP8, SWE.1.BP8, SWE.2.BP9, SWE.3.BP7 |
| Summarize and communicate ... | Right: SYS.4, SYS.5, SWE.4, SWE.5, SWE.6 | Condensed information from test execution is made available to everyone who needs it | SYS.4.BP9, SYS.5.BP7, SWE.4.BP7, SWE.5.BP9, SWE.6.BP7 |

- Neither phrase asks for a formal approval or sign-off. Formal confirmation between
  parties is a capability level 2 matter and belongs to
  `GP 2.1.7 Manage the interfaces between involved parties`.
- Vocabulary: specifications and designs are made up of "elements" (left side); the
  product is made up of "items" (right side).
- Evidence at level 1 therefore does not need a sign-off. Examples: a distribution or
  notification that reached the affected roles, review participation, a test summary that
  lets the reader judge the consequences of the results.
- Rating recommendations for this topic use the ID prefix `SAC`.

## 10. Evaluation, verification criteria and compliance

Three different checks appear in the engineering processes. They are owned by different
processes and must not be merged.

| Concept | Owner | What is done | Practices |
|---|---|---|---|
| Evaluate | The design process itself | The design is assessed by its authors' process against defined criteria; for architectures this means weighing alternatives | SYS.3.BP5 Evaluate alternative system architectures, SWE.2.BP6 Evaluate alternative software architectures, SWE.3.BP4 Evaluate software detailed design |
| Verification criteria | The requirements process | For each requirement, criteria are written that state how fulfilment will be shown; they are the input for the qualification test of the same level | SYS.2.BP5 Develop verification criteria (consumed by SYS.5), SWE.1.BP5 Develop verification criteria (consumed by SWE.6) |
| Compliance | The test process | The test specification is built so that passing it gives evidence that the test object complies with its reference | SYS.5.BP2 (system requirements), SYS.4.BP3 (system architectural design), SWE.6.BP2 (software requirements), SWE.5.BP3 (software architectural design), SWE.4.BP2 (software detailed design) |

Verification criteria also feed SUP.2 Verification where that process is in scope.
Rating rules for verification criteria use the ID prefix `VEC`.

## 11. Reading the management and support processes

The management and support processes can be read as one control system around the
engineering work. Each of them has its own specific front end and the same back end:
report progress and trends against the plan, then adjust and escalate.

| Process | Specific steps | Hands over |
|---|---|---|
| SUP.1 Quality Assurance | Set up the quality strategy and plan; measure product quality; measure process quality | Findings, which enter SUP.9 as non-conformities |
| SUP.9 Problem Resolution Management | Record non-conformities (customer claims, bugs, issues, QA findings); follow the emergency plan where needed; start a change request or a corrective action | A change request to SUP.10, or a task to MAN.3 |
| SUP.10 Change Request Management | Record change requests (from stakeholders or from SUP.9); analyse the impact; approve | An approved change, which becomes a task in MAN.3 |
| MAN.3 Project Management | Define scope; define the life cycle; estimate effort; check feasibility; secure resources; schedule tasks | The schedule that all other processes work to. New functions enter at the estimation step; tasks from SUP.9, SUP.10 and MAN.5 enter at the scheduling step |
| MAN.5 Risk Management | Define the risk strategy; identify risk sources and risks; analyse and rate them; define mitigation actions | Mitigation actions, which become tasks in MAN.3 |
| SUP.8 Configuration Management | Underlies all of the above | Controlled versions and baselines of every work product the other processes produce |

Points that follow for interpretation:

- A finding, a problem, a change and a risk action all end up as scheduled, tracked tasks.
  If they live in separate lists that never reach the project schedule, the loop is open.
- Every one of these processes is expected to show the report-and-adjust loop for its own
  subject, not only MAN.3 for the project as a whole.
- Practices that ask for a strategy (for example SUP.1.BP1, SUP.8.BP1, SUP.9.BP1,
  SUP.10.BP1) fall under the rating guidance with the ID prefix `SAP` (strategy and plan).

## 12. Applying the pattern at system, domain and component level

The same four-step pattern from principle 3 applies at each level, with level-specific
artefacts:

| Step | System level | Software level | Software component / unit level |
|---|---|---|---|
| Specify | System requirements (SYS.2) | Software requirements (SWE.1) | Component and unit specification within the detailed design (SWE.3) |
| Design | System architecture (SYS.3) | Software architecture (SWE.2) | Detailed design (SWE.3) |
| Delegate or implement | Allocate to software, hardware, mechanics | Allocate to software components | Implement the software units (SWE.3) |
| Integrate and verify against the design | SYS.4 | SWE.5 | SWE.4 |
| Qualify against the specification | SYS.5 | SWE.6 | SWE.4 |

A process element is therefore always interpreted for the level it sits on: "requirements"
in SYS.2 are system requirements only; "integration" in SWE.5 means software units and
components into the integrated software, not software onto hardware (that is SYS.4).

## 13. Work product characteristics

The model's annex of work products gives, for each work product type, three things:

| Field | Meaning |
|---|---|
| WP ID | A number used to reference the type, for example `04-04` |
| WP name | A typical name for the type. Real projects may use other names, may spread one type over several documents or tool records, or may combine several types in one; the format is free |
| WP characteristics | Examples of content the type would be expected to show. An assessor looks for them in the samples presented |

How to use them:

- They are indicators, not a template. What counts is that the content exists somewhere in
  the project's artefacts and can be shown.
- The mapping from the project's real artefacts to the model's work product types is made
  by the assessor together with the coordinator of the assessed organization. A toolkit
  should keep this mapping explicit (real artefact or tool query -> WP ID).
- Inheritance for plans: from capability level 2 upward, every process-specific plan
  (IDs `08-nn`) carries both its own characteristics and those of the generic plan `08-00`.

Two examples of what characteristics look like, restated:

| WP | Expected content |
|---|---|
| `04-00` Design (generic) | Overall structure of the product or system; the elements it needs; how the elements relate; attention to required performance, interfaces and security properties |
| `04-04` Software architectural design | Overall software structure; use of the operating system including the task structure; communication between tasks or processes; the software elements needed; which code is developed in-house and which is supplied; relations and dependencies between elements; where data such as parameters and variables is stored and how it is protected against corruption (for example checksums, redundancy); how variants for vehicle lines or configurations are derived; dynamic behaviour, for example during start-up and shutdown, during a software update and when errors are handled and recovered from; what data is kept persistently, and when; attention to performance, interfaces, security and any database design needs |

## 14. Rating rule and recommendation IDs

The VDA Automotive SPICE Guidelines (1st edition, 2017) attach rules (`RL`: to be followed
when rating; a deviation has to be justified in the assessment report) and recommendations
(`RC`: should be considered) to practices. The IDs are grouped by prefix:

| Prefix | Subject |
|---|---|
| `TAC` | Traceability and consistency |
| `SAC` | Summarize and communicate |
| `VEC` | Verification criteria |
| `SAP` | Strategy and plan |
| `MBD` | Model-based development |
| `AGE` | Agile environments |
| `DID` | Distributed development |
| `TPS` | Management of third-party software |
| `PLS` | Management of platform and legacy software |
| `APA` | Application parameters |
| `<process ID>` such as `SWE.1` | Rules for one process of the VDA scope |
| `CL2`, `CL3` | Rules for the process attributes of capability levels 2 and 3. Guidance exists for levels 1 to 3; no level-1 IDs are recorded in this knowledge base |

ID form: `<prefix>.RL.<n>` or `<prefix>.RC.<n>`, for example `MAN.3.RL.1`, `DID.RL.1`,
`PLS.RC.1`, `CL2.RC.18`.

Dependency diagrams for rating consistency use one convention: a solid line is a rule, a
dashed line a recommendation, and an arrow points from the practice being rated to the
practice its rating depends on. Dependencies exist inside one process and across processes.

## 15. Automation notes

| Topic | Script | LLM | Human |
|---|---|---|---|
| Link pairs L01 to L21 | Existence, direction and coverage of links; orphan detection; results linked to test cases | Plausibility of a link (does this test case address this requirement?) | Acceptance of justified gaps |
| Consistency | Presence and currency of review records per pair | Pre-review of linked content for contradictions | The review decision itself |
| Communicate agreed / summarize and communicate | Presence of a distribution or notification record and of a test summary | Whether a summary lets a reader judge the consequences | Whether the affected parties really share the understanding |
| Scope classification of a process | Lookup in the tables of section 4 | - | Choice of assessment scope |
| Work product mapping | Maintain the artefact -> WP ID map and check each WP type has at least one source | Compare artefact content with the expected characteristics | Confirm the mapping |
