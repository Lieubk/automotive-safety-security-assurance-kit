# Risk management plan

File: `plans/<ID>.md`. Type `plan`, `kind: risk-management`. It answers MAN.5.BP1 and
MAN.5.BP2; the trace check reports `COV-27` until it is approved, and `COV-50` reads
`risk_categories` and `risk_scale` from it. Both attributes are mandatory before review.

## Decisions to ask the user before drafting

| Decision | Typical options | Lands in |
|---|---|---|
| Organizational risk policy | none; a policy of the organization that sets scales or thresholds - name it and follow it | `Scope` |
| Which kinds of risk the project manages | technical, schedule, cost, supplier, resources, safety and security, commercial; what is left to the customer or the organization | `risk_categories`, `Scope` |
| Where risks are looked for, and when | at the plan; at each design decision, change request, problem report, supplier review and status meeting; each analysis technique the project uses (FMEA, FTA, simulation) | `Approach` |
| Rating scales | levels of probability and of impact (for example 4 each), and what each level means in this project: probabilities as ranges of likelihood, impacts as days of delay, cost, loss of a feature or a safety effect | `risk_scale` (`probability_levels`, `impact_levels`, `probability_meaning`, `impact_meaning`), `Criteria` |
| Acceptable level | the exposure (probability times impact) up to which no treatment is needed, `acceptable_up_to`; the project's and, if different, the organization's | `risk_scale`, `Criteria` |
| Who accepts a risk above the level | the project lead; the customer or management for a defined class of risks | `Criteria`, `Responsibilities` |
| Treatment options and recovery | avoid, reduce probability, reduce impact, transfer, accept; whether a recovery plan is written for the high risks | `Approach` |
| Monitoring | how often the register is reviewed; what an indicator has to show; who supplies values | `Approach`, `Responsibilities` |
| Reporting and escalation | the risk figures in each status report; the exposure or class that is reported to higher management, to whom and how fast | `Approach`, `Criteria` |
| Corrective action | when treatment counts as not progressing (an overdue action, an indicator at its threshold); who decides | `Approach`, `Responsibilities` |

## Template

The values are invented, in the power window domain.

```markdown
---
id: PLN-0008
type: plan
title: Risk management plan
status: draft
kind: risk-management
risk_categories: [technical, schedule, supplier, safety]
risk_scale:
  probability_levels: 4
  impact_levels: 4
  acceptable_up_to: 4
  probability_meaning: {1: "below 10 percent", 2: "10 to 30 percent", 3: "30 to 60 percent", 4: "above 60 percent"}
  impact_meaning: {1: "under 2 days of delay", 2: "2 to 10 days", 3: "a milestone missed", 4: "a requirement not met or a safety goal affected"}
---

## Scope
The kinds of risk managed and why; what is left to the customer or the organization;
the organizational risk policy followed, if any.

## Approach
Where risks are looked for and when; how a risk is rated, treated, monitored and closed;
the states of the schema (identified, analysed, in-treatment, closed, accepted,
rejected) and what each one needs; the review rhythm; reporting and escalation; when
treatment counts as stalled and a corrective action is raised.

## Criteria
The meaning of each scale level; exposure is probability times impact; the acceptable
level; who may accept a risk above it; the exposure or class that is escalated.

## Environment and tools
Risks as items in `records/risks/`; `traceability.py risks`; the risk figures in the
project status report; the analysis techniques used.

## Responsibilities
Who identifies, who owns a risk, who rates, who accepts, who supplies indicator
values, who decides corrective actions, who escalates.
```

Write each section out for the project; the example is a model, not a form.

## Notes

- Scale values are whole numbers from 1 to the number of levels. Exposure is their
  product; `acceptable_up_to` is a number in that range.
- A category a risk uses must be one of `risk_categories`: a new kind of risk first
  changes the plan, and the plan is reviewed again.
- A change of a scale or of the threshold makes ratings already given suspect: say which
  risks it touches (`risks`) and have their owners confirm or re-rate them.
