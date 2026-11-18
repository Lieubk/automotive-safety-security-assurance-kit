# Reviewing again

A final record is never edited. Whatever happens after a review - corrections, changed
code, a change further up - is answered by a new review whose record describes the new
state. The newest final review record of an item's present content decides what the
trace check reports.

## After a `rework` verdict

1. The author corrects with the authoring skill. `python tools/traceability.py
   check --all` shows which items still carry the findings of their last review:
   `COV-19 ... review REV-0007 left findings open: F1`. That line goes when the content
   changes.
2. Run `python tools/traceability.py diff <ID> --since <REV-ID>` for each item. It
   prints what changed since the earlier review saw the item, from the version-control
   history. "unchanged" means the item was not touched - as after a review whose
   findings were all against the code. "NOT ASSESSED ... cannot be found" means the
   reviewed text was never committed: then the whole item is reviewed again, and from
   now on the record and the items are committed after each review.
3. Run `/review` for the items. In step 5 hand the reviewing agent the earlier record
   and the `diff` output. It decides for each open finding whether the present text
   resolves it, then applies the checklist to the changed passages and to whatever
   they touch - another section that states the same value, the set the item belongs
   to - not to the unchanged rest. The checks it did not apply again keep the result of
   the earlier record, with a note that names it.
4. In the new findings file every finding of the earlier record appears again: with a
   new `id` of this record, `closes` naming the earlier finding, its origin at the start
   of `text`, and the state a reviewer confirmed - `closed` when it is resolved, `open`
   when it is not. New findings follow.
5. The new record is the evidence that the findings were closed. The earlier record
   keeps saying `rework` with open findings, and that stays true for what it describes.

`closes` is what the tool looks at when the content is the same as in the earlier
review: it refuses an approved verdict, and the check reports `COV-19`, until every
open finding of an earlier review of that content is named by a closed entry. Set it
for corrected content as well; it then simply makes the trail searchable.

```json
[
  {"id": "F1", "item": "SWR-0010", "severity": "major", "state": "closed", "closes": "REV-0007#F1",
   "text": "REV-0007#F1 (SWR-09, closing speeds not given): resolved, the criteria now name 80 mm/s and 250 mm/s."},
  {"id": "F2", "item": "SWR-0011", "severity": "minor", "state": "closed", "closes": "REV-0007#F2",
   "text": "REV-0007#F2 (SWR-04, two needs): resolved, storing the event is now SWR-0012."}
]
```

SWR-0012 is new and is a subject of this review as well.

## After code changed

`check` prints `SUSPECT ... <file> changed after review <record>: the code is no longer
the code that was reviewed` on the unit. The unit item is unchanged and stays
`approved`.

1. Review of the code: code checklist, the unit as subject, `--item-under-test` with
   the commit that holds the changed code (`scoping.md`, "Units and their code").
2. If the earlier review of this code left open findings, close them as above.
3. Because the commit was named, the record stores the hashes of the present source
   files; the `SUSPECT` line is gone.

When the review of code finds defects, the order is: record the review as `rework`;
correct the code (`/sw-unit-implement`); run the tests and the analysis again and record
the runs (`/sw-unit-verify`); commit; review the corrected code against the earlier
findings, with that commit named. Corrections made inside the sitting follow the same
order before the record is written: the runs are of the code the record names.

`COV-30` lines on the same unit say that the latest test run and analysis run describe
the old code. They are not cleared by a review: `/sw-unit-verify` runs and records again.
A review of code that has not been built, analysed and tested in this form is
possible but weak; say so, and ask whether to wait for the runs.

## After an upstream item changed

### Facts first

- `python tools/traceability.py check` prints one `SUSPECT` line per affected link:
  `suspect link: <changed item> (<role>) changed after review <record>`. The changed
  item itself shows `COV-19 ... stale approval`.
- `python tools/traceability.py impact <ID>` lists everything that depends on the
  changed item, by distance. For SWR-0003 of the power window project:

```
1  CMP-0003   software-component           WindowPos - window position and speed acquisition  (fulfils SWR-0003)
1  UNT-0002   software-unit                WindowPos - window position and speed  (implements SWR-0003)
2  CDS-0001   component-design             Detailed design of WindowPos  (refines CMP-0003)
...
21 items depend on SWR-0003
```

Only the items at distance 1 build on the changed item, and only they are reported as
suspect: here the component that fulfils the requirement and the unit that implements
it. An item further away becomes suspect when the item between them changes in turn.
A changed interface reaches the component that provides it and the components that use
it (`provided_by` and `used_by` of the interface), besides the units and views that
link to it.

### Order

1. The changed item, at its new content. Until it is approved again (or, for an
   imported item, until `/import-inputs` has registered the new version and it has
   passed its input acceptance review), nothing that links to it can be approved: the
   tool refuses, and `check` reports `UPSTREAM` on what is approved above it.
2. The items at distance 1.
3. Further items only if step 2 changed the item they link to. Run `check` again to see.

### Comparing with the new version

- Find out what changed. The earlier record lists the old hash under `references`; the
  text of the old version is in version control. Ask the user for the difference or for
  the change request that caused it. If neither is available, compare the whole subject
  with the whole new version.
- Hand the reviewing agent the ID of the changed item in addition to the usual input.
- If the subject itself did not change, the comparison is all there is to do: the
  reviewers read the subject against the new version and say whether it still agrees.
  No checklist is applied again and no checks file is written. Record it with
  `python tools/record.py review --reconfirm --reviewer "<name>" --verdict approved|rework
  <ID> ...`. The tool refuses when the subject's present content has no approving
  review: then the subject changed, and it is a full review with its checklist.
- Several unchanged items that build on the same change may share one reconfirmation,
  as long as the reviewers really compared each of them.
- A reconfirmation rests on the earlier review of the same content; the tool prints each
  record it rests on with its kind of criteria. Read them out to the user before
  recording when one used outside criteria or was itself a reconfirmation - a
  demonstration fixture is outside criteria - and let the reviewers choose a full
  review instead. `practices` does not tell the difference.

### Outcome

| The people find | Verdict | Then |
|---|---|---|
| the subject still agrees with the new version | `approved`, recorded with `--reconfirm` | the status stays `approved`; the new record lists the upstream item with its new hash, and for a unit it carries the code review over as recorded |
| the subject has to follow the change | `rework`, with a finding that says what has to follow | set it to `draft`; the authoring skill corrects it; then a full review |

Example: SYR-0001 arrives in a new version with a lower force limit. SWR-0003 and
SWR-0004 link to it and are reported as suspect. The reviewers find that SWR-0003
(window speed) does not depend on the limit: a new review of SWR-0003, verdict
approved. SWR-0004 states the speed drop at which an obstacle is detected, and that
value follows from the limit: verdict rework, back to `/sw-requirements`. Once SWR-0004
has changed and is approved again, `check` reports CMP-0004, the component that fulfils
it, and UNT-0003, the unit that implements it, as suspect, and the same steps repeat
one level down, the component first. UNT-0003 has code: whatever the outcome of its
comparison, the review of its code is recorded last, and if the unit has to change,
its code and the runs follow.

### After recording

Run `check`. The `SUSPECT` lines on the reviewed items are gone, because the newest
record lists the upstream item at its present hash. A line that is still there names
something this review did not cover: read it again, do not work around it.

## Comparison never recorded (`CONSISTENCY`)

The item is approved, but its newest approving record does not list one of the items it
builds on, or - for a unit - names no code revision. For an item: compare it with the
one named in the line and record a reconfirmation (`--reconfirm`), which fills in the
references. This is also what a component needs after an interface that names it as
provider or user was added and approved. For code: a review of the code with
`--item-under-test`; this is the normal state between the approval of a design and the
review of its code. Adding the missing item to some other review as a subject is not a
comparison.
