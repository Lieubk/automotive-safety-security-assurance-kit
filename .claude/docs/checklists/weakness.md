# Weakness review checklist

Version 1. Applies to: `weakness`, and the `cybersecurity-event` it is derived from. Supports:
21434:8.4, 21434:8.5, 21434:8.6.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

`check` means `python tools/traceability.py check --all`.

| ID | Check | How to check | Kind |
|---|---|---|---|
| WKN-01 | Mandatory attributes and sections for the state are present; the event it comes from is recorded and triaged | `check`: no `SCHEMA`, `LINK` or `COV-78` finding | script |
| WKN-02 | A vulnerability has a risk value from the plan's matrix for its impact and feasibility, and a treatment that is carried by a change request, a problem report, `corrected_by` or a claim | `check`: no `COV-61` finding | script |
| WKN-03 | `Description` names the component and version concerned and where the information came from | read next to `affects` and `source` | semantic |
| WKN-04 | `Analysis` shows exploitability in this item: attack paths from an entry point of the item definition, rated by the plan's approach; for "not a vulnerability", why it cannot be exploited here | read `Analysis` and `attack_paths` next to the item definition | semantic |
| WKN-05 | The impact is that of the assets and damage scenarios of the TARA it touches, not a new scale | read next to `tara` | semantic |
| WKN-06 | Where it shows a threat the TARA lacks, the threat scenario is added or a query to whoever owns the TARA is raised | read next to the threat scenarios | semantic |
| WKN-07 | The treatment is the decision of the person responsible for cybersecurity, and a retained risk above `retain_up_to` names who accepted it | ask; the note names who and when | accountable |
