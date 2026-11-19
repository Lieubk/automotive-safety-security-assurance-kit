# The risk

File: `records/risks/<ID>.md`. Type `risk`, lifecycle `risk` in `schema/items.yaml`. A
risk is not reviewed through `/review`; it is moved through its states with the user, and
each state needs what the table says.

| State | Means | Needs (the check reports what is missing) |
|---|---|---|
| `identified` | recorded, not yet rated | `title`, `category`, `owner`, `identified_at`, `identified_in`, section `Description` |
| `analysed` | rated and ranked | `probability`, `impact` within the scales of the plan, section `Analysis` (`COV-50`) |
| `in-treatment` | treatment is under way and watched | `treatment`, `indicators` with a threshold (`COV-52`), section `Treatment and monitoring` |
| `closed` | it can no longer occur, or it occurred and was handled | the owner's statement, written into `Treatment and monitoring` |
| `accepted` | kept as it is, knowingly | `decision`: who, when, why. Above `acceptable_up_to` this is mandatory and names a person (`COV-51`) |
| `rejected` | not a risk of the project | the reason, written into `Description` |

A risk above `acceptable_up_to` must be `in-treatment`, `closed`, or `accepted` with a
decision (`COV-51`). Moves: identified to analysed; analysed to in-treatment or
accepted; in-treatment to closed; identified or analysed to rejected.

## Example

```markdown
---
id: RSK-0001
type: risk
title: Hall sensor supplier delivers samples after integration starts
status: in-treatment
category: supplier
owner: Software lead
identified_at: '2026-03-10'
identified_in: "supplier review minutes of 2026-03-09"
probability: 3
impact: 3
treatment:
  - {action: "Agree a simulated sensor for the first integration steps", owner: Software test engineer, state: open, due: '2026-05-15'}
  - {action: "Ask the supplier for a dated delivery commitment", owner: Project lead, state: done, due: '2026-04-01', done_on: '2026-03-30'}
indicators:
  - {name: "Days between promised and actual sample date", threshold: 10, value: 4, as_of: '2026-04-30'}
---

## Description
Cause: the sample delivery depends on the supplier's own release plan. Event: the
samples come after the first integration step. Consequence: the milestone for the first
integrated build slips.

## Analysis
Probability 3: two earlier deliveries of this supplier came 2 to 3 weeks late (supplier
review). Impact 3: the milestone `M2` would be missed. Exposure 9, above the
acceptable level of the plan.

## Treatment and monitoring
What is done and by whom; how the indicator shows that the risk grows or that the
treatment works; the value at which the owner acts further; the date of the next
review.
```

## Fields

| Field | Rule |
|---|---|
| `category` | one of `risk_categories` of the approved plan |
| `owner` | the person who answers for the risk and its treatment, as the user states |
| `identified_in` | what brought the risk up: the plan, a `design-decision`, a change request, a problem report, a supplier review, a meeting - by ID or date |
| `probability`, `impact` | whole numbers from 1 to the plan's number of levels; exposure is their product |
| `treatment` | list of `{action, owner, state: open or done, due, done_on}`; every action has an owner and a due date |
| `indicators` | list of `{name, threshold, value, as_of}`; what is measured, the value at which to act, the last value seen and its date |
| `decision` | who accepted the risk, when and why; never written for a person who did not say so |

## Description

State the cause, the event and the consequence in separate sentences: a risk with only an
event cannot be treated, and one without a consequence cannot be rated. One risk states
one event. A cluster of related events is several risks, or one risk whose cause is
common and said so.

## How to rate

- Use the plan's meaning of each level and name the fact behind the level: a past
  delivery, a measured load, a figure of the supplier. A level without a reason is a
  guess; say so in `Analysis` and let the owner decide.
- Rate the risk as it stands now, with the treatment so far in place; when treatment
  changes the rating, re-rate with the reason.
- Exposure is read from `python tools/traceability.py risks`, never computed by hand.
- A rating that depends on matters outside the repository (supplier situation, staffing,
  commercial terms) is the owner's alone; the skill proposes only what the items show.

## How to treat

| Option | Means | Typical action |
|---|---|---|
| avoid | change the plan so that the event cannot occur | drop a feature, choose another technology |
| reduce probability | act on the cause | an early prototype, a simulator, a second source |
| reduce impact | act on the consequence | a fallback, buffer, recovery steps |
| transfer | someone else carries the consequence | a contract term, a supplier commitment |
| accept | keep as it is | a named person records the `decision` |

The owner chooses. A treatment action is something that can be carried out and checked:
who does what by when. "Watch the situation" is an indicator, not an action.

## How to monitor

- An indicator shows a change in this risk: a count, a date difference, a measure of the
  items. Give it a threshold that means "act now", below the point of failure.
- At each review date record the value and `as_of`; an old `as_of` is a finding for the
  owner. `traceability.py risks` lists indicators whose value reached the threshold, and
  treatment actions that are overdue.
- Treatment that does not progress, or an indicator at its threshold, leads to a
  `corrective-action` with `addresses: [<RSK-ID>]`, kept through `/project-status`.
- A risk that occurred is handled as a problem or a change; say which in
  `Treatment and monitoring` before closing it.
