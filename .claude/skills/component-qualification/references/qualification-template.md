# Component qualification

Folder `spec/software/qualification/`, type `component-qualification`, prefix `CQL`.
The values are invented.

```yaml
id: CQL-0001
type: component-qualification
title: Fixed-point filter library 2.4 for the speed estimation
status: draft
version: "2.4.0"
method: "analysis of the library documentation against SWR-0003; requirements-based tests of the filter functions used, with boundary and invalid inputs"
evidence: "the library manual 2.4 (received 2026-03-02); RUN-0007 with UT-0031 to UT-0036"
result: qualified-with-restrictions
restrictions: "only the first-order filter is used; inputs are limited to the range of SWR-0003 by the caller"
links:
  qualifies: [CMP-0007]
```

Sections:
- `Specification` - functions used, interfaces, configuration, resources, the assumptions
  of use the documentation states;
- `Qualification` - what was verified against which requirement, how, with which result;
- `Restrictions` - what the users of the component must keep to.
