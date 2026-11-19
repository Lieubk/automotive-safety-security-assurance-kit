# Supplier agreement review checklist

Version 1. Applies to: `supplier-agreement`. Supports: ACQ.4.BP1.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

Review each agreement together with the architecture items its `components` name, the
project plan, and the other plans of the project (quality assurance, configuration
management, change requests, problem resolution). `check` means `python
tools/traceability.py check --all`. The agreement is the project's record of what was
negotiated; the review does not judge the commercial terms.

## Each agreement

| ID | Check | How to check | Kind |
|---|---|---|---|
| SAG-01 | Mandatory attributes and sections for its state are present, values are allowed, dates are dates | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| SAG-02 | `supplier` names the supplier and the contract or order the agreement belongs to | read the attribute | semantic |
| SAG-03 | Every ID under `components` exists and is a software component or system element; what the supplier delivers is clear from them | `check`: no `LINK` finding; `show` each ID | script |
| SAG-04 | `Joint processes` says which processes each side performs and where they meet; the processes the supplier's deliveries touch are covered: requirements and change handling, quality assurance, configuration management, problem resolution, acceptance | read the section next to `scope.processes` and the plans | semantic |
| SAG-05 | The joint processes agree with the project's own: the change, problem and acceptance routes named here are the ones of the approved plans | compare the section with the plans | semantic |
| SAG-06 | `Interfaces and responsibilities` names, for each interface, who defines it, who may change it and who verifies each side; none is left without a responsible party | read the section next to the interfaces of the components | semantic |
| SAG-07 | Every work product the project needs from the supplier appears under `exchanges` with direction, content, due date or rhythm and format; every one the supplier needs from the project also appears | compare `exchanges` with `components` and the interfaces | semantic |
| SAG-08 | Each exchange can be told from another and has a measurable due: a date or a rhythm, not "as needed" | read `exchanges` | semantic |
| SAG-09 | `meetings` names at least one technical and one progress meeting, each with a cadence, or the agreement says why one kind is not agreed | read `meetings` and `Joint processes` | semantic |
| SAG-10 | A fixed cadence is given as a number of days, so that a missed meeting can be shown | read `cadence` of each meeting | semantic |
| SAG-11 | Participants of each meeting are named by role or person on both sides and include someone able to decide | read `participants` | semantic |
| SAG-12 | `Deviations and escalation` states what counts as a deviation, who is told, what is done, who escalates to whom, and how a changed objective is written into the agreement | read the section | semantic |
| SAG-13 | The agreement contains no statement that is only the project's wish: where a term is not agreed, it is marked as open or the item stays in draft | read the sections for "should" and "will" without a named party | semantic |
| SAG-14 | There is no other agreement for the same supplier and contract that overlaps in components or exchanges | `list --type supplier-agreement`; compare `supplier` and `components` | script |

## The people

| ID | Check | How to check | Kind |
|---|---|---|---|
| SAG-90 | The terms in the item are the terms negotiated with the supplier | ask the person who negotiated them; the note names who and when | accountable |
| SAG-91 | The supplier has seen this text and agrees to it, or the agreement says what is still open | ask the person who talked to the supplier; the note names who, when and in what form | accountable |
| SAG-92 | The project lead takes the responsibilities and meetings of the project side on | ask the project lead; the note names who and when | accountable |
