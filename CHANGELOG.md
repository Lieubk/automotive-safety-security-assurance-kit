# Changelog

## 0.1.0 - 2026-11-19

The first release. Everything is new; this list says what the toolkit holds.

### Processes and standards
- Automotive SPICE 3.1: 32 processes in the catalog with base practices, outcomes, work
  products and rating dependencies in our own words; 26 carried by evidence structures and
  coverage rules, 23 of them with an authoring skill (the VDA scope, MAN.5, SPL.2, SYS.1).
- Automotive SPICE 4.0 from the draft 3.991 of 2023-06-06, which its publisher marks as not
  for assessments: 32 processes, every base and generic practice mapped onto the 3.1
  practices whose evidence it reads; chosen per project with `aspice.version`.
- ISO 26262:2018: decisions and evidence per clause of the parts in scope; safety plan,
  HARA, safety concept with ASIL inheritance and decomposition, safety analyses, tool
  evaluation, component qualification and proven in use argument, confirmation measures,
  safety case. Part 5 (hardware), part 12 and the organization-level clauses are out of scope.
- ISO/SAE 21434:2021: decisions and evidence per subclause; cybersecurity plan and interface
  agreement, TARA with the project's risk matrix, goals and claims, concept, cybersecurity
  events and vulnerability management, cybersecurity case and assessment record. Clause 5
  (organization) is out of scope.

### Toolkit
- 38 skills, 12 role agents with limited tools, 28 review checklists.
- Trace engine (`tools/traceability.py`): 55 item types, 24 link roles, 78 coverage rules,
  stale approvals, suspect links, impact, evidence per base practice and generic practice,
  per clause of ISO 26262 and per subclause of ISO/SAE 21434, progress, risks, problems,
  quality, suppliers, releases.
- Record writer (`tools/record.py`): reviews, baselines, builds, test and analysis runs,
  communication, quality, supplier, release, safety and cybersecurity records - written from
  tool output, never typed in.
- Documents (`tools/document.py`): 40 kinds as HTML, PDF, Word or Excel, neutral or in the
  customer's Word template or Excel workbook, with provenance and DRAFT marking.
- Exchange: ReqIF, Excel, AUTOSAR ARXML, REST connectors to Polarion, codebeamer and
  Jama Connect.
- Hooks: protection of inputs, final records and baselined items; a check after every write;
  a leak scan before commits of the toolkit.
- Packaging as a Claude Code plugin (`assurance-kit`) with its own marketplace.
- Two worked examples: a software supplier (`examples/power-window`) and a system supplier
  (`examples/door-control-unit`); a user guide (`docs/user-guide.md`).

### Known limits
- The Automotive SPICE 4.0 catalog follows a draft; it will be rebuilt from the released text.
- The ALM connectors were written from the public interface descriptions and tested against
  a simulated server, not against real servers.
- The toolkit rates no capability level and replaces no qualified tool; tests on hardware are
  specified and recorded here and executed elsewhere.
