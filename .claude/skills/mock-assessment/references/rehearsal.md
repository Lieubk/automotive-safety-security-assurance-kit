# Rehearsing an assessment

## The evidence pack

Per process, one block per base practice:

| Part | Source |
|---|---|
| what must be true, typical evidence | the row of the practice in `aspice/3.1/notes/<PROCESS>.md` |
| what the trace engine observes | `python tools/traceability.py practices <PROCESS> --json`: `state`, `evidence`, `settled`, `errors`, `warnings`, and `by` - the item types, link roles and rules behind the practice |
| the evidence itself | the items and records of the types in `by` (`list --type`), the run, build, review and quality records, with their IDs |
| what stands against it | the lines of `check` whose bracket names the practice |
| the gate's view | the verdict of the latest process gate, if one exists, with its date |
| what depends on what | `depends_on` in `aspice/3.1/processes/<PROCESS>.yaml`: the practices whose rating this one depends on, by rule or by recommendation |

An assessor reads evidence and talks to people; the pack is for both. Quote IDs, so that
each piece can be opened during the rehearsal.

## Interview questions

Files show what exists. An assessor also asks how it came about. Per practice, ask what
the files cannot show, for example:

- Who did this, and who checked it? How do you know the reviewer did not write it?
- What did you base it on? Which version of the input was current then?
- How do you decide (a severity, a regression selection, an integration order)? Show me
  one case where you decided differently from the plan, and why.
- What happens when a test fails, a review finds something, a delivery is late?
- Who was told, and what did they do with it?

For a practice whose state is `no evidence structure`, the interview is the only
source the toolkit has: ask where the evidence is kept.

## Ratings

The scale, in our words:

| Rating | Meaning |
|---|---|
| N | not achieved: little or no evidence that the practice is performed |
| P | partially achieved: some evidence, but important aspects are missing or performed unpredictably |
| L | largely achieved: performed systematically, with weaknesses |
| F | fully achieved: performed completely, no significant weakness |

The band that agrees with what the trace engine observes:

| State in `practices` | Ratings in the band |
|---|---|
| `evidence present` | L, F |
| `warnings open` | P, L, F |
| `evidence not settled` | P, L |
| `findings open` | N, P, L |
| `no evidence yet` | N, P |
| `no evidence structure` | none: every rating names where the evidence is |

A rating outside the band is not wrong. It needs a reason, because a reader of the
record would otherwise see a contradiction: for example F with `findings open`, or P with
`evidence present` because the content of the evidence is weak.

The catalog records rating dependencies between practices (`depends_on`), by rule or by
recommendation. A practice rated above one it depends on by rule needs a reason; one
above a practice it depends on by recommendation is listed.

## The ratings file

```json
{
  "practices": [
    {"practice": "SUP.9.BP1", "rating": "L", "note": "status model complete, urgent path untested"},
    {"practice": "SUP.9.BP2", "rating": "F"}
  ],
  "attributes": [
    {"process": "SUP.9", "attribute": "PA 1.1", "rating": "L", "note": "as the assessors aggregate it"}
  ]
}
```

Every base practice of each process named needs an entry. `note` holds the reason in
the assessors' words. `attributes` is optional.

At level 2 (`--level 2`, or `aspice.target_level` 2 or higher) add one entry per process
and generic practice:

```json
"generic": [
  {"process": "SUP.9", "practice": "GP 2.1.1", "rating": "L", "note": "objectives in WP-0007, no quality target"}
]
```

They are checked like base practices: against the state `traceability.py generic`
prints (a state of `a person has to judge` accepts any rating) and against the
dependencies between generic practices in `aspice/3.1/capability-levels.yaml`.
