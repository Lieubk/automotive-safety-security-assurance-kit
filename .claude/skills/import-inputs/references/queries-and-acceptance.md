# Queries and the input acceptance review

## What becomes a query

A query is a question only the source of the input can answer. The examples are made
up for illustration.

| Kind | When | Example |
|---|---|---|
| unclear | the text allows more than one reading | "from the position of detection": the position at first contact, or at the moment the obstacle is reported? |
| contradiction | two objects of the delivery, or two delivered documents, disagree | the requirement names 120 mm of reversal travel, a table in the architecture names 100 mm |
| missing | something needed to use the item is not in the delivery | no tolerance on a value; no ASIL on a requirement of a safety-relevant product; no allocation to an element; a referenced document that was not delivered; a figure the text depends on |
| not verifiable | nobody could show that it is fulfilled | "the window shall close smoothly" |
| not feasible | the hardware, platform or dates the delivery itself names cannot meet it | a reaction time shorter than one cycle of the task that is to produce the reaction |
| compound | several needs under one identifier | detection and reversal in one sentence |
| mapping | an attribute of the source has no agreed counterpart | priority given as 1 to 5 |

"Not feasible" is a concern raised, with the figures it rests on. Whether it stands is
decided by the people who know the hardware, and then with the source.

Not a query: a typing error with only one possible reading (note it for the review, do
not correct it); a question the delivery answers elsewhere (cite the place); a wish
for a better requirement.

## A query is an item

A question to the source is written as a `query` item, not as a line in a hand-over
and not as text inside a finding. The item names who is asked and when, links to the
inputs it is about, and later holds the answer. One question per query; a question
that concerns several inputs (a contradiction between two) links to all of them.

File: `records/queries/QRY-0001.md`. ID from `python tools/record.py next-id query`.

```markdown
---
id: QRY-0001
type: query
title: Meaning of "position of detection"
status: open
to: Requirements contact at the customer
asked_at: "2026-03-05"
links:
  about: [SYR-0002]
---

## Question

DM-SYS-042, version 2.1, says "from the position of detection". Is this the window
position at first contact with the obstacle, or the position at the moment the
obstacle is reported? The reversal travel of the software depends on it.
```

| Part | Rule |
|---|---|
| `to` | who the question goes to at the source, by role or by the name the user gives |
| `asked_at` | the day the question is put to the source, quoted. Ask the user; the toolkit sends nothing itself. Left out while the question is written down but not sent; `check` then says "not put to its source yet" |
| `about` | the IDs of the inputs the question concerns; they must be registered |
| `Question` | the passage quoted with the identifier and version of the source, so that the source can find it without knowing the project's IDs; one question that can be answered; what depends on the answer |
| `title` | a few words for lists |

When the user reports the answer, the same item is completed (step 8 of the skill):

```markdown
status: answered
answered_by: Requirements contact at the customer, 2026-03-12
```

and a section

```markdown
## Answer

The position at the moment the obstacle is reported by the software. Version 2.2 of
the specification will say so.
```

| State | Means | Set when |
|---|---|---|
| `open` | asked, no answer | the query is written |
| `answered` | the answer and who gave it are recorded | the user reports the answer |
| `closed` | the inputs the query is about are in line with the answer | the user confirms it: nothing in the input had to change, or the new version that carries the change is registered |

An answer that does not settle the question puts the query back to `open`, with the
reason added to the `Answer` section.

While a query is open, the check prints `QUERY` as a warning on every approved item it
is about, and `still to come before review` as an `info` line on the query itself.

## What an answer changes

- The input does not change, whether it is accepted already or not. An answer that
  alters the requirement has to arrive as a new version of the input, which is
  registered as described in `new-version.md`.
- Until then the answer lives in the query. An author who builds on the clarified
  meaning cites the query ID in the `Rationale` or `Analysis` of the derived item, so
  that the review can follow it.
- An answer never reaches an input by way of this skill "improving" the text.

## Open queries at the acceptance review

This is the rule `/review` follows as well:

1. Every registered input of the delivery is reviewed. An open query is no reason to
   leave an input out.
2. For an input with an open query the review records a finding that cites the query
   by its ID, and the verdict for that input is `rework`.
3. One review record has one verdict. The review of a delivery therefore ends in two
   records: one with the verdict `approved` for the inputs that have no open query and
   no other open finding, and one with the verdict `rework` for the others.
4. An input in `rework` is not accepted and goes back to `draft`; nothing is changed
   in it. Nothing derived from it can be approved (`UPSTREAM`), and an element that
   fulfils it cannot be accepted before it: that element is left out of the record of
   the accepted inputs and waits. Say this to the user when the queries are written:
   an open question has a price.
5. The reviewers may decide that an open question does not stand in the way of using
   the input. Then they close the finding with that reason and their name, the input
   is accepted with the others, and `QUERY` warns on it until the query is closed.
6. When the query is closed, an input that was in rework is reviewed again; that
   review closes the earlier finding. If the answer came as a new version, the review
   is the acceptance of the new content.

A query raised later about an input that is already accepted (by `/sw-requirements`,
for example) does not take the acceptance back. It shows as `QUERY` until it is closed.

## Preparing the acceptance review

The review is held by named people with the authority to accept inputs; `/review`
records their verdict. This skill hands over, and suggests no verdict:

| Hand over | Content |
|---|---|
| Subject | the IDs of the registered items of the delivery; for a partial registration, which part of the document they cover |
| Order | the requirements before the architecture that fulfils them: an element is approved only when every requirement in its `fulfils` is |
| Checklist | `input-acceptance`, cited with its version as `input-acceptance v2` |
| Script results | the lines of `python tools/traceability.py check --all` that concern these items, quoted; "none" if there are none |
| Proposed findings | per finding: item ID, checklist ID, the passage it rests on, what was observed |
| Queries | the IDs of the open queries and the inputs each is about |
| Checks that do not apply | for example the new-version checks at a first delivery: named, with the reason, so that they are recorded as not applicable |
| For people only | the checks of kind `accountable` in the checklist: they are asked in the review, not answered here |

Accepting an input means: this is the version the team works from, and the open points
are named. It does not mean the input is right. After the review, rule COV-19 treats
imported items like every other approved item: the approval holds for the content
that was reviewed.
