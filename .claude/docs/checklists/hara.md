# Hazard analysis and risk assessment review checklist

Version 1. Applies to: `hazardous-event`, `safety-goal`. Supports: 26262-3:6 (the review is
the verification report 26262-3:6.5.2).

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

Review the hazardous events and safety goals of one item definition together; the
review record lists the item definition and the safety plan under `references`. `check`
means `python tools/traceability.py check --all`. Checks of a part that has no item of
its type in the review are `not-applicable`.

## Hazardous events

| ID | Check | How to check | Kind |
|---|---|---|---|
| HARA-01 | Mandatory attributes and sections are present; the event arises in the item definition | `check`: no `SCHEMA` or `LINK` finding on the item | script |
| HARA-02 | The ASIL is the one the plan's determination gives for its severity, exposure and controllability | `check`: no `COV-65` finding; a warning that ASILs are not assessed means the plan states no determination | script |
| HARA-03 | An event of ASIL A to D is addressed by a safety goal of at least its ASIL | `check`: no `COV-66` finding | script |
| HARA-04 | The malfunctions cover the functions of the item definition with the guide words the plan names, and an omission has a reason | read the events per function next to the item definition | semantic |
| HARA-05 | The operational situations are those of the vehicle's use - including workshop, parking, misuse that can be foreseen - and each event names one | read `operational_situation` | semantic |
| HARA-06 | `Classification rationale` gives a reason for each rating: who is harmed and how, how often the situation occurs and from which source, who could avoid the harm and how | read | semantic |
| HARA-07 | The hazard is described at vehicle level, not as a fault of a part | read `hazard` and `Description` | semantic |
| HARA-08 | The people the safety plan names state that the ratings are theirs | ask them; the note names who and when | accountable |

## Safety goals

| ID | Check | How to check | Kind |
|---|---|---|---|
| HARA-20 | Mandatory attributes and sections are present; the goal addresses at least one event | `check`: no `SCHEMA` or `LINK` finding on the item | script |
| HARA-21 | Its ASIL is not lower than that of any event it addresses | `check`: no `COV-66` finding on the goal | script |
| HARA-22 | `Statement` says what must not happen at vehicle level, without a solution | read `Statement` | semantic |
| HARA-23 | A safe state and a fault tolerant time interval are given where the events need them, and they are reachable in the situations of the events | read next to the events | semantic |
| HARA-24 | Goals that share events or a safe state are consistent, and no event is left with a goal that does not fit it | read the set of goals | semantic |
| HARA-25 | The safety manager states that the goals are complete for the item | ask; the note names who and when | accountable |
