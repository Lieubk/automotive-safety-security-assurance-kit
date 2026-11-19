# From goals to requirements

The example continues the power window TARA of `/tara` (`references/threats-and-rating.md`
there). Values are invented.

## Controls

A control is what protects the asset on an attack path. Name it per path of the threat
scenarios the goal addresses:

| Threat scenario, path | Control | Kind |
|---|---|---|
| THR-0001, diagnostic port -> body bus | message authentication of close requests with a freshness value | technical, in the item |
| THR-0001, telematics -> gateway -> body bus | the gateway filters body frames from the telematics unit | technical, in the environment |
| THR-0001, workshop tester | diagnostic routines need a security access level | technical, in the item |

Weighing alternatives (authentication on the bus or plausibility of the request against
the local switch) is a design decision: `/sw-architecture` or `/sys-architecture`.

## Requirements

A requirement of the concept states what is protected, verifiably, not the algorithm:

```yaml
id: SWR-0021
type: software-requirement
title: Close requests of other doors are accepted only when authentic
status: draft
asil: B
security_relevant: true
kind: functional
priority: must
release: R2
verification_method: test
origin: derived
links:
  derived_from: [CSG-0001]
```

```markdown
## Statement

The software shall ignore a close request of another door whose authentication value
does not match or whose freshness value is not newer than the last accepted one.

## Verification criteria

A forged frame and a replayed frame each leave the window still; an authentic frame
closes it within 200 ms.
```

A requirement on the operational environment is a system requirement allocated to an
external system element (`kind: external`), for example "the gateway forwards no body
frame received from the telematics unit". It stays visible to the customer as a
requirement, not as an assumption.

## Thread through the levels

| Level | Evidence | Rule |
|---|---|---|
| requirement derived from the goal | `derived_from: [CSG-...]`, `security_relevant: true` | COV-59, COV-60 |
| component or interface that fulfils it | `fulfils`, `security_relevant: true` | COV-60 |
| unit, code | designed and verified as for any unit; coding rules for security-relevant code under `conventions` | SWE.3, SWE.4 rules |
| integration or qualification test | `verifies` the requirement or the component; methods named in the plan | COV-13, COV-14 |
| vehicle validation | system qualification test that `verifies` the goal | COV-62 |
