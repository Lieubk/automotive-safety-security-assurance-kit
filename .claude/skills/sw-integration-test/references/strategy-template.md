# Software integration strategy

File: `plans/<ID>.md`. Type `plan`, `kind: software-integration`. A project has one
such plan; it answers SWE.5.BP1 (integration) and SWE.5.BP2 (integration test). The
trace check reports `COV-27` until it is approved, `COV-35` when its steps do not
account for every component, and reads its steps for `COV-36` to `COV-38`.

## Decisions to ask the user before drafting

Ask these, with the options, and write down who decided. A value taken from the
template below is a proposal and is shown as one.

| Decision | Typical options | Lands in |
|---|---|---|
| Which components this project integrates, and which someone else does | all of them; the application without the basic software, which the customer integrates on the control unit | `Scope`; a component left to others is a double of the last step |
| How components that are not developed here enter | source taken over from an earlier release, a library, generated code; with which version | `Scope`, and the build configuration that names version and files |
| Order of the steps | along the data flow (sensor to actuator); safety-relevant parts first; the risky interface first; one step for everything (only for very small software, and then said why) | `integration_steps`, `Approach` |
| What stands in for the missing parts in each step | doubles of the components not integrated yet; a double of the platform with the task bodies of the execution model | `doubles` of each step, `Environment and tools` |
| Entry criteria of a step | units unit-verified with no `COV-30` on them; earlier step passed | `Criteria` |
| What is tested per step, by which method | interfaces (ranges, invalid values, time-outs), sequences and states across components, execution order, timing, resource use | `Approach` |
| What the host cannot show, and where it is shown instead | timing and load on the target, the real platform and its configuration | `Scope`, `Environment and tools` |
| Regression rule | everything again after any change; the steps whose build contains a changed file, with all their cases; plus the cases `impact` names | `Approach`, `Criteria` |
| Pass and exit criteria; handling of a failed case | every case of the step passed; a failed case gets a problem report or a decision by a named role | `Criteria`, `Responsibilities` |
| Environments | host; software-in-the-loop; target or bench | `environment` of each step; the same names in test cases and runs |
| Who integrates, writes cases, reviews, decides | roles, not names | `Responsibilities` |

Each step is a record of `integration_steps`: `name` (one word or a short hyphenated
name; test cases refer to it in `step`), `components` (added in this step; a composition
stands for the components inside it), `doubles` (the components a double stands in for
in this step), `environment` and `description`. A step contains everything added up to
it. The last step contains the complete software of this project; a component that is
never integrated here is a double of the last step.

## Template

The values are those of the power window example (`plans/PLN-0004.md`) and are
invented. Replace every one of them with what the user decides.

```markdown
---
id: PLN-0004
type: plan
title: Software integration and integration test strategy
status: draft
kind: software-integration
integration_steps:
  - name: detection
    components: [CMP-0003, CMP-0004]
    doubles: [CMP-0002, CMP-0005, CMP-0006]
    environment: host
    description: "Hall edges to position and speed, and the obstacle detection on them"
  - name: application
    components: [CMP-0002, CMP-0005]
    doubles: [CMP-0006]
    environment: host
    description: "the command logic and the motor actuation added: the complete application"
---

## Scope

Integrated here: the components of the power window application (CMP-0001) - the two
developed in this project, WindowPos and AntiPinch, and the two taken over unchanged
from the window lifter platform release 3.2.0, WindowCmd and MotorDrive.

Not integrated here: the basic software of the door module (CMP-0006). The customer
integrates the delivered software with it on the control unit. Until then a double
stands in for it in every step, including the integration code that calls the
application functions in the order of the execution model (VIEW-0004).

Left to the customer's integration on the control unit: execution times and processor
load (VIEW-0005), the real capture interrupt, and the configuration of tasks and
exclusive areas against VIEW-0004.

## Approach

Two steps, along the path from the Hall sensor to the bridge:
...
Regression: a change of a file a step builds makes that step and every later one
stale (`COV-36`); they are built again and all their cases run again...

## Criteria
...
## Environment and tools
...
## Responsibilities
...
```

Write `Approach`, `Criteria`, `Environment and tools` and `Responsibilities` out in full
for the project, as `plans/PLN-0004.md` of the example does; the dots above only save
space here.

## Notes

- Steps follow the dependencies: a step adds what uses the parts integrated before it,
  or what they use, so that each step can be tested with doubles for what is missing.
  `show <CMP-ID>` lists the interfaces a component provides and uses.
- The plan carries no links. `impact` lists nothing for it; a change of the steps
  concerns every build and every integration test, and `COV-36` and `COV-37` say what
  no longer fits once the changed plan is approved again.
- Step names are used in `step` of the test cases and in `--step` of `record.py build`.
  Renaming a step makes those cases report `COV-37` until they are changed too.
- Roles are named, people are not.
