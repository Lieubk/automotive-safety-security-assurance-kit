# Software detailed design review checklist

Version 1. Applies to: `component-design`, `software-unit`, and `design-decision` of
level `detailed-design`. Supports: SWE.3.BP1, SWE.3.BP2, SWE.3.BP3, SWE.3.BP4,
SWE.3.BP5, SWE.3.BP6.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

Review a component design together with its units and with the items they link to:
`python tools/traceability.py hash --upstream <ID>...` lists them. A unit is reviewed
with this checklist as a design, before it has code or when its design changes. Its
code is reviewed against it with `software-unit-code.md`, in a review of its own that
is recorded with the code revision.

The record cites this checklist as `software-detailed-design v1`, or by its title as
`software detailed design review v1`. An approved verdict needs a result for every
check: `pass`, `finding`, or `not-applicable` with a note that says why (SDD-41 for a
unit without an ASIL, SDD-55 when no decision concerns the subjects, the checks of a
component design when only a unit is reviewed again). A check that cannot be answered
yet is `not-assessed`. This is normal for an accountable check that waits for someone
outside the session, such as the agreement of those who build on the design: the
items stay in review, and the review is completed when the answer exists.

## Each component design

| ID | Check | How to check | Kind |
|---|---|---|---|
| SDD-01 | Mandatory attributes and sections for its state are present, values are allowed | `check --all`: no `SCHEMA` or `FORMAT` finding on the item, and no "still to come" line | script |
| SDD-02 | It refines one developed component, which has exactly this one design and at least one unit | `check`: no `LINK` finding on the item and no `COV-09` finding on the component | script |
| SDD-03 | The design concept states the approach, why it was chosen, the constraints it obeys and the assumptions it makes; each assumption has an owner | read `Design concept` | semantic |
| SDD-04 | A choice between real alternatives is a `design-decision` that concerns the item and is referred to by ID | read `Design concept`; `show <ID>` lists the decisions | semantic |
| SDD-05 | The static structure lists every unit of the component with its files, what other components may call and what it uses, and agrees with the links of the units; the file names follow the project's naming convention | compare the section with `show <component ID>` and the `uses` and `realizes` links | semantic |
| SDD-06 | The units have one clear responsibility each, the reason for every cut is given, and the `uses` links between them form no cycle | read `Design concept`, `Static structure` and the `Purpose` of the units | semantic |
| SDD-07 | Dynamic behaviour covers start-up order, every periodic and every event-driven path, what is shared between execution contexts with its protection, and at least one failure path; or it says `Not applicable:` with a reason the units confirm | read `Dynamic behavior` | semantic |
| SDD-08 | Execution contexts, call order and timing agree with the component item and with the views that show it | compare with `execution_context` of the component and the execution model view | semantic |
| SDD-09 | The evaluation names the criteria and limits it uses, or the item that states them | read `Design evaluation` | semantic |
| SDD-10 | Each criterion has a result that is specific to this component and can be checked in the design; counted values are given against their limits and marked as estimated or measured | read `Design evaluation` against the units | semantic |
| SDD-11 | The criticality result agrees with the ASIL of the units and says what it means for their verification | read `Design evaluation`; compare with `asil` of the units and the unit verification plan | semantic |
| SDD-12 | Every risk has effect, measure and owner; every negative result ended in a design change, a risk or a stated acceptance | read the risk table | semantic |
| SDD-13 | The named owners know their risks, and each acceptance was given by the person entitled to it | ask who accepted what, and when | accountable |

## Each unit

| ID | Check | How to check | Kind |
|---|---|---|---|
| SDD-20 | Mandatory attributes and sections for its state are present; every function has a name and a category, every variable a name, type and scope | `check --all`: no `SCHEMA` or `FORMAT` finding on the item, and no "still to come" line | script |
| SDD-21 | It belongs to exactly one component, and its link targets exist and have an allowed type | `check`: no `LINK` finding and no `COV-10` "part_of" finding | script |
| SDD-22 | Its ASIL is not lower than that of its component and of the requirements it implements, or an approved decision documents the decomposition | `check`: no `COV-23` finding | script |
| SDD-23 | `origin` is stated; a generated unit names what it is generated from | `check`: no `SCHEMA` finding | script |
| SDD-24 | `source_files` lists only files that exist and no file another unit lists; a unit without code has none and is reported as designed but not implemented | `check`: no `COV-11` finding and no `COV-10` "does not exist" finding; `COV-10` "designed but not implemented" and the rules marked "pending: the unit has no code yet" are warnings, not findings of this review | script |
| SDD-25 | Every function determines exactly one C prototype: name, arguments in order with name and `type`, and one return type (`return_type`, or the same `type` in every `returns` entry), written as they will stand in C, so that the check can compare them with the code | read `functions` | semantic |
| SDD-26 | Every function of category public, scheduled or callback has a complete contract: each argument with direction and, for physical values, unit, range and resolution; each return value with its meaning; preconditions; postconditions per outcome; errors with reaction; call context; re-entrancy | read `functions` | semantic |
| SDD-27 | Every scheduled function and callback names what activates it, and its period where it is periodic | read `trigger` and `period_ms`; compare with the execution model view | semantic |
| SDD-28 | Name, arguments, ranges and error behaviour of each function that serves an interface agree with the interface item, on the providing and on the using side | read `functions` next to the interfaces under `realizes` and `uses` | semantic |
| SDD-29 | Every variable that keeps its value between calls is listed with type, range, initial value and protection; `scope: global` has its reason | read `data` and `Design notes` | semantic |
| SDD-30 | The protection stated for each variable holds for the contexts that really access it | compare `protection` with `call_context` of the functions and the execution model view | semantic |
| SDD-31 | The purpose says what the unit is for; nothing in the unit lies outside it | read `Purpose` | semantic |
| SDD-32 | The behaviour can be implemented without a design decision: algorithm, scaling, rounding, limits, overflow, initialisation, and for a unit with states every state with what each event does in it | read `Behavior` as the developer would | semantic |
| SDD-33 | A tester can derive the tests: value classes and limits of every input, the expected result for each including the error results, what to set up and what to stub | read `functions` and `Behavior` as the tester would | semantic |
| SDD-34 | The behaviour describes decisions and intent; it does not repeat code statement by statement | read `Behavior` | semantic |
| SDD-35 | Every number with a meaning is a named constant with value and unit; types the unit defines are given with members and ranges | read `Behavior` | semantic |
| SDD-36 | Every error the unit can detect or receive has detection, reaction and report: each `errors` entry, each failure of a function or interface it uses, each stored value outside its range; what the unit cannot detect is stated | read `Error handling` against `functions`, `uses` and `data` | semantic |
| SDD-37 | Dynamic behaviour states contexts, what can interrupt what, protection, timing and loop bounds; or `Not applicable:` with a reason the item confirms (no data, no trigger, every function re-entrant) | read `Dynamic behavior` against `functions` and `data` | semantic |
| SDD-38 | Platform resources the unit touches are listed and named as in the component description or configuration | read `platform`; compare with the file named in `model` of the component | semantic |
| SDD-39 | The unit fulfils each requirement it implements, and contains nothing that no requirement, interface or stated reason asks for | read the unit next to each `implements` target | semantic |
| SDD-40 | Its resource objectives fit inside the budget of the component | add up `resource_budget` of the units; compare with the component | semantic |
| SDD-41 | For a unit with an ASIL: input checks, reaction to invalid inputs and to an invalid state, and limiting of results are designed, and the notation meets what the project's safety plan asks for that ASIL | read `Behavior` and `Error handling`; ask the safety engineer where unsure | semantic |

## The set

| ID | Check | How to check | Kind |
|---|---|---|---|
| SDD-50 | Every developed component has a design and units | `check`: no `COV-09` finding | script |
| SDD-51 | Every interface provided by a developed component is realized by a unit of that component | `check`: no `COV-21` finding | script |
| SDD-52 | Every requirement a component with several units fulfils is implemented by an identified unit | `matrix`: compare the `fulfils` table of the components with the `implements` table | semantic |
| SDD-53 | Taken together, the units of each component cover everything the component is responsible for | read the component with its units (`show <component ID>`) | semantic |
| SDD-54 | Terms, types, scalings and values are the same across the units, the interfaces and the requirements | compare linked and related items | semantic |
| SDD-55 | Each detailed-design decision assesses every alternative against every criterion, and the design follows the decision | read the `design-decision` items that concern the subject | semantic |
| SDD-56 | The project's evaluation criteria and limits were decided by the person entitled to do so | ask who decided, and when | accountable |
| SDD-57 | Open questions about architecture and requirements are recorded - as `query` items for imported inputs, with their owner for items the project wrote - and none of them invalidates a design item under review | `list --type query --status open`; ask the author | accountable |
| SDD-59 | Every item the subjects link to is approved, or is itself a subject of this review | `hash --upstream <ID>...` lists the targets; `list --status draft` and `list --status in-review` name none of them | script |
| SDD-58 | Those who implement, verify and integrate the units have agreed to the design | ask who agreed, and when | accountable |
