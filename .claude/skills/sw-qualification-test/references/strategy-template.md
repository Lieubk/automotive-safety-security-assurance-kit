# Software qualification test strategy

File: `plans/<ID>.md`. Type `plan`, `kind: software-qualification-test`. A project has
one such plan; it answers SWE.6.BP1. The trace check reports `COV-27` until it is
approved.

## Decisions to ask the user before drafting

| Decision | Typical options | Lands in |
|---|---|---|
| Test object | the build of the last integration step; a software delivery received from another party (SWE.5 not in scope) | `Scope` |
| Requirements and releases covered | all requirements with `verification_method: test` of the release under test | `Scope`; compare with `release` of the requirements |
| What is left to the target, the system level or the vehicle | timing on the control unit, real sensors and actuators, closed-loop behaviour | `Scope` |
| Environment | software-in-the-loop on the host; hardware-in-the-loop bench; the control unit on a bench | `Environment and tools`; the name is `environment` of cases and runs |
| Stimuli | signals at the software's inputs as a bench applies them (pulse trains, bus values, driver faults); open or closed loop | `Approach` |
| Measurement points | outputs; published interface values read as a measurement tool would read them on the control unit; never internal variables of a unit | `Approach` |
| Fault injection, where a requirement concerns inputs the integrated software never produces | overwriting a signal as a calibration tool does; or the criterion is shown at a lower level, named | `Approach` |
| Derivation | per requirement, every verification criterion as one step or more; techniques for values (boundaries, equivalence classes) and times | `Approach` |
| Requirements verified otherwise | review, analysis, inspection: where the evidence is | `Approach` |
| Regression | everything again on every new build; a selection by impact; the cases of a release | `Approach`, `Criteria` |
| Entry, pass and exit criteria; failed cases | entry: the last integration step passed on the build; exit: every case passed on the latest build; a failed case gets a problem report | `Criteria` |
| Tester independence | testers did not develop the units or components; a separate team | `Responsibilities` |

## Template

The power window example's strategy is `examples/power-window/plans/PLN-0005.md`: read
it as the model. Its parts:

- `Scope`: the test object (the software of the last integration step with the platform
  double), the requirements covered, and what the customer tests on the control unit.
- `Approach`: derivation from the criteria; the stimuli (Hall pulse train, switch
  request as the stack delivers it, a bridge driver fault, and for one requirement a
  signal overwritten as a calibration tool would); the measurement points; a known limit
  of the integrated software and the unit test that covers it; regression.
- `Criteria`: entry, pass, exit, and the handling of a failed case.
- `Environment and tools`: the environment name, the runner, how records are written,
  and what a customer's bench would hand in instead (its JUnit report).
- `Responsibilities`: tester independence stated.

Write each part for the project; do not copy the example's values.

## Notes

- A measurement point is a value the software publishes anyway (an interface element,
  a read function an interface defines, a measurement access of a delivered component).
  Reading it is what a measurement tool does on the control unit. Reading a file-scope
  variable of a unit is not.
- A criterion that cannot be shown on the integrated software is named in the case,
  with the level that shows it (a unit test, an integration test, a review). The
  strategy says that this is allowed and who agrees to it.
- The plan carries no links. A change of the strategy concerns every case; review them
  against it once the changed plan is approved again.
