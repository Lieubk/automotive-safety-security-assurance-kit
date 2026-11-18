#!/usr/bin/env python3
"""Extract plain text from confidential source documents for the leak scan.

Reads every file under `input/` and writes one UTF-8 text file per document
into `.confidential/sources/`. Both directories are git-ignored. The output
feeds the verbatim check of `tools/confidentiality_scan.py`.

Supported: .pdf (needs `pdftotext` on PATH, or the `pypdf` package),
.xlsx and .docx (standard library only), .txt / .md / .csv (copied).

Usage:
    python tools/extract_sources.py [--input input] [--out .confidential/sources]
"""
import argparse
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XL = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
WD = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def pdf_text(path):
    if shutil.which("pdftotext"):
        res = subprocess.run(["pdftotext", "-enc", "UTF-8", "-layout", str(path), "-"],
                             capture_output=True, check=True)
        return res.stdout.decode("utf-8", errors="replace")
    from pypdf import PdfReader  # optional dependency
    return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)


def xlsx_text(path):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(XL + "si"):
            shared.append("".join(t.text or "" for t in si.iter(XL + "t")))
    out = []
    for name in sorted(n for n in z.namelist() if re.match(r"xl/worksheets/[^/]+\.xml$", n)):
        for row in ET.fromstring(z.read(name)).iter(XL + "row"):
            cells = []
            for c in row.findall(XL + "c"):
                v = c.find(XL + "v")
                if c.get("t") == "s" and v is not None:
                    cells.append(shared[int(v.text)])
                elif c.get("t") == "inlineStr":
                    cells.append("".join(t.text or "" for t in c.iter(XL + "t")))
                elif v is not None and v.text:
                    cells.append(v.text)
            if cells:
                out.append("\t".join(cells))
    return "\n".join(out)


def docx_text(path):
    root = ET.fromstring(zipfile.ZipFile(path).read("word/document.xml"))
    return "\n".join("".join(t.text or "" for t in p.iter(WD + "t")) for p in root.iter(WD + "p"))


READERS = {
    ".pdf": pdf_text,
    ".xlsx": xlsx_text,
    ".docx": docx_text,
    ".txt": lambda p: p.read_text(encoding="utf-8", errors="replace"),
    ".md": lambda p: p.read_text(encoding="utf-8", errors="replace"),
    ".csv": lambda p: p.read_text(encoding="utf-8", errors="replace"),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--input", default=str(ROOT / "input"))
    ap.add_argument("--out", default=str(ROOT / ".confidential" / "sources"))
    args = ap.parse_args()

    src, out = Path(args.input), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    done = skipped = 0
    for f in sorted(p for p in src.rglob("*") if p.is_file()):
        reader = READERS.get(f.suffix.lower())
        if reader is None:
            print("skipped (unsupported type): %s" % f.relative_to(src))
            skipped += 1
            continue
        try:
            text = reader(f)
        except Exception as exc:  # one unreadable document must not stop the rest
            print("failed: %s (%s)" % (f.relative_to(src), exc))
            skipped += 1
            continue
        name = re.sub(r"[^A-Za-z0-9._-]+", "_", str(f.relative_to(src).with_suffix(""))) + ".txt"
        (out / name).write_text(text, encoding="utf-8")
        done += 1
    print("extracted %d documents into %s, skipped %d" % (done, out, skipped))
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
