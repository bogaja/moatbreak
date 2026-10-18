#!/usr/bin/env python3
"""Client report as one HTML file for the Moatbreak skill. Standard library only.

Puts the teardown's Markdown files into a single self-contained HTML page a
client can open offline, print or forward: the written report
(teardown/report.md) first if there is one, then the market overview with
the positioning map inlined, the product map, how the original is found,
what customers hate, the needs and fixes, the estimate, the battle card
(marked internal) and the legal checklist. A section whose mode did not run
says "not researched" instead of being filled. It adds nothing of its own:
every word comes from the files, links stay links, and there are no
external fonts, scripts, styles or images.

Origin and licence: see NOTICE.md and LICENSE.

    python3 report.py teardown --as-of 2026-10-17 --out teardown/report.html
    python3 report.py teardown --lang de --title "Wettbewerbsanalyse: Kammfux" \\
        --as-of 2026-10-17 --out teardown/report.html

Markdown read: headings, paragraphs, lists (nested, numbered, [ ] and [x]),
tables, code blocks, block quotes, rules, **bold**, `code`, [links](url) and
bare http(s) links. HTML comments are dropped and any other HTML in the files
is shown as text, never run. An SVG with scripts or event handlers is not
inlined.
"""

import argparse
import datetime as _dt
import html
import os
import re
import sys

# key, files, internal; a missing summary is left out, any other missing key
# says "not researched" with the mode that writes it.
SECTIONS = (
    ("summary", ("report.md",), False),
    ("landscape", ("landscape.md", "landscape.svg"), False),
    ("recon", ("recon.md",), False),
    ("visibility", ("visibility.md", "sitemap.md", "seo.md"), False),
    ("feedback", ("feedback.md",), False),
    ("fixes", ("fixes.md",), False),
    ("estimate", ("estimate.md",), False),
    ("battlecard", ("battlecard.md",), True),
    ("legal", ("legal.md",), False),
)

TEXT = {
    "en": {
        "title": "Competitor teardown",
        "as_of": "As of {date}. Built from the files in teardown/; every claim keeps the "
                 "source and date it has there.",
        "internal_note": "The battle card is internal to the client's team: it quotes "
                         "reviewers and is not for publication.",
        "skip": "Skip to the content",
        "toc": "Contents",
        "missing": "not researched",
        "not_researched": "Not researched: {mode} did not run, so there is nothing here. "
                          "It is a possible next step, not a finding.",
        "internal": "Internal: for the client's sales team, not for publication.",
        "svg_refused": "The map {file} was not inlined because it contains scripts or event "
                       "handlers.",
        "table": "Table {n}",
        "footer": "Made with Moatbreak report.py from the Markdown files in teardown/. "
                  "Legal sections are a checklist for a lawyer, not legal advice.",
        "names": {"summary": "Report", "landscape": "Market overview",
                  "recon": "Product map", "visibility": "How it is found",
                  "feedback": "What customers hate and ask for",
                  "fixes": "Needs, fixes and positioning", "estimate": "Scope and effort",
                  "battlecard": "Battle card (internal)",
                  "legal": "Legal checklist (for a lawyer, not legal advice)"},
        "modes": {"landscape": "discover mode", "recon": "recon mode",
                  "visibility": "the visibility add-on", "feedback": "voice of customer mode",
                  "fixes": "voice of customer mode", "estimate": "the recon estimate",
                  "battlecard": "battle card mode", "legal": "the brand and legal check"},
    },
    "de": {
        "title": "Wettbewerbsanalyse",
        "as_of": "Stand {date}. Erstellt aus den Dateien in teardown/; jede Aussage behält "
                 "die Quelle und das Datum, die sie dort hat.",
        "internal_note": "Die Battle Card ist intern für das Team des Kunden: Sie zitiert "
                         "Rezensenten und ist nicht zur Veröffentlichung bestimmt.",
        "skip": "Zum Inhalt springen",
        "toc": "Inhalt",
        "missing": "nicht recherchiert",
        "not_researched": "Nicht recherchiert: {mode} lief nicht, daher steht hier nichts. "
                          "Das ist ein möglicher nächster Schritt, kein Befund.",
        "internal": "Intern: für das Vertriebsteam des Kunden, nicht zur Veröffentlichung.",
        "svg_refused": "Die Karte {file} wurde nicht eingebettet, weil sie Skripte oder "
                       "Event-Handler enthält.",
        "table": "Tabelle {n}",
        "footer": "Erstellt mit Moatbreak report.py aus den Markdown-Dateien in teardown/. "
                  "Rechtliche Abschnitte sind eine Prüfliste für einen Anwalt, keine "
                  "Rechtsberatung.",
        "names": {"summary": "Bericht", "landscape": "Marktüberblick",
                  "recon": "Produktkarte", "visibility": "Wie das Original gefunden wird",
                  "feedback": "Was Kunden stört und was sie sich wünschen",
                  "fixes": "Bedürfnisse, Fixes und Positionierung",
                  "estimate": "Umfang und Aufwand",
                  "battlecard": "Battle Card (intern)",
                  "legal": "Rechtliche Prüfliste (für einen Anwalt, keine Rechtsberatung)"},
        "modes": {"landscape": "Discover", "recon": "Recon",
                  "visibility": "Die Sichtbarkeits-Analyse", "feedback": "Voice of Customer",
                  "fixes": "Voice of Customer", "estimate": "Die Aufwandsschätzung",
                  "battlecard": "Battle Card", "legal": "Die Marken- und Rechtsprüfung"},
    },
}

CSS = """
:root{--ink:#1c1917;--muted:#57534e;--line:#d6d3d1;--bg:#ffffff;--soft:#f5f5f4;
--link:#1d4ed8;--warn:#9a3412;--warn-bg:#fff7ed}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,
"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:62rem;margin:0 auto;padding:1.5rem 1rem 3rem}
a{color:var(--link)}a:focus-visible{outline:3px solid var(--link);outline-offset:2px}
.skip{position:absolute;left:-999px;top:0}.skip:focus{left:1rem;top:1rem;background:var(--bg);
padding:.5rem 1rem;z-index:1}
h1{font-size:2rem;line-height:1.2;margin:.5rem 0}h2{font-size:1.5rem;margin:2.5rem 0 .75rem;
padding-top:1rem;border-top:2px solid var(--line)}h3{font-size:1.2rem;margin:1.75rem 0 .5rem}
h4,h5,h6{font-size:1rem;margin:1.25rem 0 .5rem}
.meta,.note{color:var(--muted)}nav ol{padding-left:1.25rem}
.internal-flag,.missing{background:var(--warn-bg);color:var(--warn);border-left:4px solid
var(--warn);padding:.5rem .75rem}
.scroll{overflow-x:auto;margin:1rem 0}.scroll:focus-visible{outline:3px solid var(--link)}
table{border-collapse:collapse;font-size:.875rem;min-width:100%}
th,td{border:1px solid var(--line);padding:.35rem .5rem;text-align:left;vertical-align:top}
th{background:var(--soft)}
pre{background:var(--soft);padding:.75rem;overflow-x:auto;font-size:.85rem}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.9em}
blockquote{margin:1rem 0;padding:.25rem 1rem;border-left:4px solid var(--line);color:var(--muted)}
figure{margin:1rem 0}svg{max-width:100%;height:auto}
li{margin:.2rem 0}
footer{margin-top:3rem;font-size:.875rem;color:var(--muted)}
@media print{.skip,nav{display:none}h2{break-before:page}a{color:inherit}}
"""

INLINE = re.compile(r"`([^`]+)`|\[([^\]]+)\]\(([^)\s]+)\)|(https?://[^\s<>\[\]\"|]+)|"
                    r"\*\*(.+?)\*\*")
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
UNSAFE_SVG = re.compile(r"<script|\son\w+\s*=|javascript:|<foreignObject", re.I)
SAFE_HREF = re.compile(r"^(https?://|mailto:|#|\.{0,2}/|[\w.-]+(/|$))", re.I)


def esc(text):
    return html.escape(text, quote=True)


def _link(url):
    url = url.rstrip(".,;:!?'")
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1]
    return url


def inline(text):
    """Escape text and turn the inline Markdown into HTML."""
    out, pos = [], 0
    for m in INLINE.finditer(text):
        out.append(esc(text[pos:m.start()]))
        code, label, href, bare, bold = m.groups()
        end = m.end()
        if code is not None:
            out.append("<code>%s</code>" % esc(code))
        elif label is not None:
            if SAFE_HREF.match(href):
                out.append('<a href="%s">%s</a>' % (esc(href), inline(label)))
            else:
                out.append(esc(m.group(0)))
        elif bare is not None:
            url = _link(bare)
            end = m.start() + len(url)
            out.append('<a href="%s">%s</a>' % (esc(url), esc(url)))
        else:
            out.append("<strong>%s</strong>" % inline(bold))
        pos = end
    out.append(esc(text[pos:]))
    return "".join(out).replace("[ ] ", "☐ ").replace("[x] ", "☑ ")


def _cells(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)]


class Doc(object):
    """Markdown blocks to HTML. shift moves headings down: # becomes <h{1+shift}>."""

    def __init__(self, shift, T):
        self.shift, self.T, self.tables = shift, T, 0

    def render(self, text):
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        lines = text.split("\n")
        out, i = [], 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
            elif line.lstrip().startswith("```"):
                j = i + 1
                while j < len(lines) and not lines[j].lstrip().startswith("```"):
                    j += 1
                out.append("<pre><code>%s</code></pre>" % esc("\n".join(lines[i + 1:j])))
                i = j + 1
            elif HEADING.match(line):
                m = HEADING.match(line)
                level = min(len(m.group(1)) + self.shift, 6)
                out.append("<h%d>%s</h%d>" % (level, inline(m.group(2)), level))
                i += 1
            elif re.match(r"^\s*(-{3,}|\*{3,})\s*$", line):
                out.append("<hr>")
                i += 1
            elif line.lstrip().startswith("|") and i + 1 < len(lines) \
                    and SEPARATOR.match(lines[i + 1]):
                j = i + 2
                while j < len(lines) and lines[j].lstrip().startswith("|"):
                    j += 1
                out.append(self.table(lines[i], lines[i + 2:j]))
                i = j
            elif line.startswith(">"):
                j = i
                while j < len(lines) and lines[j].startswith(">"):
                    j += 1
                inner = "\n".join(re.sub(r"^> ?", "", l) for l in lines[i:j])
                out.append("<blockquote>%s</blockquote>" % Doc(self.shift, self.T).render(inner))
                i = j
            elif LIST_ITEM.match(line):
                j = i
                items = []
                while j < len(lines):
                    m = LIST_ITEM.match(lines[j])
                    if m:
                        items.append([len(m.group(1).expandtabs(4)), m.group(2), [m.group(3)]])
                    elif lines[j].strip() and lines[j][:1] in " \t" and items:
                        items[-1][2].append(lines[j].strip())
                    else:
                        break
                    j += 1
                out.append(self.lists(items))
                i = j
            else:
                j = i
                para = []
                while j < len(lines) and lines[j].strip() and not self.starts_block(lines, j):
                    para.append(lines[j].strip())
                    j += 1
                out.append("<p>%s</p>" % "<br>\n".join(inline(p) for p in para))
                i = j
        return "\n".join(out)

    @staticmethod
    def starts_block(lines, j):
        line = lines[j]
        return bool(HEADING.match(line) or LIST_ITEM.match(line) or line.startswith(">")
                    or line.lstrip().startswith("```")
                    or (line.lstrip().startswith("|") and j + 1 < len(lines)
                        and SEPARATOR.match(lines[j + 1])))

    def table(self, head, body):
        self.tables += 1
        out = ['<div class="scroll" role="region" tabindex="0" aria-label="%s">'
               % esc(self.T["table"].format(n=self.tables)), "<table>", "<thead><tr>"]
        out += ['<th scope="col">%s</th>' % inline(c) for c in _cells(head)]
        out.append("</tr></thead><tbody>")
        for row in body:
            out.append("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in _cells(row)))
        out.append("</tbody></table></div>")
        return "\n".join(out)

    @staticmethod
    def lists(items):
        out, stack = [], []
        for indent, marker, text in items:
            tag = "ul" if marker in "-*+" else "ol"
            while stack and indent < stack[-1][0]:
                out.append("</li></%s>" % stack.pop()[1])
            if stack and indent == stack[-1][0] and tag == stack[-1][1]:
                out.append("</li><li>")
            else:
                if stack and indent == stack[-1][0]:
                    out.append("</li></%s>" % stack.pop()[1])
                start = re.match(r"\d+", marker)
                attr = ' start="%s"' % start.group(0) if start and start.group(0) != "1" else ""
                out.append("<%s%s><li>" % (tag, attr))
                stack.append((indent, tag))
            out.append("<br>\n".join(inline(t) for t in text))
        while stack:
            out.append("</li></%s>" % stack.pop()[1])
        return "".join(out)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def build(folder, lang="en", title=None, as_of=None):
    T = TEXT.get(lang, TEXT["en"])
    title = title or T["title"]
    date = as_of.isoformat()
    if lang == "de":
        date = as_of.strftime("%d.%m.%Y")
    present = [(key, [f for f in files if os.path.isfile(os.path.join(folder, f))], internal)
               for key, files, internal in SECTIONS]
    present = [p for p in present if p[1] or p[0] != "summary"]
    nav, body = [], []
    for key, files, internal in present:
        name = T["names"][key]
        sid = "s-" + key
        nav.append('<li><a href="#%s">%s</a>%s</li>' % (
            sid, esc(name), "" if files else " (%s)" % esc(T["missing"])))
        part = ['<section id="%s" aria-labelledby="h-%s">' % (sid, key),
                '<h2 id="h-%s">%s</h2>' % (key, esc(name))]
        if not files:
            part.append('<p class="missing">%s</p>' % esc(
                T["not_researched"].format(mode=T["modes"][key])))
        if internal and files:
            part.append('<p class="internal-flag">%s</p>' % esc(T["internal"]))
        doc = Doc(2, T)
        for f in files:
            path = os.path.join(folder, f)
            if f.endswith(".svg"):
                svg = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", read(path))
                if UNSAFE_SVG.search(svg):
                    part.append('<p class="missing">%s</p>' % esc(T["svg_refused"].format(file=f)))
                else:
                    part.append("<figure>%s</figure>" % svg.strip())
            else:
                part.append(doc.render(read(path)))
        part.append("</section>")
        body.append("\n".join(part))
    has_card = any(k == "battlecard" and f for k, f, _ in present)
    head = ['<!doctype html>', '<html lang="%s">' % lang, "<head>", '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>%s</title>" % esc(title), "<style>%s</style>" % CSS.strip(), "</head>",
            "<body>", '<a class="skip" href="#main">%s</a>' % esc(T["skip"]),
            '<div class="wrap">', "<header>", "<h1>%s</h1>" % esc(title),
            '<p class="meta">%s</p>' % esc(T["as_of"].format(date=date))]
    if has_card:
        head.append('<p class="meta">%s</p>' % esc(T["internal_note"]))
    head += ['<nav aria-label="%s"><h2 class="toc">%s</h2><ol>' % (esc(T["toc"]), esc(T["toc"]))]
    head += nav + ["</ol></nav>", "</header>", '<main id="main">']
    tail = ["</main>", '<footer><p>%s</p></footer>' % esc(T["footer"]), "</div>", "</body>",
            "</html>"]
    return "\n".join(head + body + tail) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("teardown", nargs="?", default="teardown", help="the teardown folder")
    ap.add_argument("--lang", choices=sorted(TEXT), default="en",
                    help="the client's language for headings and notes (default en)")
    ap.add_argument("--title", help="the report's title")
    ap.add_argument("--as-of", metavar="YYYY-MM-DD", help="the report's date (default today)")
    ap.add_argument("--out", help="write the HTML here (default: stdout)")
    args = ap.parse_args(argv)
    try:
        as_of = (_dt.datetime.strptime(args.as_of, "%Y-%m-%d").date() if args.as_of
                 else _dt.date.today())
    except ValueError:
        print("report: --as-of must be YYYY-MM-DD", file=sys.stderr)
        return 2
    if not os.path.isdir(args.teardown):
        print("report: %s is not a folder" % args.teardown, file=sys.stderr)
        return 2
    try:
        text = build(args.teardown, args.lang, args.title, as_of)
    except (OSError, UnicodeDecodeError) as exc:
        print("report: %s" % exc, file=sys.stderr)
        return 2
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
