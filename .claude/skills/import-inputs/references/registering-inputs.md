# Registering a delivery

## Choosing the type

The type of an imported item says what the content is for the team, and it must be a
type the team's own items can link to (`links` in `schema/items.yaml`). The title of
the delivered document does not decide it.

| Delivered content, seen from the team | Used first by | Type | `imported` |
|---|---|---|---|
| Customer or stakeholder documents that the team itself clarifies and agrees | SYS.1 | `stakeholder-requirement` | no: see "With SYS.1 in scope" below |
| Stakeholder requirements already agreed by another party | SYS.2 | `stakeholder-requirement` | yes |
| Requirements on the system; in a software-only delivery, the requirements on the software as a whole | SYS.3, SWE.1, SYS.5 | `system-requirement` | yes |
| Elements of the system architecture | SWE.1, SYS.4 | `system-element` | yes |
| Interfaces of the system architecture: hardware-software interface, bus signals, diagnostic access | SWE.1, SWE.2, SYS.4 | `system-interface` | yes |
| Behaviour across system elements: sequences, modes, timing chains | SWE.1, SYS.4 | `architecture-view` with `level: system` | yes |
| Software requirements | SWE.2, SWE.3, SWE.6 | `software-requirement` | yes |
| Software architecture: components, interfaces, views | SWE.3, SWE.5 | `software-component`, `software-interface`, `architecture-view` with `level: software` | yes |
| Component descriptions or models | SWE.3 | `software-component` with `model` naming the delivered file; `software-interface` for what the team's units realize or use | yes |
| Detailed design: component designs, unit descriptions | SWE.4 | `component-design`, `software-unit` | yes |
| Existing code | SWE.3, SWE.4 | no item of its own: see "Code" below | - |

Two cases need the user's confirmation before anything is written.

**The delivery is at the level of a process in scope.** The customer delivers
"software requirements" and SWE.1 is in scope; or a "system requirements
specification" arrives and SYS.2 is in scope. For the team this is the set to analyse,
not the result of the analysis. Register it one level up - as `system-requirement` in
the first case, as `stakeholder-requirement` in the second - so that the team's own
requirements can be `derived_from` it. Say this plainly and ask. If the user wants the
delivered set to be the team's requirements as they are, the process is not really
theirs to perform: send them back to `/aspice-start`, step 3 and step 4.

**The delivery mixes levels.** One document holds system requirements, architecture
and constraints on the software. Sort by content, object by object, and show the
sorting. An object that cannot be sorted is a question to the user, then a query.

## What an imported item must and may carry

For an imported item the trace engine enforces only what is always required: `id`,
`type`, `title`, `status`, and an `imported` block that names at least `source` and
`version`; for `stakeholder-requirement` also `source_document`; for
`architecture-view` also `level` and `kind`. Every value that is written is still
checked against the allowed values, and every structured attribute against its keys.
So the rule is: write what the delivery states and what maps cleanly; leave out the
rest.

| Part | Rule |
|---|---|
| `imported.source` | The `source` of the entry in `inputs` of `project.yaml`, letter for letter. `/next-step` finds unregistered inputs by this string. |
| `imported.version`, `imported.received` | Version of the delivery in which this content arrived, and the date received. Both quoted. |
| `imported.source_id` | The identifier in the source, unchanged. Without identifiers: the place, for example `4.2.3 paragraph 2`, exact enough to find the passage again; and a query asking the source for identifiers. |
| `title` | The source's own heading or object name. If there is none, a few words taken from the text itself. Never a judgement ("unclear timing requirement"). |
| `status` | `draft`. `/review` moves it on. |
| `asil`, `security_relevant` | Only as stated by the source. |
| `kind`, `priority`, `release`, `verification_method`, `origin` | Only when the source has such an attribute and its values map one to one. A scale that does not map (priority 1 to 5, a customer-specific category) is left out; the mapping question goes on the query list. |
| Structured attributes (`elements`, `operations`, `functions`, `data`, `table`) | Only when the delivery gives every mandatory key of the structure. Otherwise keep the delivered table as a table in the text section and raise a query. |
| `links` | Only relations the delivery states: an allocation, `derived_from` between delivered levels, `part_of`, `realizes`, `shows`. The target must be registered too. |
| Allocation | Written where the delivery states it: `allocated_to` on the requirement when the requirement names its element, `fulfils` on the element or interface when the architecture lists the requirements it answers. The two are equivalent for the checks; do not write both for one pair. An architecture that arrives after the requirements were accepted is registered with `fulfils`, because accepted requirements are not changed. |
| Sections | The section names of the type. Put the delivered text under the section it belongs to; keep the source's own sub-headings as third-level headings. A section the delivery has no text for is left out - do not write `Not applicable:` in the name of the source. |

Tables stay tables, cell for cell. A figure cannot be carried over: put one line in
square brackets where it stood, `[Figure 7 of the source, not reproduced]`, and add a
proposed finding for the review if the text cannot be understood without it. Square
brackets mark the only words in an imported item that are not the source's.

## Splitting

| Situation | Do | Do not |
|---|---|---|
| One identified object states two needs | one item; query "compound requirement" | split it into two items with invented identifiers |
| A requirement refers to "the previous requirement" or "the table above" | keep the wording; the reference is resolvable through `source_id` | replace the reference by an item ID of the project |
| The same identifier appears twice with different text | register neither; query | pick one |
| An object without identifier between identified ones | use its place as `source_id`; query | attach it to its neighbour |
| A list under one lead-in sentence ("The module shall: a) ... b) ...") | one item with the whole list, unless the source identifies the entries separately | one item per entry without the lead-in |
| Text in another language | register it in that language | translate |

## With SYS.1 in scope

Stakeholder requirements are then the team's own work product: the record of what was
received and what the team concluded about it. Register them without `imported`, with
`source_document` (name and version) and `source_id`, the `Statement` unchanged.

Each one needs an `assessment` before approval: `accepted`,
`accepted-with-deviation`, `rejected` or `needs-clarification`. The assessment is a
decision of the people who have to fulfil the requirement. Set it only to what the
user states; an item with an open query is a candidate for `needs-clarification`, and
you may say so. Any value but `accepted` needs `agreement`: the ID of the
communication record that documents what was agreed with the stakeholder. Reasons and
notes of the team go into `Assessment notes`, never into `Statement`.

Imported stakeholder requirements (SYS.1 out of scope) carry an `assessment` only when
the delivery states one per requirement. Without it rule COV-01 treats the item as
accepted and asks for a system requirement derived from it. If the delivering party
did reject or defer a requirement, that has to be stated by them: put the question on
the query list rather than leaving the requirement out.

## Code

Code is not an item. What it means for the registration depends on what came with it:

- Code delivered with unit descriptions: register the descriptions as `software-unit`
  items and name the files in `source_files`. The files themselves are put where the
  user decides, under a source root.
- Code delivered without design, to be used as it is: it belongs under a path that
  `paths.third_party` or `paths.generated` of `project.yaml` covers. That is a change
  of scope data: `/aspice-start`.
- Code delivered without design, to be maintained by the team with SWE.3 in scope: the
  design has to be written by the team (`/sw-detailed-design`). Nothing is imported;
  the delivery is recorded in `inputs` and the gap is named in the hand-over.

## Correcting and retiring

| Situation | What is possible |
|---|---|
| An error in an item whose acceptance review is not recorded yet | edit the item against the source |
| An error made at registration, found in an accepted item | the content is frozen: retire the item (`status: obsolete`, `superseded_by: <new ID>`) and register it again correctly; `LINK` findings then name what still points to the old one |
| The source delivers a new version | replace the content in place together with the new `imported.version`: `new-version.md` |
| The source withdraws a requirement | `status: obsolete` and `superseded_by` with the reason; nothing else on the item |
| An object was registered that is no requirement or element | `status: rejected` with `rejection_reason` |

An accepted input that is listed by a baseline whose purpose is not an internal one
is replaced or retired only with an approved change request that names it; the write
hook refuses it otherwise. In that case `/change-request` comes first.

A problem with what the source wrote is none of these. It is a query.

## Large deliveries

Work chapter by chapter: take stock, show, ask, write, check. Keep the running
numbers (objects read, items written, not registered, queries) and show them after
each chapter. Never report a chapter as registered that was only skimmed.
