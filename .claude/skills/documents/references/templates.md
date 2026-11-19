# Word templates

Without a template, `tools/document.py` writes a neutral Word document: the document
title, a table "Document information" (project, time, commit, uncommitted changes,
baseline, number of items), the chapters, and at the end the table of the items shown
with state and content hash.

## What a customer template brings

A `.docx` or `.dotx` file. Kept from it: the cover page and everything else it contains,
headers and footers, page layout, and the styles. The tool writes with these style
names; when the template lacks one, Word's default formatting is used for that part:

| Style | Used for |
|---|---|
| `Title` | the document title (only without a template; a template has its own cover) |
| `Heading 1` to `Heading 4` | chapters, items, sections of items |
| `List Bullet`, `List Number` | lists in the text of items |
| `Table Grid` | every table |

## Placeholders

Text in the template's paragraphs, tables, headers and footers is replaced:

| Placeholder | Replaced by |
|---|---|
| `{{title}}` | the title of the document kind |
| `{{project}}` | `project.name` of `project.yaml` |
| `{{kind}}` | the document kind, for example `software-architecture-description` |
| `{{date}}` | the date of generation |
| `{{commit}}` | the commit the document was generated from |
| `{{baseline}}` | the baseline and its tag, or `none` |
| `{{content}}` | a paragraph of its own: the place where the generated content goes |

Without `{{content}}` the content follows the template's own content. A placeholder
must stand in one paragraph; formatting inside a paragraph that holds one is reduced to
that of its first run.

## What to ask the customer

- the template file, and whether its document number and revision history are kept by
  the customer or filled in by the project;
- whether a document is expected per work product (SAD, SDD) or one document for
  several;
- whether diagrams are to be pictures: the Word version carries the Mermaid source of a
  diagram; the HTML version draws it.
