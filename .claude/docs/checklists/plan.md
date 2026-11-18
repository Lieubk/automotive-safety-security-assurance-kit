# Plan review checklist

Version 1. Applies to: `plan`. Supports: SWE.4.BP1, SWE.5.BP1, SWE.5.BP2, SWE.6.BP1,
SYS.4.BP1, SYS.4.BP2, SYS.5.BP1, SUP.1.BP1, SUP.8.BP1, SUP.9.BP1, SUP.10.BP1.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

A plan says how a process is going to be performed in this project. Apply the part
"Every plan" to each plan, then the part for its `kind`. The parts follow `plan_kinds`
in `schema/items.yaml`. A kind whose process is not in `scope.processes` needs no plan.

## Every plan

| ID | Check | How to check | Kind |
|---|---|---|---|
| PLN-01 | Mandatory attributes and sections for its state are present, and `kind` is an allowed value | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| PLN-02 | The kind answers a strategy practice of a process in scope, and no second live plan of the same kind exists | Grep `^kind:` in the `plans` folder; compare with `plan_kinds` in `schema/items.yaml` and `scope.processes` in `project.yaml` | script |
| PLN-03 | `Scope` says what the plan covers, what it leaves out, and who covers what is left out; nothing the process needs falls between two plans | read `Scope`; compare with the other plans | semantic |
| PLN-04 | The plan is written for this project: it names the item types, units, tools and environments actually in use, and would not fit an arbitrary project unchanged | read the plan against `status` and the items it refers to | semantic |
| PLN-05 | `Approach` names the methods, their order and what triggers each activity; someone new to the project could work by it | read `Approach` | semantic |
| PLN-06 | Where the rigour depends on ASIL, the plan says how, for every ASIL that occurs in the project | compare `Approach` and `Criteria` with the `asil` values in use | semantic |
| PLN-07 | Every criterion in `Criteria` can be decided as met or not met from a record or a tool output the project produces | read `Criteria`; name the record for each criterion | semantic |
| PLN-08 | The plan agrees with the other plans and with `project.yaml`: same terms, roles, tools, states and baseline purposes; no rule that another plan contradicts | read the plans side by side | semantic |
| PLN-09 | `Environment and tools` names each tool with its use and with where its version is recorded; the limits of tools and environment are stated | read the section | semantic |
| PLN-10 | `Responsibilities` gives, per activity, the role that performs it and the role that checks or approves it; where independence is needed, it is stated | read the section | semantic |
| PLN-11 | What the plan deliberately does not do is declared together with its consequence, not left out silently | read `Scope` and `Approach` for declared limitations | semantic |
| PLN-12 | The plan says which events lead to its update (a new release, a change of scope, of tools or of ASIL) | read the plan | semantic |
| PLN-13 | The people who work by the plan know it and consider it workable | ask who was informed, how, and whether objections remain | accountable |
| PLN-14 | The plan fits the project schedule and the release plan, and the people, tools and equipment it relies on are available | ask the project lead | accountable |
| PLN-15 | The roles named in `Responsibilities` are filled | ask who holds each role | accountable |

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
| PLN-30 | The items to be integrated are identified from the software architecture, including reused, supplied and generated ones | compare `Scope` with the `software-component` items | semantic |
| PLN-31 | The integration order is given as steps, with what enters each step and what an item must have passed before (for example unit verification) | read `Approach`, `Criteria` | semantic |
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
| PLN-80 | It is stated which work products and which process activities are checked, by which method, and at which events or how often | read `Scope`, `Approach` | semantic |
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
| PLN-92 | Urgent cases are covered: who may authorise an immediate action and how it is recorded in `urgent_action` | read `Approach`, `Responsibilities` | semantic |
| PLN-93 | Alert notification is defined: which problems are made known to whom, and how fast | read `Approach` | semantic |
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
