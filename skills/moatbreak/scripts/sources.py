#!/usr/bin/env python3
"""Source manifest check for the Moatbreak skill. Standard library only.

Every reference screenshot in teardown/screens/ and every proof copy in
teardown/proof/ must say where it comes from and when: a row in
teardown/sources.csv with the page's URL and the day it was read. The same
holds for the sources table of teardown/recon.md: one page per row, with its
own URL and read-on date. This check lists every file without such a row,
every row whose URL or date is missing or wrong, and every row whose file is
gone, and exits 1 if there is one. It never fetches anything: the browser
tools of the session capture the pages, this only checks the paper trail.

Origin and licence: see NOTICE.md and LICENSE.

    python3 sources.py teardown --as-of 2026-10-17
    python3 sources.py teardown --as-of 2026-10-17 --lang de --out teardown/sources.md
    python3 sources.py teardown --json

teardown/sources.csv (from templates/sources.csv; extra columns are ignored):

    file      the path inside teardown/, e.g. screens/S07-booking-1440.png or
              proof/2026-10-17-pricing.pdf
    url       the public page it shows (http or https)
    read_on   the day it was read or captured, YYYY-MM-DD, not after --as-of
    notes     optional: viewport, plan, logged in with the user's own account, ...

teardown/recon.md, if it exists, needs its sources table under "## Sources"
(or "## Quellen") with the columns URL and "read on" (or "gelesen am"). The
URL cell holds exactly one http(s) URL: plain, <url> or [text](url). No URL,
two URLs, a search query, a search engine's result page or "see
visibility.md" in that cell is a failure: list each page read, each result
of a search too, as its own row, and copy URLs from other files instead of
pointing to them. An empty table fails as well. The table is read as GitHub
Markdown renders it: outer pipes optional, "\\|" inside a cell, code blocks
skipped, every table under the heading with a URL and a read-on column.

Files starting with "." are skipped. A row read more than 90 days before
--as-of is listed as old (not a failure): recheck it before a claim that
rests on it is used again.
"""

import argparse
import csv
import datetime as _dt
import json
import os
import re
import sys

FOLDERS = ("screens", "proof")
OLD_DAYS = 90
URL = re.compile(r"^https?://[^\s/]+\.[^\s]+$")
RECON = "recon.md"
RECON_HEAD = re.compile(r"^##\s+(sources|quellen)\s*$", re.I)
READ_ON = ("read on", "read_on", "gelesen am")
CELL_URL = re.compile(r'^(?:<([^<>\s]+)>|\[[^\]]*\]\(((?:[^()\s]|\([^()\s]*\))+)'
                      r'(?:\s+"[^"]*")?\)|(\S+))$')
LINKS = re.compile(r"https?://(?:(?!https?://)[^\s<>()\[\]|])+", re.I)
SEARCH = re.compile(r"^https?://(?:[\w-]+\.)*(?:google\.[a-z.]+/search|bing\.com/search|"
                    r"yahoo\.com/search|brave\.com/search|ecosia\.org/search|duckduckgo\.com/|"
                    r"startpage\.com/|qwant\.com/)", re.I)
SEP = re.compile(r"^:?-+:?$")

TEXT = {
    "en": {
        "title": "# Sources of screenshots, proof copies and recon.md",
        "summary": "{files} files in {folders}; {rows} rows in sources.csv{recon}. As of {as_of}.",
        "recon_rows": "; {n} rows in the sources table of recon.md",
        "ok": "Every file has its URL and date.",
        "ok_recon": "Every file and every row of the sources table in recon.md has its URL "
                    "and date.",
        "bad": "{n} problems. Fix them before a screenshot, a proof copy or a recon source "
               "backs a claim.",
        "no_manifest": "No sources.csv: copy templates/sources.csv to {path} and add a row "
                       "(file, url, read_on) for every file below.",
        "nothing": "No files in {folders} and no sources.csv: nothing to check.",
        "problems": "## Problems",
        "untracked": "{file}: no row in sources.csv",
        "no_url": "line {line}: {file} has no URL (http or https): '{value}'",
        "no_date": "line {line}: {file} has no date like 2026-10-17: '{value}'",
        "future": "line {line}: {file} was read on {value}, after {as_of}",
        "gone": "line {line}: {file} is not in teardown/",
        "twice": "line {line}: {file} is already on line {first}",
        "recon_none": "recon.md has no sources table with rows: add one under '## Sources' "
                      "from templates/recon-map.md (columns URL and read on), one page per row",
        "recon_url": "recon.md line {line}: '{value}' is not one page URL. Give every page "
                     "you read its own row with its own URL: for a web search, the result "
                     "pages you read; for another file, copy its URLs here",
        "recon_urls": "recon.md line {line}: {count} URLs in one row. Give every page its "
                      "own row with its own URL and read-on date",
        "recon_search": "recon.md line {line}: '{value}' is a search result page, not a "
                        "source. Give every result page you read its own row with its own URL",
        "recon_no_date": "recon.md line {line}: no read-on date like 2026-10-17: '{value}'",
        "recon_future": "recon.md line {line}: read on {value}, after {as_of}",
        "old_h": "## Read more than {days} days before {as_of}",
        "old_note": "Not a failure. Recheck the page before a claim that rests on it is used "
                    "again.",
    },
    "de": {
        "title": "# Quellen der Screenshots, Belegkopien und von recon.md",
        "summary": "{files} Dateien in {folders}; {rows} Zeilen in sources.csv{recon}. "
                   "Stand {as_of}.",
        "recon_rows": "; {n} Zeilen in der Quellentabelle von recon.md",
        "ok": "Jede Datei hat ihre URL und ihr Datum.",
        "ok_recon": "Jede Datei und jede Zeile der Quellentabelle in recon.md hat ihre URL "
                    "und ihr Datum.",
        "bad": "{n} Probleme. Erst beheben, dann darf ein Screenshot, eine Belegkopie oder "
               "eine Recon-Quelle eine Aussage stützen.",
        "no_manifest": "Keine sources.csv: templates/sources.csv nach {path} kopieren und für "
                       "jede Datei unten eine Zeile (file, url, read_on) anlegen.",
        "nothing": "Keine Dateien in {folders} und keine sources.csv: nichts zu prüfen.",
        "problems": "## Probleme",
        "untracked": "{file}: keine Zeile in sources.csv",
        "no_url": "Zeile {line}: {file} hat keine URL (http oder https): '{value}'",
        "no_date": "Zeile {line}: {file} hat kein Datum wie 2026-10-17: '{value}'",
        "future": "Zeile {line}: {file} wurde am {value} gelesen, nach dem {as_of}",
        "gone": "Zeile {line}: {file} liegt nicht in teardown/",
        "twice": "Zeile {line}: {file} steht schon in Zeile {first}",
        "recon_none": "recon.md hat keine Quellentabelle mit Zeilen: unter '## Quellen' eine "
                      "aus templates/recon-map.md anlegen (Spalten URL und gelesen am), eine "
                      "Seite pro Zeile",
        "recon_url": "recon.md Zeile {line}: '{value}' ist nicht genau eine Seiten-URL. Jede "
                     "gelesene Seite bekommt eine eigene Zeile mit eigener URL: bei einer "
                     "Websuche die gelesenen Ergebnisseiten, bei einer anderen Datei deren "
                     "URLs hierher kopieren",
        "recon_urls": "recon.md Zeile {line}: {count} URLs in einer Zeile. Jede Seite bekommt "
                      "eine eigene Zeile mit eigener URL und eigenem Lesedatum",
        "recon_search": "recon.md Zeile {line}: '{value}' ist eine Suchergebnisseite, keine "
                        "Quelle. Jede gelesene Ergebnisseite bekommt eine eigene Zeile mit "
                        "eigener URL",
        "recon_no_date": "recon.md Zeile {line}: kein Lesedatum wie 2026-10-17: '{value}'",
        "recon_future": "recon.md Zeile {line}: am {value} gelesen, nach dem {as_of}",
        "old_h": "## Mehr als {days} Tage vor dem {as_of} gelesen",
        "old_note": "Kein Fehler. Die Seite erneut prüfen, bevor eine Aussage, die darauf "
                    "beruht, wieder verwendet wird.",
    },
}


class SourcesError(Exception):
    pass


def _rel(path):
    p = path.strip().replace("\\", "/").lstrip("./")
    return p[len("teardown/"):] if p.startswith("teardown/") else p


def files_in(root):
    out = []
    for folder in FOLDERS:
        base = os.path.join(root, folder)
        for dirpath, dirnames, names in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
            for n in sorted(names):
                if not n.startswith("."):
                    out.append(os.path.relpath(os.path.join(dirpath, n), root).replace(os.sep, "/"))
    return out


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        header = fh.readline()
        fh.seek(0)
        delim = max(",;\t", key=header.count) if header.strip() else ","
        reader = csv.DictReader(fh, delimiter=delim)
        if reader.fieldnames is None:
            return []
        fields = [(f or "").strip().lower() for f in reader.fieldnames]
        for need in ("file", "url", "read_on"):
            if need not in fields:
                raise SourcesError("%s has no '%s' column: file,url,read_on,notes"
                                   % (path, need))
        rows = []
        for i, raw in enumerate(reader, start=2):
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()
                   if not isinstance(v, list)}
            if any(row.values()):
                row["line"] = i
                rows.append(row)
    return rows


def _cells(text):
    """The cells of a table line as GitHub renders them: one outer pipe on
    each side is optional, an escaped pipe stays inside its cell."""
    t = text[1:] if text.startswith("|") else text
    t = t[:-1] if t.endswith("|") and not t.endswith("\\|") else t
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", t)]


def _sep(text):
    return "|" in text and all(SEP.match(c) for c in _cells(text))


def recon_rows(path):
    """The rows of every table with a URL and a read-on column under the
    sources heading of recon.md, as (line, URL cell, read-on cell)."""
    with open(path, encoding="utf-8-sig") as fh:
        lines = [line.strip() for line in fh.read().splitlines()]
    rows, inside, fence, cols, head = [], False, False, None, 0
    for i, text in enumerate(lines, start=1):
        if text.startswith(("```", "~~~")):
            fence = not fence
        elif fence:
            continue
        elif re.match(r"#{1,2}\s", text):
            inside, cols = bool(RECON_HEAD.match(text)), None
        elif not text:
            cols = None
        elif not inside or "|" not in text:
            continue
        elif i < len(lines) and _sep(lines[i]) and not _sep(text):
            # a header: () skips a table without a URL or read-on column
            names = [c.lower() for c in _cells(text)]
            day = [names.index(c) for c in READ_ON if c in names]
            cols, head = ((names.index("url"), day[0]) if "url" in names and day else ()), i + 1
        elif cols and i != head:
            cells = _cells(text)
            if any(cells):
                rows.append((i,) + tuple(cells[c] if c < len(cells) else "" for c in cols))
    return rows


def check(root, as_of):
    manifest = os.path.join(root, "sources.csv")
    files = files_in(root)
    rows = load(manifest) if os.path.isfile(manifest) else None
    problems, old, seen = [], [], {}
    for r in rows or []:
        f = _rel(r.get("file", ""))
        if f in seen:
            problems.append({"kind": "twice", "line": r["line"], "file": f, "first": seen[f]})
            continue
        seen[f] = r["line"]
        if not f or not os.path.isfile(os.path.join(root, f)):
            problems.append({"kind": "gone", "line": r["line"], "file": f or "-"})
        if not URL.match(r.get("url", "")):
            problems.append({"kind": "no_url", "line": r["line"], "file": f,
                             "value": r.get("url", "")})
        try:
            day = _dt.datetime.strptime(r.get("read_on", ""), "%Y-%m-%d").date()
        except ValueError:
            problems.append({"kind": "no_date", "line": r["line"], "file": f,
                             "value": r.get("read_on", "")})
            continue
        if day > as_of:
            problems.append({"kind": "future", "line": r["line"], "file": f,
                             "value": day.isoformat()})
        elif (as_of - day).days > OLD_DAYS:
            old.append({"file": f, "read_on": day.isoformat(), "url": r.get("url", "")})
    untracked = [f for f in files if f not in seen]
    problems = [{"kind": "untracked", "file": f} for f in untracked] + problems
    recon = os.path.join(root, RECON)
    table = recon_rows(recon) if os.path.isfile(recon) else []
    if os.path.isfile(recon) and not table:
        problems.append({"kind": "recon_none"})
    for line, cell, read_on in table:
        links = set(LINKS.findall(cell))
        m = CELL_URL.match(cell)
        url = next((g for g in m.groups() if g), "") if m else ""
        if len(links) > 1:
            problems.append({"kind": "recon_urls", "line": line, "count": len(links),
                             "value": cell})
        elif not URL.match(url):
            problems.append({"kind": "recon_url", "line": line, "value": cell})
        elif SEARCH.match(url):
            problems.append({"kind": "recon_search", "line": line, "value": cell})
        try:
            day = _dt.datetime.strptime(read_on, "%Y-%m-%d").date()
        except ValueError:
            problems.append({"kind": "recon_no_date", "line": line, "value": read_on})
            continue
        if day > as_of:
            problems.append({"kind": "recon_future", "line": line, "value": day.isoformat()})
        elif (as_of - day).days > OLD_DAYS:
            old.append({"file": "%s:%d" % (RECON, line), "read_on": day.isoformat(),
                        "url": url})
    return {"as_of": as_of.isoformat(), "files": len(files), "manifest": rows is not None,
            "rows": len(rows or []),
            "recon": len(table) if os.path.isfile(recon) else None,
            "problems": problems, "old": old}


def render(result, root, lang="en"):
    T = TEXT.get(lang, TEXT["en"])
    folders = ", ".join("%s/" % f for f in FOLDERS)
    as_of = result["as_of"]
    if lang == "de":
        y, m, d = as_of.split("-")
        as_of = "%s.%s.%s" % (d, m, y)
    out = [T["title"], ""]
    has_recon = result["recon"] is not None
    if not result["files"] and not result["manifest"] and not has_recon:
        return "\n".join(out + [T["nothing"].format(folders=folders)]) + "\n"
    recon = T["recon_rows"].format(n=result["recon"]) if has_recon else ""
    out.append(T["summary"].format(files=result["files"], folders=folders,
                                   rows=result["rows"], recon=recon, as_of=as_of))
    if not result["manifest"] and result["files"]:
        out += ["", T["no_manifest"].format(path=os.path.join(root, "sources.csv"))]
    ok = T["ok_recon"] if has_recon else T["ok"]
    out += ["", T["bad"].format(n=len(result["problems"])) if result["problems"] else ok]
    if result["problems"]:
        out += ["", T["problems"], ""]
        out += ["- " + T[p["kind"]].format(as_of=as_of, **p) for p in result["problems"]]
    if result["old"]:
        out += ["", T["old_h"].format(days=OLD_DAYS, as_of=as_of), "", T["old_note"], ""]
        out += ["- %s (%s) %s" % (o["file"], o["read_on"], o["url"]) for o in result["old"]]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("teardown", nargs="?", default="teardown", help="the teardown folder")
    ap.add_argument("--as-of", metavar="YYYY-MM-DD", help="the day of the check (default today)")
    ap.add_argument("--lang", choices=sorted(TEXT), default="en")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", help="write the report (or the JSON) here")
    args = ap.parse_args(argv)
    try:
        as_of = (_dt.datetime.strptime(args.as_of, "%Y-%m-%d").date() if args.as_of
                 else _dt.date.today())
    except ValueError:
        print("sources: --as-of must be YYYY-MM-DD", file=sys.stderr)
        return 2
    if not os.path.isdir(args.teardown):
        print("sources: %s is not a folder" % args.teardown, file=sys.stderr)
        return 2
    try:
        result = check(args.teardown, as_of)
    except (SourcesError, OSError, UnicodeDecodeError) as exc:
        print("sources: %s" % exc, file=sys.stderr)
        return 2
    text = (json.dumps(result, indent=2, ensure_ascii=False) + "\n" if args.json
            else render(result, args.teardown, args.lang))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    else:
        sys.stdout.write(text)
    return 1 if result["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
