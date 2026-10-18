#!/usr/bin/env python3
"""WCAG 2.2 colour contrast check for the Moatbreak skill. Standard library only.

Computes the contrast ratio of colour pairs with the WCAG relative-luminance
formula and says which levels each pair meets. For every pair that misses
the AA level its use needs, it computes the nearest darker shade and lighter
tint of the foreground that passes, so the fix is a number, not a guess. Run
it on the new palette in brand mode and again before launch: the German BFSG
makes WCAG AA a legal topic for many consumer services.

Written fresh for Moatbreak from the WCAG 2.2 definitions of relative
luminance and contrast ratio. Licence: see LICENSE.

    python3 contrast.py "#6b7280 on #ffffff"
    python3 contrast.py "#0f766e on #ffffff" "#94a3b8 on #f8fafc" --use ui
    python3 contrast.py --palette teardown/brand.json --lang de --markdown --out teardown/contrast.md
    python3 contrast.py --palette teardown/brand.json "muted on surface" --json

Colours: #rgb, #rrggbb, #rgba, #rrggbbaa, rgb() and rgba(); "auf" works
instead of "on". A transparent foreground is laid over its background first;
the background must be opaque.

Levels (a ratio is never rounded up to pass: 4.499 fails 4.5, and ratios are
shown rounded down to two decimals, so a shown 4.50 always passes 4.5):

    AA text     4.5   SC 1.4.3   normal text
    AA large    3.0   SC 1.4.3   large text: at least 24px, or about 18.7px bold
    AAA text    7.0   SC 1.4.6
    AAA large   4.5   SC 1.4.6
    UI          3.0   SC 1.4.11  component boundaries, focus indicators, icons, chart marks

--use says what the command-line pairs are for: text (default, needs 4.5),
large (3.0) or ui (3.0). A pair passes when it meets AA for its use. Exit 1
if any pair fails, 2 on bad input.

Palette file (JSON):

    {"palette": {"text": "#1a1a1a", "bg": "#ffffff", "primary": "#0f766e",
                 "on-primary": "#ffffff"},
     "pairs": [["text", "bg"], ["on-primary", "primary"], ["primary", "bg", "ui"]]}

"palette" is read first, otherwise "colors" (an object or a list), so
teardown/brand.json works as it is. In brand.json, "colors" holds the
original's brand colours: checking them shows where the original fails,
which is a fix to beat it on, not a check of the new palette. Pairs name
palette entries or colours ("text on bg" as a string works too), with an
optional third element for the use. Pairs on the command line replace the
file's pairs. With no pairs at all, every two colours of the palette are
compared and listed with what they are good for; that grid never fails the
run and has no fixes, because it does not know which colour is the
foreground.

Fixes: the foreground is mixed with black (a shade) or white (a tint) in
steps of 0.1 % until the 8-bit colour passes. Both are reported with the
share mixed in and the CIE76 Delta E to the foreground; the smaller Delta E
is marked as the nearest. The background stays as it is, so put the colour
you are willing to change first: to keep a white label and darken the brand
colour behind it, write "primary on on-primary" (the ratio is the same both
ways).
"""

import argparse
import itertools
import json
import math
import re
import sys

LEVELS = (("aa_text", 4.5), ("aa_large", 3.0), ("aaa_text", 7.0), ("aaa_large", 4.5),
          ("ui", 3.0))
NEED = {"text": 4.5, "large": 3.0, "ui": 3.0}
HEX = re.compile(r"#([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})")
RGB = re.compile(r"rgba?\(\s*(\d{1,3})\s*[,\s]\s*(\d{1,3})\s*[,\s]\s*(\d{1,3})\s*"
                 r"(?:[,/]\s*(\d*\.?\d+)(%?)\s*)?\)", re.I)
PAIR = re.compile(r"\s+(?:on|auf)\s+", re.I)
EPS = 1e-9  # float noise only, far below one 8-bit step

TEXT = {
    "en": {
        "title": "Contrast check (WCAG 2.2)",
        "levels": {"aa_text": "AA text 4.5", "aa_large": "AA large 3", "aaa_text": "AAA text 7",
                   "aaa_large": "AAA large 4.5", "ui": "UI 3"},
        "uses": {"text": "text", "large": "large text", "ui": "UI"},
        "pass": "pass", "fail": "fail", "FAIL": "FAIL",
        "needs": "needs %s",
        "pair": "pair", "ratio": "ratio", "use": "use", "result": "result",
        "flat": "flattened %s",
        "fixes": "Fixes",
        "darker": "darker", "lighter": "lighter", "nearest": "nearest",
        "black": "black", "white": "white",
        "mix": "%s%% %s", "on": "on",
        "unreachable": "none passes on this background",
        "fix_note": "Take a fix into the design tokens and run the check again.",
        "summary": "Pairs checked: %d. Failing AA for their use: %d.",
        "all_pass": "Pairs checked: %d. All meet AA for their use.",
        "grid": "No pairs given, so every two colours of the palette are compared. Name "
                "the pairs the design uses (\"pairs\" in the palette file) for pass/fail "
                "and fixes.",
        "skipped": "Not compared, both transparent (the result depends on what is under "
                   "them): %s.",
        "good_for": "good for %s",
        "nothing": "nothing (below 3:1)",
        "original": "Read \"colors\" from %s: in brand.json these are the original's "
                    "colours. Put the new palette under \"palette\".",
        "legend": "Large text: at least 24px, or about 18.7px bold. UI: component "
                  "boundaries, focus indicators, icons and chart marks against what is next "
                  "to them. Disabled controls and logos are exempt.",
    },
    "de": {
        "title": "Kontrastprüfung (WCAG 2.2)",
        "levels": {"aa_text": "AA Text 4,5", "aa_large": "AA groß 3", "aaa_text": "AAA Text 7",
                   "aaa_large": "AAA groß 4,5", "ui": "UI 3"},
        "uses": {"text": "Text", "large": "großer Text", "ui": "UI"},
        "pass": "erfüllt", "fail": "nicht erfüllt", "FAIL": "NICHT ERFÜLLT",
        "needs": "braucht %s",
        "pair": "Paar", "ratio": "Kontrast", "use": "Zweck", "result": "Ergebnis",
        "flat": "deckend %s",
        "fixes": "Korrekturen",
        "darker": "dunkler", "lighter": "heller", "nearest": "am nächsten",
        "black": "Schwarz", "white": "Weiß",
        "mix": "%s %% %s", "on": "auf",
        "unreachable": "auf diesem Hintergrund nicht erreichbar",
        "fix_note": "Eine Korrektur in die Design-Tokens übernehmen und die Prüfung "
                    "wiederholen.",
        "summary": "Geprüfte Paare: %d. AA für ihren Zweck nicht erfüllt: %d.",
        "all_pass": "Geprüfte Paare: %d. Alle erfüllen AA für ihren Zweck.",
        "grid": "Keine Paare angegeben, daher wird jede Kombination aus zwei Farben der "
                "Palette verglichen. Die Paare, die das Design nutzt, unter \"pairs\" in der "
                "Palettendatei nennen, dann gibt es Ergebnis und Korrekturen.",
        "skipped": "Nicht verglichen, beide transparent (das Ergebnis hängt davon ab, was "
                   "darunter liegt): %s.",
        "good_for": "geeignet für %s",
        "nothing": "nichts (unter 3:1)",
        "original": "\"colors\" aus %s gelesen: In brand.json sind das die Farben des "
                    "Originals. Die neue Palette gehört unter \"palette\".",
        "legend": "Großer Text: mindestens 24px, oder etwa 18,7px fett. UI: Ränder von "
                  "Bedienelementen, Fokusanzeigen, Icons und Diagrammelemente gegen ihre "
                  "Umgebung. Deaktivierte Elemente und Logos sind ausgenommen.",
    },
}


class InputError(ValueError):
    pass


def parse_colour(text):
    """Return (r, g, b, alpha): channels 0-255, alpha 0-1."""
    s = str(text).strip()
    m = HEX.fullmatch(s)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        alpha = int(h[6:8], 16) / 255.0 if len(h) == 8 else 1.0
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)
    m = RGB.fullmatch(s)
    if m:
        rgb = tuple(int(x) for x in m.group(1, 2, 3))
        alpha = 1.0
        if m.group(4):
            alpha = float(m.group(4)) / (100.0 if m.group(5) else 1.0)
        if max(rgb) <= 255 and alpha <= 1:
            return rgb + (alpha,)
    raise InputError("not a colour: %r (use #rrggbb or rgb())" % s)


def to_hex(rgb, alpha=1.0):
    out = "#" + "".join("%02x" % int(c + 0.5) for c in rgb[:3])
    return out + ("%02x" % int(alpha * 255 + 0.5) if alpha < 1 else "")


def _linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    """WCAG relative luminance of an sRGB colour."""
    r, g, b = (_linear(c) for c in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    """WCAG contrast ratio, 1 to 21, the same in both directions."""
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def passes(r, need):
    return r + EPS >= need


def shown(r):
    """Two decimals, rounded down, so what is shown agrees with passes()."""
    return math.floor(r * 100 + EPS * 100) / 100


def flatten(fg, bg):
    """Lay a transparent foreground over an opaque background."""
    if bg[3] < 1:
        raise InputError("the background %s is transparent; contrast depends on what is "
                         "under it, so give the opaque colour" % to_hex(bg, bg[3]))
    a = fg[3]
    return tuple(a * f + (1 - a) * b for f, b in zip(fg[:3], bg[:3]))


def _lab(rgb):
    r, g, b = (_linear(c) for c in rgb[:3])
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3.0) if t > 216 / 24389.0 else (24389 / 27.0 * t + 16) / 116.0
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a, b):
    """CIE76 colour difference."""
    return math.sqrt(sum((p - q) ** 2 for p, q in zip(_lab(a), _lab(b))))


def fix(fg, bg, need):
    """Nearest shade and tint of fg (opaque, 8-bit) that reach `need` on bg."""
    out = {}
    for side, toward, label in (("darker", (0, 0, 0), "black"),
                                ("lighter", (255, 255, 255), "white")):
        out[side] = None
        for k in range(1, 1001):
            t = k / 1000.0
            cand = tuple(int(c + (w - c) * t + 0.5) for c, w in zip(fg, toward))
            r = ratio(cand, bg)
            if passes(r, need):
                out[side] = {"color": to_hex(cand), "ratio": shown(r),
                             "mix": round(t * 100, 1), "with": label,
                             "delta_e": round(delta_e(cand, fg), 1)}
                break
    found = [s for s in ("darker", "lighter") if out[s]]
    out["nearest"] = min(found, key=lambda s: out[s]["delta_e"]) if found else None
    return out


def check(fg, bg, use=None, fg_name=None, bg_name=None):
    flat = flatten(fg, bg)
    r = ratio(flat, bg)
    res = {"fg": to_hex(fg, fg[3]), "bg": to_hex(bg), "fg_name": fg_name, "bg_name": bg_name,
           "ratio": shown(r),
           "levels": dict((k, passes(r, need)) for k, need in LEVELS),
           "good_for": [u for u in ("text", "large", "ui") if passes(r, NEED[u])],
           "use": use, "need": NEED[use] if use else None, "pass": None, "fix": None}
    if fg[3] < 1:
        res["fg_flat"] = to_hex(flat)
    if use:
        res["pass"] = passes(r, NEED[use])
        if not res["pass"]:
            res["fix"] = fix(flat, bg, NEED[use])
    return res


def load_palette(path):
    """Return (key read, [(name, colour)], pairs, is_brand_json)."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise InputError("%s: expected a JSON object with \"palette\" or \"colors\"" % path)
    key = "palette" if "palette" in data else "colors"
    raw = data.get(key) or []
    if isinstance(raw, dict):
        entries = [(str(k), parse_colour(v)) for k, v in raw.items()]
    elif isinstance(raw, list):
        entries = [(None, parse_colour(v)) for v in raw]
    else:
        raise InputError("%s: \"%s\" must be an object or a list" % (path, key))
    pairs = data.get("pairs") or []
    if not isinstance(pairs, list):
        raise InputError("%s: \"pairs\" must be a list" % path)
    return key, entries, pairs, "avoid" in data


def resolve(token, names):
    token = str(token).strip()
    if token in names:
        return names[token], token
    try:
        return parse_colour(token), None
    except InputError:
        raise InputError("unknown colour or palette name: %r" % token)


def split_pair(item, default_use):
    """A pair as "fg on bg", [fg, bg] or [fg, bg, use]."""
    if isinstance(item, str):
        parts, use = PAIR.split(item.strip()), default_use
    elif isinstance(item, list) and len(item) in (2, 3):
        parts, use = item[:2], (item[2] if len(item) == 3 else default_use)
    else:
        parts, use = [], None
    if len(parts) != 2:
        raise InputError("cannot read pair %r: write it as \"#1a1a1a on #ffffff\"" % (item,))
    if use not in NEED:
        raise InputError("unknown use %r in pair %r: text, large or ui" % (use, item))
    return parts[0], parts[1], use


def run(pairs=(), palette=None, use="text"):
    """Check pairs, or the whole palette as a grid. Returns the result dict."""
    entries, file_pairs, note, skipped = [], [], None, []
    if palette:
        key, entries, file_pairs, is_brand = load_palette(palette)
        if key == "colors" and is_brand:
            note = palette
    names = dict((n, c) for n, c in entries if n)
    todo = [split_pair(p, use) for p in pairs] or [split_pair(p, "text") for p in file_pairs]
    results = []
    for fg_tok, bg_tok, u in todo:
        fg, fg_name = resolve(fg_tok, names)
        bg, bg_name = resolve(bg_tok, names)
        results.append(check(fg, bg, u, fg_name, bg_name))
    grid = not todo
    if grid:
        if len(entries) < 2:
            raise InputError("nothing to check: pass pairs like \"#1a1a1a on #ffffff\", or "
                             "--palette with two or more colours")
        for (na, a), (nb, b) in itertools.combinations(entries, 2):
            if a[3] < 1 and b[3] < 1:      # contrast depends on what is under both
                skipped.append([na or to_hex(a, a[3]), nb or to_hex(b, b[3])])
                continue
            if b[3] < 1:                   # the opaque colour is the background
                (na, a), (nb, b) = (nb, b), (na, a)
            results.append(check(a, b, None, na, nb))
        results.sort(key=lambda r: -r["ratio"])
    return {"standard": "WCAG 2.2", "grid": grid, "results": results,
            "failed": sum(1 for r in results if r["pass"] is False), "brand_json": note,
            "skipped": skipped}


def _num(x, lang):
    s = "%.2f" % x
    return s.replace(".", ",") if lang == "de" else s


def _dec(x, lang):
    s = ("%.1f" % x).rstrip("0").rstrip(".")
    return s.replace(".", ",") if lang == "de" else s


def _label(r, T):
    colours = "%s %s %s" % (r["fg"], T["on"], r["bg"])
    if "fg_flat" in r:
        colours += " (%s)" % (T["flat"] % r["fg_flat"])
    if r["fg_name"] or r["bg_name"]:
        names = "%s %s %s" % (r["fg_name"] or r["fg"], T["on"], r["bg_name"] or r["bg"])
        return "%s (%s)" % (names, colours)
    return colours


def _fix_text(f, T, lang):
    out = []
    for side in ("darker", "lighter"):
        s = f[side]
        if not s:
            out.append("%s: %s" % (T[side], T["unreachable"]))
            continue
        line = "%s: %s  %s:1  (%s, dE %s)" % (
            T[side], s["color"], _num(s["ratio"], lang),
            T["mix"] % (_dec(s["mix"], lang), T[s["with"]]), _dec(s["delta_e"], lang))
        if f["nearest"] == side:
            line += ", " + T["nearest"]
        out.append(line)
    return out


def _result(r, T, lang):
    if r["use"] is None:
        good = [T["uses"][u] for u in r["good_for"]]
        return T["good_for"] % ", ".join(good) if good else T["nothing"]
    if r["pass"]:
        return T["pass"]
    return "%s, %s" % (T["FAIL"], T["needs"] % _dec(r["need"], lang))


def render(result, markdown=False, lang="en"):
    T = TEXT[lang]
    rows = result["results"]
    out = []
    if markdown:
        out += ["# " + T["title"], ""]
    else:
        out += [T["title"], ""]
    if result["brand_json"]:
        out += [T["original"] % result["brand_json"], ""]
    if result["grid"]:
        out += [T["grid"], ""]
    if markdown:
        heads = [T["pair"], T["ratio"]] + [T["levels"][k] for k, _ in LEVELS] + [T["use"],
                                                                                T["result"]]
        out.append("| " + " | ".join(heads) + " |")
        out.append("|" + " --- |" * len(heads))
        for r in rows:
            cells = [_label(r, T).replace("|", "/"), _num(r["ratio"], lang) + ":1"]
            cells += [T["pass"] if r["levels"][k] else T["fail"] for k, _ in LEVELS]
            cells += [T["uses"][r["use"]] if r["use"] else "-", _result(r, T, lang)]
            if r["pass"] is False:
                cells[-1] = "**%s**" % cells[-1]
            out.append("| " + " | ".join(cells) + " |")
        failing = [r for r in rows if r["fix"]]
        if failing:
            out += ["", "## " + T["fixes"], ""]
            for r in failing:
                out.append("- **%s** (%s, %s): %s" % (
                    _label(r, T), T["uses"][r["use"]], T["needs"] % _dec(r["need"], lang),
                    "; ".join(_fix_text(r["fix"], T, lang))))
    else:
        for r in rows:
            head = "%s  %s:1" % (_label(r, T), _num(r["ratio"], lang))
            if r["use"]:
                head += "  %s: %s" % (T["uses"][r["use"]], _result(r, T, lang))
            else:
                head += "  " + _result(r, T, lang)
            out.append(head)
            out.append("  " + " | ".join("%s %s" % (T["levels"][k], T["pass"] if r["levels"][k]
                                                    else T["fail"]) for k, _ in LEVELS))
            if r["fix"]:
                out += ["  " + line for line in _fix_text(r["fix"], T, lang)]
            out.append("")
        if out[-1] == "":
            out.pop()
    out.append("")
    if result.get("skipped"):
        out.append(T["skipped"] % ", ".join("%s %s %s" % (a, T["on"], b)
                                            for a, b in result["skipped"]))
    if not result["grid"]:
        if result["failed"]:
            out.append(T["summary"] % (len(rows), result["failed"]) + " " + T["fix_note"])
        else:
            out.append(T["all_pass"] % len(rows))
    out.append(T["legend"])
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("pairs", nargs="*", help='colour pairs, e.g. "#1a1a1a on #ffffff"')
    ap.add_argument("--palette", help="JSON palette file (teardown/brand.json works)")
    ap.add_argument("--use", choices=sorted(NEED), default="text",
                    help="what the command-line pairs are for (default text)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--lang", choices=sorted(TEXT), default="en")
    ap.add_argument("--out", help="write the report to this file")
    args = ap.parse_args(argv)
    try:
        result = run(args.pairs, args.palette, args.use)
    except (OSError, ValueError) as exc:
        print("contrast: %s" % exc, file=sys.stderr)
        return 2
    if args.json:
        text = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        text = render(result, markdown=args.markdown, lang=args.lang)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print("wrote %s" % args.out)
    else:
        print(text)
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
