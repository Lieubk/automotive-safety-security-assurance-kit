# The project plan

One `plan` item of kind `project` per project, in `plans/`. Its type is defined in
`schema/items.yaml`; the sections `Feasibility`, `Interfaces and commitments` and
`Reporting` and the attribute `milestones` are mandatory for this kind before review.
It is reviewed with `.claude/docs/checklists/plan.md`, parts "Every plan" and "Kind
project".

The example is the plan the worked example in `examples/power-window/` could have. It
names roles, not people; a real plan names who holds each role where the user states it.

```markdown
---
id: PLN-0003
type: plan
title: Project plan - power window software R1.0
status: draft
kind: project
milestones:
  - {name: Requirements agreed, date: "2026-03-20", baseline_purpose: requirements freeze, release: R1.0}
  - {name: Design frozen, date: "2026-04-17", baseline_purpose: design freeze, release: R1.0}
  - {name: Release candidate, date: "2026-06-12", baseline_purpose: release candidate, release: R1.0}
  - {name: Delivery to the customer, date: "2026-06-26", baseline_purpose: delivery, release: R1.0}
---

## Scope

Goal: software of the window lifter with anti-pinch protection for the front doors, as
the customer's system requirements 2.1 and system architecture 1.4 ask (see `inputs`).
Delivered: the software as C sources with its component descriptions, unit verification
evidence, the baselines and their notices. Not part of it: integration into the door
module software, integration and qualification tests on the target (customer), the
door module hardware, calibration.

## Approach

Life cycle: one release, R1.0, in four phases - requirements, design, implementation
with unit verification, release - each closed by the baseline in `milestones`. Changes
after a baseline go through change requests. Effort is estimated in person-days per
work package by the owner with the software lead, from the size of the deliverables
and from the actual effort of finished packages.

## Criteria

A milestone is reached when its baseline is recorded and communicated. The plan is
revised when a milestone is at risk by more than one reporting period, when the scope
changes, or when a resource is lost.

## Environment and tools

Git repository, the toolkit's trace engine and record tool, gcc and gcov on the host,
the static analyser of the compiler. Hardware samples are not needed: no target test.

## Responsibilities

| Role | Work | Skills needed | Gap and how it is closed |
|---|---|---|---|
| Project lead | plan, status, corrective actions | project management | none |
| Software lead | architecture, reviews, technical risks | AUTOSAR Classic, ISO 26262 at ASIL B | none |
| Software developer | design, code, unit tests | C99, the coding guideline | coding guideline training, by 2026-03-31 |
| Configuration manager | baselines, change requests | the configuration management plan | none |

## Feasibility

Facts: four milestones over 17 weeks, two developers at full time, estimate 64
person-days in the work packages. Assumptions: the customer answers queries within one
week; system requirements 2.1 stay stable until the design freeze. Risks: anti-pinch
thresholds may need tuning on the vehicle. Decision: feasible, on condition that the
customer confirms the system requirements by 2026-03-20 - decided by the project lead
on 2026-03-04.

## Interfaces and commitments

| Party | Exchanged | Contact role | Commitment | Date | State |
|---|---|---|---|---|---|
| Customer system engineering | system requirements and architecture to us; baselines and notices from us | system engineer | answers to queries within one week | ongoing | agreed |
| Customer integration | software and component descriptions from us | integrator | delivery of R1.0 | 2026-06-26 | agreed |

## Reporting

Every two weeks a status report to the software lead and the customer's project lead,
written with `/project-status`. A corrective action is decided when a package is late
by more than two weeks, when actual effort exceeds the estimate by more than 25 %, or
when a milestone is at risk.
```

## Questions per part

| Part | Ask | Do not |
|---|---|---|
| Scope | goals; why; deliverables; exclusions; which agreement or inputs it rests on | widen the scope beyond `scope.processes` without saying so |
| Approach | phases or releases; how a phase ends; how effort is estimated and by whom | choose a method for the user |
| Milestones | name, date, release; which baseline purpose marks it | invent a date or a purpose the configuration management plan does not have |
| Environment and tools | tools, licences, test equipment, samples; from where, from when | list tools the project does not have |
| Responsibilities | roles; what each needs to know; gaps and how they close | judge a person |
| Feasibility | facts, assumptions, risks; who decides; the decision and its date | decide, or soften a "not feasible" |
| Interfaces and commitments | every party in `inputs` and beyond; what goes each way; commitments with date and state | mark a commitment agreed that the user calls open |
| Reporting | cadence, audience, content, thresholds | set thresholds the user has not stated |

## What other skills read from the plan

- `/work-breakdown`: milestones and their dates, the estimation method, the roles.
- `/project-status`: cadence, audience and thresholds under `Reporting`.
- `traceability.py progress`: `milestones` with `date` and `baseline_purpose`; a
  milestone is reached when a final baseline record with that purpose exists.
