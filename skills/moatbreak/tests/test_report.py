import io
import os
import re
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from html.parser import HTMLParser

from _load import load

report = load("report")

VOID = {"meta", "br", "hr", "circle", "line", "rect", "polygon"}


class Nesting(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errors.append(tag)


def put(root, name, text):
    with open(os.path.join(root, name), "w", encoding="utf-8") as fh:
        fh.write(text)


def md(text):
    return report.Doc(2, report.TEXT["en"]).render(text)


class Markdown(unittest.TestCase):
    def test_blocks(self):
        out = md("# Title\n\nLine one\nline two\n\n| a | b \\| c |\n| --- | --- |\n| 1 | **2** |\n"
                 "\n```\n<b>code</b>\n```\n\n> quoted\n\n---\n")
        self.assertIn("<h3>Title</h3>", out)
        self.assertIn("<p>Line one<br>\nline two</p>", out)
        self.assertIn('<th scope="col">b | c</th>', out)
        self.assertIn("<td><strong>2</strong></td>", out)
        self.assertIn("<pre><code>&lt;b&gt;code&lt;/b&gt;</code></pre>", out)
        self.assertIn("<blockquote><p>quoted</p></blockquote>", out)
        self.assertIn("<hr>", out)

    def test_nested_lists_continuations_and_boxes(self):
        out = md("1. **Weak**\n   - \"quote\" (g2, 1*) https://x.example.com/r/1.\n"
                 "   Data: line 3\n2. Next\n\n- [ ] to check: thing\n- [x] done\n")
        self.assertEqual(out.count("<ol>"), 1)
        self.assertIn('<ul><li>&quot;quote&quot; (g2, 1*) <a href="https://x.example.com/r/1">'
                      'https://x.example.com/r/1</a>.<br>\nData: line 3</li></ul></li><li>Next',
                      out)
        self.assertIn("<li>☐ to check: thing</li><li>☑ done</li>", out)

    def test_html_is_text_and_unsafe_links_stay_text(self):
        out = md("<script>alert(1)</script> [x](javascript:alert(1)) [ok](https://a.example.com/)"
                 " <!-- hidden -->\n")
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)
        self.assertNotIn('href="javascript', out)
        self.assertIn('<a href="https://a.example.com/">ok</a>', out)
        self.assertNotIn("hidden", out)

    def test_bare_link_keeps_its_closing_bracket_outside(self):
        out = md("(see https://a.example.com/x)\n")
        self.assertIn('(see <a href="https://a.example.com/x">https://a.example.com/x</a>)', out)


class Build(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        put(self.root, "feedback.md", "# X: what customers hate\n\n- \"Too slow.\" (g2, 1*) "
                                      "https://x.example.com/1\n")
        put(self.root, "battlecard.md", "# Battle card: Y vs X\n\nInternal.\n")
        put(self.root, "landscape.svg", '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/'
                                        '2000/svg" role="img"><title>Map</title></svg>\n')

    def tearDown(self):
        self.tmp.cleanup()

    def build(self, **kw):
        import datetime
        return report.build(self.root, as_of=datetime.date(2026, 10, 17), **kw)

    def test_sections_present_missing_and_internal(self):
        page = self.build()
        p = Nesting()
        p.feed(page)
        self.assertEqual((p.stack, p.errors), ([], []))
        self.assertTrue(page.startswith('<!doctype html>\n<html lang="en">'))
        self.assertIn("As of 2026-10-17.", page)
        self.assertIn("Not researched: recon mode did not run", page)
        self.assertIn('<p class="internal-flag">Internal: for the client&#x27;s sales team', page)
        self.assertIn('<figure><svg xmlns="http://www.w3.org/2000/svg" role="img">', page)
        self.assertNotIn("<?xml", page)
        self.assertNotIn('id="s-summary"', page)          # no report.md, no summary section
        self.assertIn('<a class="skip" href="#main">', page)
        self.assertEqual(re.findall(r"<(?:link|script)\b|src=", page), [])   # nothing external

    def test_report_md_comes_first_and_german(self):
        put(self.root, "report.md", "# Bericht\n\nZusammenfassung.\n")
        page = self.build(lang="de", title="Analyse")
        self.assertLess(page.index('id="s-summary"'), page.index('id="s-landscape"'))
        self.assertIn('<html lang="de">', page)
        self.assertIn("Stand 17.10.2026.", page)
        self.assertIn("(nicht recherchiert)", page)
        self.assertIn("<title>Analyse</title>", page)

    def test_svg_with_script_is_not_inlined(self):
        put(self.root, "landscape.svg", '<svg onload="x()"><script>x()</script></svg>')
        page = self.build()
        self.assertNotIn("onload", page)
        self.assertIn("was not inlined", page)

    def test_cli(self):
        out = os.path.join(self.root, "report.html")
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(report.main([self.root, "--as-of", "2026-10-17", "--out", out]), 0)
        with open(out, encoding="utf-8") as fh:
            first = fh.read()
        with redirect_stdout(io.StringIO()):
            report.main([self.root, "--as-of", "2026-10-17", "--out", out])
        with open(out, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), first)              # deterministic
        with redirect_stderr(io.StringIO()):
            self.assertEqual(report.main([os.path.join(self.root, "nope")]), 2)
            self.assertEqual(report.main([self.root, "--as-of", "17.10.2026"]), 2)


if __name__ == "__main__":
    unittest.main()
