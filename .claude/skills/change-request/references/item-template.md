# Change request item

File: `records/changes/<ID>.md`. Attributes and sections are those of type
`change-request` in `schema/items.yaml`; the layout is defined in
`schema/item-format.md`. The values below belong to the power window example and are
invented.

```markdown
---
id: CR-0001
type: change-request
title: Protected zone from 4 mm window opening
status: analysed
requester: Customer system engineering, front door module
links:
  affects: [SYR-0001, SWR-0004, CDS-0001, UNT-0003, UT-0016]
---

## Description

Request: the closing force limit shall apply from a window opening of more than 4 mm
instead of more than 5 mm.

Reason given by the requester: the door seal of the next vehicle variant has a shorter
entry. Between 4 mm and 5 mm the glass is not yet guided by the seal, and an obstacle
there has to be detected.

Source: system requirements specification of the front door module, version 2.2,
received on 2026-11-16. It changes the requirement registered as SYR-0001 at version
2.1. `/import-inputs` has compared the two versions; nothing else in them differs.

Wanted for: release R1.1.

Related change requests: none.

## Impact analysis

Candidates from `impact SYR-0001`, read distance by distance behind the items that
change, and from a search for "5 mm" and `ANTIPINCH_ZONE_LIMIT` in the item, source and
test folders.

### Items that change

| Item | In baseline | What changes | Changed with |
|---|---|---|---|
| SYR-0001 | BL-0002 | content of version 2.2, registered with the new `imported.version` | `/import-inputs` |
| SWR-0004 | BL-0002 | zone limit in the statement; criterion 4 moves to 4.0 mm and 4.5 mm; the remark on the seal in `Analysis` | `/sw-requirements` |
| UNT-0003 | BL-0002 | `ANTIPINCH_ZONE_LIMIT` in `Behavior`: 8 counts (4 mm) | `/sw-detailed-design` |
| UT-0016 | BL-0002 | boundary values 8 and 9 counts instead of 10 and 11 | `/sw-unit-verify` |
| CDS-0001 | BL-0002 | the risk "run-out pulses" quotes the 5 mm limit; found by the text search, no link leads here | `/sw-detailed-design` |

Code and test code: the constant `ANTIPINCH_ZONE_LIMIT` in `src/antipinch/AntiPinch.h`
(`/sw-unit-implement`); the function `test_UT_0016_protected_zone_and_invalid_position`
in `tests/unit/test_AntiPinch.c` (`/sw-unit-verify`).

### Reviewed again without change

| Item | Why |
|---|---|
| SWR-0003 | derived from SYR-0001, which changes; says nothing about the zone |
| CMP-0004 | fulfils SWR-0004, which changes; names the protected zone without a value |
| UT-0013 to UT-0015, UT-0017 to UT-0020 | verify UNT-0003; their steps do not use the zone limit |

### Looked at and not affected

| Item | Why not |
|---|---|
| SYE-0001, SYE-0002 | fulfil SYR-0001; inputs that version 2.2 leaves as they are |
| CDS-0002, IFC-0003, VIEW-0001 to VIEW-0005 | hang on CMP-0004, whose text stays; none carries the limit |
| IFC-0002 | range and resolution of the window opening are unchanged; 4 mm is 8 counts |
| CMP-0003, UNT-0002, UT-0006 to UT-0012 | reached only through SWR-0003, which does not change |

### Open question to the requester

1. SWR-0008 ends automatic closing at an opening of 5 mm or less. It is derived from
   SYR-0003, which version 2.2 does not change. Does the end of automatic closing follow
   the new limit? If it does, SWR-0008 and the reused component CMP-0002 are affected,
   and this request has to be analysed again.

### Regression scope

All unit test cases of UNT-0003 (UT-0013 to UT-0020) and the static analysis of the
unit, on the commit that holds the change: regression rule of PLN-0001. The run record
holds a verdict for every approved unit test case, so the other two units are run as
well. Tests on the door module are the customer's.

### Effort, schedule, risk

Effort: 2 person-days (estimate of the software developer, 2026-11-17). Schedule: fits
release R1.1; release R1.0 is not touched. Risk: the position error of up to 1.5 mm
after a change of direction (CDS-0001) is a larger share of a 4 mm zone than of a 5 mm
zone; the design evaluation of CDS-0001 has to say whether it is still acceptable.
Highest ASIL among the items that change: B.

### Dependencies

No other open change request affects these items. The answer to question 1 can widen
the request.

### Confirmation criteria

1. SWR-0004 is approved with the limit 4 mm, and SWR-0003 is reviewed again, both in
   reviews that record SYR-0001 at version 2.2 as a reference. CMP-0004 is reviewed
   again against the changed SWR-0004.
2. UT-0016 passes with the boundary values 4.0 mm (request stays clear) and 4.5 mm
   (request set within 10 ms), in a unit test run on the commit that holds the change.
3. All unit test cases of UNT-0003 pass in that run, and the coverage of the unit still
   meets the targets of PLN-0001.
4. The changed code of UNT-0003 is reviewed, in a review recorded with the commit
   that holds the change.
5. The trace check reports no `SUSPECT`, `UPSTREAM`, `COV-19` or `COV-30` finding on
   any item named in this analysis.
6. The requester's answer to question 1 is recorded.
```

## Notes

- `title` is a short name; what is requested stands in `Description`.
- `requester` is always present: the role or party that raised the request. A person's
  name only if the user gives one.
- `Description` is needed from the first state on. It holds the request, the reason,
  the source, the wanted release and related change requests.
- `Impact analysis` and `links.affects` are needed from state `analysed` on. The
  section name is fixed by the schema; the third-level headings inside it are this
  toolkit's convention and may be left out where there is nothing to say, except
  "Items that change" and "Confirmation criteria".
- `affects` names every item whose content changes or which is retired, by its plain
  ID. Items that are only reviewed again are listed in the section, not linked:
  the trace check follows them as `SUSPECT` findings.
- `resolves` names the `problem-report` that caused the request:

  ```yaml
  links:
    affects: [SWR-0004, UNT-0003, UT-0016]
    resolves: [PRB-0001]
  ```

- A request raised by an answered `query` names the query under `affects`, beside the
  items that change, and cites it in `Description` as its source. `resolves` takes
  problem reports only. The query is closed when the items it is about are in line with
  its answer, which is what the change brings about:

  ```yaml
  links:
    affects: [QRY-0001, SYR-0001, SWR-0004, CDS-0001, UNT-0003, UT-0016]
  ```

- `decision` is added when the deciding body has decided, and `rejection_reason` when
  the request is rejected. The trace check reports a `SCHEMA` error when either is
  missing in these states. Both in the words the user gives:

  ```yaml
  status: rejected
  decision: "Change Control Board (project lead, software architect), 2026-11-19: rejected"
  rejection_reason: "the seal of the next variant is not confirmed; to be raised again with the variant decision"
  ```

- The states are `submitted`, `analysed`, `approved`, `rejected`, `implemented`,
  `verified`, `closed`. `approved` on a change request means "decided", not "reviewed".
- Figures for effort and schedule are the user's or the owners'. Write who estimated
  and when.
