# A new version of an input

A source delivers version 2.2 of a document whose version 2.1 is registered and
accepted. An accepted input is read-only, with one exception the write hook knows: its
content may be replaced when `imported.version` changes with it. That is how a new
delivery enters. The item keeps its ID, every link to it stays, and the trace engine
marks everything derived from the old content as suspect. If the input is part of a
baseline, the change needs an approved change request first (section 3).

## 0. Is it a new version at all?

Compare the delivered version with the `imported.version` of the registered items of
the source and with the entries of `inputs` in `project.yaml`.

| Delivered version | Do |
|---|---|
| higher than every registered one | go on with section 1 |
| the same as a registered one | stop and ask: a repeated delivery needs nothing; a delivery that differs under the same version number is a query to the source, and nothing is registered from it |
| lower than a registered one (1.3 after 2.1) | stop and ask. A sender's mistake and a deliberate step back look the same from here. Register it only when the user confirms, after asking the source, that this is the version to work from; say that `imported.version` will then go down and that the earlier content is replaced |
| not comparable (a date against a number, a letter against a number) | ask the user which of the two is the later one; do not guess from the form |

## 1. Compare before anything is written

1. Find the registered items of the source: `python tools/traceability.py list
   --imported` names the imported inputs with their state; Grep the item folders for
   the `source` name to keep those of this document. Leave out the ones that are
   `obsolete` or `rejected`. Read the others by ID.
2. Take stock of the new version as in step 1 of the skill. For a ReqIF delivery,
   `python tools/reqif.py compare <file> --source "<document>"` lists the new, changed
   and removed objects by their identifier in the source; it writes nothing.
3. Compare object by object through the source identifier: every text section and the
   attributes that were mapped. Differences in line breaks and spacing are not
   changes; a changed value, word, unit or attribute is. Compare the allocation
   separately: which element answers which requirement, according to the new delivery.
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
1  SYE-0001   system-element               Window control software  (fulfils SYR-0002)
1  SYE-0002   system-element               Window drive hardware  (fulfils SYR-0002)
```

and ends with the number of items that depend on SYR-0002. Distance 1 is what must be
looked at first: the requirements derived from the input, and the elements that fulfil
it. The rest follows only if the items at distance 1 really change. The count is large
because everything hangs on the elements; it is an upper bound, not a work list.

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
the hook refuses a new text under the old version. `status` goes back to `draft`
because the acceptance covered the old content. Until the new content has been
accepted, the item can be corrected against the source like any freshly registered
one.

### The allocation of added and removed requirements

The allocation is stored on the element (`fulfils`), and an accepted element changes
only with a new version of its own source. So:

- If the architecture was delivered again with the requirements, register the new
  version of the element with its new `fulfils` list, like any changed item.
- If only the requirements came, the `fulfils` list of the accepted element cannot be
  touched. An added requirement then has no allocation, and rule COV-05 does not ask
  for a software requirement for it. A removed requirement leaves a `LINK` error on
  the element (`fulfils target ... is obsolete`) that nobody in the project can clear.
  Both are queries to the source: the architecture that matches the new requirements
  is missing. Say this in the hand-over and do not hide the `LINK` line.

## 5. What the checks show afterwards

Verified on a copy of the worked example, with DM-SYS-042 changed in version 2.2:

```
error   SUSPECT     SWR-0005   suspect link: SYR-0002 (derived_from) changed after review REV-0003  [SWE.1.BP6, SWE.1.BP7]
error   SUSPECT     SWR-0007   suspect link: SYR-0002 (derived_from) changed after review REV-0003  [SWE.1.BP6, SWE.1.BP7]
error   UPSTREAM    SWR-0005   approved, but SYR-0002 (derived_from) is in state draft  [SWE.1.BP6, SWE.1.BP7]
error   UPSTREAM    SWR-0007   approved, but SYR-0002 (derived_from) is in state draft  [SWE.1.BP6, SWE.1.BP7]
```

- `UPSTREAM` says that approved work rests on an input that is not accepted in its
  new content. It goes away with the acceptance review of the new version.
- `SUSPECT` says that the dependents were reviewed against the old content. The
  acceptance review does not clear it; it belongs to the dependents. One that is
  still right is cleared by a new `/review` of it, which records the new version of
  the input as its reference. One that has to change is reworked by its authoring
  skill, loses its approval, and makes the items below it suspect in turn.
- A removed item gives a `LINK` error on every live item that still points to it, for
  example `derived_from target SYR-0004 is obsolete`. Those items are reworked: the
  link is removed or moved, and the item reviewed again.
- For an added requirement that a software element fulfils, `COV-05` asks for a
  software requirement once the input is accepted; while it is a draft the line is
  `info`.

## 6. Hand-over for a new version

In addition to the normal hand-over:

1. The lists with counts; for `changed`, old and new text side by side.
2. The `SUSPECT`, `UPSTREAM` and `LINK` lines of `check --all` after writing, quoted.
3. Whether a change request was needed, its ID, and the items it names.
4. Allocations that could not be registered, and the query raised for each.
5. Next: `/review` for the changed and added items first (it applies the checklist
   `input-acceptance`); then, per suspect dependent, either `/review` (still right) or
   its authoring skill (has to change).

## When a new ID is right after all

Only in two cases is an input retired and registered again under a new ID:

- the source withdrew, split or renumbered it (table above);
- a transcription error is found in an item after its acceptance. The item cannot be
  corrected any more without pretending to a new version, so it is retired
  (`status: obsolete`, `superseded_by: <new ID>`) and registered again correctly. The
  `LINK` errors then name every item that has to be moved to the new ID. Where one of
  them is an accepted element that fulfils the retired requirement, the project cannot
  move the link itself: see "The allocation of added and removed requirements".
