import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from _load import load

seo = load("seo")

# Synthetic exports: invented keywords and numbers, example.com URLs.
SEMRUSH = """Keyword,Position,Previous position,Search Volume,Keyword Difficulty,CPC,URL,Traffic,Traffic (%)
kammfux,1,1,"2,400",40,0.5,https://kammfux.example.com/,1500,50.0
kammfux login,1,1,880,20,0.1,https://kammfux.example.com/login,600,20.0
kammfux alternative,3,4,140,15,1.2,https://kammfux.example.com/vergleich,40,1.3
friseur software,4,5,1900,55,2.1,https://kammfux.example.com/friseur,300,10.0
online terminbuchung friseur,6,8,720,35,1.5,https://kammfux.example.com/friseur,120,4.0
friseur berlin online buchen,9,12,320,25,0.9,https://kammfux.example.com/berlin,60,2.0
wie funktioniert online terminbuchung,12,15,210,10,0.3,https://kammfux.example.com/blog/so-gehts,30,1.0
salon kasse,25,30,1300,45,1.8,https://kammfux.example.com/kasse,20,0.7
friseur software,4,5,1900,55,2.1,https://kammfux.example.com/friseur,300,10.0
"""
OURS_GSC = """Häufigste Suchanfragen;Klicks;Impressionen;CTR;Position
online terminbuchung friseur;12;400;3,0 %;14,2
taktilo;30;90;33,3 %;1,1
"""
AS_OF = "2026-10-17"


def write(d, name, text, encoding="utf-8"):
    path = os.path.join(d, name)
    with open(path, "w", encoding=encoding, newline="") as fh:
        fh.write(text)
    return path


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = seo.main(argv)
    return code, out.getvalue(), err.getvalue()


class Seo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.export = write(self.tmp.name, "semrush.csv", SEMRUSH)
        self.ours = write(self.tmp.name, "gsc.csv", OURS_GSC)
        rows, cols, _, _ = seo.load(self.export)
        self.cols = cols
        self.result = seo.analyse(rows, cols, ["Kammfux"], ["berlin"], seo.load(self.ours)[0])

    def tearDown(self):
        self.tmp.cleanup()

    def test_columns_and_duplicates(self):
        self.assertEqual(self.cols, ["keyword", "position", "traffic", "url", "volume"])
        self.assertEqual((self.result["keywords"], self.result["duplicates"]), (8, 1))

    def test_themes_in_order(self):
        themes = {t["theme"]: (t["keywords"], t["weight"]) for t in self.result["themes"]}
        self.assertEqual(themes["alternatives"], (1, 40.0))
        self.assertEqual(themes["branded"], (2, 2100.0))
        self.assertEqual(themes["local"], (1, 60.0))
        self.assertEqual(themes["how-to"], (1, 30.0))
        self.assertEqual(themes["category"], (3, 440.0))

    def test_branded_share_counts_the_name_in_alternatives_too(self):
        # (1500 + 600 + 40) of 2670 traffic
        self.assertEqual(self.result["branded_share_pct"], 80.1)

    def test_top_pages_sum_traffic(self):
        top = self.result["top_pages"][0]
        self.assertEqual((top["url"], top["traffic"]), ("https://kammfux.example.com/", 1500.0))
        friseur = [p for p in self.result["top_pages"] if p["url"].endswith("/friseur")][0]
        self.assertEqual((friseur["keywords"], friseur["traffic"]), (2, 420.0))

    def test_gap_leaves_out_brand_ours_and_beyond_top_20(self):
        gap = [r["keyword"] for r in self.result["gap"]["keywords"]]
        self.assertEqual(gap, ["friseur software", "friseur berlin online buchen",
                               "wie funktioniert online terminbuchung", "kammfux alternative"])
        self.assertEqual(self.result["gap"]["count"], 4)

    def test_report_labels_every_number(self):
        code, out, _ = run([self.export, "--tool", "semrush", "--database", "Google DE, de",
                            "--brand", "Kammfux", "--ours", self.ours, "--as-of", AS_OF,
                            "--lang", "de", "--name", "kammfux.example.com"])
        self.assertEqual(code, 0)
        label = "geschätzt von Semrush (Google DE, de), Export vom 17.10.2026"
        self.assertIn("Quelle: %s. 8 Keywords in semrush.csv." % label, out)
        self.assertIn("Markenanteil (Traffic): 80,1 %% (%s)" % label, out)
        self.assertIn("Jede Zahl oben: %s." % label, out)
        self.assertIn("| friseur software | Kategorie (allgemein) | 4 | 1.900 | 300 |", out)
        self.assertIn("Keywords im Thema Alternativen sind Vergleichssuchen", out)
        self.assertIn("Doppelte Keywords einmal gezählt: 1.", out)

    def test_search_console_is_measured_and_own_site_only(self):
        code, out, _ = run([self.ours, "--tool", "gsc", "--as-of", AS_OF])
        self.assertEqual(code, 0)
        self.assertIn("measured by Google Search Console for the user's own site", out)
        self.assertIn("never the original's", out)
        self.assertIn("Not in this export: volume, url.", out)
        self.assertIn("| online terminbuchung friseur | category (generic) | 14.2 | - | 12 | - |",
                      out)

    def test_ahrefs_utf16_tabs(self):
        ahrefs = write(self.tmp.name, "ahrefs.csv",
                       "Keyword\tVolume\tCurrent position\tCurrent URL\tOrganic traffic\n"
                       "kammfux preise\t90\t2\thttps://kammfux.example.com/preise\t30\n",
                       encoding="utf-16")
        rows, cols, _, _ = seo.load(ahrefs)
        self.assertEqual(rows[0]["volume"], 90.0)
        self.assertEqual(cols, ["keyword", "position", "traffic", "url", "volume"])

    def test_numbers(self):
        p = seo.parse_number
        self.assertEqual((p("2,400"), p("1.234"), p("12.5"), p("3,0 %"), p("1.234,5")),
                         (2400.0, 1234.0, 12.5, 3.0, 1234.5))
        self.assertIsNone(p("-"))
        with self.assertRaises(ValueError):
            p("lots")

    def test_json_and_errors(self):
        out = os.path.join(self.tmp.name, "seo.json")
        code, stdout, _ = run([self.export, "--tool", "semrush", "--as-of", AS_OF, "--json",
                               "--out", out])
        self.assertEqual((code, stdout), (0, "wrote %s\n" % out))
        with open(out, encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertEqual(data["source"]["label"],
                         "estimated by Semrush, export pulled 2026-10-17")
        self.assertIsNone(data["branded_share_pct"])
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):        # --as-of is required
                seo.main([self.export, "--tool", "semrush"])
        self.assertEqual(run([self.export, "--tool", "semrush", "--as-of", "17.10.2026"])[0], 2)
        nokw = write(self.tmp.name, "nokw.csv", "URL,Traffic\nhttps://x.example.com/,3\n")
        code, _, err = run([nokw, "--tool", "ahrefs", "--as-of", AS_OF])
        self.assertEqual(code, 2)
        self.assertIn("no keyword column", err)

    def test_bad_numbers_are_listed_not_fatal(self):
        bad = write(self.tmp.name, "bad.csv", "Keyword,Volume\nfriseur app,viele\n")
        code, out, _ = run([bad, "--tool", "sistrix", "--as-of", AS_OF])
        self.assertEqual(code, 0)
        self.assertIn("line 2: volume 'viele' is not a number", out)


if __name__ == "__main__":
    unittest.main()
