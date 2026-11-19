# Cybersecurity goals and claims

Folder `spec/cybersecurity/goals/`. The checklist is `cybersecurity-goal.md`.

## Goal

Type `cybersecurity-goal`, prefix `CSG`. A goal is a requirement at the level of the
item: what is protected against what, not how. The how is the concept's work
(`/cybersecurity-concept`).

```yaml
id: CSG-0001
type: cybersecurity-goal
title: Close requests are authentic
status: draft
links:
  addresses: [THR-0001]
```

```markdown
## Statement

The item shall act only on close requests of other doors that come from the body
controller and have not been changed on their way.

## Rationale

THR-0001 (risk value 5, reduce).
```

- One goal may address several threat scenarios when one protection serves them all;
  it must fit each of them.
- `cal` is set only where the plan's `Approach` uses cybersecurity assurance levels,
  and by the rule written there.

## Claim

Type `cybersecurity-claim`, prefix `CLM`. A claim argues why a shared or retained risk is
acceptable, and how that stays true.

```yaml
id: CLM-0001
type: cybersecurity-claim
title: Remote path through the gateway is the customer's
status: draft
monitored_by: "trigger 'gateway advisory' of the cybersecurity-monitoring plan"
links:
  addresses: [THR-0001]
```

Sections: `Claim` - what is argued; `Rationale` - the facts it rests on, for example the
gateway filter the customer confirmed in query QRY-0004 and the interface agreement that
assigns the gateway to the customer.

A shared risk needs the other party's agreement: a communication record with
`agreement`, or the interface agreement. Without it, the claim states what is assumed
and the check `GOAL-14` stays open.
