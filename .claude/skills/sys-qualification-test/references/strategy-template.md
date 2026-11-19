# System qualification test strategy

File: `plans/<ID>.md`. Type `plan`, `kind: system-qualification-test`. A project has one
such plan; it answers SYS.5.BP1. The trace check reports `COV-27` until it is approved.

## Decisions to ask the user before drafting

| Decision | Typical options | Lands in |
|---|---|---|
| Test object | the system build of the last step of the system-integration plan; an integrated system received from another party (SYS.4 not in scope: say where it comes from and how its configuration is named) | `Scope` |
| Requirements and releases covered | all system requirements with `verification_method: test` of the release under test | `Scope`; compare with `release` of the requirements |
| What is left to the vehicle or to the customer | fleet behaviour, long-term durability, environmental tests done in a laboratory, driver perception | `Scope` |
| Environment | system bench with restbus and load simulation; hardware-in-the-loop rig; test vehicle on a proving ground; the target in its real environment; the name is `environment` of cases and runs | `Environment and tools` |
| Stimuli | signals and loads at the system interfaces as the environment applies them (bus messages, supply voltage and temperature, sensor inputs, operator actions); open or closed loop | `Approach` |
| Measurement points | outputs of the system, bus signals, diagnostic data, measurements of loggers; never a value that only a debugger reaches | `Approach` |
| Fault injection | wiring faults, signal loss, supply dips, as the bench provides them; or the criterion is shown by another method, named | `Approach` |
| Derivation | per requirement, every verification criterion as one step or more; techniques for values (boundaries, equivalence classes), times and operating conditions | `Approach` |
| Requirements verified otherwise | review, analysis, inspection: where the evidence is | `Approach` |
| Configurations and variants | which variants, hardware samples and software releases are tested | `Scope`, `Approach` |
| Regression | everything again on every new system build; a selection by impact; the cases of a release; fits the release plan and the project plan | `Approach`, `Criteria` |
| Entry, pass and exit criteria; failed cases | entry: the last integration step passed on the system build; exit: every case passed on the latest build; a failed case gets a problem report | `Criteria` |
| Who runs the tests and how results reach the repository | the bench team exports a JUnit report; the case IDs are in the test names | `Environment and tools`, `Responsibilities` |
| Tester independence | testers did not develop the system elements; a separate team | `Responsibilities` |

## Template

Parts of the plan, as the schema asks for kind `plan`:

- `Scope`: the test object and its configuration, the requirements covered, and what is
  left to the vehicle level or to the customer.
- `Approach`: derivation from the criteria; stimuli; measurement points; fault
  injection; requirements verified by other methods; selection and regression rules.
- `Criteria`: entry, pass, exit, and the handling of a failed or blocked case.
- `Environment and tools`: the benches or vehicles with the names used as `environment`,
  the tools that produce the report, how records are written (`tools/record.py` from the
  bench's report).
- `Responsibilities`: who specifies, who executes, who accepts; tester independence.

Write each part for the project; do not copy values from another project.

## Notes

- The toolkit does not reach the bench. The strategy says which report format the bench
  delivers and that the toolkit records it as received.
- A measurement point is something the system provides or the bench can read without
  changing it. A criterion that cannot be shown on the integrated system is named in the
  case with the method that shows it; the strategy says that this is allowed and who
  agrees to it.
- Fit the strategy to the release plan and the project plan: the releases and dates it
  names are those of the milestones.
- The plan carries no links. A change of the strategy concerns every case; review them
  against it once the changed plan is approved again.
