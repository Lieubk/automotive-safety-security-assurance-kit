# The change request from need to closure

## When a change request is needed

An item is "in a baseline" when a final baseline record whose purpose is not internal
lists it with the content hash it has now. To find out: Grep the item ID in
`records/baselines/`, then run `python tools/traceability.py audit <baseline ID>` for a
record that lists it. If the output has no `content changed` line for the item, it is
in that baseline. Baselines with an internal purpose (`trace.internal_baselines` in
`project.yaml`) list everything and protect nothing.

| Situation | Change request? | Why |
|---|---|---|
| An item that is in a baseline is to change in content | yes | working agreement, section 5; the write hook refuses the edit otherwise |
| A new version of an imported input arrives, and the registered version or items derived from it are in a baseline | yes | the request names the input and every project item that has to follow; `/import-inputs` compares the versions and sends the user here before it registers anything |
| A problem report needs a change to items that are in a baseline | yes, with `resolves` | the problem report says what is wrong, the change request what is changed |
| The answer to a query calls for a change to items that are in a baseline | yes, with the query under `affects` | the query holds question and answer, the change request what follows from it; the query is closed when the items are in line with the answer |
| An item that is in a baseline is retired (`obsolete`, `rejected`) | yes | the write hook refuses it otherwise |
| The item is in no baseline: a draft, an item in review, an approved item never baselined, an item listed by an internal baseline only | no | it changes with its authoring skill; its approval becomes stale and `/review` renews it |
| The item was changed after its last baseline and is not baselined again | no | its present content is listed nowhere; the next baseline will list it |
| Only `status` changes, other than to `obsolete` or `rejected` | no | the status is not part of the content hash |
| Code is written for a baselined unit design and its files are registered under `source_files` | no | `source_files` is not part of the content hash: the design is unchanged and stays approved |
| A new item is added and no baselined item has to change with it | no | but a link written on a baselined item (for example `fulfils` on a component) is a change of that item |
| A review record, run record, baseline or communication record is wrong | never | records are final; a new record supersedes |

With SUP.10 in scope the plan of kind `change-request-management` may ask for a change
request in more cases than this table, for example for every approved item. Then the
plan decides. A request that only adds items still names what exists and has to follow:
the input it comes from, the items the new ones will link to, a plan whose content
changes. New items are added to `affects` when they exist.

## Full and reduced mode

| | SUP.10 in scope | SUP.10 not in scope |
|---|---|---|
| Plan of kind `change-request-management` | needed (COV-27) | not demanded; the configuration management plan says who decides |
| `COV-20` (affects link from `analysed` on) | checked by the trace check | not active: check with `show <CR-ID>` |
| `decision` from `approved` or `rejected` on | checked by the trace check (`SCHEMA`) | the same: a schema condition does not depend on the scope |
| `python tools/traceability.py practices SUP.10` | prints the practice table | prints that SUP.10 is not in the scope |
| States, impact analysis, decision, verification, closing | as below | as below: the write hook and the change control rule of the plan do not depend on the scope |
| What the hand-over claims | evidence prepared for SUP.10 | change control for the baseline only (SUP.8.BP5 where SUP.8 is in scope); no claim for SUP.10 |

In the reduced mode say at the start and in the hand-over that the work is reduced and
why. Do not leave out the analysis or the decision: they protect the baseline, not the
rating.

## States

The states are those of the `change-request` lifecycle in `schema/items.yaml`. The trace
check knows the states and what an item must carry in each, but it does not test
whether a step from one state to the next was allowed, and the item keeps no history.
This skill therefore changes the state only when the condition is shown, and says by
which command.

| Step | Condition | Shown by | Ask the user | Write |
|---|---|---|---|---|
| new -> `submitted` | requester, request and reason are known | the user's statement | who, what, why, source | the item with `requester` and `Description` |
| `submitted` -> `analysed` | `Impact analysis` is written and `affects` names every item that changes | `show <CR-ID>`; `check` without `SCHEMA` or `COV-20` on the request | whether the analysis is ready to be decided | `Impact analysis`, `links.affects`, status |
| `analysed` -> `approved` | the deciding body has decided for the change | the user's statement | who decided, when, priority, release, conditions | `decision`, status |
| `analysed` -> `rejected` | the deciding body has decided against it | the user's statement | who decided, when, the reason | `decision`, `rejection_reason`, status |
| `approved` -> `implemented` | every item under `affects` is `approved` or `obsolete`, a query among them `closed`; no `COV-19`, `UPSTREAM`, `SUSPECT` or `CONSISTENCY` finding on an item of the analysis | `show <CR-ID>`, `list --status draft`, `check` | - | status |
| `implemented` -> `verified` | the affected tests ran on the changed state; a final review record with verdict approved has the change request as subject | `check` without `COV-30` on the changed units and their test cases; `status` (latest run); Grep the change request ID in `records/reviews/` | reviewers and verdict | the review record, by tool; status |
| `verified` -> `closed` | the review record of the implementation exists with verdict approved; the requester is informed of the result and of the baseline or release that holds the change | Grep the change request ID in `records/reviews/`; the user's statement | by whom, how, when | communication record, by tool; status |

A request that is put off stays `analysed`. Note in `decision` who put it off and until
when; it is decided again later.

Related requests: when two open requests affect the same item, say so in both
(`Impact analysis`, under dependencies) and tell the user which one has to be
implemented first. `python tools/traceability.py impact <ID>` lists the change requests
that affect an item; `python tools/traceability.py list --type change-request` lists
all of them with their states.

## Summary for the deciding body

Give the user this, filled from the item, on one page:

```
CR-0001  Protected zone from 4 mm window opening          state: analysed
Requested by: customer system engineering, front door module    Wanted for: R1.1
What and why: <two sentences from Description>
Items that change: 5 (1 imported input, 1 software requirement, 1 component design,
  1 software unit, 1 unit test case); highest ASIL among them: B
Code and tests: <files>
Reviewed again without change: <count>     Regression: <scope>
Effort: <as stated>   Schedule: <as stated>   Risk: <as stated>
Depends on: <other change requests, open questions to the requester>
Confirmation criteria: <the list>
To decide: approve, reject, put off, or approve a part; priority; target release
```

Who decides is written in the plan (`Responsibilities`); the names may be in
`project.yaml`. Record the decision in `decision` as one text, in the user's words:
who, when, result, priority, target release, conditions. Example:

```yaml
decision: "Change Control Board (project lead, software architect, safety manager), 2026-11-19: approved for release R1.1, priority high; SWR-0008 stays unchanged until the customer has answered question 1"
```

From `approved` or `rejected` on, the trace check reports a `SCHEMA` error on a change
request without `decision`. It cannot tell whether the text is true: write only what
the user states. Do not judge whether the people named were entitled to decide; if the
plan names another body, say so and ask.

## Order of implementation and owning skills

Work from the top of the V downwards, and have each level reviewed before the next one
is changed. A review records the upstream items at their present hash; reviewing a
design before its changed requirement is approved produces a suspect link at once.

| Affected item | Changed with | Then |
|---|---|---|
| imported input | `/import-inputs` registers the new version with its new `imported.version`; nobody edits the content by hand | input acceptance review through `/review` |
| `software-requirement` | `/sw-requirements` | `/review` |
| `software-component`, `software-interface`, `architecture-view`, `design-decision`, and the allocation (`fulfils`) | `/sw-architecture` | `/review` |
| `component-design`, `software-unit` | `/sw-detailed-design` | `/review` |
| code of a unit | `/sw-unit-implement` | `/review` of the code, with the unit as subject and the code revision: only a review recorded with `--item-under-test` counts as a review of the code |
| `unit-test`, test code, new runs | `/sw-unit-verify` | `/review` for the test cases |
| `plan` | the skill of its process: `/sw-unit-verify` for the unit verification strategy, `/baseline` for the configuration management plan, this skill for its own plan | `/review` |
| a type without an authoring skill | the person responsible edits it by the schema; say that no skill exists | `/review` |

After every step run `python tools/traceability.py check`:

- `COV-19` names a changed item that still waits for its review.
- `UPSTREAM` names an approved item that rests on an item now in draft or in review.
  It disappears when the upper item is approved again. `python tools/record.py review`
  refuses to approve an item while something above it is not approved: this is what
  makes the order from the top down more than a recommendation.
- `SUSPECT` names an item that links to something changed, or a unit whose code changed
  after its code review. It is reviewed against the new version whether its own text
  changes or not; the newest review of its present content clears the finding.
- `CONSISTENCY` on a unit with code says that its newest approving review names no code
  revision: the design was reviewed, the code was not.
- `COV-30` names a unit or test case whose source or test file changed after the latest
  test run or analysis run: the runs are repeated with `/sw-unit-verify`.

An item created by the change (a new test case, a new requirement) is added to
`affects` when it exists, provided the analysis announced it. An existing item that the
analysis did not name is a widening of the request: stop and go back to the user.

## The write hook

Inside a session a hook checks every Write and Edit of an item file:

- It refuses a change to the content of a plan or engineering item that is in a
  baseline, and its retiring (`obsolete`, `rejected`), unless a change request in state
  `approved` or `implemented` names the item under `affects`. Name the item by its
  plain ID there, without `#` and a function name.
- It lets other changes of `status` pass, and the registering of `source_files` on a
  unit.
- It refuses changes to final records. An imported input that has been accepted
  changes only together with a new `imported.version`, or in its disposition.
- It never stops an edit of a change request or a problem report: they are not part of
  any baseline.
- It does not see code, and it does not see edits made outside a session. Those show up
  afterwards in the trace check, as `COV-19`, `SUSPECT` or `COV-30`.

When the hook refuses an edit, do not work around it. Either the change request is not
yet `approved`, or it does not name the item: say which, and go back to the analysis
or to the decision.

## Review of the implementation

Before `verified`, the implementation is reviewed against part B of
`.claude/docs/checklists/change-request.md`. `/review` takes engineering items, plans
and imported inputs, not change requests, so this review is prepared and recorded here.
The rules are those of `/review`: people give the verdict, the tool writes the record.

1. Script checks: answer them from `check`, `status` and `show <CR-ID>`; quote the
   output. The tool will refuse verdict approved while an item under `affects` is not
   approved.
2. Semantic checks: run `python tools/traceability.py hash --upstream <CR-ID>` and hand
   the agent `aspice-reviewer` the change request ID, the path of the checklist and
   that output, nothing else. It applies the semantic checks of both parts and returns
   proposed findings. Agent definitions load when a session starts; if the agent is
   not available, apply the checks yourself, say "No independent pass took place",
   also in the hand-over, and tell the user that a new session makes it available.
3. Show script findings, proposed findings and checks that could not be applied. The
   user confirms, rejects or adds findings. Ask every accountable check as a question.
4. Ask who is accountable for the verdict and who implemented the change: at least one
   reviewer is someone else. A model or an agent is never a reviewer. Ask for the
   verdict, `approved` or `rework`; do not propose one.
5. Write the result of every check of the checklist, part A and part B, as JSON to a
   file outside the item folders, for example `build/cr-review-checks.json`: a list of
   entries with `check`, `result` and `note`. Results are `pass`, `finding`,
   `not-applicable` (the note says why) and `not-assessed`. Part A is answered again
   on the present text. The tool refuses verdict approved when a check has no result
   or is `not-assessed`. Findings go into a second file in the format the help text of
   the tool gives.
6. Ask: "May I record this review of CR-nnnn: checklist change-request v2, reviewers
   <names>, verdict <verdict>, N findings?" Then run
   `python tools/record.py review --checklist "change-request v2" --reviewer "<name>" --verdict <verdict> --checks <file> --item-under-test <commit> <CR-ID>`,
   with `--findings <file>` when there are findings and one `--reviewer` per person.
   `<commit>` is the commit that holds the change. The checklist is cited by its file
   name and version, exactly as shown; the tool reads the check IDs from that file. It
   fills in the change request and every item it links to with their hashes: the
   record states which versions of the affected items were confirmed. When it refuses,
   go back to the user; do not change a result to get past it.
7. Verdict `approved`: ask to set `verified`. Verdict `rework`: the state stays
   `implemented`, the findings go to the owning skills, and a new review follows.

## Closing

- The requester is told the result: what was changed, in which release or baseline it
  is contained, what was not done. The user states that this happened; then the
  communication record is written, with `--sent-at` and the date as YYYY-MM-DD when
  that was on another day, and the state set to `closed`.
- A rejected request is also told to the requester. Record that in the same way.
- If the request resolves a problem report, name it in the hand-over: the change being
  closed is what the owner of the problem report needs to move it on.
- The changed items are in no baseline until the next one is taken with `/baseline`.

## Status history

The item holds its present state only. The history of states is the version control
history of the file. For it to exist, each change of state has to be committed on its
own, with a message such as "CR-0001 analysed". Propose that commit after every change
of state and make it only when the user asks. If the user does not want commits per
state, say in the hand-over that the status history will be incomplete.

`python tools/traceability.py list --type change-request` shows every change request
with its state. `practices SUP.10` counts a change request as settled from state
`approved` on; one that is `submitted` or `analysed` appears as `evidence not settled`.
The table shows the same row for every practice of a settled request. It cannot tell
whether the implementation was reviewed or the requester informed: say that yourself,
from the review record and the communication record.
