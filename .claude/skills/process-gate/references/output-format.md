# Layout of the gate output

The same layout is used on screen and, when the user asks for it, in the file under
`reports/`. Keep the three kinds of statement apart: what a tool printed, what was read
and judged by the model, what a person stated.

## Template

```markdown
# Process gate - <process or "all processes in scope"> - <date>

This is a readiness check by the team itself. It is not an assessment and gives no
rating and no capability level.

Asked for by: <who>. Gate for: <baseline purpose | release | delivery | current state>.

## Facts

- check: `<summary line as printed>`
- Processes in scope: <list>. Coverage rules active: <n> of <m>.
- Not checked by any rule: <what the inactive rules would cover, in one line>.
- Units without code: <IDs from the `COV-10` lines "designed but not implemented"; or "none">.
- Items with open review findings: <IDs from the `COV-19` lines "left findings open"; or "none">.
- Open queries: <`QUERY` lines, or "none">.

## <PROCESS> - <verdict> (<n> PASS, <n> CONCERNS, <n> FAIL, <n> NOT ASSESSED)

| Practice | Engine state | Deterministic | Sample | Verdict | Basis |
|---|---|---|---|---|---|
| <ID> | <state as printed> | <PASS, FAIL, CONCERNS, NOT ASSESSED> | <result, or "-"> | <verdict> | <quoted line, items read, or statement> |

Findings counted for no practice: <the `check` lines without a bracket and what
follows from them; or "none">.

### Read for the sample

| Practice | Items read | Chosen because | Looked for | Found |
|---|---|---|---|---|

## Stated by people

| Practice | Statement | By |
|---|---|---|

## Capability level 2 (target level <n>)

<the tables of level-2.md, every line NOT ASSESSED by the toolkit; left out with one
sentence when the target level is 1>

## Next

| Cause | Items or practices | Skill |
|---|---|---|
```

## Example

Excerpt of a gate for SWE.4 on the power window example, gate for the current state.
The engine states are the output of `practices SWE.4`; the example is demonstration
data, and the gate says what that means.

```markdown
## Facts

- check: `73 items | scope: SUP.8, SWE.1, SWE.2, SWE.3, SWE.4 | 21 of 30 coverage rules active | 0 errors, 0 warnings, 0 on drafts`
- Processes in scope: SUP.8, SWE.1, SWE.2, SWE.3, SWE.4. Coverage rules active: 21 of 30.
- Not checked by any rule: system level as own work, integration and qualification
  tests, change requests.
- Units without code: none. Items with open review findings: none. Open queries: none.

## SWE.4 - FAIL

| Practice | Engine state | Deterministic | Sample | Verdict | Basis |
|---|---|---|---|---|---|
| SWE.4.BP1 | evidence present | PASS | no concern in 1 of 1 | PASS | PLN-0001 read: methods in order, regression rule, exit criteria per unit, coverage targets per ASIL |
| SWE.4.BP3 | evidence present | PASS | concern | CONCERNS | SAR-0001, `tool`: "compiler static analysis (/analyze), no coding-guideline rule set"; PLN-0001 declares this as a limitation. For a person to accept, with the reason |
| SWE.4.BP6 | evidence present | PASS | not an accountable review | FAIL | REV-0006, `reviewers`: "Demonstration data - no review by a person took place" |
| SWE.4.BP7 | no evidence yet | FAIL | - | FAIL | no `communication-record` exists; nobody was informed of the results |
```

The rows for SWE.4.BP2, SWE.4.BP4 and SWE.4.BP5 are left out of this excerpt; a real
report has one row per practice and the count per verdict in the heading.

## Rules for the text

- Quote tool output; do not retell it. Quote the words a concern rests on.
- A cell never stays empty: "-" means not applicable, and "Basis" says why.
- "PASS" in the column "Deterministic" means that no rule objects, nothing more.
- Write "stated by <who>" in front of everything a person said and nothing checked.
- No adjectives about the project. No sentence that sums the processes up into one
  overall result.
