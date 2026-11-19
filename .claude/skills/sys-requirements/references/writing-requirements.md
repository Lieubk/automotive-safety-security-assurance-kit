# Writing a system requirement

## The statement

| Rule | Poor | Better |
|---|---|---|
| One need per requirement. "and", "as well as", "also" between two obligations means two items. | The door module shall detect an obstacle and reverse the glass. | Two items: one for the force limit, one for the reversal. |
| State what is needed at the boundary of the system, not how it is built or which part does it. A solution imposed by the stakeholder is a constraint and is marked as one. | The ECU shall read the motor current with a shunt and a 12-bit converter. | The door module shall detect contact with an obstacle at a force of at most 80 N. |
| Make it verifiable: a value, a unit, a tolerance, a condition. | The window shall close quickly. | The window shall close from fully open to fully closed in 4.0 s +/- 0.5 s. |
| Name the condition under which it applies: operating mode, voltage range, temperature. | The door module shall limit the closing force. | While the window closes with an opening of more than 5 mm, the door module shall ... |
| One term for one thing, everywhere, and the term of the stakeholder where there is one. | - | - |
| "shall" for `priority: must`, "should" for `priority: should`. No "will", "may", "can". | The door module will report ... | The door module shall report ... |
| No explanation inside the statement. Reasons go to `Rationale`, background to `Analysis`. | ... shall stop the motor to protect the driver stage. | Statement without the reason; reason in `Rationale`. |
| Positive wording where possible; a prohibition only when the prohibition is the need. | shall not be too slow | shall complete within ... |
| No open lists and no escape words: "etc.", "and so on", "if possible", "as appropriate", "normally". | - | - |
| Refer to other items by ID, not by "the above" or "see chapter". | as described above | as specified in SYR-0004 |
| Do not say "hardware" or "software" in a system requirement unless the stakeholder prescribes it; that is allocation. | The software shall ... | The door module shall ... |

Useful patterns, with the system or the product as subject:

- Always: `The <system> shall <response>.`
- State: `While <state>, the <system> shall <response>.`
- Event: `When <trigger>, the <system> shall <response> within <time>.`
- Fault: `If <unwanted condition>, the <system> shall <response>.`
- Option: `Where <variant or feature is present>, the <system> shall <response>.`

## What makes a set of requirements good

- Complete for its parents: reading only the children, nothing the stakeholder demands
  is missing. Check operating modes, start-up and shutdown, the range of supply voltage
  and temperature, failure of each neighbour (power, network, sensors), and the limits
  of every value.
- Free of overlap: no two items regulate the same behaviour differently.
- Consistent in values: a time, threshold or range that appears in two items is the
  same in both, or one item refers to the other.
- At one level: a system requirement constrains the system as seen from outside. If it
  names a component, a signal of the internal design or a part number, it is design -
  unless the stakeholder imposes it, then it is a constraint.
- Parameters that shape behaviour (a threshold, a calibratable time, a variant option)
  are stated with range, default and unit, so that they can be verified.

## Kind

| `kind` | Use for | Example |
|---|---|---|
| `functional` | behaviour: inputs, outputs, modes, reactions | reversal after contact with an obstacle |
| `non-functional` | timing, accuracy, robustness, lifetime, diagnosability, environmental conditions | closing time, operating temperature range |
| `interface` | what crosses the boundary of the system: signals, supply, connector, protocol, mechanical mounting | supply voltage range, position message on the vehicle network |
| `constraint` | a restriction on the solution imposed from outside | a prescribed bus system, a mounting space, a standard to comply with |

## The operating environment

For each requirement ask what it asks of the neighbours of the system: the power supply,
the vehicle network and the other ECUs on it, the mechanics the system moves, the user
and the service tool. What a neighbour must provide or tolerate goes to `Analysis`; what
crosses the boundary and must be fixed becomes an `interface` requirement, which the
`system-interface` items of `/sys-architecture` later fulfil. What cannot be settled
without the stakeholder is a query.

## Verification criteria

A criterion says what is observed, under which stimulus and conditions, and which result
counts as fulfilled. Someone who has not written the requirement must be able to build a
system qualification test case from it (`/sys-qualification-test`).

- Poor: "Test that reversal works."
- Better: "A 10 N/mm test body is placed in the path of the glass at 150 mm and 400 mm
  opening. After contact the glass has moved 50 mm downwards within 200 ms, at 9 V,
  13.5 V and 16 V."

Give the conditions that vary (voltage, temperature, mode) and the number of runs, or
say that the range is covered by the extremes. If the requirement cannot be tested (a
constraint on how something is built, a property shown by analysis), say which method
applies and what evidence the method produces.

## Requirements without a parent

A requirement with `origin: internal` exists because the system needs it although no
stakeholder asks for it: a plausibility check, a safe state, a diagnostic. Its
`Rationale` says why the system needs it and what would go wrong without it. If the need
really belongs to the stakeholder, it is a query to them, not an internal requirement.

## ASIL and security relevance

- A requirement inherits the ASIL of the requirement it is derived from.
- Assigning a lower ASIL is a decomposition. It is decided by people, recorded as an
  approved `design-decision` that concerns the item, and never done silently.
- `security_relevant: true` when the requirement protects an asset or implements a
  security control named by the inputs.
