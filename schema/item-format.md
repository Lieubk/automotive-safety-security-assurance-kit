# Item file format

How engineering items are stored. The rules for *which* items, attributes and links
exist are in [items.yaml](items.yaml); this page defines the file layout that
`tools/traceability.py` reads.

## One item, one file

- File name: `<ID>.md`, in the folder its type names in the schema (relative to the
  project root), for example `spec/software/requirements/SWR-0003.md`.
- ID: `<PREFIX>-<NNNN>`. The prefix comes from the type. Numbers are never reused.
- Encoding UTF-8, line endings LF.

```markdown
---
id: SWR-0003
type: software-requirement
title: Obstacle detection during automatic closing
status: approved
kind: functional
priority: must
release: R1.0
asil: B
security_relevant: false
verification_method: test
origin: derived
links:
  derived_from: [SYR-0002]
---

## Statement

While the window closes automatically, the software shall report an obstacle within
10 ms after the window speed has dropped by more than the calibrated threshold.

## Verification criteria

With a speed drop of threshold + 1 step injected at any position inside the protected
zone, the obstacle signal is set no later than the second 5 ms cycle after the drop.
```

## Front matter

- YAML between two `---` lines at the top of the file.
- `id`, `type`, `title`, `status` are always present.
- `links` is a mapping from link role to a list of target IDs. A link is written on
  the downstream item only - the one that depends on the other; the reverse direction
  is computed. That is why a requirement does not name the component it is allocated
  to: the component names the requirements it `fulfils`.
- A target may address one design element inside an item: `UNT-0012#AntiPinch_Step`.
- Structured attributes (`elements`, `operations`, `functions`, `data`, `table`) are
  lists of mappings with the keys the schema defines under `structures`;
  `resource_budget` is a single mapping.
- `script` of a test case is `<repository path>::<test function>`.
- Avoid bare `yes`, `no`, `on`, `off` as values: YAML 1.1 parsers read them as
  booleans. Use `true` / `false` where a boolean is meant.

## Body

- Second-level headings (`## Name`) are sections. Section names are those of the type
  in the schema. Text before the first heading is ignored by the checks.
- A section that does not apply is not left out when the schema requires it: write
  `Not applicable:` followed by the reason.
- Diagrams are code blocks (Mermaid or PlantUML), so that they are diffable and
  reviewable.

## Content hash

Approval, baselines and suspect links all refer to the content of an item at one point
in time. That content is identified by a hash computed as follows:

1. Take the front matter as data and remove the keys `status`, `source_files` and
   `progress`, and the link role `delivers` under `links` (the key `links` itself when
   nothing else is left in it).
2. Serialize it as JSON with sorted keys, separators `,` and `:`, no ASCII escaping.
3. Take the body, convert line endings to LF, strip trailing whitespace from every
   line, and strip blank lines at the start and the end.
4. Hash `<json>\n<body>` with SHA-256 and keep the first 12 hexadecimal characters.

Changing the status does not change the hash, and neither does `source_files`: a unit
design stays approved when its code is registered. In the same way a work package stays
approved while its owner records progress (`progress`) and links the items it has
produced (`delivers`): both are tracking, not plan. The code is covered separately - a
review that names the code revision stores a hash of every source file. Changing
anything else changes the hash. An item whose status is `approved` while no final review
record lists its current hash has a stale approval.

## Records

Review records, test runs, static analysis runs, baselines and communication records
are items too (same file layout), but they are evidence rather than design: once
their status is `final` they are never edited, only superseded by a new record.
Test runs and static analysis runs are written by tooling from tool reports.

A review record names what was reviewed and what it was compared against, each at a
content hash:

```yaml
id: REV-0004
type: review-record
status: final
checklist: software-requirements v2
reviewers: [A. Reviewer]
verdict: approved
subject:                       # the items this review approves
  - {item: SWR-0003, hash: 4a21cec0d127}
references:                    # the upstream items the subject was checked against
  - {item: SYR-0002, hash: 10c9e2ba6cc9}
findings:
  - {id: F1, item: SWR-0003, text: "threshold unit missing", severity: minor, state: closed}
```

`subject` is what makes an approval valid; `references` is the consistency evidence.
When a referenced item changes afterwards, every link to it from the subject is
reported as suspect until a new review records the new hash.
`python tools/traceability.py hash --upstream <ID>...` prints both blocks.

An item builds on the items it links to. A software component also builds on every
interface that names it under `provided_by` or `used_by`; these two relations are
stated on the interface and are treated like links of the component.

`checklist_source` says what the verdict rests on: `toolkit` (a checklist of the
toolkit at the cited version, with a result per check), `project` (a checklist under
`checklists/` of the project at the cited version, with a result per check; for one
that extends a toolkit checklist, `checklist_extends` names that one with its hash and
the checks of both have a result, for one that replaces it `checklist_replaces` names
it), `external` (criteria from outside the toolkit and the project, named in
`checklist`), or `reconfirmation` (the subjects did not change since their last
approving review and were compared with new versions of what they build on).

## Imported items

An item received from outside the project's process scope (for example system
requirements delivered to a software supplier) carries `imported:` with its source,
version and date received. Imported items are read-only inputs: the project does not
change them, the rules of the process that produced them do not apply, and an input
acceptance review record covers them at the boundary.

## Project configuration read by the trace engine

`project.yaml` in the project root:

```yaml
scope:
  processes: [SWE.1, SWE.2, SWE.3, SWE.4, SUP.8]   # the processes the project is responsible for
paths:
  items: [plans, spec, verification, records]       # folders scanned for item files
  source_roots: [src]                               # code that must belong to a software unit
  generated: ["src/gen/**"]                         # exempt from the unit ownership rule
  third_party: ["src/vendor/**"]
trace:
  views_not_applicable:                             # view kinds the project does not need, with the reason
    memory-layout: "single flash partition, layout fixed by the supplier boot loader"
  internal_baselines: [working]                     # baseline purposes that need no communication record
```

A coverage rule is active only when one of the processes it supports is in
`scope.processes`.
