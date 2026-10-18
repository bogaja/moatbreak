#!/usr/bin/env python3
"""Search-data summary for the Moatbreak skill (visibility). Standard library only.

Reads a keyword export the user pulled from an SEO tool (Semrush, Ahrefs,
DataForSEO, SISTRIX, Similarweb, or Google Search Console for the user's own
site) and turns it into the rows of teardown/visibility.md: keyword themes,
the branded share of traffic, the top keywords and pages, and, with --ours,
the keyword gap against the user's own export. It fetches nothing and
estimates nothing: every number is the tool's own, labelled with the tool,
the database and the day the export was pulled (--as-of, required).

Origin and licence: see NOTICE.md and LICENSE.

    python3 seo.py teardown/visibility/semrush-original.csv --tool semrush \\
        --database "Google DE, de" --brand "Kammfux" --as-of 2026-10-17 --lang de \\
        --out teardown/seo.md
    python3 seo.py original.csv --tool ahrefs --brand "Calendly" --ours ours.csv \\
        --local "berlin,münchen" --as-of 2026-10-17 --json

Columns are found by their names as the tools export them (case-insensitive):

    keyword   Keyword, Query, Top queries, Suchbegriff, Häufigste Suchanfragen  required
    position  Position, Current position, Average position, Pos.
    volume    Search Volume, Volume, Suchvolumen
    traffic   Traffic, Organic traffic, ETV, Clicks, Klicks
    url       URL, Current URL, Landing page, Page, Seite

Comma, semicolon or tab separated, UTF-8 or UTF-16 (Ahrefs' default).

Themes, checked in this order; a keyword gets the first that fits:

    alternatives  alternative, vs, versus, vergleich, compare, statt, ...
    branded       contains a --brand name (German spelling variants too)
    local         a --local term, near me, in der nähe, or a 5-digit postcode
    how-to        a question or how to, anleitung, tipps, ...
    category      everything else: generic demand for the product type

The branded share is the part of the traffic (or of the volume, or of the
keyword count, whichever the export has) that goes to keywords containing a
--brand name, "X alternative" included. The keyword gap lists the keywords
the original ranks for in the top 20 that the --ours export does not have,
by volume; searches for the original's own name are left out, "X
alternative" stays in. Third-party tools estimate; Search Console measures,
but only for a site the user owns.
"""

import argparse
import csv
import datetime as _dt
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import sweep  # noqa: E402  German spelling variants of a name

TOOLS = {"semrush": "Semrush", "ahrefs": "Ahrefs", "dataforseo": "DataForSEO",
         "sistrix": "SISTRIX", "similarweb": "Similarweb", "gsc": "Google Search Console"}
MEASURED = {"gsc"}
COLUMNS = {
    "keyword": ("keyword", "keywords", "query", "queries", "top queries", "suchbegriff",
                "suchanfrage", "suchanfragen", "häufigste suchanfragen", "keyword phrase"),
    "position": ("position", "current position", "average position", "avg. position", "pos",
                 "pos.", "rank", "durchschnittliche position", "rank_absolute"),
    "volume": ("search volume", "volume", "search_volume", "suchvolumen", "avg. monthly searches"),
    "traffic": ("traffic", "organic traffic", "current traffic", "etv", "clicks", "klicks"),
    "url": ("url", "current url", "landing page", "page", "seite", "ranking url", "top pages"),
}
THEMES = ("alternatives", "branded", "local", "how-to", "category")
ALTERNATIVES = re.compile(r"\b(alternatives?|alternativen?|vs\.?|versus|vergleich|compared?|"
                          r"comparison|konkurrenz|konkurrenten|competitors?|statt|instead of|"
                          r"similar to|ähnlich wie)(?!\w)", re.I)
HOW_TO = re.compile(r"^(how|what|why|when|which|can|is|wie|was|warum|wann|welche[rsmn]?|kann|"
                    r"ist)\b|\b(how to|anleitung|tutorial|guide|tipps|tips|erklärt|explained|"
                    r"beispiel|vorlage)\b", re.I)
LOCAL = re.compile(r"\b(near me|nearby|in der nähe|in meiner nähe|umgebung)\b|\b\d{5}\b", re.I)
GAP_TOP = 20
TOP_KEYWORDS, TOP_PAGES, TOP_GAP, EXAMPLES = 20, 10, 25, 3

TEXT = {
    "en": {
        "title": "# Search data: {name}",
        "source": "Source: {label}. {n} keywords in {file}.",
        "estimated": "estimated by {tool}{db}, export pulled {date}",
        "measured": "measured by {tool}{db} for the user's own site, export pulled {date}",
        "note_est": "These are the tool's estimates, not measurements of the site. Write "
                    "them with this label, never rounded into facts.",
        "note_gsc": "Search Console shows only sites the user has verified: this is the "
                    "user's own site, never the original's.",
        "dupes": "Duplicate keywords counted once: {n}.",
        "skipped": "Rows without a keyword: {n}.",
        "missing": "Not in this export: {cols}.",
        "themes_h": "## Keyword themes",
        "themes_head": ["theme", "keywords", "{basis}", "share", "examples"],
        "basis": {"traffic": "traffic", "volume": "volume", "keywords": "keywords"},
        "names": {"alternatives": "alternatives and vs", "branded": "branded",
                  "local": "local", "how-to": "how-to and questions",
                  "category": "category (generic)"},
        "branded": "Branded share ({basis}): {share} ({label}). Branded demand is what "
                   "the original owes its name; a rebuild cannot take it.",
        "no_brand": "Branded share: not computed, pass --brand with the original's name.",
        "top_h": "## Top keywords",
        "top_head": ["keyword", "theme", "position", "volume", "traffic", "URL"],
        "pages_h": "## Top pages",
        "pages_head": ["URL", "keywords", "traffic"],
        "no_url": "No URL column, so no top pages.",
        "gap_h": "## Keyword gap",
        "gap": "{n} keywords (searches for the original's name left out) where the original "
               "ranks in the top {top} and that {ours} does not have, by volume ({label}).",
        "gap_none": "No gap: {ours} has every keyword the original ranks for in the top {top}, "
                    "searches for its name left out.",
        "gap_head": ["keyword", "theme", "position", "volume", "URL"],
        "gap_alt": "Keywords in the alternatives theme are comparison searches: a page for "
                   "them follows references/battlecard.md (§ 6 UWG).",
        "every": "Every number above: {label}.",
        "how": "Themes are read from the keyword's words only: alternatives, then branded, "
               "local, how-to, and the rest as category. Check the examples.",
        "fix": "## Fix in the export",
        "bad_number": "line {line}: {col} '{value}' is not a number",
    },
    "de": {
        "title": "# Suchdaten: {name}",
        "source": "Quelle: {label}. {n} Keywords in {file}.",
        "estimated": "geschätzt von {tool}{db}, Export vom {date}",
        "measured": "gemessen von {tool}{db} für die eigene Website, Export vom {date}",
        "note_est": "Das sind Schätzungen des Tools, keine Messungen der Website. Immer mit "
                    "dieser Angabe weitergeben, nie als Tatsache gerundet.",
        "note_gsc": "Die Search Console zeigt nur Websites, die der Nutzer bestätigt hat: Das "
                    "ist die eigene Website, nie die des Originals.",
        "dupes": "Doppelte Keywords einmal gezählt: {n}.",
        "skipped": "Zeilen ohne Keyword: {n}.",
        "missing": "Nicht in diesem Export: {cols}.",
        "themes_h": "## Keyword-Themen",
        "themes_head": ["Thema", "Keywords", "{basis}", "Anteil", "Beispiele"],
        "basis": {"traffic": "Traffic", "volume": "Suchvolumen", "keywords": "Keywords"},
        "names": {"alternatives": "Alternativen und Vergleiche", "branded": "Marke",
                  "local": "lokal", "how-to": "Anleitungen und Fragen",
                  "category": "Kategorie (allgemein)"},
        "branded": "Markenanteil ({basis}): {share} ({label}). Suchen nach dem Namen "
                   "verdankt das Original seiner Marke; ein Nachbau kann sie nicht übernehmen.",
        "no_brand": "Markenanteil: nicht berechnet, --brand mit dem Namen des Originals "
                    "übergeben.",
        "top_h": "## Top-Keywords",
        "top_head": ["Keyword", "Thema", "Position", "Suchvolumen", "Traffic", "URL"],
        "pages_h": "## Top-Seiten",
        "pages_head": ["URL", "Keywords", "Traffic"],
        "no_url": "Keine URL-Spalte, daher keine Top-Seiten.",
        "gap_h": "## Keyword-Lücke",
        "gap": "{n} Keywords (ohne die Suchen nach dem Namen des Originals), bei denen das "
               "Original unter den ersten {top} steht und die in {ours} fehlen, nach "
               "Suchvolumen ({label}).",
        "gap_none": "Keine Lücke: {ours} hat jedes Keyword, bei dem das Original unter den "
                    "ersten {top} steht, ohne die Suchen nach seinem Namen.",
        "gap_head": ["Keyword", "Thema", "Position", "Suchvolumen", "URL"],
        "gap_alt": "Keywords im Thema Alternativen sind Vergleichssuchen: Eine Seite dafür "
                   "folgt references/battlecard.md (§ 6 UWG).",
        "every": "Jede Zahl oben: {label}.",
        "how": "Die Themen liest das Skript nur aus den Wörtern des Keywords: Alternativen, "
               "dann Marke, lokal, Anleitungen, der Rest als Kategorie. Die Beispiele prüfen.",
        "fix": "## Im Export korrigieren",
        "bad_number": "Zeile {line}: {col} '{value}' ist keine Zahl",
    },
}


class SeoError(Exception):
    pass


def parse_number(text):
    """'1,234', '1.234', '12.5', '3,2 %' -> float; '' or '-' -> None; else ValueError."""
    t = (text or "").strip().replace(" ", "").replace(" ", "").rstrip("%")
    if t in ("", "-", "n/a", "N/A"):
        return None
    if "," in t and "." in t:
        t = t.replace(".", "").replace(",", ".") if t.rfind(",") > t.rfind(".") \
            else t.replace(",", "")
    elif "," in t:
        t = t.replace(",", "") if re.match(r"^\d{1,3}(,\d{3})+$", t) else t.replace(",", ".")
    elif re.match(r"^\d{1,3}(\.\d{3})+$", t):
        t = t.replace(".", "")
    return float(t)


def read_text(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise SeoError("%s is neither UTF-8 nor UTF-16: export it again as UTF-8" % path)


def load(path):
    """Return (rows, columns found, rows without keyword, problems)."""
    text = read_text(path)
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        raise SeoError("%s is empty" % path)
    header_at = 0
    if lines[0].lower().startswith("sep="):     # Excel's separator hint
        header_at = 1
    delim = max(",;\t", key=lines[header_at].count)
    reader = csv.reader(io.StringIO("\n".join(lines[header_at:])), delimiter=delim)
    header = [h.strip().lower() for h in next(reader)]
    cols = {}
    for key, names in COLUMNS.items():
        for n in names:
            if n in header:
                cols[key] = header.index(n)
                break
    if "keyword" not in cols:
        raise SeoError("%s has no keyword column (Keyword, Query, Suchbegriff): is it a "
                       "keyword export?" % path)
    rows, skipped, problems = [], 0, []
    for line, cells in enumerate(reader, start=header_at + 2):
        get = lambda k: cells[cols[k]].strip() if k in cols and cols[k] < len(cells) else ""  # noqa: E731
        kw = get("keyword")
        if not kw:
            skipped += 1
            continue
        row = {"keyword": kw, "url": get("url") or None, "line": line}
        for k in ("position", "volume", "traffic"):
            try:
                row[k] = parse_number(get(k))
            except ValueError:
                row[k] = None
                problems.append({"line": line, "col": k, "value": get(k)})
        rows.append(row)
    return rows, sorted(cols), skipped, problems


def norm(kw):
    return " ".join(kw.casefold().split())


def theme_of(kw, brands, local):
    if ALTERNATIVES.search(kw):
        return "alternatives"
    if any(b.search(kw) for b in brands):
        return "branded"
    low = kw.casefold()
    if LOCAL.search(kw) or any(re.search(r"(?<!\w)%s(?!\w)" % re.escape(t), low) for t in local):
        return "local"
    if HOW_TO.search(kw):
        return "how-to"
    return "category"


def analyse(rows, cols, brands=(), local=(), ours=None):
    """rows from load(); brands: names; local: terms; ours: rows of the user's export."""
    brand_rx = [sweep._name_regex(b) for b in brands if b.strip()]
    local = [t.strip().casefold() for t in local if t.strip()]
    seen, kept, dupes = set(), [], 0
    for r in rows:
        key = norm(r["keyword"])
        if key in seen:
            dupes += 1
            continue
        seen.add(key)
        kept.append(dict(r, theme=theme_of(r["keyword"], brand_rx, local)))
    basis = "traffic" if "traffic" in cols else ("volume" if "volume" in cols else "keywords")

    def weight(r):
        return 1.0 if basis == "keywords" else (r.get(basis) or 0.0)

    total = sum(weight(r) for r in kept)
    themes = []
    for name in THEMES:
        items = [r for r in kept if r["theme"] == name]
        w = sum(weight(r) for r in items)
        items.sort(key=lambda r: (-weight(r), norm(r["keyword"])))
        themes.append({"theme": name, "keywords": len(items), "weight": w,
                       "share_pct": round(100.0 * w / total, 1) if total else 0.0,
                       "examples": [r["keyword"] for r in items[:EXAMPLES]]})
    branded = None
    if brand_rx:
        bw = sum(weight(r) for r in kept if r["theme"] in ("branded", "alternatives")
                 and any(b.search(r["keyword"]) for b in brand_rx))
        branded = round(100.0 * bw / total, 1) if total else 0.0
    order = "traffic" if "traffic" in cols else "volume"
    top = sorted(kept, key=lambda r: (-(r.get(order) or 0.0), r["position"] or 999,
                                      norm(r["keyword"])))[:TOP_KEYWORDS]
    pages = None
    if "url" in cols:
        by = {}
        for r in kept:
            if r["url"]:
                p = by.setdefault(r["url"], {"url": r["url"], "keywords": 0, "traffic": 0.0})
                p["keywords"] += 1
                p["traffic"] += r.get("traffic") or 0.0
        pages = sorted(by.values(), key=lambda p: (-p["traffic"], -p["keywords"],
                                                   p["url"]))[:TOP_PAGES]
    gap = None
    if ours is not None:
        have = set(norm(r["keyword"]) for r in ours)
        miss = [r for r in kept if r["theme"] != "branded" and norm(r["keyword"]) not in have
                and (r["position"] is None or r["position"] <= GAP_TOP)]
        miss.sort(key=lambda r: (-(r.get("volume") or 0.0), r["position"] or 999,
                                 norm(r["keyword"])))
        gap = {"count": len(miss), "keywords": miss[:TOP_GAP]}
    return {"keywords": len(kept), "duplicates": dupes, "columns": cols, "basis": basis,
            "themes": themes, "branded_share_pct": branded, "top_keywords": top,
            "top_pages": pages, "gap": gap}


def _num(x, lang, places=0):
    if x is None:
        return "-"
    s = ("{:,.%df}" % places).format(x)
    return s.replace(",", "X").replace(".", ",").replace("X", ".") if lang == "de" else s


def _pct(x, lang):
    s = ("%.1f" % x).rstrip("0").rstrip(".")
    return (s.replace(".", ",") + " %") if lang == "de" else s + "%"


def _cell(s):
    return str(s).replace("|", "\\|")


def _table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + " --- |" * len(head)]
    return out + ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows]


def label(meta, lang):
    T = TEXT[lang]
    db = " (%s)" % meta["database"] if meta.get("database") else ""
    date = meta["as_of"]
    if lang == "de":
        y, m, d = date.split("-")
        date = "%s.%s.%s" % (d, m, y)
    return T["measured" if meta["tool"] in MEASURED else "estimated"].format(
        tool=TOOLS[meta["tool"]], db=db, date=date)


def render(result, meta, lang="en"):
    T = TEXT.get(lang, TEXT["en"])
    lab = label(meta, lang)

    def pos(r):
        p = r["position"]
        return _num(p, lang, 0 if p is None or p == int(p) else 1)
    out = [T["title"].format(name=meta.get("name") or os.path.basename(meta["file"])), "",
           T["source"].format(label=lab, n=_num(result["keywords"], lang),
                              file=os.path.basename(meta["file"])), "",
           T["note_gsc"] if meta["tool"] in MEASURED else T["note_est"]]
    extra = []
    if result["duplicates"]:
        extra.append(T["dupes"].format(n=result["duplicates"]))
    if meta.get("skipped"):
        extra.append(T["skipped"].format(n=meta["skipped"]))
    missing = [c for c in ("position", "volume", "traffic", "url") if c not in result["columns"]]
    if missing:
        extra.append(T["missing"].format(cols=", ".join(missing)))
    if extra:
        out += [""] + extra
    basis = T["basis"][result["basis"]]
    head = [h.format(basis=basis) for h in T["themes_head"]]
    rows = [[T["names"][t["theme"]], _num(t["keywords"], lang),
             _num(t["weight"], lang) if result["basis"] != "keywords" else _num(t["keywords"], lang),
             _pct(t["share_pct"], lang), ", ".join(t["examples"]) or "-"]
            for t in result["themes"]]
    out += ["", T["themes_h"], ""] + _table(head, rows) + [""]
    if result["branded_share_pct"] is None:
        out.append(T["no_brand"])
    else:
        out.append(T["branded"].format(share=_pct(result["branded_share_pct"], lang),
                                       basis=basis, label=lab))
    out += ["", T["top_h"], ""] + _table(T["top_head"], [
        [r["keyword"], T["names"][r["theme"]], pos(r), _num(r.get("volume"), lang),
         _num(r.get("traffic"), lang), r["url"] or "-"] for r in result["top_keywords"]])
    out += ["", T["pages_h"], ""]
    if result["top_pages"] is None:
        out.append(T["no_url"])
    else:
        out += _table(T["pages_head"], [[p["url"], _num(p["keywords"], lang),
                                         _num(p["traffic"], lang)] for p in result["top_pages"]])
    gap = result["gap"]
    if gap is not None:
        ours = os.path.basename(meta["ours"])
        out += ["", T["gap_h"], ""]
        if gap["count"]:
            out += [T["gap"].format(n=gap["count"], top=GAP_TOP, ours=ours, label=lab), ""]
            out += _table(T["gap_head"], [[r["keyword"], T["names"][r["theme"]], pos(r),
                                           _num(r.get("volume"), lang), r["url"] or "-"]
                                          for r in gap["keywords"]])
            if any(r["theme"] == "alternatives" for r in gap["keywords"]):
                out += ["", T["gap_alt"]]
        else:
            out.append(T["gap_none"].format(ours=ours, top=GAP_TOP))
    out += ["", T["every"].format(label=lab), T["how"]]
    if meta.get("problems"):
        out += ["", T["fix"], ""] + ["- " + T["bad_number"].format(**p) for p in meta["problems"]]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("export", help="keyword export (CSV) from the SEO tool")
    ap.add_argument("--tool", required=True, choices=sorted(TOOLS),
                    help="the tool the export comes from")
    ap.add_argument("--as-of", required=True, metavar="YYYY-MM-DD",
                    help="the day the export was pulled; every number carries it")
    ap.add_argument("--database", help='the tool\'s database, e.g. "Google DE, de"')
    ap.add_argument("--brand", default="", help="the original's names, comma-separated")
    ap.add_argument("--local", default="", help="local terms such as cities, comma-separated")
    ap.add_argument("--ours", help="the user's own export, for the keyword gap")
    ap.add_argument("--name", help="what the export is about, for the title")
    ap.add_argument("--lang", choices=sorted(TEXT), default="en")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", help="write the report (or the JSON) here")
    args = ap.parse_args(argv)
    try:
        _dt.datetime.strptime(args.as_of, "%Y-%m-%d")
    except ValueError:
        print("seo: --as-of needs the day the export was pulled, like 2026-10-17",
              file=sys.stderr)
        return 2
    try:
        rows, cols, skipped, problems = load(args.export)
        ours = load(args.ours)[0] if args.ours else None
    except (SeoError, OSError, ValueError, csv.Error) as exc:
        print("seo: %s" % exc, file=sys.stderr)
        return 2
    result = analyse(rows, cols, args.brand.split(","), args.local.split(","), ours)
    meta = {"file": args.export, "tool": args.tool, "database": args.database,
            "as_of": args.as_of, "name": args.name, "ours": args.ours, "skipped": skipped,
            "problems": problems}
    if args.json:
        data = dict(result, source=dict(meta, tool_name=TOOLS[args.tool],
                                        label=label(meta, "en")))
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    else:
        text = render(result, meta, args.lang)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
