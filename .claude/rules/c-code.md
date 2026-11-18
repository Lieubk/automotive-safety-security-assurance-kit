---
paths:
  - "src/**"
  - "examples/**/src/**"
---

# C code of software units

Rules for hand-written C in safety-related ECU software. They apply to every file you
create or change under a source root.

- **Code follows a design.** A file under `src/` implements an approved `software-unit`
  item and is listed in its `source_files`. Names, signatures, constants and behaviour
  come from that item; `/sw-unit-implement` says how. If the design is wrong or
  incomplete, stop and take it back to its owner - do not repair it in code.
- **A change is seen.** Test runs, analysis runs and code reviews store the hash of
  every source file. After any edit the check reports the unit as `SUSPECT` and its
  runs under `COV-30` until the code has been reviewed (`/review`, with the code
  revision named) and verified (`/sw-unit-verify`) again. Say so when you change a file.
- **The project's guideline comes first.** `platform.coding_guideline` in
  `project.yaml` names the guideline set the code has to follow. Where it speaks, it
  wins; these rules are the default where it is silent. They are mainstream practice
  written for this toolkit, not the guideline set of any standards body, and keeping
  them does not show conformance to one.
- **Generated and third-party files** (`paths.generated`, `paths.third_party`) are
  never edited by hand and are not subject to these rules.
- **Check** names the first means that finds a violation: `compiler` (strict options,
  warnings as errors), `analyser` (static analyser, guideline checker or metric tool),
  `review` (a person reading the code against the design). A rule whose tool the
  project does not have falls to review.
- Identifiers and comments are written in English.

## Language subset

| ID | Rule | Why | Check |
|---|---|---|---|
| L1 | Write the language standard the project names (`platform.language`; C99 unless it says otherwise) without compiler extensions or vendor keywords. What the platform needs (interrupt, section, inline keywords) comes through its compiler abstraction macros. | The same source means the same to every compiler, analyser and reviewer. | compiler |
| L2 | No dynamic memory: no `malloc`, `free` or their relatives, no variable-length arrays. | Memory demand has to be known when the software is built. | analyser |
| L3 | No recursion, direct or through other functions; no `goto`, `setjmp` or `longjmp`. | Stack depth needs a bound, and control flow has to stay structured. | analyser |
| L4 | No floating point unless the unit design asks for it; floating-point values are never compared for equality. | It is costly on small targets, and rounding makes results hard to predict and to test. | analyser, review |
| L5 | Do not rely on undefined, unspecified or implementation-defined behaviour: signed overflow, shifts beyond the width, order of evaluation, size or sign of `int` and `char`. | Such code changes its meaning with compiler, option or target. | analyser |
| L6 | Use only the library functions the project has released; none for input and output, dynamic memory, program termination or signals. | Their timing, memory use and failure behaviour are outside the unit's control. | analyser |

## Headers and includes

| ID | Rule | Why | Check |
|---|---|---|---|
| H1 | Every header has an include guard and compiles on its own: it includes what its declarations need. | Nothing depends on the order of includes. | compiler |
| H2 | A header holds only what other units need. Types, constants and prototypes used by one source file stay in that file. | A small public surface is a small change impact. | review |
| H3 | No definition of an object or a function in a header. | A definition in a header is repeated in every file that includes it. | analyser |
| H4 | A source file includes its own header first. | Shows that the header is complete and that declaration and definition agree. | compiler, review |
| H5 | Include only what is used, and only what the unit design allows: the unit's own header, the platform's headers, and the headers of the units and interfaces the unit uses. | The includes are the dependencies of the unit; they have to match the design. | review, analyser |
| H6 | An external function or object is declared in exactly one header; no `extern` declaration in a source file. | One place to change, and the compiler catches a mismatch. | analyser |

## Types and conversions

| ID | Rule | Why | Check |
|---|---|---|---|
| T1 | Use the fixed-width types and standard return values of the platform's standard types header (`uint8`, `uint16`, `uint32`, `sint16`, `boolean`, `Std_ReturnType`) and do not redefine them. No `int`, `short`, `long` or plain `char` for numbers, and no `enum` type for data that is stored or crosses an interface. | Width and sign are then the same on every target and visible at the declaration; the size of an enumeration is not. | analyser |
| T2 | No implicit conversion that can change a value: no narrowing, no mixing of signed and unsigned. Convert with an explicit cast where the range is known, and say in a comment why it is. | Silent loss of range or sign. | compiler, analyser |
| T3 | Arithmetic must not leave its type: compute in a wider type or check first, then limit to the designed range. Wrap-around is used only where the design intends it, with a comment. | An overflow gives a wrong value without any sign of an error. | analyser, review |
| T4 | Bitwise operators and shifts take unsigned operands only; the shift count is smaller than the width of the promoted operand. | The result for signed operands depends on the implementation. | analyser |
| T5 | A `boolean` holds `TRUE` or `FALSE` only and takes no part in arithmetic. A condition is a comparison or a boolean: write `!= 0u`, `!= NULL_PTR`, `== TRUE`. | The intent stays visible; no accidental truth values. | analyser |
| T6 | No cast between pointer types or between pointer and integer; no cast that removes `const` or `volatile`. | Such casts switch off type checking and alignment rules. | analyser |
| T7 | A divisor is shown to be non-zero at the place of the division, by a check or by the range stated there. | Division by zero is undefined. | analyser, review |

## Constants and macros

| ID | Rule | Why | Check |
|---|---|---|---|
| K1 | No unexplained numbers: every value with a meaning is a named constant whose comment gives the physical value and the unit. Use the names of the unit design. | A bare number cannot be compared with the design. | review, analyser |
| K2 | A constant macro is parenthesised and typed by a cast or a suffix; unsigned constants end in `u`; no octal constants. | No surprise from promotion or precedence where the macro is used. | analyser |
| K3 | No function-like macro where a `static` function does the job. Where one is unavoidable, every parameter and the whole body are parenthesised and each parameter is evaluated once. | Macros escape type checking and hide side effects. | analyser |
| K4 | No `#undef`, no redefinition of standard or platform names, no identifier that starts with an underscore. | Reserved names and changing definitions make the code depend on include order. | analyser |
| K5 | Conditional compilation only for variants the design names, never to switch code off. | Every variant is a different program that has to be verified. | review |
| K6 | Whatever is only read is `const`: file-scope tables, and the objects that pointer parameters point to. | The compiler enforces the intent, and the data can be placed in read-only memory. | analyser |

## Functions

| ID | Rule | Why | Check |
|---|---|---|---|
| F1 | Every function has a prototype that is visible at its definition and at every call, with the same parameter names and types; `(void)` for no parameters. | The compiler can check every call. | compiler |
| F2 | Functions and file-scope objects that are used in one file only are `static`. | Nothing can be called or written from outside by accident. | compiler, analyser |
| F3 | One exit per function: a single `return` as its last statement. | Every path ends at the same place; coverage and review stay simple. | analyser |
| F4 | The value a function returns is used. Discarding it takes `(void)` and a comment with the reason. | An ignored error return is a lost error. | analyser |
| F5 | Parameters are not modified inside the function; copy to a local variable where a working value is needed. | The value passed in stays visible to the reader and in the debugger. | analyser |
| F6 | Every variable has a value before it is read: file-scope variables get an explicit initialiser, local variables one at the declaration or on every path. | Uninitialised data gives behaviour a test may not reproduce. | compiler, analyser |
| F7 | A function changes only what its designed contract says: its outputs and the data of its unit. | Hidden effects cannot be reviewed or tested from the interface. | review |
| F8 | Functions stay inside the limits of the project's design evaluation for complexity, nesting depth, number of parameters and length. A function over a limit is split, not excused. | A small function can be reviewed and covered completely. | analyser |

## Control flow

| ID | Rule | Why | Check |
|---|---|---|---|
| X1 | Braces around the body of every `if`, `else`, `for`, `while` and `do`, also around a single statement. | A statement added later cannot fall outside the body. | analyser |
| X2 | An `if ... else if` chain ends with `else`. An empty branch holds a comment that says why nothing is to be done. | Shows that the remaining case was considered. | analyser |
| X3 | Every `switch` has a `default`; every case ends with `break`; no fall-through. | Unexpected values are handled, and no case runs into the next. | compiler, analyser |
| X4 | Every loop has a bound that can be read from the code. No loop waits for hardware or for another context without a counter or a time limit. | Execution time needs an upper bound. | review, analyser |
| X5 | A `for` loop has one counter, changed only in the loop header; no `continue`, at most one `break`. | Termination is obvious. | analyser |
| X6 | One side effect per statement: no assignment in a condition, no `++` or `--` inside a larger expression, no comma operator, no side effect in the right operand of `&&` or `\|\|`. | When and whether the effect happens is not left to the reader's memory of the standard. | analyser |
| X7 | Parentheses show the grouping wherever operators of different kinds meet. | Precedence mistakes are silent. | analyser |
| X8 | No unreachable code, no unused variable, parameter or function, no code that is commented out. | Dead code hides defects and spoils the coverage analysis. | compiler, analyser |

## Pointers and arrays

| ID | Rule | Why | Check |
|---|---|---|---|
| P1 | A pointer that comes from outside the unit is checked against the null pointer before it is used, unless the precondition in the design rules null out. | A null dereference stops or corrupts the control unit. | analyser, review |
| P2 | Arrays are accessed by index, and the index is inside the array at that place by a check or a stated range. The size is a named constant or a `sizeof` expression; a function that receives an array also receives its length. | An access outside the array corrupts unrelated data. | analyser |
| P3 | No pointer arithmetic other than indexing; no comparison or subtraction of pointers into different objects. | Every access stays attributable to one object. | analyser |
| P4 | The address of a local variable does not outlive its function: it is neither returned nor stored in file-scope data. | The object is gone when the function returns. | analyser |
| P5 | No `union` to reinterpret data; bit fields only for hardware registers, never for stored data or data on an interface. | Layout and byte order are up to the implementation. | analyser |

## Shared data and interrupts

| ID | Rule | Why | Check |
|---|---|---|---|
| S1 | The data of a unit is `static` in its source file; other units reach it through functions. A global object exists only where the unit design has it with `scope: global`. | Every access then passes code that can check and protect. | analyser, review |
| S2 | Data that more than one execution context touches is accessed only under the protection the design names, and is read as one consistent copy that the function then works on. | A value that changes in the middle of a calculation gives results no test reproduces. | review |
| S3 | An exclusive area is entered and left in the same function on every path, holds a few statements, and contains no call out of the unit and no loop. | The lock time has to be short and provable. | review |
| S4 | Code at interrupt level is short and bounded: no loop over an amount of data that varies, no waiting, only services released for interrupt context. | Everything else waits while it runs. | review |
| S5 | `volatile` only for hardware registers and for data the design says changes outside the normal flow; such an object is read once into a local variable per use. | Each access to a volatile object may see a different value. | analyser, review |
| S6 | A function is called only from the context its design states; a function designed as re-entrant uses no unprotected static data. | Re-entrancy is a property of the design, not an accident. | review |

## Error handling and defensive measures

| ID | Rule | Why | Check |
|---|---|---|---|
| E1 | The result of every call that can fail is evaluated, and the reaction is the one the unit design gives. | An error nobody looks at turns into a wrong value later. | analyser, review |
| E2 | Arguments and inputs are checked where the design says so, before anything is changed. An invalid value leads to the designed reaction and is not used any further. | The unit must not turn bad input into bad output. | review |
| E3 | A result is limited to its designed range before it is stored or delivered. | Consumers rely on the stated range. | review |
| E4 | A state variable that holds a value outside its defined set is handled in the `default` branch, with the reaction the design gives. | Corrupted data has to lead to a defined state. | review, analyser |
| E5 | On failure a function leaves its outputs and the stored data exactly as its postcondition says: untouched, or set to the designed substitute value. | Callers rely on "nothing changed". | review |
| E6 | Every detected error is reported in the designed way: return value, status or diagnostic event. Status and data travel separately unless the interface defines an invalid value. | A swallowed error can be neither handled nor diagnosed. | review |
| E7 | A defensive branch that no test can reach carries a comment that says why it cannot be reached. | The coverage analysis needs the reason. | review |

## Comments

| ID | Rule | Why | Check |
|---|---|---|---|
| D1 | Each file starts with a comment that names the file, what the unit does and the design item it implements (`UNT-0001`); the header also names the component, the interfaces realized and the requirements implemented. | The trace from code to design is in the code. | review |
| D2 | Every function declared in a header has a contract comment: purpose, call context, each parameter with direction, unit and range, each return value with its condition. It says what the design says, in the markup of the project's documentation generator. | A caller gets the contract without reading the body. | review, analyser |
| D3 | Every constant, type, structure member and file-scope variable has a comment with meaning, unit, scaling and range. | Scaling errors are among the most frequent integration defects. | review |
| D4 | A comment in a body gives the reason: the intent of a step, why a wrap-around or a cast is right, why a branch is empty. It does not restate the statement, and it changes with the code. | A wrong comment is worse than none. | review |
| D5 | A deviation from one of these rules is marked at the place with the rule, the reason and who accepted it. | A deviation nobody can find cannot be reviewed. | review |

## What must never appear

| ID | Never | Why | Check |
|---|---|---|---|
| N1 | A function another file can call, a global variable or a source file that the approved unit design does not contain, or a signature that differs from the designed one. | Code beyond the design is behaviour nobody reviewed or tested. | trace check (`COV-11`, `COV-22`), review |
| N2 | `TODO`, `FIXME`, an empty function body, a placeholder value, code "for now". | Unfinished code that builds gets delivered. | review |
| N3 | Test code, debug output, trace hooks, or a branch that exists only for a test build. | The program that was tested must be the program that is delivered. | review |
| N4 | A silenced warning or analyser finding: a pragma, a changed option or a cast added only to make it go away, without a recorded and accepted justification. | The finding is still there; only the evidence is gone. | review |
| N5 | Secrets and personal data: keys, passwords, seeds, names or addresses of people, names of customers. | Source code is copied, delivered and published. | review |
| N6 | A hand change in a generated or third-party file. | It is lost with the next generation or delivery and voids the verification that came with the file. | review |

## Naming

Names are decided by the project's naming convention, not here. Find it through
`conventions.naming` in `project.yaml`, or `platform.coding_guideline`, or ask. A name the unit design gives is
used exactly as designed; if it breaks the convention, that is a finding against the
design. Where the code has to follow naming rules of the platform (names in the
component description, generated access functions), those come first.

A convention has to decide the points below. Where the project has decided nothing,
use the defaults - they are the ones the worked example follows - and say so in the
hand-over.

| Decision | Default |
|---|---|
| The module name of a unit, and which identifiers carry it as a prefix | one word in mixed case (`AntiPinch`); every identifier with file scope or external linkage carries it |
| Files and include guards | `<Module>.h`, `<Module>.c` in the folder of the component; guard `<MODULE>_H` |
| Functions | `<Module>_<VerbObject>`: `WindowPos_GetPosition`; file-local functions the same, told apart by `static` |
| Fixed names for recurring roles | `<Module>_Init`, `<Module>_Step` for the periodic function, `<Module>_Get<What>` for reading, `<Module>_On<Event>` for a callback |
| Types | `<Module>_<Name>Type`: `AntiPinch_StatusType` |
| Constants and macros | `<MODULE>_<NAME>` in upper case with underscores: `ANTIPINCH_ZONE_LIMIT` |
| Values of a set | `<MODULE>_<SET>_<VALUE>`: `ANTIPINCH_STATE_IDLE` |
| File-scope variables | `<Module>_<Name>`: `WindowPos_PositionValid` |
| Parameters, local variables, structure members | lower case with underscores: `new_pulses`, `pulse_count` |
| Physical units in names | a unit suffix on every value that is not in counts: `timestamp_us`, `speed_mm_s`, `HALLCAPTURE_MIN_INTERVAL_US` |
| Abbreviations | whole words; an abbreviation only when the project's glossary has it |
