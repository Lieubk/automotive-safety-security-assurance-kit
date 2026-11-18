# Creating, anchoring and auditing a baseline

## What a baseline is in this toolkit

A baseline is a tag in version control plus a baseline record, both for the same commit.

- The record (`records/baselines/<ID>.md`, type `baseline`) is written by
  `python tools/record.py baseline`. Its `items` list holds the approved plans and
  engineering items, imported inputs included, each as `{item, hash, status}`. Items
  that are not approved are left out. An approved item that links to one still in
  draft or in review is an `UPSTREAM` error of the trace check, and the tool refuses
  while errors exist: what gets in is approved all the way up. With an internal
  purpose the list holds every plan and engineering item, whatever its state.
- Never listed: change requests, problem reports, records (reviews, runs, earlier
  baselines, communication records), and files that are not items (code, test code,
  scripts). They are frozen by the tagged commit. This is why the tag belongs to the
  baseline and why the working tree has to be clean when the record is created.

What follows for the user, to be said before a baseline is created:

1. Every baseline record is final when written.
2. A baseline whose purpose is not internal protects the items it lists. Inside a
   session the write hook refuses a change to the content of a listed item as long as
   the item still has the listed content, and refuses retiring it (`obsolete`,
   `rejected`), unless a change request in state `approved` or `implemented` names it.
   Other changes of `status` are not refused, and neither is registering
   `source_files` on a unit: that is not part of its content hash.
3. A baseline with an internal purpose, such as `working`, protects nothing. It is a
   snapshot for reference.
4. Change requests are never listed, so an open one stays editable. Known open points
   of a baseline are therefore named in its communication, not in the record.

## Purposes

The plan of kind `configuration-management` defines the purposes, when each is due and
how its tag is formed. The table shows the purposes of the power window example with
the practice each communication serves. The plan of the project decides, not this table.

| Purpose | Due when | Tag | The communication afterwards serves |
|---|---|---|---|
| working | whenever a reference point is wanted | `work-<date>` | nothing: internal, no communication record |
| requirements freeze | all software requirements are approved | `req-<n>` | SWE.1.BP8 |
| design freeze | architecture and detailed design are approved | `design-<n>` | SWE.2.BP9, SWE.3.BP7 |
| release candidate | unit verification is complete for the release content | `rc-<release>-<n>` | SWE.4.BP7 |
| delivery | the release is handed to the customer | `rel-<release>` | all of the above, towards the customer |

To see what is due, read `python tools/traceability.py status`: the line of a type
shows how many items are in which state. "All software requirements approved" is the
line `software-requirement  9 approved` with no other state on it.

Pass the purpose to the tool exactly as the plan writes it. A purpose is internal only
if it equals an entry of `trace.internal_baselines` in `project.yaml`.

## Preconditions

Run every check and quote the output. Each one ends in `PASS`, `FAIL` or `NOT ASSESSED`.
For an internal purpose only checks 6 to 8 apply.

| No. | Check | Command | Passes when | If it does not |
|---|---|---|---|---|
| 1 | The plan is approved | `python tools/traceability.py check` | no `COV-27` line names kind configuration-management | write or review the plan first |
| 2 | The trace check has no error | the same output | the summary line shows `0 errors` | each finding names an item: its authoring skill, then `/review`. For `UPSTREAM`: the item above is reviewed first |
| 3 | What the purpose freezes is approved | `python tools/traceability.py list --status draft` and `list --status in-review` | none of the items printed belongs to what the plan demands for this purpose | finish and review them; or the user accepts, where the plan allows it, that they are left out of the baseline |
| 4 | No change request is open on what will be listed | `python tools/traceability.py list --type change-request` | every line shows `closed` or `rejected` | read the open ones by ID; the plan says who may accept one as a known open point |
| 5 | Earlier baselines are communicated | the `check` output | no `COV-26` line | step 7 of the skill for the baseline named |
| 6 | The branch is the one the plan names | `git status --short --branch` | the first line is `## <branch>`, possibly followed by `...<remote branch>` | the user switches or merges; the skill does not |
| 7 | The working tree is clean | the same output | no line after the first: nothing modified, staged or untracked | the user commits or removes what is listed |
| 8 | The tag is free | `git tag --list <tag>` and Grep `^tag: <tag>$` in `records/baselines/` | both find nothing | next number of the tag pattern |
| 9 | Verification belongs to this state (release candidate, delivery) | the `check` output; `status` prints `latest unit test run <ID> on <ref>` | no `COV-30` line: unit sources and test files are unchanged since the latest test run and analysis run | `/sw-unit-verify` repeats the runs on the present state |

Notes:

- Checks 1, 2 and 5 are errors of the trace check, and only those does the tool enforce.
  The other checks are the skill's: the tool does not look at the working tree, the
  branch, the tag, open change requests or the spelling of the purpose.
- Check 3: the tool leaves unapproved items out and says how many. Whether the baseline
  still means what its purpose says is a question for the plan and the user: a
  requirements freeze without two of the requirements is not what its readers expect.
- A design freeze does not wait for code. For a unit without code the check reports
  `COV-10`, `COV-12`, `COV-28` and `COV-29` as warnings; they do not stop the tool.
  Name them in the baseline notice as work still to come.
- Check 9: a `COV-30` finding on a unit or test case is an error and already fails
  check 2. A `COV-30` warning on a run means the run recorded no source hashes, so the
  trace check cannot tell: `NOT ASSESSED`, until `/sw-unit-verify` has repeated the run.
- A check that fails is never worked around by choosing an internal purpose.

## Creating the record

```
python tools/record.py baseline --tag req-1 --purpose "requirements freeze"
```

On success the tool prints, for example:

```
wrote records/baselines/BL-0001.md: 65 items, purpose requirements freeze, tag req-1 (set the tag after committing the record)
not in the baseline: 1 items that are not approved (python tools/traceability.py list --status draft)
```

The second line appears only when items were left out. Quote it, and name the items.
The tool assigns the ID, sets `status: final` and `created_at`, and fills `items`.

When the trace check reports errors and the purpose is not internal, it refuses:

```
the trace check reports 1 errors; a baseline with purpose 'design freeze' needs none
  COV-26 BL-0001 no final communication record names this baseline
no record written
```

It lists up to ten of the errors. Run `python tools/traceability.py check` for all of
them. Quote the refusal to the user and stop; the findings say what has to happen first.

## Commit and tag

The record is committed alone, and the tag is set on that commit. Show these commands
with the real values, and run them only on an explicit yes, or let the user run them:

```
git add records/baselines/BL-0001.md
git commit -m "Baseline BL-0001: requirements freeze (tag req-1)"
git tag -a req-1 -m "BL-0001 requirements freeze"
```

- An annotated tag (`-a`) carries who set it and when. Use the form the plan asks for.
- After the commands: `git status --short --branch` shows a clean tree, and
  `git log -1 --format=%H req-1` prints the same commit as `git log -1 --format=%H`.
- Others can use the baseline only after commit and tag are pushed. That is the user's
  step. A baseline whose tag exists only locally is an open point of the hand-over.
- A tag that has been made known is never moved or deleted. If a baseline turns out to
  be wrong, the next baseline of the same purpose supersedes it, and its communication
  record says so.

## Audit

The audit answers one question: does the tag contain what the record lists?
`python tools/traceability.py audit <baseline ID>` compares the record with the items of
the project folder it runs on, so it has to run on the content of the tag. The plan
says before which baselines an audit is due; the example plan demands it before a
delivery.

1. Read the record by ID and note its `tag`. Run `git tag --list <tag>`; no output
   means the tag does not exist: `FAIL`.
2. Get the content at the tag.
   - If `git log -1 --format=%H <tag>` and `git log -1 --format=%H` print the same commit
     and `git status --short --branch` shows a clean tree, the working tree is that
     content. Run the commands below without `--project`.
   - Otherwise ask the user for a clean checkout of the tag in a separate folder, for
     example with `git worktree add ../audit-rel-R1.0 rel-R1.0`. Show the command; the
     user runs it or agrees to it. Pass that folder with `--project`.
3. Run `python tools/traceability.py --project <folder> audit BL-0004`. Without a
   difference it prints

   ```
   BL-0004 (delivery, tag rel-R1.0): 65 items listed, 0 differences from the project as it is now
   ```

   and ends with exit code 0. Otherwise it prints one line per item first - `content
   changed`, `status changed`, `missing`, or `not listed` for an approved item the
   record does not hold - and ends with exit code 1.
4. Run `python tools/traceability.py --project <folder> check`. No error is expected,
   with one exception: `COV-26` for the audited baseline itself, when its communication
   record was committed after the tag. Any other error is an audit finding.
5. Report the verdict: `PASS` when steps 3 and 4 show nothing, `FAIL` with every line
   the commands printed, `NOT ASSESSED` when the content of the tag could not be
   obtained. Name the commit the audit ran on.
6. A difference stops the delivery. Do not edit the record and do not move the tag.
   The user decides; the usual way is a new baseline after the cause is found.

The audit is an observation, not a record: the schema has no item type for it, and the
command writes nothing. Its output goes into the hand-over. As evidence the person
responsible keeps that output with the date, the commit and their name where the plan
says, for example with the delivery documents. If the result was passed on with the
delivery, the communication record can say so in the user's words.

Run in the working tree later on, the same command shows what has moved on since the
baseline. That is useful for a change overview, and it is not an audit.

### Putting the checks on record

If the plan or the user wants the checks of a baseline, the audit among them, on
record under a person's name, that person states the verdict and the tool writes a
review record whose subject is the baseline record:

```
python tools/record.py review --checklist "baseline v2" --reviewer "<name as the user stated it>" --verdict approved --checks build/baseline-checks.json BL-0004
```

- The checks file is JSON, a list of entries with `check`, `result` and `note`, with a
  result for every check of `.claude/docs/checklists/baseline.md`: `pass`, `finding`,
  `not-applicable` (the note says why) or `not-assessed`. The tool refuses verdict
  approved while a check has no result or is `not-assessed`. Write the file outside the
  item folders.
- Do this after the communication, when every part of the checklist can be answered.
  Ask who is accountable for the verdict; a model or an agent is never the reviewer.
- The record is evidence that a named person confirmed the checks for this baseline
  record. `practices SUP.8` still shows `no evidence structure` for SUP.8.BP8: the
  schema does not map the record to that practice. Say so.

## After the baseline

- Changing the content of a listed item, and retiring it, goes through
  `/change-request`. The write hook refers to it when it refuses an edit.
- The next baseline of the same purpose gets the next number of the tag pattern.
- What changed since a baseline: `python tools/traceability.py audit <ID>` in the
  working tree lists the items whose content or state differs now, and as `not listed`
  the items approved since. Change
  requests that name an item are shown by `python tools/traceability.py show <ID>`.
