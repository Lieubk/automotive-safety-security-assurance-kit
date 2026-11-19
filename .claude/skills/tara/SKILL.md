---
name: tara
description: "Threat analysis and risk assessment of ISO/SAE 21434 for the item (clauses 9.3, 9.4 and 15): the item definition, assets with their cybersecurity properties, damage scenarios rated per impact category, threat scenarios with attack paths and feasibility, risk values from the risk matrix of the cybersecurity plan, the treatment decision for each risk, and the cybersecurity goals and claims that follow. Use when clause 9 or 15 is under scope.cybersecurity and the TARA is to be done, extended or redone after a change, when a vulnerability calls for a new threat scenario, or when the trace check reports COV-54 to COV-58."
argument-hint: "['item', 'assets', 'threats', 'rate', 'treat', a THR or AST ID, or nothing for the state of the TARA]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py next-id *)
---

# Threat analysis and risk assessment (ISO/SAE 21434 clauses 9.3, 9.4, 15)

Finds out what in the item is worth protecting, how it can be attacked, how bad the
damage for road users would be and how likely the attack is, and has the responsible
people decide what to do about each risk. The result is an `item-definition`, `asset`,
`damage-scenario` and `threat-scenario` items, and the `cybersecurity-goal` and
`cybersecurity-claim` items the treatment decisions call for. Ratings follow the
`tara_method` of the approved cybersecurity plan; the skill proposes, people rate.

| Subclause | What this skill does | Evidence it leaves |
|---|---|---|
| 21434:9.3 Item definition | describes boundary, functions, preliminary architecture and operational environment, from the system architecture where it exists | `item-definition` (WP-09-01) |
| 21434:15.3 Asset identification | proposes assets and damage scenarios from the item definition | `asset` (WP-15-02), `damage-scenario` (WP-15-01) |
| 21434:15.4 Threat scenario identification | proposes threat scenarios per asset and property | `threat-scenario` (WP-15-03) with `threatens`, `leads_to` |
| 21434:15.5 Impact rating | proposes a rating per impact category of the plan, with reasons; people rate | `impact`, `Impact rationale` (WP-15-04); COV-55 |
| 21434:15.6 Attack path analysis | works out attack paths from the entry points of the item | `attack_paths` (WP-15-05) |
| 21434:15.7 Attack feasibility rating | rates each path by the plan's approach, with the factors | `feasibility` per path and per scenario (WP-15-06); COV-56 |
| 21434:15.8 Risk value determination | reads the value from the plan's risk matrix | `risk_value` (WP-15-07); COV-57; `tara` |
| 21434:15.9 Risk treatment decision | lays out avoid, reduce, share, retain; the responsible person decides | `treatment`, `Treatment rationale`, `decision` (WP-15-08); COV-58 |
| 21434:9.4 Cybersecurity goals | writes goals for risks to reduce and claims for risks shared or retained; prepares their review | `cybersecurity-goal` (WP-09-03), `cybersecurity-claim` (WP-09-04); review records (WP-09-05) through `/review` |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. Neither clause 9 nor clause 15 under `scope.cybersecurity`: say that the project
   declares no TARA of its own and stop. A TARA received from the customer is an input:
   `/import-inputs` registers it unchanged.
3. Run `python tools/traceability.py status`, `python tools/traceability.py check` and
   `python tools/traceability.py tara`. Read `COV-27` for kind `cybersecurity` and
   `COV-54` to `COV-58`.
4. No approved cybersecurity plan with `tara_method`: say that ratings cannot be checked
   (`check` reports it as not assessed) and offer `/cybersecurity-plan` first. Item
   definition, assets and scenarios may be drafted before; ratings wait for the method.

## Steps

### 1. Item definition (9.3)
- Read `references/item-and-assets.md`. Draft from the system elements and interfaces
  (`matrix`, `show <SYE-ID>`) where SYS.3 exists, otherwise from what the user describes.
  Ask what lies outside the item and what the item relies on in its environment.
- One item definition per item. Assumptions about the environment are kept as such;
  they become requirements on the environment or claims later.

### 2. Assets and damage scenarios (15.3, 15.5)
- Propose assets from the item definition: commands and data on each interface that
  crosses the boundary, stored data and keys, the software and its configuration, the
  functions whose loss hurts someone. Give each its `properties` and `located_in`.
- Propose damage scenarios as consequences for road users. Propose a rating per impact
  category of the plan with the reason in its terms. The safety rating comes from the
  severity of the matching hazard where ISO 26262 applies: ask the person responsible
  for functional safety, do not derive it yourself.

### 3. Threat scenarios and attack paths (15.4, 15.6, 15.7)
- Read `references/threats-and-rating.md`. For each asset and property, work through the
  ways it can be lost by the threat model the plan names; each threat scenario
  `threatens` the asset and `leads_to` the damage it causes.
- Work out attack paths from an entry point of the item definition to the asset. Rate
  each by the plan's approach and record the factors. The scenario's `feasibility` is
  the highest of its paths.

### 4. Risk values (15.8)
- Run `python tools/traceability.py tara`: it shows impact, feasibility and the value of
  the plan's matrix. Write that value as `risk_value`. A value other than the matrix
  gives is a finding of `COV-57`, not a judgement call.

### 5. Treatment decisions and goals (15.9, 9.4)
- For each threat scenario, lay out the options with what each means here: avoid
  (remove the function or the entry point), reduce (a goal), share (with whom), retain
  (why acceptable). Ask the person responsible for cybersecurity to decide. Write
  `treatment` and `Treatment rationale`; a retained risk above `retain_up_to` needs
  `decision` with who accepted it, when and why.
- Reduce: draft a `cybersecurity-goal` that `addresses` the scenario. Share or retain:
  draft a `cybersecurity-claim` that `addresses` it, with `monitored_by`. Read
  `references/goals-and-claims.md` first.
- Hand the goals to `/cybersecurity-concept` once approved.

### 6. Review (WP-09-05)
- Status `in-review` when complete; `/review` with `item-definition.md`, `tara.md` and
  `cybersecurity-goal.md` under `.claude/docs/checklists/`. A review is the verification
  report of the goals.

## Writing

- Show each item before writing it and ask: "May I write THR-NNNN in
  `spec/cybersecurity/tara/`?" IDs from `python tools/record.py next-id <type>`; status
  `draft`.
- Ratings, risk treatment and acceptance are recorded as the named people state them.
  A proposal that nobody confirmed stays in the draft as a proposal, marked as such in the
  rationale.
- After a change of an approved TARA item, run `python tools/traceability.py impact <ID>`
  and name the goals, claims and requirements that become suspect.

## Checks before you finish

Run `python tools/traceability.py check` and `python tools/traceability.py tara`.
- `FORMAT`, `SCHEMA`, `LINK` on items written in this session: fix them.
- `COV-54` to `COV-58`: report each with what closes it. A warning that the TARA is not
  assessed means the plan's method is missing: name `/cybersecurity-plan`.
- Quote the figures of `tara`; do not count risk values from memory.

## Hand-over

1. The subclause table with what was done and what is open.
2. The threat scenarios by risk value with treatment and the goal or claim, as `tara`
   prints them.
3. Decisions still owed by people: ratings, treatment, acceptance of retained risks.
4. Next: `/review` for the TARA, goals and claims; `/cybersecurity-concept` for
   approved goals; `/vulnerability-management` where a weakness started this work.

## Do not

- Do not rate an impact, a feasibility or decide a treatment in anyone's name.
- Do not lower a rating to reach a lower risk value, and do not write a risk value other
  than the plan's matrix gives.
- Do not copy tables or rating criteria from ISO/SAE 21434 into items; the plan holds
  the project's own method.
- Do not edit a TARA item received from the customer: it is imported; questions go back
  as a `query`.
