# Threat scenarios, attack paths and ratings

## Threat scenario

Type `threat-scenario`, prefix `THR`, folder `spec/cybersecurity/tara/`. One scenario is
one way one property of one asset is lost. A threat model helps to be systematic; the
plan's `Approach` names the one the project uses (for example STRIDE, where spoofing
maps to authenticity, tampering to integrity, repudiation to non-repudiation,
information disclosure to confidentiality, denial of service to availability, elevation
of privilege to authorization).

```yaml
id: THR-0001
type: threat-scenario
title: Forged close request of another door
status: draft
property: authenticity
attack_paths:
  - path: "diagnostic port -> body bus -> forged close frame with the identifier of the rear door switch"
    feasibility: high
    factors: {vector: physical, note: "port reachable inside the cabin"}
  - path: "telematics unit compromised -> gateway -> body bus -> forged close frame"
    feasibility: low
    factors: {vector: network, note: "needs a gateway that forwards, see assumption of ITM-0001"}
feasibility: high
risk_value: 5
treatment: [reduce]
links:
  threatens: [AST-0001]
  leads_to: [DMG-0001]
```

Sections: `Description` - the attacker's aim, the asset and property, the cause;
`Treatment rationale` - why this treatment for this risk value.

The values are invented; the plan's matrix decides `risk_value`.

## Attack paths

- Start at an entry point named in the item definition (an interface, a port, a physical
  access) and end at the asset. Each step is something an attacker does or needs.
- A path that relies on an assumption of the item definition names it. If the assumption
  falls, the path's rating changes.
- Rate each path by the plan's `feasibility_approach`:
  - attack potential: rate the factors the plan defines (elapsed time, expertise,
    knowledge of the item, window of opportunity, equipment) and record them under
    `factors`; the sum or table of the plan gives the level;
  - CVSS: record the exploitability metrics under `factors`;
  - attack vector: record the predominant vector under `vector`; suitable early, when
    the paths are not known in detail.
- The scenario's `feasibility` is the highest of its paths (`COV-56`).

## Risk value

`python tools/traceability.py tara` shows, per scenario, the highest impact of the damage
scenarios it leads to, its feasibility and the value of the plan's `risk_matrix`. Write
that value. The engine does not choose between per-category values: it takes the
highest impact, which is the conservative reading; a plan that wants a value per
category writes one threat scenario per damage scenario.

## Treatment

| Option | Means | What follows |
|---|---|---|
| avoid | remove the function, the interface or the entry point | a design decision; the scenario is then rejected or its path is gone |
| reduce | protect the asset | a `cybersecurity-goal` that addresses the scenario (`COV-58`) |
| share | another party carries the risk (contract, the customer's measures) | a `cybersecurity-claim`, and the party's agreement in the interface agreement |
| retain | accept the risk | a `cybersecurity-claim`; above `retain_up_to`, `decision` with who accepted it, when, why |

Several options can apply together, for example reduce one path and retain the rest.
