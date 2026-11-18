# Software requirements review checklist

Version 2. Applies to: `software-requirement`. Supports: SWE.1.BP1, SWE.1.BP2,
SWE.1.BP3, SWE.1.BP4, SWE.1.BP5, SWE.1.BP6, SWE.1.BP7.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

An accountable check is answered by the person it concerns, and the note names who
answered: `pass` when that person states the fact, `not-assessed` while nobody can state
it yet, `finding` when the answer is no. Such a finding is not closed by a reviewer's
decision: the verdict is `rework` until the fact exists.

A check that does not apply to the item under review is recorded as `not-applicable`
with the reason.

The review ends with the verdict of its reviewers. Making the approved requirements
known to those who build on them, and an agreement reached with them or with the
customer, is not a condition of the approval: it follows it and is recorded with the
baseline that carries the requirements (`/baseline`, communication record; SWE.1.BP8).

## Each requirement

| ID | Check | How to check | Kind |
|---|---|---|---|
| SWR-01 | Mandatory attributes and sections for its state are present, values are allowed | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| SWR-02 | It has a parent, or is marked internal with a rationale | `check`: no `COV-06` finding | script |
| SWR-03 | Its ASIL is not lower than its parents' | `check`: no `COV-23` finding | script |
| SWR-04 | The statement expresses exactly one need | read the statement | semantic |
| SWR-05 | The statement says what is needed, not how it is built; an imposed solution is `kind: constraint` | read the statement | semantic |
| SWR-06 | Condition, response, value, unit and tolerance are given; no vague or escape words | read the statement | semantic |
| SWR-07 | It uses "shall" or "should" in line with `priority` | compare statement and attribute | semantic |
| SWR-08 | Terms and values match those used in the other requirements and in the parents | compare with linked and related items | semantic |
| SWR-09 | The verification criteria name stimulus, observation and pass condition; a test case could be built from them | read the section | semantic |
| SWR-10 | The verification method fits: `test` where behaviour can be observed, otherwise the reason is given | read attribute and section | semantic |
| SWR-11 | `kind` fits the content | read statement and attribute | semantic |
| SWR-12 | It follows from each parent: nothing is added that the parent does not ask for, unless the rationale explains it | read item and parents side by side | semantic |
| SWR-13 | It is feasible on the given hardware and platform, and what it demands of the operating environment is stated | read `Analysis`; ask the architect where unsure | semantic |
| SWR-14 | An internal requirement is really a software matter and not a missing system requirement | read `Rationale` | semantic |

## The set

| ID | Check | How to check | Kind |
|---|---|---|---|
| SWR-20 | Every system requirement allocated to software is refined by at least one software requirement | `check`: no `COV-05` finding | script |
| SWR-21 | Taken together, the children of each parent cover everything the parent asks of the software | read each parent with its children (`show <parent>`) | semantic |
| SWR-22 | No two requirements regulate the same behaviour differently; no requirement repeats another | read related requirements together | semantic |
| SWR-23 | Start-up, shutdown, every operating mode, loss or invalidity of every input, and the limits of every value are covered or deliberately left out | walk the list against the set | semantic |
| SWR-24 | Each requirement is assigned to a release, and the release content is achievable | read `release`; ask the project lead | accountable |
| SWR-25 | No open query is about a requirement under review or about one of its parents; or the reviewers have decided that the open query does not affect it | `check`: no `QUERY` finding on the subject or its parents; otherwise ask the reviewers and note the decision | accountable |
