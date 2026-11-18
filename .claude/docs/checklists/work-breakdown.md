# Work breakdown review checklist

Version 1. Applies to: `work-package`. Supports: MAN.3.BP4, MAN.3.BP5, MAN.3.BP8,
MAN.3.BP9.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

Review the work packages of a release, or the ones that changed, together with the
approved project plan: its milestones, estimation method, roles, commitments and
reporting cadence are the measure. `progress` means `python tools/traceability.py
progress`; `check` means `python tools/traceability.py check --all`. What a package has
delivered so far (`delivers`) and the owner's statements (`progress`) are tracking: they
are read, not reviewed.

## Each work package

| ID | Check | How to check | Kind |
|---|---|---|---|
| WBS-01 | Mandatory attributes and sections for its state are present, dates are dates | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| WBS-02 | `Description` says what the work is and where it ends; `Deliverables` names concrete outputs, also those that do not exist yet | read both sections | semantic |
| WBS-03 | Its state can change within one reporting period of the plan; a larger package is split | compare its duration with `Reporting` of the plan | semantic |
| WBS-04 | `Estimate basis` applies the method of the plan and names the figures it rests on; where finished packages of the same kind exist, it says how their actual effort was used | read the section next to `Approach` of the plan and `progress` | semantic |
| WBS-05 | The activities cover what the deliverables need in this toolkit: drafting, review, and for code also implementation, verification and the review of the code | read `activities` next to `Deliverables` | semantic |
| WBS-06 | The owner's role, and the owner of each activity, bring the skills the activities name, as `Responsibilities` of the plan states them | compare `activities` with the plan | semantic |
| WBS-07 | `delivers` names only items this package produces, and none that another package delivers | `show <ID>`; compare with the other packages | semantic |

## The set

| ID | Check | How to check | Kind |
|---|---|---|---|
| WBS-20 | Every package has at most one parent; no cycle in `part_of` or `depends_on` | `check`: no `COV-31` finding | script |
| WBS-21 | Every item of the processes in scope is delivered by a package | `check`: no `COV-32` finding | script |
| WBS-22 | Packages exist for engineering, management and support work | `check`: no `COV-33` finding | script |
| WBS-23 | Dates fit: finish after start, inside the parent, after what it depends on; activities inside their package | `check`: no `COV-34` finding | script |
| WBS-24 | Every milestone of the plan comes after the planned finish of the packages whose deliverables it needs | `progress` milestones next to the package dates | semantic |
| WBS-25 | Management and support work is planned as far as its processes are in scope: planning and reporting, reviews, configuration management, change control, quality assurance | compare the packages with `scope.processes` and the plans | semantic |
| WBS-26 | Dependencies are complete: a package that needs the deliverables of another depends on it; a delivery from outside appears as a commitment of the plan dated before the packages that need it | read `depends_on` and `Interfaces and commitments` | semantic |
| WBS-27 | The summed estimates of overlapping packages per owner fit the time the plan's resources give that role; an overload is named | add up estimates per owner and period; say where the figures do not allow it | semantic |
| WBS-28 | The project lead states that these estimates and dates are the ones the project works to | ask the project lead; the note names who and when | accountable |
