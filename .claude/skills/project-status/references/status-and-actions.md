# Status reports and corrective actions

## The figures

`python tools/traceability.py progress --as-of 2026-04-30` prints, for a plan like the
one in the project plan template (an illustration, not output of the worked example):

```
Progress as of 2026-04-30
WP-0001  in progress                  finish 2026-06-26 estimate 64    actual -     delivered 0/0 settled  Project lead
  WP-0002  done                         finish 2026-03-20 estimate 8     actual 9     delivered 9/9 settled  Software developer
  WP-0004  in progress                  finish 2026-05-08 estimate 12    actual 7     delivered 1/3 settled  Software developer
  WP-0005  not started                  finish 2026-05-29 estimate 14    actual -     delivered 0/0 settled  Software developer
Milestones
  Design frozen            2026-04-17 missed
  Release candidate        2026-06-12 due in 43 days
Corrective actions
  CA-0001  open   due 2026-05-08 Software lead
5 work packages: 1 done, 3 in progress (0 late), 1 not started (0 late to start); 1 milestones missed; 1 corrective actions open (0 overdue)
```

`--json` gives the same as data. `record.py status-report` takes its figures from the
same function, so the report and the command agree for the same date.

## The assessment

The reporter's own reading. It is what makes the report a report and not a printout.
A draft from the figures is a help; the reporter rewrites it.

```
Design freeze missed on 2026-04-17: the design review of WindowPos found that the
pulse time-out was not designed (REV-0015). Corrected design in review since
2026-04-28; the freeze is expected on 2026-05-06. The release candidate on 2026-06-12
is not at risk if unit verification starts by 2026-05-11, which WP-0005 allows.
Effort of WP-0002 was 9 days against 8. CA-0001 is on track. Decision needed: none.
```

Good: names the deviation, its cause as far as the items show it, the consequence for
the next milestone, and what is decided. Not good: "on track" while a milestone was
missed; causes no item supports; figures that differ from `progress`.

## The report

Written only by `python tools/record.py status-report`; final when written; never
edited. A later report supersedes it for a later date. Fields the tool fills in:
`as_of`, `period`, `reported_by`, `work_packages` (item, state, planned finish, late,
estimate, actual effort, delivered, settled), `milestones`, `corrective_actions`,
`check` (errors and warnings at that moment), and the section `Assessment` with the
reporter's text.

## A corrective action

```markdown
---
id: CA-0001
type: corrective-action
title: Design freeze late - review the pulse supervision first
status: open
owner: Software lead
due: "2026-05-08"
raised_in: PSR-0002
links:
  addresses: [WP-0004]
---

## Deviation

Design freeze planned 2026-04-17, missed: the design of WindowPos lacked the pulse
time-out (REV-0015, finding F3). WP-0004 is two weeks behind its first activity.

## Action

Review the corrected design of UNT-0002 alone and first, so that coding can start;
CDS-0001 follows. To keep it from coming back: a supervision function of every input
is a line of the design checklist the developer applies before review.
```

| State | Means | Set when |
|---|---|---|
| `open` | decided, not carried out | written |
| `done` | carried out | its owner states it |
| `closed` | the effect is shown | a later report or review shows it; `Effect` names that evidence |
| `cancelled` | dropped | the reason is added to `Action` |

An action goes back from `done` to `open` when the effect does not come about. The
schema keeps `Effect` mandatory for `closed`.
