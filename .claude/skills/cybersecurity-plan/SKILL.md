---
name: cybersecurity-plan
description: "Project-dependent cybersecurity management of ISO/SAE 21434 (clauses 6, 7, 12 to 14): responsibilities, the cybersecurity plan with an activity and a decision per subclause in scope, tailoring with reasons, the TARA method (impact categories, feasibility approach, risk matrix), reuse, out-of-context and off-the-shelf components, the cybersecurity interface agreement with customer or supplier, the post-development plans, the cybersecurity case and the record of an independent assessment. Use when a clause of ISO/SAE 21434 is under scope.cybersecurity and no approved plan of kind cybersecurity exists (COV-27), when scope, responsibilities or the method change, when the trace check reports COV-53, or when the case is to be prepared or an assessment recorded."
argument-hint: "['plan', 'agreement', 'post-development', 'case', 'assessment', or nothing for the state per subclause]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py next-id *), Bash(python tools/record.py cybersecurity-case *), Bash(python tools/record.py cybersecurity-assessment *), Bash(python tools/record.py communication *)
---

# Cybersecurity management of the project (ISO/SAE 21434 clauses 6, 7, 12 to 14)

Sets up how the project does cybersecurity engineering: who is responsible, which
activity of the standard is done, by whom, when and with which result, which is tailored
and why, and how risks are rated. At the end it argues in a cybersecurity case that the
result is adequate and records the judgement of an independent assessor where the plan
asks for one. The result is a `plan` of kind `cybersecurity`, plans of the kinds the
other clauses in scope need, a `cybersecurity-case` and a `cybersecurity-assessment`.

| Subclause | What this skill does | Evidence it leaves |
|---|---|---|
| 21434:6.4.1 Cybersecurity responsibilities | asks who is responsible for cybersecurity and for each activity | `Responsibilities`; `responsible` per activity |
| 21434:6.4.2 Cybersecurity planning | drafts an activity per subclause in scope with work products and dates | plan of kind `cybersecurity` (WP-06-01); COV-27, COV-53 |
| 21434:6.4.3 Tailoring | records each tailored or omitted activity with the reason the objective is still reached | `decision`, `rationale` per activity; COV-53 |
| 21434:6.4.4 to 6.4.6 Reuse, out-of-context, off-the-shelf | asks per reused, supplied or third-party component what is analysed or done again | entries for 6.4.4 to 6.4.6 |
| 21434:6.4.7 Cybersecurity case | prepares the evidence per work product; the responsible person writes the argument | `cybersecurity-case` (WP-06-02) |
| 21434:6.4.8 Cybersecurity assessment | prepares the assessment; records what the independent assessor judges | `cybersecurity-assessment` (WP-06-03) |
| 21434:6.4.9 Release for post-development | not a record of its own: a baseline and a communication record that name the case and the assessment | `/baseline`, communication record |
| 21434:7.4.1, 7.4.2 Supplier capability, request for quotation | not covered beyond the plan entry; supplier agreements are `/supplier-monitoring` | entries in the plan |
| 21434:7.4.3 Alignment of responsibilities | drafts the cybersecurity interface agreement | plan of kind `cybersecurity-interface-agreement` (WP-07-01) |
| 21434:12, 13.3, 14.3 Post-development | drafts the production control, incident response and end-of-support plans for the clauses in scope | plans of those kinds (WP-12-01, WP-13-01, WP-14-01) |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. `scope.cybersecurity` empty or absent: say that the project declares no clause of
   ISO/SAE 21434 and stop; `/aspice-start` adds them.
3. Run `python tools/traceability.py status`, `python tools/traceability.py check` and
   `python tools/traceability.py clauses`. Read `COV-27` for the cybersecurity kinds and
   `COV-53`.

## Steps

### 1. Responsibilities and plan (6.4.1 to 6.4.6)
- Read `references/plan-template.md`. Ask the decisions listed there, one at a time:
  the person responsible for cybersecurity, the decision per subclause, the TARA method,
  whether an assessment is done and by whom. The template's values are an example.
- `clauses` lists every subclause of the clauses in scope: write one entry per subclause
  into `cybersecurity_activities`, quoted (`"9.4"`). A tailored or not-applicable entry
  needs the user's reason; by-customer and by-supplier need the interface agreement.
- Reuse and components from elsewhere: list the software components of origin reused,
  supplied or third-party (`list --type software-component`), ask what is analysed or
  repeated for each, and write it into the entries of 6.4.4 to 6.4.6.

### 2. Interface agreement (7.4.3)
- Where a customer or supplier performs part of the activities, read
  `references/agreements-and-post-development.md` and draft the plan of kind
  `cybersecurity-interface-agreement`. Record the agreement only when the user states
  that both parties agreed, with who and when, as a communication record:
  `python tools/record.py communication --subject <PLN-ID> --audience <party> --channel <how> --agreement "<what, by whom>"`.

### 3. Post-development plans (12, 13.3, 14.3)
- For each of these clauses under `scope.cybersecurity`, draft the plan of its kind from
  the same reference. Clause 8 (monitoring) is `/vulnerability-management`.

### 4. Cybersecurity case (6.4.7)
- Run `python tools/traceability.py clauses` and show, per work product, the items that
  provide it and the open findings. Ask the person responsible for the argument: why the
  cybersecurity of the item is adequate, which open findings are accepted and why. Write
  their words to a file, show it, and only on their yes run
  `python tools/record.py cybersecurity-case --prepared-by "<name>" --argument <file>`.
- Work products without evidence and open errors are part of the case as they are; the
  record lists them. Do not leave them out of the argument.

### 5. Cybersecurity assessment (6.4.8)
- Only where the plan asks for one. The assessor is named by the user and is independent
  of the case's author. Prepare for them: the case, `clauses`, `check`, `tara`. Record
  what they state: `python tools/record.py cybersecurity-assessment --case <CSE-ID>
  --assessor "<name>" --independence "<how>" --judgement <accepted|conditionally-accepted|rejected>
  --report <file>` with `--conditions` for a conditional acceptance.

### 6. Release for post-development (6.4.9)
- Say that the toolkit has no record of its own for it: `/baseline` creates the baseline
  of the released configuration, and its communication record names the case and the
  assessment.

## Writing

- Show each plan before writing it and ask: "May I write PLN-NNNN in `plans/`?" IDs from
  `python tools/record.py next-id plan`; status `draft`; approval through `/review` with
  the checklist `plan.md`.
- Names of people come from the user. The argument of the case and the report of the
  assessment are written in the words of the person who stands behind them.

## Checks before you finish

Run `python tools/traceability.py check` and `python tools/traceability.py clauses`.
- `FORMAT`, `SCHEMA`, `LINK` on items written in this session: fix them.
- `COV-27` and `COV-53`: report each with what closes it.
- Quote `clauses` for the state per subclause; do not restate it from memory.

## Hand-over

1. The subclause table with what was done and what is open.
2. The decisions per subclause as `clauses` prints them, and the work products without
   evidence.
3. Decisions still owed: responsibilities, tailoring reasons, the TARA method, the
   assessor, agreements with other parties.
4. Next: `/review` for the plans; `/tara`; `/cybersecurity-concept`;
   `/vulnerability-management` where clause 8 is in scope; `/baseline` for the release.

## Do not

- Do not decide a tailoring, a responsibility, a rating method or an assessment
  judgement in anyone's name.
- Do not write the argument of the case or the assessor's report yourself; draft only
  what the person asks for and record their words.
- Do not record an agreement with a customer or supplier that the user has not stated.
- Do not copy the text of ISO/SAE 21434 or its annexes into a plan; the catalog gives
  the identifiers and the objectives in our words.
