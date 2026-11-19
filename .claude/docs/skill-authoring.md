# Writing skills and agents for this toolkit

Read [working-agreement.md](working-agreement.md) and [tools.md](tools.md) first. This
page says how a skill is built so that all of them behave the same way.
`python tools/skill_lint.py` checks the mechanical parts.

## Anatomy

```
.claude/skills/<name>/
  SKILL.md            what to do, step by step; at most about 160 lines
  references/*.md     detail read on demand: templates, rules, worked examples
.claude/docs/checklists/<work-product>.md    review checklists, shared by the
                                             authoring skill and the review skill
```

`SKILL.md` front matter:

```yaml
---
name: sw-requirements                 # equals the folder name
description: "<what it does, for which process, and when to use it>"
argument-hint: "[what the user may pass]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py *)
---
```

Right below the title of every `SKILL.md` and agent stands the line "Toolkit root:
`${CLAUDE_PLUGIN_ROOT}` ..." (copy it from any skill). Installed as a plugin, Claude Code puts
the toolkit's folder in its place, and the model finds `tools/`, `schema/` and
`.claude/docs/` there while it works in the user's project; in this repository it stays a
placeholder and the paths are relative to the repository. `tools/tests/test_plugin.py`
checks that the line is there.

Add `Agent` to `allowed-tools` only when the skill delegates. A skill that works with
the user states no `model` and no `effort`; see "Model and effort" below.
Do not run shell commands at load time; the first step runs them.

## Model and effort

The model is chosen by what a wrong answer costs, not by how hard the work looks.

| Work | Model, effort | Where |
|---|---|---|
| Independent judgement that people rely on: a missed contradiction becomes an approved defect | `opus`, `high` | `aspice-reviewer`, `software-architect`, `system-engineer` |
| Writing items or code from a given input and template, where a review follows | `sonnet`, `high` | `software-requirements-engineer`, `software-developer` |
| Deriving from a design and driving tools, turning their output into records | `sonnet`, `medium` | `unit-verification-engineer`, `software-test-engineer`, `system-test-engineer`, `configuration-manager`, `project-manager` |
| Reading tool output and explaining it; no question to the user, nothing written | `haiku`, `low` or `medium`, forked | `/trace-check`, `/next-step` |
| Working through a task with the user | the session's model | every other skill |

- Every agent states `model` and `effort` in its frontmatter. An agent runs in a
  context of its own, so its model costs nothing beyond its own work.
- A skill that works with the user states neither. In the conversation, `model` and
  `effort` switch the session for the rest of the turn: the new model reads the whole
  conversation again without cache, which costs more than it saves, and the user loses
  the model they chose.
- A skill that needs nothing from the conversation and asks the user nothing may run
  in a fork (`context: fork`, `background: false`) on a smaller model. It cannot ask
  questions there: where it would, it says what is missing and which skill provides it.
- A skill that starts an agent passes no model: the agent's file decides.
- Aliases only (`opus`, `sonnet`, `haiku`, `inherit`), never a version: a published
  toolkit must keep working when models change. Reducing cost is done by giving a
  model less to read - a re-review that reads what changed (`traceability.py diff`),
  a fork that does not carry the conversation - before it is done by a smaller model.
- `python tools/skill_lint.py` checks the values and that only forked skills set them.

## Sections of SKILL.md, in this order

1. **Title and purpose** - one paragraph, then a table
   `| Base practice | What this skill does | Evidence it leaves |` with one row per base
   practice of the process. A practice the skill does not cover gets a row that says
   so and names what covers it.
2. **Before you start** - the preconditions and what to say when one fails:
   - no `project.yaml`: stop, point to `/aspice-start`;
   - process not in `scope.processes`: stop, say it is out of scope;
   - required inputs missing or not approved: stop, name them and the skill that
     produces them.
   Then run `status` and `check` and read the result before reading any item.
3. **Steps** - numbered. Each step says what to do, which command gives the facts,
   what to ask the user, and what gets written. Detail lives in `references/`; the
   step says when to read which file.
4. **Writing** - IDs from `python tools/record.py next-id <type>`, the folder of the
   type, status `draft`, and the question asked before anything is written.
5. **Checks before you finish** - run `check`. Structural findings (`FORMAT`,
   `SCHEMA`, `LINK`) on items written in this session are fixed. Coverage findings
   are reported as they are, not explained away.
6. **Hand-over** - the closing report: the base practice table again with what was
   done, the evidence, and what is open; the next skill to run.
7. **Do not** - the boundaries specific to this skill.

## Rules for the text

- Write instructions, not descriptions: "Run ...", "Ask ...", "Write ...".
- A skill reads items by ID. It does not load a whole folder to "get an overview";
  `status`, `matrix` and `show` give the overview.
- Every process, base practice and work product ID comes from `aspice/3.1/`; every
  item type, attribute, section and link role from `schema/items.yaml`. Do not invent
  either. Do not quote the text of Automotive SPICE or of any other standard; refer to
  IDs and say what is expected in your own words.
- A skill never sets `status: approved`, never writes a review verdict on its own,
  and never edits an imported item or a final record. Approval goes through `/review`.
- Where a tool is needed that may be missing (compiler, analyser, coverage tool), the
  skill checks for it and reports `NOT ASSESSED` with the reason instead of skipping.
- Examples use the power window domain of `examples/power-window`. Nothing from a real
  project appears in a skill: no product, customer or person names, no identifiers.
- Plain Markdown, ASCII punctuation, lines up to about 100 characters.

## Checklists

`.claude/docs/checklists/<work-product>.md`:

```
# <Work product> review checklist
Applies to: <item types>    Supports: <BP IDs>
| ID | Check | How to check | Kind |
```

`Kind` is `script` (the trace engine or another tool answers it - name the rule or
command), `semantic` (needs reading and judgement; a model may propose, a person
confirms) or `accountable` (only a person can state it). A checklist has a version
line at the top; review records cite the checklist with its version. A check that is
added, removed or changes its meaning raises the version: the record tool refuses a
citation of another version, and the record keeps the hash of the checklist file it
was given, so that two records citing one version are known to mean one text.

A check answers from what the project holds: items, tool output, `project.yaml`. A
check that refers to a rule of the project names where it is found - normally under
`conventions` in `project.yaml` - and what applies when nothing is recorded there. A
check that can only be answered from a document the toolkit has no place for stops
every review that meets it: give the document a place first.

## Agents

A pattern in `tools`, such as `Bash(python tools/traceability.py *)`, is not enforced by
Claude Code: it grants the whole shell. The toolkit's `pre-shell` hook enforces it -
inside an agent whose `tools` name the shell only through patterns, every other
command, and every command with a shell operator, is refused. An agent that must not
write lists `disallowedTools: Write, Edit, NotebookEdit` as well.

`.claude/agents/<name>.md` front matter: `name`, `description` (when to use it),
`tools`. An agent is a role with a boundary:

- what it owns (item types and folders it may write);
- what it may only read;
- that it returns drafts and findings to whoever called it, and that questions for the
  user go back through the caller;
- that it follows the working agreement.

The reviewing agent has no write tools at all: independence is a property of what it
can do, not of what it is told.
