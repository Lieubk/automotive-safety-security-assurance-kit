# Reviews, open items and follow-up

## What `suppliers` shows

`python tools/traceability.py suppliers [--as-of DATE] [--json]` prints, per agreement:

- the meetings agreed, how often each kind was held, and how many days overdue the next
  one is (measured only where `cadence` is a number of days);
- the communication records about the agreement;
- the open items that no later review closed, with owner, due date and lateness;
- the corrective actions that address the agreement.

Quote the figures; do not recompute them. The date is `--as-of`, today by default.

## Preparing a meeting

Propose an agenda from the output and the agreement; the user changes it.

| Kind | Typical subjects | Source |
|---|---|---|
| technical (BP3) | technical matters, problems and risks of the supplier's work; interface questions; results of the supplier's tests and of the project's acceptance of deliveries; problem reports that concern the supplier | `exchanges` received, `PRB` items, earlier open items |
| progress (BP4) | schedule, quality and cost against what was agreed; the supplier's status report compared with the agreement; risks and how they are handled | status reports exchanged, `exchanges`, corrective actions |

Always: every open item not closed (read aloud with owner and due date), corrective
actions on the agreement, what the agreement says is due since the last meeting. A
meeting that deals only with logistics does not review technical work or progress; say
so to the user if the minutes show nothing else.

## What is recorded

`python tools/record.py supplier-review --agreement <SAG-ID> --kind technical|progress
--held-at <date> --participant "<name>" [--participant "<name>" ...] --minutes <file>
[--open-items <file>]`

- `--participant` is given once per person, both sides, by name or role. No participants,
  no record.
- `--minutes` is a text file of the participants' words: what was reviewed and what was
  decided. A progress review names schedule, quality and cost; a technical review the
  matters, problems and risks. The skill may help to draft from notes, but the
  participants confirm it, and the file is written outside the item folders.
- A record is final. A correction is a new record or an open item in the next review,
  never an edit.

## Open items file

JSON list, one entry per item:

```json
[
  {"id": "1", "text": "Supplier delivers the corrected interface description",
   "owner": "Supplier engineer", "due": "2026-07-10", "state": "open"},
  {"id": "2", "text": "Timing of the position signal was confirmed",
   "owner": "Software lead", "due": "2026-06-30", "state": "closed",
   "closes": "SRV-0001#3"}
]
```

- `id`, `text`, `owner` and `state` are required; `due` is a date and is asked for.
- An item is listed with state `open` in the review that raises it. Later reviews do
  not repeat it; they close it with a `closes` entry.
- A later review closes an earlier item with an entry whose `closes` is
  `<SRV-ID>#<id>` of the item. The trace check reports a `closes` that names no open
  item of an earlier review of the same agreement as `LINK`. An item closes only on the
  statement of its owner, with what settled it written in `text`.
- An item that stays open past its due date is named in the next minutes; moving a due
  date is a new open item that says why.

## Deviations

- A missed objective found in a review: ask whether action is decided. Write a
  `corrective-action` item (`python tools/record.py next-id corrective-action`, folder
  `records/actions/`) with `addresses: [<SAG-ID>]`, `raised_in` naming the review, owner,
  due date, and the sections `Deviation`, `Action` and, once done, `Effect`.
- `/project-status` follows it to closure. The decision, owner and due date are those of
  the person who decided; the skill writes them down.
- A changed objective is a change of the agreement: `references/agreement-template.md`,
  then `/change-request` where the agreement is in a baseline.
- Escalation outside the project is the user's decision. Record what was told to whom
  with `python tools/record.py communication --subject <SAG-ID> --audience ... --channel
  ... --practice ACQ.4.BP5`, only when the user says it happened.

## Exchanged information (BP2)

- Received: `/import-inputs` registers the delivery as imported items, accepted by an
  input acceptance review; code taken over is named in the build manifest under
  `delivered`. A delivery that does not match the delivery note is a query to the
  supplier or a problem report, not an edit.
- Sent or received without an item (reports, notices, questions): a communication
  record with `--subject <SAG-ID>` and `--practice ACQ.4.BP2`; add the IDs of the items
  concerned as further `--subject` values.
- `python tools/traceability.py practices ACQ.4` shows the evidence per base practice;
  quote it for what exists and what does not.
