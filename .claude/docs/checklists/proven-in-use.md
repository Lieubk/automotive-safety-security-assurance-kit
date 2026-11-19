# Proven in use argument review checklist

Version 1. Applies to: `proven-in-use-argument`. Supports: 26262-8:14.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

The review record lists the element the argument qualifies and the safety plan under
`references`. `check` means `python tools/traceability.py check --all`.

| ID | Check | How to check | Kind |
|---|---|---|---|
| PIU-01 | Mandatory attributes and sections for the state are present; it qualifies an element; the credit names clauses; the safety plan plans the credit for clause 8:14 | `check`: no `SCHEMA`, `LINK` or `COV-77` finding on the item | script |
| PIU-02 | `Candidate` identifies the candidate and its parts at the version whose field data is used, its fit, form and function, and the safety requirements and ASILs of its previous use where known | read `Candidate` next to `candidate_version` | semantic |
| PIU-03 | The future use matches the previous one closely: definition and conditions of use are the same or almost the same; a replacement that only meets the same functional requirements is not the candidate | read `Candidate` next to the requirements allocated to the element | semantic |
| PIU-04 | `Modifications` lists the changes of design, implementation, configuration or calibration and of the environment since the evaluation period, and shows for each that the status still holds, or treats it as a change under the impact analysis of the safety plan | read `Modifications` | semantic |
| PIU-05 | Configuration and change management of the candidate during and after the evaluation period is shown by the records named in `evidence` | read the records named | semantic |
| PIU-06 | `evaluation_hours` comes with the rationale of its calculation; only specimens of the same specification and realization count, each beyond the average yearly operating time of a vehicle | read `Field data` | semantic |
| PIU-07 | `target_asil` is the highest ASIL the candidate can violate in its future use, and `incident_rate_limit` is the limit the safety plan's `method_selection` states for it (the interim limit for `provisional`); the incidents counted and the evaluation period meet that limit at the confidence the plan states | read `Field data` next to the safety plan | semantic |
| PIU-08 | Failure modes whose rate depends on wear, ageing or operating hours are handled by additional measures, or are shown not to apply | read `Field data` | semantic |
| PIU-09 | The problem reporting keeps every incident of the candidate with potential safety impact recorded and retrievable while the candidate is in operation | read the problem resolution strategy and `evidence` | semantic |
| PIU-10 | The credit covers only the sub-phases and activities the field data supports; integration, safety validation and confirmation measures of the item still take place | read `credit` and `Conclusion` next to the safety plan | semantic |
| PIU-11 | The safety manager states that the argument and its result are the project's | ask; the note names who and when | accountable |
