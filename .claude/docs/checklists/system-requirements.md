# System requirements review checklist

Version 1. Applies to: `system-requirement`. Supports: SYS.2.BP1, SYS.2.BP2,
SYS.2.BP3, SYS.2.BP4, SYS.2.BP5, SYS.2.BP6, SYS.2.BP7.

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
baseline that carries the requirements (`/baseline`, communication record; SYS.2.BP8).

## Each requirement

| ID | Check | How to check | Kind |
|---|---|---|---|
| SYR-01 | Mandatory attributes and sections for its state are present, values are allowed | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| SYR-02 | It has a stakeholder requirement as parent, or is marked internal with a rationale | `check`: no `COV-02` finding | script |
| SYR-03 | Its ASIL is not lower than its parents' | `check`: no `COV-23` finding | script |
| SYR-04 | The statement expresses exactly one need | read the statement | semantic |
| SYR-05 | The statement says what the system must do, not how it is built or which element does it; an imposed solution is `kind: constraint` | read the statement | semantic |
| SYR-06 | Condition, response, value, unit and tolerance are given; no vague or escape words | read the statement | semantic |
| SYR-07 | It uses "shall" or "should" in line with `priority` | compare statement and attribute | semantic |
| SYR-08 | Terms and values match those used in the other requirements and in the parents | compare with linked and related items | semantic |
| SYR-09 | The verification criteria name stimulus, conditions, observation and pass condition at the boundary of the system; a system test case could be built from them | read the section | semantic |
| SYR-10 | The verification method fits: `test` where behaviour can be observed, otherwise the reason is given | read attribute and section | semantic |
| SYR-11 | `kind` fits the content | read statement and attribute | semantic |
| SYR-12 | It follows from each parent: nothing is added that the parent does not ask for, unless the rationale explains it | read item and parents side by side | semantic |
| SYR-13 | It is feasible with the technology in view, and what is known about cost, schedule and risk is stated | read `Analysis`; ask the architect where unsure | semantic |
| SYR-14 | What it asks of the operating environment (neighbouring systems, supply, vehicle network, mechanics, the user) is stated, or the reason why nothing is | read `Analysis` | semantic |
| SYR-15 | An internal requirement is really a system matter and not a missing stakeholder requirement | read `Rationale` | semantic |

## The set

| ID | Check | How to check | Kind |
|---|---|---|---|
| SYR-20 | Every accepted stakeholder requirement is refined by at least one system requirement | `check`: no `COV-01` finding | script |
| SYR-21 | Taken together, the children of each parent cover everything the parent asks of the system | read each parent with its children (`show <parent>`) | semantic |
| SYR-22 | No two requirements regulate the same behaviour differently; no requirement repeats another | read related requirements together | semantic |
| SYR-23 | Operating modes, start-up and shutdown, supply voltage and temperature ranges, loss of each neighbour, and the limits of every value are covered or deliberately left out | walk the list against the set | semantic |
| SYR-24 | Each requirement is assigned to a release, and the release content is achievable | read `release`; ask the project lead | accountable |
| SYR-25 | No open query is about a requirement under review or about one of its parents; or the reviewers have decided that the open query does not affect it | `check`: no `QUERY` finding on the subject or its parents; otherwise ask the reviewers and note the decision | accountable |
