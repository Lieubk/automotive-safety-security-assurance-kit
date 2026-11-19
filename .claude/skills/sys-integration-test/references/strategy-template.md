# System integration strategy

File: `plans/<ID>.md`. Type `plan`, `kind: system-integration`. A project has one such
plan; it answers SYS.4.BP1 (integration) and SYS.4.BP2 (integration test). The trace
check reports `COV-27` until it is approved, `COV-46` when its steps do not account for
every system element, and reads its steps for `COV-47` to `COV-49`.

## Decisions to ask the user before drafting

Ask these, with the options, and write down who decided. A value taken from the
template below is a proposal and is shown as one.

| Decision | Typical options | Lands in |
|---|---|---|
| Which elements this project integrates, and which someone else does | all hardware, mechanical and software elements; only the control unit with its software, the vehicle being integrated by the customer | `Scope`; an element left to others is a double of the last step |
| Which elements are external | neighbouring control units, the vehicle network, the environment; they are never integrated, always simulated | `Scope`, `doubles` of the steps that need them |
| Where the software comes from | the build of the last software integration step (`/sw-integration-test`), or a delivered software release; with which version | `Scope`, and the manifest of each build |
| Order of the steps | hardware first, then the software on it; along the signal path (sensor to actuator); the riskiest interface first; the mechanics when a sample exists | `integration_steps`, `Approach` |
| What stands in for the missing parts in each step | a rest-bus simulation, a load emulation, a sensor stimulus, a vehicle model, a sample of an earlier revision | `doubles` of each step, `Environment and tools` |
| Entry criteria of a step | samples and software build identified; software qualified or its build final; earlier step passed | `Criteria` |
| What is tested per step, by which method | signals reaching their receivers, timing and temporal relation of signals, all users of an interface reading it alike, behaviour over time and in failure | `Approach` |
| What the benches cannot show, and where it is shown instead | the real vehicle, climate and life tests, analogue measurements outside the bench's range | `Scope`, `Environment and tools` |
| Regression rule | everything again after any change; the steps whose build contains a changed element, with all their cases; plus the cases `impact` names | `Approach`, `Criteria` |
| Pass and exit criteria; handling of a failed case | every case of the step passed; a failed case gets a problem report or a decision by a named role | `Criteria`, `Responsibilities` |
| Environments | the bench names, as test cases and runs will use them | `environment` of each step |
| Release plan and project plan | which release contains which step; which milestone needs which result | `Scope`, `Approach` |
| Who integrates, writes cases, runs the bench, reviews, decides | roles, not names | `Responsibilities` |

Each step is a record of `integration_steps`: `name` (one word or a short hyphenated
name; test cases refer to it in `step`), `components` (the system elements added in this
step), `doubles` (the elements a simulation or a stand-in replaces in this step; use the
element ID and say in `description` how it is simulated), `environment` and
`description`. A step contains everything added up to it. The last step contains the
complete system of this project; an element that is never integrated here, an external
element above all, is a double of the last step.

## Template

The elements and values are invented for a window lifter control unit. Replace every one
of them with what the user decides.

```markdown
---
id: PLN-0008
type: plan
title: System integration and integration test strategy
status: draft
kind: system-integration
integration_steps:
  - name: electronics
    components: [SYE-0002]
    doubles: [SYE-0001, SYE-0003, SYE-0004]
    environment: bench-electronics
    description: "control unit sample with power stage and sensor inputs; motor, sensor and vehicle network simulated"
  - name: software
    components: [SYE-0005]
    doubles: [SYE-0001, SYE-0003, SYE-0004]
    environment: bench-electronics
    description: "the software of the window lifter on the control unit; the other elements still simulated"
  - name: drive
    components: [SYE-0001, SYE-0004]
    doubles: [SYE-0003]
    environment: bench-drive
    description: "motor with mechanics and Hall sensor connected; the vehicle network is still a rest-bus simulation"
---

## Scope

Integrated here: the control unit (SYE-0002) with its software (SYE-0005), the drive
(SYE-0001) and the Hall sensor (SYE-0004).

Not integrated here: the vehicle network and the door module (SYE-0003, external). A
rest-bus simulation stands in for it in every step; the customer integrates in the
vehicle.

Left to the customer: behaviour in the vehicle, climate and life tests.

## Approach

Three steps along the signal path: ...
Regression: a change of an element or of the software build makes its step and every
later one stale (`COV-47`, `COV-49`); they are integrated again and all their cases run
again ...

## Criteria
...
## Environment and tools
...
## Responsibilities
...
```

Write `Approach`, `Criteria`, `Environment and tools` and `Responsibilities` out in full
for the project; the dots above only save space here.

## Notes

- Steps follow the dependencies: a step adds what uses the parts integrated before it,
  or what they use, so that each step can be tested with simulations for what is missing.
  `show <SYE-ID>` lists the interfaces of an element.
- The software element is one element of the system: its build comes from the software
  integration (SWE.5) and is named in the manifest of each system build that contains it.
  The system-level step does not rebuild software.
- The plan carries no links. `impact` lists nothing for it; a change of the steps
  concerns every build and every system integration test, and `COV-46` to `COV-49` say
  what no longer fits once the changed plan is approved again.
- Step names are used in `step` of the test cases and in `--step` of `record.py build`.
  Renaming a step makes those cases report `COV-48` until they are changed too.
- Roles are named, people are not.
