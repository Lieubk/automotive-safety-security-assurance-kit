# Capability levels, process attributes and generic practices (Automotive SPICE 3.1)

## How to read this note

- A capability level is reached per process. Each level from 1 upward is defined by one or
  two process attributes (PA). A PA lists achievements (lettered a, b, c ...) and is
  evidenced by generic practices (GP). Each GP is tagged below with the achievement it
  supports.
- Generic practices are the same for every process. They are always judged for one
  concrete process: "is the performance of SWE.1 planned?", not "is the project planned?".
- `Rating rule IDs` are rule (`RL`) and recommendation (`RC`) IDs of the VDA Automotive
  SPICE Guidelines (1st edition, 2017). Only IDs are given. The first group in each cell is
  attached to the practice directly; IDs marked "dep." come from the dependency relations in
  the section "Dependencies".
- `Typical evidence` gives examples of what could be shown. The model itself names no
  mandatory generic work products, so the examples are illustrative, not a checklist.
- Rating scale and the rule that combines PA ratings into a level are in
  `assessment-method.md` and, as data, in `catalog-fragments/capability-levels.yaml`.

## Level overview

| Level | Name | Process attributes | A process at this level ... |
|---|---|---|---|
| 0 | Incomplete | none | does not achieve its purpose, or only partly |
| 1 | Performed | PA 1.1 | achieves its purpose |
| 2 | Managed | PA 2.1, PA 2.2 | is in addition run in a managed way (planning, monitoring, adjustment), with work products that are properly established, controlled and maintained |
| 3 | Established | PA 3.1, PA 3.2 | is in addition run as a defined process derived from an organizational standard process that is able to deliver the outcomes |
| 4 | Predictable | PA 4.1, PA 4.2 | in addition operates within quantitatively defined limits |
| 5 | Innovating | PA 5.1, PA 5.2 | is in addition improved continually in line with organizational goals |

Levels are cumulative: a level counts only if all attributes of the lower levels are
fully achieved.

## PA 1.1 Process performance (level 1)

Intent: measures how far the process achieves its purpose. Fully achieved when the process
produces its defined outcomes.

| GP | Official short name | Achievement | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|---|
| GP 1.1.1 | Achieve the process outcomes | a | The intent of every base practice of the process is met, and work products exist that demonstrate the outcomes | The output work products of the process with the expected content; statements of the people doing the work that match those work products | none recorded here; the base practice rules of the process apply |

Generic resource for this attribute: the resources actually used to carry out the base
practices (people, tools, infrastructure).

PA 1.1 is rated from the base practice ratings of the process and the work products that
back them. The process-specific rules and most term-specific rules (`TAC`, `SAC`, `VEC`,
`SAP`) are attached to base practices and therefore act on this attribute.

## PA 2.1 Performance management (level 2)

Intent: measures how far the execution of the process is managed.

Achievements when fully met:

- a) objectives for performing the process are identified
- b) performance is planned
- c) performance is monitored
- d) performance is adjusted so that plans are met
- e) responsibilities and authorities are defined, assigned and communicated
- f) the people performing the process are prepared for their responsibilities
- g) needed resources and information are identified, provided, allocated and used
- h) interfaces between the parties involved are managed, so that communication works and
  responsibility is clearly assigned

| GP | Official short name | Achievement | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|---|
| GP 2.1.1 | Identify the objectives for the performance of the process | a | Performance objectives for this process are derived from what the process is required to deliver; it is stated what the performance of the process covers; assumptions and constraints were taken into account. Objectives can address on-time delivery of artefacts that meet their quality criteria, cycle time or frequency, resource usage and the boundaries of the process. As a minimum, objectives for resources, effort and schedule are stated | A plan section or planning record per process that states due dates or cadence, effort and resource budget, quality targets for the outputs, scope, assumptions and constraints | CL2.RL.1, CL2.RL.2, CL2.RL.3, CL2.RL.4 |
| GP 2.1.2 | Plan the performance of the process to fulfill the identified objectives | b | A plan for performing the process exists: the performance cycle is defined, key milestones are set, estimates for the performance attributes are made and kept current, activities and tasks are defined, the schedule fits the chosen approach, and reviews of the process's work products are planned | Schedule or backlog entries for the activities of this process with owners, effort and dates; milestone or iteration plan; estimate records with updates; planned review dates per work product | CL2.RL.5, CL2.RL.6, CL2.RL.7, CL2.RL.8, CL2.RL.9, CL2.RL.22; dep.: CL2.RC.4 |
| GP 2.1.3 | Monitor the performance of the process against the plans | c | The process is carried out as planned, and it is monitored so that planned results are reached and deviations become visible | Plan-versus-actual comparison for the tasks of this process, status reports, progress metrics, recorded deviations | CL2.RL.10, CL2.RL.11, CL2.RL.12, CL2.RL.23; dep.: CL2.RC.5 |
| GP 2.1.4 | Adjust the performance of the process | d | Performance issues are identified; action is taken when planned results or objectives are missed; plans are adjusted and work is rescheduled where needed | Issue and action list with owners and closure, re-planned schedule versions with the reason for the change, escalation records | CL2.RL.13, CL2.RL.14, CL2.RL.24, CL2.RL.25, CL2.RL.26; dep.: CL2.RC.6 |
| GP 2.1.5 | Define responsibilities and authorities for performing the process | e | It is defined, assigned and made known who is responsible for what, who has committed to what and who holds which authority in performing the process; this includes who is responsible and authorized to verify the work products; the experience, knowledge and skills the process needs are defined | Role assignment for this process (for example a responsibility matrix), named reviewers and approvers per work product type, skill requirements per role, proof that the assignment was communicated | DID.RL.4, CL2.RL.15, CL2.RL.16, CL2.RL.17 |
| GP 2.1.6 | Identify, prepare, and make available resources to perform the process according to plan | f, g | Human and infrastructure resources needed for the process are identified, provided, allocated and actually used; the people performing and managing the process are prepared through training, mentoring or coaching; the information needed to perform the process is identified and accessible | Resource plan (people, tools, licences, test equipment) and evidence of availability, training or coaching records for the assigned people, access to the input information | DID.RL.5, CL2.RL.18, CL2.RL.19, CL2.RL.27, CL2.RL.28; dep.: CL2.RC.7 |
| GP 2.1.7 | Manage the interfaces between involved parties | h | The people and groups that take part in performing the process are determined; their responsibilities are assigned; the interfaces between them are managed; communication between them is ensured and is effective | Stakeholder and interface list for the process, agreed communication channels and cadence, minutes and action items, confirmations or sign-offs exchanged between the parties | SAC.RC.1, DID.RL.7, CL2.RL.20, CL2.RL.21, CL2.RC.3; dep.: CL2.RC.8, CL2.RC.9, CL2.RC.10 |

## PA 2.2 Work product management (level 2)

Intent: measures how well the work products that the process produces are managed. The
work products meant are those that result from achieving the process purpose through its
outcomes.

Achievements when fully met:

- a) what each work product must contain and satisfy is specified
- b) how work products are to be documented and kept under control is specified
- c) each work product is identifiable, documented and under control
- d) reviews happen as planned and work products are corrected until they satisfy what was specified

Documentation and control requirements can include how changes and revision status are
identified, approval and re-approval, distribution, and making the relevant versions
available where they are used.

| GP | Official short name | Achievement | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|---|
| GP 2.2.1 | Define the requirements for the work products | a | It is defined what the work products to be produced have to fulfil, which can include content and structure; quality criteria are identified; suitable review and approval criteria are defined | Templates or content definitions per work product type, quality criteria, review checklists, stated approval criteria | DID.RL.8, CL2.RL.29, CL2.RL.30, CL2.RL.31, CL2.RL.32, CL2.RL.33; dep.: CL2.RC.12 |
| GP 2.2.2 | Define the requirements for documentation and control of the work products | b | Requirements for documenting and controlling the work products are defined, which can cover distribution, identification of work products and their parts, and traceability; it is known and understood how the work products depend on one another; approval requirements for the controlled work products are defined | Rules for naming, identification, versioning, storage, status model, approval and distribution (often in the configuration management plan); a map of which work product depends on which | DID.RL.6, CL2.RL.34; dep.: CL2.RC.13, CL2.RC.14 |
| GP 2.2.3 | Identify, document and control the work products | c | It is identified which work products are to be controlled; they are under change control; they are documented and controlled as required; versions are assigned to product configurations where applicable; they are accessible through suitable mechanisms; their revision status can be found out easily | Configuration item list, repository history, change records, baselines that tie work product versions to a product configuration, access rights, visible version and status in each work product | CL2.RL.40; dep.: CL2.RC.15, CL2.RC.16 |
| GP 2.2.4 | Review and adjust work products to meet the defined requirements | d | Reviews take place as planned and check the work products against the requirements defined for them; the issues raised in the reviews are resolved | Review records per work product version that reference the criteria used, findings tracked to closure, evidence of rework and approval | none attached directly; dep.: CL2.RC.17, CL2.RC.18 and one rule whose ID is unconfirmed (see Open points) |

## PA 3.1 Process definition (level 3)

Intent: measures how far a standard process is maintained that supports the deployment of
the defined process. A standard process belongs to the organization; a defined process is
what a project runs after selecting and tailoring from it.

Achievements when fully met:

- a) a standard process with suitable tailoring guidelines is defined and maintained; it
  describes the fundamental elements every defined process must contain
- b) it is determined in which order the standard process runs relative to other processes
  and how it interacts with them
- c) the standard process identifies the competencies and roles it needs
- d) the standard process identifies the infrastructure and work environment it needs
- e) it is determined by which methods and measures the process is monitored for being
  effective and suitable

| GP | Official short name | Achievement | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|---|
| GP 3.1.1 | Define and maintain the standard process that will support the deployment of the defined process | a | A standard process containing the fundamental process elements is developed and maintained; it states its deployment needs and context; guidance or procedures support its implementation where needed; tailoring guidelines are available where needed | Organization-level process description (activities, inputs, outputs, roles), supporting guidance and templates, tailoring guideline, maintenance history of the description | CL3.RL.1, CL3.RL.2, CL3.RL.3, CL3.RL.4, CL3.RL.5, CL3.RC.4, CL3.RC.5; dep.: CL3.RC.3 |
| GP 3.1.2 | Determine the sequence and interaction between processes so that they work as an integrated system of processes | b | The order of the standard process and its interaction with other processes are determined; deploying it as a defined process keeps the processes intact as a whole | Process landscape or interface description showing order, hand-overs and exchanged work products | CL3.RL.6, CL3.RC.3, CL3.RC.4, CL3.RC.5 |
| GP 3.1.3 | Identify the roles and competencies, responsibilities, and authorities for performing the standard process | c | Roles for performing the process are identified, together with the competencies they need and the authorities required to carry out their responsibilities | Role descriptions in the standard process with competencies, responsibilities and authorities | CL3.RL.7, CL3.RC.3, CL3.RC.4, CL3.RC.5 |
| GP 3.1.4 | Identify the required infrastructure and work environment for performing the standard process | d | The infrastructure components of the process (facilities, tools, networks, methods and the like) are identified, as are the requirements on the work environment | Standard tool chain and environment definition attached to the standard process | CL3.RL.8, CL3.RC.3, CL3.RC.4, CL3.RC.5 |
| GP 3.1.5 | Determine suitable methods and measures to monitor the effectiveness and suitability of the standard process | e | Methods and measures for monitoring effectiveness and suitability are determined; the criteria and data needed for that are defined; the need for internal audits and management reviews is established; process changes are implemented so that the standard process stays maintained | Defined process measures and feedback channels, audit and management review scheme, change history of the standard process | CL3.RL.9; dep.: CL3.RC.4 |

## PA 3.2 Process deployment (level 3)

Intent: measures how far a defined process, derived from the standard process, is in use and
achieves its outcomes.

Achievements when fully met:

- a) the process in use is a defined one, taken from the standard process by appropriate selection or tailoring
- b) who holds which role, responsibility and authority in the defined process is assigned and made known
- c) those who perform the defined process have the competence for it, by education, training and experience
- d) the necessary resources and information are made available, assigned and actually used
- e) the necessary infrastructure and work environment are in place, managed and kept up
- f) suitable data is collected and analysed to understand how the process behaves, to show
  that it is suitable and effective, and to find where it can be improved continually

| GP | Official short name | Achievement | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|---|
| GP 3.2.1 | Deploy a defined process that satisfies the context specific requirements of the use of the standard process | a | The defined process is selected or tailored appropriately from the standard process, and its conformance with the requirements of the standard process is verified | Project tailoring record with justification, result of a conformance check of the project process against the standard | CL3.RL.10; dep.: CL3.RC.5 |
| GP 3.2.2 | Assign and communicate roles, responsibilities and authorities for performing the defined process | b | Roles, responsibilities and authorities for the defined process are assigned and communicated | Project staffing against the standard role definitions, communicated to the team | CL3.RL.11, CL3.RC.1, CL3.RL.17, CL3.RL.22 |
| GP 3.2.3 | Ensure necessary competencies for performing the defined process | c | The competencies the assigned people need are identified; suitable training is available to those who deploy the defined process | Comparison of people's skills with the role requirements, training offered and attended | CL3.RL.12, CL3.RL.13, CL3.RL.18 |
| GP 3.2.4 | Provide resources and information to support the performance of the defined process | d | The human resources needed are provided, allocated and used; the information needed to perform the process is provided, allocated and used | Staffing per defined role, access of the team to the required information | CL3.RL.14, CL3.RL.19, CL3.RC.6 |
| GP 3.2.5 | Provide adequate process infrastructure to support the performance of the defined process | e | The required infrastructure and work environment is available; the organization supports managing and maintaining it; it is used and maintained | Standard tools and environments installed and in use in the project, maintenance and support arrangements | CL3.RL.15, CL3.RL.20, CL3.RC.7 |
| GP 3.2.6 | Collect and analyze data about performance of the process to demonstrate its suitability and effectiveness | f | The data needed to understand behaviour, suitability and effectiveness of the defined process is identified, collected and analysed; the results are used to find where the standard or the defined process can be improved. The data may be qualitative or quantitative | Collected process data and feedback from the project, analysis results, improvement proposals passed to the owner of the standard process | CL3.RL.16, CL3.RC.2, CL3.RL.21 |

## Dependencies

Convention: "A depends on B" means that A is rated in the light of B; a weakness in B
normally limits the rating of A. Recommendations between a generic practice and base practices are mutual: the two ratings
should be looked at together and should not contradict each other without a stated reason.
The gist column describes the relation only; the wording of the rules is not reproduced.

### Rules inside PA 2.1

| ID | Practice rated | Depends on | Gist |
|---|---|---|---|
| CL2.RL.22 | GP 2.1.2 | GP 2.1.1 | A plan is judged by whether it serves the identified objectives |
| CL2.RL.23 | GP 2.1.3 | GP 2.1.2 | Monitoring is done against the plans |
| CL2.RL.24 | GP 2.1.4 | GP 2.1.1 | Adjustment reacts when planned objectives are missed |
| CL2.RL.25 | GP 2.1.4 | GP 2.1.2 | Adjustment includes updating the plans |
| CL2.RL.26 | GP 2.1.4 | GP 2.1.3 | Adjustment reacts to monitored results that fall short of the plan |
| CL2.RL.27 | GP 2.1.6 | GP 2.1.2 | Resources are provided as the plan requires |
| CL2.RL.28 | GP 2.1.6 | GP 2.1.5 | Resources are made available in line with what was defined for responsibilities |

Recommendation inside PA 2.1: CL2.RC.3 - GP 2.1.7 depends on GP 2.1.5 (interfaces are
managed along the defined responsibilities).

### Rules inside PA 2.2

| ID | Practice rated | Depends on | Gist |
|---|---|---|---|
| CL2.RL.40 | GP 2.2.3 | GP 2.2.2 | Work products are controlled according to the defined control requirements |
| unconfirmed ID | GP 2.2.4 | GP 2.2.1 | Reviews are held against the defined work product requirements |

### Recommendations between level-2 generic practices and base practices

| ID | Generic practice | Related base practices | Subject |
|---|---|---|---|
| CL2.RC.4 | GP 2.1.2 | MAN.3.BP4, MAN.3.BP5, MAN.3.BP8 | Defining activities, estimates and resources, and schedule |
| CL2.RC.5 | GP 2.1.3 | MAN.3.BP4, MAN.3.BP5, MAN.3.BP8 | Monitoring them |
| CL2.RC.6 | GP 2.1.4 | MAN.3.BP4, MAN.3.BP5, MAN.3.BP8 | Adjusting them |
| CL2.RC.7 | GP 2.1.6 | MAN.3.BP6 | Ensuring skills, knowledge and experience |
| CL2.RC.8 | GP 2.1.7 | MAN.3.BP7 | Project interfaces and agreed commitments |
| CL2.RC.9 | GP 2.1.7 | SYS.2.BP8, SYS.3.BP8, SWE.1.BP8, SWE.2.BP9, SWE.3.BP7 | For each of these processes, its own "communicate agreed" practice is taken into account |
| CL2.RC.10 | GP 2.1.7 | SYS.4.BP9, SYS.5.BP7, SWE.4.BP7, SWE.5.BP9, SWE.6.BP7 | For each of these processes, its own "summarize and communicate" practice is taken into account |
| CL2.RC.12 | GP 2.2.1 | SUP.1.BP1 | Quality criteria set in the quality assurance strategy |
| CL2.RC.13 | GP 2.2.2 | SUP.8.BP1, SUP.8.BP2 | Configuration management strategy and identification of configuration items |
| CL2.RC.14 | GP 2.2.2 | SUP.10.BP1 | Change request management strategy |
| CL2.RC.15 | GP 2.2.3 | SUP.8.BP3, SUP.8.BP5, SUP.8.BP6 | Configuration management system, control of modifications and releases, baselines |
| CL2.RC.16 | GP 2.2.3 | SUP.10.BP2, SUP.10.BP3, SUP.10.BP7 | Recording change requests, recording their status, tracking them to closure |
| CL2.RC.17 | GP 2.2.4 | SUP.1.BP2 | Quality assurance of work products |
| CL2.RC.18 | GP 2.2.4 | SUP.8.BP8; SYS.2.BP7, SYS.3.BP7, SYS.4.BP8, SYS.5.BP6; SWE.1.BP7, SWE.2.BP8, SWE.3.BP6, SWE.4.BP6, SWE.5.BP8, SWE.6.BP6 | Verification of configured items; the "ensure consistency" practice of each engineering process |

Summary by process:

| Process | Related generic practices |
|---|---|
| MAN.3 | GP 2.1.2, GP 2.1.3, GP 2.1.4 (via BP4, BP5, BP8); GP 2.1.6 (via BP6); GP 2.1.7 (via BP7) |
| SUP.1 | GP 2.2.1 (via BP1); GP 2.2.4 (via BP2) |
| SUP.8 | GP 2.2.2 (via BP1, BP2); GP 2.2.3 (via BP3, BP5, BP6); GP 2.2.4 (via BP8) |
| SUP.10 | GP 2.2.2 (via BP1); GP 2.2.3 (via BP2, BP3, BP7) |
| SYS.2, SYS.3, SWE.1, SWE.2, SWE.3 | GP 2.1.7 (via "communicate agreed"); GP 2.2.4 (via "ensure consistency") |
| SYS.4, SYS.5, SWE.4, SWE.5, SWE.6 | GP 2.1.7 (via "summarize and communicate"); GP 2.2.4 (via "ensure consistency") |

Practical reading: when project management is weak, PA 2.1 of every other process is hard
to rate high, because each process plans, monitors and staffs through the project's
mechanisms. When quality assurance and configuration management are weak, PA 2.2 of every
other process suffers in the same way. The link also works as a plausibility check in the
other direction: a strong rating of GP 2.2.4 for a process whose own consistency practice
at level 1 is rated low should be questioned.

### Dependencies at level 3

| ID | Kind | Practice rated | Depends on | Gist |
|---|---|---|---|---|
| CL3.RL.17 | rule | GP 3.2.2 | GP 3.1.3 | Roles are assigned on the basis of the roles in the standard process |
| CL3.RL.18 | rule | GP 3.2.3 | GP 3.1.3 | Competencies are ensured against those the standard process identifies |
| CL3.RL.19 | rule | GP 3.2.4 | GP 3.1.3 | Resources and information are provided on the basis of the standard process |
| CL3.RL.20 | rule | GP 3.2.5 | GP 3.1.4 | Infrastructure is provided as the standard process identifies it |
| CL3.RL.21 | rule | GP 3.2.6 | GP 3.1.5 | Data is collected on the basis of the measures the standard process determines |
| CL3.RC.5 | recommendation | GP 3.2.1 | GP 3.1.1 to GP 3.1.4 as a group | The defined process is based on the standard process |
| CL3.RC.3 | recommendation, mutual | GP 3.1.1 | GP 3.1.2, GP 3.1.3, GP 3.1.4 | The standard process includes interaction, roles and infrastructure |
| CL3.RC.4 | recommendation, mutual | GP 3.1.5 | GP 3.1.1 to GP 3.1.4 as a group | Effectiveness monitoring refers to the standard process as defined |

In short: every PA 3.2 practice has a counterpart in PA 3.1 on which its rating depends, by
rule for GP 3.2.2 to GP 3.2.6 and by recommendation for GP 3.2.1. A project cannot deploy
well what the organization has not defined.

### Process weaknesses that usually show up in a process attribute

`++` strong and `+` normal dependency: a weak process in a row usually goes
together with a weak process attribute in the marked column (for the processes assessed).

| Process | PA 2.1 | PA 2.2 | PA 3.1 | PA 3.2 |
|---|---|---|---|---|
| MAN.3 Project Management | ++ | | | |
| MAN.5 Risk Management | + | | | + |
| REU.2 Reuse Program Management | | + | + | |
| ACQ.4 Supplier Monitoring | + | + | | |
| SUP.1 Quality Assurance | | ++ | | + |
| SUP.2 Verification | | ++ | | + |
| SUP.4 Joint Review | | + | | |
| SUP.7 Documentation | | + | + | |
| SUP.8 Configuration Management | | ++ | + | |
| SUP.9 Problem Resolution Management | + | + | | + |
| SUP.10 Change Request Management | | + | | + |
| SPL.2 Product Release | | + | | |

## What changes when a project targets CL2 instead of CL1

At CL1 it is enough that the outcomes exist: the work products are there, with the right
content, links and consistency. How the team got there may be informal. For CL2 the same
has to be shown as managed work, for every process in scope separately.

1. Rating threshold. PA 1.1 now has to be rated fully achieved (above 85 %), no longer just
   largely. Gaps that were tolerable at CL1 (partial coverage, missing trace links, late
   test levels) can block CL2 before any generic practice is looked at. PA 2.1 and PA 2.2
   each need at least largely achieved.
2. Per-process objectives and plan. Each process needs stated objectives - at least effort,
   resources and schedule - and a plan with activities, milestones, estimates and planned
   reviews. One project plan can hold them, but it must be possible to point at the entries
   for requirements analysis, for architecture, for each test level and so on.
3. Monitoring and reaction. Plan-versus-actual tracking exists per process, deviations are
   recorded, and there is a visible reaction: actions, re-planning, escalation.
4. Named responsibility. Who performs, who verifies and who approves each work product
   type is defined and communicated, with the skills the role needs.
5. Resources and preparation. People, tools and environments are planned and available;
   the people were prepared (training, mentoring or coaching); needed information is accessible.
6. Managed interfaces. The parties a process exchanges with are known and communication
   with them is arranged and works. This is where formal agreement and confirmation belong,
   beyond the level-1 "communicate" practices.
7. Work product requirements. For every work product type there are defined content and
   structure expectations, quality criteria, and review and approval criteria - before the
   work product is reviewed.
8. Control. Work products are identified, versioned, under change control, assigned to
   baselines or product configurations, accessible, with visible status. Rules for this are
   written down (identification, distribution, traceability, approval).
9. Reviews as planned. Reviews take place according to the plan and against the defined
   criteria, and findings are closed. A review record that names no reference criteria
   gives only weak support to GP 2.2.4.
10. Plans inherit. Every process-specific plan also has to meet the characteristics of the
    generic plan work product `08-00`.
11. Supporting processes become load-bearing. MAN.3 carries PA 2.1; SUP.1, SUP.2 and SUP.8
    carry PA 2.2 (see the matrix). A CL2 target for engineering processes is not realistic
    while these are weak.

## What changes when a project targets CL3 instead of CL2

At CL2 a project may manage each process in its own way. For CL3 the way of working has to
come from the organization and flow back to it.

1. Rating threshold. PA 1.1, PA 2.1 and PA 2.2 must all be fully achieved; PA 3.1 and
   PA 3.2 each need at least largely achieved.
2. A standard process exists above the project. For each process in scope the organization
   maintains a description with the fundamental elements, the order and interaction with
   neighbouring processes, roles with competencies and authorities, required infrastructure
   and work environment, and tailoring guidelines. This is evidence from the organization,
   not from the project.
3. Effectiveness monitoring is designed in. The standard process says which measures and
   feedback are used to judge whether it is effective and suitable, and establishes
   internal audits and management reviews.
4. The project process is derived, not invented. The project documents which standard
   process it uses and how it tailored it according to the guidelines, and someone verifies
   that the result conforms.
5. Roles and competencies follow the standard. Assignment uses the standard role
   definitions; competence of the assigned people is checked against them and training is
   available.
6. Standard infrastructure. The project uses the tool chain and environment the standard
   process defines, with organizational support for maintaining it.
7. Feedback loop. The project collects data on how the process behaves (qualitative or
   quantitative), analyses it, and the results reach whoever maintains the standard process
   as improvement input.
8. Evidence comes from two places. The organization shows the standard process and how it
   is maintained; the project shows the deployment and the feedback it returns.
9. Dependencies. GP 3.2.2 to GP 3.2.6 each depend on a PA 3.1 counterpart (CL3.RL.17 to
   CL3.RL.21). Weak REU.2, SUP.7 or SUP.8 tends to show in PA 3.1; weak MAN.5, SUP.1, SUP.2,
   SUP.9 or SUP.10 tends to show in PA 3.2.

## CL4 Predictable process

On top of an established process, performance is managed with numbers. PA 4.1 Quantitative
analysis (GP 4.1.1 to GP 4.1.7) requires that business goals are identified, that the
information needs of stakeholders are derived from them, that measurement objectives,
measurable relations between process elements and quantitative performance objectives are
set, that measures and collection frequency are defined, and that measurement results are
collected, analysed and reported. PA 4.2 Quantitative control (GP 4.2.1 to GP 4.2.5) requires
chosen analysis techniques, distributions and control limits that characterize process
performance, identification of assignable causes for every deviation from the limits,
corrective actions whose effect is checked, and separate distributions where assignable
causes are at work. Typically the standard process is extended to include the data
collection.

## CL5 Innovating process

On top of a predictable process, the process is improved continually in response to change
and in line with organizational goals. PA 5.1 Process innovation (GP 5.1.1 to GP 5.1.4)
requires innovation objectives derived from business goals, analysis of process data and
of common causes of variation to find opportunities, evaluation of new technologies and
process concepts, and an implementation strategy backed by management. PA 5.2 Process
innovation implementation (GP 5.2.1 to GP 5.2.3) requires that each proposed change is
evaluated for its impact on the objectives of both the defined and the standard process,
that the roll-out of agreed changes is managed (including economic, human, management and
technology factors, training, communication and records), and that the effect of a change
is measured against objectives and historical data.

## Automation notes

| Check | Script | LLM | Human |
|---|---|---|---|
| Presence of per-process objectives, plan entries, owners, review dates | Yes, if planning data is structured (tasks tagged with process ID) | Judge whether objectives are specific enough | Confirm the objectives are the real ones |
| Plan versus actual, open deviations without action | Yes | Summarize trends | Decide on escalation |
| Work product requirements exist per type (template, criteria, checklist) | Yes, by lookup in a work product catalogue | Compare a work product with its criteria | Approve criteria |
| Identification, versioning, baseline membership, status | Yes | - | - |
| Review held as planned, against criteria, findings closed | Yes, from review records | Quality of findings and of closure rationale | Review decision |
| Dependency plausibility (for example GP 2.1.3 rated above GP 2.1.2) | Yes, from the dependency tables; flag for justification | Draft the justification text | Accept or change the rating |
| Tailoring record against a standard process | Presence and completeness | Consistency of the tailoring with the guideline | Conformance decision |

## Open points

- One rule links GP 2.2.4 to GP 2.2.1 (reviews against defined requirements). Its ID could
  not be established reliably and has to be confirmed in the VDA guideline before it is used
  as a rule ID. CL2.RL.35 to CL2.RL.39 are not mapped to a practice in this knowledge base,
  and no rule ID is attached directly to GP 2.2.4.
- CL2.RC.4, CL2.RC.5 and CL2.RC.6 relate to MAN.3.BP5 with certainty. Their extension to
  MAN.3.BP4 and MAN.3.BP8 as one group is the reading used here and should be confirmed.
- CL3.RL.17 to CL3.RL.20: that each of these PA 3.2 practices depends on the standard
  process definition is certain. The specific PA 3.1 practice named in the table is the
  most plausible reading; CL3.RL.19 (GP 3.2.4 -> GP 3.1.3) in particular should be confirmed
  in the VDA guideline.
- CL2.RC.1, CL2.RC.2 and CL2.RC.11 are not mapped to a practice here.
- No rule IDs for PA 1.1, PA 4.x or PA 5.x are recorded.
- The content of the rules is deliberately not reproduced; only IDs, direction and subject
  of each dependency are given.
