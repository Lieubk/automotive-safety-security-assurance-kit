# Roles, processes and what the scope means

## Roles and their typical process sets

A typical set is where the conversation starts, never where it ends. Two teams with
the same role rarely have the same contract. Show the row of the role, then let the
user add and remove.

| Role | `scope.role` | Usually receives | Typical responsibility | Ask in particular |
|---|---|---|---|---|
| Vehicle manufacturer | `manufacturer` | needs of vehicle functions, legal and internal demands | SYS.1 to SYS.5; ACQ.4 for each supplier it monitors; SWE.1 to SWE.6 only for software it builds itself; MAN.3, SUP.1, SUP.8, SUP.9, SUP.10 | Which parts are bought? For those the team specifies and monitors, and the supplier's processes are not the team's. |
| System supplier (ECU: system and software) | `system-supplier` | customer requirement specifications | SYS.2 to SYS.5, SWE.1 to SWE.6, MAN.3, SUP.1, SUP.8, SUP.9, SUP.10; SYS.1 when the team agrees the requirements with the customer itself; ACQ.4 when it has suppliers of its own | Who agrees the customer requirements? Who builds hardware and mechanics, and who tests the system? |
| Software supplier to a system supplier | `software-supplier` | system requirements, system architecture, hardware-software interface | SWE.1 to SWE.6, MAN.3, SUP.1, SUP.8, SUP.9, SUP.10 | Who integrates the software and who runs the qualification test? In the worked example the customer integrates, and the team's scope ends at SWE.4. |
| Supplier of a software component | `component-supplier` | software requirements for the component, the architecture and interfaces around it | SWE.3, SWE.4; SWE.1 and SWE.2 when the component has requirements and an inner structure of its own to define; SWE.5 and SWE.6 when the team integrates and tests the component before delivery; SUP.8, SUP.9, SUP.10 | Is the component delivered as source or as a tested binary? Whose change and problem process applies? |
| Engineering service on work packages | `engineering-service` | whatever the work package names | only the processes the work packages name, for example SWE.3 and SWE.4 for a design-and-implement package, or SWE.6 for a test package | Which supporting processes are the client's? Work done inside the client's configuration, change and problem management is not the team's process. |

## Processes that can be put in scope

These are the processes of `aspice/3.1/index.yaml`; read the file and use its names
and scope classes, and correct this table in what you show if they differ. `VDA` is
the scope class of the index: `vda` (the basic set), `extended`, or `other`.

Toolkit support has three levels. `authoring`: a skill drafts the work products with
the user. `checked`: the catalog, the item schema and trace rules exist, the items are
written by hand, and `/review`, `/trace-check` and `/process-gate` work on them.
`catalog`: only the process description and notes exist; the toolkit holds no item
type and no rule for the process, so its evidence lives outside the toolkit.

| Group | Process | Name | VDA | Toolkit support today |
|---|---|---|---|---|
| System | SYS.1 | Requirements Elicitation | extended | checked; `/import-inputs` registers what was received |
| System | SYS.2 | System Requirements Analysis | vda | checked |
| System | SYS.3 | System Architectural Design | vda | checked |
| System | SYS.4 | System Integration and Integration Test | vda | checked |
| System | SYS.5 | System Qualification Test | vda | checked |
| Software | SWE.1 | Software Requirements Analysis | vda | authoring: `/sw-requirements` |
| Software | SWE.2 | Software Architectural Design | vda | authoring: `/sw-architecture` |
| Software | SWE.3 | Software Detailed Design and Unit Construction | vda | authoring: `/sw-detailed-design`, `/sw-unit-implement` |
| Software | SWE.4 | Software Unit Verification | vda | authoring: `/sw-unit-verify` |
| Software | SWE.5 | Software Integration and Integration Test | vda | checked |
| Software | SWE.6 | Software Qualification Test | vda | checked |
| Supporting | SUP.1 | Quality Assurance | vda | checked; reviews through `/review`, gates through `/process-gate` |
| Supporting | SUP.2 | Verification | extended | catalog |
| Supporting | SUP.4 | Joint Review | extended | catalog |
| Supporting | SUP.7 | Documentation | extended | catalog |
| Supporting | SUP.8 | Configuration Management | vda | authoring for baselines: `/baseline` |
| Supporting | SUP.9 | Problem Resolution Management | vda | checked |
| Supporting | SUP.10 | Change Request Management | vda | authoring for change requests: `/change-request` |
| Management | MAN.3 | Project Management | vda | authoring: `/project-plan`, `/work-breakdown`, `/project-status` |
| Management | MAN.5 | Risk Management | extended | catalog |
| Acquisition | ACQ.4 | Supplier Monitoring | vda | catalog |
| Supply | SPL.2 | Product Release | extended | catalog |
| Reuse | REU.2 | Reuse Program Management | other | catalog |

Before showing the table, compare the skills named in it with the result of Glob
`.claude/skills/*/SKILL.md`. A skill that is not installed is shown as "not installed"
and its process drops to `checked`. A skill that is installed and not named here is
added from its own description. `/review`, `/trace-check` and `/process-gate` serve
every process that has item types.

Tell the user what `checked` and `catalog` mean before they pick: putting such a
process in scope makes the toolkit report what is missing, but nobody drafts it.

## Responsibility and assessment scope

`scope.processes` says what the team does and answers for. `scope.assessment_scope`
says what an assessment will rate. The first is the team's decision with its customer;
the second is set by whoever commissions the assessment, together with the assessor.
They often differ, and the difference is worth seeing on day one.

The usual trap: the customer delivers a finished requirement set, the team concludes
that the analysis process of that level is not its business, and the assessment rates
it anyway. A delivery can stand in for writing the requirements down. It does not
stand in for what the team is expected to do with them: structure them for its own
work, examine them for correctness, feasibility and verifiability, work out what they
mean for the environment, give each one verification criteria, link them up and down,
check consistency, and agree and communicate the result. An assessor who rates the
process looks for that work at the team.

For every process in `assessment_scope` that is not in `processes`, say:

- no coverage rule of this process is active, so `check` is silent about it;
- no skill will produce or review its work products;
- the assessment will ask for its evidence all the same.

Then offer the two ways out and let the user decide:

1. Take the process into the responsibility. A delivered set then becomes the input of
   that process, registered one level up (see "Choosing the type" in the references of
   `/import-inputs`), and the team produces its own work products from it.
2. Clarify with whoever commissions the assessment that the process is performed, and
   rated, at another party. The answer is an agreement: record it only when the user
   states that it was given, by whom and when.

Record both lists as the user states them. A difference that remains is shown again
by `/next-step` every time, which is the point of recording it.

The opposite case needs no warning: a team may be responsible for more than an
assessment rates.

## Target level

Keep the explanation to these lines; `aspice/3.1/notes/capability-levels.md` has the
detail.

| Target | What has to be shown, per process | What it means here |
|---|---|---|
| 1 | The results exist: work products with the right content, linked and consistent. | This is what the items, the trace rules and the reviews of this toolkit are about. |
| 2 | Level 1 without gaps, and the work is managed: planned and tracked per process, responsibilities named, work products under control and reviewed against criteria defined beforehand. | Project management carries the planning side, quality assurance and configuration management the work product side. With MAN.3, SUP.1 or SUP.8 in neither list the target is not realistic: warn. Named reviewers in `people` and checklists with versions are no longer optional. |
| 3 | Level 2, and the project works from a standard process of the organization, tailored by rule, with feedback going back. | Half of that evidence comes from the organization, outside any project. The toolkit records the target and helps with nothing beyond level 2. |

One value is recorded for all processes in scope. If the user names different targets
for single processes, record the highest and list the exceptions as open points in the
hand-over. Say once: the toolkit prepares evidence and shows gaps; a level is the
result of an assessment, not of a tool.
