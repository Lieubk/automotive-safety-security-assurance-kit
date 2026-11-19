# Hazardous events and safety goals

The values are invented for the power window example. The classifications are examples
of the form; the project's people rate, and the ASIL comes from the determination the
safety plan states.

## Hazardous event

Folder `spec/safety/hara/`, type `hazardous-event`, prefix `HZE`.

```yaml
id: HZE-0001
type: hazardous-event
title: Window closes against a child's neck while parked
status: draft
malfunction: "automatic closing does not reverse at an obstacle"
hazard: "trapping and strangulation by the closing window"
operational_situation: "vehicle parked, child in the rear seat with the head out of the window, closing started by the driver"
severity: S3
exposure: E2
controllability: C3
asil: B
links:
  arises_in: [ITM-0001]
```

Sections: `Description` - what happens, to whom, in which situation;
`Classification rationale` - one reason per rating, who rated, the source of the
exposure (field data, driving cycles, the customer's statement).

The ratings above are an example only. Do not take ASILs from this page.

## Safety goal

Folder `spec/safety/goals/`, type `safety-goal`, prefix `SG`.

```yaml
id: SG-0001
type: safety-goal
title: The window does not trap an occupant
status: draft
asil: B
safe_state: "window stopped and reversed by at least the reversal distance"
ftti_ms: 300
links:
  addresses: [HZE-0001]
```

Section `Statement`: what must not happen, at vehicle level, without naming a solution.
`Rationale`: the events it answers and why one goal covers them.

## Guide words for malfunctions

A plan may name its own. A common set: no function; function without request;
function opposite to the request; too much or too fast; too little or too slow; too
early; too late; stuck; intermittent.
