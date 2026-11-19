---
name: mock-assessment
description: "Rehearse an Automotive SPICE assessment of the processes in assessment scope: an evidence pack per base practice, interview questions for what the repository cannot show, a walkthrough in which named people rate each base practice N, P, L or F, a consistency check of their ratings against the observations of the trace engine and the rating dependencies of the process catalog, and a self-assessment record with strengths, weaknesses and actions. Use some weeks before an assessment, after a process gate, or when the team wants to know where it stands. The toolkit rates nothing and the result is not an assessment."
argument-hint: "[process IDs, or nothing for the assessment scope]"
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---

# Mock assessment

Prepares the team for an assessment by going through it once without an assessor: the
evidence per base practice, the questions an assessor would ask, and a rating by people
of the team, checked for consistency. The ratings are theirs. Nothing here is an
assessment, and no capability level follows from it.

| Purpose | What this skill does | What it leaves |
|---|---|---|
| Evidence | assembles per base practice what the project holds and what the trace engine observes | the evidence pack in the conversation; on request a file under `reports/` |
| Interviews | lists, per practice, the questions whose answers lie with people, not in files | the question list |
| Ratings | records the rating N, P, L or F the named assessors give, with their reasons | `self-assessment` record |
| Consistency | compares every rating with the observation and with the rating dependencies of the catalog; asks for a reason where they part | `consistency` in the record |
| Follow-up | turns the weaknesses the assessors name into actions | corrective actions or problem reports through their skills |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. Say: "This is a rehearsal by the team. It is not an assessment, gives no capability
   level, and its ratings are those of the people who give them."
3. Processes: the arguments, else `scope.assessment_scope`, else `scope.processes`.
   Name a process of the assessment scope that the project is not responsible for:
   its evidence lies with another party.
4. Ask who rates. People who know the assessment model and, where possible, did not
   write the work products; their names go into the record as the user states them.
5. Run `python tools/traceability.py check` and `python tools/traceability.py practices`
   for the processes. A process gate older than the last commit is out of date: propose
   `/process-gate` first, its report is the best input.

## Steps

### 1. Evidence pack
- Read `references/rehearsal.md`, "The evidence pack". Per base practice: the row of
  `aspice/3.1/notes/<PROCESS>.md` (what must be true, typical evidence), the state and
  the `by` of `practices --json`, the items and records behind it, open findings of
  `check`, and the verdict of the process gate if one exists.
- With `aspice.target_level` 2 or higher, add the generic practices per process, as the
  file `level-2.md` among the references of `/process-gate` lists them.

### 2. Interview questions
- Per practice, the questions whose answer no file holds: who did it, how they decided,
  whether the people concerned know the plan, what happens when it goes wrong. Read
  "Interview questions" in `references/rehearsal.md`.
- Name the role to ask for each process.

### 3. Walkthrough and ratings
- Go through the practices with the assessors, one by one: show the evidence, ask the
  questions, let them rate. The scale and the band that agrees with each observation are
  in "Ratings" in `references/rehearsal.md`. Show the band as what the tools see, not as a
  proposal; do not suggest a rating.
- Write their ratings, with every reason they give, to a JSON file as
  "The ratings file" describes. Ratings of process attributes are optional and are
  theirs too.

### 4. Consistency
- `python tools/record.py self-assessment --ratings <file> --process <ID> ... --check-only`
  lists practices without a rating and the flags: a rating outside the band of the
  observation, and a rating above that of a practice it depends on by a rule of the
  catalog (a recommendation is listed too, without the need for a reason).
- Put every flag to the assessors: they change the rating or give the reason; the
  reason goes into the note. Repeat until the command reports no gap.

### 5. Record
- The summary - strengths, weaknesses, proposed actions - in the assessors' words, to a
  file. `python tools/record.py self-assessment --ratings <file> --process <ID> ...
  --assessor "<name>" ... --summary <file> --as-of <date>`.

### 6. Follow-up
- For each weakness the assessors want acted on: a corrective action (`/project-status`
  or, where SUP.1 is in scope, `/quality-assurance`), a problem report
  (`/problem-resolution`), or the skill of the process for missing work.

## Writing

- Show the ratings file and the summary before the record is written, and ask.
- The record is written only by `record.py`; it is final.

## Checks before you finish

- The record exists and lists every practice of the processes; `consistency` holds every
  flag with its note.
- No sentence of the hand-over states a capability level or calls the result an
  assessment.

## Hand-over

1. Per process: the ratings side by side with the observations; the flags and their
   reasons.
2. Strengths and weaknesses as the assessors put them; the actions decided.
3. What the repository could not show and was answered by people, by name.
4. Next: the actions; `/process-gate` again before the assessment; the date of the
   assessment if one is planned.

## Do not

- Do not rate, suggest a rating, or present the band of an observation as a rating.
- Do not derive a capability level, and do not call the rehearsal an assessment.
- Do not record a reason the assessors did not give.
