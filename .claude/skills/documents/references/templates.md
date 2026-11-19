# Customer templates

## Word

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

## Excel

Customers often hand over a workbook for test specifications and reports, TARA
worksheets or requirement lists - frequently an earlier report of theirs. It is filled
through a map file that the project keeps next to the workbook, for example
`templates/integration-test-report.yaml`, and names with `--template` or under
`documents.excel_maps` of `project.yaml`. The format is in the docstring of
`tools/excel_template.py`; in short:

| Key | What it says |
|---|---|
| `template` | the workbook, relative to the map file |
| `cells` | single cells and the placeholders they get: `{{title}}`, `{{project}}`, `{{kind}}`, `{{date}}`, `{{commit}}`, `{{baseline}}`, `{{draft}}` |
| `tables` | per sheet: `header_row`, `from: table` (a table of the document, chosen by its column names) or `from: items` with `types` (one row per item), and `columns` from the template's header to the source |
| `values` | per template header, the document's words in the template's words - for example `passed: Passed` for a drop-down list |
| `clear` | `table` (default: every column with a header is emptied below it, formulas stay), `mapped`, or `false` |

To write a map: `python tools/xlsx.py sheets <workbook>` shows the sheets; read the header
row of the sheet to fill and the table the document has (build it once as plain `xlsx`
and look at the sheet of the chapter). The tool refuses a map whose headers or columns do
not exist and names what is there. The filled workbook gets a sheet "Document
information" with the provenance, the DRAFT reasons and the items with their hashes. It
needs the package openpyxl; charts of a template are not kept, so look at the result
before sending it.
