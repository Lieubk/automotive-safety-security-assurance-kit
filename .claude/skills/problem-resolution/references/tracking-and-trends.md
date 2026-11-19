# Tracking problems and analysing their trends

## The commands

| Command | Shows |
|---|---|
| `python tools/traceability.py problems [--as-of DATE] [--json]` | every problem report known on the date: state, severity, origin, detection, age in days (to the closure, or to the date), affected items, the change requests that resolve it; then counts by severity, origin and detection, and unresolved problems by age |
| `python tools/traceability.py history <PRB-ID>` | the states the report had in the commits that changed it, with dates. It reads git: commit the report at each change of state, or the history has gaps |
| `python tools/traceability.py check` | `COV-39` to `COV-42` and the `PROBLEM` warnings |
| `python tools/record.py problem-trends --reported-by NAME --assessment FILE [--as-of DATE] [--period TEXT]` | writes the trend report: the list and the figures of `problems` for the date, and the analyst's assessment |

`problems` reports the states as they are now and measures ages to the date given; it
does not reconstruct the past. For a report "as of" an earlier date, run it on that date.

## Reading the figures

Propose a reading; the analyst decides what it means.

| Look at | Asks | Possible action |
|---|---|---|
| `origin` against `detected_by` | which activity let problems through that an earlier one should have found - a requirement problem found in qualification, a design problem found by integration tests | a sharper check in the checklist of that activity; a review of the strategy of that level |
| one `origin` or one component recurring | a weak spot | a review of that component or work product; a decision on the design |
| unresolved by age | problems that stay | a corrective action with an owner and a date (`/project-status`) |
| `critical` and `major` unresolved | risk to the next milestone | a statement in the next project status report |
| rejected share | reports that were not problems | clearer criteria for what to report |

With few problems there is no trend: say so rather than reading one into three data
points.

## The assessment

The assessment is the analyst's text, in their words: what they see, what they conclude,
the actions decided with owners and dates, and what was decided not to do. The skill
may propose a draft from the figures; the analyst changes it as they see fit and states
that it is theirs. A report without an assessment is refused.
