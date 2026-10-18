#!/usr/bin/env python3
"""Sales battle card for the Moatbreak skill. Standard library only.

Turns what the teardown already found into a one-page battle card: where the
competitor is weak (complaint themes with verbatim, linked quotes), where it
is strong (praise, so sales does not attack it), what only we have (from the
feature matrix), objection-handling stubs, and, as an appendix, a SWOT of our
product against it in which every line names its source and the claims that
are fit for a public comparison page. It invents nothing: every line comes
from the two input files, and every part a person must write says "to write".

Origin and licence: see NOTICE.md and LICENSE.

    python3 reviews.py teardown/reviews.csv --as-of 2026-10-17 --json --out teardown/feedback.json
    python3 battlecard.py --feedback teardown/feedback.json --features teardown/features.csv \\
        --target "X" --ours "Y" --as-of 2026-10-17 --lang de --out teardown/battlecard.md
    python3 battlecard.py --features teardown/features.csv --target X --ours Y --json

Inputs (at least one; a missing one is reported as "not researched"):

    --feedback   the output of reviews.py --json
    --features   the feature matrix (feature,area,priority,original,clone,
                 effort,notes): original is the competitor, clone is our
                 product. original may also be partial (teilweise). Two
                 optional columns make a claim about the competitor usable:
                 source (the link where it was checked) and checked (the
                 date, YYYY-MM-DD). parity.py ignores both.

Every claim about the competitor carries a tag:

    verified   a features.csv row with a source and a checked date
    reported   what reviewers say, with the links of the quotes
    assumed    anything else, including original = unknown. Never say it
               to a prospect.

A verified claim checked more than 90 days before --as-of is stale. The
comparison-page list takes only verified, fresh rows with a public link
(http or https), never reviews, and warns when it shows only rows we win.
"""

import argparse
import datetime as _dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import parity  # noqa: E402  feature matrix loader and its value sets
import reviews  # noqa: E402  label_for, parse_date

STALE_DAYS = 90
TOP_WEAK, TOP_ASKED, TOP_STRONG, TOP_GAP_OBJECTIONS, QUOTES = 5, 3, 3, 5, 2
PARTIAL = {"partial", "teilweise", "teils"}
RANK = {"no": 0, "partial": 1, "yes": 2}
PUBLIC = re.compile(r"^https?://", re.I)

TEXT = {
    "en": {
        "title": "# Battle card: {ours} vs {target}",
        "intro": "As of {date}. Internal, for sales: not for publication. Every claim about "
                 "{target} has a tag: verified (checked in a primary source, with link and "
                 "date), reported (what reviewers say, with links), assumed (not checked: "
                 "never say it to a prospect). Replace every \"to write\".",
        "todo": "to write",
        "oneline": "## In one line",
        "oneline_todo": "to write: why a customer picks {ours} over {target}, in one sentence, "
                        "from the angle in teardown/fixes.md, with its evidence.",
        "weak": "## Where they are weak",
        "weak_note": "Top complaint themes from {nr}. Ask about them; do not state "
                     "them as facts about {target}.",
        "ask": "Discovery question: to write",
        "strong": "## Where they are strong",
        "strong_note": "Praised in 4-5 star reviews. Do not attack these; match them.",
        "plain": "In plain words: to write: what customers praise {target} for here, "
                 "in one sentence of your own, and our line: agree, then how {ours} matches it.",
        "no_feedback": "Not researched: run voice of customer and pass the output of "
                       "reviews.py --json with --feedback.",
        "none_weak": "No complaint theme matched. Read teardown/feedback.md by hand.",
        "none_strong": "No praise theme matched.",
        "diff": "## Our differentiators",
        "diff_note": "What {ours} has done (clone = yes) and {target} lacks or only does partly.",
        "diff_head": "| priority | feature | {target} | claim about {target} | line |",
        "none_diff": "None in features.csv yet.",
        "unchecked": "Check first: {ours} has it, nobody checked {target}: {items}.",
        "not_yet": "Not yet, do not claim: own features that are not done: {items}.",
        "no_features": "Not researched: no features.csv (pass --features).",
        "objections": "## Objection handling",
        "obj_note": "A person writes each answer: true, short, no claim about {target} "
                    "that is not verified.",
        "obj_gap": "\"{target} has this: {feature}. Does {ours}?\"",
        "obj_gap_data": "Data: {ref}; {target}: {theirs} {tag}; {ours}: {us}. Answer: to write",
        "obj_praise": "\"We are happy with {target}.\"",
        "obj_praise_data": "Data: {ref}, praised topic {label} ({nr}), e.g. "
                           "\"{quote}\" {url}. Answer: to write",
        "none_obj": "No objection in the data yet.",
        "prices": "## Prices",
        "prices_todo": "to write: each plan of {target} with price, billing period, net or "
                       "gross, the date checked and the link to its pricing page, next to the "
                       "comparable plan of {ours}. No price without a date.",
        "swot": "## SWOT: {ours} against {target}",
        "swot_note": "Only from features.csv and the review analysis; every line names "
                     "its source.",
        "S": "**Strengths** ({ours})", "W": "**Weaknesses** ({ours})",
        "O": "**Opportunities**", "T": "**Threats**",
        "none": "- none in the data",
        "row_line": "- [{prio}] {feature}: {target} {theirs}, {ours} {us} ({ref}) {tag}",
        "opp_line": "- {label}{thin}: {nc}, {ns} ({ref})",
        "req_line": "- Asked for: {label}{thin}: {nr}, {ns} ({ref})",
        "threat_line": "- {label}: praised in {nr} ({ref})",
        "page": "## For a comparison page",
        "page_note": "Only verified claims with a public link, checked at most {days} days "
                     "before {date}. Reviews never go on the page. Before publishing: the "
                     "checklist in references/battlecard.md, reviewed by a lawyer.",
        "page_head": "| feature | {ours} | {target} | source | checked |",
        "page_none": "No row is usable yet.",
        "balance": "Ahead: {ours} {wins}, {target} {losses}; equal: {ties}.",
        "lopsided": "Warning: the table shows no row where {target} is ahead, but "
                    "features.csv has must or should rows where it is (count: {n}). Leaving "
                    "them out can mislead (§ 5a UWG): verify and add them, or narrow what the "
                    "page claims.",
        "excluded": "Not usable yet:",
        "why": {"unknown": "original unknown", "source": "no source",
                "checked": "no checked date", "stale": "stale, recheck",
                "private": "source is not a public link"},
        "footer": "## Sources and sample",
        "sample": "Reviews: {n} from {ns} ({names}); with stars: {rated}; dropped (no link "
                  "or text): {dropped}; duplicates: {dupes}.",
        "small": "Under 30 reviews: the themes show a direction, not a ranking.",
        "dominant": "{share:.0f}% of the reviews come from {source}: one platform's audience "
                    "is not the market.",
        "matrix": "Feature matrix: {nrows}; claims about {target}: {verified} verified "
                  "({stale} stale), {assumed} assumed.",
        "checked_range": "Checked between {first} and {last}.",
        "asof": "Card as of {date}. Stale means checked more than {days} days before that date.",
        "fix": "Fix in features.csv:",
        "bad_date": "line {line}: checked '{value}' is not a date (YYYY-MM-DD)",
        "values": {"yes": "yes", "partial": "partial", "no": "no", "unknown": "unknown"},
        "tag_verified": "[verified, checked {date}: {source}]",
        "tag_stale": "[verified, checked {date}, stale: {source}]",
        "tag_assumed": "[assumed: {why}]",
        "tag_reported": "[reported: {nr}, {ns}{avg}]",
        "avg": ", avg {avg} stars",
        "thin": " (thin)",
        "line": "line {line}",
        "n_review": ("review", "reviews"), "n_source": ("source", "sources"),
        "n_complaint": ("complaint", "complaints"), "n_row": ("row", "rows"),
    },
    "de": {
        "title": "# Battle Card: {ours} gegen {target}",
        "intro": "Stand {date}. Intern, für den Vertrieb: nicht zur Veröffentlichung. Jede "
                 "Aussage über {target} trägt ein Etikett: geprüft (in einer Primärquelle "
                 "nachgesehen, mit Link und Datum), berichtet (was Rezensenten schreiben, mit "
                 "Links), angenommen (nicht geprüft: nie gegenüber Interessenten behaupten). "
                 "Jedes „zu schreiben“ ersetzen.",
        "todo": "zu schreiben",
        "oneline": "## In einem Satz",
        "oneline_todo": "zu schreiben: warum ein Kunde {ours} statt {target} wählt, in einem "
                        "Satz, aus dem Winkel in teardown/fixes.md, mit seinem Beleg.",
        "weak": "## Wo sie schwach sind",
        "weak_note": "Die stärksten Beschwerde-Themen aus {nr}. Danach fragen, "
                     "nicht als Tatsache über {target} behaupten.",
        "ask": "Frage im Gespräch: zu schreiben",
        "strong": "## Wo sie stark sind",
        "strong_note": "Gelobt in 4-5-Sterne-Bewertungen. Hier nicht angreifen, sondern "
                       "mithalten.",
        "plain": "In eigenen Worten: zu schreiben: wofür Kunden {target} hier loben, in einem "
                 "eigenen Satz, und unsere Linie: zustimmen, dann wie {ours} mithält.",
        "no_feedback": "Nicht recherchiert: Voice of Customer ausführen und die Ausgabe von "
                       "reviews.py --json mit --feedback übergeben.",
        "none_weak": "Kein Beschwerde-Thema gefunden. teardown/feedback.md von Hand lesen.",
        "none_strong": "Kein Lob-Thema gefunden.",
        "diff": "## Was nur wir haben",
        "diff_note": "Was {ours} fertig hat (clone = ja) und {target} nicht oder nur "
                     "teilweise kann.",
        "diff_head": "| Priorität | Feature | {target} | Aussage über {target} | Zeile |",
        "none_diff": "Noch keine in features.csv.",
        "unchecked": "Erst prüfen: {ours} hat es, bei {target} hat es niemand geprüft: {items}.",
        "not_yet": "Noch nicht behaupten, eigene Features noch nicht fertig: {items}.",
        "no_features": "Nicht recherchiert: keine features.csv (--features übergeben).",
        "objections": "## Einwände",
        "obj_note": "Jede Antwort schreibt ein Mensch: wahr, kurz, keine ungeprüfte Aussage "
                    "über {target}.",
        "obj_gap": "„{target} hat das: {feature}. Und {ours}?“",
        "obj_gap_data": "Daten: {ref}; {target}: {theirs} {tag}; {ours}: {us}. Antwort: zu "
                        "schreiben",
        "obj_praise": "„Wir sind mit {target} zufrieden.“",
        "obj_praise_data": "Daten: {ref}, gelobtes Thema {label} ({nr}), z. B. "
                           "„{quote}“ {url}. Antwort: zu schreiben",
        "none_obj": "Noch kein Einwand in den Daten.",
        "prices": "## Preise",
        "prices_todo": "zu schreiben: jeder Tarif von {target} mit Preis, "
                       "Abrechnungszeitraum, netto oder brutto, Prüfdatum und Link zur "
                       "Preisseite, daneben der vergleichbare Tarif von {ours}. Kein Preis "
                       "ohne Datum.",
        "swot": "## SWOT: {ours} gegen {target}",
        "swot_note": "Nur aus features.csv und der Bewertungsanalyse; jede Zeile nennt ihre "
                     "Quelle.",
        "S": "**Stärken** ({ours})", "W": "**Schwächen** ({ours})",
        "O": "**Chancen**", "T": "**Risiken**",
        "none": "- keine in den Daten",
        "row_line": "- [{prio}] {feature}: {target} {theirs}, {ours} {us} ({ref}) {tag}",
        "opp_line": "- {label}{thin}: {nc}, {ns} ({ref})",
        "req_line": "- Gewünscht: {label}{thin}: {nr}, {ns} ({ref})",
        "threat_line": "- {label}: gelobt in {nr} ({ref})",
        "page": "## Für eine Vergleichsseite",
        "page_note": "Nur geprüfte Aussagen mit öffentlichem Link, höchstens {days} Tage vor "
                     "dem {date} geprüft. Bewertungen kommen nie auf die Seite. Vor der "
                     "Veröffentlichung: die Checkliste in references/battlecard.md, von einem "
                     "Anwalt geprüft.",
        "page_head": "| Feature | {ours} | {target} | Quelle | geprüft |",
        "page_none": "Noch keine Zeile verwendbar.",
        "balance": "Vorn: {ours} {wins}, {target} {losses}; gleich: {ties}.",
        "lopsided": "Achtung: Die Tabelle zeigt keine Zeile, in der {target} vorn ist, aber "
                    "features.csv hat Muss- oder Soll-Zeilen, in denen es so ist (Anzahl: "
                    "{n}). Sie wegzulassen kann irreführen (§ 5a UWG): prüfen und ergänzen, "
                    "oder die Aussage der Seite enger fassen.",
        "excluded": "Noch nicht verwendbar:",
        "why": {"unknown": "Original unbekannt", "source": "keine Quelle",
                "checked": "kein Prüfdatum", "stale": "veraltet, neu prüfen",
                "private": "Quelle ist kein öffentlicher Link"},
        "footer": "## Quellen und Stichprobe",
        "sample": "Bewertungen: {n} aus {ns} ({names}); mit Sternen: {rated}; verworfen "
                  "(ohne Link oder Text): {dropped}; doppelt: {dupes}.",
        "small": "Unter 30 Bewertungen: Die Themen zeigen eine Richtung, keine Rangfolge.",
        "dominant": "{share:.0f}% der Bewertungen stammen von {source}: Das Publikum einer "
                    "Plattform ist nicht der Markt.",
        "matrix": "Feature-Matrix: {nrows}; Aussagen über {target}: {verified} geprüft "
                  "(davon {stale} veraltet), {assumed} angenommen.",
        "checked_range": "Geprüft zwischen {first} und {last}.",
        "asof": "Stand der Karte: {date}. Veraltet heißt: mehr als {days} Tage vor diesem "
                "Datum geprüft.",
        "fix": "In features.csv korrigieren:",
        "bad_date": "Zeile {line}: checked '{value}' ist kein Datum (JJJJ-MM-TT)",
        "values": {"yes": "ja", "partial": "teilweise", "no": "nein", "unknown": "unbekannt"},
        "tag_verified": "[geprüft am {date}: {source}]",
        "tag_stale": "[geprüft am {date}, veraltet: {source}]",
        "tag_assumed": "[angenommen: {why}]",
        "tag_reported": "[berichtet: {nr}, {ns}{avg}]",
        "avg": ", Ø {avg} Sterne",
        "thin": " (dünn)",
        "line": "Zeile {line}",
        "n_review": ("Bewertung", "Bewertungen"), "n_source": ("Quelle", "Quellen"),
        "n_complaint": ("Beschwerde", "Beschwerden"), "n_row": ("Zeile", "Zeilen"),
    },
}


class CardError(Exception):
    pass


def load_feedback(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or not isinstance(data.get("themes"), list):
        raise CardError("%s is not the output of reviews.py --json" % path)
    return data


def theirs_of(row):
    v = (row.get("original") or "yes").lower()   # blank counts as yes, as in parity.py
    if v in parity.NO:
        return "no"
    if v in parity.UNKNOWN:
        return "unknown"
    return "partial" if v in PARTIAL else "yes"


def ours_of(row):
    v = (row.get("clone") or "").lower()
    if v in parity.SKIP:
        return "skip"
    credit = parity.CREDIT.get(v, 0.0)
    return "yes" if credit == 1.0 else ("partial" if credit == 0.5 else "no")


def tag_of(row, as_of):
    """The evidence behind this row's claim about the competitor."""
    source = (row.get("source") or "").strip()
    checked = reviews.parse_date(row.get("checked", ""))
    missing = []
    if theirs_of(row) == "unknown":
        missing.append("unknown")
    if not source:
        missing.append("source")
    if checked is None:
        missing.append("checked")
    return {"status": "assumed" if missing else "verified", "missing": missing,
            "source": source, "checked": checked.isoformat() if checked else None,
            "stale": checked is not None and (as_of - checked).days > STALE_DAYS,
            "public": bool(PUBLIC.match(source))}


def _theme(t, lang, ref):
    return {"id": t["id"], "label": reviews.label_for(t["label"], lang), "ref": ref,
            "count": t.get("count", 0), "sources": len(t.get("sources", [])),
            "avg_rating": t.get("avg_rating"), "thin": bool(t.get("thin")),
            "quotes": t.get("quotes", [])[:QUOTES], "tag": "reported"}


def _matrix(card, rows, as_of):
    """Sort the feature matrix rows into the card's lists and the comparison page."""
    items = []
    for r in rows:
        us = ours_of(r)
        if us == "skip":
            continue
        if (r.get("checked") or "").strip() and reviews.parse_date(r["checked"]) is None:
            card["problems"].append({"line": r["line"], "value": r["checked"]})
        items.append({"line": r["line"], "ref": "features.csv:%d" % r["line"],
                      "feature": r["feature"], "area": r.get("area", ""),
                      "weight": parity.WEIGHT.get(r.get("priority", "").lower(), 1),
                      "theirs": theirs_of(r), "ours": us, "tag": tag_of(r, as_of)})

    def their_rank(i):   # parity.py counts unknown as theirs, so do we
        return RANK["yes"] if i["theirs"] == "unknown" else RANK[i["theirs"]]

    by_prio = lambda i: (-i["weight"], i["line"])   # noqa: E731
    card["differentiators"] = sorted((i for i in items if i["ours"] == "yes"
                                      and i["theirs"] in ("no", "partial")), key=by_prio)
    card["unchecked"] = [i for i in items if i["ours"] == "yes" and i["theirs"] == "unknown"]
    card["not_yet"] = [i for i in items if i["theirs"] == "no" and i["ours"] != "yes"]
    card["gaps"] = sorted((i for i in items if their_rank(i) > RANK[i["ours"]]),
                          key=lambda i: (-i["weight"], RANK[i["ours"]], i["line"]))

    claims = [i for i in items if their_rank(i) or RANK[i["ours"]]]
    page, excluded = [], []
    for i in sorted(claims, key=by_prio):
        t = i["tag"]
        why = t["missing"] + (["stale"] if t["stale"] else [])
        if t["source"] and not t["public"]:
            why.append("private")
        (excluded if why else page).append(dict(i, why=why))
    diff = [RANK[i["ours"]] - their_rank(i) for i in page]
    wins, losses = sum(1 for d in diff if d > 0), sum(1 for d in diff if d < 0)
    key_gaps = [i for i in card["gaps"] if i["weight"] >= 2]
    card["page"] = {"rows": page, "excluded": excluded, "wins": wins, "losses": losses,
                    "ties": len(page) - wins - losses,
                    "lopsided": len(key_gaps) if page and not losses and key_gaps else 0}

    dates = sorted(i["tag"]["checked"] for i in claims if i["tag"]["checked"])
    card["claims"] = {"rows": len(rows), "count": len(claims),
                      "verified": sum(1 for i in claims if i["tag"]["status"] == "verified"),
                      "stale": sum(1 for i in claims if i["tag"]["stale"]
                                   and i["tag"]["status"] == "verified"),
                      "assumed": sum(1 for i in claims if i["tag"]["status"] == "assumed"),
                      "first": dates[0] if dates else None, "last": dates[-1] if dates else None}


def build(feedback, rows, target, ours, as_of, lang="en"):
    card = {"target": target, "ours": ours, "as_of": as_of.isoformat(),
            "has_feedback": feedback is not None, "has_features": rows is not None,
            "problems": []}
    if feedback is not None:
        themes = feedback["themes"]
        complaints = [t for t in themes if t.get("kind", "complaint") == "complaint"]
        asked = [t for t in themes if t.get("kind") == "request"]
        card["weak"] = [_theme(t, lang, "themes/" + t["id"]) for t in complaints[:TOP_WEAK]]
        card["asked"] = [_theme(t, lang, "themes/" + t["id"]) for t in asked[:TOP_ASKED]]
        card["strong"] = [_theme(p, lang, "praise/" + p["id"])
                          for p in feedback.get("praise", [])[:TOP_STRONG]]
        card["sample"] = {k: feedback.get(k) for k in
                          ("reviews", "sources", "rated", "dropped", "duplicates",
                           "dominant_source")}
    if rows is not None:
        _matrix(card, rows, as_of)
    key_gaps = [i for i in card.get("gaps", []) if i["weight"] >= 2]
    card["objections"] = [{"kind": "gap", "item": i, "answer": None}
                          for i in key_gaps[:TOP_GAP_OBJECTIONS]]
    card["objections"] += [{"kind": "praise", "theme": p, "answer": None}
                           for p in card.get("strong", [])]
    card["swot"] = {"strengths": [i["ref"] for i in card.get("differentiators", [])],
                    "weaknesses": [i["ref"] for i in card.get("gaps", [])],
                    "opportunities": [t["ref"] for t in
                                      card.get("weak", []) + card.get("asked", [])],
                    "threats": [p["ref"] for p in card.get("strong", [])]}
    return card


def _date(iso, lang):
    if not iso:
        return "-"
    return _dt.date(*map(int, iso.split("-"))).strftime("%d.%m.%Y") if lang == "de" else iso


def _dec(x, lang):
    s = "%.1f" % x
    return s.replace(".", ",") if lang == "de" else s


def _stars(r):
    return "-" if r is None else "%g*" % r


def _n(n, words):
    return "%d %s" % (n, words[0] if n == 1 else words[1])


def _cell(text):
    return (text or "").replace("|", "\\|")


def render(card, lang="en"):
    T = TEXT.get(lang, TEXT["en"])
    names = {"target": card["target"], "ours": card["ours"]}
    V = T["values"]

    def ref(item_or_ref):
        r = item_or_ref if isinstance(item_or_ref, str) else item_or_ref["ref"]
        if r.startswith("features.csv:"):
            return "features.csv " + T["line"].format(line=r.split(":", 1)[1])
        return "feedback.json " + r

    def tag(i):
        t = i["tag"]
        if t["status"] == "assumed":
            return T["tag_assumed"].format(why=", ".join(T["why"][m] for m in t["missing"]))
        return T["tag_stale" if t["stale"] else "tag_verified"].format(
            date=_date(t["checked"], lang), source=t["source"])

    def reported(t):
        avg = T["avg"].format(avg=_dec(t["avg_rating"], lang)) if t.get("avg_rating") else ""
        return T["tag_reported"].format(nr=_n(t["count"], T["n_review"]),
                                        ns=_n(t["sources"], T["n_source"]), avg=avg)

    def quote(q, indent):
        return '%s- "%s" (%s, %s) %s' % (indent, q["quote"], q["source"],
                                         _stars(q["rating"]), q["url"])

    def row_line(i):
        return T["row_line"].format(prio=parity.TEXT[lang]["prio"][i["weight"]],
                                    feature=i["feature"], theirs=V[i["theirs"]],
                                    us=V[i["ours"]], ref=ref(i), tag=tag(i), **names)

    def listing(items, with_status=False):
        return "; ".join("%s (%s%s)" % (i["feature"], T["line"].format(line=i["line"]),
                                        (", " + V[i["ours"]]) if with_status else "")
                         for i in items)

    out = [T["title"].format(**names), "",
           T["intro"].format(date=_date(card["as_of"], lang), **names),
           "", T["oneline"], "", T["oneline_todo"].format(**names)]

    out += ["", T["weak"], ""]
    if not card["has_feedback"]:
        out.append(T["no_feedback"])
    elif not card["weak"]:
        out.append(T["none_weak"])
    else:
        out += [T["weak_note"].format(nr=_n(card["sample"]["reviews"], T["n_review"]),
                                      **names), ""]
        for n, t in enumerate(card["weak"], 1):
            out.append("%d. **%s**%s %s" % (n, t["label"], T["thin"] if t["thin"] else "",
                                            reported(t)))
            out += [quote(q, "   ") for q in t["quotes"]]
            out.append("   - " + T["ask"])

    out += ["", T["strong"], ""]
    if not card["has_feedback"]:
        out.append(T["no_feedback"])
    elif not card["strong"]:
        out.append(T["none_strong"])
    else:
        out += [T["strong_note"], ""]
        for t in card["strong"]:
            out.append("- **%s** %s" % (t["label"], reported(t)))
            out += [quote(q, "  ") for q in t["quotes"]]
            out.append("  - " + T["plain"].format(**names))

    out += ["", T["diff"], ""]
    if not card["has_features"]:
        out.append(T["no_features"])
    else:
        out += [T["diff_note"].format(**names), ""]
        if card["differentiators"]:
            out += [T["diff_head"].format(**names), "| --- | --- | --- | --- | --- |"]
            for i in card["differentiators"]:
                out.append("| %s | %s | %s | %s | %d |" % (
                    parity.TEXT[lang]["prio"][i["weight"]], _cell(i["feature"]),
                    V[i["theirs"]], _cell(tag(i)), i["line"]))
        else:
            out.append(T["none_diff"])
        if card["unchecked"]:
            out += ["", T["unchecked"].format(items=listing(card["unchecked"]), **names)]
        if card["not_yet"]:
            out += ["", T["not_yet"].format(items=listing(card["not_yet"], True))]

    out += ["", T["objections"], ""]
    objections = card.get("objections", [])
    if not objections:
        out.append(T["none_obj"])
    else:
        out += [T["obj_note"].format(**names), ""]
        for n, o in enumerate(objections, 1):
            if o["kind"] == "gap":
                i = o["item"]
                out.append("%d. %s" % (n, T["obj_gap"].format(feature=i["feature"], **names)))
                out.append("   " + T["obj_gap_data"].format(ref=ref(i), theirs=V[i["theirs"]],
                                                            us=V[i["ours"]], tag=tag(i), **names))
            else:
                p = o["theme"]
                q = p["quotes"][0] if p["quotes"] else {"quote": "", "url": ""}
                out.append("%d. %s" % (n, T["obj_praise"].format(**names)))
                out.append("   " + T["obj_praise_data"].format(
                    ref=ref(p), label=p["label"], nr=_n(p["count"], T["n_review"]),
                    quote=q["quote"], url=q["url"]))

    out += ["", T["prices"], "", T["prices_todo"].format(**names), "", "---"]

    out += ["", T["swot"].format(**names), "", T["swot_note"], ""]
    S = card.get("differentiators", [])
    W = card.get("gaps", [])
    O = [(T["opp_line"], t) for t in card.get("weak", [])]
    O += [(T["req_line"], t) for t in card.get("asked", [])]
    for head, lines in (("S", [row_line(i) for i in S]), ("W", [row_line(i) for i in W]),
                        ("O", [f.format(label=t["label"], thin=T["thin"] if t["thin"] else "",
                                        nc=_n(t["count"], T["n_complaint"]),
                                        nr=_n(t["count"], T["n_review"]),
                                        ns=_n(t["sources"], T["n_source"]), ref=ref(t))
                               for f, t in O]),
                        ("T", [T["threat_line"].format(label=t["label"], ref=ref(t),
                                                       nr=_n(t["count"], T["n_review"]))
                               for t in card.get("strong", [])])):
        out += [T[head].format(**names), ""] + (lines or [T["none"]]) + [""]

    out += [T["page"], ""]
    if not card["has_features"]:
        out.append(T["no_features"])
    else:
        pg = card["page"]
        out += [T["page_note"].format(days=STALE_DAYS, date=_date(card["as_of"], lang)), ""]
        if pg["rows"]:
            out += [T["page_head"].format(**names), "| --- | --- | --- | --- | --- |"]
            for i in pg["rows"]:
                out.append("| %s | %s | %s | %s | %s |" % (
                    _cell(i["feature"]), V[i["ours"]], V[i["theirs"]],
                    _cell(i["tag"]["source"]), _date(i["tag"]["checked"], lang)))
            out += ["", T["balance"].format(wins=pg["wins"], losses=pg["losses"],
                                            ties=pg["ties"], **names)]
            if pg["lopsided"]:
                out += ["", T["lopsided"].format(n=pg["lopsided"], **names)]
        else:
            out.append(T["page_none"])
        if pg["excluded"]:
            groups = {}
            for i in pg["excluded"]:
                groups.setdefault(", ".join(T["why"][w] for w in i["why"]), []).append(i)
            out += ["", T["excluded"]]
            out += ["- %s: %s" % (why, listing(items)) for why, items in groups.items()]

    out += ["", T["footer"], ""]
    if card["has_feedback"]:
        s = card["sample"]
        out.append(T["sample"].format(n=s["reviews"], ns=_n(len(s["sources"] or []),
                                                            T["n_source"]),
                                      names=", ".join(s["sources"] or []) or "-",
                                      rated=s["rated"], dropped=s["dropped"] or 0,
                                      dupes=s["duplicates"] or 0))
        if (s["reviews"] or 0) < 30:
            out.append(T["small"])
        if s.get("dominant_source"):
            d = s["dominant_source"]
            out.append(T["dominant"].format(share=d["share_pct"], source=d["source"]))
    else:
        out.append(T["no_feedback"])
    if card["has_features"]:
        c = card["claims"]
        out.append(T["matrix"].format(nrows=_n(c["rows"], T["n_row"]),
                                      verified=c["verified"], stale=c["stale"],
                                      assumed=c["assumed"], **names))
        if c["first"]:
            out.append(T["checked_range"].format(first=_date(c["first"], lang),
                                                 last=_date(c["last"], lang)))
    else:
        out.append(T["no_features"])
    out.append(T["asof"].format(date=_date(card["as_of"], lang), days=STALE_DAYS))
    if card["problems"]:
        out += ["", T["fix"]] + ["- " + T["bad_date"].format(**p) for p in card["problems"]]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--feedback", help="output of reviews.py --json")
    ap.add_argument("--features", help="the feature matrix CSV (teardown/features.csv)")
    ap.add_argument("--target", required=True, help="the competitor's name")
    ap.add_argument("--ours", required=True, help="our product's name")
    ap.add_argument("--as-of", help="YYYY-MM-DD, the card's date (default today)")
    ap.add_argument("--lang", choices=sorted(TEXT), default="en")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", help="write the card here")
    args = ap.parse_args(argv)
    if not args.feedback and not args.features:
        print("battlecard: pass --feedback, --features or both", file=sys.stderr)
        return 2
    try:
        as_of = (_dt.datetime.strptime(args.as_of, "%Y-%m-%d").date() if args.as_of
                 else _dt.date.today())
        feedback = load_feedback(args.feedback) if args.feedback else None
        rows = parity.load(args.features) if args.features else None
    except (CardError, parity.MatrixError, OSError, ValueError) as exc:
        print("battlecard: %s" % exc, file=sys.stderr)
        return 2
    card = build(feedback, rows, args.target, args.ours, as_of, args.lang)
    text = (json.dumps(card, indent=2, ensure_ascii=False) + "\n" if args.json
            else render(card, args.lang))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
