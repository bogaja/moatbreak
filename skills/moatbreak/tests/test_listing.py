import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from _load import load, ROOT

listing = load("listing")

GOOD = {"app_store": {"name": "Taktilo: Termine im Salon", "subtitle": "Buchen ohne Doppeltermine",
                      "keywords": "friseur,termin,salon,buchung,kalender",
                      "promotional_text": "Neu: Wartelisten für freie Termine.",
                      "description": "Taktilo plant Termine für Friseursalons."},
        "google_play": {"title": "Taktilo – Salontermine", "short_description":
                        "Termine für Friseursalons online buchen lassen.",
                        "full_description": "Taktilo plant Termine für Friseursalons."}}


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = listing.main(argv)
    return code, out.getvalue(), err.getvalue()


class Listing(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, data, name="listing.json"):
        path = os.path.join(self.tmp.name, name)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
        return path

    def test_limits_are_the_stores(self):
        self.assertEqual(dict(listing.LIMITS["app_store"]),
                         {"name": 30, "subtitle": 30, "keywords": 100,
                          "promotional_text": 170, "description": 4000})
        self.assertEqual(dict(listing.LIMITS["google_play"]),
                         {"title": 30, "short_description": 80, "full_description": 4000})

    def test_clean_listing_passes(self):
        res = listing.check(GOOD, ["Kammfux", "Kammfux GmbH"])
        self.assertEqual(res["failed"], 0)
        self.assertEqual(len(res["fields"]), 8)

    def test_too_long_and_empty_fail(self):
        data = {"app_store": {"name": "x" * 31, "subtitle": "  ", "keywords": "k" * 100}}
        res = listing.check(data)
        by = {r["field"]: r for r in res["fields"]}
        self.assertEqual(by["name"]["problems"], [{"kind": "too_long", "n": 1}])
        self.assertEqual(by["subtitle"]["problems"], [{"kind": "empty"}])
        self.assertTrue(by["keywords"]["pass"])                  # exactly at the limit
        self.assertFalse(res["names_checked"])

    def test_names_variants_and_near_spellings_fail(self):
        data = {"app_store": {"name": "Taktilo", "keywords": "kammfux,friseur",
                              "description": "Besser als Kamfux und Mueller Salon."},
                "google_play": {"title": "Taktilo", "short_description":
                                "Die Alternative zu Müller Salon",
                                "full_description": "Ein Kalender für Salons."}}
        res = listing.check(data, ["Kammfux", "Müller Salon"])
        by = {(r["store"], r["field"]): r["problems"] for r in res["fields"]}
        self.assertEqual(by[("app_store", "keywords")],
                         [{"kind": "name", "name": "Kammfux", "match": "kammfux"}])
        self.assertIn({"kind": "near", "name": "Kammfux", "match": "Kamfux"},
                      by[("app_store", "description")])
        self.assertIn({"kind": "name", "name": "Müller Salon", "match": "Mueller Salon"},
                      by[("app_store", "description")])
        self.assertEqual(by[("google_play", "short_description")][0]["kind"], "name")
        self.assertEqual(by[("google_play", "full_description")], [])   # Kalender is no name

    def test_locales_and_unknown_fields(self):
        data = {"locales": {"de-DE": {"app_store": {"name": "Taktilo", "titel": "x"}},
                            "en-US": {"google_play": {"title": "Taktilo"}}}}
        res = listing.check(data)
        self.assertEqual([(r["locale"], r["field"]) for r in res["fields"]],
                         [("de-DE", "name"), ("en-US", "title")])
        self.assertEqual(res["unknown"], [{"locale": "de-DE", "store": "app_store",
                                           "fields": ["titel"]}])

    def test_cli_with_brand_json(self):
        brand = self.write({"avoid": ["Kammfux"], "colors": []}, "brand.json")
        bad = self.write({"app_store": {"name": "Kammfux Alternative"}})
        code, out, _ = run([bad, "--config", brand, "--lang", "de", "--markdown"])
        self.assertEqual(code, 1)
        self.assertIn("| - | App Store | name | 19 | 30 | NICHT OK: Name des Originals: "
                      "Kammfux |", out)
        good = self.write(GOOD, "good.json")
        out_file = os.path.join(self.tmp.name, "listing.md")
        code, stdout, _ = run([good, "--config", brand, "--out", out_file])
        self.assertEqual((code, stdout), (0, "wrote %s\n" % out_file))
        code, _, err = run([self.write({"other": {}}, "x.json")])
        self.assertEqual(code, 2)
        self.assertIn("no \"app_store\" or \"google_play\"", err)

    def test_shipped_template_has_every_field_and_fails_empty(self):
        path = os.path.join(ROOT, "templates", "listing.json")
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        res = listing.check(data)
        self.assertEqual(len(res["fields"]), 8)
        self.assertEqual(res["failed"], 8)                       # an empty template never passes


if __name__ == "__main__":
    unittest.main()
