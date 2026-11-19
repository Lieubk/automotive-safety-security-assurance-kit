# Software component qualification review checklist

Version 1. Applies to: `component-qualification`. Supports: 26262-8:12.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

The review record lists the qualified component and the requirements allocated to it
under `references`. `check` means `python tools/traceability.py check --all`.

| ID | Check | How to check | Kind |
|---|---|---|---|
| CQL-01 | Mandatory attributes and sections for the state are present; it qualifies a component | `check`: no `SCHEMA` or `LINK` finding on the item | script |
| CQL-02 | Every supplied or reused component of ASIL A to D is qualified, or the safety plan argues why clause 8:12 does not apply | `check`: no `COV-75` finding | script |
| CQL-03 | `Specification` describes the component's functions, interfaces, configuration and assumptions of use at the version qualified, as far as the requirements allocated to it need | read next to the allocated requirements | semantic |
| CQL-04 | The method fits the ASIL and the use: what is verified covers the allocated requirements, including behaviour on faults and outside the specified use | read `Qualification` | semantic |
| CQL-05 | The evidence named exists and shows what `Qualification` says | read the evidence | semantic |
| CQL-06 | Restrictions are stated where they apply and are reflected in the architecture or the requirements of the users of the component | read `Restrictions` next to the architecture | semantic |
| CQL-07 | The safety manager states that the qualification is the project's | ask; the note names who and when | accountable |
