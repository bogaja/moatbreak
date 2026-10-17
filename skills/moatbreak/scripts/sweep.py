#!/usr/bin/env python3
"""Distance sweep for the Moatbreak skill (brand mode). Standard library only.

Searches the new product's codebase for anything that still belongs to the
original: its name, its domains, its brand colours, and colours so close to
them that the overall impression stays the same. Run it before every launch.
It exits 1 on exact hits, so it can block a deploy.

Origin and licence: see NOTICE.md and LICENSE.

    python3 sweep.py . --avoid "Calendly"
    python3 sweep.py . --avoid "Müller Shop,Mueller GmbH" --domains mueller-shop.de \\
        --colors "#006bff,#0ae8f0" --near 12
    python3 sweep.py . --config teardown/brand.json --json

--config reads {"avoid": [...], "domains": [...], "colors": [...], "near": 12,
"allow": [...]}.

--allow takes file patterns (LICENSE, NOTICE.md, docs/compare-*.md) where the
original's name is there on purpose: a licence attribution, or a comparison
page a lawyer has reviewed. Hits there are counted as allowed and never fail
the run. Keep the list short; every entry is a decision, not a convenience.

Names match case-insensitively anywhere, including inside identifiers
(CalendlyButton, calendly_sync), with or without spaces, hyphens and
underscores, and in German spelling variants (Müller, Mueller, Muller;
Straße, Strasse). Colours match as #rgb, #rrggbb, #rrggbbaa, rgb() and rgba().

Near colours: any colour within --near (CIE76 Delta E, default 10, 0 turns it
off) of an avoided brand colour is reported as a warning. Around 2 is the
smallest difference most people see; below 10 reads as "the same colour" at a
glance. Warnings do not fail the run unless you pass --strict.

Skipped: .git, node_modules, build output, lock files, binary files, and the
teardown/ planning folder, where the original's name belongs. Pass
--include-planning to check it too.
"""

import argparse
import fnmatch
import json
import math
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", ".next", ".nuxt", ".svelte-kit", "dist", "build",
             "out", ".vercel", ".turbo", ".cache", "coverage", "__pycache__", ".venv",
             "venv", "Pods", ".expo", "DerivedData", ".gradle", "vendor"}
PLANNING_DIRS = {"teardown"}
SKIP_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
              "Podfile.lock", "Cargo.lock", "poetry.lock", "composer.lock"}
BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".icns", ".pdf", ".zip",
              ".gz", ".woff", ".woff2", ".ttf", ".otf", ".eot", ".mp4", ".mov", ".mp3",
              ".wav", ".avif", ".heic", ".psd", ".sketch", ".fig", ".jar", ".so", ".dylib"}
HEX = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})(?![0-9a-zA-Z])")
RGB = re.compile(r"rgba?\(\s*(\d{1,3})\s*[, ]\s*(\d{1,3})\s*[, ]\s*(\d{1,3})")
TRANSLIT = (("ä", "(?:ä|ae|a)"), ("ö", "(?:ö|oe|o)"), ("ü", "(?:ü|ue|u)"), ("ß", "(?:ß|ss)"))


def norm_hex(h):
    h = h.lower().lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h[:3])
    return "#" + h[:6]


def hex_to_rgb(h):
    h = norm_hex(h)
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c))) for c in rgb)


def _lab(rgb):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 1.00000
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3.0) if t > 0.008856 else 7.787 * t + 16 / 116.0
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a, b):
    """CIE76 colour difference between two RGB tuples."""
    la, lb = _lab(a), _lab(b)
    return math.sqrt(sum((p - q) ** 2 for p, q in zip(la, lb)))


def _word_regex(word):
    """German spelling variants: Müller = Mueller = Muller, Straße = Strasse."""
    umlaut = dict(TRANSLIT)
    digraph = {"ae": "(?:ae|ä)", "oe": "(?:oe|ö)", "ue": "(?:ue|ü)", "ss": "(?:ss|ß)"}
    w, i, rx = word.lower(), 0, ""
    while i < len(w):
        if w[i:i + 2] in digraph:
            rx += digraph[w[i:i + 2]]
            i += 2
        else:
            rx += umlaut.get(w[i], re.escape(w[i]))
            i += 1
    return rx


def _name_regex(name):
    parts = [_word_regex(p) for p in re.split(r"[\s_.-]+", name.strip()) if p]
    return re.compile(r"[\s_.-]?".join(parts), re.I)


def build_patterns(avoid, domains):
    pats = []
    for name in avoid:
        name = name.strip()
        if name:
            pats.append(("name", name, _name_regex(name)))
    for d in domains:
        d = d.strip().lower()
        if d:
            pats.append(("domain", d, re.compile(re.escape(d), re.I)))
    return pats


def is_binary(path):
    if os.path.splitext(path)[1].lower() in BINARY_EXT:
        return True
    try:
        with open(path, "rb") as fh:
            return b"\0" in fh.read(4096)
    except OSError:
        return True


def colours_in(line):
    for m in HEX.finditer(line):
        yield m.group(0), hex_to_rgb(m.group(0))
    for m in RGB.finditer(line):
        rgb = tuple(int(x) for x in m.groups())
        if all(0 <= c <= 255 for c in rgb):
            yield m.group(0) + ")", rgb


def is_allowed(rel, allow):
    rel = rel.replace(os.sep, "/").rstrip("/")
    return any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(os.path.basename(rel), p)
               for p in allow)


def sweep(root, avoid=(), domains=(), colors=(), include_planning=False, near=10.0,
          max_size=2_000_000, allow=()):
    pats = build_patterns(avoid, domains)
    targets = {}
    for c in colors:
        c = c.strip()
        if HEX.fullmatch(c):
            targets[norm_hex(c)] = hex_to_rgb(c)
    hits = []
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        keep = []
        for d in dirnames:
            if d in SKIP_DIRS:
                continue
            if d in PLANNING_DIRS and rel_dir == "." and not include_planning:
                continue
            keep.append(d)
        dirnames[:] = sorted(keep)
        for d in dirnames:
            for kind, label, rx in pats:
                if kind == "name" and rx.search(d):
                    hits.append({"file": os.path.normpath(os.path.join(rel_dir, d)) + "/",
                                 "line": 0, "kind": "path", "match": label,
                                 "text": "folder name"})
        for fn in sorted(filenames):
            if fn in SKIP_FILES:
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.normpath(os.path.join(rel_dir, fn))
            for kind, label, rx in pats:
                if kind == "name" and rx.search(fn):
                    hits.append({"file": rel, "line": 0, "kind": "path", "match": label,
                                 "text": "file name"})
            try:
                if os.path.getsize(path) > max_size or is_binary(path):
                    continue
                with open(path, encoding="utf-8", errors="replace") as fh:
                    lines = fh.readlines()
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                for kind, label, rx in pats:
                    if rx.search(line):
                        hits.append({"file": rel, "line": i, "kind": kind, "match": label,
                                     "text": line.strip()[:160]})
                if not targets:
                    continue
                for raw, rgb in colours_in(line):
                    hx = rgb_to_hex(rgb)
                    if hx in targets:
                        hits.append({"file": rel, "line": i, "kind": "color", "match": hx,
                                     "text": line.strip()[:160]})
                    elif near > 0:
                        best = min(targets.items(), key=lambda kv: delta_e(rgb, kv[1]))
                        de = delta_e(rgb, best[1])
                        if de < near:
                            hits.append({"file": rel, "line": i, "kind": "near-color",
                                         "match": "%s~%s" % (hx, best[0]),
                                         "delta_e": round(de, 1),
                                         "text": line.strip()[:160]})
    if allow:
        for h in hits:
            if is_allowed(h["file"], allow):
                h["allowed"] = True
    return hits


def blocking(hits, strict=False):
    return [h for h in hits if not h.get("allowed")
            and (strict or h["kind"] != "near-color")]


def render(hits, strict=False):
    allowed = [h for h in hits if h.get("allowed")]
    hits = [h for h in hits if not h.get("allowed")]
    note = ("\n%d allowed hits in allow-listed files, not counted." % len(allowed)
            if allowed else "")
    if not hits:
        return "Clean. Nothing of the original's name, domain or colours found." + note
    out = []
    by_kind = {}
    for h in hits:
        by_kind[h["kind"]] = by_kind.get(h["kind"], 0) + 1
        loc = h["file"] if not h["line"] else "%s:%d" % (h["file"], h["line"])
        extra = (" (dE %.1f)" % h["delta_e"]) if "delta_e" in h else ""
        out.append("%-10s %-18s %s%s  %s" % (h["kind"], h["match"][:18], loc, extra, h["text"]))
    out.append("")
    summary = ", ".join("%s %d" % kv for kv in sorted(by_kind.items()))
    if blocking(hits, strict):
        out.append("%d hits (%s). Replace every exact hit before you launch." % (len(hits), summary))
    else:
        out.append("No exact hits. %d near-colour warnings (%s): check the overall "
                   "impression by eye, or pass --strict to block on them." % (len(hits), summary))
    return "\n".join(out) + note


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--avoid", default="", help="comma-separated names")
    ap.add_argument("--domains", default="", help="comma-separated domains")
    ap.add_argument("--colors", default="", help="comma-separated hex colours")
    ap.add_argument("--near", type=float, help="Delta E threshold for near colours (default 10)")
    ap.add_argument("--strict", action="store_true", help="near colours fail the run too")
    ap.add_argument("--config", help="JSON with avoid / domains / colors lists")
    ap.add_argument("--include-planning", action="store_true")
    ap.add_argument("--allow", default="",
                    help="comma-separated file patterns where the name is there on purpose")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    avoid = [x for x in args.avoid.split(",") if x.strip()]
    domains = [x for x in args.domains.split(",") if x.strip()]
    colors = [x for x in args.colors.split(",") if x.strip()]
    allow = [x.strip() for x in args.allow.split(",") if x.strip()]
    near = args.near
    if args.config:
        try:
            with open(args.config, encoding="utf-8") as fh:
                cfg = json.load(fh)
        except (OSError, ValueError) as exc:
            print("sweep: %s" % exc, file=sys.stderr)
            return 2
        avoid += cfg.get("avoid", [])
        domains += cfg.get("domains", [])
        colors += cfg.get("colors", [])
        allow += cfg.get("allow", [])
        if near is None and "near" in cfg:
            near = float(cfg["near"])
    if near is None:
        near = 10.0
    if not (avoid or domains or colors):
        print("sweep: nothing to look for. Pass --avoid with the original's name.",
              file=sys.stderr)
        return 2
    hits = sweep(args.root, avoid, domains, colors, args.include_planning, near, allow=allow)
    print(json.dumps(hits, indent=2, ensure_ascii=False) if args.json
          else render(hits, args.strict))
    return 1 if blocking(hits, args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
