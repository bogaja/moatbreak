"""Checks for the eval suite in evals/: its format, that the fixtures stay
synthetic, and the facts about the fixtures that the assertions rely on. The
scripts run as a user runs them, so a change to a script or a fixture that
would make an assertion wrong fails here first."""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

from _load import ROOT

EVALS = os.path.join(ROOT, "evals")
FILES = os.path.join(EVALS, "files")
SCRIPTS = os.path.join(ROOT, "scripts")
FIELDS = {"id", "prompt", "expected_output", "assertions", "files", "web", "should_trigger"}
AS_OF = "2026-10-17"

with open(os.path.join(EVALS, "evals.json"), encoding="utf-8") as _f:
    SUITE = json.load(_f)
EVAL = {e["id"]: e for e in SUITE["evals"]}


def text(eval_id):
    e = EVAL[eval_id]
    return " ".join([e["expected_output"]] + e["assertions"])


def fixture(*parts):
    return os.path.join(FILES, *parts)


def run(script, *args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, script + ".py")] + list(args),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                          encoding="utf-8")
    return proc.returncode, proc.stdout


class FormatTest(unittest.TestCase):
    def test_skill_name_matches_frontmatter(self):
        with open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8") as f:
            name = re.search(r"^name:\s*(\S+)", f.read(), re.M).group(1)
        self.assertEqual(SUITE["skill_name"], name)

    def test_fields_and_ids(self):
        evals = SUITE["evals"]
        self.assertEqual(len(evals), 18)
        self.assertEqual([e["id"] for e in evals], list(range(1, len(evals) + 1)))
        for e in evals:
            with self.subTest(id=e["id"]):
                self.assertEqual(set(e), FIELDS)
                self.assertTrue(e["prompt"].strip() and e["expected_output"].strip())
                self.assertTrue(5 <= len(e["assertions"]) <= 9)
                self.assertTrue(all(isinstance(a, str) and a.strip() for a in e["assertions"]))
                self.assertEqual(len(set(e["assertions"])), len(e["assertions"]))
                self.assertIsInstance(e["web"], bool)
                self.assertIsInstance(e["should_trigger"], bool)

    def test_files_exist_inside_a_set(self):
        for e in SUITE["evals"]:
            for path in e["files"]:
                with self.subTest(id=e["id"], path=path):
                    parts = path.split("/")
                    self.assertEqual(parts[:2], ["evals", "files"])
                    self.assertGreaterEqual(len(parts), 4, "evals/files/<set>/<path>")
                    self.assertTrue(os.path.isfile(os.path.join(ROOT, *parts)))

    def test_suite_has_both_kinds(self):
        negatives = [e for e in SUITE["evals"] if not e["should_trigger"]]
        self.assertGreaterEqual(len(negatives), 3)      # near misses, not only far-off topics
        self.assertEqual({True, False}, {e["web"] for e in SUITE["evals"]})

    def test_fixtures_are_synthetic(self):
        for folder, _, names in os.walk(FILES):
            for name in names:
                with open(os.path.join(folder, name), encoding="utf-8") as f:
                    content = re.sub(r'\sxmlns(:\w+)?="[^"]*"', "", f.read())  # a namespace is no link
                for url in re.findall(r"https?://[^\s\"',)<>|]+", content):
                    host = re.match(r"https?://([^/:]+)", url).group(1)
                    with self.subTest(file=name, url=url):
                        self.assertTrue(host == "example.com" or host.endswith(".example.com"))


class FixtureFactsTest(unittest.TestCase):
    """Facts the assertions quote. Change the assertion together with the fixture."""

    reviews_csv = fixture("build", "teardown", "reviews.csv")
    build_features = fixture("build", "teardown", "features.csv")

    def test_reviews(self):
        code, out = run("reviews", self.reviews_csv, "--as-of", AS_OF, "--target", "ExampleSlot",
                        "--json")
        self.assertEqual(code, 0)
        d = json.loads(out)
        self.assertEqual((d["reviews"], d["dropped"], len(d["sources"])), (26, 1, 3))
        self.assertEqual(d["dominant_source"]["source"], "capterra")
        self.assertGreater(d["dominant_source"]["share_pct"], 60)
        thin = {t["id"] for t in d["themes"] if t["thin"]}
        self.assertTrue({"privacy", "account"} <= thin)
        alternatives = {a["name"]: a["count"] for a in d["switching"]["alternatives"]}
        self.assertEqual(alternatives, {"AltSlot": 2})
        self.assertEqual([r["url"].rsplit("/", 1)[1] for r in d["switching"]["toward_original"]],
                         ["exampleslot-115"])
        unthemed = [r["url"].rsplit("/", 1)[1] for r in d["unthemed_negative"]]
        self.assertIn("exampleslot-111", unthemed)
        for needle in ("26 reviews", "1 row", "AltSlot (2 reviews)", "exampleslot-115",
                       "exampleslot-111"):
            self.assertIn(needle, text(5))
        self.assertIn("26 reviews from 3 sources", text(14))

    def test_parity(self):
        code, out = run("parity", self.build_features, "--markdown")
        self.assertEqual(code, 0)
        self.assertIn("Parity: 53.4 / 100", out)
        self.assertIn("must-haves 4 of 7 done", out)
        self.assertIn("Not shippable", out)
        self.assertIn("Gift vouchers", out.split("have no effort")[-1])
        self.assertIn("53.4", text(9))
        self.assertIn("4 of 7", text(9))

    def test_offer_estimate(self):
        code, out = run("parity", fixture("offer", "teardown", "features.csv"), "--estimate-only",
                        "--lang", "de", "--markdown", "--buffer", "20", "--overhead", "QA=15,PM=10",
                        "--fixed", "Workshop=2-3;Setup=2-3;Design=5-8;Go-live=2-3",
                        "--day-rate", "720")
        self.assertEqual(code, 0)
        mvp = [line for line in out.splitlines() if line.startswith("| MVP")][0]
        self.assertIn("24,5 - 51,5", mvp)
        self.assertIn("17.640 - 37.080", mvp)
        self.assertIn("24,5-51,5", text(14))
        self.assertIn("17.640-37.080", text(14))

    def test_battlecard(self):
        with tempfile.TemporaryDirectory() as d:
            code, out = run("reviews", self.reviews_csv, "--as-of", AS_OF, "--json")
            self.assertEqual(code, 0)
            feedback = os.path.join(d, "feedback.json")
            with open(feedback, "w", encoding="utf-8") as f:
                f.write(out)
            code, out = run("battlecard", "--feedback", feedback, "--features", self.build_features,
                            "--target", "ExampleSlot", "--ours", "NeuSlot", "--as-of", AS_OF,
                            "--json")
        self.assertEqual(code, 0)
        card = json.loads(out)
        self.assertEqual((card["claims"]["stale"], card["claims"]["assumed"]), (2, 1))
        page = {r["feature"]: r for r in card["page"]["rows"]}
        for left_out in ("Stylist levels with different prices", "DATEV export",
                         "Waitlist for cancelled slots", "Online payment at booking"):
            self.assertNotIn(left_out, page)
        self.assertIn("Several services in one booking", page)
        self.assertEqual((page["Several services in one booking"]["theirs"],
                          page["Several services in one booking"]["ours"]), ("yes", "no"))
        # the praised performance theme carries its praise label, never the raw complaint label
        strong = {p["id"]: p["label"] for p in card["strong"]}
        self.assertEqual(strong.get("performance"), "Fast, no waiting")
        self.assertIn("Slow, laggy, heavy", text(7))
        for eval_id in (7, 8):
            self.assertIn("stylist levels", text(eval_id).lower())
        self.assertIn("2026-05-02", text(7))
        self.assertIn("2026-06-01", text(7))

    def test_visibility(self):
        code, out = run("sitemap", fixture("visibility", "teardown", "visibility", "sitemap.xml"),
                        "--as-of", AS_OF, "--json")
        self.assertEqual(code, 0)
        d = json.loads(out)
        types = {t["type"]: t["pages"] for t in d["types"]}
        self.assertEqual((d["pages"], dict(d["folders"]), dict(d["hreflang"])),
                         (16, {"de": 14, "en": 2}, {"de": 2, "en": 2}))
        self.assertEqual((types["comparison"], types["locations"]), (2, 2))
        for needle in ("16 pages", "14 in /de/ and 2 in /en/", "AltSlot", "OtherSlot",
                       "2 location pages", "Core Web Vitals"):
            self.assertIn(needle, text(15))

    def test_build_handoff(self):
        code, out = run("parity", self.build_features, "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["must_have_total"], 7)
        for needle in ("7 must features", "2.53:1", "WCAG 2.2 AA", "EN 301 549"):
            self.assertIn(needle, text(16))

    def test_brand(self):
        brand = fixture("brand", "teardown", "brand.json")
        code, out = run("contrast", "--palette", brand, "--json")
        self.assertEqual(code, 1)
        failing = [r for r in json.loads(out)["results"] if not r["pass"]]
        self.assertEqual([(r["fg_name"], r["bg_name"], r["ratio"]) for r in failing],
                         [("muted", "bg", 2.53)])
        code, out = run("sweep", fixture("brand"), "--config", brand, "--json")
        self.assertEqual(code, 1)
        hits = {(h["kind"], h["file"].replace(os.sep, "/")): h for h in json.loads(out)}
        self.assertIn(("name", "src/tokens.css"), hits)
        self.assertEqual(hits[("near-color", "src/tokens.css")]["delta_e"], 3.5)
        for needle in ("2.53:1", "#1565c0", "3.5", "exampleslot-button"):
            self.assertIn(needle, text(10))


if __name__ == "__main__":
    unittest.main()
