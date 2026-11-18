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

## Format

One question per query. The passage is quoted from the item; the question can be
answered by someone at the source who does not know the project's items.

```
Q3   SYR-0002 (DM-SYS-042, version 2.1)   unclear
Passage:   "from the position of detection"
Question:  Is the position of detection the window position at first contact with the
           obstacle, or the position at the moment the obstacle is reported?
Needed for: the reversal travel in the software requirements
Blocks acceptance: proposed yes
```

`Blocks acceptance` is a proposal with one line of reason. The reviewer decides.

## Where queries are kept

1. In the hand-over of this skill, always, as a numbered list.
2. As proposed findings for `/review`. A query that is still open at the review
   becomes an open finding in the review record. `record.py review` refuses the
   verdict `approved` while a finding is open, so an item with an open query is
   either left out of the approving review, or the reviewer closes the finding with
   the reason why the open question does not block the use of the item. A finding
   left open in a review with verdict `rework` has to be closed explicitly in the
   later review of the same content; `/review` does that.
3. As a communication record, once the user states that queries were sent - to whom,
   how and when:

   `python tools/record.py communication --subject <ID> --audience "<who received
   them>" --channel "<how and when they were sent>"`

   with one `--subject` per item concerned; and again when the user states that an
   answer came, with `--agreement "<what the source answered, who answered, when>"`
   added. The command is typed on one line.

   Pass what the user states and nothing else. The record is final when written. If
   the event was on an earlier day, add `--sent-at <date>` with the date the user
   names.

## What an answer changes

- The item does not change, whether it is accepted already or not. An answer that
  alters the requirement has to arrive as a new version of the input, which is
  registered as described in `new-version.md`.
- Until then the answer lives in the communication record. An author who builds on
  the clarified meaning cites the record ID in the `Rationale` or `Analysis` of the
  derived item, so that the review can follow it.
- An answer never reaches an item by way of this skill "improving" the text.

## Preparing the acceptance review

The review is held by named people with the authority to accept inputs; `/review`
records their verdict. This skill hands over, and suggests no verdict:

| Hand over | Content |
|---|---|
| Subject | the IDs of the registered items of the delivery; for a partial registration, which part of the document they cover |
| Checklist | `input-acceptance`, with the version given in its first line |
| Script results | the lines of `python tools/traceability.py check --all` that concern these items, quoted; "none" if there are none |
| Proposed findings | per finding: item ID, checklist ID, the passage it rests on, what was observed |
| Queries | the numbered list, with which were sent and which answered, as the user stated |
| For people only | the checks of kind `accountable` in the checklist: they are asked in the review, not answered here |

Accepting an input means: this is the version the team works from, and the open points
are named. It does not mean the input is right. After the review, rule COV-19 treats
imported items like every other approved item: the approval holds for the content
that was reviewed.
