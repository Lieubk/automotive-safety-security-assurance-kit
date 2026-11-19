# Cybersecurity goal review checklist

Version 1. Applies to: `cybersecurity-goal`, `cybersecurity-claim`. Supports: 21434:9.4
(verification of goals and claims, WP-09-05), 21434:9.5 (the goals the concept refines).

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

Review goals and claims together with the threat scenarios they address; the review
record lists the threat scenarios under `references`. `check` means
`python tools/traceability.py check --all`. Checks of a part that has no item of its type
in the review are `not-applicable`.

## Cybersecurity goals

| ID | Check | How to check | Kind |
|---|---|---|---|
| GOAL-01 | Mandatory attributes and sections are present; it addresses at least one threat scenario | `check`: no `SCHEMA` or `LINK` finding on the item | script |
| GOAL-02 | Every threat scenario whose treatment includes reduce is addressed by a goal | `check`: no `COV-58` finding on the threat scenarios | script |
| GOAL-03 | `Statement` says which property of which asset is protected against which threat, as a requirement at the level of the item, not as a solution | read `Statement` next to the threat scenarios | semantic |
| GOAL-04 | Achieving the goal reduces the risk of every threat scenario it addresses; a goal that addresses several scenarios fits each of them | read next to the threat scenarios | semantic |
| GOAL-05 | Goals do not contradict each other or a claim | read the set of goals and claims | semantic |
| GOAL-06 | `cal`, where the project uses it, follows the rule of the cybersecurity plan for the risk it addresses | read next to the plan's `Approach` | semantic |
| GOAL-07 | The goal is refined into requirements (once the concept exists): at least one system or software requirement is derived from it | `check`: no `COV-59` finding | script |

## Cybersecurity claims

| ID | Check | How to check | Kind |
|---|---|---|---|
| GOAL-10 | Mandatory attributes and sections for the state are present; it addresses at least one threat scenario or weakness | `check`: no `SCHEMA` or `LINK` finding on the item | script |
| GOAL-11 | Every threat scenario whose treatment includes share or retain is addressed by a claim | `check`: no `COV-58` finding on the threat scenarios | script |
| GOAL-12 | `Claim` states what is argued - who carries a shared risk, or why a retained risk is acceptable - and `Rationale` gives the facts it rests on | read `Claim` and `Rationale` | semantic |
| GOAL-13 | `monitored_by` names how the claim is watched, and that monitoring exists in the cybersecurity-monitoring plan where clause 8 is in scope | read next to that plan | semantic |
| GOAL-14 | A shared risk is accepted by the party that takes it, as recorded in the cybersecurity interface agreement or a communication record that names the agreement | read the agreement; the note names the record | accountable |
| GOAL-15 | The person responsible for cybersecurity states that the goals and claims are the project's | ask that person; the note names who and when | accountable |
