# Judgement calls in the software architecture

What `/sw-architecture` has to decide or prepare for a decision, and how. Examples refer
to `examples/power-window`.

## What shapes the architecture

Most requirements fit into any reasonable structure. A few decide it. Find them before
drawing, by asking of each requirement: would a different structure make this easier,
harder or impossible?

| Kind of driver | In the example |
|---|---|
| A reaction time across several steps | 20 ms from the speed drop to the reversed motor command (SYE-0001), split over SWR-0004 and SWR-0007 |
| A safety requirement next to functions without one | obstacle detection ASIL B, comfort functions QM |
| Hardware that needs handling at interrupt level | one Hall pulse every 2.5 ms to 6.25 ms, each with a time stamp (SYI-0001) |
| Limits of the controller | 16384 bytes of flash, 1024 bytes of RAM, 10 % of the processor time |
| Software that exists already | command logic and motor actuation of an earlier product; the customer's basic software |
| Change that is expected | a different position sensor |

Turn the drivers into evaluation criteria and let the user rank them. A criterion is
usable when two people would agree whether a structure meets it: "a different sensor
changes one component only", "no QM component lies between sensor and bridge", "the
reused components stay unchanged". Project goals that are not requirements (reuse,
development in parallel, testing on a development host) count as drivers too; write
down who named them.

## How far to decompose

A component is the smallest element the architecture names. Below it the detailed
design continues with units. Stop splitting when all of these hold:

- its purpose fits into one to three sentences without "and also";
- its requirements belong together: they change for the same reasons;
- everything it exchanges with others can be listed as interfaces;
- one ASIL, one origin and one kind of execution context apply to all of it, or the
  exception has a reason.

Split a candidate when it mixes duties with different ASIL, logic with access to
hardware, developed code with reused code, or parts that run at very different rates
and share little. Merge two candidates when they could only work through a wide
interface between them, or when one of them has no requirement and no reason of its own.

Add a level to the hierarchy only where the level means something: a delivery boundary,
a feature area, a partition. In the example one composition is enough, and it exists
because it is the boundary of the delivery. `part_of` and `layer` are independent: the
composition groups what is delivered together, although one of its parts is a complex
driver.

Splitting a component into files or functions is not architecture. If the reason for a
split is "the interrupt part and the task part", that is two units of one component, as
in WindowPos.

When an architecture exists already, read its structure view and its decisions before
proposing anything: a new requirement goes to the component whose purpose it fits. A
new component is the answer only when no existing purpose covers the need, and it is a
choice worth a decision item.

## Supplied, reused and basic software

Everything that is in the build takes part in the architecture, whoever wrote it.

- **How many items.** One component for a whole supplied platform is enough when the
  project only uses it, as the example does with the customer's basic software. When
  the project configures and integrates the basic software itself, use one component
  per cluster whose tasks, start-up order and budgets the project decides: operating
  system, communication, memory services, diagnostics, mode management, drivers.
- **`supplier`.** Who delivers, which version, in which form (source, object library,
  generated from configuration), and for an element that carries safety requirements
  the ASIL it was developed to or the qualification that comes with it. A reused
  element without such evidence cannot simply be given the ASIL: that is a question for
  the people responsible for functional safety, and an open point until answered.
- **`Responsibility`.** What this project uses of it, not everything it can do.
- **Requirements.** A `reused` component fulfils requirements of the project and lists
  them under `fulfils` like a developed one. A `supplied` or `generated` component may
  have none; then `Purpose` says why it is present, which is what `COV-08` accepts.
- **Budgets.** Either objectives, or `not_relevant` naming who budgets it instead. A
  budget nobody has decided yet is neither: the component stays short of approval, and the
  open budget is a query to whoever sets it (or a risk), not a `not_relevant`.
- **Interfaces.** Defined to the same depth as all others, with the names of the
  supplied release. This boundary is where integration problems collect.

## AUTOSAR Classic

| Element | `kind` | `layer` |
|---|---|---|
| Composition of application components | `composition` | `application` |
| Application software component | `application` | `application` |
| Component bound to one sensor or actuator | `sensor-actuator` | `application` |
| Component that only provides calibration data | `parameter` | `application` |
| Runtime environment | `other`, with `origin: generated` | `runtime-environment` |
| Service component; basic software module or cluster of the service layer | `service` or `basic-software` | `services` |
| Abstraction of the control unit's inputs and outputs | `ecu-abstraction` | `ecu-abstraction` |
| Driver of a microcontroller peripheral | `basic-software` | `microcontroller-abstraction` |
| Complex driver | `complex-driver` | `complex-drivers` |
| Library | `library` | the layer it is delivered with |
| Supplied platform modelled as one component (the customer's basic software, for example) | `basic-software`, with `origin: supplied` | `several` |

- A complex driver needs its reason in `Purpose`: what the standard path through the
  basic software cannot deliver. WindowPos is one because it needs the time stamp of
  every edge at interrupt level.
- With a generated runtime environment, components of the application layer exchange
  data through port-style interfaces only (`sender-receiver`, `client-server`,
  `mode-switch`, `parameter`, `non-volatile-data`, `trigger`). `function-call` is for
  complex drivers, and for software delivered as plain C that integration code connects,
  as in the example.
- **The component description is the source.** Ports, port interfaces, data types,
  runnables and their events are defined in the description file, and `model` on the
  component item names that file. The item adds what the file cannot hold: purpose,
  boundary, modes, budgets, ASIL. Read names from the file; never type a port or
  runnable list into the item body. Interface items take element names, types and
  ranges from the port interface definitions unchanged. The `entries` of the execution
  model are the runnable names of the description, mapped as the configuration maps them.
- If the architecture comes first and no description exists yet, the items are the
  specification the description is created from. Once it exists, set `model`, compare
  both once with the user, and from then on correct the item when they differ.
- No command compares the description with the items (see "What the tools do not
  check"). Say so in the hand-over as `NOT ASSESSED`; do not claim agreement after
  reading the file once.

## Interfaces

Rules per key are in `interface-template.md`. The judgement is where to stop:

- Describe the contract, not the implementation: what crosses the boundary, what it
  means, when it is valid, what happens otherwise. Not how the provider computes it.
- A value that appears in a requirement (a range, a time, a threshold) appears with the
  same number in the interface, or the interface refers to the requirement.
- State the age of data. A user in a slower task, or one that runs before the provider
  in the same task, sees an older value; whether that is acceptable is a design
  statement with a reason (IFC-0005 of the example gives one).
- For every element ask "what does the user get before the first update, and when the
  provider has nothing valid?" and for every operation "what can come back, and what
  does the caller do then?". An interface with no answer is not finished.

## Dynamic behaviour

What each view kind must show is in `view-templates.md`. Two tests for a useful view:

- **It answers a question a requirement asks.** A sequence that only shows who calls
  whom repeats the structure. One that shows in which cycle each step happens and adds
  up the time proves that the reaction time can be met.
- **It can be wrong.** A state view whose transitions carry conditions, and a sequence
  with numbers, can be checked against the requirements and tested in integration. A
  picture that fits every implementation says nothing.

Describe the failure side as carefully as the good case: an input that is missing or
out of range, a call that fails, a step that takes too long. Where the software has no
part in a subject - shut-down handled by a supplied platform, for example - say that in
the component item instead of leaving the subject out.

## Deriving budgets

1. **Capacity.** What the hardware offers or the customer assigns, from a system item
   (SYE-0001 in the example) or from the user. Never assume a capacity.
2. **Reserve.** The share that must stay free at delivery, from the customer or a
   project rule. If nobody has set one, propose one and label it a proposal. The example
   keeps 20 % of flash, RAM and processor time and 30 % of every stack free.
3. **Component objectives.** Sources in order of trust: the measured size or run time of
   the same component in an earlier product (for reused components); a comparable
   component; an estimate from the design; what is left after the others. Say which
   source each number has. Round up. An objective is a limit the developer has to meet.
4. **Processor time.** `wcet_us` per activation; `cpu_load_percent` is `wcet_us` over
   the period, plus for an interrupt the highest rate times its run time. WindowPos:
   40 us / 5 ms + 400 x 10 us / 1 s = 0.8 % + 0.4 % = 1.2 %.
5. **Stack.** Per task the deepest chain of one entry plus the caller, not the sum of
   the entries: they run one after the other.

Then check that the numbers agree, and show the calculation to the user:

| Check | In the example |
|---|---|
| Composition = sum of its parts (flash, RAM, processor time) | 3072 + 2048 + 1536 + 2560 = 9216 bytes |
| Task budget = `wcet_us` of its entries + stated overhead | 40 + 30 + 60 + 20 = 150 us |
| Load = sum of budget over period, plus interrupt rate x budget | 3.0 % + 0.7 % + 0.4 % = 4.1 % |
| Summary objective = the sums above | 9216 bytes; 4.1 % |
| Objective <= capacity x (100 - reserve) / 100 | 9216 <= 16384 x 0.8 = 13107 |
| Differences between two sums are explained | components 3.6 %, tasks 4.1 %: integration code |

Budgets are objectives. Whether they are met is known only from a map file and from
measurements on the target. Until someone delivers those, the `measured` key stays
absent and the hand-over says who is to deliver them.

## Allocation in both directions

Forward, per requirement: which element would have to change if this requirement
changed? That element is the target.

- One requirement, one component is the normal case. Allocate to several only when
  each has a share that can be named; write the shares into their `Responsibility`.
  If the shares cannot be named, the requirement holds two needs (a query to its
  author) or the cut between the components is wrong.
- A requirement about what crosses a boundary (`kind: interface`) goes to the interface
  item. A `kind: constraint` with a `Rationale` that binds the whole software may stay
  unallocated; `COV-07` accepts that.
- Allocate to the component that does the work, not to the composition above it.

Backward, per component: run `python tools/traceability.py show <ID>` and read the
allocated requirements against `Responsibility`. A duty without a requirement means a
requirement is missing (hand it to `/sw-requirements`) or the duty is not needed. A
requirement that no sentence of `Responsibility` covers means the allocation or the text
is wrong.

The link is written on the element, as `fulfils`, because the element depends on the
requirement and not the other way round:

- No requirement is touched. Approved requirements stay approved, and imported ones
  can be allocated.
- `matrix` has one `fulfils` table for components and one for interfaces. A requirement
  with `-` in both is not allocated (`COV-07`).
- `python tools/traceability.py hash --upstream <ID>` lists the requirements an element
  fulfils as references. The review record of the architecture therefore names them, and
  that is the consistency evidence for the allocation.
- When a requirement changes later, `impact <requirement ID>` names the elements that
  fulfil it, and `check` reports their links as `SUSPECT` until they are reviewed again.
- Approval goes top down. An element cannot be approved while a requirement it fulfils
  is in `draft` or `in-review`: `check` reports `UPSTREAM` on an approved item above an
  unapproved one, and the review refuses the verdict. The same holds inside the
  architecture: a part after or together with its composition, a view after or together
  with the items it shows, a decision after or together with the items it concerns.

Withdrawing an element: nothing is deleted. First move what points to the element -
`part_of` of its parts, `shows` of views, `concerns` of decisions, `used_by` and
`provided_by` of interfaces, links of units and tests - then set it to `obsolete` with
`superseded_by` naming its successor or the reason. `LINK` reports every link from a
live item to an obsolete one, and `COV-24` every view that still shows it. An element
inside a baseline is withdrawn only with an approved change request.

## Questions to the source of an input

A question about an imported item - a system element or interface, a delivered
requirement, the description of supplied software - that the user cannot answer is
written as a `query` item, not as a remark in the hand-over. While it is open, `check`
warns with `QUERY` on every approved item it is about. A design statement that rests on
the open answer names the query by ID.

```markdown
---
id: QRY-0001
type: query
title: Memory separation between the QM and the ASIL B partition
status: open
to: "customer, system architect of the front door module"
asked_at: "2026-11-18"
links:
  about: [SYE-0001]
---

## Question

SYE-0001 assigns the window control software two tasks and one interrupt on the
microcontroller of the door module. The software architecture runs the command logic
(QM) and the obstacle detection (ASIL B) in different partitions and relies on the QM
partition having no write access to data of the ASIL B partition.

Is this separation enforced by memory protection in the basic software release 5.4.1,
and is the mechanism developed to ASIL B?
```

One question per query, answerable by someone who does not know the project's items.
`Answer` and `answered_by` are added when the user reports the answer; the status then
becomes `answered`, and `closed` once the items are in line with it. A question about a
requirement the project wrote itself is not a query: it goes back to `/sw-requirements`.

## ASIL and partitioning

- A component carries the highest ASIL of the requirements allocated to it; a
  composition the highest of its parts. An interface carries at least the ASIL of the
  function that depends on its data: IFC-0005 is ASIL B because position counting and
  obstacle supervision rely on it; IFC-0004 is QM, and its `Description` says why no
  value of it can defeat the reversal.
- `security_relevant` follows the same way from the allocated requirements.
- Elements of different ASIL in one software can disturb each other on three routes.
  For each, the architecture says what prevents it:

| Route | Typical answer | In the example |
|---|---|---|
| Memory: the lower element overwrites data of the higher | separate partitions with memory protection, stated in `execution_context` | QM partition without write access to ASIL B data |
| Time: the lower element delays the higher | priorities and budgets in the execution model, with the worst delay stated | at most 0.15 ms delay of the 5 ms task, inside the 5 ms left in the reaction budget |
| Data: the higher element uses what the lower delivers | no such input; or a check at the higher side; or an override at the higher side | no ASIL B component takes input from WindowCmd; MotorDrive lets the reversal win |

- Without such an argument every element is developed to the highest ASIL present
  (ISO 26262-9, clause 6). The mechanism that separates - operating system, memory
  protection - carries the highest ASIL of what it separates.
- An element with a lower ASIL than a requirement allocated to it is a decomposition
  (ISO 26262-9, clause 5). `COV-23` reports it until an approved `design-decision`
  `concerns` the element. Where the decomposition also creates requirements with a
  lower ASIL than their source, the same decision `concerns` those requirements. The
  decision belongs to the people responsible for functional safety.
- Safety analyses of the architecture are not produced by this skill. Ask whether they
  exist and whether their results are in the requirements; list the answer as given.

## What the tools do not check

Three things this skill would like a tool to answer, and how it copes until one does:

| Not checked | What the skill does instead |
|---|---|
| Whether the budgets add up: parts to composition, entries to task budget, tasks to processor load, objectives to the rows of the resource summary | computes the sums itself, shows the calculation to the user before writing, and writes it into the view; the checklist asks the reviewer to recompute |
| Whether the items agree with the component description named in `model` | reads names from the file, never retypes lists, and reports the comparison as `NOT ASSESSED` |
| Whether a draft would pass the checks of state `approved`. `check --all` previews only what review needs, without `resource_budget`, `Dynamic behavior`, `used_by`, `Decision`, `Consequences` and without what depends on `kind` or `origin` (`elements`, `operations`, `table`, `Diagram`, `supplier`) | walks the "Needed" column of the templates for every draft |

Say in the hand-over which of these applied in the session.

## Typical weaknesses, and what the skill does about them

| Weakness | What prevents it here |
|---|---|
| A component is a box with a name; nobody can say what it must not do | `Purpose` and `Responsibility` are separate sections; the second names the boundary and cites requirement IDs |
| Interfaces exist only as lines in a diagram | every labelled connection of the structure view is an interface item with `elements` or `operations` |
| The boundary to basic software is skipped because the platform defines it | supplied components are items; their interfaces are defined like all others |
| State views with numbered arrows; sequences of the good case only | a trigger in words per transition; a failure path or the reason why there is none |
| Start-up, shut-down and error handling are missing | the list "Which views a project needs" is walked with the user; each line ends in a view or a reason |
| Budgets exist for the control unit only, or do not add up | `resource_budget` per component; the sums are shown before writing |
| No alternatives, because the structure was given | adopting a given structure is recorded as a decision, with what was checked |
| Criteria that were written after the choice | criteria are ranked by the user before a structure is drawn |
| Links exist, but the component cannot fulfil the requirement | allocation is checked in both directions against `Responsibility` |
| A requirement changes and the architecture silently stays as it was | the element that fulfils it becomes `SUSPECT`; `impact <requirement ID>` names it |
| Open questions live in mails and hand-over notes | a question to the source of an input is a `query` item; `QUERY` shows while it is open |
| Consistency is claimed because every requirement has a link | the skill claims none; `/review` records what was compared, and `check` reports `CONSISTENCY` and `SUSPECT` |
| Description and model drift apart | `model` names the source; nothing is retyped; the comparison is reported as `NOT ASSESSED` |
| An ASIL is lowered without anyone deciding it | `COV-23`; only an approved decision that concerns the element is accepted |
| The architecture changes after approval and nobody notices | a changed item loses its approval (`COV-19`); `impact` and `SUSPECT` show what depends on it |
