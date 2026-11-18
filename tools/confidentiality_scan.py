#!/usr/bin/env python3
"""Leak scan for everything this repository would publish.

Three checks, all deterministic:

1. denylist   Terms from `.confidential/denylist.txt` (organization, people,
              internal document codes, hosts). One term per line, `#` for
              comments. A plain term matches case-insensitively as a whole
              word; `re:<pattern>` is a case-insensitive regular expression.
2. patterns   Built-in shapes of things that should not be published: e-mail
              addresses, URLs whose host has no dot (intranet), UNC paths.
3. verbatim   Any run of `--min-run` or more consecutive words that also occurs
              in a source document under `.confidential/sources/`. Catches both
              proprietary text and copyrighted model text. Official identifiers
              (`id` + `name` pairs in the catalogs under `aspice/`, plus lines in
              `tools/verbatim-allow.txt`) are exempt, alone or listed one after
              another; a run that continues past them is still reported.

`.confidential/` is git-ignored and never published; without it the tool runs
the pattern check only. Fill `.confidential/sources/` with
`python tools/extract_sources.py`.

Usage:
    python tools/confidentiality_scan.py [paths...] [--min-run 8]

With no paths it scans what git would publish (tracked plus untracked,
ignored files excluded). Exit code 0 = clean, 1 = findings.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONF = ROOT / ".confidential"
SKIP_DIRS = {".git", "input", ".confidential", "__pycache__", "node_modules"}

PATTERNS = [
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("intranet-url", re.compile(r"\b(?:https?|ftp|svn|file)://[A-Za-z0-9_-]+(?=[/:\s\"')>\]]|$)")),
    ("unc-path", re.compile(r"\\\\[A-Za-z0-9_.-]+\\[A-Za-z0-9_.$-]+")),
]
PATTERN_ALLOW = re.compile(
    r"@(example\.(com|org|net)|users\.noreply\.github\.com|anthropic\.com)$|://localhost$", re.I
)
WORD = re.compile(r"[a-z0-9]+")
NAME_LINE = re.compile(r"^\s*(?:-\s+)?name:\s*(.+?)\s*(?:#.*)?$")
ID_LINE = re.compile(r"^\s*(?:-\s+)?id:\s*(.+?)\s*(?:#.*)?$")
INLINE_PAIR = re.compile(r'\bid:\s*"?([^,"}]+)"?\s*,\s*name:\s*"?([^,"}]+)')


def words(text):
    return WORD.findall(text.lower())


def shingles(ws, n):
    return {" ".join(ws[i:i + n]) for i in range(len(ws) - n + 1)}


def read_text(path):
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data:
        return None
    return data.decode("utf-8", errors="replace")


def files_to_scan(paths):
    if paths:
        out = []
        for p in map(Path, paths):
            if p.is_dir():
                # a directory named explicitly is scanned even if it is normally skipped
                out += [f for f in p.rglob("*") if f.is_file() and not SKIP_DIRS & set(f.relative_to(p).parts)]
            else:
                out.append(p)
        return out
    try:
        res = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-co", "--exclude-standard", "-z"],
            capture_output=True, check=True,
        )
        names = [n for n in res.stdout.decode("utf-8").split("\0") if n]
        return [ROOT / n for n in names if not SKIP_DIRS & set(Path(n).parts)]
    except (OSError, subprocess.CalledProcessError):
        return [f for f in ROOT.rglob("*") if f.is_file() and not SKIP_DIRS & set(f.relative_to(ROOT).parts)]


def load_denylist():
    path = CONF / "denylist.txt"
    rules = []
    if not path.exists():
        return rules
    for raw in path.read_text(encoding="utf-8").splitlines():
        term = raw.strip()
        if not term or term.startswith("#"):
            continue
        if term.startswith("re:"):
            rules.append((term, re.compile(term[3:], re.I)))
            continue
        body = r"\s+".join(re.escape(part) for part in term.split())
        left = r"(?<![A-Za-z0-9])" if term[0].isalnum() else ""
        right = r"(?![A-Za-z0-9])" if term[-1].isalnum() else ""
        rules.append((term, re.compile(left + body + right, re.I)))
    return rules


def load_sources(n):
    """Map shingle -> source file name, for every source document."""
    index = {}
    src_dir = CONF / "sources"
    if not src_dir.is_dir():
        return index
    for src in sorted(src_dir.glob("*.txt")):
        for sh in shingles(words(src.read_text(encoding="utf-8", errors="replace")), n):
            index.setdefault(sh, src.name)
    return index


def load_allowed():
    """Official identifier phrases (as word tuples) that may be used verbatim."""
    phrases = []
    for cat in (ROOT / "aspice").rglob("*.yaml") if (ROOT / "aspice").is_dir() else []:
        last_id = ""
        for line in cat.read_text(encoding="utf-8", errors="replace").splitlines():
            pairs = INLINE_PAIR.findall(line)
            if pairs:
                for ident, name in pairs:
                    phrases += [name, ident + " " + name]
                continue
            m = ID_LINE.match(line)
            if m:
                last_id = m.group(1).strip("\"'")
                continue
            m = NAME_LINE.match(line)
            if m:
                name = m.group(1).strip("\"'")
                phrases += [name, last_id + " " + name]
    extra = ROOT / "tools" / "verbatim-allow.txt"
    if extra.exists():
        phrases += [l.strip() for l in extra.read_text(encoding="utf-8").splitlines()
                    if l.strip() and not l.startswith("#")]
    by_first = {}
    for p in phrases:
        ws = tuple(words(p))
        if len(ws) >= 2:
            by_first.setdefault(ws[0], set()).add(ws)
    return by_first


def verbatim_runs(text, index, allowed, n):
    """Yield (line, word_count, snippet, source) for each run shared with a source."""
    toks = []  # (word, line number)
    for lineno, line in enumerate(text.splitlines(), 1):
        toks += [(w, lineno) for w in words(line)]
    ws = [w for w, _ in toks]
    hit = [False] * len(ws)
    # positions that belong to an official identifier phrase
    official = [False] * len(ws)
    for i, w in enumerate(ws):
        for phrase in allowed.get(w, ()):
            if tuple(ws[i:i + len(phrase)]) == phrase:
                for j in range(i, i + len(phrase)):
                    official[j] = True
    origin = {}
    for i in range(len(ws) - n + 1):
        window = ws[i:i + n]
        # ignore windows that are mostly numbers / ID fragments
        if sum(1 for w in window if w.isalpha() and len(w) > 1) < n - 2:
            continue
        if all(official[i:i + n]):
            continue
        sh = " ".join(window)
        if sh in index:
            for j in range(i, i + n):
                hit[j] = True
            origin.setdefault(i, index[sh])
    i = 0
    while i < len(ws):
        if not hit[i]:
            i += 1
            continue
        j = i
        while j < len(ws) and hit[j]:
            j += 1
        snippet = " ".join(ws[i:j])
        src = next((origin[k] for k in range(i, j) if k in origin), "?")
        yield toks[i][1], j - i, snippet[:140] + ("..." if len(snippet) > 140 else ""), src
        i = j


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="*", help="files or directories (default: what git would publish)")
    ap.add_argument("--min-run", type=int, default=8, help="shared word run that counts as verbatim (default 8)")
    args = ap.parse_args()

    deny = load_denylist()
    index = load_sources(args.min_run)
    allowed = load_allowed()
    files = files_to_scan(args.paths)

    findings = []
    for f in files:
        text = read_text(f)
        if text is None:
            continue
        try:
            rel = f.resolve().relative_to(ROOT)
        except ValueError:
            rel = f
        for lineno, line in enumerate(text.splitlines(), 1):
            for label, rx in deny:
                if rx.search(line):
                    findings.append(("denylist", rel, lineno, label))
            for label, rx in PATTERNS:
                for m in rx.finditer(line):
                    if not PATTERN_ALLOW.search(m.group(0)):
                        findings.append(("pattern:" + label, rel, lineno, m.group(0)))
        for lineno, count, snippet, src in verbatim_runs(text, index, allowed, args.min_run):
            findings.append(("verbatim", rel, lineno, "%d words shared with %s: %s" % (count, src, snippet)))

    for kind, rel, lineno, detail in findings:
        print("%s:%d: [%s] %s" % (rel, lineno, kind, detail))
    print("scanned %d files | denylist terms: %d | source shingles: %d | findings: %d"
          % (len(files), len(deny), len(index), len(findings)))
    if not deny:
        print("note: no .confidential/denylist.txt - denylist check skipped")
    if not index:
        print("note: no .confidential/sources/*.txt - verbatim check skipped")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
