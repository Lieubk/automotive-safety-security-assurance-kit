# Code this skill does not write, and code that carries an ASIL

## Generated code

A unit with `origin: generated` is produced by a tool from the model or configuration
named in `generated_from`. For such a unit:

- Do not write its files and do not edit them, not even to fix a warning or a typo.
  A correction is made in the model, in the configuration or in the generator
  settings, and the code is generated again.
- If the user runs the generator, report what they state: tool, version, the input
  with its version, and where the output went. If the generator is not available,
  the files are missing; a listed file that does not exist is reported by `COV-10`.
  Report that, do not hand-write a replacement.
- Check by reading that every function the unit item lists for other units exists in
  the generated files under the designed name and with the designed types. `COV-22`
  does not compare generated or third-party units with their design. A difference is
  a design problem or a generator configuration problem, never a manual edit.
- Registering generated files in `source_files` works as for handwritten ones: the
  design approval stays valid, and a review recorded with the code revision stores
  the hashes of the files, so that a later hand change or a new generation shows.
- Generated output must be reproducible: the same input and tool give the same files.
  If hand changes are found in generated files, report them as a finding.

Code that the platform tooling generates and that is no unit of the project (headers
of the runtime environment, configuration code of the basic software) is listed under
`paths.generated` of `project.yaml`. Handwritten units call it only through the
access functions the design names; they never copy from it and never include its
internal headers.

## Third-party and reused code

A unit with `origin: third-party` or `reused` is taken over as delivered, in the
version its source states:

- Do not modify it. A file that is changed is no longer what was delivered, and the
  verification that came with it no longer applies. If a change is unavoidable, that
  is a decision for the user and a change of the design item first (`origin`, and what
  re-verification follows).
- Adapt around it instead: a handwritten unit with its own design that wraps or
  converts, where the design provides one.
- The coding rules of the project are not applied to it; the rules still apply to
  every call the handwritten code makes into it (checked return values, ranges).
- Third-party files belong under a path matched by `paths.third_party`; how such code
  is verified is stated in the unit verification strategy.

The same care applies to fragments. Do not paste code from outside the project into a
handwritten unit - from another product, from the internet, from a library - unless
the user confirms that the project may use it. Such code is then written to the
project's rules like any other.

## Units with an ASIL

For a unit whose `asil` is A to D, the implementation shows the safety-related
behaviour of the design completely and visibly. The measures fall into three groups.

**1. What the design specifies, the code implements without gaps.**

- Every range check in `Error handling` exists, at the place the design names, before
  the checked value is used and before any stored data is changed.
- Every reaction is the designed one. Where the design says "refuse the step", the
  code does not limit the value and carry on; where it says "reverse", it does not
  merely report.
- Every state variable is handled for values outside its set, with the reaction the
  design gives (in AntiPinch: treated as IDLE, or reversed when an argument is out of
  range).
- Every result is limited to its designed range before it is stored or delivered.
- A failed call leaves exactly what the postcondition states. Compute into local
  variables and commit to the stored data at the end, so that "nothing changed" is
  true on every failure path.

**2. How the code is written.** These are the mainstream principles for the
implementation of safety-related units; ISO 26262-6, clause 8, is where the standard
treats them, and the project's safety plan says which apply from which ASIL. All are
part of `.claude/rules/c-code.md`:

- one entry and one exit per function;
- no dynamic memory; every variable initialised before use;
- one name means one thing; no shadowing;
- data is file-local; anything wider is in the design with its reason;
- pointers only where the design has one, checked before use, no arithmetic on them;
- no conversion that can change a value without an explicit, argued cast;
- no hidden data flow or control flow: a function changes only what its contract
  says, and nothing happens through macros or side effects in conditions;
- no `goto`, no recursion;
- arithmetic that cannot leave its type: widen first, then limit;
- loops with a bound that is visible in the code.

A rule that cannot be kept in one place is not dropped quietly: mark the place with
the rule, the reason and the alternative considered, and list it in the hand-over.
Accepting a deviation in a unit with an ASIL is a decision of the person the project
names for it.

**3. What the code does not add on its own.**

- No safety mechanism the design does not contain: no silent clamping, no extra
  plausibility check with a reaction of its own, no redundant copy of a variable. If
  you think one is needed, that is a design problem (`design-problems.md`); the people
  responsible for safety decide.
- No defensive branch that changes designed behaviour. A defensive branch the design
  does contain but a unit test cannot reach is marked with a comment that says why it
  cannot be reached, so that the coverage analysis has its reason. Whether the gap is
  accepted is decided in `/sw-unit-verify` by the person the strategy names.
- No call from a unit with an ASIL into code of a lower ASIL, and no shared variable
  with it, unless the design states it.
- Sections and partitions as `platform.memory_sections` says, with the mapping
  mechanism of the platform; no section pragma written directly into the unit.

**Tools.** The compiler and options used for the build check are the ones the product
is built with, or the difference is stated. Whether the project needs qualified tools
is decided there; this toolkit drives the tools it is given and reports what they
said.

**Hand-over.** For a unit with an ASIL say explicitly in the report: which designed
checks and reactions are where in the code (the comparison table has these rows),
which deviations from the coding rules exist, and which designed branches a test
will not reach. The code review of such a unit needs a reviewer who did not write it;
the form of the review per ASIL is in the project's plans. Every later change of the
code, however small, brings the unit back to that review: the check reports it as
`SUSPECT` until the new code has been reviewed.
