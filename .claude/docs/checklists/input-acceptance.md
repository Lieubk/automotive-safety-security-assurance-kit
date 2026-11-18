# Input acceptance review checklist

Version 1. Applies to: every item that carries `imported`, whatever its type; and
`stakeholder-requirement` items registered without `imported` because SYS.1 is in
scope. It does not apply to any other item the team writes itself. Supports:
SYS.1.BP1, SYS.1.BP2, SYS.1.BP3 when SYS.1 is in scope. Without SYS.1 in scope it is
the entry check of the first process in scope and supports no base practice of its own.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

Accepting an input means that the team works from this version with the open points
named. It does not mean that the input is correct. A problem found here is never
repaired in the item: it becomes a query to the source or a finding of this review.

## The delivery

| ID | Check | How to check | Kind |
|---|---|---|---|
| INP-01 | Everything the source announced for this level was delivered, in the version recorded in `inputs` of `project.yaml` | compare `inputs` with the files received and with what the source announced | accountable |
| INP-02 | Every item names its source and version as the entry in `inputs` of `project.yaml` does, the date received, and the identifier or place in the source | read the `imported` block of each item (`source_document` and `source_id` for stakeholder requirements with SYS.1 in scope); a block without source or version is already a `SCHEMA` finding of INP-06 | semantic |
| INP-03 | The registration is complete: each requirement or element of the delivery, or of the part that was to be registered, has exactly one item | compare the object count and the list of identifiers of the source with the items; read the not-registered list of the import hand-over and its reasons | semantic |
| INP-04 | The text of each item is the text of the source, unchanged; tables are complete; a figure that was not carried over is marked | compare with the source word for word: every item with an ASIL above QM, and a sample of the rest whose size the reviewer sets | semantic |
| INP-05 | Every document the delivery refers to was delivered as well, or its absence is an open query | read the list of referenced documents in the import hand-over | semantic |
| INP-06 | The item files are well-formed and their attribute values are allowed | `python tools/traceability.py check --all`: no `FORMAT` or `SCHEMA` finding on the items | script |

## Each item

| ID | Check | How to check | Kind |
|---|---|---|---|
| INP-10 | It can be understood on its own: its terms are defined in the delivery, and what it refers to can be found | read the item; follow each reference | semantic |
| INP-11 | It has one reading only: condition, response, value, unit and tolerance are given; no vague or open wording | read the statement or definition | semantic |
| INP-12 | It states one need; a compound under one identifier is on the query list | read the statement | semantic |
| INP-13 | It can be verified: it is clear how fulfilment could be shown, by test, analysis, review or inspection; delivered verification criteria fit the statement | read the statement and, where delivered, `Verification criteria` | semantic |
| INP-14 | ASIL and security relevance are stated by the source wherever the product is safety or security relevant | read `asil` and `security_relevant`; compare with `safety` and `security` in `project.yaml` | semantic |
| INP-15 | It is clear whom it addresses: a requirement is allocated to an element (`allocated_to` on the requirement or `fulfils` on the element, as the source states it), and the team can tell whether it concerns its scope | `python tools/traceability.py show <ID>`; read the allocation stated by the source | semantic |
| INP-16 | An interface is defined completely enough to build against: signals or operations, ranges, units, resolution, timing, behaviour on error | read `Definition` or `Description` | semantic |
| INP-17 | Nothing known today makes it infeasible on the hardware, the platform and the dates the delivery names; each concern is written down with the figures it rests on | read the item against the delivered architecture; ask the architect | semantic |

## The set

| ID | Check | How to check | Kind |
|---|---|---|---|
| INP-20 | No two items contradict each other; a value that appears in several items is the same in all | read related items together | semantic |
| INP-21 | No source identifier is registered twice among the items that are neither obsolete nor rejected | compare the `source_id` values of the items of the source | semantic |
| INP-22 | Links between the inputs are those the delivery states; their targets exist and are not retired | `python tools/traceability.py check --all`: no `LINK` finding on the items; `show <ID>` for a sample | script |
| INP-23 | Requirements and architecture that were delivered together fit: every requirement that concerns the team has an element or interface, and every interface a requirement names is defined | read each element with `show <ID>` and the requirements allocated to it | semantic |
| INP-24 | For the team's purpose nothing obvious is missing: start-up, shutdown, each operating mode, loss or invalidity of each input, limits of each value. Each gap is a query, not an assumption | walk the list against the set | semantic |
| INP-25 | For a new version: unchanged, changed, added and removed objects are identified; a changed item carries the new content under its old ID with the new `imported.version`; a removed one is retired with the reason | read the comparison of the import hand-over against the source's own change list | semantic |
| INP-26 | For a new version: what depends on changed and removed items is visible and known to the people who own it | `python tools/traceability.py check`: the `SUSPECT` lines name the dependents of changed items, the `LINK` lines those of retired ones; `impact <ID>` for the reach | script |
| INP-27 | For a new version that replaces or retires inputs listed by a baseline other than an internal one: an approved change request names each of them | `python tools/traceability.py show <ID>`: an `affects` link from a change request; `list --type change-request` for its state | script |

## Queries and agreement

| ID | Check | How to check | Kind |
|---|---|---|---|
| INP-30 | Every query names its item and the passage it is about, and asks one question the source can answer | read the query list | semantic |
| INP-31 | The queries were sent to the source | ask who sent them, to whom and when; a communication record names the items | accountable |
| INP-32 | No open query invalidates an item that is to be accepted now; an item that depends on an open answer is left out of the acceptance or the finding stays open | go through the open queries item by item with the people who will work from the items | accountable |
| INP-33 | Answers that arrived are on record, and an answer that changes a requirement has been delivered as a new version rather than typed into an item | ask; read the communication records | accountable |
| INP-34 | What the team cannot fulfil, or will fulfil differently, has been told to the source and is agreed or under clarification | ask who agreed, and when | accountable |
| INP-35 | The source has confirmed that this version is the one to work from | ask who confirmed, and when | accountable |
| INP-36 | The reviewers are the people with the authority to accept inputs for the team, and at least one of them did not register the items | ask; compare with `people` in `project.yaml` | accountable |
