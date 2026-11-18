# From the unit item to header and source

How each element of an approved `software-unit` item becomes C code, and how the result
is compared with the design. Complete pairs of design and code:
`examples/power-window/spec/software/design/UNT-0001.md` with
`examples/power-window/src/windowpos/HallCapture.h` and `.c`, and the other two units.

## What comes from where

| In the unit item | In the code |
|---|---|
| `source_files`, or for a unit without code the `Files` column of `Static structure` in its component design | the files to create, at exactly these paths; no others |
| `title`, `id`, links | the file comment: unit ID, component, interfaces realized, requirements implemented |
| `functions` entry with `category: public`, `scheduled` or `callback` | one declaration in the header, one definition in the source, external linkage |
| `functions` entry with `category: local` | one `static` prototype and one `static` definition in the source; not in the header |
| `arguments`, `returns` (or `return_type`) | the prototype: see "The prototype" below |
| `preconditions`, `postconditions`, `errors`, `call_context`, `reentrant` | the contract comment in the header; the checks and the failure paths in the body |
| `data` entry with `scope: file` | a `static` variable in the source with the designed type and an explicit initialiser equal to `initial` |
| `data` entry with `scope: global` | a definition in the source and an `extern` declaration in the header; only when the design says so |
| `protection` of a variable | every access is inside the named protection, or in the single context the design names |
| types and constants in `Behavior` | `typedef`s and named constants with the designed names, members and values; in the header when an argument, a return value or another unit needs them, otherwise in the source |
| numbered steps, formulas, state descriptions in `Behavior` | the function bodies |
| `Error handling` table | one check per row at the place the row names, with the designed reaction and report |
| `platform` | calls of the named services and nothing beyond them: exclusive area enter and exit, access functions of the runtime environment, diagnostic and memory services |
| `uses` links | the includes: the unit's own header, the platform headers, the headers of the units and interfaces it uses |

What the item does not contain is not written. What the item contains is written
completely: an entry of `functions` without a definition is as much a difference as a
function without an entry.

## The prototype

An entry of `functions` determines one prototype:

- name: `name`, character for character;
- return type: `return_type`, or the one `type` given in every entry of `returns`; a
  single entry with `type: void` means `void`;
- parameters: the entries of `arguments` in their order, each as `type` followed by
  `name`; a `type` that holds a pointer or `const` is taken as written
  (`"const HallCapture_SnapshotType *"`); `arguments: []` means `(void)`;
- `static` for category `local`, no storage class otherwise.

Design (UNT-0001):

```yaml
  - name: HallCapture_GetSnapshot
    category: public
    arguments:
      - {name: snapshot, direction: out, type: "HallCapture_SnapshotType *", description: "..."}
    returns:
      - {type: Std_ReturnType, value: E_OK, meaning: "the snapshot was written"}
      - {type: Std_ReturnType, value: E_NOT_OK, meaning: "snapshot is a null pointer"}
```

Code:

```c
Std_ReturnType HallCapture_GetSnapshot(HallCapture_SnapshotType *snapshot);
```

If the entry does not determine one prototype - the return type is missing, the entries
of `returns` name different types, an argument has no type - the design is incomplete.
Do not guess; see `design-problems.md`. Such an entry is also one the check cannot
compare with the code.

## The header

Order, as in the worked example:

1. file comment: file name, one line on what the unit does, "Design item: UNT-0001.
   Component: WindowPos (CMP-0003).", the interfaces it realizes, the requirements it
   implements, then scaling and units that hold for the whole file;
2. include guard;
3. includes: the platform's standard types header, and only headers the declarations
   below need;
4. exported constants, each with its physical value and unit in the comment;
5. exported types, every member commented with meaning and range;
6. exported function declarations, each with its contract comment.

The contract comment restates the design entry for the reader of the header, in the
markup of the project's documentation generator: what the function does, its call
context, every parameter with direction, unit and range, every return value with the
condition under which it is returned. It adds nothing the design does not say. If you
want to write a sentence that is not in the design, either it is implementation
freedom and belongs in the source, or the design is missing something.

Nothing else is in the header: no `static` function, no variable definition, no
constant that only the source uses.

## The source

Order, as in the worked example:

1. file comment with the unit ID and a pointer to the header for the contract;
2. includes: the unit's own header first, then what the bodies need;
3. file-local constants and types;
4. file-local variables, each with a comment giving meaning, unit and range, and one
   comment that says from which context they are accessed and under which protection;
5. prototypes of the file-local functions, each with a short comment;
6. definitions, in the order of the design.

Writing the bodies:

- Follow the steps of `Behavior` in their order where the order matters, and keep the
  names of the design for every constant, state and variable.
- Put each check of `Error handling` where its row says ("before anything else",
  "before the pulse data is read"), and make the failure path leave exactly what the
  postcondition states: outputs untouched or set to the designed value, stored data
  unchanged.
- Implement arithmetic as the design specifies it: width, order of operations,
  rounding, saturation, intended wrap-around. Where the design says "as unsigned 16 bit
  subtraction", write the cast that makes it one and say in a comment why the wrap is
  intended.
- A value outside the set of a state variable is handled as the design says, in the
  `default` branch.
- Access shared data only as `protection` and `platform` state: enter the exclusive
  area, copy, leave, then work on the copy.
- Comments in the body give the reason a reader cannot see in the statement: "First
  edge: there is no earlier edge to measure an interval against."

## What the developer may decide, and what not

| Free | Fixed by the design |
|---|---|
| names of local variables and of parameters of functions the design does not name | names and signatures of all designed functions |
| order of statements where no result depends on it | order of checks, of updates and of calls where the design gives one |
| the form of a condition or loop, within the coding rules | every value, limit, rounding and saturation |
| how a designed function is split into file-local helpers | what is visible outside the file |
| comments | error reactions and what is reported |

A file-local helper the design does not name is allowed when it only structures a
designed function - to stay inside the complexity limit, for example - and adds no
behaviour. It is `static`, follows the naming convention, and is listed in the
hand-over, so that the owner of the design can decide whether the item should name
it. Where the design lists its local functions, as all units of the worked example
do, implement those and report every further one.

## Registering the files

The unit item says which files hold its code. A unit that was designed before it had
code has no `source_files`; the check reports it as "designed but not implemented"
(`COV-10`), and a file under a source root that no unit lists as an error (`COV-11`).
So the files are registered as soon as they are written:

```yaml
source_files:
  - src/antipinch/AntiPinch.h
  - src/antipinch/AntiPinch.c
```

- Add the attribute after `origin`, with the paths relative to the project root, and
  change nothing else in the item, the status included.
- `source_files` is not part of the content hash of the item (`schema/item-format.md`).
  The design approval stays valid, and a unit inside a baseline needs no change
  request for this entry. Any other change to the item is a design change and is not
  made here.
- The design is approved; the code is not yet reviewed. The check says so with
  `CONSISTENCY` on the unit ("a review of the code against the design is not
  evidenced") until a review with the unit as its subject has been recorded with the
  code revision. Only then does the record store the hash of every listed file.
- With code registered, the verification rules of the unit are no longer pending:
  `COV-12`, `COV-28`, `COV-29` and `COV-30` are errors until `/sw-unit-verify` has
  tested and analysed the code.
- When the code changes later, the item is not touched. The check reports `SUSPECT` on
  the unit ("the code is no longer the code that was reviewed") until it has been
  reviewed again, and `COV-30` until the runs have been repeated.

## Comparison

Once the files are registered, `COV-22` of the trace check compares the design with
the code:

| It reports | From |
|---|---|
| a designed function of category public, scheduled or callback that is not defined | the listed `.c` files |
| a function defined without `static` that the design lacks | the listed `.c` files |
| parameter types, in their order, that differ from `arguments` | the first declaration or definition of each designed function, `local` ones included, when every argument has a `type` |
| a return type that differs from the design | the same, when the design states one return type |

Types are compared as written, apart from spacing: `const`, `*` and the type names
have to be the same words in the same order.

It does not compare, and reading has to:

- parameter names;
- linkage against category: a `public` function defined `static`, a `local` one
  declared in the header;
- the declarations in the header against the definitions, and that the header holds
  nothing beyond the design;
- variables against `data`, types and constants against `Behavior`;
- behaviour, error handling, protection, use of platform resources;
- any function whose types the design leaves open.

Write the result of the reading as a table, one row per element:

| Design element | Design | Code | Result |
|---|---|---|---|
| `UNT-0001#HallCapture_GetSnapshot` | public; `Std_ReturnType`; (`HallCapture_SnapshotType *snapshot`) | `HallCapture.h:90`, `HallCapture.c:85`: same return type, same parameter | equal |
| `UNT-0001#HallCapture_OnEdge` | callback; `void`; (`uint32 timestamp_us`) | `HallCapture.h:78`, `HallCapture.c:52`: same | equal |
| data `HallCapture_PulseCount` | `uint16`, file, initial 0 | `HallCapture.c:25`: `static uint16 ... = 0u` | equal |
| constant `HALLCAPTURE_MIN_INTERVAL_US` | 400 us | `HallCapture.h:31`: `((uint32)400u)` | equal |

Rows to write:

- every function: category against linkage (`static` or not, declared in the header or
  not), parameter names, and that declaration and definition agree; types and return
  type are quoted from the check where it compared them, and read where it could not;
- every variable: type, `static` or not, initial value;
- every type and constant of `Behavior`: members, values;
- every error row of `Error handling`: where the check is in the code;
- every resource of `platform`: where it is used;
- the reverse direction: every function, file-scope variable, type and exported
  constant in the code that the design does not contain.

The result of a row is `equal`, `different` (with what differs) or `not in design`.
A row that is not `equal` is either corrected in the code or reported as a design
problem. The table is a semantic check made by reading: it is shown with the lines it
is based on and becomes evidence only when a reviewer confirms it. Say in the table
which rows rest on the check ("no `COV-22` finding") and which on reading.
