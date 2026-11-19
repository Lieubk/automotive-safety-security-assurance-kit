---
name: supplier-monitoring
description: "Agree with a supplier how the two sides work together and follow what the supplier delivers (Automotive SPICE ACQ.4): the supplier agreement with joint processes, interfaces, responsibilities, the information to exchange and the rhythm of technical and progress meetings; record of what was exchanged; supplier reviews with minutes and open items followed to closure; corrective action when agreed objectives are missed. Use when a supplier delivers software or system elements to the project, when a delivery, a meeting or an open item is due, when a supplier misses an agreed objective, or when the agreement has to change."
argument-hint: "['agreement', 'review', 'exchange', 'deviation', a SAG ID, or nothing for the state of every supplier]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---

# Supplier monitoring (ACQ.4)

Keeps track of what the project's own supplier delivers and how. The agreement says what
is done together, what is exchanged and how often the two sides meet; the reviews, the
records of exchange and the corrective actions show that it happened. Here the project
is the customer. The toolkit does not negotiate or sign: the agreement and its changes,
the acceptance of a delivery and the decision on action towards the supplier belong to
named people, and are recorded as they state them.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| ACQ.4.BP1 Agree on and maintain joint processes, joint interfaces, and information to be exchanged | drafts the agreement from what the user says was negotiated; keeps it current | `supplier-agreement` item (SAG), reviewed with `supplier-agreement v1` |
| ACQ.4.BP2 Exchange all agreed information | shows what is due; registers deliveries received; records what was sent or received | imported items, `delivered` of the build manifest, communication records |
| ACQ.4.BP3 Review technical development with the supplier | prepares the meeting from the open items; records the minutes the participants give, and the open items | `supplier-review` record, kind `technical` |
| ACQ.4.BP4 Review progress of the supplier | the same for schedule, quality and cost against the agreement | `supplier-review` record, kind `progress` |
| ACQ.4.BP5 Act to correct deviations | records the action a named person decides; routes a changed objective to the agreement | `corrective-action` items; agreement versions and change requests |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. `ACQ.4` not in `scope.processes`: stop. "Supplier monitoring is out of scope for this
   project. I record nothing about suppliers."
3. Run `python tools/traceability.py check` and `python tools/traceability.py suppliers
   --as-of <date>` (today unless the user names a date). Every command takes `--project
   <dir>` after the script name when the project is not the current directory. Read: the
   meetings agreed and how often each kind was held, meetings overdue, open items with
   owner, due date and lateness, communication records, corrective actions.
4. With a SAG ID as argument, read that agreement with `show <ID>`; without one, work
   through the agreements the output lists, most overdue first.

## Steps

### 0. Selection (ISO/SAE 21434 7.4.1, 7.4.2; ISO 26262-8:5)
- Where the standards are in scope and the supplier is still to be chosen, read
  `references/supplier-selection.md`: what the request for quotation asks for safety and
  cybersecurity, the criteria and their evidence, and the decision of a named person, as
  a `supplier-evaluation` reviewed with `/review`. `COV-76` asks for an approved
  evaluation that selected the supplier of each agreement.

### 1. The agreement (BP1)
- No agreement for the supplier, or the user says terms changed: read
  `references/agreement-template.md`, ask the questions listed there and draft one SAG
  item. What was agreed is stated by the user, with the other side; do not propose
  terms as if they were agreed. Proposals are labelled as proposals.
- An agreement in a baseline changes only through `/change-request`; name it, do not
  edit. Any other approved agreement that changes is no longer approved.
- Review through `/review` with the checklist `supplier-agreement`. Approval is a
  named person's; the agreement is not signed here.

### 2. Exchanged information (BP2)
- For each `exchanges` entry of the agreement that is due, ask whether it happened.
  Deliveries received: register with `/import-inputs` (imported items, accepted by an
  input acceptance review); code taken over is named in the build manifest under
  `delivered`. Deliveries and information sent: ask what, to whom, when, by which channel.
- When the user states that something was sent or received, record it:
  `python tools/record.py communication --subject <SAG-ID> [--subject <item IDs>]
  --audience "<party>" --channel "<how>" --practice ACQ.4.BP2 [--sent-at <date>]`.
- Whether a delivery is accepted, and on which criteria, is the user's decision. Record
  the answer; do not write it.

### 3. Prepare a review (BP3, BP4)
- Read `references/reviews-and-follow-up.md`. From `suppliers` list: the open items not
  closed, with lateness; the corrective actions addressing the agreement; what the
  agreement says is exchanged and due. This is the agenda proposal; the user changes it.
- Technical review: matters, problems and risks of the supplier's technical work.
  Progress review: schedule, quality and cost against the agreement. Ask which kind.

### 4. Record the review (BP3, BP4)
- After the meeting, ask for: date held, every participant on both sides, the minutes
  (the participants' own text, in a file), and the open items with owner and due date.
- A later review that settles an earlier open item lists an entry with `closes:
  "<SRV-ID>#<id>"`. Ask the owner's statement before closing one; an open item whose
  owner has not answered stays open and the minutes of the next review say so.
- Offer to write the minutes down from the user's notes as a draft; the participants
  confirm the text before it is recorded.

### 5. Deviations (BP5)
- Where `suppliers` or the minutes show a missed objective, ask whether action is
  decided. If yes - owner, due date, what is done, how recurrence is kept away - write a
  `corrective-action` item with `addresses: [<SAG-ID>]`; `/project-status` keeps the
  register and follows it to closure. A deviation without a decided action is named as
  open in the hand-over.
- A changed objective is a change of the agreement: step 1 and, once baselined,
  `/change-request`. Escalation to the supplier is the user's decision and their words.
- A defect in a delivery is also a problem: name `/problem-resolution`.

## Writing

- Show the draft and ask before writing: "May I write SAG-NNNN in `plans/suppliers/`?"
  and "May I record this review of <agreement>, held <date>, kind <kind>, with <N>
  participants and <M> open items?". Status of a new agreement is `draft`.
- IDs: `python tools/record.py next-id supplier-agreement` and `next-id corrective-action`.
- Review record, only by the tool: `python tools/record.py supplier-review --agreement
  <SAG-ID> --kind technical|progress --held-at <date> --participant "<name>" [--participant
  ...] --minutes <file> [--open-items <file>]`. Minutes and open items are written to
  files outside the item folders, for example `build/supplier-minutes.md`. Layout in
  `references/reviews-and-follow-up.md`.
- Names, dates and statements are what the user gives. Nothing about a real supplier
  leaves the project: no names in anything published.

## Checks before you finish

Run `python tools/traceability.py check`, then `suppliers` and `practices ACQ.4` again.
- `FORMAT`, `SCHEMA`, `LINK` on items and records written in this session: fix them. A
  `LINK` on `closes` means the entry names no open item of an earlier review: correct it.
- Quote what `suppliers` now shows: meetings overdue, open items late, corrective
  actions open. Coverage findings are reported as they are.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session.
2. Per agreement, in one line each: meetings held against agreed, overdue meetings,
   open items and how many are late, corrective actions open (from `suppliers`).
3. What is missing: statements not given, deliveries not confirmed, deviations without
   a decided action, agreement not reviewed.
4. Next: `/review` for a draft agreement; `/change-request` where a baselined agreement
   changes; `/project-status` for the corrective actions; the date of the next meeting.

## Do not

- Do not write terms, dates or commitments of the supplier that nobody stated.
- Do not record a delivery, a meeting or an exchange that the user did not say happened.
- Do not accept a delivery, decide corrective action or escalate in anyone's name.
- Do not write minutes into a record that the participants have not confirmed.
- Do not close an open item without the statement of its owner, nor edit a recorded review.
- Do not edit an agreement that is in a baseline, and do not approve an agreement.
