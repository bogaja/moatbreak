#!/usr/bin/env python3
"""Source manifest check for the Moatbreak skill. Standard library only.

Every reference screenshot in teardown/screens/ and every proof copy in
teardown/proof/ must say where it comes from and when: a row in
teardown/sources.csv with the page's URL and the day it was read. This check
lists every file without such a row, every row whose URL or date is missing
or wrong, and every row whose file is gone, and exits 1 if there is one. It
never fetches anything: the browser tools of the session capture the pages,
this only checks the paper trail.

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

TEXT = {
    "en": {
        "title": "# Sources of screenshots and proof copies",
        "summary": "{files} files in {folders}; {rows} rows in sources.csv. As of {as_of}.",
        "ok": "Every file has its URL and date.",
        "bad": "{n} problems. Fix them before a screenshot or proof copy backs a claim.",
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
        "old_h": "## Read more than {days} days before {as_of}",
        "old_note": "Not a failure. Recheck the page before a claim that rests on it is used "
                    "again.",
    },
    "de": {
        "title": "# Quellen der Screenshots und Belegkopien",
        "summary": "{files} Dateien in {folders}; {rows} Zeilen in sources.csv. Stand {as_of}.",
        "ok": "Jede Datei hat ihre URL und ihr Datum.",
        "bad": "{n} Probleme. Erst beheben, dann darf ein Screenshot oder eine Belegkopie "
               "eine Aussage stützen.",
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
    return {"as_of": as_of.isoformat(), "files": len(files), "manifest": rows is not None,
            "rows": len(rows or []), "problems": problems, "old": old}


def render(result, root, lang="en"):
    T = TEXT.get(lang, TEXT["en"])
    folders = ", ".join("%s/" % f for f in FOLDERS)
    as_of = result["as_of"]
    if lang == "de":
        y, m, d = as_of.split("-")
        as_of = "%s.%s.%s" % (d, m, y)
    out = [T["title"], ""]
    if not result["files"] and not result["manifest"]:
        return "\n".join(out + [T["nothing"].format(folders=folders)]) + "\n"
    out.append(T["summary"].format(files=result["files"], folders=folders,
                                   rows=result["rows"], as_of=as_of))
    if not result["manifest"]:
        out += ["", T["no_manifest"].format(path=os.path.join(root, "sources.csv"))]
    out += ["", T["bad"].format(n=len(result["problems"])) if result["problems"] else T["ok"]]
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
