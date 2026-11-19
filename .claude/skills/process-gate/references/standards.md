# Gating clauses of ISO/SAE 21434 and ISO 26262

The standards have no base practices. Their unit is the clause (ISO 26262) or the
subclause (ISO/SAE 21434), and the engine observes each the same way it observes a base
practice: `python tools/traceability.py safety [PART] --json` and
`python tools/traceability.py clauses [CLAUSE] --json` print, per clause, the decision of
the plan, the evidence (items of the types and plan kinds that carry its work products,
with state and hash), the open findings of the rules behind it, and a `state`.

The engine decides the state in this order: no entry in the plan -> `not decided`; the
plan leaves it to another party or says it does not apply -> `not ours`; the schema
holds nothing for it -> `no evidence structure`; any error -> `findings open`; no item
-> `no evidence yet`; an item not approved or final -> `evidence not settled`; any
warning -> `warnings open`; otherwise `evidence present`.

| State | Verdict | What the report says |
|---|---|---|
| `not decided` | FAIL | the plan (safety or cybersecurity) has no entry for it; `/safety-plan` or `/cybersecurity-plan` |
| `not ours` | not gated | the decision and its rationale, quoted from the plan; the party that answers for it |
| `findings open` | FAIL | the `error` lines, quoted |
| `no evidence yet` | FAIL | the types that would carry the evidence and the skill that produces them |
| `evidence not settled` | CONCERNS or FAIL | as for base practices: FAIL when the gate is for a release, a delivery or a final baseline |
| `warnings open` | CONCERNS | the `warning` lines, quoted; who can accept them |
| `no evidence structure` | NOT ASSESSED by the toolkit | that the toolkit holds nothing for it; the user's statement about evidence elsewhere, marked as such |
| `evidence present` | PASS for the deterministic part | then the sample: read one item per work product against its checklist; the verdict is the worse of the two |

The verdict of a part (ISO 26262) or clause (ISO/SAE 21434) is the worst verdict of its
gated clauses or subclauses. A clause whose plan entry is `performed` but whose work
lies in a later phase is FAIL for a gate of that phase's end, and is reported with the
phase - the plan says when.

A gate per clause prepares a functional safety assessment or a cybersecurity
assessment; it does not replace them, and it does not judge whether a measure is
sufficient - that is the confirmation measures' and the assessors' work.
