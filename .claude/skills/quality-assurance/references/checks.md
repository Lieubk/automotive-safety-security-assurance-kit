# Preparing a quality check

A check prepared here has two parts kept apart: the facts the tools show, which the
record stores, and the judgement, which is the checker's. The record states both.

## Work products

1. **Sample.** With the checker: the types the check names; per type the items with the
   highest risk first - the highest ASIL, changed since the last check
   (`python tools/traceability.py diff <ID>`), with findings in an earlier review, from a
   process with open findings in `practices`.
2. **Facts per item.** `show <ID>`; the approving review record (checklist and version,
   reviewers, findings and how they were closed); `check` lines on the item. An item
   without an approving review, or with `SUSPECT`, `CONSISTENCY` or `UPSTREAM`, does not
   conform as it stands: the facts say so without a reading.
3. **Content.** Apply the checklist of the type to the sample - all checks of kind
   semantic, quoting the text each answer rests on. A second reading by the
   `aspice-reviewer` agent is possible (give it the IDs, the checklist and the upstream
   items, as `/review` does); its results are proposals.
4. **The review itself.** Did the review do what its checklist asks: a result for every
   check, findings closed by a later review, a reviewer who did not write the item? A
   review that passed something the checklist forbids is a finding against the review.
5. **Verdict.** The checker reads facts and proposals and decides.

## Process activities

1. **What was promised.** The plan of the process (`plans/`, its `kind`): methods, order,
   entry and exit criteria, responsibilities, independence, regression.
2. **What the records show.** `python tools/traceability.py practices <PROCESS>`; the
   process gate report if one exists; `progress` for its work packages; `problems` for
   problems whose origin or detection lies in it; a sample of its records (runs, builds,
   reviews) read against the plan.
3. **Questions the records cannot answer** - did the people work by the plan, do they
   know it - are asked of the people, and their answers are named as theirs.
4. **Verdict.** The checker decides; a gap between plan and practice is a finding
   whether the plan or the practice has to change.

## Findings

Every finding the checker confirms gets an action before it is recorded:

| The finding is | Action |
|---|---|
| a work product that is wrong | a `problem-report` through `/problem-resolution` |
| a way of working that departs from the plan, a missing record, a plan that does not fit | a `corrective-action` with owner, due date, `raised_in` the quality record, `Deviation` and `Action` |

The action item is written first, so that the finding can name it; the record tool
refuses a finding whose action does not exist.

## Independence

`checked_by` is the person in the role, as the user names them. The facts list the
reviewers of each item; if the checker is among them, or wrote the item, say so: the
check is then not independent, whatever its result.
