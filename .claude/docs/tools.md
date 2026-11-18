# Tools

Deterministic commands that skills and agents call. Run them from the toolkit root.
`--project DIR` selects the project (default: the current directory; the worked
example is `examples/power-window`). They need Python 3 and PyYAML.

## Trace engine - `python tools/traceability.py [--project DIR] <command>`

| Command | Use it to | Output |
|---|---|---|
| `check` | find out what is wrong or missing | one line per finding: level, rule, item, message, base practices; a summary line. Exit code 1 when there are errors |
| `check --all` | also see gaps on items still in draft, and what each draft still needs for its next state | as above, plus `info` lines |
| `check --json` | process findings in a script | JSON |
| `status` | see how many items of each type are in which state, and the latest runs | table |
| `list [--type T] [--status S] [--imported]` | get the IDs of items by type and state, or of the imported inputs | `ID state type title` per line |
| `show <ID>` | read one item's links in both directions | what it links to, what links to it; for a component also the interfaces it uses |
| `impact <ID>` | see what a change to an item affects | every item that depends on it, by distance |
| `audit <BL-ID>` | compare a baseline record with the items as they are now | one line per difference; exit code 1 when there are any |
| `matrix` | produce the traceability tables for the link pairs in scope | Markdown tables |
| `hash [ID ...]` | get content hashes | `ID hash` per line |
| `hash --upstream ID ...` | prepare a review | `subject` and `references` blocks |
| `practices [PROCESS]` | see, per base practice, the evidence the project holds and the findings still open | table; `--json` for scripts |

`practices` reports one of these states per base practice. They are observations, not
ratings:

| State | Meaning |
|---|---|
| `evidence present` | items exist, all are approved or final, and no rule objects |
| `warnings open` | as above, but warnings concern this practice |
| `evidence not settled` | items exist, but not all are approved or final |
| `no evidence yet` | the schema has a place for the evidence, and nothing is there |
| `findings open` | errors concern this practice |
| `no evidence structure` | the schema has no item type, link or rule for this practice: the toolkit cannot tell, a person has to |

Finding levels: `error` (approved items, or always-wrong structure), `warning` (items
in review, or missing consistency evidence), `info` (drafts). Rule names: `FORMAT`,
`SCHEMA`, `LINK` (structure), `COV-01` to `COV-30` (coverage rules of
`schema/items.yaml`), `SUSPECT` (an upstream item, or the code of a unit, changed after
the review), `CONSISTENCY` (a review did not record what the item was compared with, or
did not record the code of a unit).

Only the coverage rules of processes in `scope.processes` of `project.yaml` are
active. The summary line says how many.

## Records - `python tools/record.py [--project DIR] <command>`

| Command | Use it to |
|---|---|
| `next-id <type>` | get the next free ID before creating an item |
| `test-run --level L --results FILE --item-under-test REF --environment NAME [--deviation UNIT=TEXT]` | turn a test result file into a final test-run record, with coverage per unit and a hash of every source and test file. `--deviation` records why a person accepted a coverage figure below target |
| `analysis-run --results FILE --item-under-test REF` | turn a static analysis result file into a final record, attributed to units; justified deviations in the file are recorded as such, not as open findings |
| `review --checklist NAME --reviewer NAME --verdict approved\|rework [--findings FILE] [--checks FILE] [--item-under-test REF] ID ...` | record a review a person has given a verdict on; hashes and references are filled in. With `--item-under-test` it is a review of the code as well: the hashes of the units' source files are stored; without it the record covers the design only. `--checks` stores the result per checklist item. Verdict approved is refused while a finding is open, while a check is not assessed, or while an open finding of an earlier review of the same content is not closed by an entry with `closes` |
| `baseline --tag TAG --purpose TEXT` | write a baseline record: the approved plans and engineering items with hash and status (an internal purpose: all of them). Refused while the trace check reports errors, unless the purpose is an internal one |
| `communication --subject ID --audience WHO --channel TEXT [--agreement TEXT] [--sent-at DATE]` | record what was made known to whom, and what was agreed; `--subject` and `--audience` may repeat |

Input file formats are in the tool's help (`python tools/record.py --help` and the
module text). Records are final when written and are never edited afterwards.

## Things that follow from how the tools work

- The newest final review record of an item's current content decides. A re-review
  that records the upstream versions clears `SUSPECT` and `CONSISTENCY`.
- An allocation may be stated on the requirement (`allocated_to`) or on the
  architectural element (`fulfils`). Architecture work uses `fulfils`, so that it does not
  change requirements that are already approved.
- A unit may be approved as a design before it has code; the check then reports it as
  not implemented, and its verification rules (`COV-12`, `COV-28`, `COV-29`) as pending:
  warnings, so a design baseline stays possible. Registering `source_files` afterwards
  does not change the unit's content hash, so the design approval stays valid and a
  baselined unit needs no change request for it. Once source files are listed, the design is compared with
  the code: functions both ways, and parameter and return types where the design states
  them.
- Test runs, analysis runs, and reviews recorded with `--item-under-test` store hashes of
  the code they covered. When the code changes afterwards, `COV-30` and `SUSPECT` say so.
  A unit with code whose newest approving review does not name the code revision gives a
  `CONSISTENCY` warning: the design was reviewed, the code was not.
- An imported item may be corrected until its acceptance review is recorded. After that
  it changes only with a new `imported.version`, or in its disposition (`status`,
  `superseded_by`, `rejection_reason`).
- Baselines with an internal purpose freeze nothing. Any other baseline protects the
  engineering items it lists: their content changes, and they are retired (`obsolete`,
  `rejected`), only with an approved change request that names them.
- `audit <BL-ID>` reports items whose content or status differs from the baseline record,
  items the record lists that no longer exist, and approved items the record does not
  list.

## Catalog and schema

| Command | Use it to |
|---|---|
| `python tools/catalog.py validate` | check the process catalog under `aspice/` |
| `python tools/schema_check.py` | check `schema/items.yaml` against the catalog; lists base practices that have no evidence structure yet |
| `python -m unittest discover -s tools/tests` | run the regression tests of the engine and the hooks |
| `python tools/skill_lint.py` | check skills, agents and checklists mechanically: shape, and that every identifier they mention exists |

## Where knowledge lives

| Need | Read |
|---|---|
| What a process expects, practice by practice | `aspice/3.1/notes/<PROCESS>.md` |
| Identifiers, outcomes, work products, rating dependencies | `aspice/3.1/processes/<PROCESS>.yaml` |
| Traceability and consistency, key concepts | `aspice/3.1/notes/key-concepts.md` |
| Capability levels and generic practices | `aspice/3.1/notes/capability-levels.md` |
| Item types, attributes, links, coverage rules | `schema/items.yaml` |
| File layout of an item, content hash | `schema/item-format.md` |
| A complete worked example | `examples/power-window/` |
