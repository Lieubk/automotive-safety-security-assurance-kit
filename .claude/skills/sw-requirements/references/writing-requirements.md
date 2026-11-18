# Writing a software requirement

## The statement

| Rule | Poor | Better |
|---|---|---|
| One need per requirement. "and", "as well as", "also" between two obligations means two items. | The software shall detect an obstacle and reverse the motor. | Two items: one for detection, one for the reversal command. |
| State what is needed, not how it is built. A solution imposed by the customer is a constraint and is marked as one. | The software shall debounce the switch with a 4-sample ring buffer. | The software shall accept a switch request only after it has been stable for 20 ms. |
| Make it verifiable: a value, a unit, a tolerance, a condition. | The software shall react quickly to an obstacle. | The software shall command motor reversal no later than 10 ms after an obstacle is reported. |
| Name the condition under which it applies. | The software shall limit the closing force. | While the window closes automatically and its position is inside the protected zone, the software shall ... |
| One term for one thing, everywhere. Decide once whether it is "window position" or "glass position". | - | - |
| "shall" for `priority: must`, "should" for `priority: should`. No "will", "may", "can". | The software will report ... | The software shall report ... |
| No explanation inside the statement. Reasons go to `Rationale`, background to `Analysis`. | ... shall stop the motor to protect the driver stage. | Statement without the reason; reason in `Rationale`. |
| Positive wording where possible; a prohibition only when the prohibition is the need. | shall not be too slow | shall complete within ... |
| No open lists and no escape words: "etc.", "and so on", "if possible", "as appropriate", "normally". | - | - |
| Refer to other items by ID, not by "the above" or "see chapter". | as described above | as specified in SWR-0004 |

Useful patterns:

- Always: `The software shall <response>.`
- State: `While <state>, the software shall <response>.`
- Event: `When <trigger>, the software shall <response> within <time>.`
- Fault: `If <unwanted condition>, the software shall <response>.`
- Option: `Where <variant or feature is present>, the software shall <response>.`

## What makes a set of requirements good

- Complete for its parents: reading only the children, nothing the parent demands of
  the software is missing. Check start-up, shutdown, each operating mode, each failure
  of an input, and the limits of every value.
- Free of overlap: no two items regulate the same behaviour differently.
- Consistent in values: a time, threshold or range that appears in two items is the
  same in both, or one item refers to the other.
- At one level: a software requirement constrains the software as a whole. If it names
  a component, a function or a variable, it is design.

## Kind

| `kind` | Use for | Example |
|---|---|---|
| `functional` | behaviour: inputs, outputs, modes, reactions | reversal on a reported obstacle |
| `non-functional` | timing, resource use, robustness, diagnosability | worst-case reaction time, memory limit |
| `interface` | what crosses the software boundary: signals, services, data formats | resolution and range of the position signal |
| `constraint` | a restriction on the solution imposed from outside | language standard, a prescribed platform service |

## Verification criteria

A criterion says what is observed, under which stimulus, and which result counts as
fulfilled. Someone who has not written the requirement must be able to build a test
case from it.

- Poor: "Test that reversal works."
- Better: "With a speed drop of the detection threshold plus one step injected at any
  position inside the protected zone during automatic closing, the reversal command is
  present no later than the second 5 ms cycle after the drop."

If the requirement cannot be tested (a constraint on how something is built, a
property shown by analysis), say which method applies and what evidence the method
produces.

## Requirements without a parent

A requirement with `origin: internal` exists because the software needs it although no
input asks for it: a plausibility check, a defensive default, a diagnostic. Its
`Rationale` says why the software needs it and what would go wrong without it. If the
need really belongs to the system, it is a query to the source of the inputs, not an
internal requirement.

## ASIL and security relevance

- A requirement inherits the ASIL of the requirement or element it is derived from.
- Assigning a lower ASIL is a decomposition. It is decided by people, recorded as an
  approved `design-decision` that concerns the item, and never done silently.
- `security_relevant: true` when the requirement protects an asset or implements a
  security control named by the inputs.
