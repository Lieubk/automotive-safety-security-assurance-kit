# Tool evaluation review checklist

Version 1. Applies to: `tool-evaluation`. Supports: 26262-8:11.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

`check` means `python tools/traceability.py check --all`.

| ID | Check | How to check | Kind |
|---|---|---|---|
| TEV-01 | Mandatory attributes and sections are present; TCL2 and TCL3 name a qualification method and evidence | `check`: no `SCHEMA` finding on the item | script |
| TEV-02 | The confidence level is the one the plan's tool confidence determination gives | `check`: no `COV-71` finding | script |
| TEV-03 | Every tool the build and analysis records name is evaluated | `check`: no `COV-72` finding | script |
| TEV-04 | `tool` names the tool and the version in use, as the records name it | compare with the records' `tool` | semantic |
| TEV-05 | `Use cases` lists every use in the project and, for each, the errors the tool could introduce into a work product or fail to detect | read | semantic |
| TEV-06 | The impact and detection ratings follow from the use cases: which later activity would find an error of the tool, and how likely | read `Classification rationale` | semantic |
| TEV-07 | The qualification method fits the confidence level and the ASIL, and the evidence named shows it was carried out | read `Qualification` and the evidence | semantic |
| TEV-08 | The safety manager states that the classification is the project's | ask; the note names who and when | accountable |
