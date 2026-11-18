# From observations to verdicts

The engine observes; it does not judge. `python tools/traceability.py practices` prints
one state per base practice. This page fixes how a state becomes a verdict of the
working agreement (PASS, CONCERNS, FAIL, NOT ASSESSED), so that two runs on the same
project give the same result.

## What the columns mean

| Column | Content |
|---|---|
| `state` | the observation, see below |
| `evidence` | live items (not rejected, not obsolete) that back the practice: items of the types named for it, or, for a practice backed only by links and rules, the items that carry those links or that the rules check |
| `settled` | those of them that have passed the decision of their lifecycle: `approved` for engineering items, `final` for records, `approved` and later for change requests, `in-resolution` and later for problem reports |
| `errors`, `warnings` | findings of `check` whose bracket names the practice. A finding on an item is counted for the process that produces the item |

`practices <PROCESS> --json` adds `by`: the item types, link roles (`link <role>`) and
rules that back the practice.

The engine decides the state in this order: nothing in `by` -> `no evidence structure`;
any error -> `findings open`; no item -> `no evidence yet`; an item not settled ->
`evidence not settled`; any warning -> `warnings open`; otherwise `evidence present`.

## Three things the states do not tell

### Findings that count for no practice

A `check` line without a bracket is counted for no practice. Quote every such line
under "Facts".

- A finding on an imported item whose process is out of scope, for example
  `COV-19 SYR-0003 stale approval: content changed since review REV-0001`: the input is
  no longer covered by its acceptance review. If a gated process has items that link
  to the item named (`show <ID>`), its consistency practice is FAIL with the reason
  "input not accepted", whatever state the engine printed for it.
- `QUERY ... open query QRY-0003 is about this approved item`: a question to the source
  is unanswered. The practices of a gated process whose items link to that item are
  CONCERNS at most, with the query named; the user says whether the question blocks
  what the gate is for.
- `PROBLEM ... problem report PRB-0001 (major, open) concerns this approved item`: the
  consistency practice of the process that owns the item is CONCERNS at most, with the
  report named; FAIL when its severity is `critical`.

An input that was never accepted needs no such correction: every approved item derived
from it carries an `UPSTREAM` error, which the engine counts for the traceability and
consistency practices of the deriving process. That is `findings open`, FAIL.

### Open review findings on items that are not approved

`check --all` prints `COV-19 ... review REV-0007 left findings open: F1` on an item in
draft (as `info`) or in review (as `warning`). The item was reviewed, found wanting and
not corrected. `practices` shows the practices behind it as `evidence not settled`; an
`info` line is not even counted. Such an item makes the practice FAIL, see below.

### Communication records

Any final communication record counts for every practice about communicating or
summarizing that is in scope. `evidence present` on such a practice only says that some
record exists. Whether it concerns this process is found out in the sample.

## The mapping

| State | Verdict | Say |
|---|---|---|
| `findings open` | FAIL | the `check` lines of level `error` whose bracket names the practice, quoted |
| `no evidence yet` | FAIL | which item types or links would carry the evidence (`by`), that none exists, and which skill produces them |
| `evidence not settled` | CONCERNS or FAIL | see the next table |
| `warnings open` | CONCERNS | the `check` lines of level `warning`, quoted; who can accept them and with what reason |
| `no evidence structure` | NOT ASSESSED by the toolkit | that the schema holds nothing for the practice; then the user's statement about evidence outside the repository, marked as a statement |
| `evidence present` | PASS for the deterministic part | then the result of the sample; the practice verdict is the worse of the two |
| `not assessed` (the catalog has no such process) | NOT ASSESSED | that the process ID is not in `aspice/3.1/` |

### `evidence not settled`

Find the unsettled items with `python tools/traceability.py list --type <type>` for the
types named in `by`, or `list --status draft` and `list --status in-review`.

| What is unsettled | Verdict |
|---|---|
| An item whose last review left findings open (`COV-19 ... left findings open` in `check --all`) | FAIL: a known finding stands against it. Quote the line and name the record |
| Everything: `settled` is 0 | FAIL |
| An item in `draft` or `in-review` that belongs to what the gate is for: the release named (requirements carry `release`), the delivery, or a baseline whose purpose is not listed under `trace.internal_baselines` | FAIL |
| A record in state `open` | FAIL: an open record is not evidence |
| Only items outside what the gate is for - assigned to a later release, or stated by the user as work for a later delivery | CONCERNS, with the reason and who stated it |
| The gate is for the current state and at least one item is settled | CONCERNS, listing the unsettled items |
| Change requests or problem reports that have not reached their decision | CONCERNS, listing them; FAIL if the user states that one of them blocks what the gate is for |

### `warnings open`

| The warnings are | Verdict |
|---|---|
| Marked `(pending: the unit has no code yet)` (`COV-12`, `COV-28`, `COV-29`), or `COV-10 ... designed but not implemented` | Gate for a design-stage baseline or for the current state: CONCERNS at most, and the report names the units without code. Gate for a release candidate, a delivery or a release these units belong to: FAIL - what is to be delivered is neither implemented nor verified |
| `CONSISTENCY ... a review of the code against the design is not evidenced` | CONCERNS: the design is reviewed, the code is not. Name the units |
| Any other warning | CONCERNS |

A gate whose only warnings are pending ones still says that verification of those units
has not begun. It does not report them as verified, and it does not leave them out.

## The sample

`evidence present` says that items exist, are settled, and that no rule objects.
Whether the practice is carried out well needs reading.

### Choosing

At least three items or records per practice, or all if there are fewer. If the gate is
for a release, only items of that release. Take:

1. the item with the highest ASIL (lowest ID if several);
2. the item most others link to, from `matrix`;
3. the item with the highest ID, usually the newest;

and any item the user names. Say which rule chose which item. One sample of an item
type can serve several practices of a process; read each item once.

### What to read for

The yardstick is the row of the practice in `aspice/3.1/notes/<PROCESS>.md`: what it
says must be true, with its typical evidence as orientation.

| The practice is about | Read | Look for |
|---|---|---|
| specifying, designing, writing test cases (item types in `by`) | three items of the type | the part of the item that belongs to this practice. One type often backs several practices: for a software requirement, `Statement` for SWE.1.BP1, `kind`, `priority` and `release` for SWE.1.BP2, `Analysis` for SWE.1.BP3 and SWE.1.BP4, `Verification criteria` for SWE.1.BP5. An optional section that is absent everywhere is a concern for its practice |
| a strategy (`plan` in `by`) | the plan of the kind | every element the row of the practice names; the part for the kind in `.claude/docs/checklists/plan.md` can serve as a lens |
| traceability (only link roles and rules in `by`) | three links from `matrix`, both ends | whether the downstream item really states, implements or verifies what the upstream item says |
| consistency (`COV-19` in `by`) | the newest approving review records of three items of the process (Grep the item ID under `records/reviews/`) | reviewers are people; `checklist_source` is `toolkit` and the checklist is named with its version, or the external criteria are named so that a reader can find them; `checks` holds a result for every check, and every `not-applicable` has a reason that holds; `references` lists the upstream items with hashes; for a unit with code, `sources` and `item_under_test` are there and the checklist is the one for code; no finding is open |
| writing the code (SWE.3.BP8) | three units with their source files | what `COV-22` cannot compare: that the code does what `Behavior` and `Error handling` describe |
| performing verification (run records in `by`) | the latest final run of the level | `item_under_test` names a commit, tag or baseline; every test case has a verdict; coverage or the reason it was not measured, deviations with the reason a person accepted; the evidence files exist |
| communicating or summarizing (`communication-record` in `by`) | the communication records | the subject is a baseline or a set that contains this process's items at their present hashes; the audience covers the parties the row names; for results, a reader can judge the consequences |

### Result of the sample

| Reading shows | Result | Practice verdict |
|---|---|---|
| nothing that contradicts the row | "no concern in N of M" | PASS |
| something a careful reader would question | a proposed concern, with the quoted text | CONCERNS; the user confirms or rejects it. A concern the user confirms as missing mandatory content is reported as FAIL, "confirmed by <who>" |
| a review record whose `reviewers` names no person - a placeholder, a tool, a model | quoted | FAIL for the consistency practice: the record is not an accountable review |
| a review record without `checks` (possible only with `checklist_source: external`) | quoted | CONCERNS for the consistency practice: the record does not say which checks were applied; the user says where the external criteria and their results are kept |
| a communication record that does not concern this process | quoted | FAIL for the practice: no evidence for it exists |
| the notes or the items cannot be read | the reason | NOT ASSESSED |

The power window example shows the third row. `practices SWE.4` prints SWE.4.BP6 as
`evidence present`. The record that approves the unit test cases, REV-0006, says
`reviewers: Demonstration data - no review by a person took place`. The verdict for
SWE.4.BP6 is FAIL.

## Verdict per process

Order from worst to best: FAIL, NOT ASSESSED, CONCERNS, PASS. The process verdict is
the worst among its practices.

- NOT ASSESSED ranks above CONCERNS and PASS because nothing was established for that
  practice; it ranks below FAIL because a known problem tells more than an unknown one.
- Always print the count per verdict with the process verdict: "SUP.8: FAIL (1 PASS,
  0 CONCERNS, 2 FAIL, 6 NOT ASSESSED)".
- A process with only PASS is reported as "PASS for what the toolkit can check, by
  sample", never as "fulfilled" or "achieved".
- Across several processes there is no overall verdict. Report them side by side.
