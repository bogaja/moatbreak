#!/usr/bin/env python3
"""Feature parity and effort estimate for the Moatbreak skill. Standard library only.

Reads the feature matrix written in recon mode and filled in during the build,
and answers three questions: how much of the original does the new product
do, what is missing, and how much work is left. The effort part turns the
same matrix into an offer: MVP (must), + should, + could, in person-days and
optionally in money, with overheads and fixed items on top.

Origin and licence: see NOTICE.md and LICENSE.

    python3 parity.py teardown/features.csv
    python3 parity.py teardown/features.csv --lang de --markdown --out teardown/parity.md
    python3 parity.py teardown/features.csv --estimate-only --lang de --markdown \\
        --buffer 20 --overhead "QA=15,PM=10" --fixed "Setup=2-3,Design=5-8" \\
        --day-rate 650 --out teardown/estimate.md
    python3 parity.py teardown/features.csv --visual teardown/diffs/*.json
    python3 parity.py teardown/features.csv --fail-under 80

Columns (extra columns are ignored; German values work too):

    feature    what it does, in plain words ("reschedule a booking")
    area       the screen, page type or flow it belongs to ("checkout")
    priority   must | should | could            (P0-P2, muss | soll | kann)
    original   yes | no | unknown               (ja | nein | unbekannt | ?)
    clone      yes | partial | no | skip        (ja | teilweise | nein | entfällt)
    effort     XS | S | M | L | XL, or person-days: 3, 2-4, 1,5   (optional)
    notes      anything. For skip, say why ("licensed content, out of scope")

Parity: must 3, should 2, could 1; yes counts 1, partial 0.5, no 0. skip rows
and rows where original is "no" (your additions) are left out of the parity
score and listed separately. "unknown" counts as the original's feature but
is listed as unverified, so guesses never pass silently as facts.

Effort: sizes map to person-day ranges (XS 0.25-0.5, S 0.5-1, M 1-3, L 3-6,
XL 6-12; override with --effort-map). Remaining effort counts what is not
built yet (partial counts half) and includes your additions. --buffer adds a
contingency in percent to the feature effort. --overhead adds percentages of
the feature effort (incl. buffer) such as QA or project management.
--fixed adds person-day items that do not depend on scope, such as setup.
Rows without an effort are reported as unestimated, never guessed.

With --visual, layout scores from imgdiff.py --json are averaged and the
overall score is 80% features + 20% layout. Features are what users pay for.
"""

import argparse
import csv
import json
import re
import sys

WEIGHT = {"must": 3, "should": 2, "could": 1, "p0": 3, "p1": 2, "p2": 1,
          "muss": 3, "soll": 2, "kann": 1}
CREDIT = {"yes": 1.0, "done": 1.0, "ja": 1.0, "fertig": 1.0,
          "partial": 0.5, "teilweise": 0.5, "teils": 0.5,
          "no": 0.0, "nein": 0.0, "": 0.0, "todo": 0.0, "offen": 0.0}
SKIP = {"skip", "entfällt", "entfaellt", "übersprungen", "uebersprungen", "n/a"}
NO = {"no", "n", "false", "nein"}
UNKNOWN = {"?", "unknown", "unbekannt", "unklar", "unsure"}
EFFORT_MAP = {"xs": (0.25, 0.5), "s": (0.5, 1.0), "m": (1.0, 3.0),
              "l": (3.0, 6.0), "xl": (6.0, 12.0)}

TEXT = {
    "en": {
        "prio": {3: "must", 2: "should", 1: "could"},
        "status": {1.0: "done", 0.5: "partial", 0.0: "open"},
        "feature_1": "feature", "feature_n": "features",
        "parity": "Parity: %s / 100",
        "features": "features %s  (%d counted, must-haves %d of %d done)",
        "layout": "layout   %s  (%d screens compared)",
        "no_parity": "No features of the original in the matrix yet, so parity cannot be "
                     "measured. Run recon first, or use --estimate-only for an offer.",
        "not_shippable": "Not shippable yet: %d must-have features are not done.",
        "by_area": "By area, weakest first",
        "missing": "Missing, by priority",
        "missing_note": "Sorted by priority, then area. Order the build by dependencies, "
                        "core loop first.",
        "none_missing": "- nothing. Every counted feature is done.",
        "skipped": "Left out on purpose (not scored, not in the estimate)",
        "no_reason": "no reason given, add one",
        "extras": "Yours, not in the original (no parity, but counted as work)",
        "unverified": "Unverified: %d rows have original = unknown. They are counted as "
                      "the original's features. Verify before quoting: %s",
        "screens": "Screens",
        "fix": "Fix in the matrix",
        "estimate_title": "Effort estimate",
        "effort": "Remaining effort (person-days)",
        "scope": "scope", "count": "features", "days": "person-days",
        "feat_days": "feature days", "overhead": "overheads", "fixed": "fixed", "total": "total days",
        "mvp": "MVP (must)",
        "plus_should": "+ should",
        "plus_could": "+ could (everything)",
        "own": "%d (%d own)",
        "unestimated": "%d open features have no effort yet, so the totals are too low. "
                       "Estimate them: %s",
        "buffer": "Contingency: %s%% on the feature effort.",
        "overhead_note": "Overheads (%% of the feature effort incl. contingency): %s.",
        "fixed_note": "Fixed items (person-days, no contingency): %s.",
        "no_effort": "No effort column filled in. Add XS/S/M/L/XL or person-days per "
                     "feature to get an estimate.",
    },
    "de": {
        "prio": {3: "Muss", 2: "Soll", 1: "Kann"},
        "status": {1.0: "fertig", 0.5: "teilweise", 0.0: "offen"},
        "feature_1": "Feature", "feature_n": "Features",
        "parity": "Parität: %s / 100",
        "features": "Features %s  (%d gezählt, Muss-Features %d von %d fertig)",
        "layout": "Layout   %s  (%d Screens verglichen)",
        "no_parity": "Noch keine Features des Originals in der Matrix, Parität ist daher "
                     "nicht messbar. Erst Recon, oder --estimate-only für ein Angebot.",
        "not_shippable": "Noch nicht auslieferbar, offene Muss-Features: %d.",
        "by_area": "Nach Bereich, schwächster zuerst",
        "missing": "Fehlt, nach Priorität",
        "missing_note": "Sortiert nach Priorität, dann Bereich. Die Bau-Reihenfolge richtet "
                        "sich nach Abhängigkeiten, Kernablauf zuerst.",
        "none_missing": "- nichts. Jedes gezählte Feature ist fertig.",
        "skipped": "Bewusst weggelassen (nicht bewertet, nicht in der Schätzung)",
        "no_reason": "kein Grund angegeben, bitte ergänzen",
        "extras": "Eigene Features, nicht im Original (keine Parität, aber Aufwand)",
        "unverified": "Ungeprüft: %d Zeilen mit original = unbekannt. Sie zählen als "
                      "Features des Originals. Vor dem Angebot prüfen: %s",
        "screens": "Screens",
        "fix": "In der Matrix korrigieren",
        "estimate_title": "Aufwandsschätzung",
        "effort": "Restaufwand (Personentage)",
        "scope": "Umfang", "count": "Features", "days": "Personentage",
        "feat_days": "Feature-PT", "overhead": "Zuschläge", "fixed": "Pauschal", "total": "Gesamt-PT",
        "mvp": "MVP (Muss)",
        "plus_should": "+ Soll",
        "plus_could": "+ Kann (alles)",
        "own": "%d (davon %d eigene)",
        "unestimated": "%d offene Features ohne Aufwand, die Summen sind also zu niedrig. "
                       "Bitte schätzen: %s",
        "buffer": "Puffer: %s %% auf den Feature-Aufwand.",
        "overhead_note": "Zuschläge (in %% vom Feature-Aufwand inkl. Puffer): %s.",
        "fixed_note": "Pauschalen (Personentage, ohne Puffer): %s.",
        "no_effort": "Keine Aufwandsspalte gefüllt. XS/S/M/L/XL oder Personentage pro "
                     "Feature eintragen, dann gibt es eine Schätzung.",
    },
}


class MatrixError(Exception):
    pass


def load(path):
    try:
        return _load(path)
    except UnicodeDecodeError:
        raise MatrixError(NOT_UTF8 % path)


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
            raise MatrixError("%s is empty" % path)
        fields = [f.strip().lower() for f in reader.fieldnames]
        for need in ("feature", "priority", "clone"):
            if need not in fields:
                raise MatrixError("%s has no '%s' column. Columns needed: "
                                  "feature, area, priority, original, clone, effort, notes"
                                  % (path, need))
        rows = []
        for i, raw in enumerate(reader, start=2):
            if None in raw:   # csv puts the cells beyond the header under None
                raise MatrixError("%s line %d has more fields than the header; put quote marks "
                                  "around a cell that contains a comma (\"Note, with a comma\")"
                                  % (path, i))
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
            if not row.get("feature"):
                continue
            row["line"] = i
            rows.append(row)
    return rows


def parse_effort(value, effort_map=EFFORT_MAP):
    """Return (low, high) person-days, or None if blank or unreadable."""
    v = (value or "").strip().lower().replace(",", ".")
    if not v:
        return None
    if v in effort_map:
        lo, hi = effort_map[v]
        return float(lo), float(hi)
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(?:(?:-|–|bis|to)\s*(\d+(?:\.\d+)?))?\s*"
                 r"(?:pt|pd|d|tage?|days?)?$", v)
    if not m:
        return None
    lo = float(m.group(1))
    hi = float(m.group(2)) if m.group(2) else lo
    if hi < lo:
        lo, hi = hi, lo
    return lo, hi


def parse_items(text, percent=False):
    """'QA=15,PM=10' or 'Setup=2-3;Design=5-8' -> [(name, low, high)]."""
    text = (text or "").strip()
    if not text:
        return []
    sep = ";" if ";" in text else ","
    items = []
    for part in text.split(sep):
        if not part.strip():
            continue
        if "=" not in part:
            raise ValueError("'%s' needs the form name=value" % part.strip())
        name, value = part.split("=", 1)
        if percent:
            pct = float(value.strip().rstrip("%").replace(",", "."))
            items.append((name.strip(), pct, pct))
        else:
            e = parse_effort(value)
            if e is None:
                raise ValueError("'%s' is not person-days like 2 or 2-3" % value.strip())
            items.append((name.strip(), e[0], e[1]))
    return items


def score(rows, effort_map=EFFORT_MAP):
    counted, skipped, extras, problems, unverified = [], [], [], [], []
    for row in rows:
        original = row.get("original", "yes").lower() or "yes"
        clone = row.get("clone", "").lower()
        prio = row.get("priority", "").lower()
        if row.get("effort") and parse_effort(row["effort"], effort_map) is None:
            problems.append("line %d: effort '%s' is not XS/S/M/L/XL or person-days, ignored"
                            % (row["line"], row["effort"]))
        if prio not in WEIGHT:
            problems.append("line %d: priority '%s' is not must/should/could, counted as could"
                            % (row["line"], row.get("priority", "")))
        weight = WEIGHT.get(prio, 1)
        if clone in SKIP:
            skipped.append(dict(row, weight=weight, credit=1.0))
            continue
        if clone not in CREDIT:
            problems.append("line %d: clone '%s' is not yes/partial/no/skip, counted as no"
                            % (row["line"], row.get("clone", "")))
        entry = dict(row, weight=weight, credit=CREDIT.get(clone, 0.0))
        if original in NO:
            extras.append(entry)
            continue
        if original in UNKNOWN:
            unverified.append(entry)
        counted.append(entry)

    total = sum(r["weight"] for r in counted)
    got = sum(r["weight"] * r["credit"] for r in counted)
    feature_score = 100.0 * got / total if total else 0.0

    areas = {}
    for r in counted:
        a = r.get("area") or "(no area)"
        t = areas.setdefault(a, [0.0, 0.0, 0])
        t[0] += r["weight"] * r["credit"]
        t[1] += r["weight"]
        t[2] += 1
    by_area = sorted(
        ({"area": a, "score": round(100.0 * g / t, 1) if t else 0.0, "features": n}
         for a, (g, t, n) in areas.items()),
        key=lambda d: d["score"])

    missing = [r for r in counted if r["credit"] < 1.0]
    missing.sort(key=lambda r: (-r["weight"], r["credit"], r.get("area", ""), r["feature"]))

    def brief(r):
        return {"feature": r["feature"], "area": r.get("area", ""),
                "weight": r["weight"], "credit": r["credit"],
                "clone": r.get("clone", "") or "no", "effort": r.get("effort", ""),
                "notes": r.get("notes", "")}

    musts = [r for r in counted if r["weight"] == 3]
    return {
        "feature_score": round(feature_score, 1),
        "counted": len(counted),
        "must_have_done": sum(1 for r in musts if r["credit"] == 1.0),
        "must_have_total": len(musts),
        "by_area": by_area,
        "missing": [brief(r) for r in missing],
        "skipped": [brief(r) for r in skipped],
        "extras": [brief(r) for r in extras],
        "unverified": [r["feature"] for r in unverified],
        "problems": problems,
        "_open": [dict(r, own=False) for r in counted if r["credit"] < 1.0]
                 + [dict(r, own=True) for r in extras if r["credit"] < 1.0],
    }


def estimate(result, effort_map=EFFORT_MAP, buffer_pct=0.0, day_rate=None,
             overhead=(), fixed=()):
    """Remaining effort by cumulative scope: must, + should, + could."""
    open_rows = result.pop("_open", [])
    factor = 1.0 + (buffer_pct or 0.0) / 100.0
    ov_pct = sum(p for _, p, _ in overhead) / 100.0
    fx_lo = sum(lo for _, lo, _ in fixed)
    fx_hi = sum(hi for _, _, hi in fixed)
    tiers = []
    any_effort = False
    for min_weight, key in ((3, "mvp"), (2, "plus_should"), (1, "plus_could")):
        lo = hi = 0.0
        n = own = 0
        for r in open_rows:
            if r["weight"] < min_weight:
                continue
            n += 1
            own += 1 if r["own"] else 0
            e = parse_effort(r.get("effort", ""), effort_map)
            if e is None:
                continue
            any_effort = True
            remaining = 1.0 - r["credit"]
            lo += e[0] * remaining
            hi += e[1] * remaining
        f_lo, f_hi = lo * factor, hi * factor
        o_lo, o_hi = f_lo * ov_pct, f_hi * ov_pct
        tier = {"scope": key, "features": n, "own": own,
                "feature_low": round(f_lo, 1), "feature_high": round(f_hi, 1),
                "overhead_low": round(o_lo, 1), "overhead_high": round(o_hi, 1),
                "fixed_low": round(fx_lo, 1), "fixed_high": round(fx_hi, 1),
                "days_low": round(f_lo + o_lo + fx_lo, 1),
                "days_high": round(f_hi + o_hi + fx_hi, 1)}
        if day_rate:
            tier["cost_low"] = round(tier["days_low"] * day_rate)
            tier["cost_high"] = round(tier["days_high"] * day_rate)
        tiers.append(tier)
    unestimated = [r["feature"] for r in open_rows
                   if parse_effort(r.get("effort", ""), effort_map) is None]
    result["effort"] = {"tiers": tiers, "unestimated": unestimated,
                        "buffer_pct": buffer_pct or 0.0, "day_rate": day_rate,
                        "overhead": [{"name": n, "pct": p} for n, p, _ in overhead],
                        "fixed": [{"name": n, "low": lo, "high": hi} for n, lo, hi in fixed],
                        "has_effort": any_effort}
    return result


def visual_scores(paths):
    scores = []
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            data = json.load(fh)
        if "score" not in data:
            raise MatrixError("%s is not imgdiff.py --json output" % p)
        name = data.get("files", {}).get("clone", p)
        scores.append({"file": name, "score": float(data["score"]),
                       "mode": data.get("mode", "layout")})
    return scores


def combine(result, visuals):
    if visuals:
        layout = sum(v["score"] for v in visuals) / len(visuals)
        result["visual"] = visuals
        result["layout_score"] = round(layout, 1)
        result["overall"] = round(0.8 * result["feature_score"] + 0.2 * layout, 1)
    else:
        result["overall"] = result["feature_score"]
    return result


def _num(x, lang):
    s = ("%.1f" % x).rstrip("0").rstrip(".")
    return s.replace(".", ",") if lang == "de" else s


def _dec(x, lang):
    s = "%.1f" % x
    return s.replace(".", ",") if lang == "de" else s


def _money(x, lang):
    s = "{:,.0f}".format(x)
    return s.replace(",", ".") if lang == "de" else s


def _range(lo, hi, lang, fmt=_num):
    return fmt(lo, lang) if lo == hi else "%s - %s" % (fmt(lo, lang), fmt(hi, lang))


def _features(n, T):
    return "%d %s" % (n, T["feature_1"] if n == 1 else T["feature_n"])


def render_effort(eff, T, lang, currency, h):
    out = [h + T["effort"], ""]
    if not eff["has_effort"]:
        return out + [T["no_effort"]]
    cost = bool(eff["day_rate"])
    split = bool(eff["overhead"] or eff["fixed"])
    cols = [T["scope"], T["count"]]
    cols += [T["feat_days"], T["overhead"], T["fixed"], T["total"]] if split else [T["days"]]
    cols += [currency] if cost else []
    out.append("| " + " | ".join(cols) + " |")
    out.append("|" + " --- |" * len(cols))
    for t in eff["tiers"]:
        n = T["own"] % (t["features"], t["own"]) if t["own"] else str(t["features"])
        cells = [T[t["scope"]], n]
        if split:
            cells += [_range(t["feature_low"], t["feature_high"], lang),
                      _range(t["overhead_low"], t["overhead_high"], lang),
                      _range(t["fixed_low"], t["fixed_high"], lang),
                      _range(t["days_low"], t["days_high"], lang)]
        else:
            cells.append(_range(t["days_low"], t["days_high"], lang))
        if cost:
            cells.append(_range(t["cost_low"], t["cost_high"], lang, _money))
        out.append("| " + " | ".join(cells) + " |")
    notes = []
    if eff["buffer_pct"]:
        notes.append(T["buffer"] % _num(eff["buffer_pct"], lang))
    if eff["overhead"]:
        notes.append(T["overhead_note"] % ", ".join(
            "%s %s %%" % (o["name"], _num(o["pct"], lang)) for o in eff["overhead"]))
    if eff["fixed"]:
        notes.append(T["fixed_note"] % ", ".join(
            "%s %s" % (f["name"], _range(f["low"], f["high"], lang)) for f in eff["fixed"]))
    if eff["unestimated"]:
        notes.append(T["unestimated"] % (len(eff["unestimated"]),
                                         "; ".join(eff["unestimated"][:12])))
    if notes:
        out += [""] + notes
    return out


def render(result, markdown=False, lang="en", currency="EUR", estimate_only=False):
    T = TEXT.get(lang, TEXT["en"])
    h = "## " if markdown else ""
    out = []
    if estimate_only:
        out += [("# " if markdown else "") + T["estimate_title"], ""]
        if result.get("effort"):
            out += render_effort(result["effort"], T, lang, currency, h)
        if result["unverified"]:
            out += ["", T["unverified"] % (len(result["unverified"]),
                                           "; ".join(result["unverified"][:12]))]
        if result["skipped"]:
            out += ["", h + T["skipped"]]
            for m in result["skipped"]:
                out.append("- %s: %s" % (m["feature"], m["notes"] or T["no_reason"]))
        if result["problems"]:
            out += ["", h + T["fix"]] + ["- %s" % p for p in result["problems"]]
        return "\n".join(out)

    if result["counted"] == 0:
        out.append(T["no_parity"])
    else:
        out.append(h + T["parity"] % _dec(result["overall"], lang))
        out.append("")
        out.append(T["features"] % (_dec(result["feature_score"], lang), result["counted"],
                                    result["must_have_done"], result["must_have_total"]))
        if "layout_score" in result:
            out.append(T["layout"] % (_dec(result["layout_score"], lang),
                                      len(result["visual"])))
        if result["must_have_done"] < result["must_have_total"]:
            out += ["", T["not_shippable"] % (result["must_have_total"]
                                              - result["must_have_done"])]
        out += ["", h + T["by_area"]]
        for a in result["by_area"]:
            out.append("- %-28s %5s  (%s)" % (a["area"], _dec(a["score"], lang),
                                             _features(a["features"], T)))
        out += ["", h + T["missing"], "", T["missing_note"]]
        if not result["missing"]:
            out.append(T["none_missing"])
        for m in result["missing"]:
            note = ("  (%s)" % m["notes"]) if m["notes"] else ""
            eff = (" [%s]" % m["effort"]) if m["effort"] else ""
            out.append("- [%s] %s: %s, %s%s%s" % (T["prio"][m["weight"]], m["area"] or "-",
                                                   m["feature"], T["status"][m["credit"]],
                                                   eff, note))
    if result["unverified"]:
        out += ["", T["unverified"] % (len(result["unverified"]),
                                       "; ".join(result["unverified"][:12]))]
    if result["skipped"]:
        out += ["", h + T["skipped"]]
        for m in result["skipped"]:
            out.append("- %s: %s" % (m["feature"], m["notes"] or T["no_reason"]))
    if result["extras"]:
        out += ["", h + T["extras"]]
        for m in result["extras"]:
            out.append("- [%s] %s: %s" % (T["prio"][m["weight"]], m["feature"],
                                          T["status"][m["credit"]]))
    if result.get("effort"):
        out += [""] + render_effort(result["effort"], T, lang, currency, h)
    if result.get("visual"):
        out += ["", h + T["screens"]]
        for v in sorted(result["visual"], key=lambda d: d["score"]):
            out.append("- %-40s %5s" % (v["file"], _dec(v["score"], lang)))
    if result["problems"]:
        out += ["", h + T["fix"]] + ["- %s" % p for p in result["problems"]]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("matrix", help="the feature matrix CSV")
    ap.add_argument("--visual", nargs="*", default=[],
                    help="imgdiff.py --json outputs to fold in")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--lang", choices=sorted(TEXT), default="en")
    ap.add_argument("--estimate-only", action="store_true",
                    help="only the effort estimate, for offers (no parity lines)")
    ap.add_argument("--buffer", type=float, default=0.0,
                    help="contingency in percent on the feature effort (e.g. 20)")
    ap.add_argument("--overhead", default="",
                    help='percent of the feature effort, e.g. "QA=15,PM=10"')
    ap.add_argument("--fixed", default="",
                    help='person-day items, e.g. "Setup=2-3;Design=5-8"')
    ap.add_argument("--day-rate", type=float, help="price per person-day, for a cost range")
    ap.add_argument("--currency", default="EUR")
    ap.add_argument("--effort-map",
                    help='JSON file mapping sizes to [low, high] days, e.g. {"m": [2, 4]}')
    ap.add_argument("--out", help="write the report to this file")
    ap.add_argument("--fail-under", type=float)
    args = ap.parse_args(argv)
    effort_map = dict(EFFORT_MAP)
    try:
        if args.effort_map:
            with open(args.effort_map, encoding="utf-8") as fh:
                for k, v in json.load(fh).items():
                    effort_map[k.lower()] = (float(v[0]), float(v[1]))
        overhead = parse_items(args.overhead, percent=True)
        fixed = parse_items(args.fixed)
        result = score(load(args.matrix), effort_map)
        result = estimate(result, effort_map, args.buffer, args.day_rate, overhead, fixed)
        result = combine(result, visual_scores(args.visual))
    except (MatrixError, OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        print("parity: %s" % exc, file=sys.stderr)
        return 2
    if args.json:
        text = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        text = render(result, markdown=args.markdown, lang=args.lang, currency=args.currency,
                      estimate_only=args.estimate_only)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print("wrote %s" % args.out)
    else:
        print(text)
    if args.fail_under is not None and result["overall"] < args.fail_under:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
