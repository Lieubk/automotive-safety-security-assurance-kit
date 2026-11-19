# Safety plan

File `plans/PLN-NNNN.md`, type `plan`, `kind: safety`. One per project; the checklist is
`plan.md`, part "Kind safety".

## Decisions to ask before drafting

| Decision | Typical options | Lands in |
|---|---|---|
| Safety manager and the other safety roles | named by the user; roles, not names, in the plan | `Responsibilities` |
| What is new, changed, reused, and what follows for the activities (impact analysis) | new development; modification of a predecessor; reuse unchanged with an argument | `Scope` |
| The decision per clause of the parts in scope | performed, tailored, not-applicable, by-customer, by-supplier, by-organization | `safety_activities` |
| The methods per table of parts 4, 5, 6, 8 in scope, per ASIL | as the responsible people read the standard; where written | `method_selection` |
| ASIL determination, tool confidence determination | typed from the project's copy of the standard | `asil_determination`, `tcl_determination` |
| Confirmation reviews, audit, assessment: what, when, with which independence, by whom | as the responsible people read the standard for the ASIL | `confirmation_measures` |
| Interfaces with customer and suppliers | the development interface agreement and who does what | `Scope`, `Responsibilities` |

## Template

The values are invented for the power window example. Entries are listed in part; a
real plan has one per clause and per table in scope. The determinations are left to the
project: this template does not carry the standard's tables.

```markdown
---
id: PLN-0009
type: plan
title: Safety plan of the window control software
status: draft
kind: safety
safety_activities:
  - {clause: "2:6", decision: performed, responsible: Safety manager}
  - {clause: "6:7", decision: performed, responsible: Software architect, work_products: ["26262-6:7.5.1", "26262-6:7.5.2"]}
  - {clause: "8:13", decision: not-applicable, responsible: Safety manager,
     rationale: "the software supplier delivers no hardware element"}
  - {clause: "8:5", decision: performed, responsible: Project lead,
     rationale: "development interface agreement with the customer, see Scope"}
  # ... one entry per clause of every part in scope.safety
method_selection:
  - {table: "6:7", decision: applied, asil: [B], applied_in: PLN-0001,
     methods: "the methods for unit verification the unit verification strategy names for ASIL B"}
  - {table: "8:4", decision: not-applicable, rationale: "no tool is classified TCL3"}
  # ... one entry per table of parts 4, 5, 6, 8 in scope
confirmation_measures:
  - {measure: confirmation-review, subject: "safety plan", independence: I1, by: "safety engineer of another project"}
  - {measure: confirmation-review, subject: "software safety analyses", independence: I1}
  - {measure: functional-safety-audit, subject: "implementation of the safety plan", independence: I2}
asil_determination: {}        # the project types the determination it applies, from its copy of the standard
tcl_determination: {}         # likewise
---

## Scope
...
## Approach
...
## Criteria
...
## Environment and tools
...
## Responsibilities
...
```

## Notes

- Quote `"<part>:<clause>"` and `"<part>:<table>"`: unquoted, YAML reads 6:7 as a time.
- `COV-63` compares `safety_activities` with the catalog `iso-26262/2018/catalog.yaml`;
  `COV-64` compares `method_selection` with the tables listed there.
- The subjects of `confirmation_measures` are the names `record.py confirmation-measure`
  is given; `COV-73` matches them letter for letter.
