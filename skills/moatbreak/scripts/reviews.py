#!/usr/bin/env python3
"""Voice-of-customer ranker for the Moatbreak skill. Standard library only.

Takes real reviews you collected about a competitor (app, SaaS, website or
online shop) and ranks what its users hate and what they keep asking for,
with the exact words and a link for every claim. English and German reviews
are themed out of the box; add more languages in themes.json.

Origin and licence: see NOTICE.md and LICENSE.

    python3 reviews.py teardown/reviews.csv
    python3 reviews.py teardown/reviews.csv --lang de --as-of 2026-10-17 --out teardown/feedback.md
    python3 reviews.py teardown/reviews.csv --as-of 2026-10-17 --json --out teardown/feedback.json
    python3 reviews.py teardown/reviews.csv --themes my-themes.json
    python3 reviews.py teardown/reviews.csv --verify teardown/fixes.md

CSV columns (extra columns are ignored, header names are case-insensitive and
German headers work too):

    source   app-store, google-play, g2, capterra, trustpilot, omr, reddit,
             trusted-shops, google-maps, ...        (quelle; "App Store" = app-store)
    url      link to the review or thread. Required. (link)
    date     2026-08-01, 2026-08 or 01.08.2026       (datum)
    rating   4, 4.5, 4,5, 4/5, 8/10, "4 Sterne", ★★★★☆ (bewertung, sterne, stars)
    text     the review, copied exactly. Required.  (review, inhalt, kommentar)
    segment  optional: the reviewer's role or company size exactly as the
             platform shows it ("Inhaber, 2-10 Mitarbeiter"), never guessed;
             empty where it shows none                (role, rolle, company size)

A row without a url or without text is dropped and counted, never guessed.
This tool only reorganises what you give it. It does not write, translate or
paraphrase reviews, and every quote it prints is a substring of a row you
supplied, with that row's link.

Praise is not a complaint: a 4.5-5 star review never counts toward a
complaint theme, and a 4 star review only when the matching sentence has a
"but" (but, unfortunately, aber, leider, ...). Those mentions are reported as
praise instead, which shows where the original is strong, under the theme's
praise_label ("Fast, no waiting", not "Slow, laggy, heavy") where it has one.

Ranking: every review that matches a theme adds a weight. A 1 star review adds
1.0, a 5 star review 0.2, an unrated one 0.6. Reviews older than --months
(default 18) count half; ages are counted from --as-of (default today, pass it
for reproducible runs; --today is the old name; without it the report says so
and the JSON has "as_of_today": true). Themes with fewer than 3
reviews, or all from one source, are marked thin.

Sample by source: per source the number of reviews, its share, its average
stars and its date range. The report warns when one source supplies more than
60% of the sample, when a source's average is 1 star or more away from the
average of all rated reviews, and when more than 70% of the dated reviews are
from the last 90 days or older than --months, because one platform's audience
or one bad month is not the market.

Segments: with a segment column, the report counts the sample and every
theme per segment ("Who says it"), and marks a segment with fewer than 3
reviews as thin.

Why they leave: reviews that say the writer left, cancelled or is looking for
something else (switch_patterns in themes.json; the shipped ones are written
in the first person, so "the salon cancelled my appointment" is not a writer
leaving). Each is quoted with its sentence and link, with the alternative it
names (only words that stand where a pattern has {alt} and start with a
capital letter or digit, copied from the review, never guessed; a number
alone or a common word such as Konkurrenten or Dark Mode is not a name) and
the themes the same review complains about. High ratings, and alternatives
that are --target itself, are listed apart: those are people coming to the
original, not leaving it.

--verify FILE checks a report written from these reviews (fixes.md, an offer,
a battle card): every quoted text on a line with a link must stand word for
word in a review with that link, whole words only, "..." standing for
left-out words. It lists what is not found and exits 1, so a paraphrase
cannot pass as a quote, and neither can "helpful" cut out of "unhelpful".

--json writes the analysis as JSON (to --out, as UTF-8, or to stdout).
"""

import argparse
import csv
import datetime as _dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_THEMES = os.path.join(HERE, "themes.json")
SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
DOMINANT_SHARE = 0.6
RATING_GAP = 1.0
RECENT_DAYS = 90
BUNCHED_SHARE = 0.7
UNTHEMED_MAX_RATING = 3
# What {alt} in a switch pattern stands for: up to four words, cut by name_in().
ALT = r"(?P<alt>[^\s,;:!?()\[\]\"„“”]+(?: [^\s,;:!?()\[\]\"„“”]+){0,3})"
QUOTED = re.compile(r'"([^"\n]+)"|„([^“”"\n]+)[“”"]|“([^”\n]+)”|«([^»\n]+)»')
LINK = re.compile(r"https?://[^\s<>()\[\]\"]+")
GAP = re.compile(r"\s*(?:\[\.\.\.\]|\[…\]|\.\.\.|…)\s*")
CONTRAST = re.compile(r"\b(but|however|unfortunately|sadly|except|only|wish|aber|leider|jedoch|"
                      r"allerdings|nur|bis auf|schade|trotzdem)\b", re.I)
# Capitalised words that stand where a product name could, but are not one.
NOT_A_NAME = frozenset((
    "another", "other", "alternative", "alternatives", "competitor", "competitors",
    "competition", "app", "apps", "tool", "tools", "software", "program", "provider",
    "service", "platform", "system", "solution", "dark", "light", "mode", "settings",
    "version", "pro", "premium", "plus", "basic", "free", "business", "enterprise",
    "konkurrent", "konkurrenten", "konkurrenz", "wettbewerber", "wettbewerbern",
    "mitbewerber", "anbieter", "anbietern", "alternativen", "programm", "lösung",
    "dunkelmodus", "einstellungen"))
MIN_SEGMENT = 3

COLUMN_ALIASES = {
    "source": ("source", "quelle", "plattform", "platform"),
    "url": ("url", "link", "href"),
    "date": ("date", "datum"),
    "rating": ("rating", "bewertung", "sterne", "stars", "score"),
    "text": ("text", "review", "inhalt", "kommentar", "comment", "body", "content"),
    "segment": ("segment", "reviewer segment", "role", "rolle", "company size",
                "unternehmensgröße", "firmengröße"),
}

TEXT = {
    "en": {
        "title": "# {target}: what customers hate and ask for",
        "summary": "{n} reviews from {s} sources ({names}). {rated} had star ratings.",
        "dropped": "{n} rows dropped: no link or no text. Nothing is counted without its source.",
        "dupes": "{n} duplicate reviews removed.",
        "small": "Small sample. Under 30 reviews supports a direction, not a ranking. "
                 "Collect more before you bet the roadmap on it.",
        "dominant": "{share:.0f}% of the reviews come from {source}. One platform's audience "
                    "is not the whole market: add other sources before ranking.",
        "by_source": "## Sample by source",
        "source_head": "| source | reviews | share | avg stars | from | to |",
        "all_sources": "all",
        "dates": "{dated} of {n} reviews have a date, from {first} to {last}. Ages are counted "
                 "from {as_of}.",
        "as_of_today": " No --as-of was given, so that is the day of this run: pass --as-of "
                       "to get the same report from the same sheet on another day.",
        "no_dates": "No review has a date, so the age of the sample is unknown.",
        "lean": "How the sample leans:",
        "gap": "{source} gives {avg} stars on average, {gap} stars {dir} than all rated reviews "
               "together ({overall}; {n} rated reviews there). A different crowd writes there: "
               "check that its complaints show up in other sources too.",
        "higher": "higher",
        "lower": "lower",
        "recent": "{share:.0f}% of the dated reviews are from the last {days} days (since "
                  "{since}). That can be one update, outage or price change talking, not the "
                  "long-term picture.",
        "old": "{share:.0f}% of the dated reviews are older than {months} months (before "
               "{before}). The product may have changed since: check its changelog before "
               "calling anything unfixed.",
        "no_lean": "No lean found: no source has more than 60% of the reviews, and none is 1 star "
                   "or more away from the overall average.",
        "no_lean_dates": " The dates are not bunched in the last {days} days or before {before}.",
        "switch": "Why they leave",
        "switch_note": "Reviews that say the writer left, cancelled or is looking for something "
                       "else, one sentence each, as written. An alternative is shown only where "
                       "the review names it.",
        "switch_none": "No review says the writer left or switched. Searches like 'X alternative', "
                       "'switched from X' or 'X kündigen' find these.",
        "switch_count": "{n} reviews say the writer left or wants to.",
        "switch_reasons": "The same reviews complain about: {items}.",
        "switch_alts": "Where they say they went: {items}.",
        "switch_named": "named: {name}",
        "switch_in": "Switched to {target} (why people come, not why they leave):",
        "switch_target": "the original",
        "verify_ok": "{checked} linked quotes in {file} checked: all stand word for word in {csv}.",
        "verify_bad": "{checked} linked quotes in {file} checked: {bad} do not stand word for word "
                      "in {csv}. Fix or remove them before anything is sent.",
        "verify_none": "No linked quote found in {file}. Put the quote in quote marks and the "
                       "review's link on the same line.",
        "not_found": "line {line}: \"{quote}\" is not in the review at {url}",
        "unknown_url": "line {line}: {url} is not a review link in {csv}",
        "complaint": "What they hate",
        "request": "What they ask for",
        "nothing": "Nothing matched. Read the reviews by hand.",
        "table_head": "| rank | theme | score | reviews | share | avg stars | sources |",
        "thin": " (thin)",
        "asked": "## Asked for in their own words",
        "by_hand": "## Read these by hand",
        "by_hand_note": "Ratings of 3 stars or less that matched no theme. Either noise, "
                        "or a theme themes.json does not have yet. Often the most useful part.",
        "target": "The original",
        "praise": "What they praise",
        "praise_note": "Themes mentioned in 4-5 star reviews without a complaint. Do not "
                       "compete where the original is loved; match it.",
        "multi": "A review can match several themes, so shares add up to more than 100%.",
        "by_segment": "## Sample by segment",
        "segment_note": "Who wrote the reviews, as the platform shows it (role, company size), "
                        "never guessed. A segment with fewer than 3 reviews is thin: an "
                        "anecdote, not that segment's view.",
        "segment_head": "| segment | reviews | share | avg stars |",
        "not_shown": "not shown",
        "who": "Who says it: {items}.",
    },
    "de": {
        "title": "# {target}: was Kunden stört und was sie sich wünschen",
        "summary": "{n} Bewertungen aus {s} Quellen ({names}). {rated} davon mit Sternen.",
        "dropped": "{n} Zeilen verworfen: ohne Link oder ohne Text. Ohne Quelle zählt nichts.",
        "dupes": "{n} doppelte Bewertungen entfernt.",
        "small": "Kleine Stichprobe. Unter 30 Bewertungen zeigen eine Richtung, keine "
                 "Rangfolge. Erst mehr sammeln, dann die Roadmap darauf bauen.",
        "dominant": "{share:.0f}% der Bewertungen stammen von {source}. Das Publikum einer "
                    "Plattform ist nicht der ganze Markt: weitere Quellen ergänzen.",
        "by_source": "## Stichprobe nach Quelle",
        "source_head": "| Quelle | Bewertungen | Anteil | Ø Sterne | von | bis |",
        "all_sources": "alle",
        "dates": "{dated} von {n} Bewertungen haben ein Datum, vom {first} bis {last}. Das Alter "
                 "zählt ab {as_of}.",
        "as_of_today": " Ohne --as-of ist das der Tag dieses Laufs: mit --as-of gibt derselbe "
                       "Bogen auch an einem anderen Tag denselben Bericht.",
        "no_dates": "Keine Bewertung hat ein Datum. Wie alt die Stichprobe ist, bleibt offen.",
        "lean": "Schieflage der Stichprobe:",
        "gap": "{source} vergibt im Schnitt {avg} Sterne, {gap} Sterne {dir} als alle "
               "Bewertungen zusammen ({overall}; dort {n} mit Sternen). Dort schreibt ein anderes "
               "Publikum: prüfen, ob dieselbe Kritik auch in anderen Quellen steht.",
        "higher": "mehr",
        "lower": "weniger",
        "recent": "{share:.0f}% der datierten Bewertungen stammen aus den letzten {days} Tagen "
                  "(seit {since}). Das kann ein einzelnes Update, ein Ausfall oder eine "
                  "Preiserhöhung sein, nicht das langfristige Bild.",
        "old": "{share:.0f}% der datierten Bewertungen sind älter als {months} Monate (vor dem "
               "{before}). Das Produkt kann sich seitdem geändert haben: erst im Changelog "
               "nachsehen, ob es behoben ist.",
        "no_lean": "Keine Schieflage gefunden: keine Quelle hat mehr als 60% der Bewertungen, "
                   "keine liegt 1 Stern oder mehr neben dem Gesamtschnitt.",
        "no_lean_dates": " Die Daten ballen sich nicht in den letzten {days} Tagen oder vor dem "
                         "{before}.",
        "switch": "Warum sie gehen",
        "switch_note": "Bewertungen, in denen jemand schreibt, dass er gewechselt oder gekündigt "
                       "hat oder eine Alternative sucht, je ein Satz im Wortlaut. Eine Alternative "
                       "steht nur da, wo die Bewertung sie nennt.",
        "switch_none": "Keine Bewertung sagt, dass jemand gewechselt oder gekündigt hat. Suchen "
                       "wie 'X Alternative', 'X kündigen' oder 'switched from X' finden solche "
                       "Stimmen.",
        "switch_count": "{n} Bewertungen sagen, dass jemand gegangen ist oder gehen will.",
        "switch_reasons": "Dieselben Bewertungen kritisieren: {items}.",
        "switch_alts": "Wohin sie nach eigener Aussage gewechselt sind: {items}.",
        "switch_named": "genannt: {name}",
        "switch_in": "Gewechselt zu {target} (warum Leute kommen, nicht warum sie gehen):",
        "switch_target": "dem Original",
        "verify_ok": "{checked} verlinkte Zitate in {file} geprüft: alle stehen wörtlich in {csv}.",
        "verify_bad": "{checked} verlinkte Zitate in {file} geprüft: {bad} stehen nicht wörtlich "
                      "in {csv}. Korrigieren oder streichen, bevor etwas rausgeht.",
        "verify_none": "Kein verlinktes Zitat in {file} gefunden. Das Zitat in Anführungszeichen "
                       "setzen und den Link der Bewertung in dieselbe Zeile.",
        "not_found": "Zeile {line}: \"{quote}\" steht nicht in der Bewertung unter {url}",
        "unknown_url": "Zeile {line}: {url} ist kein Bewertungslink in {csv}",
        "complaint": "Was sie stört",
        "request": "Was sie sich wünschen",
        "nothing": "Keine Treffer. Bewertungen von Hand lesen.",
        "table_head": "| Rang | Thema | Score | Bewertungen | Anteil | Ø Sterne | Quellen |",
        "thin": " (dünn)",
        "asked": "## Wünsche im O-Ton",
        "by_hand": "## Von Hand lesen",
        "by_hand_note": "Bewertungen mit 3 Sternen oder weniger ohne Thema. Entweder Rauschen "
                        "oder ein Thema, das in themes.json noch fehlt. Oft der wertvollste Teil.",
        "target": "Das Original",
        "praise": "Was gelobt wird",
        "praise_note": "Themen aus 4-5-Sterne-Bewertungen ohne Kritik. Wo das Original "
                       "geliebt wird, nicht angreifen, sondern mithalten.",
        "multi": "Eine Bewertung kann zu mehreren Themen passen, die Anteile ergeben "
                 "daher zusammen mehr als 100%.",
        "by_segment": "## Stichprobe nach Segment",
        "segment_note": "Wer die Bewertungen geschrieben hat, so wie die Plattform es zeigt "
                        "(Rolle, Unternehmensgröße), nie geraten. Ein Segment mit weniger als "
                        "3 Bewertungen ist dünn: eine Einzelstimme, nicht die Sicht des Segments.",
        "segment_head": "| Segment | Bewertungen | Anteil | Ø Sterne |",
        "not_shown": "nicht angegeben",
        "who": "Wer das sagt: {items}.",
    },
}


class FeedbackError(Exception):
    pass


def _flatten(patterns):
    """themes.json allows a plain list or {"en": [...], "de": [...]}."""
    if isinstance(patterns, dict):
        out = []
        for lang in sorted(patterns):
            out.extend(patterns[lang])
        return out
    return list(patterns or [])


def load_themes(path=DEFAULT_THEMES):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    shipped = {}
    if os.path.abspath(path) != DEFAULT_THEMES:
        # a copy made before praise_label existed gets the shipped one for an unchanged theme
        with open(DEFAULT_THEMES, encoding="utf-8") as fh:
            shipped = {t["id"]: t for t in json.load(fh)["themes"]}
    themes = []
    for t in data.get("themes", []):
        label = t.get("label", t["id"])
        ship = shipped.get(t["id"], {})
        themes.append({
            "id": t["id"],
            "label": label,
            "praise_label": t.get("praise_label") or (
                ship.get("praise_label") if ship.get("label") == label else None) or label,
            "kind": t.get("kind", "complaint"),
            "patterns": [re.compile(p, re.I) for p in _flatten(t.get("patterns"))],
        })
    requests = [re.compile(p, re.I) for p in _flatten(data.get("request_patterns"))]
    return themes, requests


def load_switching(path=DEFAULT_THEMES):
    """switch_patterns as [(regex, names_alternative)]. A themes file copied
    before switch_patterns existed gets the shipped ones."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if "switch_patterns" not in data and os.path.abspath(path) != DEFAULT_THEMES:
        return load_switching(DEFAULT_THEMES)
    return [(re.compile(p.replace("{alt}", ALT), re.I), "{alt}" in p)
            for p in _flatten(data.get("switch_patterns"))]


def label_for(theme_label, lang):
    if isinstance(theme_label, dict):
        return theme_label.get(lang) or theme_label.get("en") or next(iter(theme_label.values()))
    return theme_label


def parse_date(text):
    text = (text or "").strip()
    if not text:
        return None
    for fmt, n in (("%Y-%m-%d", 10), ("%Y/%m/%d", 10), ("%d.%m.%Y", 10), ("%Y-%m", 7)):
        try:
            return _dt.datetime.strptime(text[:n], fmt).date()
        except ValueError:
            continue
    m = re.match(r"^(\d{1,2})\.(\d{1,2})\.(\d{2,4})", text)
    if m:
        d, mo, y = (int(x) for x in m.groups())
        if y < 100:
            y += 2000
        try:
            return _dt.date(y, mo, d)
        except ValueError:
            return None
    return None


def parse_rating(text):
    """Normalise a rating to the 1..5 scale, or None."""
    text = (text or "").strip()
    if not text:
        return None
    stars = text.count("★")
    if stars and set(text) <= set("★☆ "):
        return float(stars) if 1 <= stars <= 5 else None
    m = re.match(r"^\s*(\d+(?:[.,]\d+)?)\s*(?:/\s*(\d+(?:[.,]\d+)?))?", text)
    if not m:
        return None
    value = float(m.group(1).replace(",", "."))
    if m.group(2):
        scale = float(m.group(2).replace(",", "."))
        if scale <= 0:
            return None
        value = 1 + (value / scale) * 4 if scale != 5 else value
    if value < 1 or value > 5:
        return None
    return round(value, 2)


def _column_map(fieldnames):
    cols = {(c or "").strip().lower(): c for c in fieldnames}
    found = {}
    for key, aliases in COLUMN_ALIASES.items():
        for a in aliases:
            if a in cols:
                found[key] = cols[a]
                break
    return found


def load_reviews(path, dedupe=True):
    """Return (kept rows, dropped count, duplicate count)."""
    try:
        return _load_reviews(path, dedupe)
    except UnicodeDecodeError:
        raise FeedbackError(NOT_UTF8 % path)


NOT_UTF8 = ("%s is not UTF-8. Excel's 'CSV (Trennzeichen-getrennt)' saves Windows-1252: "
            "save it again as 'CSV UTF-8 (durch Trennzeichen getrennt)' and run again")


def _load_reviews(path, dedupe):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        # German Excel exports use ";". Decide from the header line only, since
        # review texts are full of commas and semicolons.
        header = fh.readline()
        fh.seek(0)
        delim = max(",;\t", key=header.count) if header.strip() else ","
        reader = csv.DictReader(fh, delimiter=delim)
        if reader.fieldnames is None:
            raise FeedbackError("%s is empty" % path)
        cmap = _column_map(reader.fieldnames)
        for need in ("url", "text"):
            if need not in cmap:
                raise FeedbackError(
                    "%s has no '%s' column. Every review needs the link it came "
                    "from and its exact text: source,url,date,rating,text" % (path, need))
        kept, dropped, dupes = [], 0, 0
        seen = set()
        for i, raw in enumerate(reader, start=2):
            row = {k: (raw.get(col) or "").strip() for k, col in cmap.items()}
            url, text = row.get("url", ""), row.get("text", "")
            if not url or not text or not re.match(r"^https?://", url):
                dropped += 1
                continue
            key = re.sub(r"\W+", " ", text.lower()).strip()
            if dedupe and key in seen:
                dupes += 1
                continue
            seen.add(key)
            kept.append({
                "line": i,
                # "App Store" and "app-store" are one source, or the bias check splits it.
                "source": re.sub(r"[\s_]+", "-", (row.get("source", "") or _host(url)).lower()),
                "url": url,
                "date": parse_date(row.get("date", "")),
                "rating": parse_rating(row.get("rating", "")),
                "text": text,
                "segment": row.get("segment", "") or None,
            })
    return kept, dropped, dupes


def _host(url):
    m = re.match(r"^https?://(?:www\.)?([^/]+)", url)
    return m.group(1) if m else "unknown"


def weight(review, today, months):
    r = review["rating"]
    w = 0.6 if r is None else (6.0 - r) / 5.0
    if review["date"] is not None and today is not None:
        age_days = (today - review["date"]).days
        if age_days > months * 30.4:
            w *= 0.5
    return w


def snippet(text, pattern, limit=220):
    """The first sentence of text that matches pattern, verbatim."""
    for sent in SENTENCE.split(text):
        if pattern.search(sent):
            s = sent.strip()
            if len(s) > limit:
                m = pattern.search(s)
                start = max(0, m.start() - limit // 2)
                s = s[start:start + limit].strip()
                s = ("..." if start > 0 else "") + s + "..."
            return s
    s = text.strip()
    return s if len(s) <= limit else s[:limit].rstrip() + "..."


def name_in(words):
    """The leading words that look like a name (each starts with a capital
    letter or a digit; a word ending in "." ends it), copied, never completed.
    A number alone ("3 different apps") or a common word that German or a UI
    capitalises ("Konkurrenten", "Dark Mode", "Premium") is not a name."""
    out = []
    for w in words.split():
        core = w.rstrip(".")
        if not core or not (core[0].isupper() or core[0].isdigit()):
            break
        out.append(core)
        if core != w:
            break
    if not out or all(w.isdigit() for w in out) or out[0].lower() in NOT_A_NAME:
        return None
    return " ".join(out)


def find_switch(text, patterns):
    """(sentence, named alternative or None) if the review says the writer
    left or wants to, else None. A pattern with {alt} only counts with a name,
    and then the sentence quoted is the one that names it."""
    for p, names in patterns:
        if not names:
            continue
        for m in p.finditer(text):
            alt = name_in(m.group("alt"))
            if alt:
                sent = next((s for s in SENTENCE.split(text) if alt in s and p.search(s)), text)
                quote = snippet(sent, p)
                return quote, (alt if alt in quote else None)
    for sent in SENTENCE.split(text):
        for p, names in patterns:
            if not names and p.search(sent):
                return snippet(sent, p), None
    return None


def source_stats(reviews):
    total = len(reviews) or 1
    stats = {}
    for r in reviews:
        st = stats.setdefault(r["source"], {"source": r["source"], "count": 0,
                                            "ratings": [], "dates": []})
        st["count"] += 1
        if r["rating"] is not None:
            st["ratings"].append(r["rating"])
        if r["date"] is not None:
            st["dates"].append(r["date"])
    out = []
    for st in stats.values():
        rs, ds = st.pop("ratings"), st.pop("dates")
        st["avg_rating"] = round(sum(rs) / len(rs), 2) if rs else None
        st["rated"] = len(rs)
        st["share_pct"] = round(100.0 * st["count"] / total, 1)
        st["first_date"] = min(ds).isoformat() if ds else None
        st["last_date"] = max(ds).isoformat() if ds else None
        out.append(st)
    out.sort(key=lambda d: (-d["count"], d["source"]))
    return out


def source_bias(reviews, by_source, today, months):
    """Where the sample leans: one source too big, a source whose stars are far
    from the rest, or dates bunched in the last 90 days or before --months."""
    rated = [r["rating"] for r in reviews if r["rating"] is not None]
    overall = round(sum(rated) / len(rated), 2) if rated else None
    dates = [r["date"] for r in reviews if r["date"] is not None]
    since = today - _dt.timedelta(days=RECENT_DAYS)
    before = today - _dt.timedelta(days=int(months * 30.4))
    warnings = []
    if by_source and by_source[0]["count"] / len(reviews) > DOMINANT_SHARE:
        warnings.append({"kind": "one_source", "source": by_source[0]["source"],
                         "share_pct": by_source[0]["share_pct"]})
    for st in by_source:
        if overall is None or st["avg_rating"] is None:
            continue
        gap = round(st["avg_rating"] - overall, 2)
        if abs(gap) >= RATING_GAP:
            warnings.append({"kind": "rating_gap", "source": st["source"],
                             "avg_rating": st["avg_rating"], "overall_avg_rating": overall,
                             "gap": gap, "rated": st["rated"]})
    recent = sum(1 for d in dates if (today - d).days <= RECENT_DAYS)
    old = sum(1 for d in dates if (today - d).days > months * 30.4)

    def pct(n):
        return round(100.0 * n / len(dates), 1) if dates else None

    if dates and recent / len(dates) > BUNCHED_SHARE:
        warnings.append({"kind": "mostly_recent", "share_pct": pct(recent), "days": RECENT_DAYS,
                         "since": since.isoformat()})
    if dates and old / len(dates) > BUNCHED_SHARE:
        warnings.append({"kind": "mostly_old", "share_pct": pct(old), "months": months,
                         "before": before.isoformat()})
    return {
        "overall_avg_rating": overall,
        "dated": len(dates),
        "first_date": min(dates).isoformat() if dates else None,
        "last_date": max(dates).isoformat() if dates else None,
        "recent_share_pct": pct(recent),
        "recent_since": since.isoformat(),
        "old_share_pct": pct(old),
        "old_before": before.isoformat(),
        "warnings": warnings,
    }


def segment_stats(reviews):
    """Reviews per segment as the platform shows it, or None when no review has one."""
    if not any(r.get("segment") for r in reviews):
        return None
    total = len(reviews)
    groups = {}
    for r in reviews:
        groups.setdefault(r.get("segment"), []).append(r)
    out = []
    for seg, rs in groups.items():
        rated = [r["rating"] for r in rs if r["rating"] is not None]
        out.append({"segment": seg, "count": len(rs),
                    "share_pct": round(100.0 * len(rs) / total, 1),
                    "avg_rating": round(sum(rated) / len(rated), 2) if rated else None,
                    "thin": len(rs) < MIN_SEGMENT})
    out.sort(key=lambda d: (d["segment"] is None, -d["count"], d["segment"] or ""))
    return out


def segment_counts(items):
    counts = {}
    for x in items:
        seg = x["rv"].get("segment")
        counts[seg] = counts.get(seg, 0) + 1
    return sorted(({"segment": k, "count": v} for k, v in counts.items()),
                  key=lambda d: (d["segment"] is None, -d["count"], d["segment"] or ""))


def is_complaint(review, sentence):
    """Does this review's matching sentence count as a complaint?"""
    r = review["rating"]
    if r is None or r <= 3.5:
        return True
    if r >= 4.5:
        return False
    return bool(CONTRAST.search(sentence))


def is_target(name, target):
    return bool(name and target and
                re.search(r"(?<!\w)%s(?!\w)" % re.escape(target), name, re.I))


def switching_summary(away, toward, themes):
    """Count the themes and the named alternatives of the reviews that left."""
    labels = {t["id"]: t["label"] for t in themes}
    reasons, alts = {}, {}
    for it in away:
        for tid in it["themes"]:
            reasons[tid] = reasons.get(tid, 0) + 1
        if it["alternative"]:
            a = alts.setdefault(it["alternative"].lower(),
                                {"name": it["alternative"], "count": 0, "sources": set()})
            a["count"] += 1
            a["sources"].add(it["source"])
    return {
        "away": away,
        "toward_original": toward,
        "reasons": sorted(({"id": k, "label": labels[k], "count": v} for k, v in reasons.items()),
                          key=lambda d: (-d["count"], d["id"])),
        "alternatives": sorted(({"name": a["name"], "count": a["count"],
                                 "sources": sorted(a["sources"])} for a in alts.values()),
                               key=lambda d: (-d["count"], d["name"].lower())),
    }


def analyse(reviews, themes, request_patterns, today=None, months=18,
            switch_patterns=None, target=None):
    if today is None:
        today = _dt.date.today()
    results = {t["id"]: {"id": t["id"], "label": t["label"], "kind": t["kind"],
                         "praise_label": t.get("praise_label") or t["label"],
                         "reviews": [], "score": 0.0, "praise": []} for t in themes}
    requests = []
    unthemed_negative = []
    away, toward = [], []
    for rv in reviews:
        w = weight(rv, today, months)
        matched = False
        counted = []
        for t in themes:
            hit = next((p for p in t["patterns"] if p.search(rv["text"])), None)
            if hit is None:
                continue
            matched = True
            res = results[t["id"]]
            quote = snippet(rv["text"], hit)
            if t["kind"] == "complaint" and not is_complaint(rv, quote):
                res["praise"].append({"rv": rv, "quote": quote})
                continue
            res["score"] += w
            res["reviews"].append({"rv": rv, "quote": quote})
            counted.append(t["id"])
        req = next((p for p in request_patterns if p.search(rv["text"])), None)
        if req is not None:
            requests.append({"quote": snippet(rv["text"], req), "url": rv["url"],
                             "source": rv["source"], "rating": rv["rating"]})
        if not matched and rv["rating"] is not None and rv["rating"] <= UNTHEMED_MAX_RATING:
            unthemed_negative.append(rv)
        found = find_switch(rv["text"], switch_patterns or [])
        if found is not None:
            quote, alt = found
            item = {"quote": quote, "url": rv["url"], "source": rv["source"],
                    "rating": rv["rating"],
                    "date": rv["date"].isoformat() if rv["date"] else None,
                    "alternative": alt, "themes": counted}
            coming = is_target(alt, target) or not is_complaint(rv, quote)
            (toward if coming else away).append(item)

    total = len(reviews) or 1
    ranked = []
    praised = []
    by_segment = segment_stats(reviews)
    for res in results.values():
        if res["praise"]:
            praised.append({
                "id": res["id"], "label": res["praise_label"], "count": len(res["praise"]),
                "sources": sorted({x["rv"]["source"] for x in res["praise"]}),
                "quotes": [{"quote": x["quote"], "url": x["rv"]["url"],
                            "source": x["rv"]["source"], "rating": x["rv"]["rating"]}
                           for x in res["praise"][:2]],
            })
        items = res["reviews"]
        if not items:
            continue
        rated = [x["rv"]["rating"] for x in items if x["rv"]["rating"] is not None]
        sources = sorted({x["rv"]["source"] for x in items})
        # Lowest rated first, then shortest, so the quotes shown are the sharpest.
        items.sort(key=lambda x: (x["rv"]["rating"] if x["rv"]["rating"] is not None else 3,
                                  len(x["quote"])))
        ranked.append({
            "id": res["id"], "label": res["label"], "kind": res["kind"],
            "score": round(res["score"], 2),
            "count": len(items),
            "share_pct": round(100.0 * len(items) / total, 1),
            "avg_rating": round(sum(rated) / len(rated), 2) if rated else None,
            "sources": sources,
            "thin": len(items) < 3 or len(sources) < 2,
            "quotes": [{"quote": x["quote"], "url": x["rv"]["url"],
                        "source": x["rv"]["source"], "rating": x["rv"]["rating"]}
                       for x in items[:3]],
            "segments": segment_counts(items) if by_segment else [],
        })
    ranked.sort(key=lambda d: (-d["score"], -d["count"], d["id"]))
    praised.sort(key=lambda d: (-d["count"], d["id"]))
    by_source = source_stats(reviews)
    dominant = None
    if len(reviews) >= 10 and by_source and by_source[0]["count"] / total > DOMINANT_SHARE:
        dominant = {"source": by_source[0]["source"],
                    "share_pct": round(100.0 * by_source[0]["count"] / total, 1)}
    return {
        "reviews": len(reviews),
        "sources": sorted({r["source"] for r in reviews}),
        "rated": sum(1 for r in reviews if r["rating"] is not None),
        "by_source": by_source,
        "dominant_source": dominant,
        "themes": ranked,
        "praise": praised,
        "requests": requests,
        "unthemed_negative": [{"url": r["url"], "source": r["source"],
                               "rating": r["rating"],
                               # a cut text says so, or --verify could not pass it
                               "text": r["text"] if len(r["text"]) <= 220
                               else r["text"][:220].rstrip() + "..."}
                              for r in unthemed_negative],
        "as_of": today.isoformat(),
        "source_bias": source_bias(reviews, by_source, today, months) if reviews else None,
        # None, not an empty list, when no switch patterns ran: a check nobody ran is not "none".
        "switching": switching_summary(away, toward, themes) if switch_patterns else None,
        "by_segment": by_segment,
    }


def _stars(r):
    return "-" if r is None else ("%g*" % r)


def _dec(x, lang):
    if x is None:
        return "-"
    s = "%.1f" % x
    return s.replace(".", ",") if lang == "de" else s


def _day(iso, lang):
    if not iso:
        return "-"
    if lang == "de":
        y, m, d = iso.split("-")
        return "%s.%s.%s" % (d, m, y)
    return iso


def render_sample(result, T, lang):
    """Sample by source: the table, the date range and where the sample leans."""
    out = ["", T["by_source"], "", T["source_head"], "| --- | --- | --- | --- | --- | --- |"]
    row = "| %s | %d | %.0f%% | %s | %s | %s |"
    for st in result.get("by_source", []):
        out.append(row % (st["source"], st["count"], st["share_pct"], _dec(st["avg_rating"], lang),
                          _day(st["first_date"], lang), _day(st["last_date"], lang)))
    bias = result.get("source_bias")
    if not bias:
        return out
    out.append(row % (T["all_sources"], result["reviews"], 100, _dec(bias["overall_avg_rating"], lang),
                      _day(bias["first_date"], lang), _day(bias["last_date"], lang)))
    out.append("")
    if bias["dated"]:
        out.append(T["dates"].format(dated=bias["dated"], n=result["reviews"],
                                     first=_day(bias["first_date"], lang),
                                     last=_day(bias["last_date"], lang),
                                     as_of=_day(result["as_of"], lang))
                   + (T["as_of_today"] if result.get("as_of_today") else ""))
    else:
        out.append(T["no_dates"])
    lines = []
    for w in bias["warnings"]:
        if w["kind"] == "one_source":
            lines.append(T["dominant"].format(share=w["share_pct"], source=w["source"]))
        elif w["kind"] == "rating_gap":
            lines.append(T["gap"].format(
                source=w["source"], avg=_dec(w["avg_rating"], lang), gap=_dec(abs(w["gap"]), lang),
                dir=T["higher"] if w["gap"] > 0 else T["lower"],
                overall=_dec(w["overall_avg_rating"], lang), n=w["rated"]))
        elif w["kind"] == "mostly_recent":
            lines.append(T["recent"].format(share=w["share_pct"], days=w["days"],
                                            since=_day(w["since"], lang)))
        elif w["kind"] == "mostly_old":
            lines.append(T["old"].format(share=w["share_pct"], months=w["months"],
                                         before=_day(w["before"], lang)))
    if lines:
        out += ["", T["lean"], ""] + ["- " + x for x in lines]
    else:
        no_lean = T["no_lean"]
        if bias["dated"]:
            no_lean += T["no_lean_dates"].format(days=RECENT_DAYS,
                                                 before=_day(bias["old_before"], lang))
        out += ["", no_lean]
    return out


def render_segments(result, T, lang):
    out = ["", T["by_segment"], "", T["segment_note"], "", T["segment_head"],
           "| --- | --- | --- | --- |"]
    for st in result["by_segment"]:
        name = st["segment"] or T["not_shown"]
        out.append("| %s%s | %d | %.0f%% | %s |" % (name, T["thin"] if st["thin"] else "",
                                                   st["count"], st["share_pct"],
                                                   _dec(st["avg_rating"], lang)))
    return out


def who_says(segments, by_segment, T):
    thin = {st["segment"] for st in by_segment if st["thin"]}
    return T["who"].format(items=", ".join(
        "%s (%d%s)" % (s["segment"] or T["not_shown"], s["count"],
                       ", " + T["thin"].strip(" ()")
                       if s["segment"] is not None and s["segment"] in thin else "")
        for s in segments))


def _switch_line(q, T):
    extra = ", " + T["switch_named"].format(name=q["alternative"]) if q["alternative"] else ""
    return '- "%s" (%s, %s%s) %s' % (q["quote"], q["source"], _stars(q["rating"]), extra, q["url"])


def render_switching(sw, T, lang, target=None):
    out = ["", "## %s" % T["switch"], "", T["switch_note"], ""]
    if not sw["away"] and not sw["toward_original"]:
        out.append(T["switch_none"])
    if sw["away"]:
        out.append(T["switch_count"].format(n=len(sw["away"])))
        if sw["reasons"]:
            out.append(T["switch_reasons"].format(items=", ".join(
                "%s (%d)" % (label_for(r["label"], lang), r["count"]) for r in sw["reasons"])))
        if sw["alternatives"]:
            out.append(T["switch_alts"].format(items=", ".join(
                "%s (%d)" % (a["name"], a["count"]) for a in sw["alternatives"])))
        out.append("")
        out += [_switch_line(q, T) for q in sw["away"][:25]]
    if sw["toward_original"]:
        out += ["", T["switch_in"].format(target=target or T["switch_target"]), ""]
        out += [_switch_line(q, T) for q in sw["toward_original"][:10]]
    return out


def render(result, dropped=0, dupes=0, lang="en", target=None):
    T = TEXT.get(lang, TEXT["en"])
    out = [T["title"].format(target=target or T["target"]), ""]
    out.append(T["summary"].format(n=result["reviews"], s=len(result["sources"]),
                                   names=", ".join(result["sources"]) or "-",
                                   rated=result["rated"]))
    if dropped:
        out.append(T["dropped"].format(n=dropped))
    if dupes:
        out.append(T["dupes"].format(n=dupes))
    if result["reviews"] < 30:
        out += ["", T["small"]]
    out += render_sample(result, T, lang)
    if result.get("by_segment"):
        out += render_segments(result, T, lang)
    for kind in ("complaint", "request"):
        rows = [t for t in result["themes"] if t["kind"] == kind]
        out += ["", "## %s" % T[kind], ""]
        if not rows:
            out.append(T["nothing"])
            continue
        out.append(T["table_head"])
        out.append("| --- | --- | --- | --- | --- | --- | --- |")
        for i, t in enumerate(rows, 1):
            out.append("| %d | %s%s | %s | %d | %.0f%% | %s | %d |" % (
                i, label_for(t["label"], lang), T["thin"] if t["thin"] else "",
                _dec(t["score"], lang), t["count"], t["share_pct"],
                _dec(t["avg_rating"], lang), len(t["sources"])))
        for t in rows:
            out += ["", "**%s**" % label_for(t["label"], lang)]
            for q in t["quotes"]:
                out.append('- "%s" (%s, %s) %s' % (q["quote"], q["source"],
                                                   _stars(q["rating"]), q["url"]))
            if result.get("by_segment") and t.get("segments"):
                out.append("- " + who_says(t["segments"], result["by_segment"], T))
    if result["themes"]:
        out += ["", T["multi"]]
    if result.get("switching") is not None:
        out += render_switching(result["switching"], T, lang, target)
    if result.get("praise"):
        out += ["", "## %s" % T["praise"], "", T["praise_note"], ""]
        for p in result["praise"]:
            q = p["quotes"][0]
            out.append('- **%s** (%d): "%s" (%s, %s) %s' % (
                label_for(p["label"], lang), p["count"], q["quote"], q["source"],
                _stars(q["rating"]), q["url"]))
    if result["requests"]:
        out += ["", T["asked"], ""]
        for q in result["requests"][:25]:
            out.append('- "%s" (%s, %s) %s' % (q["quote"], q["source"],
                                               _stars(q["rating"]), q["url"]))
    if result["unthemed_negative"]:
        out += ["", T["by_hand"], "", T["by_hand_note"], ""]
        for r in result["unthemed_negative"][:15]:
            out.append('- (%s, %s) %s: "%s"' % (r["source"], _stars(r["rating"]),
                                               r["url"], r["text"]))
    return "\n".join(out) + "\n"


def _norm(s):
    return " ".join(s.split())


def _contains(text, quote):
    """quote stands in text word for word, in order; "..." may stand for left-out words.
    Every part starts and ends on a word boundary, so "helpful" never matches inside
    "unhelpful" and "slow" not inside "slowly". Only where the quote itself opens or
    closes with "..." may its first or last part start or end inside a word, which is
    how snippet() cuts a long sentence."""
    parts = GAP.split(_norm(quote))
    kept = [(k, p) for k, p in enumerate(parts) if p]
    pos = 0
    for n, (k, part) in enumerate(kept):
        open_start = n == 0 and k > 0
        open_end = n == len(kept) - 1 and k < len(parts) - 1
        m = re.compile(("" if open_start else r"(?<!\w)") + re.escape(part)
                       + ("" if open_end else r"(?!\w)")).search(text, pos)
        if m is None:
            return False
        pos = m.end()
    return True


def verify(report, rows):
    """Check every quoted text on a line with a link against the reviews behind
    that link. Returns {"checked", "ok", "problems": [{line, quote, url, problem}]}."""
    texts = {}
    for r in rows:
        texts.setdefault(r["url"], []).append(_norm(r["text"]))
    checked, problems = 0, []
    for no, line in enumerate(report.splitlines(), 1):
        urls = [u.rstrip(".,;:!?'*_") for u in LINK.findall(line)]
        quotes = [next(g for g in m.groups() if g is not None) for m in QUOTED.finditer(line)]
        quotes = [q for q in quotes if len(GAP.sub("", q).strip()) >= 3]
        if not urls or not quotes:
            continue
        known = [t for u in urls for t in texts.get(u, [])]
        for q in quotes:
            checked += 1
            if not known:
                problems.append({"line": no, "quote": q, "url": urls[0], "problem": "unknown_url"})
            elif not any(_contains(t, q) for t in known):
                problems.append({"line": no, "quote": q, "url": urls[0], "problem": "not_found"})
    return {"checked": checked, "ok": checked - len(problems), "problems": problems}


def render_verify(res, report_path, csv_path, lang="en"):
    T = TEXT.get(lang, TEXT["en"])
    names = {"checked": res["checked"], "file": report_path, "csv": csv_path}
    if not res["checked"]:
        return T["verify_none"].format(**names) + "\n"
    if not res["problems"]:
        return T["verify_ok"].format(**names) + "\n"
    out = [T["verify_bad"].format(bad=len(res["problems"]), **names)]
    for p in res["problems"]:
        out.append(T[p["problem"]].format(line=p["line"], quote=p["quote"], url=p["url"],
                                          csv=csv_path))
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("reviews", help="CSV with source,url,date,rating,text")
    ap.add_argument("--themes", default=DEFAULT_THEMES)
    ap.add_argument("--months", type=int, default=18,
                    help="reviews older than this count half (default 18)")
    ap.add_argument("--as-of", "--today", dest="as_of", metavar="YYYY-MM-DD",
                    help="count review ages from this day, for reproducible runs "
                         "(default: today; --today is the old name)")
    ap.add_argument("--lang", choices=sorted(TEXT), default="en",
                    help="language of the report headings (default en)")
    ap.add_argument("--target", help="name of the product analysed, for the title")
    ap.add_argument("--out", help="write the report (or with --json the JSON) here, as UTF-8")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--verify", metavar="FILE",
                    help="check that every linked quote in FILE stands word for word in the "
                         "reviews; exit 1 if one does not")
    args = ap.parse_args(argv)
    try:
        today = (_dt.datetime.strptime(args.as_of, "%Y-%m-%d").date() if args.as_of
                 else _dt.date.today())
    except ValueError:
        print("reviews: --as-of needs a date like 2026-10-17, not %r" % args.as_of,
              file=sys.stderr)
        return 2
    try:
        reviews, dropped, dupes = load_reviews(args.reviews, dedupe=not args.verify)
        if args.verify:
            with open(args.verify, encoding="utf-8") as fh:
                report = fh.read()
        else:
            themes, req = load_themes(args.themes)
            switch = load_switching(args.themes)
    except (FeedbackError, OSError, ValueError, KeyError, re.error) as exc:
        print("reviews: %s" % exc, file=sys.stderr)
        return 2
    if not reviews:
        print("reviews: no usable rows. Every row needs a url (http...) and the "
              "review text.", file=sys.stderr)
        return 2
    if args.verify:
        res = verify(report, reviews)
        code = 0 if res["checked"] and not res["problems"] else 1
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            sys.stdout.write(render_verify(res, args.verify, args.reviews, args.lang))
        return code
    result = analyse(reviews, themes, req, today=today, months=args.months,
                     switch_patterns=switch, target=args.target)
    result["dropped"] = dropped
    result["duplicates"] = dupes
    if not args.as_of:          # say so, or nobody can tell the date was not fixed
        result["as_of_today"] = True
    if args.json:
        text = json.dumps(result, indent=2, default=str, ensure_ascii=False) + "\n"
    else:
        text = render(result, dropped, dupes, lang=args.lang, target=args.target)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
