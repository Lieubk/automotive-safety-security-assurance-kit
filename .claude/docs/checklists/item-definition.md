# Item definition review checklist

Version 1. Applies to: `item-definition`. Supports: 21434:9.3.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

The item definition is what the TARA analyses. Where the system architecture exists
(SYS.3), the review record lists its elements and interfaces under `references`.
`check` means `python tools/traceability.py check --all`.

| ID | Check | How to check | Kind |
|---|---|---|---|
| ITEM-01 | Mandatory sections for the state are present | `check`: no `SCHEMA` finding on the item | script |
| ITEM-02 | `Boundary and functions` says what belongs to the item and what lies outside, and lists its functions | read | semantic |
| ITEM-03 | `Preliminary architecture` names the elements and every interface that crosses the boundary, and agrees with the system architecture where one exists | read next to the system elements and interfaces | semantic |
| ITEM-04 | `Operational environment` describes what surrounds the item in use - networks, connected units, users, workshops, the backend - as far as it matters for cybersecurity | read | semantic |
| ITEM-05 | Assumptions about the environment are stated as such, so that they can become requirements on the operational environment or claims | read `Assumptions` | semantic |
| ITEM-06 | Whoever is responsible for the item at the customer or in the project states that the boundary and the functions are those of the item | ask that person; the note names who and when | accountable |
