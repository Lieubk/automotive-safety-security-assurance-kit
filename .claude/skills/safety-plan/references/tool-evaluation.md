# Tool evaluation

Folder `plans/tools/`, type `tool-evaluation`, prefix `TEV`. The checklist is
`tool-evaluation.md`.

```yaml
id: TEV-0001
type: tool-evaluation
title: Host compiler for unit and integration tests
status: draft
tool: "gcc 13"
impact: TI2
detection: TD2
confidence: TCL2              # as the plan's tcl_determination gives it
asil: B
qualification_method: "validation of the tool for its use cases: compiling the unit tests and comparing with a second compiler"
evidence: "RUN-0001 and the runs with the Microsoft compiler (BLD-0001, BLD-0002)"
```

Sections:
- `Use cases` - what the tool does in the project, on which work products, and which
  errors it could introduce into them or fail to detect;
- `Classification rationale` - why this impact and this detection: which later activity
  would find an error of the tool, and how likely;
- `Qualification` - for TCL2 and TCL3: the method and its result.

`tool` is matched against the `tool` of build and analysis records (`COV-72`): the
first word or the whole name must appear there. The values above are invented; the
classification is the project's.
