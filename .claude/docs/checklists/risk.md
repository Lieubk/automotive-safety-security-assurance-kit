# Risk check list

Version 1. Applies to: `risk`. Supports: MAN.5.BP3, MAN.5.BP4, MAN.5.BP5, MAN.5.BP6,
MAN.5.BP7.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the result stays open until the fact exists.

A risk is not approved through `/review`; it moves through its states with the user. This
list is used by `/risk-management`, by the quality assurance checks and by a process gate
at the reviews of the register. Apply it to the risks that changed, or to all of them,
together with the approved risk management plan: its categories, scales and acceptable
level are the measure. `risks` means `python tools/traceability.py risks`; `check` means
`python tools/traceability.py check --all`.

## Each risk

| ID | Check | How to check | Kind |
|---|---|---|---|
| RSK-01 | Mandatory attributes and sections for its state are present, dates are dates | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| RSK-02 | `category` is one of the categories of the plan, and `probability` and `impact` lie within its scales | `check`: no `COV-50` finding on the item | script |
| RSK-03 | A risk above the acceptable level is in treatment, closed, or accepted with a decision that names who accepted it | `check`: no `COV-51` finding on the item; `risks` shows exposure and state | script |
| RSK-04 | A risk in treatment has an indicator with a threshold | `check`: no `COV-52` finding on the item | script |
| RSK-05 | `Description` states cause, event and consequence in separate statements, and one event | read `Description` | semantic |
| RSK-06 | `identified_in` names a real source in the project (a plan, decision, change request, problem, supplier review or meeting) and the source shows the risk | `show` the source; read | semantic |
| RSK-07 | `Analysis` gives a reason for the probability and for the impact in the terms of the plan's scale, from facts in the project rather than the level alone | read `Analysis` next to `risk_scale` of the plan | semantic |
| RSK-08 | The treatment acts on the cause or the consequence named in `Description`, not only on a symptom, and fits the chosen option | read `treatment` next to `Description` | semantic |
| RSK-09 | Every treatment action can be carried out and checked, and has an owner and a due date; done actions have `done_on` | read `treatment`; `risks` lists open and overdue actions | semantic |
| RSK-10 | Each indicator can show a change of this risk or the progress of its treatment, and its threshold lies before the point at which the consequence occurs | read `indicators` next to `Description` | semantic |
| RSK-11 | Indicator values are current: `as_of` lies within the review rhythm of the plan, and none has reached its threshold without a reaction | `risks`: indicators at threshold; compare `as_of` with `Approach` of the plan | script |
| RSK-12 | Where treatment is overdue or an indicator reached its threshold, a corrective action addresses the risk | `risks`: corrective actions per risk | script |
| RSK-13 | The risk does not duplicate or overlap another risk of the register | read the register next to the risk | semantic |
| RSK-14 | A closed risk says why it cannot occur or how it was handled; a rejected one says why it is not a risk of the project | read `Treatment and monitoring` or `Description` | semantic |
| RSK-15 | The owner states that the risk, its rating and its treatment are as recorded | ask the owner; the note names who and when | accountable |
| RSK-16 | The person named in `decision` states that they accepted the risk, on the grounds written there | ask that person; the note names who and when | accountable |

## The register

| ID | Check | How to check | Kind |
|---|---|---|---|
| RSK-30 | An approved risk management plan exists | `check`: no `COV-27` finding for kind `risk-management` | script |
| RSK-31 | Risks were added and re-rated during the project, not only at its start | `history` of the risk items; compare dates with the milestones of the plan | script |
| RSK-32 | Risks from the sources the plan names are covered: open problems, change requests, late packages and open design decisions each have a risk, or a stated reason that they need none | `status`, `problems`, `progress`; read the register against them | semantic |
| RSK-33 | The ranking by exposure is the order in which treatment effort goes: no risk above the others' exposure waits without treatment | `risks`: list by exposure with state | script |
| RSK-34 | The risk figures were reported in the latest status report, and the risks the plan says to escalate were passed on | read the project status report; `risks` | semantic |
| RSK-35 | The project lead states that the register is the project's list of risks and that its treatment is resourced | ask the project lead; the note names who and when | accountable |
