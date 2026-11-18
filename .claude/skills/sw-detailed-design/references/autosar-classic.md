# AUTOSAR Classic in the detailed design

What changes when the component is an AUTOSAR Classic software component or a complex
driver, and where each platform concept goes in a `software-unit` item.

## The component description stays the source

Ports, port interfaces, runnables, their events, exclusive areas, non-volatile block
needs, diagnostic events and calibration parameters are defined in the software
component description and in the basic software configuration. The component item
names that file in `model`. The detailed design:

- uses the names of the description exactly, and reads them from it; it does not copy
  the description into prose and does not introduce names the description lacks;
- adds what the description cannot hold: intent, algorithm, the reaction to every
  error value, the order of accesses inside a runnable, what must be consistent;
- is the place where a disagreement becomes visible. If the design needs something
  the description does not offer (a port, an event, an exclusive area), that is a
  query to whoever owns the description, and the item says so until it is resolved.

Before drafting ask the user for the description of the component and read the part
that concerns it. If there is none - the component is plain C called by integration
code, as in the worked example - leave `model` aside and describe the same facts in
the items; the categories below still apply.

## Where each concept goes

| Platform concept | In the unit item |
|---|---|
| Runnable activated by an event of the runtime environment (timing, data reception, mode switch, initialisation) | `functions` entry with `category: scheduled`; `trigger` names the event and, where the architecture fixes it, the task and the position in the task; `period_ms` for a timing event; `call_context: task` |
| Server runnable of a provided client-server port | `functions` entry with `category: public`; the unit `realizes` the interface; `call_context` and `reentrant` say whether concurrent invocation is possible |
| Function called by a basic software module or from an interrupt (notification, hook, the handler part of a complex driver) | `functions` entry with `category: callback`; `trigger` names the caller and the event; `call_context` as it really is |
| Provided port | `realizes` link to the `software-interface`; the function that writes or serves it is named in `Behavior` |
| Required port | `uses` link to the `software-interface`; `Behavior` says in which function it is read or called, `Error handling` what is done for every status other than success (time-out, never received, invalid value) |
| Inter-runnable variable, per-instance memory, static variable | `data` entry; `protection` names the mechanism |
| Exclusive area | `platform.exclusive_areas`: name, what it protects, which functions enter and leave it, through which service |
| Interrupt | `platform.interrupts`: which interrupt calls which function of the unit, with the view that holds its priority and budget |
| Non-volatile data | `platform.non_volatile_blocks`: block name and content; when it is written; the default; the reaction when the block is missing or invalid |
| Diagnostic event | `platform.diagnostic_events`: event name, the fault it stands for, the condition for reporting failed and passed, where debouncing happens |
| Calibration data | `platform.calibration_parameters`: name, type, unit, range, default, and whether it may change while the software runs |
| Memory mapping | `platform.memory_sections`: the sections the unit's code, constants and variables are placed in, where partitioning or ASIL separation depends on it |
| Other basic software services (mode management, watchdog supervision, communication, operating system) | `platform.services`: module and service, the calling function, the reaction to a failure |

Each key holds a list of one-line statements, as in UNT-0001 of the worked example:

```yaml
platform:
  exclusive_areas:
    - "HallData: locks Isr_HallCapture; entered and left by HallCapture_GetSnapshot through SchM_Enter_WindowPos_HallData and SchM_Exit_WindowPos_HallData (header SchM_WindowPos.h of the basic software)"
```

The one-liner identifies the resource and its use. Behaviour that needs more than a
line goes into `Behavior` and `Error handling` and refers to the resource by name.

## What to write for each

**Runnables and triggers.** One `functions` entry per runnable, with the name of the
description. State what the architecture's execution model fixes: task, period,
position among the other entries. A design that depends on an order ("after
`WindowPos_Step`, before `MotorDrive_Step`") says so in `trigger` and in the
`Dynamic behavior` of the component design, and refers to the view (VIEW-0004).

**Access to ports.** Name the access function the runnable uses and how often per
activation. Read each input once per activation and work on the copy, so that one
activation sees one set of values. For every access say what the unit does when it
does not return success; "ignored" is a design statement and needs its reason.

**Interrupts.** Name each interrupt that enters the unit and the function it calls
("Isr_HallCapture calls HallCapture_OnEdge (VIEW-0004)"). Category, priority and the
vector belong to the configuration and to the execution model view; the unit states
what its function may assume: not nested, which data it may touch, how long it may run.

**Exclusive areas.** Say which data the area protects, which contexts compete for it,
and how long it is held, counted in what is done inside ("four assignments"). Nothing
inside an area calls out of the unit. Whether the area locks interrupts, a resource or
nothing is configuration; the design states what it needs ("the capture interrupt
cannot run while the area is held").

**Non-volatile data.** The worked example stores nothing over a reset. A unit that
does - say, a later release that keeps the window position - states the layout of the
block with types and ranges, the defaults, the moment of writing (on change, at
shutdown), how often that can happen against the endurance of the memory, and the
behaviour with a missing, invalid or outdated block. Reading at start-up and the
state of the unit until the data is available belong to `Behavior`.

**Diagnostic events.** Per event: the fault, the detection condition with its values,
whether the unit debounces or the diagnostic module does, when "passed" is reported,
and what the unit itself does while the fault is present. The mapping to trouble
codes and the storage conditions are configuration and are not repeated.

**Calibration data.** Release R1.0 of the worked example has none: its thresholds are
named constants (CDS-0002). When a threshold becomes a calibration parameter, the
design states its range and default, what the unit does with a value outside the
range, and whether dependencies exist between parameters (a confirmation time that
must stay below a time-out, for example). For a unit with an ASIL, say how a corrupted
value would be noticed.

**Services.** For every service call the function that makes it, its context, and
the reaction to each failure value.

## Component kinds

- An application or sensor-actuator component reaches the rest of the software
  through the runtime environment only. A direct call into another component or into
  a basic software module from such a unit is a finding against the design.
- A complex driver may call basic software and offer C functions directly. Every
  such function is still a designed interface: an operation of a `software-interface`
  the unit `realizes` or `uses`.
- The worked example delivers plain C functions that the customer's integration code
  connects to tasks, the interrupt and the bus. The design therefore names the tasks
  and the interrupt in `trigger` and `preconditions`, and the exclusive area services
  in `platform`, and leaves the wiring to the supplied basic software (CMP-0006).

## Generated code

- Headers and skeletons that the platform tooling generates are not units of the
  project. Their paths belong under `paths.generated` of `project.yaml`, which exempts
  them from the file ownership rule (`COV-11`).
- A unit whose code is generated from a model or from configuration has
  `origin: generated` and `generated_from` naming that source. Its `functions` still
  list what other units call; its behaviour is described by the model, and the item
  says where the model is and which generator and version produce the code.
- A handwritten unit never includes logic copied out of generated files; it calls
  them through the access functions the description defines.

## What stays out of the unit item

- Task configuration, priorities and the mapping of runnables to tasks: the execution
  model view of the architecture holds them; the unit refers to it.
- Trouble codes, storage and ageing of diagnostic entries: configuration.
- The linker configuration: the memory layout view, where the project provides one.
- Signal packing on the bus: the communication configuration; the unit sees the
  interface item.
