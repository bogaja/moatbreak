#!/usr/bin/env python3
"""Store listing check for the Moatbreak skill (launch). Standard library only.

Checks the new product's App Store and Google Play texts before they are
submitted: every field within the store's character limit, no field left
empty, and none of the original's names in any field, in German spelling
variants (Müller, Mueller) or as a near spelling ("Calendy" for "Calendly").
Store rules forbid other apps' names in the metadata, and a listing that
leans on the original's name is a confusion and trademark risk in the EU.
It exits 1 on any failure, so it can block a release.

Origin and licence: see NOTICE.md and LICENSE.

    python3 listing.py teardown/listing.json --config teardown/brand.json
    python3 listing.py teardown/listing.json --config teardown/brand.json --lang de \\
        --markdown --out teardown/listing.md
    python3 listing.py teardown/listing.json --avoid "Calendly" --json

The listing file (from templates/listing.json) holds the fields of one or
both stores, or a "locales" object with them per store language:

    {"app_store": {"name", "subtitle", "keywords", "promotional_text", "description"},
     "google_play": {"title", "short_description", "full_description"}}

Limits in characters (the stores' published limits; check them again before
a release): App Store name 30, subtitle 30, keywords 100, promotional text
170, description 4000; Google Play title 30, short description 80, full
description 4000. Characters are counted as Unicode code points.

Names come from "avoid" in teardown/brand.json and from --avoid. A near
spelling is a word at least 4 letters long that is 85% similar to a
one-word name (difflib ratio, after umlauts are folded).
"""

import argparse
import difflib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import sweep  # noqa: E402  name patterns with German spelling variants

LIMITS = {
    "app_store": (("name", 30), ("subtitle", 30), ("keywords", 100),
                  ("promotional_text", 170), ("description", 4000)),
    "google_play": (("title", 30), ("short_description", 80), ("full_description", 4000)),
}
STORES = {"app_store": "App Store", "google_play": "Google Play"}
NEAR = 0.85
WORD = re.compile(r"[^\W_]{4,}")
FOLD = (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss"))

TEXT = {
    "en": {
        "title": "Store listing check",
        "head": ["locale", "store", "field", "characters", "limit", "result"],
        "ok": "ok", "too_long": "FAIL: {n} over", "empty": "FAIL: empty",
        "name": "FAIL: name of the original: {match}",
        "near": "FAIL: near spelling of {name}: {match}",
        "all_ok": "Fields checked: {n}. All within the limit, none empty, none naming the "
                  "original.",
        "failed": "Fields checked: {n}. Failing: {bad}. Fix them before the listing is "
                  "submitted.",
        "no_names": "No names checked: pass --config teardown/brand.json (its \"avoid\" list) "
                    "or --avoid.",
        "unknown": "Not a field of {store}, not checked: {fields}.",
        "limits": "Limits as published by the stores; check them again before a release. "
                  "Store rules also forbid other apps' names in keywords and descriptions.",
    },
    "de": {
        "title": "Prüfung der Store-Einträge",
        "head": ["Sprache", "Store", "Feld", "Zeichen", "Grenze", "Ergebnis"],
        "ok": "ok", "too_long": "NICHT OK: {n} zu viel", "empty": "NICHT OK: leer",
        "name": "NICHT OK: Name des Originals: {match}",
        "near": "NICHT OK: ähnliche Schreibweise wie {name}: {match}",
        "all_ok": "Geprüfte Felder: {n}. Alle innerhalb der Grenze, keines leer, keines nennt "
                  "das Original.",
        "failed": "Geprüfte Felder: {n}. Nicht ok: {bad}. Vor dem Einreichen korrigieren.",
        "no_names": "Keine Namen geprüft: --config teardown/brand.json (die Liste \"avoid\") "
                    "oder --avoid übergeben.",
        "unknown": "Kein Feld von {store}, nicht geprüft: {fields}.",
        "limits": "Grenzen wie von den Stores veröffentlicht; vor jeder Veröffentlichung neu "
                  "prüfen. Die Store-Regeln verbieten auch Namen anderer Apps in Keywords und "
                  "Beschreibungen.",
    },
}


class ListingError(Exception):
    pass


def _fold(word):
    w = word.casefold()
    for a, b in FOLD:
        w = w.replace(a, b)
    return w


def name_checks(avoid):
    """[(name, exact regex, folded one-word name or None)]."""
    out = []
    for name in avoid:
        name = name.strip()
        if not name:
            continue
        words = [w for w in re.split(r"[\s_.-]+", name) if w]
        single = _fold(words[0]) if len(words) == 1 and len(words[0]) >= 4 else None
        out.append((name, sweep._name_regex(name), single))
    return out


def find_names(text, checks):
    """('name', name, match) or ('near', name, word) hits in text."""
    hits = []
    for name, rx, single in checks:
        m = rx.search(text)
        if m:
            hits.append(("name", name, m.group(0)))
            continue
        if single:
            for w in WORD.findall(text):
                f = _fold(w)
                if f != single and difflib.SequenceMatcher(None, f, single).ratio() >= NEAR:
                    hits.append(("near", name, w))
                    break
    return hits


def sections(data):
    """[(locale or None, store, fields)] from a listing file."""
    if not isinstance(data, dict):
        raise ListingError("the listing must be a JSON object")
    if "locales" in data:
        if not isinstance(data["locales"], dict):
            raise ListingError('"locales" must be an object of store languages')
        items = sorted(data["locales"].items())
    else:
        items = [(None, data)]
    out = []
    for locale, block in items:
        for store in LIMITS:
            fields = block.get(store) if isinstance(block, dict) else None
            if fields is None:
                continue
            if not isinstance(fields, dict):
                raise ListingError('"%s" must be an object of fields' % store)
            out.append((locale, store, fields))
    if not out:
        raise ListingError('no "app_store" or "google_play" fields in the listing')
    return out


def check(data, avoid=()):
    checks = name_checks(avoid)
    rows, unknown = [], []
    for locale, store, fields in sections(data):
        known = dict(LIMITS[store])
        extra = sorted(k for k in fields if k not in known and not k.startswith("_"))
        if extra:
            unknown.append({"locale": locale, "store": store, "fields": extra})
        for field, limit in LIMITS[store]:
            if field not in fields:
                continue
            value = fields[field]
            if not isinstance(value, str):
                raise ListingError("%s %s must be text" % (store, field))
            n = len(value)
            problems = []
            if not value.strip():
                problems.append({"kind": "empty"})
            elif n > limit:
                problems.append({"kind": "too_long", "n": n - limit})
            for kind, name, match in find_names(value, checks):
                problems.append({"kind": kind, "name": name, "match": match})
            rows.append({"locale": locale, "store": store, "field": field, "chars": n,
                         "limit": limit, "problems": problems, "pass": not problems})
    return {"fields": rows, "failed": sum(1 for r in rows if not r["pass"]),
            "names_checked": bool(checks), "unknown": unknown}


def render(result, markdown=False, lang="en"):
    T = TEXT.get(lang, TEXT["en"])

    def verdict(r):
        if r["pass"]:
            return T["ok"]
        return "; ".join(T[p["kind"]].format(**p) for p in r["problems"])

    out = [("# " if markdown else "") + T["title"], ""]
    rows = [[r["locale"] or "-", STORES[r["store"]], r["field"], str(r["chars"]),
             str(r["limit"]), verdict(r)] for r in result["fields"]]
    if markdown:
        out.append("| " + " | ".join(T["head"]) + " |")
        out.append("|" + " --- |" * len(T["head"]))
        out += ["| " + " | ".join(c.replace("|", "\\|") for c in row) + " |" for row in rows]
    else:
        out += ["  ".join(row) for row in rows]
    out.append("")
    n = len(result["fields"])
    out.append(T["failed"].format(n=n, bad=result["failed"]) if result["failed"]
               else T["all_ok"].format(n=n))
    if not result["names_checked"]:
        out.append(T["no_names"])
    for u in result["unknown"]:
        out.append(T["unknown"].format(store=STORES[u["store"]] + (
            " (%s)" % u["locale"] if u["locale"] else ""), fields=", ".join(u["fields"])))
    out.append(T["limits"])
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("listing", help="teardown/listing.json")
    ap.add_argument("--config", help="teardown/brand.json, for the original's names (avoid)")
    ap.add_argument("--avoid", default="", help="more names, comma-separated")
    ap.add_argument("--lang", choices=sorted(TEXT), default="en")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", help="write the report (or the JSON) here")
    args = ap.parse_args(argv)
    avoid = [x for x in args.avoid.split(",") if x.strip()]
    try:
        with open(args.listing, encoding="utf-8") as fh:
            data = json.load(fh)
        if args.config:
            with open(args.config, encoding="utf-8") as fh:
                avoid += list(json.load(fh).get("avoid", []))
        result = check(data, avoid)
    except (ListingError, OSError, ValueError, AttributeError) as exc:
        print("listing: %s" % exc, file=sys.stderr)
        return 2
    text = (json.dumps(result, indent=2, ensure_ascii=False) + "\n" if args.json
            else render(result, args.markdown, args.lang))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    else:
        sys.stdout.write(text)
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
