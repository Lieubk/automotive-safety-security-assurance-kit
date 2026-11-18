# Design decision item

File: `spec/decisions/<ID>.md`. Attributes and sections are those of type
`design-decision` in `schema/items.yaml`. A decision of the software architecture has
`level: software`. The example project holds one (ADR-0001, the measuring principle of
the window speed). The example below is a second decision of the same architecture,
written the way `/sw-architecture` would draft it.

```markdown
---
id: ADR-0002
type: design-decision
title: Where the reversal request overrides the movement command
status: draft
level: software
links:
  concerns: [CMP-0002, CMP-0005, IFC-0003, IFC-0004]
---

## Context

While the reversal request is set, the bridge has to be driven open whatever the
comfort functions ask for, starting no later than 5 ms after the request (SWR-0007,
ASIL B). The comfort functions are in WindowCmd, which is reused QM software running
every 20 ms. Somewhere between the detection and the bridge the request has to win over
the movement command. Where this happens decides which components lie on the path of
the safety function and which ASIL they need.

## Evaluation criteria

1. **Independence**: no component below ASIL B lies on the path from the Hall sensor
   to the bridge. Weight 3.
2. **Reaction time**: bridge commanded "opening" within 5 ms after the request is set
   (SWR-0007). Weight 3.
3. **Reuse**: WindowCmd and MotorDrive of platform release 3.2.0 stay unchanged.
   Weight 2.
4. **Resources** against the shares assigned to the application (SYE-0001). Weight 1.

## Alternatives

**A - Override in MotorDrive.** MotorDrive reads the reversal request (IFC-0003) in
every 5 ms cycle and ignores the movement command while it is set.

**B - Override in WindowCmd.** WindowCmd reads the detection status and changes its
movement command to "opening"; MotorDrive only carries out movement commands.

**C - Arbiter component.** A new component in the 5 ms task selects between the
movement command and the reversal and passes the result to MotorDrive.

| Criterion | A - in MotorDrive | B - in WindowCmd | C - arbiter |
|---|---|---|---|
| 1 Independence | path is WindowPos, AntiPinch, MotorDrive, all ASIL B - fulfilled | WindowCmd lies on the path and would have to be raised to ASIL B - not fulfilled | fulfilled if the arbiter is developed to ASIL B |
| 2 Reaction time | same 5 ms cycle - fulfilled | next 20 ms cycle of WindowCmd, then one 5 ms cycle: up to 25 ms - not fulfilled | same 5 ms cycle - fulfilled |
| 3 Reuse | both unchanged; the reused MotorDrive has the reversal input - best | WindowCmd changed and verified again - not fulfilled | both unchanged, but one more component to develop and one more call in the chain - acceptable |
| 4 Resources | nothing added - best | nothing added - best | budget for one more component - acceptable |

Weighted, with 2 points for fulfilled or best, 1 for acceptable and 0 for not
fulfilled: A reaches 3x2 + 3x2 + 2x2 + 1x2 = 18 points, B reaches 0 + 0 + 0 + 2 = 2,
C reaches 3x2 + 3x2 + 2x1 + 1x1 = 15.

## Decision

Alternative A, override in MotorDrive. B fails the two criteria that carry the safety
function. C meets them but adds a component whose only duty MotorDrive already has.

## Consequences

- MotorDrive is ASIL B and is the only component that commands the bridge (CMP-0005).
- WindowCmd stays QM. Its movement command (IFC-0004) can be QM as well, because no
  value of it keeps the window closing against a reversal request.
- WindowCmd learns of a reversal only afterwards, from the detection status
  (IFC-0003), and withdraws its command within its own 20 ms cycle.
- The argument holds only if WindowCmd cannot overwrite data of the ASIL B components.
  That separation is provided by the partitioning of the door module, which the
  customer owns; it is stated in `execution_context` of CMP-0002 and has to be
  confirmed by the customer.
```

In a draft, `Decision` and `Consequences` are written only when the user has decided.
Until then the item ends after `Alternatives`, and the hand-over lists it as open.

A consequence that someone outside the project has to confirm, like the last one above,
is not left as a sentence: it becomes a `query` item `about` the input concerned (here
SYE-0001), and the consequence names the query by its ID. The layout of a query is in
`architecture-guidance.md`.

## What is needed when

| Attribute or section | Needed | What to write |
|---|---|---|
| `id`, `type`, `title`, `status` | always | `title`: the question that is decided |
| `level` | always | `software` for the architecture |
| `Context` | before review | the question, why it has to be decided now, what it fixes for others |
| `Evaluation criteria` | before review | the criteria, each decidable, with weight or rank |
| `Alternatives` | before review | each alternative described, and assessed against each criterion |
| `Decision` | before approval | the chosen alternative and why, as the user decided it |
| `Consequences` | before approval | what follows for components, interfaces, views and other parties; what is accepted |
| `links.concerns` | every decision | the components, interfaces and views the decision shapes; for an ASIL decomposition also every requirement whose ASIL is lower than that of its source |

## Writing the sections

**Context.** State the question so that someone outside the project understands why
it matters. Refer to the requirements and system items that force it, by ID.

**Evaluation criteria.** Take them from the ranked list agreed with the user before
the design started. Each criterion says what is needed and how one can tell: a value
from a requirement, a budget, a count of changed components. "Maintainability" alone is
not a criterion; "a different sensor changes one component only" is. Use only criteria
that can tell the alternatives apart.

**Alternatives.** At least two that were really considered. An alternative that nobody
would choose does not count. Describe each in two or three sentences, then assess every
alternative against every criterion in one table, with the reason in the cell. Numbers
are derived in the cell or by reference to an item, not asserted. If a scoring scheme
is used, state it; the scheme supports the reasoning and does not replace it.

**Decision.** One alternative, and the reason in terms of the criteria. The person who
decides is the user or whoever the user names. A decision the skill only proposes is
labelled as a proposal in the conversation and is not written into the item.

**Consequences.** What the choice costs and what others must now do: new interfaces,
budget rows, constraints on a supplier, assumptions that someone has to confirm. Each
consequence that concerns an item appears in that item as well.

## When a decision item is needed

- A choice between structures: how the software is cut, which component owns a duty.
- A principle that fixes interfaces or load: measuring method, task model, where data
  is stored, how tasks exchange data.
- Make, reuse or buy for a component, including taking over an existing architecture
  or platform unchanged. "Given by the platform" is itself the decision: record what
  was checked before adopting it and which risks come with it.
- Coexistence of elements with different ASIL: how the lower ones are kept from
  disturbing the higher ones.
- An item that is to carry a lower ASIL than its source: an element below a requirement
  allocated to it, or a requirement below the requirement it is derived from. `COV-23`
  accepts this only when an approved decision `concerns` that item, so the decision
  names every element and every requirement whose ASIL is lowered. It documents the
  decomposition: which requirements replace the original one, which elements fulfil
  them, why these are independent of each other, and who agreed. The people responsible
  for functional safety take this decision; the skill prepares it and never takes it.

Not every choice needs an item. A choice with no real alternative, or one that shapes
only the inside of a component, is explained in `Purpose` or left to the detailed
design.
