# The communication record

A communication record (`records/communication/<ID>.md`, type `communication-record`)
states that something was made known: what (`subject`), to whom (`audience`), how
(`channel`), on which day (`sent_at`), and, where it happened, what was agreed and by
whom (`agreement`). It is written by `python tools/record.py communication` and is
final when written.

## What it is evidence for

| Practice | What has to be true | Typical subject | Typical audience |
|---|---|---|---|
| SWE.1.BP8 | everyone who builds on the software requirements works from the same agreed set | the requirements freeze baseline | software architect, developers, test, the source of the system-level inputs |
| SWE.2.BP9 | everyone affected knows the agreed architecture | the design freeze baseline | developers, integration and test, owners of neighbouring components |
| SWE.3.BP7 | everyone affected knows the agreed detailed design | the design freeze baseline | developers, unit verification |
| SWE.4.BP7 | the unit verification results reached those who decide on their basis | the release candidate baseline and its test run and analysis run records | project lead, quality assurance, integration |

Two limits to keep in mind and to say in the hand-over:

- These practices ask that the affected parties share one understanding. They do not ask
  for a signature. A notice that reached the right roles is evidence; an agreement is
  recorded only when one was actually reached.
- Name per record which practices it serves, from its subject and audience, with
  `--practice` (repeatable): a mail to customer system engineering about the
  requirements freeze serves SWE.1.BP8, not SWE.3.BP7. `practices` then counts the
  record only for those; a record without `--practice` counts for every communicate
  practice, which overstates the evidence.

`COV-26` demands at least one final communication record for every baseline whose
purpose is not internal, and names all communicate practices of the processes in
scope. One record that names the baseline satisfies the rule. It does not follow that
every practice was served: a release candidate whose only record went to the
developers has not brought the verification results to those who decide on them.

## What to ask the user

Ask for facts, in this order. Write down the answers in the user's words.

1. What was made known: which baseline, and for unit verification results which runs?
2. To whom? Roles or parties, as the schema asks: "software architect", "customer
   system engineering". Not "the team".
3. How? A meeting, a mail with the baseline notice, a release note, a review session.
4. When? Without `--sent-at` the tool writes today's date into `sent_at`. If the
   communication happened on another day, pass `--sent-at` with that date as
   YYYY-MM-DD. Anything else stops the command.
5. Was anything agreed, and by whom? Only then pass `--agreement`. This is the place
   where the agreement of those who build on the items is put on record - developers,
   test, integration, the customer. The review checklists of the items do not ask for
   it: an item is approved by its reviewers, and made known afterwards.

If the answer to 2 or 3 is "not yet", nothing is recorded. Give the user the notice
below and stop.

## The command

A notification:

```
python tools/record.py communication --subject BL-0001 --audience "software architect" --audience "software developers" --audience "customer system engineering" --channel "baseline notice by mail, with the status output" --practice SWE.1.BP8
```

A notification with an agreement:

```
python tools/record.py communication --subject BL-0001 --audience "customer system engineering" --channel "requirements review meeting" --sent-at 2026-11-17 --agreement "customer system engineering confirmed SWR-0001 to SWR-0009 as the software requirements of release R1.0"
```

Unit verification results (SWE.4.BP7):

```
python tools/record.py communication --subject BL-0003 --subject RUN-0001 --subject SAR-0001 --audience "project lead" --audience "quality assurance" --channel "verification summary in the release meeting" --sent-at 2026-11-24
```

The tool prints `wrote records/communication/CMR-0001.md: BL-0001 to ...`. A subject
that is not an item of the project is refused with `no such item: <ID>` and
`no record written`.

Rules:

- One record per event. Two audiences informed in two different ways are two records.
- Pass what the user said. Do not improve an audience ("all stakeholders"), and do not
  turn "they did not object" into an agreement.
- Roles and parties, no names of persons, unless the user asks for a name to be
  recorded.
- A record with a mistake stays as it is. Write a new one and tell the user which one
  counts.

## The baseline notice

When nothing has been communicated yet, draft this for the user to send. Every figure
comes from a tool or from the record; quote, do not retype from memory.

```
Baseline BL-0001, tag req-1, purpose: requirements freeze, created 2026-11-18

Content: <the lines of `python tools/traceability.py status` for the types concerned>
Not in the baseline: <items left out because they are not approved, from `list`>
Trace check at the baseline: <the summary line of `check`>
Changed since baseline <previous ID>: <the lines of `audit <previous ID>`, each with
  the change request that names the item>
Known open points: <open change requests from `list --type change-request`; accepted
  deviations>
For a release candidate: <the `latest ... test run` lines of `status`; coverage and
  open findings from the run records>
What we ask of you: <take note / object by <date> / confirm>
```

`python tools/traceability.py audit <previous ID>`, run in the working tree, lists
every item whose content or state differs from the previous baseline, and as
`not listed` the items approved since.

## After recording

- Run `python tools/traceability.py check`: the `COV-26` line for the baseline is gone.
- Propose the commit of the record; commit only on the user's yes:

```
git add records/communication/CMR-0001.md
git commit -m "Communication record CMR-0001 for baseline BL-0001"
```

- When SUP.8 is out of scope and the project has no baseline of its own, the subject is
  what was communicated instead: the item IDs, or the IDs of the run records.
