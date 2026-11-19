---
name: risk-management
description: "Manage the risks of the project (Automotive SPICE MAN.5): the risk management plan with categories, rating scales and the acceptance threshold, risks identified throughout the project, rated and ranked, treated with owned actions, monitored with indicators, accepted by a named person, and followed by corrective action when treatment stalls. Use when MAN.5 is in scope and no approved plan of kind risk-management exists (COV-27), at each design decision, change request, problem report, supplier review and status meeting, at every reporting date, when the trace check reports COV-50 to COV-52, or when a risk is to be rated, treated, accepted or closed."
argument-hint: "['plan', 'identify', an RSK ID to take further, 'review', or nothing for the risks by exposure]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---

# Risk management (MAN.5)
> Toolkit root: `${CLAUDE_PLUGIN_ROOT}` - where this shows a placeholder instead of a folder, it is the repository you are in. The `tools/`, `schema/`, `aspice/`, `iso-26262/`, `iso-sae-21434/`, `examples/` and `.claude/docs/` named here and in the references lie in the toolkit root; run its tools from the project folder as `python "<toolkit root>/tools/<script>.py"`.

Looks ahead for events that could harm the project, ranks them, has the owner decide what
to do about each one and keeps checking whether it works. It never stops: risks are
found at the plan and again at every decision. The result is a `plan` of kind
`risk-management`, `risk` items moving through their states, `corrective-action` items
where treatment stalls, and the risk figures in the project status report.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| MAN.5.BP1 Establish risk management scope | asks which kinds of risk the project manages and what the organization's risk policy requires | `risk_categories`, section `Scope` of the plan |
| MAN.5.BP2 Define risk management strategies | writes with the user how risks are found, the rating scales, the acceptable level, the review rhythm and the escalation | `risk_scale`, `Approach` and `Criteria` of the plan |
| MAN.5.BP3 Identify risks | looks for risks where the project decides; writes each as a risk with cause, event and consequence | `risk` in state `identified`; `identified_in` |
| MAN.5.BP4 Analyze risks | proposes probability and impact with reasons; the owner rates; ranks by exposure | `probability`, `impact`, `Analysis`; state `analysed`; COV-50 |
| MAN.5.BP5 Define risk treatment actions | proposes treatment; the owner chooses, or a named person accepts the risk | `treatment` or `decision`; states `in-treatment`, `accepted`; COV-51 |
| MAN.5.BP6 Monitor risks | defines indicators with thresholds, records their values, reads the register by exposure | `indicators`; `traceability.py risks`; risk figures in the status report; COV-52 |
| MAN.5.BP7 Take corrective action | when treatment stalls or an indicator reaches its threshold, drafts a corrective action that addresses the risk | `corrective-action` with `addresses` |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. `MAN.5` not in `scope.processes`: say so and stop. Do not write risks that no rule
   will check.
3. Run `python tools/traceability.py status` and `python tools/traceability.py check`,
   then `python tools/traceability.py risks`. Read `COV-27` for kind `risk-management`
   and `COV-50` to `COV-52`.
4. `COV-27` open: do step 1 first. A risk that comes up before the plan exists is
   recorded in state `identified` and rated once the scales exist.

## Steps

### 1. Plan (BP1, BP2)
- Search `plans/` for `kind: risk-management`. If there is none or only a draft, read
  `references/plan-template.md`, ask the decisions listed there and draft the plan.
  Categories, scale, acceptable level, review rhythm, escalation and who may accept a
  risk are the user's decisions; the template's values are an example, not a default.

### 2. Identify (BP3)
- Read `references/risk-template.md`. Ask the user for the risks they see now, then look
  where risks come up, naming what each source shows, never a risk without a source:
  - the project plan and work breakdown: tight dates, a single owner for critical work,
    a commitment from outside, a milestone before its deliverables;
  - `design-decision` items: an open trade-off, a rejected alternative, a new technology;
  - change requests and their impact analysis; problem reports that are not resolved;
  - supplier reviews and imported inputs that are late or unclear;
  - status reports and meetings: late packages, overdue actions, staffing.
- Compare with the register first; a duplicate is not recorded twice, name the existing
  one. Propose, then write each accepted one in state `identified` with `category`,
  `owner` (as stated), `identified_at` and `identified_in`.

### 3. Analyse (BP4)
- Propose probability and impact on the plan's scales, with the reasons from the items;
  state what is judgement and what a tool shows. The owner rates. Write `Analysis`, set
  `probability` and `impact`, state `analysed`. Run `check` for `COV-50`.
- Rank: `python tools/traceability.py risks` lists the risks by exposure. Show it; do
  not calculate exposure from memory.

### 4. Decide and treat (BP5)
- For each risk above `acceptable_up_to`, propose options (avoid, reduce probability,
  reduce impact, transfer, accept) and ask the owner which. The choice is theirs.
- Treatment: write `treatment` with action, owner, due date and state `open`, and the
  indicators that show whether the risk grows or the treatment works, each with a
  threshold. An indicator can be simple - the answer to a query not received by the
  action's due date, with that date as threshold - but it is stated, not left out.
  Write `Treatment and monitoring`, state `in-treatment`.
- Acceptance: only a named person accepts a risk above the threshold. Record who, when
  and why in `decision`, state `accepted`. Within the threshold, state `accepted` needs
  no decision, but say so in `Analysis`.
- Not a risk of the project: state `rejected` with the reason.

### 5. Monitor (BP6)
- At every review date of the plan: run `python tools/traceability.py risks --as-of
  <date>`. Ask the owners for the current value of each indicator and the state of each
  action as they state it; write `value` and `as_of`, set action `state` and `done_on`.
- Re-rate a risk when its facts changed, with the reason in `Analysis`. Close it
  (`closed`) only when the owner states that it cannot occur any more or was handled.
- The risk status report is the project status report: `/project-status` carries the
  figures when risks exist. Say which risks the plan requires to be escalated.

### 6. Corrective action (BP7)
- Triggers in the output of `risks`: an overdue treatment action, an indicator whose
  value reached its threshold, a risk whose exposure rose. Ask the owner what to do;
  new treatment or another approach is the owner's decision.
- Draft a `corrective-action` with `addresses: [<RSK-ID>]` and hand it to
  `/project-status`, which keeps the register. A risk that shows on the status report
  without a decision about it is an open question to the project lead.

## Writing

- Show each risk, plan change or state change before writing it and ask: "May I record
  RSK-NNNN in `records/risks/`?" Ask again before each change of state.
- IDs: `python tools/record.py next-id risk`. Status of the plan is `draft`; it is
  approved only through `/review`. A risk is not reviewed; it moves through its states
  with the user. A risk is never deleted; a wrong one is `rejected` with the reason.
- Names in `owner`, `treatment` and `decision` are what the user states, never invented.

## Checks before you finish

Run `python tools/traceability.py check` and `python tools/traceability.py risks`.
- `FORMAT`, `SCHEMA`, `LINK` on items written in this session: fix them.
- `COV-50` to `COV-52`: report each with what closes it - a rating within the scales, a
  treatment or an acceptance by a named person, an indicator with a threshold.
- Quote the figures of `risks`; do not restate them from memory.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. The risks by exposure with state, owner, open and overdue actions and indicators at
   their threshold, as `risks` prints them.
3. Decisions still owed by people: ratings, treatment, acceptance, escalation.
4. Corrective actions proposed for `/project-status`.
5. Next: `/review` for the plan; `/project-status` for the report and the actions; the
   skill whose decision brought up a risk.

## Do not

- Do not rate a risk, accept it, choose its treatment or decide a corrective action in
  anyone's name. Propose, then record what the named person states.
- Do not invent a risk without a source in the items or a statement of the user.
- Do not lower a rating or an exposure to make a finding go away.
- Do not close a risk whose indicators still show it, or accept one above the threshold
  without a named person and a reason.
- Do not delete a risk. Do not mark an indicator value as measured when nobody measured it.
