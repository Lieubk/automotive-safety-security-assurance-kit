# Supplier selection

Before the agreement: what the candidate was asked, how its capability was evaluated,
and who selected it. Folder `plans/suppliers/`, type `supplier-evaluation`, prefix `SEV`.
The checklist is `supplier-evaluation.md`. The values are invented.

```yaml
id: SEV-0001
type: supplier-evaluation
title: Evaluation of the motor driver software supplier
status: draft
supplier: "Example Drives Ltd., order 4711"
scope_of_supply: "motor driver software component for the bridge, ASIL B"
criteria:
  - {criterion: "process for functional safety at ASIL B", result: met, evidence: "assessment report of their last product, 2025"}
  - {criterion: "cybersecurity process for the delivered software", result: partly-met, evidence: "vulnerability handling defined, no TARA practice yet"}
  - {criterion: "competence of the named team", result: met, evidence: "CVs and trainings shown in the audit of 2026-02-10"}
result: selected-with-conditions
decided_by: "Purchasing and project lead, 2026-02-20"
```

Sections:
- `Request for quotation` - what was asked for functional safety and cybersecurity: the
  activities, work products and interface agreement the project expects;
- `Evaluation` - what the evidence of each criterion showed;
- `Decision` - the selection, its conditions and how they are followed up (in the supplier
  agreement, the development interface agreement or the cybersecurity interface agreement).

`COV-76` matches the `supplier` of each supplier agreement with an approved evaluation
that selected it: write the name the same way in both.
