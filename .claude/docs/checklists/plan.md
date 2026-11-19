# Plan review checklist

Version 11. Applies to: `plan`. Supports: MAN.3.BP1, MAN.3.BP2, MAN.3.BP3, MAN.3.BP6,
MAN.3.BP7, SWE.4.BP1, SWE.5.BP1, SWE.5.BP2, SWE.6.BP1, SYS.4.BP1, SYS.4.BP2, SYS.5.BP1,
SUP.1.BP1, SUP.8.BP1, SUP.9.BP1, SUP.10.BP1, MAN.5.BP1, MAN.5.BP2, the subclauses of
ISO/SAE 21434 that the cybersecurity kinds name, and the clauses of ISO 26262 the kind safety
names.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

A plan says how a process is going to be performed in this project. Apply the part
"Every plan" to each plan, then the part for its `kind`. The parts follow `plan_kinds`
in `schema/items.yaml`. A kind whose process is not in `scope.processes`, or whose clause
is not under `scope.cybersecurity` or part not under `scope.safety`, needs no plan.

Recording: the review record needs a result for every check ID of this file. The checks
of the parts for other kinds are `not-applicable`, with the note "plan of kind <kind>";
`tools/record.py review` fills them in when all subjects are plans of one kind, so only
"Every plan" and the part of that kind are listed in `--checks`. Plans of different kinds
are reviewed in separate reviews.

Accountable checks: some answers depend on something that cannot happen in the sitting -
an agreement of people who are not present, a confirmation from outside the team. Such
a check stays `not-assessed`, the plan stays `in-review`, and the review is completed
when the answer exists. It is not answered on someone's behalf. Where a check refers to
`project.yaml` (`scope.processes`, `people`, `safety`, `trace`) and the key is absent or
empty, ask the user; do not assume a value.

## Every plan

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-01 | Mandatory attributes and sections for its state are present, and `kind` is an allowed value | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| PLN-02 | The kind answers a strategy practice of a process in scope, and no second live plan of the same kind exists | Grep `^kind:` in the `plans` folder; compare with `plan_kinds` in `schema/items.yaml` and `scope.processes` in `project.yaml` | script |
| PLN-03 | `Scope` says what the plan covers, what it leaves out, and who covers what is left out; nothing the process needs falls between two plans | read `Scope`; compare with the other plans | semantic |
| PLN-04 | The plan is written for this project: it names the item types, units, tools and environments actually in use, and would not fit an arbitrary project unchanged | read the plan against `status` and the items it refers to | semantic |
| PLN-05 | `Approach` names the methods, their order and what triggers each activity; someone new to the project could work by it | read `Approach` | semantic |
| PLN-06 | Where the rigour depends on ASIL, the plan says how, for every ASIL that occurs in the project | compare `Approach` and `Criteria` with the `asil` values of the items and with `safety.highest_asil` in `project.yaml` | semantic |
| PLN-07 | Every criterion in `Criteria` can be decided as met or not met from a record or a tool output the project produces | read `Criteria`; name the record for each criterion | semantic |
| PLN-08 | The plan agrees with the other plans and with `project.yaml`: same terms, roles, tools, states and baseline purposes; no rule that another plan contradicts | read the plans side by side | semantic |
| PLN-09 | `Environment and tools` names each tool with its use and with where its version is recorded; the limits of tools and environment are stated | read the section | semantic |
| PLN-10 | `Responsibilities` gives, per activity, the role that performs it and the role that checks or approves it; where independence is needed, it is stated | read the section | semantic |
| PLN-11 | What the plan deliberately does not do is declared together with its consequence, not left out silently | read `Scope` and `Approach` for declared limitations | semantic |
| PLN-12 | The plan says which events lead to its update (a new release, a change of scope, of tools or of ASIL) | read the plan | semantic |
| PLN-13 | The people who work by the plan know it and consider it workable | ask who was informed, how, and whether objections remain | accountable |
| PLN-14 | The plan fits the project schedule and the release plan, and the people, tools and equipment it relies on are available | ask the project lead | accountable |
| PLN-15 | The roles named in `Responsibilities` are filled | ask who holds each role; compare with `people` in `project.yaml` where that key is filled | accountable |

## Kind project (MAN.3.BP1, MAN.3.BP2, MAN.3.BP3, MAN.3.BP6, MAN.3.BP7)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-110 | `Feasibility`, `Interfaces and commitments`, `Reporting` and `milestones` are present | `check`: no `SCHEMA` finding on the item | script |
| PLN-111 | `Scope` names goals, deliverables, exclusions and the agreement or inputs it rests on; it agrees with `scope.processes` and `inputs` of `project.yaml` | read `Scope` next to `project.yaml` | semantic |
| PLN-112 | The life cycle in `Approach` fits the processes in scope and the customer's milestones the inputs name; every phase ends at a milestone | read `Approach` and `milestones` | semantic |
| PLN-113 | Every milestone has a date and a `baseline_purpose` that the configuration management plan defines, or `Criteria` says how it is decided instead | `progress`: no milestone "not assessed"; compare purposes with the configuration management plan | semantic |
| PLN-114 | The estimation method and its unit are stated, and every resource the work needs - people, tools, equipment, samples - with where it comes from and from when | read `Approach`, `Environment and tools` | semantic |
| PLN-115 | Each role has the skills its work needs stated; every gap has a way to close it with a date | read `Responsibilities` | semantic |
| PLN-116 | Every party the project receives from or delivers to is named with what is exchanged; every source under `inputs` appears; every commitment has a date and a state | read `Interfaces and commitments` next to `inputs` | semantic |
| PLN-117 | `Reporting` states cadence, audience, content and the thresholds that call for a corrective action | read `Reporting` | semantic |
| PLN-118 | `Feasibility` lists facts, assumptions and risks, and records the decision with who took it and when | read `Feasibility` | semantic |
| PLN-119 | The decision on feasibility was taken by the person entitled to take it | the plan names who decided; ask the project lead whether that is the person entitled | accountable |
| PLN-120 | The people the plan relies on in `Responsibilities` are assigned to the project for the planned period | ask the project lead | accountable |

## Kind unit-verification (SWE.4.BP1)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-20 | `coverage_targets` is set | `check`: no `COV-28` warning on the plan | script |
| PLN-21 | Every ASIL that occurs among the software units has a target, or the plan gives the reason why not; the metrics chosen (statement, branch, MC/DC) are stated per ASIL, and a higher ASIL does not get a weaker target | compare the keys of `coverage_targets` with `asil` of the `software-unit` items | semantic |
| PLN-22 | Static and dynamic verification are both planned: which analysis, which review and which tests, in which order, for which units | read `Approach` | semantic |
| PLN-23 | Test cases are to be derived from the unit design by named techniques (value classes, boundaries, error returns, states), not from the code, and every designed function that others can call or that is scheduled gets test cases that name it | read `Approach`; `COV-29` later checks the second part | semantic |
| PLN-24 | The rule set of the static analysis and the coding guideline are named, or their absence is declared as a limitation | read `Approach`, `Environment and tools` | semantic |
| PLN-25 | Regression is defined: what is repeated when a unit, something it uses, or its test code changes; at least the runs whose recorded code no longer matches (`COV-30`) and the review of the changed code | read `Approach` | semantic |
| PLN-26 | Generated, reused and third-party units are addressed: which other verification applies to them and where its evidence is | read `Scope`, `Approach`; compare with `origin` of the units | semantic |
| PLN-27 | The exit criteria per unit can be decided from `test-run` and `static-analysis-run` records and from the review record of the code, and say how a coverage gap or an analysis finding is justified, who may accept it, and that the deviation is recorded with the run | read `Criteria` | semantic |
| PLN-28 | What results from the host do not show about the target is stated, together with where that is verified instead | read `Scope`, `Environment and tools` | semantic |
| PLN-29 | Coverage targets and methods per ASIL are accepted by whoever is responsible for functional safety | ask who agreed, and when | accountable |

## Kind software-integration (SWE.5.BP1, SWE.5.BP2)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-38 | `integration_steps` is present; every software component is integrated in exactly one step or named as a double of the last step, and every name in a step is a live component | `check`: no `SCHEMA` finding on the item and no `COV-35` finding | script |
| PLN-30 | The items to be integrated are identified from the software architecture, including reused, supplied and generated ones; a component this project does not integrate is a double of the last step, and `Scope` says who integrates it | compare `Scope` and `integration_steps` with the `software-component` items | semantic |
| PLN-31 | The integration order is given as steps, with what enters each step and what an item must have passed before (for example unit verification); the order follows the dependencies in the architecture, so that each step can be tested with doubles for what is still missing | read `integration_steps`, `Approach`, `Criteria`; compare with the interfaces' `provided_by` and `used_by` | semantic |
| PLN-32 | The test strategy follows the integration order: for each step what is tested and by which method (interface, data flow, timing, resource use) | read `Approach` | semantic |
| PLN-33 | Integration tests are to be derived from the architecture: every `software-interface` and the interplay shown in the `architecture-view` items are to be covered | read `Approach`, `Criteria` | semantic |
| PLN-34 | The environment of each step is named, and what can only be shown on the target is assigned to a step that runs there | read `Environment and tools` | semantic |
| PLN-35 | Regression is defined: what is integrated and tested again when an item changes | read `Approach` | semantic |
| PLN-36 | Exit criteria per step and the handling of a failed test are given | read `Criteria` | semantic |
| PLN-37 | The steps are assigned to releases, and the assignment fits the release plan | ask the project lead | accountable |

## Kind software-qualification-test (SWE.6.BP1)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-40 | The test object and the scope per release are stated: which requirements are tested for which release | read `Scope`; compare with `release` of the requirements | semantic |
| PLN-41 | Test cases are to be derived from the software requirements and their verification criteria, by named test design techniques | read `Approach` | semantic |
| PLN-42 | Requirements whose `verification_method` is not `test` are addressed: how they are verified and where the evidence is recorded | read `Approach`; compare with the requirements | semantic |
| PLN-43 | The environment is named; where a requirement is tested in simulation instead of on the control unit, the reason is given | read `Environment and tools` | semantic |
| PLN-44 | Entry, exit and pass criteria are given, as is the handling of a failed test | read `Criteria` | semantic |
| PLN-45 | Regression is defined: how test cases are selected for a release and what is tested again after a change | read `Approach`, `Criteria` | semantic |
| PLN-46 | The independence of the testers that the project requires is stated and met | read `Responsibilities`; ask who tests | accountable |
| PLN-47 | The test schedule fits the release plan | ask the project lead | accountable |

## Kind system-integration (SYS.4.BP1, SYS.4.BP2)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-50 | The system items to be integrated are identified from the system architecture, with the order of integration and the preconditions of each step | compare `Scope`, `Approach` with the `system-element` items | semantic |
| PLN-51 | The test strategy follows the integration order: test objects per step, methods, and how every `system-interface` is exercised | read `Approach` | semantic |
| PLN-52 | Environment and equipment of each step are named (bench, door on a rig, vehicle) | read `Environment and tools` | semantic |
| PLN-53 | Entry and exit criteria per step and the handling of a failed test are given | read `Criteria` | semantic |
| PLN-54 | Regression is defined: what is tested again when a system item changes | read `Approach` | semantic |
| PLN-55 | The deliveries the steps depend on (hardware samples, mechanical parts, software releases) are agreed with their sources and fit the release plan | ask the project lead | accountable |

## Kind system-qualification-test (SYS.5.BP1)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-60 | The scope per release and the rule for selecting test cases for a release are stated | read `Scope`, `Criteria` | semantic |
| PLN-61 | Test cases are to be derived from the system requirements and their verification criteria; the methods are named | read `Approach` | semantic |
| PLN-62 | Requirements whose `verification_method` is not `test` are addressed | read `Approach`; compare with the requirements | semantic |
| PLN-63 | The environments are named, including what is tested on the vehicle and what on a bench | read `Environment and tools` | semantic |
| PLN-64 | Entry, exit and pass criteria are given, as is the handling of a failed test | read `Criteria` | semantic |
| PLN-65 | Regression is defined: what is tested again on the integrated system when a system item changes | read `Approach` | semantic |
| PLN-66 | The test schedule fits the release plan | ask the project lead | accountable |

## Kind configuration-management (SUP.8.BP1)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-70 | It is stated what is a configuration item (item files, records, code, test code, scripts, configuration, imported inputs) and what is not, with the reason | read `Scope`; compare with the repository | semantic |
| PLN-71 | Identification is defined: how an item, a version of an item and a version of the whole are named; where the product has variants, how items and baselines relate to them | read `Approach`; compare with `schema/item-format.md` | semantic |
| PLN-72 | Repositories, tools and access rights are named: who may change what | read `Environment and tools`, `Responsibilities` | semantic |
| PLN-73 | Branch rules are given: when a branch is created, how it is merged, who reviews the merge, and what must always hold on the main line | read `Approach` | semantic |
| PLN-74 | Baselines are defined: their purposes, when each is drawn, how it is tagged; the purposes that need no communication are those under `trace.internal_baselines` in `project.yaml` | read `Approach`; compare with `project.yaml` | semantic |
| PLN-75 | The criteria a baseline must meet can be decided from `check` and the baseline record | read `Criteria` | semantic |
| PLN-76 | Change control is defined: from which baseline on an item changes only through a change request (a baseline with an internal purpose freezes nothing), in agreement with the change request management plan | read `Approach`; compare the two plans | semantic |
| PLN-77 | Status reporting is defined: what is reported, from which command or record, to whom | read `Approach` | semantic |
| PLN-78 | It is defined how the content of a baseline is verified before a delivery (for example `audit <BL-ID>` at the tagged commit), and how storage, backup, retention and recovery are arranged | read `Criteria`, `Environment and tools` | semantic |
| PLN-79 | Access rights and backup are set up as the plan says | ask the configuration manager | accountable |

## Kind quality-assurance (SUP.1.BP1)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-88 | `quality_checks` and `escalation` are present; every check names its kind and scope, and the baseline purposes under `before` are purposes of the configuration management plan | `check`: no `SCHEMA` finding on the item; compare `before` with the purposes the configuration management plan defines | script |
| PLN-80 | It is stated which work products and which process activities are checked, by which method, and at which events or how often: one entry of `quality_checks` per check | read `quality_checks`, `Scope`, `Approach` | semantic |
| PLN-81 | It is stated who performs the checks and what makes that person independent of the people whose work is checked; conflicts of interest are addressed | read `Approach`, `Responsibilities` | semantic |
| PLN-82 | The criteria are named: which checklist in which version applies to which work product type, and what a process check compares against | compare with `.claude/docs/checklists/` | semantic |
| PLN-83 | The part played by tools and by reviews prepared by a model is stated: their output is input for a person, not an independent check in itself | read `Approach` | semantic |
| PLN-84 | The handling of deviations is defined: how they are recorded, followed until corrected and kept from recurring, and how this connects to problem resolution | read `Approach` | semantic |
| PLN-85 | Reporting is defined: what is reported (results, deviations, trends), to whom and how often | read `Approach` | semantic |
| PLN-86 | An escalation path is defined: when a deviation is escalated, to which level of management, and how the answer is recorded | read `Approach`, `Criteria` | semantic |
| PLN-87 | The person in the quality assurance role has the authority to escalate, and the management named has agreed to respond | ask who agreed, and when | accountable |

## Kind problem-resolution (SUP.9.BP1)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-90 | The activities from recording to closure are described, and the states agree with the `problem-report` lifecycle in `schema/items.yaml` | compare `Approach` with the schema | semantic |
| PLN-91 | The severity classes are defined by criteria and agree with the values of `severity` | read `Criteria`; compare with the schema | semantic |
| PLN-99 | `urgent_severities` and `alerts` are present and name only severities of the schema | `check`: no `SCHEMA` finding on the item and no `COV-39` finding on the plan | script |
| PLN-92 | Urgent cases are covered: `urgent_severities` names the severities that need an immediate decision, `Approach` says who may authorise it, and how fast; it is recorded in `urgent_action` | read `urgent_severities`, `Approach`, `Responsibilities` | semantic |
| PLN-93 | Alert notification is defined: `alerts` names, per severity, the parties to be told and how fast; the parties are those that other software, other systems or other users depend on (customer, suppliers of affected components, safety and security managers) | read `alerts` and `Scope` | semantic |
| PLN-94 | It is defined when a problem leads to a change request and how the two stay linked | read `Approach`; compare with the change request management plan | semantic |
| PLN-95 | The interfaces are named: who may report a problem and who is informed, including customer, suppliers and other users of the same software | read `Scope`, `Responsibilities` | semantic |
| PLN-96 | It is defined how the effect of a resolution is shown before a problem is closed (retest or review) | read `Criteria` | semantic |
| PLN-97 | Trend analysis is defined: what is evaluated, how often, and who acts on the result | read `Approach` | semantic |
| PLN-98 | The parties named as interfaces know the arrangement | ask who was informed, and when | accountable |

## Kind change-request-management (SUP.10.BP1)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-100 | The activities from request to closure are described, and the states agree with the `change-request` lifecycle in `schema/items.yaml` | compare `Approach` with the schema | semantic |
| PLN-101 | The analysis criteria are defined: what an impact analysis has to cover (affected items from `impact`, effort, schedule, risk, regression scope) | read `Criteria` | semantic |
| PLN-102 | The deciding body is defined: who decides, on what basis, and how the decision is recorded in `decision` | read `Approach`, `Responsibilities` | semantic |
| PLN-103 | It is defined how the implementation of a change is confirmed before closure: review of the affected items and a new run of the affected tests | read `Criteria` | semantic |
| PLN-104 | It is defined from when a change needs a change request - from the first baseline that is not internal on - in agreement with the configuration management plan | compare the two plans | semantic |
| PLN-105 | The interfaces are named: who may request a change and who is informed about decision and closure | read `Scope`, `Responsibilities` | semantic |
| PLN-106 | The deciding body exists and its members know their role | ask who the members are | accountable |

## Kind risk-management (MAN.5.BP1, MAN.5.BP2)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-130 | `risk_categories` and `risk_scale` are present, and the scale has `probability_levels`, `impact_levels` and `acceptable_up_to` | `check`: no `SCHEMA` finding on the item | script |
| PLN-131 | The scope names the kinds of risk the project manages and what it leaves to others, and states the organizational risk policy followed, or that none applies | read `Scope`, `risk_categories` | semantic |
| PLN-132 | The ways of finding risks are defined: where they are looked for (plan, design decisions, change requests, problem reports, supplier reviews, status meetings), when, and with which techniques | read `Approach` | semantic |
| PLN-133 | Every level of both scales has a meaning that two people would apply alike (a range, a duration, a consequence), and the number of levels agrees with `risk_scale` | read `Criteria`, `probability_meaning`, `impact_meaning` | semantic |
| PLN-134 | `acceptable_up_to` lies within the range of exposure (probability times impact) the scales allow, and `Criteria` says why that level is acceptable for the project and the organization | compare `risk_scale` with `Criteria` | semantic |
| PLN-135 | The activities from identification to closure are described, and the states agree with the `risk` lifecycle in `schema/items.yaml` | compare `Approach` with the schema | semantic |
| PLN-136 | The treatment options are defined, and it is said when a recovery plan is written and who accepts a risk above the acceptable level | read `Approach`, `Criteria`, `Responsibilities` | semantic |
| PLN-137 | Monitoring is defined: the review rhythm, what an indicator must show, who supplies values, and when an overdue action or an indicator at its threshold counts as treatment not progressing | read `Approach`, `Responsibilities` | semantic |
| PLN-138 | Reporting and escalation are defined: the risk figures in the project status report, which risks go to higher management, to whom and how fast; it agrees with the project plan and the quality assurance escalation path | read `Approach`; compare with the project plan and the quality assurance plan | semantic |
| PLN-139 | The people named as risk owners, acceptors and escalation recipients know the arrangement and have agreed to take the roles | ask who was informed, and when | accountable |

## Kind cybersecurity (21434:6.4.1, 21434:6.4.2, 21434:6.4.3, 21434:6.4.4, 21434:6.4.5, 21434:6.4.6, 21434:15.8)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-140 | `tara_method` and `cybersecurity_activities` are present, and the risk matrix has four values 1 to 5 for every impact level | `check`: no `SCHEMA` finding on the item, no `COV-57` finding on the plan | script |
| PLN-141 | Every subclause of the clauses in `scope.cybersecurity` has an entry with a decision; tailored and not-applicable entries have a rationale | `check`: no `COV-53` finding; `clauses` shows the decision per subclause | script |
| PLN-142 | Each tailored or not-applicable entry says how the objective of the subclause is still reached, or why it does not apply to this item | read `rationale` next to the subclause's objective in `iso-sae-21434/2021/catalog.yaml` | semantic |
| PLN-143 | Each entry names who is responsible, and the work products and dates agree with the work breakdown where MAN.3 is in scope | read next to the work packages | semantic |
| PLN-144 | Reused components, components developed out of context and off-the-shelf components of the architecture are named, with what is analysed or done again for each (entries for 6.4.4 to 6.4.6) | read next to the components of origin reused, supplied or third-party | semantic |
| PLN-145 | The impact categories and their meaning, the feasibility approach and the risk matrix are defined so that two people rate alike; `impact_meaning` and `feasibility_meaning` are filled | read `tara_method` | semantic |
| PLN-146 | The risk matrix rises with impact and with feasibility, and `retain_up_to` says up to which risk value a risk may be retained without a named person accepting it | read `risk_matrix` and `retain_up_to` | semantic |
| PLN-147 | Activities left to the customer or a supplier are the ones the cybersecurity interface agreement assigns to them | read next to the plan of kind cybersecurity-interface-agreement | semantic |
| PLN-148 | Whether a cybersecurity assessment is done, by whom and with which independence is stated, with the reason | read `Approach` and `Responsibilities` | semantic |
| PLN-149 | The person responsible for cybersecurity and the project lead state that the plan is the project's and that its activities are resourced | ask them; the note names who and when | accountable |

## Kind cybersecurity-interface-agreement (21434:7.4.3)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-150 | `shared_activities` is present; each entry names the activity and the role of customer and supplier | `check`: no `SCHEMA` finding on the item | script |
| PLN-151 | Every activity of the cybersecurity plan decided by-customer or by-supplier appears, and each activity has exactly one side that performs it | read next to `cybersecurity_activities` | semantic |
| PLN-152 | What is exchanged, in which form and when is said for each activity that needs input from the other side, including vulnerabilities and incidents | read `exchange` and `Approach` | semantic |
| PLN-153 | Both parties have agreed to the arrangement, as a communication record with `agreement` shows | read the communication record; the note names who agreed and when | accountable |

## Kind cybersecurity-monitoring (21434:8.3)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-154 | `monitoring_sources` and `triggers` are present | `check`: no `SCHEMA` finding on the item | script |
| PLN-155 | The sources cover the components of the item that come from outside (origin supplied, third-party, reused) and the item's own field and test data | read next to the components | semantic |
| PLN-156 | Each trigger can be decided from the collected information without interpretation, and says what follows | read `triggers` | semantic |
| PLN-157 | The rhythm of collection and triage, who triages and how a cybersecurity event becomes a weakness item are defined | read `Approach` and `Responsibilities` | semantic |

## Kind cybersecurity-incident-response (21434:13.3)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-158 | The plan says who is told of an incident, how fast, who decides the remedy, how progress is followed and when an incident is closed | read `Approach`, `Criteria`, `Responsibilities` | semantic |
| PLN-159 | It agrees with the escalation of the problem resolution strategy and with the interface agreement | read next to those plans | semantic |

## Kind production-control (21434:12, 26262-7:6)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-160 | The plan names each cybersecurity requirement for post-development and the production step that puts it in place (keys, configuration, locks of debug access) and how that is checked | read next to the requirements marked for post-development | semantic |
| PLN-161 | Protection of the production equipment and the data it handles is stated | read `Approach`, `Environment and tools` | semantic |

## Kind end-of-cybersecurity-support (21434:14.3)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-162 | The procedure says how and when customers learn that cybersecurity support ends, and what happens to open vulnerabilities | read `Approach` | semantic |

## Kind safety (26262-2:6, 26262-4:5, 26262-5:5, 26262-6:5)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-163 | `safety_activities`, `method_selection` and `confirmation_measures` are present | `check`: no `SCHEMA` finding on the item | script |
| PLN-164 | Every clause of the parts in `scope.safety` has an entry with a decision; tailored and not-applicable entries have a rationale | `check`: no `COV-63` finding; `safety` shows the decision per clause | script |
| PLN-165 | Every table of parts 4, 5, 6 and 8 in scope has an entry; applied entries say which methods or where they are written; not-applicable entries have a rationale | `check`: no `COV-64` finding | script |
| PLN-166 | Each tailored or not-applicable clause says how its purpose is still reached or why it does not apply to this item | read `rationale` next to the clause's purpose in `iso-26262/2018/catalog.yaml` | semantic |
| PLN-167 | `Scope` holds the impact analysis: what is new, changed or reused, and what follows for the activities | read `Scope` | semantic |
| PLN-168 | The methods named per table agree with the strategies that apply them (unit verification, integration, qualification, coding guideline) | read `method_selection` next to those plans | semantic |
| PLN-169 | Where the plan states an ASIL or tool confidence determination, the safety manager states that it is the one of the standard. A determination not stated yet is no finding: `check` then reports the ASILs or confidence levels as not assessed, and the plan says when it will be stated | ask; the note names who and when; `not-applicable` while none is stated | accountable |
| PLN-170 | The confirmation measures cover the work products and the audit and assessment the ASIL calls for, each with the independence the responsible people read from the standard, and name who performs them | read `confirmation_measures` | semantic |
| PLN-171 | Activities left to the customer or a supplier are those the development interface agreement assigns to them | read next to the agreement | semantic |
| PLN-172 | The safety manager and the project lead state that the plan is the project's and that its activities are resourced | ask them; the note names who and when | accountable |

## Kind development-interface-agreement (26262-8:5)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-173 | `shared_activities` is present; each entry names the activity and the role of customer and supplier | `check`: no `SCHEMA` finding on the item | script |
| PLN-174 | Every clause of the safety plan decided by-customer or by-supplier appears, and each activity has exactly one side that performs it | read next to `safety_activities` | semantic |
| PLN-175 | What is exchanged, when, and how problems and changes of safety requirements reach the other side is stated | read `exchange` and `Approach` | semantic |
| PLN-176 | Both parties have agreed to the arrangement, as a communication record with `agreement` shows | read the communication record; the note names who agreed and when | accountable |

## Kind release (SPL.2.BP1, SPL.2.BP2, SPL.2.BP3, SPL.2.BP4, SPL.2.BP6, SPL.2.BP7, SPL.2.BP8)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-177 | The content of each planned release is named, with the milestone or order it serves | read `Scope` next to the project plan | semantic |
| PLN-178 | Classification and numbering are defined, and the numbering agrees with the baseline tags | read `Approach` next to the configuration management plan | semantic |
| PLN-179 | The build of a release and its environment are named, and the build comes from configured items | read `Environment and tools` | semantic |
| PLN-180 | Support, media and packaging are stated per classification | read `Approach`, `Environment and tools` | semantic |
| PLN-181 | Who approves a release and how the receipt is confirmed is stated, and the people named agree | ask them; the note names who and when | accountable |

## Kind operation-and-service (26262-7:5, 26262-7:7)

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-182 | The plan says what keeps the safety-related properties in operation, service and decommissioning: instructions for users and workshops, field monitoring of safety-related events, and how they reach problem resolution | read `Approach` | semantic |
| PLN-183 | It agrees with what the safety concept requires of production, operation, service and decommissioning | read next to those requirements | semantic |
