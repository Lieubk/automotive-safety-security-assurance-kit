#!/usr/bin/env python3
"""Extract plain text from confidential source documents for the leak scan.

Reads every file under `input/` and writes one UTF-8 text file per document
into `.confidential/sources/`. Both directories are git-ignored. The output
feeds the verbatim check of `tools/confidentiality_scan.py`.

Supported: .pdf (needs `pdftotext` on PATH, or the `pypdf` package),
.xlsx and .docx (standard library only), .txt / .md / .csv (copied).

Project identifiers: documents that describe a real product (design documents,
assessment evidence, code) are named in `.confidential/project-docs.txt`, one
file-name pattern per line, matched against the extracted file names. Every
code-like identifier that occurs in those documents and in no other source is
written to `.confidential/identifiers.txt`, which the leak scan checks. Lines
in `.confidential/identifiers-allow.txt` are left out (for standard names the
heuristic picks up by mistake).

Usage:
    python tools/extract_sources.py [--input input] [--out .confidential/sources]
"""
import argparse
import fnmatch
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


TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}")


def looks_like_code(token):
    """True for names shaped like code: snake_case, camelCase, or part numbers."""
    core = token.strip("_")
    if len(core) < 5:
        return False
    if "_" in core:
        return True
    if re.search(r"[a-z][A-Z]", core):
        return True
    return bool(re.fullmatch(r"[A-Z0-9]{6,}", core) and re.search(r"\d", core) and re.search(r"[A-Z]", core))


# Public names that are not project identifiers: C standard integer types, and
# `<Module>_<Function>` API names of AUTOSAR Classic basic software modules.
C_STANDARD = re.compile(r"^(u?int(_least|_fast)?(8|16|32|64)_t|u?intmax_t|u?intptr_t|size_t|ptrdiff_t|wchar_t|va_list)$")
AUTOSAR_MODULES = frozenset(
    "Adc BswM Can CanIf CanNm CanSM CanTp CanTrcv Com ComM Crc Csm CryIf Crypto Dcm Dem Det Dio Dlt DoIP E2E Ea "
    "EcuM Eep Eth EthIf EthSM EthTrcv Fee FiM Fls Fr FrIf FrNm FrSM FrTp Gpt Icu IoHwAb IpduM Lin LinIf LinSM "
    "LinTp LinTrcv Mcu MemIf Nm NvM Ocu Os PduR Port Pwm Rte SchM SecOC SoAd Spi StbM Std TcpIp Tm UdpNm Wdg "
    "WdgIf WdgM Xcp".split())
AUTOSAR_API = re.compile(r"^(%s)_[A-Za-z0-9]+$" % "|".join(sorted(AUTOSAR_MODULES)))
# Standard return values and error codes: E_OK, E_NOT_OK, STD_ON, RTE_E_TIMEOUT, E_OS_ACCESS, ...
AUTOSAR_CONSTANT = re.compile(
    r"^(E_OK|E_NOT_OK|NULL_PTR|STD_[A-Z]+|E_OS_[A-Z_]+|(%s)_E_[A-Z0-9_]+)$"
    % "|".join(sorted(m.upper() for m in AUTOSAR_MODULES)))


def candidates(text):
    for token in TOKEN.findall(text):
        if (token in AUTOSAR_MODULES or C_STANDARD.match(token) or AUTOSAR_API.match(token)
                or AUTOSAR_CONSTANT.match(token)):
            continue
        yield token
        if "_" in token:
            yield from (part for part in token.split("_") if part and part not in AUTOSAR_MODULES)


def harvest_identifiers(out):
    conf = out.parent
    cfg = conf / "project-docs.txt"
    if not cfg.exists():
        return None
    patterns = [l.strip() for l in cfg.read_text(encoding="utf-8").splitlines()
                if l.strip() and not l.startswith("#")]
    project, generic = [], set()
    for f in sorted(out.glob("*.txt")):
        text = f.read_text(encoding="utf-8", errors="replace")
        if any(fnmatch.fnmatch(f.name, p) for p in patterns):
            project.append(text)
        else:
            generic |= {c.lower() for c in candidates(text)}
    allow = conf / "identifiers-allow.txt"
    if allow.exists():
        generic |= {l.strip().lower() for l in allow.read_text(encoding="utf-8").splitlines() if l.strip()}
    found = {c for text in project for c in candidates(text)
             if looks_like_code(c) and c.lower() not in generic}
    (conf / "identifiers.txt").write_text(
        "# Generated by tools/extract_sources.py - do not edit, do not commit.\n"
        + "\n".join(sorted(found, key=str.lower)) + "\n", encoding="utf-8")
    return len(project), len(found)


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
    harvested = harvest_identifiers(out)
    if harvested:
        print("project identifiers: %d from %d project documents" % (harvested[1], harvested[0]))
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
