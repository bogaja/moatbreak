#!/usr/bin/env python3
"""Market landscape and positioning map for the Moatbreak skill. Standard library only.

Step 0 (discover): when the user names a niche instead of a product, every
candidate found goes into teardown/competitors.csv, one row per product, with
the public page each claim comes from. This script turns that file into a
landscape matrix, a proposal of up to five verified reference products for the
user to confirm, and, with --svg, a positioning map as a standalone SVG.

Origin and licence: see NOTICE.md and LICENSE.

    python3 landscape.py teardown/competitors.csv
    python3 landscape.py teardown/competitors.csv --lang de --market DACH \\
        --title "Buchungs-App für Friseure" --out teardown/landscape.md
    python3 landscape.py teardown/competitors.csv --lang de --market DACH \\
        --svg teardown/landscape.svg --x price_from --y axis_y \\
        --x-label "Preis ab (EUR/Monat, netto)" --y-label "Kernaufgaben laut Website (von 8)" \\
        --out teardown/landscape.md
    python3 landscape.py teardown/competitors.csv --json

Columns (header names are case-insensitive, extra columns are ignored):

    name          product name                                         required
    url           its homepage                                         required
    evidence_url  the public page that shows what it does and for whom
                  (its own feature or industry page)                   required
    category      what it is, in its own words ("Online-Terminbuchung")
    customer      who it sells to ("Friseur- und Kosmetiksalons")
    market        countries it sells in: DE, AT, CH, DACH, EU, global, ...
    languages     UI languages: de, en, ...
    price_from    entry price as read ("ab 29 EUR / Monat", "kostenlos")
    price_model   per month, per seat, per booking, net or gross, ...
    price_url     the pricing page price_from comes from
    axis_x        a number for the map, read by one stated rule
    axis_y        a second number for the map
    axis_url      the page axis_x and axis_y come from; if they come from two
                  pages, both URLs separated by a space, the one for x first
    status        candidate | fit | adjacent | out | confirmed | planned
                  (Kandidat | passt | angrenzend | raus | bestätigt | geplant)
    read_on       date the pages were read, YYYY-MM-DD
    notes         one line: why it fits, or why it is out
    company, seat, founded, size
                  optional company facts as printed on a public page (the
                  Impressum, the Handelsregister or Unternehmensregister
                  entry, the company's own press page)
    company_url   the page(s) those facts come from, separated by a space

Status: candidate = found, not yet checked against the five criteria (same
job, same customer, active, public sources, the user's market); fit = passes
all five; adjacent = same job, broader or other customer (a horizontal tool
customers compare against); out = fails one, the notes say which; confirmed =
the user picked it for the teardown; planned = the user's own product as
intended, drawn on the map as a plan and never treated as a competitor.

Rules this script enforces:

- A row without an http(s) evidence_url is unverified. It is listed after
  every verified row and never proposed, so a product known only from memory
  cannot pass as a finding.
- A price without a price_url and an axis value without an axis_url are
  marked "no source" in the matrix and drawn hollow on the map.
- A price cell with a word of guessing (vermutlich, ca., geschätzt,
  probably, estimated, ~, ?) is flagged: the cell holds what the page
  prints, nothing worked out or assumed.
- Only fit and confirmed rows are proposed, at most five. With --market, only
  rows whose market includes the user's market (DACH = DE, AT, CH; EU = the
  27 member states; global = everywhere).
- Numbers are never estimated: a row without a number on an axis is listed
  as "not on the map". price_from counts the first number, or 0 when the text
  starts with free / kostenlos / gratis. Swiss 1'200 and German 1.200,50 work.
- Company facts without a company_url are marked "no source".
- Rows whose url ends in .example (the documented sample) are dropped.
"""

import argparse
import csv
import json
import math
import re
import sys
from xml.sax.saxutils import escape

REQUIRED = ("name", "url", "evidence_url")
STATUS = {"": "candidate", "candidate": "candidate", "kandidat": "candidate",
          "fit": "fit", "passt": "fit",
          "adjacent": "adjacent", "angrenzend": "adjacent",
          "out": "out", "raus": "out", "ausgeschlossen": "out",
          "confirmed": "confirmed", "bestätigt": "confirmed", "bestaetigt": "confirmed",
          "planned": "planned", "geplant": "planned"}
RANK = {"confirmed": 0, "fit": 1, "candidate": 2, "adjacent": 3}
PROPOSE = ("confirmed", "fit")
MAX_PROPOSAL = 5
MIN_PROPOSAL = 3

EU27 = frozenset("AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO "
                 "SK SI ES SE".split())
EVERYWHERE = "*"
REGIONS = {
    "dach": {"DE", "AT", "CH"}, "d-a-ch": {"DE", "AT", "CH"},
    "eu": EU27, "ewr": EU27 | {"IS", "LI", "NO"}, "eea": EU27 | {"IS", "LI", "NO"},
    "europe": EU27 | {"CH", "GB", "IS", "LI", "NO"},
    "europa": EU27 | {"CH", "GB", "IS", "LI", "NO"},
    "global": {EVERYWHERE}, "worldwide": {EVERYWHERE}, "weltweit": {EVERYWHERE},
    "international": {EVERYWHERE},
    "deutschland": {"DE"}, "germany": {"DE"}, "österreich": {"AT"}, "oesterreich": {"AT"},
    "austria": {"AT"}, "schweiz": {"CH"}, "switzerland": {"CH"}, "suisse": {"CH"},
    "svizzera": {"CH"}, "liechtenstein": {"LI"}, "uk": {"GB"}, "el": {"GR"}, "usa": {"US"},
}
# Lower-case two-letter words that are prepositions, not country codes. In
# capitals (IN, IT, NO, BE) they still count as codes.
NOT_CODES = {"in", "im", "an", "am", "um", "zu", "or", "to", "of", "on", "is", "it", "by",
             "no", "be"}
# D/A/CH, D, A, CH and DE-AT-CH all mean DACH (D and A are vehicle codes, not ISO).
DACH_FORMS = re.compile(r"\b(?:de|d)\s*[-/,]\s*(?:at|a)\s*[-/,]\s*ch\b", re.I)
COLUMNS = ("name", "url", "evidence_url", "category", "customer", "market", "languages",
           "price_from", "price_model", "price_url", "axis_x", "axis_y", "axis_url", "read_on",
           "notes", "company", "seat", "founded", "size", "company_url")
COMPANY = ("company", "seat", "founded", "size")
NUMBER = re.compile(r"\d[\d.,'\u2019]*")
FREE = re.compile(r"\b(?:free|kostenlos|gratis|gratuit)\b", re.I)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Words that mark a price as worked out or assumed rather than read.
GUESS = re.compile(r"(?<!\w)(?:vermutlich|wahrscheinlich|geschätzt|schätzungsweise|ungefähr|"
                   r"circa|ca\.|etwa|probably|likely|presumably|estimated|approx\.?|"
                   r"approximately|roughly)(?!\w)|~|\?", re.I)

TEXT = {
    "en": {
        "title": "Market landscape", "title_for": "Market landscape: %s",
        "summary": "Products: %d, with evidence: %d, unverified: %d.",
        "market": "Market checked against: %s.",
        "proposal": "Proposal for the teardown (verified and fit only, at most %d)",
        "proposal_none": "Nothing to propose yet: no row is verified and marked fit. Check the "
                         "candidates against the five criteria (status) and add evidence links.",
        "proposal_few": "Verified and fit: only %d. Search further, or tell the user the market "
                        "is thin.",
        "evidence": "evidence",
        "next": "Next: the user confirms which to tear down and names any product that is "
                "missing. Recon starts only after that answer.",
        "confirmed": "Confirmed for the teardown: %s. Next step: recon.",
        "matrix": "Landscape matrix",
        "cols": ["#", "product", "category", "customer", "market", "languages", "price from",
                 "price model", "status", "evidence", "read on"],
        "status": {"confirmed": "confirmed", "fit": "fit", "candidate": "candidate (not checked)",
                   "adjacent": "adjacent", "out": "out", "planned": "planned"},
        "unverified": "unverified", "no_source": "no source", "not_in": "not in %s",
        "out": "Filtered out", "no_reason": "no reason given, add one",
        "planned": "Planned position (a plan, not a finding)",
        "not_plotted": "Not on the map (no number for %s or %s): %s.",
        "unverified_note": "Unverified (no evidence link): %s. Listed last and never proposed. "
                           "Open the product's own page and add evidence_url, or drop the row.",
        "fix": "Fix in the CSV",
        "map_title": "Positioning map",
        "legend": {"fit": "sourced", "adjacent": "adjacent", "hollow": "no source, not a finding",
                   "confirmed": "confirmed", "planned": "planned (yours)"},
        "map_note": "Values from the linked public pages in the landscape matrix.",
        "p_status": "line %d: status '%s' is not candidate/fit/adjacent/out/confirmed/planned, "
                    "read as candidate",
        "p_bad_url": "line %d: %s '%s' is not an http(s) link, ignored",
        "p_no_evidence": "line %d: %s is marked %s but has no evidence_url, so it is not proposed",
        "p_price": "line %d: %s has a price but no price_url",
        "p_guess": "line %d: %s %s '%s' has '%s', a guess: keep only what the page prints",
        "p_axis": "line %d: %s has a value for %s but no axis_url",
        "p_number": "line %d: %s '%s' for %s is not a number, so it is not on the map",
        "p_read_on": "line %d: read_on '%s' is not a date like 2026-10-17",
        "p_market": "line %d: %s is marked %s, but its market '%s' does not include %s, so it "
                    "is not proposed",
        "p_no_market": "line %d: %s is marked %s but has no market, so it is not proposed",
        "p_duplicate": "line %d: %s is already on line %d, dropped",
        "p_example": "line %d: %s is the sample row (.example), dropped",
        "p_company": "line %d: %s has company facts but no company_url",
        "companies": "Companies behind the products",
        "company_labels": {"company": "company", "seat": "seat", "founded": "founded",
                           "size": "size"},
        "source": "source",
    },
    "de": {
        "title": "Marktüberblick", "title_for": "Marktüberblick: %s",
        "summary": "Produkte: %d, mit Beleg: %d, ungeprüft: %d.",
        "market": "Markt geprüft gegen: %s.",
        "proposal": "Vorschlag für die Analyse (nur belegt und passend, höchstens %d)",
        "proposal_none": "Noch kein Vorschlag möglich: keine Zeile ist belegt und als passend "
                         "markiert. Kandidaten gegen die fünf Kriterien prüfen (status) und "
                         "Beleg-Links ergänzen.",
        "proposal_few": "Belegt und passend: nur %d. Weiter suchen oder offen sagen, dass der "
                        "Markt dünn ist.",
        "evidence": "Beleg",
        "next": "Nächster Schritt: bestätigen, welche Produkte analysiert werden, und fehlende "
                "Produkte nennen. Recon startet erst nach dieser Antwort.",
        "confirmed": "Für die Analyse bestätigt: %s. Nächster Schritt: Recon.",
        "matrix": "Marktmatrix",
        "cols": ["#", "Produkt", "Kategorie", "Zielkunde", "Markt", "Sprachen", "Preis ab",
                 "Preismodell", "Status", "Beleg", "gelesen am"],
        "status": {"confirmed": "bestätigt", "fit": "passt", "candidate": "Kandidat (ungeprüft)",
                   "adjacent": "angrenzend", "out": "raus", "planned": "geplant"},
        "unverified": "ungeprüft", "no_source": "ohne Beleg", "not_in": "nicht in %s",
        "out": "Aussortiert", "no_reason": "kein Grund angegeben, bitte ergänzen",
        "planned": "Geplante Position (ein Plan, kein Befund)",
        "not_plotted": "Nicht auf der Karte (keine Zahl für %s oder %s): %s.",
        "unverified_note": "Ungeprüft (kein Beleg-Link): %s. Steht am Ende und wird nie "
                           "vorgeschlagen. Die eigene Seite des Produkts öffnen und evidence_url "
                           "ergänzen, oder die Zeile streichen.",
        "fix": "In der CSV korrigieren",
        "map_title": "Positionierungskarte",
        "legend": {"fit": "belegt", "adjacent": "angrenzend", "hollow": "ohne Beleg, kein Befund",
                   "confirmed": "bestätigt", "planned": "geplant (eigenes Produkt)"},
        "map_note": "Werte von den verlinkten öffentlichen Seiten in der Marktmatrix.",
        "p_status": "Zeile %d: Status '%s' ist nicht Kandidat/passt/angrenzend/raus/bestätigt/"
                    "geplant, als Kandidat gelesen",
        "p_bad_url": "Zeile %d: %s '%s' ist kein http(s)-Link, ignoriert",
        "p_no_evidence": "Zeile %d: %s ist als %s markiert, hat aber keine evidence_url und wird "
                         "nicht vorgeschlagen",
        "p_price": "Zeile %d: %s hat einen Preis, aber keine price_url",
        "p_guess": "Zeile %d: %s %s '%s' enthält '%s', eine Vermutung: nur übernehmen, was "
                   "die Seite druckt",
        "p_axis": "Zeile %d: %s hat einen Wert für %s, aber keine axis_url",
        "p_number": "Zeile %d: %s '%s' für %s ist keine Zahl und steht nicht auf der Karte",
        "p_read_on": "Zeile %d: read_on '%s' ist kein Datum wie 2026-10-17",
        "p_market": "Zeile %d: %s ist als %s markiert, aber der Markt '%s' enthält %s nicht und "
                    "wird nicht vorgeschlagen",
        "p_no_market": "Zeile %d: %s ist als %s markiert, hat aber keinen Markt und wird nicht "
                       "vorgeschlagen",
        "p_duplicate": "Zeile %d: %s steht schon in Zeile %d, verworfen",
        "p_example": "Zeile %d: %s ist die Beispielzeile (.example), verworfen",
        "p_company": "Zeile %d: %s hat Firmenangaben, aber keine company_url",
        "companies": "Firmen hinter den Produkten",
        "company_labels": {"company": "Firma", "seat": "Sitz", "founded": "gegründet",
                           "size": "Größe"},
        "source": "Quelle",
    },
}


class LandscapeError(Exception):
    pass


def is_url(value):
    return bool(re.match(r"^https?://[^\s/]+\.[^\s]+", value or ""))


def host(url):
    m = re.match(r"^https?://(?:www\.)?([^/?#\s]+)", url or "")
    return m.group(1).lower() if m else ""


def parse_number(text):
    """First number in a cell ('ab 29,90 EUR' -> 29.9), 0 for a leading 'free', else None."""
    t = (text or "").strip()
    if not t:
        return None
    num, free = NUMBER.search(t), FREE.search(t)
    if free and (num is None or free.start() < num.start()):
        return 0.0
    if num is None:
        return None
    s = num.group(0).rstrip(".,'\u2019").replace("'", "").replace("\u2019", "")
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", "") if re.match(r"^\d{1,3}(,\d{3})+$", s) else s.replace(",", ".")
    elif re.match(r"^\d{1,3}(\.\d{3})+$", s):
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


def parse_market(text):
    """'DE, AT', 'DACH', 'EU', 'weltweit' -> set of country codes ('*' = everywhere)."""
    codes = set()
    for tok in re.split(r"[\s,;/+&|()]+", DACH_FORMS.sub(" DACH ", (text or "").strip())):
        low = tok.lower()
        if low in REGIONS:
            codes |= REGIONS[low]
        elif re.match(r"^[A-Za-z]{2}$", tok) and (tok.isupper() or low not in NOT_CODES):
            codes.add(tok.upper())
    return codes


def covers(row_codes, user_codes):
    """True or False, or None when the row names no market."""
    if not row_codes:
        return None
    if EVERYWHERE in row_codes or EVERYWHERE in user_codes:
        return True
    return bool(row_codes & user_codes)


def axis_source(row, col):
    """The URL a value in column col comes from, or ''."""
    if col == "price_from":
        return row["price_url"]
    if col in ("axis_x", "axis_y"):
        urls = [u for u in row.get("axis_url", "").split() if is_url(u)]
        if not urls:
            return ""
        return urls[1] if col == "axis_y" and len(urls) > 1 else urls[0]
    return row["evidence_url"]


def load(path):
    """Return (rows, header fields in lower case)."""
    try:
        return _load(path)
    except UnicodeDecodeError:
        raise LandscapeError(NOT_UTF8 % path)


NOT_UTF8 = ("%s is not UTF-8. Excel's 'CSV (Trennzeichen-getrennt)' saves Windows-1252: "
            "save it again as 'CSV UTF-8 (durch Trennzeichen getrennt)' and run again")


def _load(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        # German Excel exports use ";". Decide from the header line only.
        header = fh.readline()
        fh.seek(0)
        delim = max(",;\t", key=header.count) if header.strip() else ","
        reader = csv.DictReader(fh, delimiter=delim)
        if reader.fieldnames is None:
            raise LandscapeError("%s is empty" % path)
        fields = [(f or "").strip().lower() for f in reader.fieldnames]
        for need in REQUIRED:
            if need not in fields:
                raise LandscapeError(
                    "%s has no '%s' column. Every product needs its name, its homepage and "
                    "the public page the claims come from: name,url,evidence_url,..."
                    % (path, need))
        rows = []
        for i, raw in enumerate(reader, start=2):
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()
                   if not isinstance(v, list)}
            if not row.get("name"):
                continue
            row["line"] = i
            rows.append(row)
    return rows, fields


def analyse(rows, lang="en", market=None, axes=None):
    """Classify, check and sort the rows. axes = (x column, y column) or None."""
    T = TEXT.get(lang, TEXT["en"])
    problems = []
    user_codes = parse_market(market) if market else None
    seen = {}
    listed, out, planned = [], [], []
    for raw in rows:
        line, name = raw["line"], raw["name"]
        if host(raw.get("url", "")).endswith(".example"):
            problems.append((line, T["p_example"] % (line, name)))
            continue
        key = re.sub(r"\W+", " ", name.casefold()).strip()
        if key in seen:
            problems.append((line, T["p_duplicate"] % (line, name, seen[key])))
            continue
        seen[key] = line
        r = {k: raw.get(k, "") for k in COLUMNS}
        for col in axes or ():          # a custom numeric column for the map
            r.setdefault(col, raw.get(col, ""))
        r["line"] = line
        for col in ("url", "evidence_url", "price_url"):
            if r[col] and not is_url(r[col]):
                problems.append((line, T["p_bad_url"] % (line, col, r[col])))
                r[col] = ""
        for u in r["company_url"].split():
            if not is_url(u):
                problems.append((line, T["p_bad_url"] % (line, "company_url", u)))
        r["company_url"] = " ".join(u for u in r["company_url"].split() if is_url(u))
        if any(r[c] for c in COMPANY) and not r["company_url"]:
            problems.append((line, T["p_company"] % (line, name)))
        raw_status = raw.get("status", "").lower()
        if raw_status not in STATUS:
            problems.append((line, T["p_status"] % (line, raw.get("status", ""))))
        r["status"] = STATUS.get(raw_status, "candidate")
        r["verified"] = bool(r["evidence_url"])
        if r["read_on"] and not DATE.match(r["read_on"]):
            problems.append((line, T["p_read_on"] % (line, r["read_on"])))
        if r["status"] == "planned":
            planned.append(r)
            continue
        for col in ("price_from", "price_model"):
            guess = GUESS.search(r[col])
            if guess:
                problems.append((line, T["p_guess"] % (line, name, col, r[col],
                                                       guess.group(0))))
        if r["status"] == "out":
            out.append(r)
            continue
        if r["price_from"] and not r["price_url"]:
            problems.append((line, T["p_price"] % (line, name)))
        r["market_ok"] = covers(parse_market(r["market"]), user_codes) if user_codes else True
        if r["status"] in PROPOSE:
            label = T["status"][r["status"]]
            if not r["verified"]:
                problems.append((line, T["p_no_evidence"] % (line, name, label)))
            elif r["market_ok"] is None:
                problems.append((line, T["p_no_market"] % (line, name, label)))
            elif r["market_ok"] is False:
                problems.append((line, T["p_market"] % (line, name, label, r["market"],
                                                        market)))
        listed.append(r)

    def order(r):
        mk = {True: 0, None: 1, False: 2}[r["market_ok"]]
        return (0 if r["verified"] else 1, mk, RANK[r["status"]], r["name"].casefold())

    listed.sort(key=order)
    out.sort(key=lambda r: r["name"].casefold())
    proposal = [r for r in listed
                if r["verified"] and r["status"] in PROPOSE and r["market_ok"] is True]
    proposal = proposal[:MAX_PROPOSAL]
    result = {
        "market": market or None,
        "counts": {"listed": len(listed),
                   "verified": sum(1 for r in listed if r["verified"]),
                   "unverified": sum(1 for r in listed if not r["verified"]),
                   "out": len(out), "planned": len(planned)},
        "proposal": [r["name"] for r in proposal],
        "confirmed": [r["name"] for r in proposal if r["status"] == "confirmed"],
        "rows": listed, "out": out, "planned": planned,
    }
    if axes:
        result["map"] = plot_points(listed + planned, axes, problems, T)
    result["problems"] = [msg for _, msg in sorted(problems, key=lambda p: p[0])]
    return result


def plot_points(rows, axes, problems, T):
    xcol, ycol = axes
    points, missing = [], []
    for r in rows:
        vals, ok = [], True
        line = r["line"]
        for col in (xcol, ycol):
            raw = r.get(col, "")
            v = parse_number(raw)
            if v is None:
                if raw:
                    problems.append((line, T["p_number"] % (line, col, raw, r["name"])))
                ok = False
            elif r["status"] != "planned" and col.startswith("axis") and not axis_source(r, col):
                problems.append((line, T["p_axis"] % (line, r["name"], col)))
            vals.append(v)
        if not ok:
            missing.append(r["name"])
            continue
        sourced = r["status"] == "planned" or (
            r["verified"] and all(axis_source(r, c) for c in (xcol, ycol)))
        points.append({"name": r["name"], "x": vals[0], "y": vals[1],
                       "status": r["status"], "sourced": bool(sourced)})
    return {"x": xcol, "y": ycol, "points": points, "not_plotted": missing}


# ---------------------------------------------------------------- rendering


def _cell(text):
    return (text or "").replace("|", "\\|").replace("\n", " ").strip() or "-"


def _link(text, url):
    target = url.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
    return "[%s](%s)" % (_cell(text), target)


def _num(x, lang):
    s = ("%.2f" % x).rstrip("0").rstrip(".")
    return s.replace(".", ",") if lang == "de" else s


def _sourced(value, url, T):
    if not value:
        return "-"
    return _link(value, url) if url else "%s (%s)" % (_cell(value), T["no_source"])


def render(result, lang="en", title=None, labels=None):
    T = TEXT.get(lang, TEXT["en"])
    c = result["counts"]
    out = ["# " + (T["title_for"] % title if title else T["title"]), ""]
    line = T["summary"] % (c["listed"], c["verified"], c["unverified"])
    if result["market"]:
        line += " " + T["market"] % result["market"]
    out += [line, "", "## " + T["proposal"] % MAX_PROPOSAL, ""]
    rows_by_name = {r["name"]: r for r in result["rows"]}
    if not result["proposal"]:
        out.append(T["proposal_none"])
    for name in result["proposal"]:
        r = rows_by_name[name]
        box = "[x]" if r["status"] == "confirmed" else "[ ]"
        head = _link(name, r["url"]) if r["url"] else _cell(name)
        reason = (": " + _cell(r["notes"])) if r["notes"] else ""
        out.append("- %s %s%s (%s: %s)" % (box, head, reason, T["evidence"],
                                          _link(host(r["evidence_url"]), r["evidence_url"])))
    if result["proposal"]:
        if len(result["proposal"]) < MIN_PROPOSAL:
            out += ["", T["proposal_few"] % len(result["proposal"])]
        out += ["", T["confirmed"] % ", ".join(result["confirmed"]) if result["confirmed"]
                else T["next"]]

    axes = result.get("map")
    cols = list(T["cols"])
    extra = []
    if axes:
        names = dict(zip((axes["x"], axes["y"]), labels or (axes["x"], axes["y"])))
        extra = [c for c in names if c != "price_from"]
        cols[8:8] = [names[c] for c in extra]
    out += ["", "## " + T["matrix"], "",
            "| " + " | ".join(_cell(x) for x in cols) + " |", "|" + " --- |" * len(cols)]
    for i, r in enumerate(result["rows"], start=1):
        market = _cell(r["market"])
        if r["market_ok"] is False:
            market += " (%s)" % (T["not_in"] % result["market"])
        cells = [str(i), _link(r["name"], r["url"]) if r["url"] else _cell(r["name"]),
                 _cell(r["category"]), _cell(r["customer"]), market, _cell(r["languages"]),
                 _sourced(r["price_from"], r["price_url"], T), _cell(r["price_model"])]
        for col in extra:
            cells.append(_sourced(r.get(col, ""), axis_source(r, col), T))
        cells += [T["status"][r["status"]],
                  _link(host(r["evidence_url"]), r["evidence_url"]) if r["verified"]
                  else "**%s**" % T["unverified"],
                  _cell(r["read_on"])]
        out.append("| " + " | ".join(cells) + " |")

    unverified = [r["name"] for r in result["rows"] if not r["verified"]]
    if unverified:
        out += ["", T["unverified_note"] % "; ".join(unverified)]
    if result["out"]:
        out += ["", "## " + T["out"], ""]
        for r in result["out"]:
            out.append("- %s: %s" % (_cell(r["name"]), _cell(r["notes"]) if r["notes"]
                                     else T["no_reason"]))
    if result["planned"]:
        out += ["", "## " + T["planned"], ""]
        for r in result["planned"]:
            note = (": " + _cell(r["notes"])) if r["notes"] else ""
            out.append("- %s%s" % (_cell(r["name"]), note))
    firms = [r for r in result["rows"] + result["out"] if any(r.get(c) for c in COMPANY)]
    if firms:
        out += ["", "## " + T["companies"], ""]
        for r in firms:
            facts = ", ".join("%s %s" % (T["company_labels"][c], _cell(r[c]))
                              for c in COMPANY if r[c])
            src = ", ".join(_link(host(u), u) for u in r["company_url"].split())
            out.append("- %s: %s (%s)" % (_cell(r["name"]), facts,
                                          "%s: %s" % (T["source"], src) if src
                                          else T["no_source"]))
    if axes and axes["not_plotted"]:
        xl, yl = labels or (axes["x"], axes["y"])
        out += ["", T["not_plotted"] % (xl, yl, "; ".join(axes["not_plotted"]))]
    if result["problems"]:
        out += ["", "## " + T["fix"], ""] + ["- %s" % p for p in result["problems"]]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------- map

W, H = 800, 560
X0, X1, Y0, Y1 = 80, 690, 64, 440
INK, GRID, MUTED = "#1f2933", "#e4e7eb", "#7b8794"
SOURCED, ADJACENT, PLANNED = "#1f5f99", "#8fb3d9", "#c2410c"
FONT = "system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
CHAR_W, LINE_H = 6.6, 14


def ticks(values):
    lo, hi = min(0.0, min(values)), max(values)
    if hi <= lo:
        hi = lo + 1.0
    raw = (hi - lo) / 5.0
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 5, 10) if raw <= m * mag * (1 + 1e-9))
    k0 = int(math.floor(lo / step + 1e-9))
    k1 = int(math.ceil(hi / step - 1e-9))
    if k1 * step <= hi + 1e-9:  # a point on the top edge: leave room for its label
        k1 += 1
    return [k * step for k in range(k0, k1 + 1)]


def _esc(text):
    return escape(text or "", {'"': "&quot;"})


def _overlaps(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def _place(px, py, text, placed):
    w = CHAR_W * len(text) + 2
    cands = [(px + 13, py + 4), (px - 13 - w, py + 4), (px - w / 2, py - 14),
             (px - w / 2, py + 24)]
    for i in range(1, 6):
        cands += [(px + 13, py + 4 + i * LINE_H), (px + 13, py + 4 - i * LINE_H)]
    for tx, ty in cands:
        box = (tx, ty - 11, tx + w, ty + 3)
        if box[0] >= 4 and box[2] <= W - 4 and box[1] >= Y0 - 20 and box[3] <= Y1 + 4 \
                and not any(_overlaps(box, b) for b in placed):
            placed.append(box)
            return tx, ty
    tx, ty = cands[0]
    placed.append((tx, ty - 11, tx + w, ty + 3))
    return tx, ty


def render_svg(mapdata, lang="en", title=None, labels=None):
    T = TEXT.get(lang, TEXT["en"])
    pts = mapdata["points"]
    xl, yl = labels or (mapdata["x"], mapdata["y"])
    xt, yt = ticks([p["x"] for p in pts]), ticks([p["y"] for p in pts])

    def sx(v):
        return X0 + (v - xt[0]) / (xt[-1] - xt[0]) * (X1 - X0)

    def sy(v):
        return Y1 - (v - yt[0]) / (yt[-1] - yt[0]) * (Y1 - Y0)

    head = T["map_title"] + (": " + title if title else "")
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'role="img" aria-labelledby="map-title" font-family="%s">' % (W, H, W, H, _esc(FONT)),
         '<title id="map-title">%s</title>' % _esc(head),
         '<rect width="%d" height="%d" fill="#ffffff"/>' % (W, H),
         '<text x="%d" y="34" font-size="16" font-weight="600" fill="%s">%s</text>'
         % (X0, INK, _esc(head))]
    for v in xt:
        x = sx(v)
        o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s"/>' % (x, Y0, x, Y1, GRID))
        o.append('<text x="%.1f" y="%d" font-size="11" fill="%s" text-anchor="middle">%s</text>'
                 % (x, Y1 + 18, MUTED, _num(v, lang)))
    for v in yt:
        y = sy(v)
        o.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s"/>' % (X0, y, X1, y, GRID))
        o.append('<text x="%d" y="%.1f" font-size="11" fill="%s" text-anchor="end">%s</text>'
                 % (X0 - 8, y + 4, MUTED, _num(v, lang)))
    o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s"/>' % (X0, Y1, X1, Y1, INK))
    o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s"/>' % (X0, Y0, X0, Y1, INK))
    o.append('<text x="%d" y="%d" font-size="13" fill="%s" text-anchor="middle">%s</text>'
             % ((X0 + X1) // 2, Y1 + 42, INK, _esc(xl)))
    o.append('<text x="22" y="%d" font-size="13" fill="%s" text-anchor="middle" '
             'transform="rotate(-90 22 %d)">%s</text>'
             % ((Y0 + Y1) // 2, INK, (Y0 + Y1) // 2, _esc(yl)))

    placed, labels_out = [], []
    for p in pts:
        x, y = sx(p["x"]), sy(p["y"])
        if p["status"] == "planned":
            o.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                     % (x, y - 8, x + 8, y, x, y + 8, x - 8, y, PLANNED))
        elif not p["sourced"]:
            o.append('<circle cx="%.1f" cy="%.1f" r="6" fill="#ffffff" stroke="%s" '
                     'stroke-width="1.5" stroke-dasharray="3 2"/>' % (x, y, MUTED))
        else:
            fill = ADJACENT if p["status"] == "adjacent" else SOURCED
            o.append('<circle cx="%.1f" cy="%.1f" r="6" fill="%s"/>' % (x, y, fill))
            if p["status"] == "confirmed":
                o.append('<circle cx="%.1f" cy="%.1f" r="10" fill="none" stroke="%s" '
                         'stroke-width="2"/>' % (x, y, SOURCED))
        tx, ty = _place(x, y, p["name"], placed)
        colour = INK if p["sourced"] else MUTED
        style = '' if p["sourced"] else ' font-style="italic"'
        labels_out.append('<text x="%.1f" y="%.1f" font-size="12" fill="%s"%s>%s</text>'
                          % (tx, ty, colour, style, _esc(p["name"])))
    o += labels_out

    present = set()
    for p in pts:
        if p["status"] == "planned":
            present.add("planned")
        elif not p["sourced"]:
            present.add("hollow")
        else:
            present.add("adjacent" if p["status"] == "adjacent" else "fit")
            if p["status"] == "confirmed":
                present.add("confirmed")
    lx, ly = X0, H - 44
    for key in ("fit", "confirmed", "adjacent", "hollow", "planned"):
        if key not in present:
            continue
        if key == "planned":
            o.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s"/>'
                     % (lx, ly - 7, lx + 7, ly, lx, ly + 7, lx - 7, ly, PLANNED))
        elif key == "hollow":
            o.append('<circle cx="%d" cy="%d" r="6" fill="#ffffff" stroke="%s" '
                     'stroke-width="1.5" stroke-dasharray="3 2"/>' % (lx, ly, MUTED))
        elif key == "confirmed":
            o.append('<circle cx="%d" cy="%d" r="6" fill="%s"/><circle cx="%d" cy="%d" r="10" '
                     'fill="none" stroke="%s" stroke-width="2"/>'
                     % (lx, ly, SOURCED, lx, ly, SOURCED))
        else:
            o.append('<circle cx="%d" cy="%d" r="6" fill="%s"/>'
                     % (lx, ly, ADJACENT if key == "adjacent" else SOURCED))
        text = T["legend"][key]
        o.append('<text x="%d" y="%d" font-size="12" fill="%s">%s</text>'
                 % (lx + 14, ly + 4, INK, _esc(text)))
        lx += int(28 + CHAR_W * len(text) + 18)
    o.append('<text x="%d" y="%d" font-size="11" fill="%s">%s</text>'
             % (X0, H - 14, MUTED, _esc(T["map_note"])))
    o.append("</svg>")
    return "\n".join(o) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("competitors", help="teardown/competitors.csv")
    ap.add_argument("--lang", choices=sorted(TEXT), default="en")
    ap.add_argument("--market", help="the user's market, e.g. DE, DACH, EU, \"DE,AT\"")
    ap.add_argument("--title", help="the niche or market, for the headings")
    ap.add_argument("--svg", help="write the positioning map to this SVG file")
    ap.add_argument("--x", default="axis_x", help="numeric column for the x axis (default axis_x)")
    ap.add_argument("--y", default="axis_y", help="numeric column for the y axis (default axis_y)")
    ap.add_argument("--x-label", help="x axis label: what is measured, and how")
    ap.add_argument("--y-label", help="y axis label: what is measured, and how")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", help="write the report (or the JSON) to this file")
    args = ap.parse_args(argv)
    try:
        if args.market and not parse_market(args.market):
            raise LandscapeError("--market '%s' names no country or region (use codes like "
                                 "DE, AT, CH or DACH, EU, global)" % args.market)
        rows, fields = load(args.competitors)
        axes = None
        if args.svg:
            for col in (args.x, args.y):
                if col.lower() not in fields:
                    raise LandscapeError("%s has no '%s' column for the map"
                                         % (args.competitors, col))
            axes = (args.x.lower(), args.y.lower())
        result = analyse(rows, lang=args.lang, market=args.market, axes=axes)
        if axes and not result["map"]["points"]:
            raise LandscapeError("no row has a number in both %s and %s, so there is no map"
                                 % axes)
    except (LandscapeError, OSError, ValueError) as exc:
        print("landscape: %s" % exc, file=sys.stderr)
        return 2
    labels = None
    if axes:
        labels = (args.x_label or axes[0], args.y_label or axes[1])
        with open(args.svg, "w", encoding="utf-8") as fh:
            fh.write(render_svg(result["map"], lang=args.lang, title=args.title, labels=labels))
        print("wrote %s" % args.svg, file=sys.stdout if args.out else sys.stderr)
    if args.json:
        text = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        text = render(result, lang=args.lang, title=args.title, labels=labels)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text if text.endswith("\n") else text + "\n")
        print("wrote %s" % args.out)
    else:
        sys.stdout.write(text if text.endswith("\n") else text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
