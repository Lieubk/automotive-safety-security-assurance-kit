# TARA review checklist

Version 1. Applies to: `asset`, `damage-scenario`, `threat-scenario`. Supports:
21434:15.3, 21434:15.4, 21434:15.5, 21434:15.6, 21434:15.7, 21434:15.8, 21434:15.9,
21434:9.4 (verification of the TARA that the goals rest on, WP-09-05).

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

The measure is the approved cybersecurity plan: its `tara_method` (impact categories,
feasibility approach, risk matrix, `retain_up_to`). Review the assets, damage scenarios and
threat scenarios of one item definition together; the review record lists the item
definition and the plan under `references`. `check` means
`python tools/traceability.py check --all`; `tara` means `python tools/traceability.py tara`.
Checks of a part that has no item of its type in the review are `not-applicable`.

## Assets

| ID | Check | How to check | Kind |
|---|---|---|---|
| TARA-01 | Mandatory attributes and sections are present, `properties` uses only the listed properties | `check`: no `SCHEMA` or `LINK` finding on the item | script |
| TARA-02 | Every asset is threatened by at least one threat scenario | `check`: no `COV-54` finding on the asset | script |
| TARA-03 | The assets cover what the item definition holds, processes or carries that has value: data and commands on its interfaces, stored data and keys, software and its configuration, functions whose loss harms someone | read the assets next to the item definition and its interfaces | semantic |
| TARA-04 | Each asset names the properties whose loss leads to damage, and no property that cannot | read `properties` next to the damage scenarios | semantic |
| TARA-05 | `located_in` names where the asset lives, so that a change there makes the asset suspect | `show` the asset; read | semantic |

## Damage scenarios

| ID | Check | How to check | Kind |
|---|---|---|---|
| TARA-10 | Every category of the plan is rated with severe, major, moderate or negligible, and no other category | `check`: no `COV-55` finding | script |
| TARA-11 | Every damage scenario is reached by at least one threat scenario | `check`: no `COV-54` finding on it | script |
| TARA-12 | `Description` states a consequence for road users, not a technical event, and how it comes about | read `Description` | semantic |
| TARA-13 | `Impact rationale` gives a reason per rating in the terms of `impact_meaning` of the plan | read next to the plan | semantic |
| TARA-14 | Where ISO 26262 applies, the safety rating agrees with the severity of the matching hazard, and the person responsible for functional safety states that it does | ask that person; the note names who and when | accountable |

## Threat scenarios

| ID | Check | How to check | Kind |
|---|---|---|---|
| TARA-20 | It threatens an asset, leads to a damage scenario, and its property is one of the asset's | `check`: no `COV-56` finding | script |
| TARA-21 | It has attack paths, each rated, and its `feasibility` is the highest of them | `check`: no `COV-56` finding | script |
| TARA-22 | Its `risk_value` is the value of the plan's risk matrix for the highest impact it leads to and its feasibility | `check`: no `COV-57` finding; `tara` shows stated and matrix value | script |
| TARA-23 | Its treatment is decided; reduce is addressed by a cybersecurity goal, share and retain by a claim; a retained risk above `retain_up_to` names who accepted it | `check`: no `COV-58` finding | script |
| TARA-24 | `Description` names the attacker's aim, the asset, the property lost and the cause, as one scenario | read `Description` | semantic |
| TARA-25 | The threat scenarios cover the assets systematically: for each asset and property, the ways it can be lost were considered (for example with a threat model the plan names), and an omission has a reason | read the scenarios per asset next to the plan's `Approach` | semantic |
| TARA-26 | Each attack path runs from an entry point of the item definition to the asset, step by step, and is possible in the operational environment described | read `attack_paths` next to the item definition | semantic |
| TARA-27 | The feasibility ratings follow the approach of the plan, and the `factors` justify each rating | read `attack_paths` next to `feasibility_meaning` of the plan | semantic |
| TARA-28 | `Treatment rationale` explains the decision for the risk value, and a claim or goal is named for it | read next to `treatment` | semantic |
| TARA-29 | The person responsible for cybersecurity states that the ratings and the treatment decisions are the project's | ask that person; the note names who and when | accountable |
