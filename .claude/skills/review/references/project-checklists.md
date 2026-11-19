# Checklists of a project

The toolkit brings a checklist for every type it reviews. A project may have to apply
other criteria as well or instead: the customer prescribes checks in its supplier
requirements, or the organization has a review checklist in its standard process. Such
criteria become checklists of the project, kept under `checklists/` in the project root
and applied by `/review` exactly like the toolkit's: cited with their version, a result
per check, the file hash in the record.

## Three relations

| The project checklist | Its head says | A review of the type cites | The record says |
|---|---|---|---|
| covers a type the toolkit has no checklist for | nothing besides `Applies to:` | the project checklist | `checklist_source: project` |
| adds checks to a toolkit checklist | `Extends: <name> v<N>` | the project checklist; the checks of both get a result | `checklist_source: project`, `checklist_extends` with the toolkit checklist and its hash |
| is applied in place of a toolkit checklist | `Replaces: <name> v<N>` | the project checklist; only its checks get a result | `checklist_source: project`, `checklist_replaces` with the toolkit checklist |

Once the project extends or replaces a toolkit checklist, `tools/record.py review`
refuses to record a review that cites the toolkit checklist on its own.
`python tools/record.py checklists --type <type>` says what to cite for a type.

Extending is the normal case: the toolkit's checks carry the base practices and the
rules of the trace engine, the project adds what its customer or organization demands.
Replacing drops every check of the toolkit checklist, its `script` checks included,
for the type. Say so before the user decides it, and name the base practices the
toolkit checklist supports (its `Supports:` line): the project's checklist has to
cover them, or the process gate will find less to stand on.

## Format

The format of the toolkit's checklists (`.claude/docs/skill-authoring.md`,
"Checklists"):

```
# <Name> review checklist

Version 1. Applies to: `<item type>`. Extends: <toolkit checklist> v<N>.
Supports: <base practices or clauses>.

<Where the criteria come from, in a sentence: customer, organization, edition.>

## <Section>

| ID | Check | How to check | Kind |
|---|---|---|---|
| CUS-01 | ... | ... | semantic |
```

- The file name is the name it is cited by. It must differ from every toolkit checklist
  (`customer-software-requirements v1` beside the toolkit's `software-requirements v2`).
- `Version <n>` is raised whenever a check is added, removed or changes its meaning.
- `Applies to:` names the item types in backticks; `imported` for input acceptance.
- `Extends:` or `Replaces:` names one toolkit checklist with its present version.
- Check IDs are two to five capital letters, a hyphen and a number. In an extension
  they must differ from the IDs of the toolkit checklist; a prefix of the project's own
  (`CUS-`, `ORG-`) avoids clashes.
- `Kind` is `script`, `semantic` or `accountable`, as in the toolkit's checklists. A
  `script` check names the rule or command that answers it.

`python tools/traceability.py check` reports a project checklist that breaks one of
these rules as `CHECKLIST`, and no review can cite it until it is corrected.

## Turning a checklist the user hands over into one of the project

When the user has a checklist of the customer or the organization (a document, a
workbook, a list in a mail):

1. Ask which item types it is for and whether it is to extend or to replace the
   toolkit checklist of those types (`record.py checklists --type <type>`). The user
   decides; do not propose replacing.
2. Transcribe it, one row per check the source states. Do not add checks of your own,
   do not merge or drop any. A check the toolkit checklist already has is still
   transcribed when the user wants the customer's numbering visible; otherwise ask
   whether it can be left to the toolkit's check, and name that check.
3. Propose a kind per row (`semantic` for reading and judgement, `accountable` for what
   only a person can state, `script` only where a rule or command of the toolkit answers
   it) and let the user confirm each kind.
4. Write the "How to check" column from the source; where the source says nothing, say
   what a reviewer reads. A check that can only be answered from a document the project
   has no place for: ask where it is kept, and name that place in the row.
5. Show the whole file, ask "May I write `checklists/<name>.md`?", write it, run
   `python tools/record.py checklists` and quote its output.
6. Say that the plan that states the project's review criteria (the quality assurance
   plan, or the verification strategy of the level; plan checklist PLN-82) has to name
   this checklist; a plan that changes goes back to review.

The project repository may hold the customer's wording; it stays in the project and is
not copied into the toolkit or anything published.

## Changing a checklist of the project

- Raise `Version` when a check is added, removed or changes its meaning. Reviews
  recorded before keep the version and hash they cite; approvals do not become stale.
- When the toolkit brings a new version of a checklist the project extends or replaces,
  `check` reports `CHECKLIST` and reviews of the type are refused. Compare the two
  versions of the toolkit checklist, decide with the user whether the project's checks
  still hold, then change the version in the `Extends:` or `Replaces:` line, and raise
  the project checklist's own version if one of its checks changed.
