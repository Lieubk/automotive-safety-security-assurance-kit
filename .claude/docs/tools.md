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
| `status` | see how many items of each type are in which state, the latest runs, and the latest build of each integration step | table |
| `list [--type T] [--status S] [--imported]` | get the IDs of items by type and state, or of the imported inputs | `ID state type title` per line |
| `show <ID>` | read one item's links in both directions | what it links to, what links to it; for a component also the interfaces it provides and uses |
| `impact <ID>` | see what a change to an item affects | every item that depends on it, by distance |
| `audit <BL-ID>` | compare a baseline record with the items as they are now | one line per difference; exit code 1 when there are any |
| `progress [--as-of DATE] [--json]` | compare the plan with what the items show: per work package its state read from the items it delivers, lateness, effort against estimate; milestones against baselines; open corrective actions | a tree of work packages, milestones, corrective actions, a summary line |
| `problems [--as-of DATE] [--json]` | see every problem report with state, severity, origin, detection, age and the change requests that resolve it, and counts by severity, origin, detection and age | a list and a summary line |
| `quality [--as-of DATE] [--json]` | see the checks of the quality assurance plan with their last record, every finding with the state of its action, how far it is overdue and the escalation due by the plan, and whether the reports were communicated | lists and a summary line |
| `history <ID>` | see the states an item had, from the commits that changed its file | date, commit, state per change; NOT ASSESSED with exit code 2 when git cannot be read |
| `diff <ID> [--since REV-ID]` | see what changed in an item since a review saw it, as subject or as reference (an upstream item since the review of what builds on it); the reviewed text is taken from the git history by its content hash | a unified diff; "unchanged"; or NOT ASSESSED with exit code 2 when the reviewed text is in no commit |
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
`SCHEMA`, `LINK` (structure), `COV-01` to `COV-45` (coverage rules of
`schema/items.yaml`), `SUSPECT` (an upstream item, or the code of a unit, changed after
the review), `CONSISTENCY` (a review did not record what the item was compared with, or
did not record the code of a unit), `UPSTREAM` (approved above something that is not),
`QUERY` (an open query is about an approved item), `PROBLEM` (an unresolved problem
report affects an approved item).

Only the coverage rules of processes in `scope.processes` of `project.yaml` are
active. The summary line says how many.

## Records - `python tools/record.py [--project DIR] <command>`

| Command | Use it to |
|---|---|
| `next-id <type>` | get the next free ID before creating an item |
| `test-run --level L --results FILE --item-under-test REF --environment NAME [--deviation UNIT=TEXT] [--build BLD-ID] [--selection TEXT] [--executed-at TIME]` | turn a test result file - JSON from a runner, or the JUnit XML report of a test bench - into a final test-run record, with coverage per unit and a hash of every source and test file. `--deviation` records why a person accepted a coverage figure below target. `--build` names the build record of the integrated software tested: needed for level software-integration (then the cases of the build's step must appear, earlier steps' may, later steps' may not) and, once an approved software-integration plan exists, for software-qualification (a build of the last step). `--selection` says how the cases were chosen |
| `build --step NAME --manifest FILE --item-under-test REF` | turn the manifest a build of one integration step wrote into a final build record: the units built per component, components integrated as received with their version, the doubles, and a hash of every file built. Refused without an approved software-integration plan that has the step, and for a built file that belongs to no unit |
| `analysis-run --results FILE --item-under-test REF` | turn a static analysis result file into a final record, attributed to units; justified deviations in the file are recorded as such, not as open findings |
| `review --checklist "NAME vN" --reviewer NAME --verdict approved\|rework [--findings FILE] [--checks FILE] [--item-under-test REF] [--external-criteria] ID ...` | record a review a person has given a verdict on; the checklist is cited as the file name under `.claude/docs/checklists` (or its title) and its version, and must exist unless `--external-criteria` is given; hashes and references are filled in. With `--item-under-test` it is a review of the code as well: the hashes of the units' source files are stored; without it the record covers the design only. `--checks` stores the result per checklist item (`pass`, `finding`, `not-applicable` with a note, `not-assessed`). Verdict approved is refused while a finding is open, while a check of the checklist has no result or is not assessed, while an accountable check is answered with a finding, while an item the subject builds on is not approved, or while an open finding of an earlier review of the same content is not closed by an entry with `closes` |
| `review --reconfirm --reviewer NAME --verdict approved\|rework [--findings FILE] ID ...` | record that items which did not change were compared with new versions of what they build on. No checklist and no check results; refused for an item whose present content has no approving review. The new versions are recorded as references. The code review of a unit is carried over as it was recorded, so code that changed since stays `SUSPECT`; it cannot be combined with `--item-under-test` |
| `baseline --tag TAG --purpose TEXT` | write a baseline record: the approved plans and engineering items with hash and status (an internal purpose: all of them). Refused while the trace check reports errors, unless the purpose is an internal one |
| `status-report --reported-by NAME --assessment FILE [--as-of DATE] [--period TEXT]` | write a project status report: the figures of `progress` and `check` for the date, and the reporter's assessment from the file, in their words. Refused without an assessment |
| `quality-check --kind work-product\|process [--check NAME] --subject ID ... --criteria TEXT --checked-by NAME --result R --summary FILE [--findings FILE] [--checked-at DATE]` | record a check by quality assurance: the facts at the time (per item state, hash, approving review; per process the evidence per base practice) and the checker's result, summary and findings. Refused without an approved quality-assurance plan, for a finding whose action does not exist, and for a result that does not agree with the findings |
| `quality-report --checked-by NAME --result R --summary FILE [--as-of DATE] [--period TEXT]` | record the periodic report of quality assurance: the quality records since the last report, the figures and findings of `quality`, and the reading of the person in the role. It raises no findings of its own |
| `self-assessment --ratings FILE --assessor NAME [--process ID ...] --summary FILE [--as-of DATE] [--check-only]` | record the ratings N, P, L, F that named people gave per base practice in a mock assessment, with the observations of `practices` at the time and the consistency flags: a rating outside the band of the observation, a rating above that of a practice it depends on in the catalog. A flag from an observation or a rule needs the reason in the rating's note. `--check-only` lists gaps and flags and writes nothing. The toolkit rates nothing |
| `problem-trends --reported-by NAME --assessment FILE [--as-of DATE] [--period TEXT]` | write a problem trend report: the list and figures of `problems` for the date, and the analyst's assessment from the file, in their words. Refused without an assessment |
| `communication --subject ID --audience WHO --channel TEXT [--agreement TEXT] [--sent-at DATE] [--practice BP]` | record what was made known to whom, and what was agreed; `--subject`, `--audience` and `--practice` may repeat. `--practice` names the communicate practices the record serves; `practices` counts it for those only |

Input file formats are in the tool's help (`python tools/record.py --help` and the
module text). Records are final when written and are never edited afterwards.

## Things that follow from how the tools work

- The newest final review record of an item's current content decides. A re-review
  that records the upstream versions clears `SUSPECT` and `CONSISTENCY`; for an item
  that did not change itself that is `review --reconfirm`.
- An item builds on the items it links to. A component also builds on every interface
  that names it under `provided_by` or `used_by`: a changed interface makes these
  components suspect, and an interface in draft or in review makes an approved component
  it names report `UPSTREAM`. The messages call the two relations `provider of` and
  `user of`.
- An accountable check answered with a finding blocks approval for good: what a person
  states is missing is not closed by a reviewer's decision. The agreement of those who
  build on approved items is recorded after the approval, as a communication record.
- An allocation is stated on the architectural element: it `fulfils` the requirement.
  The requirement itself is not touched, so allocating does not change requirements that
  are already approved, and a requirement that changes makes the element suspect.
- An approved item whose upstream item is still in draft or in review is reported as
  `UPSTREAM`; `record.py review` refuses to approve it. Approve from the top down.
- A question to the source of an input is a `query` item with an `about` link. While it is
  open, `QUERY` warns on every approved item it is about, and says so when the question
  has no `asked_at` yet, that is, it has not been put to its source.
- A problem found in an item of the project outside a review of it is a
  `problem-report` with an `affects` link (`/problem-resolution`); `PROBLEM` warns on the approved item until the
  report is resolved. `record.py review` refuses a finding on an item that is not a
  subject.
- A requirement that uses what another requirement of its level defines links to it
  with `relies_on`; a change of that requirement then makes it suspect.
- While an item is in draft or in review, what builds on it is reported as `UPSTREAM`
  only; once it is approved again, as `SUSPECT` until the comparison is recorded.
- Work packages plan; their links to the items they deliver, and the owner's `progress`,
  track. Tracking is left out of the content hash, and links that plan or track work
  (`delivers`, `depends_on`, `part_of` between packages, `addresses`) are not compared
  in reviews: they raise no `SUSPECT`, `UPSTREAM` or `CONSISTENCY`. A package is done
  when its owner states it and every item it delivers is settled; `progress` reports a
  stated completion that the items contradict.
- `progress` depends on the date it is given; `check` does not. Lateness is never a
  `check` finding.
- A re-review reads what changed: `diff <ID> --since <REV-ID>` finds the reviewed text
  in the git history. Commit items and records after each review, or it cannot.
- A draft or in-review item whose last review left findings open shows them under `COV-19`
  in `check --all`.
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
