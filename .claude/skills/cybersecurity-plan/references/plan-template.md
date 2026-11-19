# Cybersecurity plan

File `plans/PLN-NNNN.md`, type `plan`, `kind: cybersecurity`. One per project. The
checklist is `plan.md`, part "Kind cybersecurity".

## Decisions to ask before drafting

| Decision | Typical options | Lands in |
|---|---|---|
| Who is responsible for cybersecurity of the project | a named cybersecurity lead; the project lead with a cybersecurity engineer | `Responsibilities` |
| Which subclause is performed here, tailored, not applicable, done by the customer or by a supplier | per subclause of the clauses in scope (`clauses` lists them) | `cybersecurity_activities` |
| Why a tailored or not-applicable activity still reaches its objective | the user's reason, per entry | `rationale` |
| Impact categories | safety, financial, operational, privacy; a project may add its own | `tara_method.impact_categories`, `impact_meaning` |
| Feasibility approach | attack potential (detailed paths), CVSS (known vulnerabilities), attack vector (early phase) | `tara_method.feasibility_approach`, `feasibility_meaning` |
| Risk matrix | a value 1 to 5 per impact level and feasibility level, rising with both | `tara_method.risk_matrix` |
| Up to which risk value a risk may be retained without a named person accepting it | 1; 2; none | `tara_method.retain_up_to` |
| Threat model for finding threat scenarios | STRIDE per asset property; attack trees; a catalog of the organization | `Approach` |
| Whether cybersecurity assurance levels are used, and how they follow from risk | not used; per goal from the risk value | `Approach` |
| Cybersecurity assessment: whether, by whom, with which independence | none, with the reason; an assessor of another department; an external assessor | `Approach`, `Responsibilities` |
| Reuse, out-of-context and off-the-shelf components | per component of origin reused, supplied, third-party | entries for 6.4.4, 6.4.5, 6.4.6 |

## Template

The values are invented for the power window example. The risk matrix is an example of
the form, not a recommendation: the organization decides its own.

```markdown
---
id: PLN-0009
type: plan
title: Cybersecurity plan
status: draft
kind: cybersecurity
tara_method:
  impact_categories: [safety, financial, operational, privacy]
  impact_meaning: "severe: life-threatening or a total loss of a vehicle function on the road; major: ...; moderate: ...; negligible: ..."
  feasibility_approach: attack-vector
  feasibility_meaning: "high: physical access inside the cabin with common tools; medium: ...; low: ...; very-low: ..."
  risk_matrix:                       # columns: very-low, low, medium, high
    severe:     [3, 4, 5, 5]
    major:      [2, 3, 4, 5]
    moderate:   [1, 2, 3, 4]
    negligible: [1, 1, 2, 2]
  retain_up_to: 1
cybersecurity_activities:
  - {subclause: "6.4.1", decision: performed, responsible: Cybersecurity lead}
  - {subclause: "6.4.4", decision: performed, responsible: Cybersecurity lead,
     rationale: "WindowCmd and MotorDrive are reused from platform 3.2: analyse the changed environment of the body bus"}
  - {subclause: "6.4.8", decision: not-applicable, responsible: Project lead,
     rationale: "the customer assesses the vehicle; no separate assessment agreed for the door module"}
  - {subclause: "9.3", decision: by-customer, responsible: Customer, work_products: [WP-09-01]}
  - {subclause: "15.3", decision: performed, responsible: Cybersecurity engineer, due: 2026-09-30}
  # ... one entry per subclause of every clause in scope.cybersecurity
---

## Scope

The door module software of the power window (CMP-0001) as a component of the
customer's item. Clauses in scope: 6, 9, 10, 15. Left to the customer: the vehicle-level
item definition, validation (clause 11), production and operations.

## Approach

Threat scenarios per asset and property with STRIDE. Ratings by the method above; the
risk value of a threat scenario is that of its highest impact. Goals for reduced risks
become software requirements (derived_from) and are allocated in SWE.2. ...

## Criteria

The TARA is complete when every asset has a threat scenario and every threat scenario a
decided treatment; the plan is updated at every milestone of the project plan. ...

## Environment and tools

The items in this repository and `tools/traceability.py tara`. ...

## Responsibilities

Cybersecurity lead: the plan, the treatment decisions, the case. ...
```

Write the five sections out in full; the dots only save space here.

## Notes

- Quote subclause numbers: `"9.4"`; unquoted, YAML reads 9.4 as a number and `10.40`
  and `10.4` would look alike.
- `COV-53` compares the entries with the catalog: every subclause of a clause in scope
  needs one.
- Changing `tara_method` after the TARA is approved makes every rating suspect: run
  `python tools/traceability.py check` and redo the ratings with `/tara`.
