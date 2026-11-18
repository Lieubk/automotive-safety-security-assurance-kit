# Findings, check results and the review record

## From proposal to finding

| Stage | Who | What it is |
|---|---|---|
| Script finding | the trace engine | a fact; quoted as printed |
| Proposed finding | the reviewing agent, or this session when no independent pass took place | a proposal, shown with the text it rests on |
| Finding | a person who confirms, changes or adds it | part of the review record |
| Answer to an accountable check | a named person | "yes" closes the check; "no" or "not yet" becomes a finding |

A proposal the user rejects is dropped and does not enter the findings. Say in the
hand-over how many were rejected.

Show the overview before asking anything:

```
Review 2: SWR-0010, SWR-0011 - software requirements review v1 - independent pass: yes

Script (check):      no finding on the subject
Proposed (semantic):
  P1 SWR-0010 SWR-09 major  "Checked at the lowest and the highest closing speed."
     The two speeds are not given. Fix: state both with unit.
  P2 SWR-0011 SWR-04 minor  "... shall stop the motor and store the event."
     Two needs in one statement. Fix: split into two requirements.
Pass:                SWR-04 and SWR-13 on SWR-0010; SWR-09 on SWR-0011; on both items
                     SWR-05 to SWR-08, SWR-10 to SWR-12, SWR-14; on the set SWR-21 to SWR-23
Not assessed:        SWR-13 on SWR-0011 - the Analysis section refers to a timing budget
                     the agent could not find in any item
Accountable, open:   SWR-24, SWR-25, SWR-26
Blocks `approved`:   SWR-0011 - still to come before approval: release
```

## A finding

| Field | Content |
|---|---|
| `id` | `F1`, `F2`, ... within this record |
| `item` | ID of the item the finding is on |
| `text` | the check ID, what is wrong, the words it rests on, and what would fix it |
| `severity` | `major`: the item cannot be relied on as it stands (contradicts or misses what an upstream item demands, cannot be verified, can be read in two ways, lacks what the next step needs). `minor`: usable as it is; wording, terms or form should improve |
| `state` | `open`: still to be corrected. `closed`: corrected, and a reviewer has confirmed the correction on the present text |
| `closes` | optional: `<REV-ID>#<finding id>` of the finding of an earlier review that this entry settles |

A reviewer may decide that a finding needs no correction. Then it is `closed` with the
reason and the reviewer's name in `text`. This is the reviewer's decision; do not
propose it.

A finding can be `closed` in the same review only if the correction was made before the
record is written. The content has then changed: repeat the script checks, and have
the reviewer confirm the correction on the present text.

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

JSON, a list with one entry for every check of the checklist - script, semantic and
accountable. It is what makes the record say what was actually looked at.

| Field | Content |
|---|---|
| `check` | the check ID of the checklist |
| `result` | `pass`: applied to every subject it concerns, nothing found. `finding`: at least one confirmed finding rests on it. `not-assessed`: not applied to at least one subject, or an accountable check nobody answered |
| `note` | what the result rests on: the quoted line of `check` for a script check; "reviewing agent" or "applied in the session, no independent pass" for a semantic check, with the finding IDs or the items left out; the answer and who gave it for an accountable check |

```json
[
  {"check": "SWR-01", "result": "pass", "note": "check: no SCHEMA or FORMAT finding on SWR-0010, SWR-0011"},
  {"check": "SWR-04", "result": "finding", "note": "reviewing agent; F2 on SWR-0011, confirmed by the reviewer"},
  {"check": "SWR-09", "result": "finding", "note": "reviewing agent; F1 on SWR-0010"},
  {"check": "SWR-13", "result": "not-assessed", "note": "SWR-0011: the timing budget the Analysis refers to is in no item"},
  {"check": "SWR-24", "result": "pass", "note": "release R1.0 confirmed as achievable by <name as the user stated it>"},
  {"check": "SWR-26", "result": "not-assessed", "note": "not answered"}
]
```

Every check of the checklist appears once. Do not leave out a check to avoid
`not-assessed`: a check that is missing from the record looks like one that never
existed. In a re-review limited to the comparison with a changed upstream item
(`re-review.md`), a check that was not applied again may be `pass` only if the subject's
hash is the one an earlier approving record lists, and the note names that record. The
same holds for a repeated review of code that `check` did not report as changed.

When the user named criteria of their own instead of a checklist of the toolkit, the
entries are those criteria, by the names the user gave them.

## The command

```
python tools/record.py review --checklist "software requirements review v1" --reviewer "<name as the user stated it>" --verdict rework --findings build/review-findings.json --checks build/review-checks.json SWR-0010 SWR-0011
```

Add `--project <dir>` before `review` when the project is not the current directory.
Repeat `--reviewer` for each person. When the code of the units was part of the review,
and only then, add `--item-under-test <commit>`:

```
python tools/record.py review --checklist "software unit code review v1" --reviewer "<name>" --verdict approved --checks build/review-checks.json --item-under-test 3d65a59 UNT-0002
```

The tool prints, for example:

```
wrote records/reviews/REV-0010.md: rework, 2 items, 3 references, 2 findings
```

| The tool fills in | From |
|---|---|
| `id` | the next free review record number |
| `status: final` | a record is final when written |
| `reviewed_at` | the date of the command |
| `subject` | the IDs given, each with its content hash at this moment |
| `references` | every item the subject links to that is not itself a subject, with its content hash |
| `checks`, `item_under_test` | what was passed with `--checks` and `--item-under-test` |
| `sources` | only with `--item-under-test`: for software units among the subjects, every file under `source_files` that exists, with its hash as it lies in the working tree |

| The tool refuses | It prints |
|---|---|
| an ID that does not exist | `no such item: <ID>` |
| a finding without `severity` major or minor, or without `state` open or closed | `finding <id> needs severity major\|minor and state open\|closed` |
| a check with another result than the three allowed | `check <id> needs result pass\|finding\|not-assessed` |
| verdict `approved` while a finding is `open` | `verdict approved is not possible while a finding is open` |
| verdict `approved` while a check is `not-assessed` | `verdict approved is not possible while checks are not assessed: <IDs>` |
| verdict `approved` while an earlier review of the same content has an open finding that no entry closes | `<ID>: finding <REV-ID>#<id> of an earlier review of the same content is open; close it with a finding entry that has "closes": "<REV-ID>#<id>"` |

After a refusal it prints `no record written`. Nothing has changed; go back to the user.
An approved verdict with open findings or with checks that were not assessed does not
exist in this toolkit: either the findings are corrected and confirmed and the checks
are applied or answered first, or the verdict is `rework`.

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

In the last case the unit keeps its approved design, and `check` reports
`COV-19 ... findings of an earlier review of the same content are open` on it. That is
intended: the line stays until a later review of the code closes those findings with
`closes`.

Change the `status` line and nothing else: the content hash does not cover the status,
so the record stays valid. Once its acceptance review is recorded, an imported item
changes only in its disposition (`status`, `superseded_by`, `rejection_reason`) or
through a new delivery registered by `/import-inputs`. Its findings go back to the
source of the input as queries.

Then run `python tools/traceability.py check` and read the lines on the subject.

## What still goes into the hand-over

The record now holds the result of every check, the answers to accountable checks and
the commit of reviewed code. It has no field of its own for whether an independent pass
took place: say it in the `note` of the semantic checks and again in the hand-over.
