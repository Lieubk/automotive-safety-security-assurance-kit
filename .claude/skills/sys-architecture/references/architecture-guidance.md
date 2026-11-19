# Judgement calls in the system architecture

What `/sys-architecture` has to decide or prepare for a decision, and how. Examples
refer to `examples/power-window`.

## What shapes the architecture

Most requirements fit into any reasonable partitioning. A few decide it. Ask of each
requirement: would a different split between hardware, software and mechanics make it
easier, harder or impossible?

| Kind of driver | In the example |
|---|---|
| A safety function next to functions without one | obstacle detection ASIL B, comfort functions QM |
| A reaction time over several elements | 20 ms from the speed drop to the changed motor command |
| A physical principle with consequences for hardware | pulse per 0.5 mm from a Hall sensor on the motor shaft |
| Limits of the controller | program flash, RAM, processor time |
| What exists already or is supplied | the customer's basic software; a reused drive unit |
| Cost, installation space, mass | housing size, number of connector pins |
| Variants and change that is expected | a different position sensor in a later release |
| Security, diagnosability, serviceability | access to diagnostics through the bus |

Turn the drivers into evaluation criteria and let the user rank them. A criterion is
usable when two people would agree whether an architecture meets it: "a change of the
sensor leaves the software element unchanged", "no QM function shares the processor
with the safety function without protection", "the supplied drive unit stays unchanged".
Write down who named a goal that is not a requirement.

## Elements and how far to decompose

A system element is the smallest part the system architecture names and allocates
requirements to. Below it, the discipline that builds it continues: the software
architecture for a software element, the hardware design for a hardware element.

- Make an element of a part when one discipline builds it, one ASIL and one owner apply
  to it, its purpose fits into one to three sentences without "and also", and what it
  exchanges with others can be listed as interfaces.
- Split when a candidate mixes ASIL, mixes disciplines (the hardware and the software
  that runs on it are two elements even when one person builds both), or mixes parts
  with different suppliers or release cycles.
- Merge two candidates that could only work through a wide interface or that no
  requirement tells apart.
- Hierarchy: add a level only where it means something: a delivery boundary, a supplier,
  a variant. Name the parent in `Responsibility` and show the nesting in the `structure`
  view; no link models it.
- Software on the controller: one system element for the software that the project
  develops, one for supplied software the project integrates, when they have different
  owners or ASIL. Their split into components is `/sw-architecture`.
- Elements that exist only in a diagram do not exist. Every box of a view is an item,
  and every item an element of the architecture (`COV-24`).

## External elements

A neighbouring system, the vehicle, the user or the environment is an element of kind
`external` only when a requirement is allocated to it, normally an assumption the
system makes of it. State in `Responsibility` what is assumed, and ask its owner
through a `query` where it is not known. The neighbour's own design is not described.

## Interfaces

- One interface per exchange between two elements; the bus as a whole is not one, its
  signals used here are.
- The hardware-software interfaces are the foundation of the software requirements.
  They carry what software cannot find out for itself: polarity, ranges, resolution,
  timing, reset state, behaviour on failure.
- Do not hide an interface in a `Responsibility` text ("the software reads the sensor"):
  if two elements exchange something, an item says what and how.
- Interface requirements may exist in the system requirements. An interface that fulfils
  one carries the `fulfils` link; the definition does not restate the requirement.

## Dynamic behavior

Cover, for the system and not for one element, or give the reason it does not apply:

- operating modes and the transitions between them (off, start-up, normal, degraded,
  diagnosis, shut-down), including what triggers each;
- start-up and shut-down order across elements, with the reset state of each;
- reaction to failure of an element or interface: what the system does, what the user
  sees, which element holds the safe state;
- every chain with a time requirement, with the time spent per element and its sum.

Behaviour of one element goes into its `Dynamic behavior` section; behaviour across
elements goes into a view.

## Views at system level

A view has `level: system`. Usually a system architecture needs:

| View | Kind | Shows |
|---|---|---|
| Context | `context` | the system and its neighbours; the interfaces that cross the boundary |
| Structure | `structure` | the elements and the interfaces between them |
| Main functions over time | `sequence` | who does what in which order, with the time per step |
| Operating modes | `state-machine` | the modes of the system and what the elements do in each |
| Failure reactions | `fault-reaction` | a failure and the reaction of the system, with the `table` the kind needs |

This is a recommendation. The trace engine has no rule for required view kinds at
system level; the review checks that what the requirements make necessary is covered
(checklist `system-architecture`, SYA-71). The form of each kind follows
`view-templates.md` of `/sw-architecture`.

## Allocation

- Each requirement goes to the element that can fulfil it by its nature: what a sensor
  measures to the sensor, what the program decides to software. State the allocation as
  `fulfils` on the element.
- A requirement that spans disciplines (a reaction time) is fulfilled by every element
  on the chain; each `Responsibility` names its share, the sum is shown in a view.
- Requirements on an interface go to the interface, requirements on the whole system
  that no element can carry alone (a constraint on cost, say) go to the element the
  user names as responsible, with a note in `Responsibility`.
- What lands on a `software` element is the input of `/sw-requirements`: `COV-05` asks
  for software requirements derived from each requirement allocated to it. Allocate
  carefully; a wrong allocation costs a software requirement that nobody can verify.
- A requirement nobody can fulfil, or that the allocation shows to be contradictory
  or infeasible, goes back to `/sys-requirements` with the reason; it is not
  silently weakened here.

## Decisions

Draft a `design-decision` of level `system` for every choice that shapes the system:
the split between hardware and software, make or buy or reuse, the sensing or actuation
principle, the bus or wiring, where a safety function lives, the partitioning of
functions of different ASIL. Rules:

- The criteria are fixed with the user before the alternatives are assessed.
- Alternatives are real: ones that could have been chosen. "Do nothing" counts only if
  it is possible.
- An assessment names a reason per cell; an empty plus or minus is not an assessment.
- The decision is the user's, with the people responsible for functional safety where
  safety is concerned. A draft shows what follows from the assessment and stops.
- Cost, supply and feasibility of hardware and mechanics are judged by those who know
  them; where they are not in the conversation, the assessment says so and the check
  `SYA-67` asks for their view.

## ASIL

An element carries the highest ASIL of the requirements allocated to it. A lower
ASIL on an element is a decomposition: an approved decision `concerns` every item whose
ASIL is lowered, and it is the safety people's to approve. The skill never lowers one.
Where elements of different ASIL share a resource (the processor, the supply, a bus),
the architecture states what protects the higher from the lower, in a view or a decision.

## What the tools do not check

- Whether an interface definition at one end agrees with that at the other: no tool
  compares them. The review does (`SYA-26`).
- Whether numbers add up (time chains, resources): no tool adds them; report as
  `NOT ASSESSED` until a person has recomputed them.
- Whether the allocation is sensible: `COV-03` and `COV-04` show that something is
  allocated, not that it is allocated well.
