# What goes into one review

## Where candidates come from

| Source | How it shows | What the review has to do |
|---|---|---|
| New or reworked item | `list --status draft`, `list --status in-review` | full review against the checklist |
| Changed after approval | `COV-19 ... stale approval: content changed since review REV-0004` | full review of the present content; the earlier record tells what was approved before |
| Approved without a review | `COV-19 ... approved, but no final review record covers it` | full review; tell the user that the status claimed an approval nobody gave |
| Findings left open | `COV-19 ... review REV-0009 still has open findings` or `... findings of an earlier review of the same content are open` | the author corrects first; then a review that closes each finding with `closes` (`re-review.md`) |
| Upstream item changed | `SUSPECT ... suspect link: UNT-0002 (verifies) changed after review REV-0005` | compare the item with the new version of the upstream item (`re-review.md`) |
| Code changed after its review | `SUSPECT ... src/windowpos/WindowPos.c changed after review REV-0007: the code is no longer the code that was reviewed` | code review of the unit |
| Code never reviewed | `CONSISTENCY ... review REV-0004 does not record src/windowpos/WindowPos.c: a review of the code against the design is not evidenced` | code review of the unit |
| Comparison not recorded | `CONSISTENCY ... review REV-0004 does not record IFC-0002 (uses) as a reference` | compare the item with the item named and record a review that lists it |

Not candidates: records (they are final), items in state `rejected` or `obsolete`, and
drafts whose author says they are not finished. Change requests and problem reports are
not candidates either. The record tool takes any item ID, and a change request does
become the subject of a review record - the review of its implementation - but that
review is prepared and recorded by `/change-request` with its own checklist, and it
moves the change request to `verified`, never to an approval. Baselines are checked by
`/baseline`.

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
| Anything else of the `engineering` lifecycle | for example `system-requirement` written by the project, `software-integration-test` | whichever checklist names the type; if none does, the semantic part is NOT ASSESSED |

Cite a checklist as its title without the word "checklist", in lower case, followed by
`v` and the number of its version line: `software requirements review v1` for
`software-requirements.md`, `software unit code review v1` for `software-unit-code.md`.

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
| approved, has code; `SUSPECT ... suspect link` only | review against the changed upstream item, then review of the code |

The newest approving record of a unit decides. A design review or a comparison with a
changed upstream item, recorded without `--item-under-test`, becomes that record, and
`check` then prints the `CONSISTENCY` warning about the code again even if an earlier
record named it. So for a unit that has code the review of the code is the last one
recorded. In the last row of the table, when neither the unit nor the code changed and
`check` printed no line about the code beforehand, that review can be short: the
reviewers confirm the earlier one, and the checks carry its results as `recording.md`
describes.

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
5. Upstream first. A subject is compared with upstream items that are approved, or
   imported and accepted. If an upstream item is itself waiting, review it first, or
   tell the user that the comparison becomes suspect as soon as that item changes.
6. One delivery, one input acceptance review: all imported items with the same
   `imported.source` and `imported.version`.

Example for the power window project, software requirements just written:

| Review | Items | Checklist | Upstream items |
|---|---|---|---|
| 1 | SWR-0001, SWR-0002, SWR-0003 (position and speed) | software requirements review v1 | from `hash --upstream SWR-0001 SWR-0002 SWR-0003` |
| 2 | SWR-0004, SWR-0005, SWR-0006 (anti-pinch) | software requirements review v1 | from `hash --upstream SWR-0004 SWR-0005 SWR-0006` |
| 3 | SWR-0007, SWR-0008, SWR-0009 (command and motor) | software requirements review v1 | from `hash --upstream SWR-0007 SWR-0008 SWR-0009` |

The number in the last column is never estimated. For one requirement the command prints:

```
subject:
  - {item: SWR-0003, hash: 97d88c9d90a4}
references:
  - {item: CMP-0003, hash: fedf3d902a9b}
  - {item: SYI-0001, hash: fd6d4321eb97}
  - {item: SYR-0001, hash: 574d727eac01}
```

`references` holds every item the subject links to, whatever the link role, that is not
itself part of the subject. `record.py review` writes the same list into the record.
An allocation stated on the architecture side (`fulfils` on a component) is a link of
the component: the requirement then appears among the references of the component's
review, not the other way round.

## Ready for review

| Condition | How to tell | If not |
|---|---|---|
| No structural error | no `FORMAT`, `SCHEMA` or `LINK` line of level `error` on the item after it was set to `in-review` | back to `draft`, to the authoring skill |
| The author considers it finished | ask | leave it out |
| Mandatory content for approval is there | `check --all` prints no `still to come before approval` line for the item; `conditions` of the schema with that stage are met (read them: the preview leaves them out) | the review may run, but the verdict cannot be `approved` |
| Upstream items exist and are settled | `hash --upstream` lists them; `show <ID>` gives the state of each | review the upstream item first, or say that the result will not last |

Coverage findings on a subject (for example `COV-07`, not yet allocated) do not stop a
review. They are reported, and the reviewers decide whether they matter for the verdict.
Tell them that such a finding is a `warning` while the item is in review and becomes an
`error` once it is approved, until the missing link exists.
