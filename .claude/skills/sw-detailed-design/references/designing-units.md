# Designing components and units

How to get from a component of the architecture to units a developer can implement.
Item layout: `item-templates.md`. Complete items of the quality aimed at:
`examples/power-window/spec/software/design/`.

## Which component gets a detailed design

| Component (`software-component`) | What this skill writes |
|---|---|
| `origin: developed`, `kind` other than `composition` | one `component-design` that `refines` it and at least one `software-unit` that is `part_of` it. `COV-09` reports a developed component that lacks either |
| `kind: composition` | nothing. A composition has no behaviour of its own; its parts are designed |
| `origin: reused` or `supplied` | nothing. The design belongs to whoever developed the component and comes with it in the form `supplier` states. Its interfaces are used as they are; a gap in them is a query to the architecture owner |
| `origin: generated` | nothing by hand. The input of the generator is the design; the hand-over says where it is kept |

In the worked example WindowPos (CMP-0003) and AntiPinch (CMP-0004) are designed.
WindowCmd and MotorDrive are reused, the basic software is supplied: none of the three
has a design item, and the design of AntiPinch treats MotorDrive as a given.

A reused component that has to be modified is no longer reused. Changing its `origin`
is an architecture decision; only after that change is approved does it get a design.

## What a unit is

A `software-unit` item is the smallest piece that is designed, implemented and verified
as a whole. In C it is normally one source file with its header. Every file under the
source roots belongs to exactly one unit (`COV-11`), and every unit to exactly one
component (`COV-10`). Functions, types, constants and variables are design elements
inside the unit; a function is addressed as `UNT-0003#AntiPinch_Step`.

A unit is designed and approved before it has code. The design names the files the
unit will consist of in `Static structure` of the component design. The attribute
`source_files` lists files that exist: it is left out while there is no code, and
`/sw-unit-implement` adds it when the files are written. Until then the check reports
the unit as "designed but not implemented" (`COV-10`) and its verification rules as
pending; these are warnings once the unit is approved, so the design can be baselined.
`source_files` is not part of the content hash of the item: registering the code later
leaves the design approval valid. When the design of existing code is written or
reworked, `source_files` names that code from the start.

## Splitting a component into units

Look for the lines that run through the component, and cut along them:

| Line | Why a cut there pays | Power window |
|---|---|---|
| Execution context | interrupt-level code has to be short and bounded and is reviewed differently from task code; the data both sides share gets one owner | HallCapture runs in the capture interrupt, WindowPos in the 5 ms task (CDS-0001) |
| Platform or hardware access against logic | the logic compiles and runs on a host unchanged, so it can be unit tested without the target | both units receive time stamps and the drive direction as arguments |
| Reasons to change | a new threshold must not force a re-test of the pulse capture | edge acceptance in one unit, position and speed arithmetic in the other |
| ASIL | the code that needs the full set of safety measures stays small; a mixed unit carries the highest ASIL everywhere | a QM diagnostic read-out would not live in the unit that decides the reversal |
| Kind of behaviour | a state machine is tested with sequences, a calculation with value classes; mixed units need both everywhere | - |
| Origin | `origin` is set per unit: generated and handwritten code never share a unit | - |

Do not cut where the parts work on the same data and always change together. Then one
unit with local functions is the better design: AntiPinch is one unit whose eight local
functions carry one state or one transition each (CDS-0002).

Signs that a split is wrong:

- a unit whose purpose needs an "and" between two unrelated things;
- two units writing the same variable;
- a cycle in the `uses` links;
- a unit that cannot be tested without the real code of another one;
- a "common" or "utilities" unit that collects what did not fit elsewhere;
- one unit per function, with the behaviour visible only in how they call each other.

Record the reason for each cut in `Design concept`. "Split where its two execution
contexts meet" (CDS-0001) is a reason; "split for modularity" is not.

Then make the assignment complete:

- every requirement allocated to the component belongs to at least one unit;
- every operation or data element of a provided interface is served by exactly one unit;
- every used interface is used by a named unit;
- a unit to which no requirement and no interface leads is removed, or its reason is
  written into its `Purpose` (start-up code the architecture implies, for example).

## How much detail

A unit design is detailed enough when both hold:

1. **Two developers** who implement it independently produce units that can be swapped:
   same signatures, same results for every input including the invalid ones, same
   effect on stored data. Neither had to choose anything that changes behaviour.
2. **A tester** who sees only the design can list the classes and limits of every
   input, the expected result for each, the states and transitions to cover, what has
   to be set up before a call, and what must be replaced by a stub.

What the design decides, so that the developer does not have to:

| Decision | Example from the power window |
|---|---|
| Name, arguments, return type and visibility of every function another unit or the platform calls | `Std_ReturnType WindowPos_GetPosition(uint16 *position)` |
| Type, unit, scaling, range and resolution of every argument, return value and stored value | position in counts of 0.5 mm, 0..960, 65535 = not referenced |
| The reaction to every invalid input and to every failure of a called function | direction above 2: refuse the step before anything is read |
| States, and what each event does in each state | IDLE, SETTLING, MONITORING, REVERSING with every transition |
| The algorithm wherever two sensible choices give different numbers: filter, rounding, saturation, debouncing, order of updates | reference speed: `stored - stored / 16 + speed`, division rounding down |
| Number representation and overflow | unsigned differences modulo the width of the type; 4 fractional bits |
| What must have happened before a call, and the order of calls | `HallCapture_Init` before `WindowPos_Init` |
| Execution context, period and what can interrupt what | interrupt writes, 5 ms task reads one copy |
| Protection of everything more than one context touches | exclusive area HallData around four assignments |
| Every number with a meaning, as a named constant with value and unit | `ANTIPINCH_CONFIRM_CYCLES`, 2 cycles (10 ms) |
| Which platform services are used and what is done when they fail | - |
| Resource objectives where the component has a budget | `resource_budget` of the unit inside that of the component |

What stays with the developer: names of local variables, the order of statements where
it does not change the result, how a loop or a condition is written, and anything the
coding rules already settle.

The opposite failure is a design that transcribes code. It cannot be reviewed before
the code exists, it says nothing the code does not say, and it is wrong after the next
commit. The same behaviour at three levels:

| Level | Text |
|---|---|
| Too little | "The unit filters the speed and reports an obstacle when the speed drops." Which filter, which constant, how rounded, when is the reference held? Two developers would build two detectors. |
| Right | "Update per cycle: stored = stored - stored / 16 + speed, with the division rounding down, then limited to at least 800 (50 mm/s). A drop is speed + 20 < reference; while a drop is pending the reference is not updated." (UNT-0003) |
| Too much | "Declare a 16 bit variable for the filtered value. Shift the stored reference right by four and subtract the result from the stored reference. Add the speed. If the sum is below 800, assign 800. Assign the sum to the stored reference." One sentence per statement; the reason for the limit is gone. |

Marks of transcription: local variable names in the text, a flow chart with one box per
statement, steps whose order does not matter given as a sequence, and a function that
only returns a stored value described in a paragraph. Such a function needs its
contract and nothing else.

When code already exists and the design is written afterwards, say so to the user and
in `Design notes`. Write contracts, states, decisions and their reasons all the same,
and let the review judge the design, not its resemblance to the code.

## The function contract (`functions`)

An entry must determine exactly one C prototype and tell a caller everything they may
rely on.

| Key | Write | Needed for |
|---|---|---|
| `name` | the final C name, following the project's naming convention | every function |
| `category` | `public` (called by other units or components), `scheduled` (activated by the scheduler or the runtime environment), `callback` (called by the platform or from an interrupt), `local` (file-local) | every function |
| `description` | one sentence, only if `Purpose` and `Behavior` do not already say it | optional |
| `arguments` | in call order; each with `name`, `direction` (`in`, `out`, `inout`) and `type` as it will stand in C, with `const` and `*` in their place, quoted when it holds `*` (`"const HallCapture_SnapshotType *"`). Physical values also get `unit`, `min`, `max`, `resolution`; a value that marks "invalid" goes into `invalid`. `description` says what the value is and, for pointers, whether null is allowed and who owns the object. `[]` for no arguments | every function |
| `returns` | one entry `{type, value, meaning}` per value or value class; `meaning` says when exactly it is returned. The return type of the function is `return_type`, or the one `type` given in every entry, as the worked example does; use one form throughout the project. A function that returns nothing has one entry with `type: void` | every function |
| `preconditions` | what the caller guarantees: initialisation, call order, context | public, scheduled, callback |
| `postconditions` | what holds afterwards, per outcome: which data changed, in which range, and what is unchanged after a failure | public, scheduled, callback |
| `errors` | one `{condition, reaction}` per error the function detects or receives: the exact condition, and what is returned, written and left untouched | public, scheduled, callback; `[]` when it cannot fail |
| `trigger` | the event that activates it: the task and position in the task, the interrupt, the runtime environment event | scheduled, callback |
| `period_ms` | the period of a periodic activation | scheduled, when periodic |
| `call_context` | `task`, `interrupt` or `both` | public, scheduled, callback |
| `reentrant` | `true` only if concurrent calls are safe by design | public, scheduled, callback |

Rules:

- The types are compared with the code. Once the unit has source files, `COV-22`
  reports every designed function whose parameter types, in their order, or whose
  return type differ from the code; spacing does not count, the words and their order
  do. An argument without `type`, or `returns` entries that name different types, take
  the function out of that comparison. Leave no type open.
- Where the architecture fixes an operation (`operations` of a `function-call` or
  `client-server` interface), name and arguments are taken over unchanged. In the
  example `HallCapture_OnEdge` of UNT-0001 equals the operation of IFC-0001.
- Ranges fit the type, and they agree with the interface item on both sides of a call.
  A value that is legal although it looks invalid is said to be legal ("65535 = not
  referenced, a legal value").
- Every error return listed in `returns` has an entry in `errors`, and the other way
  round.
- A `local` function is listed when `Behavior` refers to it: one per state, per
  transition, per calculation step. It gets name, arguments and return values; the
  rest of its behaviour is described where the unit's behaviour is described. Helpers
  that only shorten code are left to the developer.

## Data (`data`)

One entry per variable that keeps its value between calls.

| Key | Write |
|---|---|
| `name` | the final C name |
| `type` | the C type |
| `scope` | `file` as the rule. `global` only with the reason in `Design notes`: other units then depend on the variable and not on a function |
| `unit`, `min`, `max` | for every value with a range; the unit includes the scaling ("0.5 mm", "1/16 mm/s") |
| `initial` | the value after initialisation; quote `"FALSE"` and `"TRUE"` |
| `protection` | what guards concurrent access, or why none is needed, with the contexts named: "exclusive area HallData; written in Isr_HallCapture", "none needed: task level only" |

`protection` is never left empty. "None needed" is a design statement that the review
checks against the execution model.

## Types and constants

Types and constants the unit defines are part of `Behavior`, as tables: for a structure
every member with type, meaning and range; for a constant its name, value with unit,
and meaning. The names are final; the code uses exactly these. A number that appears in
the behaviour text without a name is a finding.

## What goes into which section

| Section | Content | Not here |
|---|---|---|
| `Purpose` | what the unit is for in two or three sentences, and, if it helps, what it deliberately does not do | the algorithm |
| `Behavior` | scaling, types, constants; the algorithm as numbered steps or formulas; states with a diagram and what one step does in each state; initialisation | error cases, timing |
| `Error handling` | a table: error, detected by, reaction, reported how. Then what the unit cannot detect and who covers it | normal behaviour |
| `Dynamic behavior` | execution contexts of the functions, what can interrupt what, protection, timing that follows from the call period, loops and their bounds | the state diagram, if `Behavior` holds it: refer to it |
| `Design notes` | reasons for choices inside the unit, assumptions with their owner, traps for the developer | decisions others depend on: those are a `design-decision` |

Diagrams are code blocks (Mermaid or PlantUML). Every name in a diagram is a design
element that exists in `functions`, `data` or a table. A state machine is complete
when every state says what happens for every event, including "nothing".

## Dynamic behaviour, and when it does not apply

Component design, `Dynamic behavior` - how the units work together:

- start-up: who is initialised before whom, and in which state of the interrupts;
- one activation of every periodic path and every event path, as a sequence diagram
  when more than one unit or context takes part;
- what is shared between contexts and how it is read consistently;
- at least one path in which something fails or arrives late;
- how the component looks from outside: call order in the task, what a caller may
  assume about the freshness of the values.

Unit, `Dynamic behavior` - the unit by itself: contexts, preemption, protection,
states and timing.

`Not applicable:` followed by the reason is the right answer when the item shows all
of this:

- no entry in `data`, so there is no state;
- every function has one `call_context` and is `reentrant: true`;
- no function has a `trigger`;
- the result of a call depends on its arguments only.

A unit that converts a raw value with a table lookup is such a case: "Not applicable:
the unit has no data and no state; both functions are pure and may be called from any
context." For a component design it applies when the component has one unit whose own
section says everything; even then a few lines on how the component looks from outside
are better (CDS-0002).

It is not the right answer for a unit with a scheduled function, with stored data,
with data another context touches, or with a time-out, however small the unit is.
"Not applicable: simple unit" is a finding.

## Links, and what checks them

Every link is written once, on the design item, and can be followed in both directions
with `show` and `matrix`.

| Link | Says | What the trace check reports |
|---|---|---|
| `refines` on the component design | which component this is the design of | `COV-09`: a developed component that does not have exactly one design |
| `part_of` on the unit | which component the unit belongs to | `COV-10`: a unit without exactly one; `COV-09`: a developed component without a unit; `COV-23`: a unit with a lower ASIL than its component |
| `realizes` on the unit | which provided interface the unit serves | `COV-21`: an interface of a developed component that no unit of that component realizes |
| `uses` on the unit | which interfaces and units it depends on at run time | structure only (`LINK`); whether the list is complete is read in the review |
| `implements` on the unit | which requirements it fulfils | `COV-23`: a unit with a lower ASIL than a requirement it implements |
| `source_files` on the unit | which files hold its code | `COV-10`: a listed file that does not exist, or none listed ("designed but not implemented"); `COV-11`: a file under a source root that is not listed by exactly one unit; `COV-22`: a designed function missing in the code, a function in the code missing in the design, or parameter and return types that differ |
| `verifies` on a unit test | which function of the unit a test checks | `COV-29`: a function of category public, scheduled or callback that no unit test names |
| `concerns` on a decision | which design items the decision shapes | `LINK`; an approved decision is the waiver of `COV-23` |

What the check cannot tell is whether a link is true. Read each one in both directions:

- downwards: does the unit do everything the requirement, the interface or the
  component asks of it?
- upwards: is there anything in the unit that no requirement, interface or stated
  reason asks for?

The requirements a component is responsible for are those it `fulfils`: the link is
on the component, `show <component ID>` lists the requirements, and
`show <requirement ID>` lists the component and the units that implement it.
Link a requirement to the unit that fulfils it, not to every unit of the component.
Where a component has one unit, the path requirement, component, unit already exists
and `implements` adds nothing new; the worked example sets it anyway so that the unit
can be read alone.

After the review, the record holds the content hash of every item the design links
to. When one of them changes, the check reports the link as `SUSPECT` until the design
has been reviewed against the new version; `impact <ID>` shows this in advance. The
code of a unit is covered by a review of its own, recorded with the code revision:
that record stores the hash of every source file, so that a later change of the code
shows as `SUSPECT` on the unit as well.

Approval goes from the top down. A design item cannot be approved while an item it
links to - its component, an interface, a requirement, a unit it uses, the design a
decision concerns - is in draft or in review, unless that item is a subject of the
same review: `/review` refuses the verdict, and an approved item above an unsettled
one is reported as `UPSTREAM`. Review a component design, its units and their
decisions together.

## Questions that come up while designing

| The question is about | It becomes | Who answers |
|---|---|---|
| an imported item: a delivered requirement, element, interface or component | a `query` item with an `about` link to that item (`item-templates.md`). While it is open, the check warns with `QUERY` on every approved item it is about | the source of the input, named in `to` |
| an item the project wrote: its architecture, its requirements | a point for the owner of that item, passed on through the user and listed in the hand-over. The owner changes the item with `/sw-architecture` or `/sw-requirements`; it is then reviewed again and the design becomes `SUSPECT` until it has followed | the owner of the item |
| the design itself | a decision in `Design concept`, or a `design-decision` | the user |

Either way the design does not answer the question for the other side. If work goes
on before the answer, the assumption is written into `Design concept` with its owner,
and with the ID of the query where there is one.

## Units with an ASIL

The design, not the developer, defines the safety-related behaviour inside a unit:

- which inputs are checked against which range, and the reaction when the check fails,
  chosen towards the safe state of the function (the window opens rather than closes);
- what happens when a state variable holds a value outside its set;
- which results are limited to their range before they are stored or delivered;
- how data that more than one context touches is kept consistent;
- which data, if any, is stored redundantly or protected by a check value, and what is
  done on a mismatch.

Keep the control flow simple enough to test: no behaviour that depends on hidden
state, no output through side channels, every loop with a bound that is in the design.
The higher the ASIL, the more of the behaviour is expected in a notation with defined
meaning (state diagram plus transition list, sequence diagram, decision table) next to
the prose; the project's safety plan says which notation it requires for which ASIL.
Safety mechanisms are specified like any other behaviour: with condition, reaction and
a place in `Error handling`.

## Writing style

- Present tense, active voice, one statement per sentence: "The step refuses the call."
- One term for one thing, and the same term as the architecture and the requirements.
- Values with units; names of functions, constants and states in code font.
- Refer to other items by ID (SWR-0004, IFC-0002, VIEW-0004), never by "see above".
- No "etc.", "as appropriate", "if necessary", "should normally". A developer cannot
  implement them and a tester cannot test them.
