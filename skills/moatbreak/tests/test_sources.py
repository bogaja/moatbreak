import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from _load import load

sources = load("sources")

AS_OF = "2026-10-17"


def put(root, rel, data=b"x"):
    path = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    return path


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = sources.main(argv)
    return code, out.getvalue(), err.getvalue()


class Sources(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.tmp.name, "teardown")
        put(self.root, "screens/S01-home-1440.png")
        put(self.root, "screens/S01-home-390.png")
        put(self.root, "proof/2026-10-17-pricing.pdf")
        put(self.root, "screens/.DS_Store")

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self, text):
        put(self.root, "sources.csv", "file,url,read_on,notes\n" + text)

    def test_complete_manifest_passes(self):
        self.manifest("screens/S01-home-1440.png,https://x.example.com/,2026-10-17,1440x900\n"
                      "teardown/screens/S01-home-390.png,https://x.example.com/,2026-10-17,\n"
                      "proof/2026-10-17-pricing.pdf,https://x.example.com/preise,2026-10-17,\n")
        code, out, _ = run([self.root, "--as-of", AS_OF])
        self.assertEqual(code, 0)
        self.assertIn("3 files in screens/, proof/; 3 rows in sources.csv.", out)
        self.assertIn("Every file has its URL and date.", out)

    def test_every_gap_in_the_paper_trail_fails(self):
        self.manifest("screens/S01-home-1440.png,,2026-10-17,\n"
                      "proof/2026-10-17-pricing.pdf,https://x.example.com/preise,17.10.2026,\n"
                      "screens/S02.png,https://x.example.com/b,2026-10-01,\n"
                      "screens/S01-home-1440.png,https://x.example.com/,2026-10-17,\n")
        code, out, _ = run([self.root, "--as-of", AS_OF, "--json"])
        self.assertEqual(code, 1)
        kinds = [(p["kind"], p["file"]) for p in json.loads(out)["problems"]]
        self.assertEqual(kinds, [("untracked", "screens/S01-home-390.png"),
                                 ("no_url", "screens/S01-home-1440.png"),
                                 ("no_date", "proof/2026-10-17-pricing.pdf"),
                                 ("gone", "screens/S02.png"),
                                 ("twice", "screens/S01-home-1440.png")])

    def test_future_and_old_dates(self):
        self.manifest("screens/S01-home-1440.png,https://x.example.com/,2026-10-18,\n"
                      "screens/S01-home-390.png,https://x.example.com/,2026-05-01,\n"
                      "proof/2026-10-17-pricing.pdf,https://x.example.com/preise,2026-10-17,\n")
        code, out, _ = run([self.root, "--as-of", AS_OF, "--lang", "de"])
        self.assertEqual(code, 1)
        self.assertIn("Zeile 2: screens/S01-home-1440.png wurde am 2026-10-18 gelesen, "
                      "nach dem 17.10.2026", out)
        self.assertIn("## Mehr als 90 Tage vor dem 17.10.2026 gelesen", out)
        self.assertIn("- screens/S01-home-390.png (2026-05-01)", out)

    def test_no_manifest_lists_every_file(self):
        out_file = os.path.join(self.tmp.name, "sources.md")
        code, stdout, _ = run([self.root, "--as-of", AS_OF, "--out", out_file])
        self.assertEqual((code, stdout), (1, "wrote %s\n" % out_file))
        with open(out_file, encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("No sources.csv", text)
        self.assertEqual(text.count("no row in sources.csv"), 3)

    def test_nothing_to_check_and_errors(self):
        empty = os.path.join(self.tmp.name, "empty")
        os.mkdir(empty)
        code, out, _ = run([empty, "--as-of", AS_OF])
        self.assertEqual(code, 0)
        self.assertIn("nothing to check", out)
        self.assertEqual(run([os.path.join(self.tmp.name, "nope")])[0], 2)
        self.assertEqual(run([self.root, "--as-of", "17.10.2026"])[0], 2)
        put(self.root, "sources.csv", "file,link\nx,y\n")
        code, _, err = run([self.root, "--as-of", AS_OF])
        self.assertEqual(code, 2)
        self.assertIn("no 'url' column", err)


class ReconSources(unittest.TestCase):
    EN = "## Sources\n\n| # | source | URL | read on | notes |\n| --- | --- | --- | --- | --- |\n"
    DE = ("## Quellen\n\n| # | Quelle | URL | gelesen am | Notizen |\n"
          "| --- | --- | --- | --- | --- |\n")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.tmp.name, "teardown")
        os.mkdir(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def recon(self, table, rows):
        # the table rows start on line 7
        put(self.root, "recon.md", "# Recon: X\n\n" + table + rows +
            "\n## Messaging\n\n| product | URL | read on |\n| --- | --- | --- |\n| X | | |\n")

    def kinds(self, argv=()):
        code, out, _ = run([self.root, "--as-of", AS_OF, "--json"] + list(argv))
        return code, [(p["kind"], p.get("line")) for p in json.loads(out)["problems"]]

    def test_good_table_passes_and_lists_old_rows(self):
        self.recon(self.EN.replace("\n\n", "\n\n<!-- one page per row -->\n\n", 1),
                   "| 1 | help center | https://x.example.com/hilfe | 2026-10-17 | |\n"
                   "| 2 | pricing | [Preise](https://x.example.com/preise) | 2026-10-01 | |\n"
                   "| 3 | changelog | <https://x.example.com/changelog> | 2026-05-01 | |\n"
                   "| 4 | wiki | [Kamm](https://x.example.com/w/Kamm_(Werkzeug)) | 2026-10-17 | |\n"
                   '| 5 | help | [Hilfe](https://x.example.com/a "Hilfe") | 2026-10-17 | |\n')
        code, out, _ = run([self.root, "--as-of", AS_OF])
        self.assertEqual(code, 0)
        self.assertIn("0 files in screens/, proof/; 0 rows in sources.csv; 5 rows in the "
                      "sources table of recon.md. As of 2026-10-17.", out)
        self.assertIn("Every file and every row of the sources table in recon.md has its URL "
                      "and date.", out)
        self.assertNotIn("No sources.csv", out)
        self.assertIn("- recon.md:11 (2026-05-01) https://x.example.com/changelog", out)

    def test_rows_without_one_page_url_fail(self):
        self.recon(self.EN,
                   "| 1 | help center | | 2026-10-17 | |\n"
                   '| 2 | Websuche Nische | Suche "nachhaltige Arbeitskleidung" | 2026-10-17 | |\n'
                   "| 3 | robots.txt, sitemap | siehe `visibility.md` | 2026-10-17 | |\n"
                   "| 4 | help | https://x.example.com/a, https://x.example.com/b | 2026-10-17 | |\n"
                   "| 5 | help | https://x.example.com/a (and the pages next to it) | 2026-10-17 | |\n"
                   "| 6 | pricing | https://x.example.com/preise | 2026-10-18 | |\n"
                   "| 7 | pricing | https://x.example.com/preise | 17.10.2026 | |\n"
                   "| 8 | help | https://x.example.com/a,https://x.example.com/b | 2026-10-17 | |\n"
                   "| 9 | help | https://x.example.com/a;https://x.example.com/b | 2026-10-17 | |\n")
        self.assertEqual(self.kinds(), (1, [
            ("recon_url", 7), ("recon_url", 8), ("recon_url", 9), ("recon_urls", 10),
            ("recon_url", 11), ("recon_future", 12), ("recon_no_date", 13),
            ("recon_urls", 14), ("recon_urls", 15)]))
        code, out, _ = run([self.root, "--as-of", AS_OF])
        self.assertIn("- recon.md line 8: 'Suche \"nachhaltige Arbeitskleidung\"' is not one "
                      "page URL. Give every page you read its own row with its own URL: for a "
                      "web search, the result pages you read; for another file, copy its URLs "
                      "here", out)
        self.assertIn("- recon.md line 10: 2 URLs in one row.", out)
        self.assertIn("- recon.md line 12: read on 2026-10-18, after 2026-10-17", out)

    def test_german_headings(self):
        self.recon(self.DE, "| 1 | Hilfe | https://x.example.com/hilfe | 2026-10-02 | |\n"
                            "| 2 | robots.txt | siehe visibility.md | 2026-10-02 | |\n")
        code, out, _ = run([self.root, "--as-of", AS_OF, "--lang", "de"])
        self.assertEqual(code, 1)
        self.assertIn("; 2 Zeilen in der Quellentabelle von recon.md. Stand 17.10.2026.", out)
        self.assertIn("- recon.md Zeile 8: 'siehe visibility.md' ist nicht genau eine "
                      "Seiten-URL.", out)
        self.assertIn("bei einer anderen Datei deren URLs hierher kopieren", out)

    def test_rows_are_read_as_github_renders_them(self):
        # outer pipes are optional and "\|" stays inside its cell
        put(self.root, "recon.md", "# Recon: X\n\n## Sources\n\n"
            "n | source | URL | read on | notes\n--- | --- | --- | --- | ---\n"
            "1 | help | https://x.example.com/a | 2026-10-17 |\n"
            "| 2 | Hilfe \\| FAQ | https://x.example.com/b | 2026-10-17 | |\n"
            "||help|https://x.example.com/c|2026-10-17||\n"
            "3 | robots | siehe visibility.md | 2026-10-17\n"
            "| 4 | a \\| https://x.example.com/d | siehe visibility.md | 2026-10-17 | |\n")
        self.assertEqual(self.kinds(), (1, [("recon_url", 10), ("recon_url", 11)]))
        code, out, _ = run([self.root, "--as-of", AS_OF])
        self.assertIn("- recon.md line 11: 'siehe visibility.md' is not one page URL.", out)
        self.assertIn("5 rows in the sources table of recon.md", out)

    def test_search_result_pages_fail(self):
        self.recon(self.EN,
                   "| 1 | search | https://www.google.com/search?q=kleidung | 2026-10-17 | |\n"
                   "| 2 | search | <https://duckduckgo.com/?q=kammfux+friseur> | 2026-10-17 | |\n"
                   "| 3 | site search | https://x.example.com/search?q=kamm | 2026-10-17 | |\n")
        self.assertEqual(self.kinds(), (1, [("recon_search", 7), ("recon_search", 8)]))
        code, out, _ = run([self.root, "--as-of", AS_OF, "--lang", "de"])
        self.assertIn("- recon.md Zeile 7: 'https://www.google.com/search?q=kleidung' ist "
                      "eine Suchergebnisseite, keine Quelle.", out)

    def test_code_blocks_and_every_table_under_the_heading(self):
        put(self.root, "recon.md", "# Recon: X\n\n## Quellen\n\n"
            "```\n# robots.txt\nDisallow: /\n```\n\n"                       # lines 5-9
            "| Suchbegriff | Notiz |\n| --- | --- |\n| Kamm | b |\n\n"        # lines 10-13
            "| # | Quelle | URL | gelesen am | Notizen |\n| --- | --- | --- | --- | --- |\n"
            "| 1 | Hilfe | https://x.example.com/a | 2026-10-17 | |\n"       # line 16
            "~~~\n# robots.txt\n~~~\n"
            "| 2 | robots | siehe visibility.md | 2026-10-17 | |\n\n"       # line 20
            "| Anfrage | URL | gelesen am |\n| --- | --- | --- |\n"
            "| q | https://x.example.com/b | 2026-10-17 |\n\n"               # line 24
            "## Quellen\n\n| URL | gelesen am |\n| --- | --- |\n"
            "| https://x.example.com/c | 2026-10-17 |\n")                    # line 30
        self.assertEqual(self.kinds(), (1, [("recon_url", 20)]))
        code, out, _ = run([self.root, "--as-of", AS_OF, "--json"])
        self.assertEqual(json.loads(out)["recon"], 4)

    def test_recon_without_a_sources_table_fails(self):
        put(self.root, "recon.md", "# Recon: X\n\n## Core loop\n\nBook a slot.\n")
        self.assertEqual(self.kinds(), (1, [("recon_none", None)]))
        self.recon("## Sources\n\n| # | source | notes |\n| --- | --- | --- |\n",
                   "| 1 | help center | |\n")
        self.assertEqual(self.kinds(), (1, [("recon_none", None)]))
        self.recon(self.EN, "")     # bad rows deleted instead of fixed
        self.assertEqual(self.kinds(), (1, [("recon_none", None)]))
        code, out, _ = run([self.root, "--as-of", AS_OF])
        self.assertIn("recon.md has no sources table", out)

    def test_no_recon_md_is_not_checked(self):
        code, out, _ = run([self.root, "--as-of", AS_OF, "--json"])
        self.assertEqual((code, json.loads(out)["recon"]), (0, None))
        self.assertIn("nothing to check", run([self.root, "--as-of", AS_OF])[1])


if __name__ == "__main__":
    unittest.main()
