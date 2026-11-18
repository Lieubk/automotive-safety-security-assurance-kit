# Tools

Deterministic commands that skills and agents call. Run them from the toolkit root.
`--project DIR` selects the project (default: the current directory; the worked
example is `examples/power-window`). They need Python 3 and PyYAML.

## Trace engine - `python tools/traceability.py [--project DIR] <command>`

| Command | Use it to | Output |
|---|---|---|
| `check` | find out what is wrong or missing | one line per finding: level, rule, item, message, base practices; a summary line. Exit code 1 when there are errors |
| `check --all` | also see gaps on items still in draft | as above, plus `info` lines |
| `check --json` | process findings in a script | JSON |
| `status` | see how many items of each type are in which state, and the latest runs | table |
| `show <ID>` | read one item's links in both directions | what it links to, what links to it |
| `impact <ID>` | see what a change to an item affects | every item that depends on it, by distance |
| `matrix` | produce the traceability tables for the link pairs in scope | Markdown tables |
| `hash [ID ...]` | get content hashes | `ID hash` per line |
| `hash --upstream ID ...` | prepare a review | `subject` and `references` blocks |

Finding levels: `error` (approved items, or always-wrong structure), `warning` (items
in review, or missing consistency evidence), `info` (drafts). Rule names: `FORMAT`,
`SCHEMA`, `LINK` (structure), `COV-01` to `COV-28` (coverage rules of
`schema/items.yaml`), `SUSPECT` (an upstream item changed after the review),
`CONSISTENCY` (a review did not record what the item was compared with).

Only the coverage rules of processes in `scope.processes` of `project.yaml` are
active. The summary line says how many.

## Records - `python tools/record.py [--project DIR] <command>`

| Command | Use it to |
|---|---|
| `next-id <type>` | get the next free ID before creating an item |
| `test-run --level L --results FILE --item-under-test REF --environment NAME` | turn a test result file into a final test-run record |
| `analysis-run --results FILE --item-under-test REF` | turn a static analysis result file into a final record, attributed to units |
| `review --checklist NAME --reviewer NAME --verdict approved\|rework [--findings FILE] ID ...` | record a review a person has given a verdict on; hashes and references are filled in |

Input file formats are in the tool's help (`python tools/record.py --help` and the
module text). Records are final when written and are never edited afterwards.

## Catalog and schema

| Command | Use it to |
|---|---|
| `python tools/catalog.py validate` | check the process catalog under `aspice/` |
| `python tools/schema_check.py` | check `schema/items.yaml` against the catalog; lists base practices that have no evidence structure yet |
| `python -m unittest discover -s tools/tests` | run the engine's regression tests |

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
