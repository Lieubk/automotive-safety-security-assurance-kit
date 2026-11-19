# Working agreement

Rules every skill and agent of this toolkit follows. They exist because the product
of an Automotive SPICE project is not only software but evidence, and evidence is
only worth something if it is true.

## 1. People decide and are accountable; the toolkit drafts and checks

- A skill works in the order **question -> options -> decision -> draft -> approval**.
  It shows what it intends to write and asks before writing engineering items.
- Approval of a work product is given by a named person in a review record. An agent
  may prepare the review - read the items, apply the checklist, list findings - but
  it never records a verdict in its own name and never invents a reviewer.
- Agreement with a customer or another party is recorded only when the user states
  that it happened, with who and when.
- No commit, tag or baseline without the user asking for it in this project.

## 2. Facts come from tools, judgement from people and models

Three kinds of statement are kept apart and labelled:

| Kind | Source | Example |
|---|---|---|
| Deterministic | `tools/traceability.py`, compilers, test runners, analysers | "no component fulfils SWR-0007" |
| Semantic | a model reading the items, always shown with the text it is based on | "SWR-0007 states two needs in one sentence" |
| Accountable | a named person | "approved", "agreed with the customer" |

- A skill never states a coverage figure, a test result or a link status from memory.
  It runs the tool and quotes the output.
- A semantic finding is a proposal. It becomes a review finding when a person
  confirms it.
- Evidence records are written by tooling from tool output (`tools/record.py`),
  not typed in. A test result nobody ran does not exist.

## 3. Verdict vocabulary

Every check that others rely on reports one of:

| Verdict | Meaning |
|---|---|
| `PASS` | everything that had to be checked was checked, and nothing was found |
| `CONCERNS` | checked; findings exist that a person may accept with a reason |
| `FAIL` | checked; a rule is violated or mandatory evidence is missing |
| `NOT ASSESSED` | it could not be checked - a tool did not run, an input is missing, the process is out of scope. The report names which |

`NOT ASSESSED` outranks `PASS` (nothing was established) and does not outrank `FAIL`
(a known problem is more useful than an unknown). A step that was skipped says so in
the output by name. A check that cannot report that it did not run is not a check.

## 4. Scope

- `project.yaml` names the processes the project is responsible for. A skill whose
  process is not in scope says so and stops; it does not quietly do the work anyway.
- What comes from outside the scope is an **imported input**: registered as received,
  never edited, and accepted through an input acceptance review. Questions about it
  go back to whoever delivered it, as a recorded query.
- The rules of a process apply only to the items that process produces.

## 5. Change

- An approved item that changes is no longer approved. Nobody restores the status by
  hand; a new review does.
- An item inside a final baseline changes only through an approved change request
  that names it.
- When an item changes, the items that depend on it are suspect until they have been
  reviewed against the new version. `tools/traceability.py impact <ID>` lists them.

## 6. Writing items

- One item per file, in the folder and format of `schema/item-format.md`.
- A requirement states one need, can be verified, and says what, not how.
- A section that does not apply is written as `Not applicable:` with the reason.
- Where a skill or an agent applies a checklist of the toolkit, it looks under
  `checklists/` of the project as well: a checklist there that says `Extends:` it is
  applied with it, one that says `Replaces:` it instead of it
  (`python tools/record.py checklists --type <type>` names them).
- Names of people, customers and products of real projects stay out of anything that
  could be published.

## 7. What the toolkit does not do

- It does not rate capability levels. It prepares evidence and shows gaps; an
  assessment rates.
- It does not replace qualified tools. Where a project needs a qualified compiler,
  test tool or analyser, the toolkit drives it and records what it reported.
- It does not reach hardware. Tests on a target or a test bench are specified,
  traced and recorded here; they are executed there.
