# Findings, check results and the review record

## From proposal to finding

| Stage | Who | What it is |
|---|---|---|
| Script finding | the trace engine | a fact; quoted as printed |
| Proposed finding | the reviewing agent, or this session when no independent pass took place | a proposal, shown with the text it rests on |
| Finding | a person who confirms, changes or adds it | part of the review record |
| Answer to an accountable check | a named person | "yes": `pass`. "No": a `finding` that only the missing fact closes, verdict `rework`. "Not yet": `not-assessed`, the review waits |

A proposal the user rejects is dropped and does not enter the findings. Say in the
hand-over how many were rejected.

Show the overview before asking anything:

```
Review 2: SWR-0010, SWR-0011 - software-requirements v1 - independent pass: yes

Script (check):      no finding on the subject
Proposed (semantic):
  P1 SWR-0010 SWR-09 major  "Checked at the lowest and the highest closing speed."
     The two speeds are not given. Fix: state both with unit.
  P2 SWR-0011 SWR-04 minor  "... shall stop the motor and store the event."
     Two needs in one statement. Fix: split into two requirements.
Pass:                SWR-04 and SWR-13 on SWR-0010; SWR-09 on SWR-0011; on both items
                     SWR-05 to SWR-08, SWR-10 to SWR-12; on the set SWR-21 to SWR-23
Not applicable:      SWR-14 - neither item has `origin: internal`
Not assessed:        SWR-13 on SWR-0011 - the Analysis section refers to a timing budget
                     the agent could not find in any item
Accountable, open:   SWR-24, SWR-25
Open queries:        QRY-0003 about SYR-0002, the parent of SWR-0010
Blocks `approved`:   SWR-0011 - still to come before approval: release
```

## A finding

| Field | Content |
|---|---|
| `id` | `F1`, `F2`, ... within this record |
| `item` | ID of the item the finding is on |
| `text` | the check ID, what is wrong, the words it rests on, and what would fix it; the ID of the query when only the source of an input can settle it |
| `severity` | `major`: the item cannot be relied on as it stands (contradicts or misses what an upstream item demands, cannot be verified, can be read in two ways, lacks what the next step needs). `minor`: usable as it is; wording, terms or form should improve |
| `state` | `open`: still to be corrected. `closed`: corrected, and a reviewer has confirmed the correction on the present text |
| `closes` | optional: `<REV-ID>#<finding id>` of the finding of an earlier review that this entry settles |

A reviewer may decide that a finding needs no correction. Then it is `closed` with the
reason and the reviewer's name in `text`. This is the reviewer's decision; do not
propose it.

A finding can be `closed` in the same review only if the correction was made before the
record is written. The content has then changed: repeat the script checks, and have
the reviewer confirm the correction on the present text.

## Findings that need the source of an input

A question only the source of an input can answer is a `query` item, not a sentence in
a finding or in a hand-over. The finding cites the query: "INP-11: the passage 'from
the position of detection' can be read in two ways; see QRY-0003."

- Look first: `python tools/traceability.py list --type query` and `show <input ID>`
  (a query appears as `about <- QRY-...`).
- If no query covers the question, ask: "May I write this question as QRY-nnnn?" Take
  the ID from `python tools/record.py next-id query`, and ask whom the question goes
  to and on which date it is put. Do not fill in either yourself.

```markdown
---
id: QRY-0003
type: query
title: Meaning of "position of detection" in SYR-0002
status: open
to: "<who the user names at the source of the input>"
asked_at: "<date the user states>"
links:
  about: [SYR-0002]
---

## Question

SYR-0002 says "from the position of detection". Is that the window position at first
contact with the obstacle, or the position at the moment the obstacle is reported?
Needed for: the reversal travel in the software requirements.
```

The file goes to `records/queries/`. Answering and closing a query is not part of the
review: the answer is recorded when the user states that it came and from whom.

## The findings file

JSON, a list. Write it outside the item folders; it is input for the tool only.

```json
[
  {"id": "F1", "item": "SWR-0010", "severity": "major", "state": "open",
   "text": "SWR-09: the verification criteria say 'at the lowest and the highest closing speed' without values, so the pass condition cannot be reproduced. State both speeds with unit, or refer to the item that defines them."},
  {"id": "F2", "item": "SWR-0011", "severity": "minor", "state": "open",
   "text": "SWR-04: 'shall stop the motor and store the event' states two needs. Split into two requirements."}
]
```

A review without findings needs no findings file: the record then says `findings: []`,
which states that there were none.

## The checks file

JSON, a list with one entry for every check ID of the checklist - script, semantic and
accountable, every part of the file. The tool reads the IDs from the checklist and
refuses an approved verdict while one of them has no result.

| Field | Content |
|---|---|
| `check` | the check ID as the checklist prints it |
| `result` | `pass`: applied to every subject it concerns, nothing found. `finding`: at least one confirmed finding rests on it. `not-applicable`: the check does not concern these subjects at all; the note must say why. `not-assessed`: it concerns them but was not applied to at least one, or it is an accountable check nobody could answer |
| `note` | what the result rests on: the quoted line of `check` for a script check; "reviewing agent" or "applied in the session, no independent pass" for a semantic check, with the finding IDs or the items left out; the answer and who gave it for an accountable check; the reason for `not-applicable` |

```json
[
  {"check": "SWR-01", "result": "pass", "note": "check: no SCHEMA or FORMAT finding on SWR-0010, SWR-0011"},
  {"check": "SWR-04", "result": "finding", "note": "reviewing agent; F2 on SWR-0011, confirmed by the reviewer"},
  {"check": "SWR-09", "result": "finding", "note": "reviewing agent; F1 on SWR-0010"},
  {"check": "SWR-13", "result": "not-assessed", "note": "SWR-0011: the timing budget the Analysis refers to is in no item"},
  {"check": "SWR-14", "result": "not-applicable", "note": "neither subject has origin internal"},
  {"check": "SWR-24", "result": "pass", "note": "release R1.0 confirmed as achievable by <name as the user stated it>"},
  {"check": "SWR-25", "result": "not-assessed", "note": "QRY-0003 is open; the reviewers decide on <date> whether it affects SWR-0010"}
]
```

The example is shortened; a real file has all 20 check IDs of that checklist.

- `not-applicable` is for a check that has nothing to look at: a check for internal
  requirements when none is internal, the part of the plan checklist for another kind
  of plan. It is not a way around a check that is inconvenient.
- `not-assessed` is honest and blocks approval. Do not leave out a check to avoid it,
  and do not turn it into `not-applicable`.
- An accountable check whose answer depends on something that has not happened yet -
  a decision of a board, an acceptance by the person responsible for functional safety -
  stays `not-assessed`. Then no approving record is written: the items stay `in-review`,
  the two files are kept, and the hand-over says which answer is awaited from whom.
  When the answer exists, run `/review` for the same items again. If `hash` prints the
  same hashes as before, the earlier results stand and only the open check is asked
  again.
- An accountable check answered with "no" is a `finding`, and its finding stays `open`:
  a fact that a person says is missing is not closed by a reviewer's decision, and the
  tool refuses an approved verdict over it. The verdict is `rework`; the finding says
  what has to exist, and who provides it.
- The agreement of those who build on the items - developers, integration, the customer -
  is not a check of an item checklist. It follows the approval and is recorded by
  `/baseline` as a communication record.
- A check is never `pass` because an earlier record said so. Items that did not change
  and are only compared with a changed upstream item are recorded with `--reconfirm`
  (`re-review.md`), which needs no checks file.

## The command

```
python tools/record.py review --checklist "software-requirements v1" --reviewer "<name as the user stated it>" --verdict rework --findings build/review-findings.json --checks build/review-checks.json SWR-0010 SWR-0011
```

`--project <dir>` goes before `review` when the project is not the current directory.
Repeat `--reviewer` for each person. When the code of the units was part of the review,
and only then, add `--item-under-test <commit>`:

```
python tools/record.py review --checklist "software-unit-code v1" --reviewer "<name>" --verdict approved --checks build/review-checks.json --item-under-test c2dc5ca UNT-0002
```

When the user named criteria from outside the toolkit because no checklist exists for
the type, cite them as stated and add `--external-criteria`:

```
python tools/record.py review --checklist "<criteria as the user names them>" --external-criteria --reviewer "<name>" --verdict approved SYR-0010
```

When the subjects did not change and were compared with a new version of something
they build on (`re-review.md`), no checklist is applied and none is cited:

```
python tools/record.py review --reconfirm --reviewer "<name>" --verdict approved CMP-0004 UNT-0003
```

The tool prints, for example:

```
wrote records/reviews/REV-0007.md: rework, 2 items, 3 references, 2 findings
```

| The tool fills in | From |
|---|---|
| `id` | the next free review record number |
| `status: final` | a record is final when written |
| `checklist_source` | `toolkit`, `external` with `--external-criteria`, or `reconfirmation` with `--reconfirm` |
| `reviewed_at` | the date of the command |
| `subject` | the IDs given, each with its content hash at this moment |
| `references` | every item the subject builds on that is not itself a subject, with its content hash: the items it links to and, for a component, the interfaces that name it as provider or user |
| `checks`, `item_under_test` | what was passed with `--checks` and `--item-under-test` |
| `sources` | with `--item-under-test`: for software units among the subjects, every file under `source_files` that exists, with its hash as it lies in the working tree. With `--reconfirm`: carried over from the unit's last approving record exactly as recorded there, so a code review stays valid for code that did not change, and code that changed since stays reported as `SUSPECT` |

| The tool refuses | It prints |
|---|---|
| an ID that does not exist | `no such item: <ID>` |
| a citation that names no checklist of the toolkit | `'<text>' cites no checklist of this toolkit: expected '<name> v<N>' ...` |
| a citation with another version than the file has | `<file> is at version <n>, the citation says v<m>` |
| a finding without `severity` major or minor, or without `state` open or closed | `finding <id> needs severity major\|minor and state open\|closed` |
| a check with a result that is not one of the four, or an ID the checklist does not have | `check <id> needs result ...`, `check <id> is not in <file>` |
| `not-applicable` without a note | `check <id> is not-applicable: the note must say why` |
| verdict `approved` while a finding is `open` | `verdict approved is not possible while a finding is open` |
| verdict `approved` while a check of the checklist has no result | `verdict approved needs a result for every check of <file> (--checks); none for: <IDs>` |
| verdict `approved` while a check is `not-assessed` | `verdict approved is not possible while checks are not assessed: <IDs>` |
| verdict `approved` while an accountable check has the result `finding` | `accountable checks answered with a finding: <IDs>. What a person states is missing cannot be closed by decision ...` |
| `--reconfirm` for an item whose present content no review has approved | `<ID>: its current content has no approving review, so there is nothing to reconfirm; it needs a review against its checklist` |
| verdict `approved` while an item the subject builds on is in draft or in review and not a subject itself | `<ID> cannot be approved while <ID> (<role>) is in state <state>` |
| verdict `approved` while an earlier review of the same content has an open finding that no entry closes | `<ID>: finding <REV-ID>#<id> of an earlier review of the same content is open; close it with a finding entry that has "closes": "<REV-ID>#<id>"` |

After a refusal it prints `no record written`. Nothing has changed; go back to the user.
An approved verdict with open findings, with checks that were not assessed, or above an
item that is not approved does not exist in this toolkit: either the cause is removed
first, or the verdict is `rework`, or the review waits.

The hashes are taken when the command runs. That is why the content is frozen from step
3 on and `hash` is compared once more just before recording.

## Status after the record

| Verdict | Item was | Set `status` to |
|---|---|---|
| `approved` | `in-review` | `approved` |
| `approved` | `approved`, here because of `SUSPECT` or `CONSISTENCY`, or for a review of its code | leave it |
| `rework` | `in-review` | `draft` |
| `rework` | `approved`, and the item itself has to change | `draft` |
| `rework` | `approved`, review of its code, every finding is against the code | leave it; the code goes back to `/sw-unit-implement` |
| none yet: an accountable check waits for an answer | `in-review` | leave it |

In the fifth case the unit keeps its approved design, and `check` reports
`COV-19 ... findings of an earlier review of the same content are open` on it. That is
intended: the line stays until a later review of the code closes those findings with
`closes`.

Change the `status` line and nothing else: the content hash does not cover the status,
so the record stays valid. Once its acceptance review is recorded, an imported item
changes only in its disposition (`status`, `superseded_by`, `rejection_reason`) or
through a new delivery registered by `/import-inputs`.

Then run `python tools/traceability.py check` and read the lines on the subject.

## What still goes into the hand-over

The record holds the result of every check, the answers to accountable checks and the
commit of reviewed code. It has no field of its own for whether an independent pass
took place: say it in the `note` of the semantic checks and again in the hand-over.
