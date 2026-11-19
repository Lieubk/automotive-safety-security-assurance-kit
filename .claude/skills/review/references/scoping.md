# What goes into one review

## Where candidates come from

| Source | How it shows | What the review has to do |
|---|---|---|
| New or reworked item | `list --status draft`, `list --status in-review` | full review against the checklist |
| Changed after approval | `COV-19 ... stale approval: content changed since review REV-0003` | full review of the present content; the earlier record tells what was approved before |
| Approved without a review | `COV-19 ... approved, but no final review record covers it` | full review; tell the user that the status claimed an approval nobody gave |
| Findings left open | `COV-19 ... review REV-0007 left findings open: F1` on a draft (with `check --all`), or `... still has open findings` on an approved item | the author corrects first; then a review that closes each finding with `closes` (`re-review.md`) |
| Approved above something that is not | `UPSTREAM ... approved, but SYR-0002 (derived_from) is in state in-review` | review the item named in the message; the approved item above it then stands again |
| Upstream item changed | `SUSPECT ... suspect link: UNT-0002 (verifies) changed after review REV-0006` | compare the item with the new version of the upstream item (`re-review.md`) |
| Code changed after its review | `SUSPECT ... src/windowpos/WindowPos.c changed after review REV-0005: the code is no longer the code that was reviewed` | review of the code of the unit |
| Code never reviewed | `CONSISTENCY ... review REV-0005 does not record src/windowpos/WindowPos.c: a review of the code against the design is not evidenced` | review of the code of the unit |
| Comparison not recorded | `CONSISTENCY ... review REV-0005 does not record IFC-0002 (uses) as a reference` | compare the item with the item named and record a review that lists it |

Not candidates: records (they are final), items in state `rejected` or `obsolete`, and
drafts whose author says they are not finished. Change requests, problem reports and
queries are not candidates either. The record tool takes any item ID, and a change
request does become the subject of a review record - the review of its implementation -
but that review is prepared and recorded by `/change-request` with its own checklist,
and it moves the change request to `verified`, never to an approval. Baselines are
checked by `/baseline`.

A `QUERY` line (an open query is about an approved item) is not a candidate but a fact
to show: the reviewers should know which questions to the source are still open.

The same line can be printed more than once, for example when a test case links to
several functions of one unit. Count items, not lines.

## Work product kinds and their checklists

One review applies one checklist, and the record cites it. The `Applies to:` sentence
of each checklist decides; it can run over several lines, so read it to its end. This
table says what to expect.

| Kind | Item types | Checklist in `.claude/docs/checklists/` |
|---|---|---|
| Imported inputs | any type with `imported` set; the checklist names what else it covers | `input-acceptance.md` |
| Software requirements | `software-requirement` | `software-requirements.md` |
| Software architecture | `software-component`, `software-interface`, `architecture-view` and `design-decision` of level `software` | `software-architecture.md` |
| Detailed design | `component-design`, `software-unit`, `design-decision` of level `detailed-design` | `software-detailed-design.md` |
| Unit code | `software-unit` as subject, read together with the files under `source_files` | `software-unit-code.md` |
| Unit test specification | `unit-test`, with the test code its `script` names | `unit-test-specification.md` |
| Plans | `plan` | `plan.md` |
| Item definition (ISO/SAE 21434) | `item-definition` | `item-definition.md` |
| TARA | `asset`, `damage-scenario`, `threat-scenario` | `tara.md` |
| Cybersecurity goals and claims | `cybersecurity-goal`, `cybersecurity-claim` | `cybersecurity-goal.md` |
| Hazard analysis and safety goals | `hazardous-event`, `safety-goal` | `hara.md` |
| Safety analyses | `safety-analysis` | `safety-analysis.md` |
| Tool evaluations | `tool-evaluation` | `tool-evaluation.md` |
| Anything else of the `engineering` lifecycle | for example `system-requirement` written by the project, `software-integration-test` | whichever checklist names the type; if none does, the semantic part is NOT ASSESSED |

Cite a checklist as its file name without `.md`, followed by `v` and the number of its
version line: `software-requirements v2`, `software-unit-code v2`, `plan v10`. The tool
looks the file up and refuses a citation it cannot find or whose version is not the one
in the file. It also accepts the title without the word "checklist"
(`software requirements review v2`); use the file name, it cannot be mistyped as easily.

When the toolkit has no checklist for the type and the reviewers use criteria of their
own, `--checklist` names those criteria as the user states them, and the command gets
`--external-criteria`. The record then says `checklist_source: external`, and the tool
asks for no check results. Use this only for criteria the user names; never to get
around a checklist that exists.

## Units and their code

Two checklists name `software-unit`. The design checklist reviews the unit item. The
code checklist reviews the files under `source_files` against the unit item, which must
already be approved at its present content. Both reviews have the unit as subject.

What tells the two apart in the record is `--item-under-test`. Without it the record
covers the design only. With it the tool stores a hash of every source file of the
unit, and the record says: this code, at this commit, was compared with this design.
Registering `source_files` on a unit does not change its content hash, so writing the
code does not make the design approval stale.

For every unit that has code, ask before the review: "Is the code part of this
review?" Pass `--item-under-test <commit>` exactly when the answer is yes.

| What `list` and `check` show for the unit | Reviews, in this order |
|---|---|
| in `draft` or `in-review`, or `COV-19`; no source file exists yet | design review |
| in `draft` or `in-review`, or `COV-19`; source files exist | design review, then review of the code |
| approved; `CONSISTENCY ... a review of the code against the design is not evidenced` | review of the code |
| approved; `SUSPECT ... the code is no longer the code that was reviewed` | review of the code |
| approved, has code; `SUSPECT ... suspect link` only | reconfirmation against the changed upstream item (`--reconfirm`), which carries the review of the unchanged code over; if the unit has to change, design review, then review of the code |

The newest approving record of a unit decides. A design review recorded without
`--item-under-test` becomes that record, and `check` then prints the `CONSISTENCY`
warning about the code again even if an earlier record named it. So for a unit that
has code and a changed design, the review of the code is the last one recorded. A
reconfirmation is different: it carries the code review of the record it rests on over
exactly as recorded, so unchanged code needs no new review, and code that changed
since stays `SUSPECT`.

When the code is part of the review:

- The subject is the unit, or the units of one component. The unit stays `approved`.
- Ask which commit holds the code under review, and have the user confirm that the
  working tree is clean at that commit: the tool hashes the files as they lie there. It
  should be the commit the latest test run and analysis run name; `status` prints it.
- Hand the reviewing agent the unit IDs and the commit; it reads the files under
  `source_files`.
- Findings against the code go to `/sw-unit-implement`. A finding against the design
  sets the unit back to `draft` and goes to `/sw-detailed-design`.
- Test runs and analysis runs of changed code are a matter for `/sw-unit-verify`
  (`COV-30`), not for this review.

When it is not: say in the hand-over that the code of the unit is not reviewed, and
that `check` says so with a `CONSISTENCY` warning.

## Grouping

1. One checklist per review.
2. Keep together what has to be read together: the children of one parent (checks about
   the set need the whole set), a component with its interfaces and the views that show
   it, a component design with its units, the test cases of one unit.
3. Keep apart what was not compared. Items in one record count as compared with each
   other: the trace engine treats a link between two subject items as covered by that
   review. Never add an item to a review to make a `CONSISTENCY` line go away.
4. Keep it readable in one sitting. As a guide: about ten requirements, one component
   with its interfaces, one or two units with their design, the test cases of one unit.
   A larger set becomes several reviews. The user decides the cut.
5. From the top down. The tool refuses to approve an item while an item it links to is
   in `draft` or `in-review`, unless that item is a subject of the same review; and
   `check` reports an approved item above an unapproved one as `UPSTREAM`. So: inputs
   before the requirements derived from them, requirements before the components that
   fulfil them, components before their design, units before their test cases.
6. One delivery, one sitting: all imported items with the same `imported.source` and
   `imported.version` are reviewed together, including those with an open query.

## A delivery with open questions

Every item of the delivery is reviewed, also one that a query is about. An open query
about an input is cited in a finding on that input, by its ID. One record has one
verdict, so the result of the sitting is written as two records when the verdicts
differ:

| Record | Subjects | Verdict | Findings |
|---|---|---|---|
| first | the inputs with an open finding - as a rule those an open query is about | `rework` | one per query, open, citing `QRY-nnnn`, on the input the query is about |
| second | the other inputs of the delivery | `approved` | none open |

Both records cite the input acceptance checklist and carry a result for every check.
An input that links to one of the first group cannot be approved before it: the tool
refuses. It is left out of the second record, stays `in-review`, and is approved
together with that group later. Say which inputs wait for this reason.

The inputs of the first record go back to `draft`. Nothing is changed in them. When
the answer arrives and the query is closed, they are reviewed again: if the text did
not have to change, the new record closes the finding with `closes`; if it did, the
source delivers a new version and `/import-inputs` registers it.

If the reviewers decide that an open question does not stand in the way of using the
input, the finding is closed with that reason and their name, and the input belongs to
the second record. `check` then keeps a `QUERY` warning on it until the query is closed.

Example for the power window project, software requirements just written:

| Review | Items | Checklist | Upstream items |
|---|---|---|---|
| 1 | SWR-0001, SWR-0002, SWR-0003 (position and speed) | software-requirements v2 | from `hash --upstream SWR-0001 SWR-0002 SWR-0003` |
| 2 | SWR-0004, SWR-0005, SWR-0006 (anti-pinch) | software-requirements v2 | from `hash --upstream SWR-0004 SWR-0005 SWR-0006` |
| 3 | SWR-0007, SWR-0008, SWR-0009 (command and motor) | software-requirements v2 | from `hash --upstream SWR-0007 SWR-0008 SWR-0009` |

The number in the last column is never estimated. For one requirement the command prints:

```
subject:
  - {item: SWR-0003, hash: 8d80d6da2d66}
references:
  - {item: SYI-0001, hash: fd6d4321eb97}
  - {item: SYR-0001, hash: c36e504b2d84}
```

`references` holds every item the subject links to, whatever the link role, that is not
itself part of the subject. `record.py review` writes the same list into the record.
An allocation is a link of the architectural element (`fulfils`): the requirement
appears among the references of the component's review, not the other way round.

## Ready for review

| Condition | How to tell | If not |
|---|---|---|
| No structural error | no `FORMAT`, `SCHEMA` or `LINK` line of level `error` on the item after it was set to `in-review` | back to `draft`, to the authoring skill |
| The author considers it finished | ask; `COV-19 ... left findings open` on a draft says the last review's findings were not yet dealt with | leave it out |
| Mandatory content for approval is there | `check --all` prints no `still to come before approval` line for the item; `conditions` of the schema with that stage are met (read them: the preview leaves them out) | the review may run, but the verdict cannot be `approved` |
| Upstream items are approved | `hash --upstream` lists them; `show <ID>` gives the state of each | review the upstream item first, or in the same review; otherwise the verdict cannot be `approved` |

Coverage findings on a subject (for example `COV-07`, no component fulfils it yet) do
not stop a review. They are reported, and the reviewers decide whether they matter for
the verdict. Tell them that such a finding is a `warning` while the item is in review
and becomes an `error` once it is approved, until the missing link exists.
