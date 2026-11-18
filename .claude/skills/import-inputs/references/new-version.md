# A new version of an input

A source delivers version 2.2 of a document whose version 2.1 is registered and
accepted. An accepted input is read-only, with one exception the write hook knows: its
content may be replaced when `imported.version` changes with it. That is how a new
delivery enters. The item keeps its ID, every link to it stays, and the trace engine
marks everything derived from the old content as suspect. If the input is part of a
baseline, the change needs an approved change request first (section 3).

## 1. Compare before anything is written

1. Find the registered items of the source: `python tools/traceability.py list
   --imported` names the imported inputs with their state; Grep the item folders for
   the `source` name to keep those of this document. Leave out the ones that are
   `obsolete` or `rejected`. Read the others by ID.
2. Take stock of the new version as in step 1 of the skill.
3. Compare object by object through the source identifier: every text section, the
   attributes that were mapped, the links the delivery states. Differences in line
   breaks and spacing are not changes; a changed value, word, unit, attribute or
   allocation is.
4. Sort every object into one of these lists:

| List | Meaning |
|---|---|
| unchanged | same identifier, same content |
| changed | same identifier, different content |
| added | identifier not registered so far |
| removed | registered, but no longer in the delivery |
| split or renumbered | the source says that one identifier was replaced by others |

   A changed identifier with the same text, without a word from the source about it,
   is a query: do not guess that two objects are the same.
5. Use the change list of the source (revision history, change marks) as a cross-check
   only. Where it and the comparison disagree, that is a proposed finding for the
   review.

The comparison is made by reading, not by a tool. Say so in the report, label it as
semantic, and ask the user to spot-check it against the source.

## 2. Show what depends on the changes

For every changed, removed, split or renumbered item run

```
python tools/traceability.py impact <ID>
```

and show the result. For the worked example and a change of DM-SYS-042, registered as
SYR-0002, it begins:

```
1  SWR-0005   software-requirement         End of the reversal  (derived_from SYR-0002)
1  SWR-0007   software-requirement         Priority of the reversal request  (derived_from SYR-0002)
2  UNT-0003   software-unit                AntiPinch - obstacle detection state machine  (implements SWR-0005)
```

continues with the unit tests of UNT-0003 at distance 3, and ends with the number of
items that depend on SYR-0002. Distance 1 is what must be looked at first; the rest
follows only if the items at distance 1 really change.

## 3. Decide how the change enters

- Search `records/baselines` with Grep for the IDs of the items that will be replaced
  or retired. If a final baseline lists one of them and its `purpose` is not among
  `trace.internal_baselines` of `project.yaml`, stop before writing and hand over to
  `/change-request`, with these items as the affected items. The comparison and the
  `impact` output are the input for its impact analysis. Come back when the request is
  approved. The write hook enforces this: it refuses to replace or to retire an
  accepted input that such a baseline lists unless an approved change request names
  it, also when the new content carries a new `imported.version`.
- Items of the delivery that no baseline lists, and added ones, need no change
  request. Do not register them ahead of the rest: a delivery enters as a whole, so
  wait for the request when any of its items needs one.
- Otherwise show the lists and ask: "May I register version <new> like this?"

## 4. Write

| List | What is written |
|---|---|
| unchanged | nothing. The item keeps its file and its `imported.version`: that is the version in which its content arrived. |
| changed | the same item, in one edit: the content of the new version, `imported.version` and `imported.received` of the new delivery, `status: draft`. The ID and `source_id` stay. |
| added | a new item, as in a first import. |
| removed | on the old item only its disposition: `status: obsolete` and `superseded_by` with the reason, for example "removed by the source in version 2.2". |
| split or renumbered | new items for the new identifiers; on the old item `status: obsolete` and `superseded_by` naming the successor, or a text naming several. |

Then add an entry for the new version to `inputs` of `project.yaml`; the entry of the
earlier version stays.

The change of content and the change of `imported.version` must be in the same edit:
the hook refuses a new text under the old version, and it refuses nothing else that
belongs to a new delivery. `status` goes back to `draft` because the acceptance covered
the old content. Until the new content has been accepted, the item can be corrected
against the source like any freshly registered one.

## 5. What the checks show afterwards

Verified on a copy of the worked example, with DM-SYS-042 changed in version 2.2:

```
error   SUSPECT     SWR-0005   suspect link: SYR-0002 (derived_from) changed after review REV-0002  [SWE.1.BP6, SWE.1.BP7]
error   SUSPECT     SWR-0007   suspect link: SYR-0002 (derived_from) changed after review REV-0002  [SWE.1.BP6, SWE.1.BP7]
```

- Every approved item that was reviewed against the old content is reported. The
  acceptance review of the new version does not clear these lines; they belong to the
  dependents.
- A dependent that is still right is cleared by a new `/review` of it, which records
  the new version of the input as its reference. A dependent that has to change is
  reworked by its authoring skill, loses its approval, and makes the items below it
  suspect in turn.
- A removed item gives a `LINK` error on every live item that still points to it, for
  example `derived_from target SYR-0004 is obsolete`. Those items are reworked: the
  link is removed or moved, and the item reviewed again.
- For an added requirement that is allocated to software, `COV-05` asks for a software
  requirement once the input is accepted; while it is a draft the line is `info`.

## 6. Hand-over for a new version

In addition to the normal hand-over:

1. The lists with counts; for `changed`, old and new text side by side.
2. The `SUSPECT` and `LINK` lines of `check --all` after writing, quoted.
3. Whether a change request was needed, its ID, and the items it names.
4. Next: `/review` with the checklist `input-acceptance` for the changed and added
   items; then, per suspect dependent, either `/review` (still right) or its authoring
   skill (has to change).

## When a new ID is right after all

Only in two cases is an input retired and registered again under a new ID:

- the source withdrew, split or renumbered it (table above);
- a transcription error is found in an item after its acceptance. The item cannot be
  corrected any more without pretending to a new version, so it is retired
  (`status: obsolete`, `superseded_by: <new ID>`) and registered again correctly. The
  `LINK` errors then name every item that has to be moved to the new ID.
