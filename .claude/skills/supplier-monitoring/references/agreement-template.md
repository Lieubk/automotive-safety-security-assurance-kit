# The supplier agreement

File: `plans/suppliers/<ID>.md`. Type `supplier-agreement` (prefix SAG), lifecycle
`engineering` (draft, in-review, approved), reviewed with `/review` against
`.claude/docs/checklists/supplier-agreement.md`. It supports ACQ.4.BP1 and holds what
customer and supplier agreed to do together. It is the project's record of that
agreement; the contract itself stays where the project keeps contracts.

## Questions to ask before drafting

Ask them in this order; each answer is the user's, stated as agreed with the supplier.
Where it was not agreed yet, the item says so with `Not applicable:` or stays in draft.

1. Who is the supplier, and which contract or order does this belong to (`supplier`)?
2. Which software components or system elements does the supplier deliver
   (`components`, IDs of the architecture items)?
3. Which processes does each side perform, and where do they meet: requirements and
   change handling, quality assurance, configuration management, problem resolution,
   acceptance of deliveries? Are the supplier's processes consistent with the project's?
4. What is exchanged, in which direction, in which form and when (`exchanges`)?
5. Which meetings, of which kind, how often, who takes part (`meetings`)?
6. Who is responsible for what at each interface?
7. What happens when an agreed objective is missed: who is told, what is done, who
   escalates to whom, and how is the agreement changed?

## Layout

```markdown
---
id: SAG-0001
type: supplier-agreement
title: Agreement with the window lift motor driver supplier
status: draft
supplier: "Motor driver supplier, order of the example project"
components: [CMP-0004]
exchanges:
  - {name: Driver software release, direction: from-supplier, content: "source code and
     release notes of the driver", due: "with each delivery", format: "archive with checksum"}
  - {name: Interface change notice, direction: to-supplier, content: "changes to the
     interface specification", due: "before the change applies", format: "document"}
meetings:
  - {name: Technical review, kind: technical, cadence: 28, participants: [Software lead, Supplier engineer]}
  - {name: Progress review, kind: progress, cadence: 14, participants: [Project lead, Supplier project lead]}
---

## Joint processes
Which processes are performed together and how: ...

## Interfaces and responsibilities
Per interface: who defines it, who changes it, who tests which side ...

## Deviations and escalation
What counts as a deviation, who is told, who decides, to whom it escalates ...
```

(Values above are an illustration in the power window domain, not agreed terms.)

## Rules for the attributes

- `exchanges` entries: `name`, `direction` (`to-supplier` or `from-supplier`) and
  `content` are required; `due` is a date or a rhythm such as `weekly` or `with each
  delivery`; `format` is how it is passed.
- `meetings` entries: `name`, `kind` (`technical` or `progress`) and `cadence` are
  required. Give `cadence` as a number of days between two meetings when it is fixed:
  only then `suppliers` can say how many days overdue the next one is. A text such as
  "at each milestone" is allowed and is not measured.
- Both kinds of meeting are needed for ACQ.4.BP3 and BP4; if only one is agreed, say
  in `Joint processes` why.
- Sections before approval: `Deviations and escalation`. One agreement per supplier and
  contract; a supplier with several contracts has several agreements.

## Changing the agreement

A change of terms is a change of the item. In `draft` or `in-review` edit it and review
again. In `approved`, the item is no longer approved after the edit and is reviewed
again. In a baseline it is not edited at all: `/change-request` names it. The change
follows from a negotiation the user reports; keep who agreed and when in `Joint
processes` or in the change request, as stated.
