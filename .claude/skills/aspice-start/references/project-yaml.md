# project.yaml

One file in the project root. The trace engine reads `scope.processes`, `paths` and
`trace`, and `aspice.version` to find the process catalog. Everything else is for the
skills and for people. Keep every key, in this order. A value that is still open stays
empty; it is never filled with a guess.

## Template

```yaml
schema_version: 1
project:
  name: ""                 # what the team calls the project
  product: ""              # what is being developed, in a few words
aspice:
  version: "3.1"           # process catalog under aspice/<version>/
  target_level: 2          # 1, 2 or 3: capability level the processes in scope aim at
scope:
  role: ""                 # manufacturer | system-supplier | software-supplier |
                           # component-supplier | engineering-service
  processes: []            # what the team is responsible for: process IDs from
                           # aspice/3.1/index.yaml. Never written empty: the trace
                           # engine reads an empty list as "every process in scope"
  assessment_scope: []     # what an assessment will rate, when that differs from
                           # `processes`; empty when it does not differ or when no
                           # assessment is planned
  cybersecurity: []        # clauses of ISO/SAE 21434 the team is responsible for,
                           # as numbers 5 to 15 (iso-sae-21434/2021/catalog.yaml);
                           # empty: no rule of the standard runs
inputs:                    # what was received: one entry per document and version
  - level: ""              # stakeholder requirements | system requirements |
                           # system architecture | software requirements |
                           # software architecture | detailed design | code.
                           # Component descriptions and models: software architecture
                           # when they describe components and their interfaces,
                           # detailed design when they describe the inside of one
    source: ""             # name of the document or baseline as the deliverer calls
                           # it; /import-inputs copies it letter for letter into
                           # `imported.source` of every item registered from it
    version: ""            # quoted, so that 2.10 stays 2.10
    received: ""           # date received, "YYYY-MM-DD", quoted
    format: ""             # for example PDF, text export, ReqIF, ARXML, C sources
safety:
  highest_asil: QM         # QM | A | B | C | D: highest ASIL of any function of the
                           # product; empty while nobody has decided
security:
  relevant: false          # true when the product is cybersecurity relevant
conventions:               # the project's rules that reviews check against. Each value
                           # says what the rule is and where it is written; empty means
                           # that the toolkit default named here applies
  naming: ""               # default: "Naming" in .claude/rules/c-code.md
  design_limits: ""        # complexity, nesting, parameters, length of functions;
                           # default: the limits the first component design states
  design_notation: ""      # what the safety plan asks of the notation of the software
                           # design per ASIL; default: the unit format of the toolkit
  review_independence: ""  # who may review what, per ASIL; default: at least one
                           # reviewer who did not write the item
platform:
  architecture: autosar-classic   # or a short name of the platform used instead
  microcontroller: ""
  language: C99
  coding_guideline: ""     # guideline set and edition the code has to follow
toolchain:                 # name and version of each tool; empty = not decided yet
  compiler: ""
  static_analysis: ""
  unit_test: ""
  coverage: ""
  alm: ""                  # requirements or ALM tool the items are exchanged with
paths:
  items: [plans, spec, verification, records]   # folders scanned for item files
  source_roots: [src]      # code that must belong to a software unit (COV-11)
  generated: []            # patterns of generated code, for example "src/gen/**"
  third_party: []          # patterns of third-party code, for example "src/vendor/**"
trace:
  views_not_applicable: {} # view kinds the project does not need, as
                           # <kind>: "<reason>" (waiver of COV-25)
  internal_baselines: [working]   # baseline purposes that freeze nothing and need
                                  # no communication record (waiver of COV-26)
  derive_via_elements: false      # true: a software requirement derived from the
                                  # software element covers every system requirement
                                  # allocated to that element (weaker form of COV-05)
people:                    # who is accountable; review records need these names
  - name: ""
    roles: []              # for example project lead, requirements engineer,
                           # software architect, developer, tester, quality
                           # assurance, functional safety, configuration manager
```

## What each part is for

| Key | Read by | Effect |
|---|---|---|
| `scope.processes` | trace engine, every skill | Only the coverage rules of these processes run. A skill whose process is not listed stops. |
| `scope.cybersecurity` | trace engine, cybersecurity skills | Only the rules of ISO/SAE 21434 whose subclauses belong to these clauses run, and `COV-27` asks for the plans of their kinds. Unlike `processes`, an empty list means none. |
| `scope.assessment_scope` | skills and people | No effect on the checks. `/aspice-start` and `/next-step` warn while it names a process that `processes` does not. |
| `aspice.version` | `practices` command | Selects the catalog the base practices are read from. |
| `aspice.target_level` | people | A target, never a result. See "Target level" in `roles-and-processes.md`. |
| `inputs` | `/import-inputs`, `/next-step` | The record of what was received and when. An entry whose `source` appears in no item has not been registered yet. |
| `safety`, `security` | skills and people | The highest `asil` an item of this product can carry; whether `security_relevant` has to be considered at all. |
| `conventions` | review checklists, design and implementation skills | The one place a check looks for a rule of the project: SDD-05 (naming), SDD-09 and SUC-34 (limits), SDD-41 (notation), SUC-45 and UT-31 (independence). A value names the rule and where it is written; a rule that no document holds is written out in the value with who stated it and when. Empty means the toolkit default in the comment applies; a review then checks against that default and says so. The value is stated by the person accountable for the rule, never filled in by a skill. |
| `platform`, `toolchain` | skills and people | The platform vocabulary and the tools that design, implementation and verification work with. A tool that is named here but not available is reported as `NOT ASSESSED`, never skipped. |
| `paths.items` | trace engine | Folders scanned for item files. The folder of each type is fixed by `schema/items.yaml` and is not configurable. |
| `paths.source_roots`, `generated`, `third_party` | COV-11 | Every file under a source root needs exactly one owning software unit unless a pattern matches it. |
| `trace.views_not_applicable` | COV-25 | A missing software architecture view kind is accepted, with the reason given. |
| `trace.internal_baselines` | COV-26, baseline tool, write hook | A baseline with one of these purposes needs no communication record, may be taken while the check reports errors, and protects nothing against change. |
| `trace.derive_via_elements` | COV-05 | `false` or absent: every system requirement allocated to software needs a software requirement derived from it. `true`: one derived from the software element it is allocated to is enough. |
| `people` | skills and people | The names a review or a communication can be recorded with. A record never carries a name that the user has not given. |

## Rules for writing it

- `scope.processes` holds IDs exactly as in `aspice/3.1/index.yaml`, in the order of
  the V: SYS.1 to SYS.3, SWE.1 to SWE.6, SYS.4, SYS.5, then supporting, management
  and the rest. A process that is not in the index cannot be put in scope: the
  `practices` command would report it as not in the catalog.
- `assessment_scope` holds what the user states an assessment will rate. It is not
  derived from the role and not copied from `processes`.
- `inputs` is a history. A new version of a document is a new entry; the entry of the
  earlier version stays.
- Patterns in `paths.generated` and `paths.third_party` are matched against the path
  relative to the project root, with forward slashes; `*` also matches across folders.
- `trace.views_not_applicable` stays empty at the start. An entry is added in a re-run
  when the architecture work has shown that a view kind is not needed, with the reason
  the user gives.
- `trace.derive_via_elements` is `false` unless the user decides otherwise, and it only
  matters with SWE.1 in scope. It is the choice of the trace route from system level
  to software requirements. Say what `true` costs before recording it: a system
  requirement that no software requirement refers to is then no longer reported, as
  long as something is derived from its element.
- Names in `people` are names the user gave. A role without a person is left out, not
  filled with a placeholder.

## Changing an existing file

1. Read the file and run `python tools/traceability.py check`; keep the summary line.
2. Show the file and ask what is to change. Go through only the steps of the skill
   that concern the change, with the same confirm-each-answer rule. If the file lacks
   keys of the template (it was written by hand, or before a key existed), name them
   and ask for the answers; add a key empty rather than with a default the user has
   not confirmed. Other skills ask the user when a key is missing; they do not assume.
3. Before writing, say what the change does:

| Change | Say this first |
|---|---|
| A process is removed from `scope.processes` | Its coverage rules stop running and its skill refuses to work. Findings of that process disappear from `check` without having been resolved, and the items it produced stay in the repository unchecked. Quote `python tools/traceability.py practices <PROCESS>` before the change so that the user sees what goes silent. |
| A process is added | Its rules start running. Expect new findings at once: the plans it needs (COV-27) and gaps on items that already exist. If its upstream process is out of scope, it has a boundary of its own: see `starting-point.md`. |
| `assessment_scope` changes | Nothing changes in the checks. Repeat the warning of step 4 for every process that is rated but not in `processes`. |
| An input is added or has a new version | Add an entry; do not overwrite the earlier one. The content is registered with `/import-inputs`, which also shows what a new version affects. |
| A source root or pattern changes | COV-11 changes: files may gain or lose the obligation to belong to a unit. |
| `trace.derive_via_elements` is switched | `true` silences COV-05 for system requirements whose software element already has derived requirements; `false` brings those findings back. Quote the COV-05 lines of `check --all` before and after. |
| The highest ASIL changes | Items keep the `asil` they have. Lowering the value does not lower any item; items above the new value need a decision by the people accountable for safety. |
| A person leaves or joins | Review records already written keep the names they carry; they are final. |

4. Edit only the lines that change, run `check` again and compare the two summary
   lines: scope, and number of active coverage rules.

## Example

`examples/power-window/project.yaml` is a complete file in this format, for a software
supplier that is responsible for SWE.1 to SWE.4 and SUP.8 and received a system
requirements specification and a system architecture description. Read it before
writing the first file of a project.

It also shows what an honest file looks like when answers are open: the
microcontroller and the coding guideline set are empty, and `people` is an empty list
because the example has no reviewers. A real project names its people; a hand-over
lists every empty value as open.
