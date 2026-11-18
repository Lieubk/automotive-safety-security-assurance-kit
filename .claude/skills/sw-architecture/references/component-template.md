# Software component item

File: `spec/software/architecture/<ID>.md`. Attributes and sections are those of type
`software-component` in `schema/items.yaml`; the layout is defined in
`schema/item-format.md`. The example is CMP-0004 of `examples/power-window`, the way
this skill drafts it: with the allocation stated on the component (`fulfils`).

```markdown
---
id: CMP-0004
type: software-component
title: AntiPinch - anti-pinch detection
status: draft
asil: B
security_relevant: false
kind: application
layer: application
origin: developed
execution_context: "OsTask_Control_5ms, called after WindowPos; ASIL B partition of the door module"
resource_budget: {rom_bytes: 1536, ram_bytes: 16, stack_bytes: 64, cpu_load_percent: 0.6, wcet_us: 30}
links:
  part_of: [CMP-0001]
  fulfils: [SWR-0004, SWR-0005, SWR-0006]
---

## Purpose

Holds the safety function of the product - recognising that the closing glass meets an
obstacle and asking for the reversal - in one small component that depends on nothing
but its three input values.

## Responsibility

- Supervises every closing movement, manual or automatic, from the motor state
  (IFC-0005) and the window motion (IFC-0002).
- Sets the reversal request on IFC-0003 when the window speed falls below the
  reference speed inside the protected zone (SWR-0004), and when an input is outside
  its range during closing (SWR-0006).
- Clears the request after 120 mm of opening travel, at the fully open position or
  after 2 s (SWR-0005).

It does not command the motor (MotorDrive acts on the request, SWR-0007), does not know
why the window closes, and takes no input from WindowCmd.

## Dynamic behavior

One cycle function, `AntiPinch_Step`, every 5 ms, after `WindowPos_Step` of the same
cycle and before `MotorDrive_Step`, so that a detection reaches the bridge in the cycle
in which it is made. States: IDLE, SETTLING (first 100 ms of closing), MONITORING,
REVERSING. After initialisation the state is IDLE and the request is clear.
Worst-case execution time objective 30 us per cycle.
```

## What is needed when

"Needed" uses the stages of the schema: "before review" is an error from state
`in-review` on, "before approval" from state `approved` on. A draft written by
`/sw-architecture` carries all of them from the start. For a draft, `check --all` lists
what review still needs ("still to come before review"), but neither what approval needs
nor what depends on another attribute, such as `supplier`.

| Attribute or section | Needed | What to write |
|---|---|---|
| `id`, `type`, `title`, `status` | always | `title`: the name used in code or model, then what the component is |
| `asil`, `security_relevant` | before review | highest ASIL of the allocated requirements; for a composition, of its parts |
| `kind`, `layer`, `origin` | before review | see the mapping in `architecture-guidance.md` |
| `supplier` | before review when `origin` is `supplied` or `reused` | who delivers it, which version, in which form, and the ASIL it was developed to |
| `Purpose` | before review | why the component exists as an element of its own |
| `Responsibility` | before review | what it does and what it does not do |
| `resource_budget` | before approval | objectives, or `not_relevant` with the reason |
| `Dynamic behavior` | before approval | the component's own modes and timing |
| `execution_context` | optional | task, interrupt, core, partition or operating system application it runs in |
| `model` | optional | path of the component description this item documents |
| `variants` | optional | product variants the component belongs to; absent means all |
| `links.part_of` | every component except the top of the hierarchy | the composition it belongs to; exactly one |
| `links.fulfils` | every component that requirements are allocated to | the software requirements the component is responsible for |

`fulfils` is the allocation. It is stated on the component, so that allocating never
changes a requirement. An allocation may also arrive with a requirement, as
`allocated_to` on the requirement: in the example project all nine requirements carry
it, and the components there have no `fulfils`. Either side establishes the allocation;
do not state the same one on both. `python tools/traceability.py show <ID>` lists the
requirements of a component whichever side names them, together with the interfaces it
provides and uses.

A changed `fulfils` list is a change of the component: an approved component loses its
approval until `/review` covers it again. The review record then names the requirements
as references, which is the evidence that component and requirements were compared.

## The three sections

**Purpose** answers "why is this a component?": what it hides, isolates or keeps in one
place, and what would be worse without it. One to three sentences. If it only repeats
the title or the responsibility, it is missing.

**Responsibility** is the contract of the component with the rest of the software:

- what it does, one statement per duty, each with the requirement and interface IDs it
  concerns, so that a reviewer can tick off every allocated requirement;
- what it does not do, where a reader could expect it to: the boundary to its neighbours;
- for a `composition`: its parts, what holds them together, and that it has no code of
  its own;
- no algorithm, no function list, no variables: those are detailed design.

**Dynamic behavior** covers this component alone:

- how it is activated: cycle function and period, event, or interrupt, and its place in
  the calling order where the order matters;
- its own states, the state after initialisation, and what it does while an input is
  missing or invalid;
- its timing objective, which must equal `wcet_us` and fit the task budget of the
  execution model;
- what it shares with another execution context, and that this is protected.

Behaviour that needs two or more components to explain belongs in a view; the section
then names the view. A component without behaviour of its own (a composition, a
parameter component) says so in one sentence instead of leaving the section out.

## Variants of the front matter

Composition at the top of the delivery (CMP-0001). No `part_of`; the budget is formed
from the parts:

```yaml
kind: composition
layer: application
origin: developed
asil: B                    # highest of its parts
resource_budget: {rom_bytes: 9216, ram_bytes: 192, stack_bytes: 160, cpu_load_percent: 3.6}
```

Reused component (CMP-0005). `supplier` says where it comes from and why it may carry
ASIL B requirements; requirements are allocated to it like to a developed one:

```yaml
kind: sensor-actuator
layer: application
origin: reused
supplier: "software supplier's own window lifter platform, release 3.2.0; C source with its released detailed design and unit verification results, developed to ASIL B, taken over without change"
resource_budget: {rom_bytes: 2560, ram_bytes: 48, stack_bytes: 96, cpu_load_percent: 1.2, wcet_us: 60}
links:
  part_of: [CMP-0001]
  fulfils: [SWR-0007]
```

Supplied basic software (CMP-0006). No requirement of the project is allocated to it,
so `Purpose` has to say why it is in the architecture; that is what satisfies `COV-08`:

```yaml
kind: basic-software
layer: services
origin: supplied
supplier: "customer; basic software package of the front door module, release 5.4.1, delivered as configured object library with headers and a description of the configuration"
execution_context: "all tasks and interrupts of the door module"
resource_budget: {not_relevant: "sized and budgeted by the customer, who owns the door module; the shares assigned to the delivered application are the capacities in VIEW-0005"}
```

Component described by an AUTOSAR component description. The item names the file and
repeats neither ports nor runnables (the example project has no such file; the path is
an illustration):

```yaml
kind: application
layer: application
origin: developed
model: model/components/AntiPinch.arxml
```

## Notes

- `resource_budget` is one mapping, not a list. Keys: `rom_bytes`, `ram_bytes`,
  `stack_bytes`, `cpu_load_percent`, `wcet_us`, `not_relevant`. Give the keys that
  matter for the component; an empty mapping is a `SCHEMA` error.
- The values are objectives, never measurements. Measured values belong to the
  `measured` key of the resource summary view and come from a map file or a measurement
  on the target, not from this skill.
- Write booleans as `true` and `false`; quote any text that contains a colon.
- A component with `origin: developed` and a `kind` other than `composition` will need
  one component design and at least one unit (`COV-09`). That is the task of
  `/sw-detailed-design`, not a defect of the architecture item.
