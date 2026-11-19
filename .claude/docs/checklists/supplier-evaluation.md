# Supplier evaluation review checklist

Version 1. Applies to: `supplier-evaluation`. Supports: 21434:7.4.1, 21434:7.4.2, 26262-8:5.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

`check` means `python tools/traceability.py check --all`.

| ID | Check | How to check | Kind |
|---|---|---|---|
| SEV-01 | Mandatory attributes and sections for the state are present | `check`: no `SCHEMA` finding on the item | script |
| SEV-02 | `Request for quotation` states what the supplier was asked to do and deliver for functional safety and cybersecurity, as far as the project's scope needs it | read | semantic |
| SEV-03 | The criteria cover the supplier's processes, competence and earlier assessments or audits for the standards in scope, and each result names the evidence looked at | read `criteria` | semantic |
| SEV-04 | A selection with conditions names the conditions and how they are followed up (for example in the supplier agreement or the interface agreement) | read `Decision` | semantic |
| SEV-05 | The person who decided states the selection and its reasons | ask; the note names who and when | accountable |
