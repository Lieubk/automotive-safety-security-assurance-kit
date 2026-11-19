# Proven in use argument

Folder `spec/safety/proven-in-use/`, type `proven-in-use-argument`, prefix `PIU`. The values
are invented; the incident rate limit is the project's statement in the safety plan, not a
value taken from the standard.

```yaml
id: PIU-0001
type: proven-in-use-argument
title: Hall sensor evaluation of the door module, carried over unchanged
status: draft
candidate_version: "HallEval 3.2.1 as built in the door module series since 2023"
credit: ["6:8", "6:9"]
target_asil: B
incident_rate_limit: "as the safety plan PLN-0010 states for table 8:6, ASIL B"
evaluation_hours: "4.1e8 h from 96 000 vehicles, each counted after its first year in service"
observed_incidents: 0
result: obtained
evidence: "change history of HallEval 3.2.1 (no change since release); field returns database extract 2026-10; problem reports PRB-0003 to PRB-0005 analysed as unrelated"
links:
  qualifies: [CMP-0003]
```

Sections:
- `Candidate` - what the candidate is and consists of, at which version; its fit, form and
  function; the safety requirements and ASILs of its previous use where they are known;
- `Modifications` - changes since the evaluation period to the candidate (design,
  implementation, configuration, calibration) and to its environment, and for each the
  analysis that the status still holds;
- `Field data` - how configuration and change management covered the evaluation period;
  which specimens count and why; the calculation of the evaluation period; the incidents
  found and their analysis; what was done for failure rates that depend on wear or age;
- `Conclusion` - the status reached, the credit it gives, and what the item still needs
  (integration, safety validation, confirmation measures).
