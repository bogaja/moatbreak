#!/usr/bin/env python3
"""Sitemap summary for the Moatbreak skill (recon, visibility). Standard library only.

Reads sitemap files of the original that you saved by hand (sitemap.xml, a
sitemap index, .xml.gz, or a plain list of URLs, one per line) and counts its
public pages: by page type (blog, product, category, help, pricing,
comparison, ...), by first folder, by language or country folder (/de/,
/en-us/, /ch-de/) and by hreflang. It never fetches anything: an index lists
its child sitemaps, and you save the ones you need and pass them too. A child
counts as given when a saved file's path ends with the child's URL path
(de/sitemap.xml) or, if no other child has its file name, when the names
match; the index file itself never counts.

Origin and licence: see NOTICE.md and LICENSE.

    python3 sitemap.py teardown/visibility/sitemap.xml
    python3 sitemap.py teardown/visibility/sitemap*.xml --lang de --as-of 2026-10-17 \\
        --out teardown/sitemap.md
    python3 sitemap.py teardown/visibility/sitemap.xml --json

Page types come from words in the address (blog, hilfe, products,
collections, preise, impressum, ...), checked in a fixed order: comparison,
legal, help, blog, product, category, pricing, integrations, templates,
customers, features, locations, company. So /blog/x-vs-y is a comparison page
and /collections/x/products/y a product page. /product/ on a SaaS site often
means feature pages: read the examples. A page whose address says nothing is
"other"; the section table still counts it.

The counts are what the site lists in its sitemap, not a crawl: pages left
out of the sitemap are missing, and listed pages may be noindex or gone.
lastmod dates are the site's own claim; if most of them fall on one day, the
report says the sitemap probably stamps its build date. --as-of YYYY-MM-DD
adds how many pages of each type changed in the 90 days up to that date.

Files with a DOCTYPE are refused (sitemaps never need one, and it is how XML
entity attacks work), and so are files over 60 MB after unpacking.
"""

import argparse
import datetime as _dt
import gzip
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zlib
from urllib.parse import unquote, urlsplit

MAX_BYTES = 60 * 1024 * 1024
RECENT_DAYS = 90
STAMPED_SHARE = 0.9
STAMPED_MIN = 10
MAX_SECTIONS = 25
EXAMPLES = 3

LANGS = frozenset(("en de fr es it nl pt pl sv da no nb nn fi cs sk hu ro bg el tr ru uk "
                   "ar he ja zh ko hi th vi hr sl sr bs mk sq lt lv et is ga ca eu gl lb "
                   "mt fa").split())
COUNTRIES = frozenset("at ch li lu be us gb ie au nz br mx".split())
MARKET_SEG = re.compile(r"^([a-z]{2})(?:[-_]([a-z]{2}))?$")
EXT = re.compile(r"\.(?:html?|php|aspx?|jsp)$")
TOKEN = re.compile(r"[-_+.]+")
DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")
DOCTYPE = re.compile(rb"<!(?:DOCTYPE|ENTITY)", re.I)

VS = frozenset(("vs", "versus", "vergleich"))
COMPARE_PAGES = frozenset(("compare", "comparison", "vergleich", "alternatives", "alternativen"))
ALTERNATIVE = frozenset(("alternative", "alternatives", "alternativen"))
ALT_LINK = frozenset(("to", "zu", "for", "fuer", "für"))

TYPES = tuple((name, frozenset(words.split())) for name, words in (
    ("legal", "impressum imprint legal legal-notice datenschutz datenschutzerklaerung "
              "datenschutzerklärung privacy privacy-policy terms terms-of-service "
              "terms-and-conditions tos agb nutzungsbedingungen widerruf widerrufsbelehrung "
              "cookies cookie-policy rechtliches"),
    ("help", "help hilfe support faq faqs docs doc documentation dokumentation hc kb "
             "knowledge-base knowledgebase help-center helpcenter hilfe-center hilfecenter "
             "academy akademie tutorials anleitung anleitungen"),
    ("blog", "blog blogs news magazin magazine ratgeber articles beitraege beiträge posts "
             "stories journal insights resources ressourcen guide guides wissen podcast"),
    ("product", "product products produkt produkte p dp item items"),
    ("category", "category categories kategorie kategorien collections collection c catalog "
                 "catalogue katalog shop sortiment brands marken department departments"),
    ("pricing", "pricing prices price preise preis plans tarife kosten pakete"),
    ("integrations", "integrations integration integrationen apps marketplace connectors "
                     "plugins addons add-ons extensions erweiterungen"),
    ("templates", "templates template vorlagen vorlage"),
    ("customers", "customers kunden case-studies case-study cases referenzen success-stories "
                  "testimonials kundenstimmen erfahrungen"),
    ("features", "features feature funktionen solutions loesungen lösungen use-cases "
                 "industries branchen platform plattform"),
    ("locations", "locations location standorte standort filialen filiale cities staedte "
                  "städte stores"),
    ("company", "about about-us ueber-uns über-uns uber-uns team careers jobs karriere press "
                "presse contact kontakt"),
))
TYPE_ORDER = ("home", "comparison") + tuple(t[0] for t in TYPES) + ("other",)

TEXT = {
    "en": {
        "title": "# Sitemap: {host}",
        "read": "{pages} pages from {files} file(s): {names}.",
        "dupes": "Duplicate addresses removed: {n}.",
        "hosts": "Hosts: {list}.",
        "types_h": "## Page types",
        "types_head": ["type", "pages", "share", "newest lastmod"],
        "recent_col": "changed in the 90 days to {as_of}",
        "examples_col": "examples",
        "lang_h": "## Language and country folders",
        "lang_head": ["folder", "pages"],
        "lang_none": "No language or country folders in the addresses.",
        "lang_rest": "{n} pages sit in no language folder.",
        "hreflang": "hreflang alternates listed in the sitemap: {list}.",
        "sections_h": "## Sections (first folder)",
        "sections_head": ["section", "pages", "example"],
        "top_level": "/ (top-level pages)",
        "more": "{k} more sections with {p} pages.",
        "index_h": "## Child sitemaps in the index",
        "index_head": ["sitemap", "lastmod", "given"],
        "partial": "Counts are partial: {given} of {total} child sitemaps were given. This "
                   "tool fetches nothing; save the missing ones from the index under their "
                   "own file names and run it again.",
        "index_only": "Only a sitemap index was given, so there are no pages to count yet. "
                      "Save the child sitemaps listed below and pass them too.",
        "shared": "{n} child sitemaps share a file name ({names}), so a saved file with that "
                  "name cannot be matched to one of them and none counts as given. Save each "
                  "under folders that follow its address (https://x.com/de/sitemap.xml as "
                  "de/sitemap.xml) and pass those paths.",
        "notes_h": "## Notes",
        "stamped": "{share} of the dated pages carry the same lastmod ({date}): the sitemap "
                   "probably stamps its build date, so it says nothing about publishing "
                   "activity.",
        "basis": "These are the pages the site lists in its sitemap, not a crawl: pages left "
                 "out are missing here too, and listed pages may be noindex, redirected or "
                 "gone. Types are read from the address only; check the examples.",
        "yes": "yes", "no": "no",
        "types": {"home": "home", "comparison": "comparison", "legal": "legal",
                  "help": "help", "blog": "blog", "product": "product",
                  "category": "category", "pricing": "pricing",
                  "integrations": "integrations", "templates": "templates",
                  "customers": "customers", "features": "features",
                  "locations": "locations", "company": "company", "other": "other"},
    },
    "de": {
        "title": "# Sitemap: {host}",
        "read": "{pages} Seiten aus {files} Datei(en): {names}.",
        "dupes": "Doppelte Adressen entfernt: {n}.",
        "hosts": "Hosts: {list}.",
        "types_h": "## Seitentypen",
        "types_head": ["Typ", "Seiten", "Anteil", "neuestes lastmod"],
        "recent_col": "geändert in den 90 Tagen bis {as_of}",
        "examples_col": "Beispiele",
        "lang_h": "## Sprach- und Länderordner",
        "lang_head": ["Ordner", "Seiten"],
        "lang_none": "Keine Sprach- oder Länderordner in den Adressen.",
        "lang_rest": "{n} Seiten liegen in keinem Sprachordner.",
        "hreflang": "hreflang-Alternativen in der Sitemap: {list}.",
        "sections_h": "## Bereiche (erster Ordner)",
        "sections_head": ["Bereich", "Seiten", "Beispiel"],
        "top_level": "/ (Seiten auf oberster Ebene)",
        "more": "{k} weitere Bereiche mit {p} Seiten.",
        "index_h": "## Unter-Sitemaps im Index",
        "index_head": ["Sitemap", "lastmod", "übergeben"],
        "partial": "Die Zahlen sind unvollständig: {given} von {total} Unter-Sitemaps wurden "
                   "übergeben. Das Skript lädt nichts herunter; speichere die fehlenden aus "
                   "dem Index unter ihrem eigenen Dateinamen und starte es noch einmal.",
        "index_only": "Es wurde nur ein Sitemap-Index übergeben, es gibt also noch keine "
                      "Seiten zu zählen. Speichere die unten gelisteten Unter-Sitemaps und "
                      "übergib sie mit.",
        "shared": "{n} Unter-Sitemaps haben denselben Dateinamen ({names}). Eine gespeicherte "
                  "Datei mit diesem Namen lässt sich keiner von ihnen zuordnen, daher zählt "
                  "keine als übergeben. Speichere jede in Ordnern nach ihrer Adresse "
                  "(https://x.com/de/sitemap.xml als de/sitemap.xml) und übergib diese Pfade.",
        "notes_h": "## Hinweise",
        "stamped": "{share} der datierten Seiten tragen dasselbe lastmod ({date}): Die "
                   "Sitemap stempelt vermutlich ihr Erstellungsdatum und sagt nichts über "
                   "Veröffentlichungen aus.",
        "basis": "Das sind die Seiten, die die Website in ihrer Sitemap listet, kein Crawl: "
                 "Ausgelassene Seiten fehlen auch hier, und gelistete Seiten können noindex, "
                 "umgeleitet oder gelöscht sein. Den Typ liest das Skript nur aus der "
                 "Adresse; prüfe die Beispiele.",
        "yes": "ja", "no": "nein",
        "types": {"home": "Startseite", "comparison": "Vergleich", "legal": "Rechtliches",
                  "help": "Hilfe", "blog": "Blog", "product": "Produkt",
                  "category": "Kategorie", "pricing": "Preise",
                  "integrations": "Integrationen", "templates": "Vorlagen",
                  "customers": "Kunden", "features": "Funktionen",
                  "locations": "Standorte", "company": "Unternehmen", "other": "Sonstige"},
    },
}


class SitemapError(Exception):
    pass


def _local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _child_text(parent, name):
    for el in parent:
        if _local(el.tag) == name:
            return (el.text or "").strip() or None
    return None


def read_bytes(path):
    with open(path, "rb") as fh:
        data = fh.read(MAX_BYTES + 1)
    if data[:2] == b"\x1f\x8b":
        try:
            data = gzip.GzipFile(fileobj=io.BytesIO(data)).read(MAX_BYTES + 1)
        except (OSError, EOFError, zlib.error) as exc:
            raise SitemapError("%s: cannot unpack (%s)" % (path, exc))
    if len(data) > MAX_BYTES:
        raise SitemapError("%s: larger than 60 MB; a sitemap is at most 50 MB" % path)
    return data


def parse(data, name="sitemap"):
    """Return (kind, urls, children). kind is urlset, index or text."""
    if not data.lstrip(b"\xef\xbb\xbf \t\r\n").startswith(b"<"):
        urls = [{"loc": line.strip(), "lastmod": None, "alternates": []}
                for line in data.decode("utf-8-sig", "replace").splitlines()
                if line.strip().lower().startswith(("http://", "https://"))]
        return "text", urls, []
    if DOCTYPE.search(data):
        raise SitemapError("%s: has a DOCTYPE or ENTITY declaration; refused, a sitemap "
                           "never needs one" % name)
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise SitemapError("%s: not valid XML (%s)" % (name, exc))
    kind = _local(root.tag)
    if kind == "sitemapindex":
        children = []
        for sm in root:
            loc = _child_text(sm, "loc") if _local(sm.tag) == "sitemap" else None
            if loc:
                children.append({"loc": loc, "lastmod": _child_text(sm, "lastmod")})
        return "index", [], children
    if kind == "urlset":
        urls = []
        for u in root:
            loc = _child_text(u, "loc") if _local(u.tag) == "url" else None
            if not loc:
                continue
            alts = [el.get("hreflang").strip().lower() for el in u
                    if _local(el.tag) == "link" and el.get("hreflang")]
            urls.append({"loc": loc, "lastmod": _child_text(u, "lastmod"), "alternates": alts})
        return "urlset", urls, []
    raise SitemapError("%s: root element is <%s>, expected <urlset> or <sitemapindex>"
                       % (name, kind))


def market_folder(seg):
    """'de', 'en-us', 'ch-de', 'at' -> the folder name; anything else -> None."""
    m = MARKET_SEG.match(seg)
    if not m:
        return None
    first, region = m.group(1), m.group(2)
    if first in LANGS or first in COUNTRIES or (region and region in LANGS):
        return seg.replace("_", "-")
    return None


def split_path(path):
    """Lower-cased, unquoted path segments, with a leading language folder split off."""
    segs = [unquote(s).lower() for s in path.split("/") if s]
    folder = market_folder(segs[0]) if segs else None
    return folder, (segs[1:] if folder else segs)


def _is_comparison(word):
    if word in COMPARE_PAGES:
        return True
    toks = [t for t in TOKEN.split(word) if t]
    if VS & set(toks):
        return True
    for i, t in enumerate(toks):
        if t in ALTERNATIVE and ((i > 0 and i == len(toks) - 1)
                                 or (i + 1 < len(toks) and toks[i + 1] in ALT_LINK)):
            return True
    return False


def classify(segs):
    """Page type of a path given as segments after the language folder."""
    if not segs:
        return "home"
    words = [EXT.sub("", s) for s in segs]
    if any(_is_comparison(w) for w in words):
        return "comparison"
    for name, keys in TYPES:
        if any(w in keys for w in words):
            return name
    return "other"


def _date(text):
    m = DATE.match(text or "")
    if not m:
        return None
    try:
        return _dt.datetime.strptime(m.group(1), "%Y-%m-%d").date()
    except ValueError:
        return None


def _base(path_or_url):
    name = os.path.basename(urlsplit(path_or_url).path if "://" in path_or_url
                            else path_or_url).lower()
    return name[:-3] if name.endswith(".gz") else name


def mark_given(children, parsed):
    """A child sitemap counts as given when a saved urlset or URL list (never an
    index) is its file: one whose path ends with the child's URL path
    (de/sitemap.xml for https://x.com/de/sitemap.xml), or one with the child's
    file name when no other child in the index has that name."""
    files = ["/" + name.replace(os.sep, "/").lower() for name, kind, _u, _c in parsed
             if kind != "index"]
    files = [f[:-3] if f.endswith(".gz") else f for f in files]
    names = {}
    for c in children:
        names[_base(c["loc"])] = names.get(_base(c["loc"]), 0) + 1
    out = []
    for c in children:
        path = unquote(urlsplit(c["loc"]).path).lower()
        path = path[:-3] if path.endswith(".gz") else path
        base = _base(c["loc"])
        shared = names[base] > 1
        by_path = path.count("/") >= 2 and any(f.endswith(path) for f in files)
        by_name = not shared and any(os.path.basename(f) == base for f in files)
        out.append(dict(c, given=by_path or by_name, shared_name=shared))
    return out


def _ranked(counts):
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def analyse(parsed, as_of=None):
    """parsed: list of (file name, kind, urls, children) from parse()."""
    seen, children, pages, dupes = set(), [], [], 0
    child_seen = set()
    for _name, _kind, urls, kids in parsed:
        for c in kids:
            if c["loc"] not in child_seen:
                child_seen.add(c["loc"])
                children.append(c)
        for u in urls:
            loc = u["loc"].split("#", 1)[0]
            if loc in seen:
                dupes += 1
                continue
            seen.add(loc)
            parts = urlsplit(loc)
            folder, segs = split_path(parts.path)
            pages.append({"loc": loc, "host": parts.netloc.lower(), "folder": folder,
                          "segs": segs, "type": classify(segs),
                          "date": _date(u.get("lastmod")),
                          "alternates": u.get("alternates") or []})

    hosts, folders, hreflang, sections = {}, {}, {}, {}
    folder_names = set(p["segs"][0] for p in pages if len(p["segs"]) > 1)
    types = dict((t, {"type": t, "pages": 0, "newest": None, "recent": 0, "examples": []})
                 for t in TYPE_ORDER)
    start = as_of - _dt.timedelta(days=RECENT_DAYS) if as_of else None
    dates = {}
    for p in pages:
        hosts[p["host"]] = hosts.get(p["host"], 0) + 1
        if p["folder"]:
            folders[p["folder"]] = folders.get(p["folder"], 0) + 1
        for h in p["alternates"]:
            hreflang[h] = hreflang.get(h, 0) + 1
        segs = p["segs"]
        key = "/%s/" % segs[0] if segs and (len(segs) > 1 or segs[0] in folder_names) else "/"
        sec = sections.setdefault(key, {"section": key, "pages": 0, "example": p["loc"]})
        sec["pages"] += 1
        t = types[p["type"]]
        t["pages"] += 1
        if len(t["examples"]) < EXAMPLES:
            t["examples"].append(p["loc"])
        d = p["date"]
        if d:
            dates[d] = dates.get(d, 0) + 1
            if t["newest"] is None or d > t["newest"]:
                t["newest"] = d
            if start and start < d <= as_of:
                t["recent"] += 1

    total = len(pages)
    type_rows = []
    for name in TYPE_ORDER:
        t = types[name]
        if t["pages"]:
            t["share"] = round(100.0 * t["pages"] / total, 1)
            t["newest"] = t["newest"].isoformat() if t["newest"] else None
            if not as_of:
                del t["recent"]
            type_rows.append(t)
    sec_rows = sorted(sections.values(), key=lambda s: (-s["pages"], s["section"]))
    rest = sec_rows[MAX_SECTIONS:]
    dated = sum(dates.values())
    top_day, top_n = (max(dates.items(), key=lambda kv: (kv[1], kv[0])) if dates
                      else (None, 0))
    return {
        "files": [{"file": name, "kind": kind, "urls": len(urls), "sitemaps": len(kids)}
                  for name, kind, urls, kids in parsed],
        "pages": total,
        "duplicates": dupes,
        "hosts": _ranked(hosts),
        "types": type_rows,
        "folders": _ranked(folders),
        "no_folder": sum(1 for p in pages if not p["folder"]),
        "hreflang": _ranked(hreflang),
        "sections": sec_rows[:MAX_SECTIONS],
        "more_sections": {"sections": len(rest), "pages": sum(s["pages"] for s in rest)},
        "lastmod": {"dated": dated, "top_date": top_day.isoformat() if top_day else None,
                    "top_share": round(100.0 * top_n / dated, 1) if dated else 0.0,
                    "stamped": dated >= STAMPED_MIN and top_n >= STAMPED_SHARE * dated},
        "as_of": as_of.isoformat() if as_of else None,
        "index": mark_given(children, parsed),
    }


def _n(x, lang):
    s = format(x, ",")
    return s.replace(",", ".") if lang == "de" else s


def _pct(x, lang):
    s = "%.0f" % x
    return s + " %" if lang == "de" else s + "%"


def _cell(s):
    return str(s).replace("|", "\\|")


def _row(cells):
    return "| " + " | ".join(_cell(c) for c in cells) + " |"


def _table(head, rows):
    out = [_row(head), "|" + " --- |" * len(head)]
    return out + [_row(r) for r in rows]


def render(result, lang="en"):
    T = TEXT.get(lang, TEXT["en"])
    one_host = len(result["hosts"]) <= 1
    host = (result["hosts"][0][0] if result["hosts"]
            else (urlsplit(result["index"][0]["loc"]).netloc if result["index"] else "?"))

    def show(url):
        if not one_host:
            return url
        parts = urlsplit(url)
        return unquote(parts.path or "/") + ("?" + parts.query if parts.query else "")

    names = ", ".join(os.path.basename(f["file"]) for f in result["files"])
    out = [T["title"].format(host=host), "",
           T["read"].format(pages=_n(result["pages"], lang), files=len(result["files"]),
                            names=names)]
    if result["duplicates"]:
        out.append(T["dupes"].format(n=_n(result["duplicates"], lang)))
    if len(result["hosts"]) > 1:
        out.append(T["hosts"].format(list=", ".join(
            "%s (%s)" % (h, _n(c, lang)) for h, c in result["hosts"])))
    index = result["index"]
    given = sum(1 for c in index if c["given"])
    if index and not result["pages"]:
        out += ["", T["index_only"]]
    elif index and given < len(index):
        out += ["", T["partial"].format(given=given, total=len(index))]
    shared = sorted(set(_base(c["loc"]) for c in index if c["shared_name"] and not c["given"]))
    if shared:
        out += ["", T["shared"].format(
            n=sum(1 for c in index if c["shared_name"] and not c["given"]),
            names=", ".join(shared))]

    if result["types"]:
        head = list(T["types_head"])
        if result["as_of"]:
            head.append(T["recent_col"].format(as_of=result["as_of"]))
        head.append(T["examples_col"])
        rows = []
        for t in result["types"]:
            r = [T["types"][t["type"]], _n(t["pages"], lang), _pct(t["share"], lang),
                 t["newest"] or "-"]
            if result["as_of"]:
                r.append(_n(t["recent"], lang))
            r.append(", ".join(show(u) for u in t["examples"]))
            rows.append(r)
        out += ["", T["types_h"], ""] + _table(head, rows)

        out += ["", T["lang_h"], ""]
        if result["folders"]:
            out += _table(T["lang_head"], [[f, _n(c, lang)] for f, c in result["folders"]])
            if result["no_folder"]:
                out += ["", T["lang_rest"].format(n=_n(result["no_folder"], lang))]
        else:
            out.append(T["lang_none"])
        if result["hreflang"]:
            out += ["", T["hreflang"].format(list=", ".join(
                "%s (%s)" % (h, _n(c, lang)) for h, c in result["hreflang"]))]

        out += ["", T["sections_h"], ""]
        out += _table(T["sections_head"], [
            [T["top_level"] if s["section"] == "/" else s["section"], _n(s["pages"], lang),
             show(s["example"])] for s in result["sections"]])
        more = result["more_sections"]
        if more["sections"]:
            out += ["", T["more"].format(k=_n(more["sections"], lang),
                                         p=_n(more["pages"], lang))]

    if index:
        out += ["", T["index_h"], ""]
        out += _table(T["index_head"], [[c["loc"], c["lastmod"] or "-",
                                         T["yes"] if c["given"] else T["no"]] for c in index])

    out += ["", T["notes_h"], ""]
    lm = result["lastmod"]
    if lm["stamped"]:
        out.append("- " + T["stamped"].format(share=_pct(lm["top_share"], lang),
                                              date=lm["top_date"]))
    out.append("- " + T["basis"])
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("files", nargs="+",
                    help="saved sitemap.xml, sitemap index, .xml.gz or a list of URLs")
    ap.add_argument("--as-of", help="YYYY-MM-DD: also count pages changed in the 90 days "
                                    "up to this date")
    ap.add_argument("--lang", choices=sorted(TEXT), default="en",
                    help="language of the report (default en)")
    ap.add_argument("--out", help="write the report here")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    as_of = None
    if args.as_of:
        try:
            as_of = _dt.datetime.strptime(args.as_of, "%Y-%m-%d").date()
        except ValueError:
            print("sitemap: --as-of must be YYYY-MM-DD", file=sys.stderr)
            return 2
    parsed = []
    try:
        for path in args.files:
            kind, urls, kids = parse(read_bytes(path), path)
            parsed.append((path, kind, urls, kids))
    except (SitemapError, OSError) as exc:
        print("sitemap: %s" % exc, file=sys.stderr)
        return 2
    if not any(urls or kids for _p, _k, urls, kids in parsed):
        print("sitemap: no addresses found. Pass a sitemap.xml, a sitemap index or a list "
              "of URLs saved from the site.", file=sys.stderr)
        return 2
    result = analyse(parsed, as_of)
    text = (json.dumps(result, indent=2, ensure_ascii=False) + "\n" if args.json
            else render(result, args.lang))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
