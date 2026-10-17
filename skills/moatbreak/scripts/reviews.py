#!/usr/bin/env python3
"""Voice-of-customer ranker for the Moatbreak skill. Standard library only.

Takes real reviews you collected about a competitor (app, SaaS, website or
online shop) and ranks what its users hate and what they keep asking for,
with the exact words and a link for every claim. English and German reviews
are themed out of the box; add more languages in themes.json.

Origin and licence: see NOTICE.md and LICENSE.

    python3 reviews.py teardown/reviews.csv
    python3 reviews.py teardown/reviews.csv --lang de --out teardown/feedback.md
    python3 reviews.py teardown/reviews.csv --json
    python3 reviews.py teardown/reviews.csv --themes my-themes.json

CSV columns (extra columns are ignored, header names are case-insensitive and
German headers work too):

    source   app-store, google-play, g2, capterra, trustpilot, omr, reddit,
             trusted-shops, google-maps, ...        (quelle)
    url      link to the review or thread. Required. (link)
    date     2026-08-01, 2026-08 or 01.08.2026       (datum)
    rating   4, 4.5, 4,5, 4/5, 8/10, "4 Sterne", ★★★★☆ (bewertung, sterne, stars)
    text     the review, copied exactly. Required.  (review, inhalt, kommentar)

A row without a url or without text is dropped and counted, never guessed.
This tool only reorganises what you give it. It does not write, translate or
paraphrase reviews, and every quote it prints is a substring of a row you
supplied, with that row's link.

Praise is not a complaint: a 4.5-5 star review never counts toward a
complaint theme, and a 4 star review only when the matching sentence has a
"but" (but, unfortunately, aber, leider, ...). Those mentions are reported as
praise instead, which shows where the original is strong.

Ranking: every review that matches a theme adds a weight. A 1 star review adds
1.0, a 5 star review 0.2, an unrated one 0.6. Reviews older than --months
(default 18) count half. Themes with fewer than 3 reviews, or all from one
source, are marked thin. If one source supplies more than 60% of the sample,
the report says so, because one platform's audience is not the market.
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
UNTHEMED_MAX_RATING = 3
CONTRAST = re.compile(r"\b(but|however|unfortunately|sadly|except|only|wish|aber|leider|jedoch|"
                      r"allerdings|nur|bis auf|schade|trotzdem)\b", re.I)

COLUMN_ALIASES = {
    "source": ("source", "quelle", "plattform", "platform"),
    "url": ("url", "link", "href"),
    "date": ("date", "datum"),
    "rating": ("rating", "bewertung", "sterne", "stars", "score"),
    "text": ("text", "review", "inhalt", "kommentar", "comment", "body", "content"),
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
        "source_head": "| source | reviews | avg stars |",
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
        "source_head": "| Quelle | Bewertungen | Ø Sterne |",
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
    themes = []
    for t in data.get("themes", []):
        themes.append({
            "id": t["id"],
            "label": t.get("label", t["id"]),
            "kind": t.get("kind", "complaint"),
            "patterns": [re.compile(p, re.I) for p in _flatten(t.get("patterns"))],
        })
    requests = [re.compile(p, re.I) for p in _flatten(data.get("request_patterns"))]
    return themes, requests


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


def load_reviews(path):
    """Return (kept rows, dropped count, duplicate count)."""
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
            if key in seen:
                dupes += 1
                continue
            seen.add(key)
            kept.append({
                "line": i,
                "source": (row.get("source", "") or _host(url)).lower(),
                "url": url,
                "date": parse_date(row.get("date", "")),
                "rating": parse_rating(row.get("rating", "")),
                "text": text,
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


def source_stats(reviews):
    stats = {}
    for r in reviews:
        st = stats.setdefault(r["source"], {"source": r["source"], "count": 0, "ratings": []})
        st["count"] += 1
        if r["rating"] is not None:
            st["ratings"].append(r["rating"])
    out = []
    for st in stats.values():
        rs = st.pop("ratings")
        st["avg_rating"] = round(sum(rs) / len(rs), 2) if rs else None
        out.append(st)
    out.sort(key=lambda d: (-d["count"], d["source"]))
    return out


def is_complaint(review, sentence):
    """Does this review's matching sentence count as a complaint?"""
    r = review["rating"]
    if r is None or r <= 3.5:
        return True
    if r >= 4.5:
        return False
    return bool(CONTRAST.search(sentence))


def analyse(reviews, themes, request_patterns, today=None, months=18):
    if today is None:
        today = _dt.date.today()
    results = {t["id"]: {"id": t["id"], "label": t["label"], "kind": t["kind"],
                         "reviews": [], "score": 0.0, "praise": []} for t in themes}
    requests = []
    unthemed_negative = []
    for rv in reviews:
        w = weight(rv, today, months)
        matched = False
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
        req = next((p for p in request_patterns if p.search(rv["text"])), None)
        if req is not None:
            requests.append({"quote": snippet(rv["text"], req), "url": rv["url"],
                             "source": rv["source"], "rating": rv["rating"]})
        if not matched and rv["rating"] is not None and rv["rating"] <= UNTHEMED_MAX_RATING:
            unthemed_negative.append(rv)

    total = len(reviews) or 1
    ranked = []
    praised = []
    for res in results.values():
        if res["praise"]:
            praised.append({
                "id": res["id"], "label": res["label"], "count": len(res["praise"]),
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
                               "rating": r["rating"], "text": r["text"][:220]}
                              for r in unthemed_negative],
    }


def _stars(r):
    return "-" if r is None else ("%g*" % r)


def _dec(x, lang):
    if x is None:
        return "-"
    s = "%.1f" % x
    return s.replace(".", ",") if lang == "de" else s


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
    if result.get("dominant_source"):
        d = result["dominant_source"]
        out += ["", T["dominant"].format(share=d["share_pct"], source=d["source"])]
    out += ["", T["by_source"], "", T["source_head"], "| --- | --- | --- |"]
    for st in result.get("by_source", []):
        out.append("| %s | %d | %s |" % (st["source"], st["count"],
                                         _dec(st["avg_rating"], lang)))
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
    if result["themes"]:
        out += ["", T["multi"]]
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("reviews", help="CSV with source,url,date,rating,text")
    ap.add_argument("--themes", default=DEFAULT_THEMES)
    ap.add_argument("--months", type=int, default=18,
                    help="reviews older than this count half (default 18)")
    ap.add_argument("--today", help="YYYY-MM-DD, for reproducible runs")
    ap.add_argument("--lang", choices=sorted(TEXT), default="en",
                    help="language of the report headings (default en)")
    ap.add_argument("--target", help="name of the product analysed, for the title")
    ap.add_argument("--out", help="write the markdown report here")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        themes, req = load_themes(args.themes)
        reviews, dropped, dupes = load_reviews(args.reviews)
    except (FeedbackError, OSError, ValueError, KeyError, re.error) as exc:
        print("reviews: %s" % exc, file=sys.stderr)
        return 2
    if not reviews:
        print("reviews: no usable rows. Every row needs a url (http...) and the "
              "review text.", file=sys.stderr)
        return 2
    today = parse_date(args.today) if args.today else None
    result = analyse(reviews, themes, req, today=today, months=args.months)
    result["dropped"] = dropped
    result["duplicates"] = dupes
    if args.json:
        print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
        return 0
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
