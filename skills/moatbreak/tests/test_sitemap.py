import datetime as dt
import gzip
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from _load import load

sitemap = load("sitemap")

URLSET = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url><loc>https://ex.com/</loc><lastmod>2026-10-01</lastmod>
    <xhtml:link rel="alternate" hreflang="de-DE" href="https://ex.com/de/"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://ex.com/"/></url>
  <url><loc>https://ex.com/de/</loc><lastmod>2026-10-01</lastmod>
    <xhtml:link rel="alternate" hreflang="de-DE" href="https://ex.com/de/"/></url>
  <url><loc>https://ex.com/blog</loc><lastmod>2026-09-20T10:00:00+02:00</lastmod></url>
  <url><loc>https://ex.com/blog/how-to-book</loc><lastmod>2026-09-20</lastmod></url>
  <url><loc>https://ex.com/de/blog/termine-planen</loc><lastmod>2025-01-05</lastmod></url>
  <url><loc>https://ex.com/blog/calendly-vs-acuity</loc></url>
  <url><loc>https://ex.com/collections/shoes</loc></url>
  <url><loc>https://ex.com/collections/shoes/products/red-sneaker</loc></url>
  <url><loc>https://ex.com/de-at/preise</loc></url>
  <url><loc>https://ex.com/pricing</loc></url>
  <url><loc>https://ex.com/hilfe/konto-loeschen</loc></url>
  <url><loc>https://ex.com/impressum.html</loc></url>
  <url><loc>https://ex.com/integrations/zoom</loc></url>
  <url><loc>https://ex.com/%C3%BCber-uns</loc></url>
  <url><loc>https://ex.com/alternative-energie</loc></url>
  <url><loc>https://ex.com/pricing#plans</loc></url>
</urlset>
"""

INDEX = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://ex.com/sitemap-pages.xml</loc><lastmod>2026-10-01</lastmod></sitemap>
  <sitemap><loc>https://ex.com/sitemap_products_1.xml?from=1&amp;to=99</loc></sitemap>
</sitemapindex>
"""


def put(root, name, data):
    path = os.path.join(root, name)
    with open(path, "wb") as fh:
        fh.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    return path


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = sitemap.main(argv)
    return code, out.getvalue(), err.getvalue()


class Classify(unittest.TestCase):
    def test_types_by_address(self):
        c = lambda path: sitemap.classify(sitemap.split_path(path)[1])
        self.assertEqual(c("/"), "home")
        self.assertEqual(c("/de/"), "home")
        self.assertEqual(c("/blog/calendly-vs-acuity"), "comparison")
        self.assertEqual(c("/calendly-alternative"), "comparison")
        self.assertEqual(c("/alternativen-zu-calendly"), "comparison")
        self.assertEqual(c("/alternative-energie"), "other")
        self.assertEqual(c("/collections/shoes/products/red"), "product")
        self.assertEqual(c("/collections/shoes"), "category")
        self.assertEqual(c("/hc/de/articles/123-konto"), "help")
        self.assertEqual(c("/blog/pricing-strategy"), "blog")
        self.assertEqual(c("/impressum.html"), "legal")
        self.assertEqual(c("/%C3%BCber-uns"), "company")
        self.assertEqual(c("/damen/schuhe/sneaker-123"), "other")

    def test_market_folders(self):
        self.assertEqual(sitemap.split_path("/de/blog/x")[0], "de")
        self.assertEqual(sitemap.split_path("/en_US/x")[0], "en-us")
        self.assertEqual(sitemap.split_path("/ch-de/x")[0], "ch-de")
        self.assertEqual(sitemap.split_path("/at/x")[0], "at")
        self.assertIsNone(sitemap.split_path("/go/x")[0])
        self.assertIsNone(sitemap.split_path("/c/damen")[0])


class Analyse(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def result(self, *files, **kw):
        parsed = []
        for p in files:
            kind, urls, kids = sitemap.parse(sitemap.read_bytes(p), p)
            parsed.append((p, kind, urls, kids))
        return sitemap.analyse(parsed, **kw)

    def test_counts_types_folders_hreflang_and_duplicates(self):
        r = self.result(put(self.root, "sitemap-pages.xml", URLSET))
        self.assertEqual(r["pages"], 15)
        self.assertEqual(r["duplicates"], 1)      # /pricing#plans
        types = dict((t["type"], t["pages"]) for t in r["types"])
        self.assertEqual(types["home"], 2)
        self.assertEqual(types["blog"], 3)
        self.assertEqual(types["comparison"], 1)
        self.assertEqual(types["pricing"], 2)     # /pricing and /de-at/preise
        self.assertEqual(types["product"], 1)
        self.assertEqual(types["category"], 1)
        self.assertEqual(types["other"], 1)
        self.assertEqual(dict(r["folders"]), {"de": 2, "de-at": 1})
        self.assertEqual(dict(r["hreflang"]), {"de-de": 2, "x-default": 1})
        sections = dict((s["section"], s["pages"]) for s in r["sections"])
        self.assertEqual(sections["/blog/"], 4)   # the /blog index joins its folder
        self.assertEqual(sections["/collections/"], 2)
        self.assertNotIn("recent", r["types"][0])

    def test_as_of_counts_recent_changes(self):
        r = self.result(put(self.root, "s.xml", URLSET), as_of=dt.date(2026, 10, 17))
        blog = [t for t in r["types"] if t["type"] == "blog"][0]
        self.assertEqual(blog["recent"], 2)       # 2025-01-05 is too old
        self.assertEqual(blog["newest"], "2026-09-20")

    def test_index_marks_given_children_and_gzip_works(self):
        gz = put(self.root, "sitemap-pages.xml.gz", gzip.compress(URLSET.encode("utf-8")))
        r = self.result(put(self.root, "sitemap.xml", INDEX), gz)
        self.assertEqual(r["pages"], 15)
        given = dict((c["loc"].split("/")[-1], c["given"]) for c in r["index"])
        self.assertEqual(given, {"sitemap-pages.xml": True,
                                 "sitemap_products_1.xml?from=1&to=99": False})
        text = sitemap.render(r)
        self.assertIn("Counts are partial: 1 of 2", text)

    def test_index_file_and_shared_child_names_are_not_given(self):
        index = ("<sitemapindex xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"
                 "<sitemap><loc>https://x.com/de/sitemap.xml</loc></sitemap>"
                 "<sitemap><loc>https://x.com/en/sitemap.xml</loc></sitemap></sitemapindex>")
        child = ("<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"
                 "<url><loc>https://x.com/de/</loc></url></urlset>")
        r = self.result(put(self.root, "sitemap.xml", index),
                        put(self.root, "de-sitemap.xml", child))
        self.assertEqual([c["given"] for c in r["index"]], [False, False])
        text = sitemap.render(r)
        self.assertIn("Counts are partial: 0 of 2", text)
        self.assertIn("2 child sitemaps share a file name (sitemap.xml)", text)
        os.mkdir(os.path.join(self.root, "de"))
        r = self.result(put(self.root, "sitemap.xml", index),
                        put(os.path.join(self.root, "de"), "sitemap.xml", child))
        self.assertEqual([c["given"] for c in r["index"]], [True, False])
        self.assertIn("Counts are partial: 1 of 2", sitemap.render(r))

    def test_bom_and_corrupt_gzip(self):
        r = self.result(put(self.root, "urls.txt", "\ufeffhttps://ex.com/a\nhttps://ex.com/b\n"))
        self.assertEqual(r["pages"], 2)
        bad = gzip.compress(URLSET.encode("utf-8"))
        bad = bad[:10] + b"\x00" * 20 + bad[30:]
        with self.assertRaises(sitemap.SitemapError):
            sitemap.read_bytes(put(self.root, "bad.xml.gz", bad))

    def test_text_sitemap_and_stamped_lastmod(self):
        lines = "\n".join("https://ex.com/blog/post-%d" % i for i in range(12))
        r = self.result(put(self.root, "urls.txt", "# saved by hand\n" + lines + "\n"))
        self.assertEqual(r["pages"], 12)
        self.assertFalse(r["lastmod"]["stamped"])
        stamped = ("<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"
                   + "".join("<url><loc>https://ex.com/p/%d</loc><lastmod>2026-10-16"
                             "</lastmod></url>" % i for i in range(12)) + "</urlset>")
        r = self.result(put(self.root, "stamped.xml", stamped))
        self.assertTrue(r["lastmod"]["stamped"])
        self.assertIn("stamps its build date", sitemap.render(r))

    def test_refuses_doctype_and_bad_xml(self):
        bomb = ('<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa">]>'
                '<urlset><url><loc>&a;</loc></url></urlset>')
        with self.assertRaises(sitemap.SitemapError):
            sitemap.parse(bomb.encode("utf-8"))
        with self.assertRaises(sitemap.SitemapError):
            sitemap.parse(b"<urlset><url><loc>x</url>")
        with self.assertRaises(sitemap.SitemapError):
            sitemap.parse(b"<rss><channel/></rss>")


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.xml = put(self.root, "sitemap.xml", URLSET)

    def tearDown(self):
        self.tmp.cleanup()

    def test_german_report_to_file(self):
        out = os.path.join(self.root, "sitemap.md")
        code, stdout, _ = run([self.xml, "--lang", "de", "--as-of", "2026-10-17",
                               "--out", out])
        self.assertEqual(code, 0)
        with open(out, encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("## Seitentypen", text)
        self.assertIn("geändert in den 90 Tagen bis 2026-10-17", text)
        self.assertIn("/über-uns", text)
        self.assertIn("Doppelte Adressen entfernt: 1.", text)
        self.assertIn("| Vergleich | 1 |", text)
        self.assertIn("/blog/calendly-vs-acuity", text)
        self.assertNotIn("https://ex.com/blog/calendly", text)   # one host: paths only

    def test_json_and_errors(self):
        code, stdout, _ = run([self.xml, "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout)["pages"], 15)
        code, _, err = run([put(self.root, "empty.txt", "nothing here\n")])
        self.assertEqual(code, 2)
        self.assertIn("no addresses", err)
        code, _, err = run([self.xml, "--as-of", "17.10.2026"])
        self.assertEqual(code, 2)

    def test_index_only(self):
        code, stdout, _ = run([put(self.root, "index.xml", INDEX)])
        self.assertEqual(code, 0)
        self.assertIn("Only a sitemap index was given", stdout)


if __name__ == "__main__":
    unittest.main()
