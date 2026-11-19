# Safety analysis review checklist

Version 1. Applies to: `safety-analysis`. Supports: 26262-9:7, 26262-9:8 (verification of
safety analyses and dependent failures analyses, 26262-9:7.5.2, 26262-9:8.5.2), 26262-6:7,
26262-4:6.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

The review record lists the analysed elements and the goals or requirements the analysis
is measured against under `references`. `check` means
`python tools/traceability.py check --all`.

| ID | Check | How to check | Kind |
|---|---|---|---|
| SAN-01 | Mandatory attributes and sections are present; the analysed elements exist | `check`: no `SCHEMA` or `LINK` finding on the item | script |
| SAN-02 | Every finding is open or closed; a closed one names an existing carrier or a rationale; no open finding remains at approval | `check`: no `COV-68` finding | script |
| SAN-03 | The elements of ASIL A to D of the level are analysed, and coexisting ASILs have a dependent failures analysis | `check`: no `COV-69` finding | script |
| SAN-04 | `Scope` names the elements, their interfaces and the goals or requirements the analysis is measured against, and the depth fits the ASIL | read `Scope` | semantic |
| SAN-05 | The method fits the question: inductive for the effects of failure modes, deductive for the causes of a goal violation, dependent failures for independence and freedom from interference | read `Method` | semantic |
| SAN-06 | The failure modes or initiators are complete for each analysed output, interface and shared resource (timing, memory, execution, communication, common inputs) | read the findings next to the interfaces of the elements | semantic |
| SAN-07 | Each effect is followed up to the safety goal or requirement it endangers | read `effect` | semantic |
| SAN-08 | Each measure prevents, detects or controls the fault in time, and its carrier states it | read `measure` next to the item under `carried_by` | semantic |
| SAN-09 | A rationale for a finding without a measure is a fact of the design, not an assumption | read `rationale` | semantic |
| SAN-10 | `Results` states what the analysis shows overall, what stays open, and the assumptions it rests on | read `Results` | semantic |
| SAN-11 | The safety manager states that the analysis is the project's and its open points are planned | ask; the note names who and when | accountable |
