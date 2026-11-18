# Evaluating the detailed design

SWE.3.BP4 asks that the design is judged before it is built. The judgement is the
content of the `Design evaluation` section of each `component-design`; a choice between
alternatives is a `design-decision` item. Worked examples: CDS-0001 and CDS-0002.

## 1. Criteria first

An evaluation without criteria is an opinion. Before writing a result, establish what
the project measures the design against:

1. Read `conventions.design_limits` in `project.yaml`. Where it is empty, ask the user
   where the project's evaluation criteria and limits are written: an approved
   `component-design` that already states them, the approved `plan` of kind
   `unit-verification` (its `Criteria` section may hold complexity limits and what
   each ASIL means for verification), a customer requirement, a project guideline.
   Once they are decided, propose to record where they are under
   `conventions.design_limits` with `/aspice-start`.
2. If they exist, use them as they are and refer to them. CDS-0002 does it in one
   line: "Limits as in CDS-0001."
3. If they do not exist, propose a set and let the user decide. The set has two parts:
   the six aspects below, and numeric limits for what can be counted. The worked
   example uses, for hand-written units: cyclomatic complexity at most 10 per
   function, nesting depth at most 4, at most 4 parameters, no recursion, no dynamic
   memory. These are example values, not a recommendation for every project.
4. Write the decided criteria once, at the top of the `Design evaluation` of the first
   component design, and refer to that item from the others. Do not paste the scale
   into every component. Write who decided them, by name or role as the user states
   it (SDD-56 asks for it).

The six aspects come from the process: interaction, interoperability, criticality,
technical complexity, testability, risks. A project may add its own (memory or timing
margin, portability, reuse).

## 2. One result per aspect

Each result is a finding about this component, supported by something in the design
that a reviewer can check. A sentence that would fit any component is not a result.

| Aspect | Question | Take the answer from | Example of a result (worked example) |
|---|---|---|---|
| Interaction | Do the units work together correctly over time: call order, start-up order, concurrency, a partner that fails or is late? | `Dynamic behavior`, `preconditions`, `protection`, the execution model | "One call from interrupt, one from the task, two read functions. The only shared data is the pulse data of UNT-0001, guarded by one exclusive area." |
| Interoperability | Does every unit fit its callers, its callees and the platform: types, units, ranges, error values on both sides of each call; which headers, services, compiler properties does it depend on? | `arguments` and `returns` against the interface items; `platform`; includes named in `Static structure` | "Depends on `Std_Types.h` only. Repeats the value ranges of two interfaces as constants; a change of IFC-0002 or IFC-0005 has to be followed here by hand." |
| Criticality | How much depends on this unit, and what follows for its verification? | `asil`, `security_relevant`, what a wrong output causes | "ASIL B, the unit that decides whether the window reverses. Full unit verification of the project; in addition every comparison limit has a unit test on both sides." |
| Technical complexity | Is the design inside the limits, and could it be simpler? | count from the design: decisions per function, nesting, parameters, states and transitions, call depth | "Highest cyclomatic complexity 6 (`AntiPinch_StepMonitoring`), nesting depth at most 3, at most 3 parameters. Within the limits." |
| Testability | Can every input be set and every output observed from a test; what must be stubbed; is every path reachable; is time under control of the test? | `arguments`, getters, `uses` links, the state diagram | "No stub needed. Every state is reachable by argument sequences. Time is counted in calls, so a test of the 2 s limit runs in microseconds. Not reachable from outside: a corrupted state variable." |
| Risks | What can still go wrong technically, although the design is as intended? | everything above, open assumptions, values not yet confirmed, dependence on what others deliver | a row per risk, see section 4 |

Not an evaluation:

- quoting the limits and naming the tool that will check them later;
- "testability is ensured by unit tests";
- the same paragraph in every component with the name exchanged;
- a criticality class without saying what it changes in the verification.

## 3. Figures: estimate now, measure later

Before code exists, complexity and resource figures are estimates read from the design:
count the decisions the described behaviour needs per function, the nesting the steps
imply, the parameters in `functions`. Say that they are estimates. Never write a
measured-looking figure nobody measured.

After implementation the figures are measured: `/sw-unit-verify` runs the analyser,
and a static analysis run can carry the measured values per unit as `metrics`. A
measured value that breaks a limit, or that differs so much that the result no longer
holds, comes back as a finding against the design. The owner then changes the design or records
the excess as a risk with its reason; the item changes, and its review is repeated.

A function that is over a limit on paper is redesigned now: split a step into a local
function, turn nested conditions into a state or a table. Accepting an excess is a
decision of a person, with the reason and the extra verification written next to it.

## 4. Risks with owners

One row per risk:

| Column | Content |
|---|---|
| Risk | the technical condition, concrete enough to recognise when it occurs: "run-out pulses after a change of direction are counted in the new direction (up to 3 per change)" |
| Effect | what it does to the product, with a size where possible: "position error of up to 1.5 mm per change" |
| Measure | what is done about it and by when it is known to work, or "accepted" with the reason and the item that carries the reason |
| Owner | the role or person who follows it up |

- Ask the user for every owner. Do not fill in a role because it sounds plausible.
- "Accepted" is a statement of the owner. Record it only when the user says who
  accepted the risk.
- A risk that belongs to someone outside the project (a value the customer has to
  confirm, a measurement only possible on the target) names what the project does:
  raise it, with whom, and what the design does until the answer arrives.
- A risk that turns out to be a missing requirement or an architecture gap is also a
  query to the owner of that item.

## 5. Every negative result has a consequence

For each aspect that shows a problem, the section says which of these happened:

1. the design was changed (say how);
2. it is a risk with measure and owner;
3. it was accepted by a named role, with the reason.

The evaluation also steers work downstream. Say explicitly what it means for:

- unit verification: which units need more than the standard set (boundary tests on
  both sides of every limit, injected failures of called functions), which stubs the
  tests need, which branch cannot be reached and why;
- integration: orders, timings and platform resources that only the integrated
  software can confirm (the execution time of the interrupt, the configured exclusive
  area).

## 6. Design decisions at detailed-design level

Write a `design-decision` with `level: detailed-design` when all three hold: there were
at least two workable alternatives, they differ in something measurable or in what
other parties have to provide, and someone will ask later why it was done this way.
Typical subjects: the algorithm of a detection, the number format of a filter, the way
shared data is kept consistent, the cut between units, table against calculation.

- `Context`: the need and the constraints, with the IDs of the items that set them.
- `Evaluation criteria`: derived from requirements, budgets and the aspects above,
  fixed before the alternatives are assessed.
- `Alternatives`: each one described so that it could be built, and assessed against
  every criterion in one table.
- `Decision`, `Consequences`: what was decided, why, by whom and when, as the user
  states it; what follows for units, interfaces, configuration and verification.
- `links.concerns`: the `component-design` and `software-unit` items the decision
  shapes.

Choices with no real alternative stay in `Design concept` under "Decisions taken
here". A decision that changes what the component offers or needs is not a detailed
design decision: it goes back to the architecture.

A unit with a lower ASIL than its component or than a requirement it implements needs
an approved decision that documents the decomposition and concerns the unit. People
take that decision; the skill drafts the alternatives and never lowers an ASIL itself.
