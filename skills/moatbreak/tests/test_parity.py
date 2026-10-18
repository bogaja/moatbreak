import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from _load import load, ROOT

parity = load("parity")

MATRIX = """feature,area,priority,original,clone,effort,notes
Pick a time slot,booking page,must,yes,yes,M,
Confirmation email,booking page,must,yes,partial,S,no calendar file yet
Reschedule link,booking page,must,yes,no,M,
Round-robin across a team,team,should,yes,no,L,
Custom booking questions,booking page,should,yes,yes,S,
Embed on a website,sharing,could,yes,no,2-4,
Their partner marketplace,integrations,could,yes,skip,XL,their network not ours
SMS reminders,notifications,should,no,yes,M,ours: the top request in reviews
"""

GERMAN = """feature;area;priority;original;clone;effort;notes
Warenkorb;Kasse;muss;ja;ja;M;
Kauf auf Rechnung;Kasse;muss;ja;teilweise;2;
Wunschliste;Konto;kann;ja;nein;1,5;
Marktplatz;Partner;kann;ja;entfällt;XL;fremdes Netzwerk
"""


def write(d, name, text):
    path = os.path.join(d, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


class Score(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = write(self.tmp.name, "features.csv", MATRIX)

    def tearDown(self):
        self.tmp.cleanup()

    def test_weighted_score(self):
        r = parity.score(parity.load(self.path))
        # counted weights: 3+3+3+2+2+1 = 14, earned: 3 + 1.5 + 0 + 0 + 2 + 0 = 6.5
        self.assertAlmostEqual(r["feature_score"], round(100 * 6.5 / 14, 1))
        self.assertEqual(r["counted"], 6)
        self.assertEqual((r["must_have_done"], r["must_have_total"]), (1, 3))

    def test_skip_and_extras_are_not_scored_but_listed(self):
        r = parity.score(parity.load(self.path))
        self.assertEqual([m["feature"] for m in r["skipped"]], ["Their partner marketplace"])
        self.assertEqual([m["feature"] for m in r["extras"]], ["SMS reminders"])

    def test_missing_is_in_build_order(self):
        r = parity.score(parity.load(self.path))
        order = [m["feature"] for m in r["missing"]]
        self.assertEqual(order[0], "Reschedule link")          # must, not started
        self.assertEqual(order[1], "Confirmation email")       # must, partial
        self.assertEqual(order[2], "Round-robin across a team")
        self.assertEqual(order[-1], "Embed on a website")
        self.assertEqual(r["missing"][0]["weight"], 3)

    def test_weakest_area_first(self):
        r = parity.score(parity.load(self.path))
        self.assertEqual(r["by_area"][0]["score"], 0.0)
        self.assertIn(r["by_area"][0]["area"], ("team", "sharing"))

    def test_render_says_not_shippable(self):
        r = parity.combine(parity.estimate(parity.score(parity.load(self.path))), [])
        text = parity.render(r)
        self.assertIn("Not shippable yet: 2 must-have", text)
        self.assertIn("their network not ours", text)

    def test_visual_folds_in_at_20_percent(self):
        d = self.tmp.name
        v1 = write(d, "a.json", json.dumps({"score": 80.0, "mode": "layout",
                                            "files": {"clone": "clone/home.png"}}))
        v2 = write(d, "b.json", json.dumps({"score": 60.0, "mode": "layout"}))
        r = parity.combine(parity.score(parity.load(self.path)),
                           parity.visual_scores([v1, v2]))
        self.assertEqual(r["layout_score"], 70.0)
        self.assertAlmostEqual(r["overall"], round(0.8 * r["feature_score"] + 14.0, 1))

    def test_bad_values_are_reported_not_fatal(self):
        p = write(self.tmp.name, "bad.csv",
                  "feature,priority,clone,effort\nThing,urgent,maybe,lots\n")
        r = parity.score(parity.load(p))
        self.assertEqual(len(r["problems"]), 3)
        self.assertEqual(r["feature_score"], 0.0)

    def test_missing_column_is_an_error(self):
        p = write(self.tmp.name, "nocol.csv", "feature,area\nx,y\n")
        with redirect_stderr(io.StringIO()):
            self.assertEqual(parity.main([p]), 2)

    def test_extra_fields_name_the_line(self):
        p = write(self.tmp.name, "comma.csv", "feature,priority,clone,notes\n"
                  "Booking,must,yes,ok\nExport,should,no,CSV, PDF\n")
        with self.assertRaises(parity.MatrixError) as ctx:
            parity.load(p)
        self.assertIn("line 3 has more fields than the header", str(ctx.exception))
        with redirect_stderr(io.StringIO()):
            self.assertEqual(parity.main([p]), 2)

    def test_cli_fail_under(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(parity.main([self.path, "--fail-under", "80"]), 1)
            self.assertEqual(parity.main([self.path, "--fail-under", "10"]), 0)

    def test_shipped_template_parses(self):
        path = os.path.join(ROOT, "templates", "features.example.csv")
        r = parity.score(parity.load(path))
        self.assertGreater(r["counted"], 0)
        self.assertEqual(r["problems"], [])


class Effort(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = write(self.tmp.name, "features.csv", MATRIX)

    def tearDown(self):
        self.tmp.cleanup()

    def test_parse_effort(self):
        p = parity.parse_effort
        self.assertEqual(p("M"), (1.0, 3.0))
        self.assertEqual(p("3"), (3.0, 3.0))
        self.assertEqual(p("2-4"), (2.0, 4.0))
        self.assertEqual(p("1,5"), (1.5, 1.5))
        self.assertEqual(p("2 bis 3 Tage"), (2.0, 3.0))
        self.assertEqual(p("4-2"), (2.0, 4.0))
        self.assertIsNone(p(""))
        self.assertIsNone(p("lots"))

    def test_cumulative_tiers(self):
        r = parity.estimate(parity.score(parity.load(self.path)))
        tiers = {t["scope"]: t for t in r["effort"]["tiers"]}
        # must open: reschedule M (1-3) + confirmation S half (0.25-0.5)
        self.assertEqual((tiers["mvp"]["days_low"], tiers["mvp"]["days_high"]), (1.2, 3.5))
        # + should: round-robin L (3-6); SMS (extra) is done, so 0
        self.assertEqual((tiers["plus_should"]["days_low"], tiers["plus_should"]["days_high"]),
                         (4.2, 9.5))
        # + could: embed 2-4; the skipped marketplace is not work
        self.assertEqual((tiers["plus_could"]["days_low"], tiers["plus_could"]["days_high"]),
                         (6.2, 13.5))
        self.assertEqual(r["effort"]["unestimated"], [])

    def test_buffer_and_day_rate(self):
        r = parity.estimate(parity.score(parity.load(self.path)), buffer_pct=20, day_rate=600)
        mvp = r["effort"]["tiers"][0]
        self.assertEqual((mvp["days_low"], mvp["days_high"]), (1.5, 4.2))
        self.assertEqual((mvp["cost_low"], mvp["cost_high"]), (900, 2520))

    def test_unestimated_rows_are_reported_not_guessed(self):
        p = write(self.tmp.name, "f.csv",
                  "feature,priority,original,clone,effort\nA,must,yes,no,M\nB,must,yes,no,\n")
        r = parity.estimate(parity.score(parity.load(p)))
        self.assertEqual(r["effort"]["unestimated"], ["B"])
        text = parity.render(parity.combine(r, []))
        self.assertIn("1 open features have no effort yet", text)

    def test_german_matrix_and_report(self):
        p = write(self.tmp.name, "de.csv", GERMAN)
        r = parity.score(parity.load(p))
        self.assertEqual(r["problems"], [])
        self.assertEqual(r["counted"], 3)
        self.assertEqual([m["feature"] for m in r["skipped"]], ["Marktplatz"])
        r = parity.combine(parity.estimate(r, buffer_pct=0, day_rate=700), [])
        text = parity.render(r, markdown=True, lang="de")
        self.assertIn("## Parität:", text)
        self.assertIn("Noch nicht auslieferbar, offene Muss-Features: 1.", text)
        self.assertIn("| MVP (Muss) | 1 | 1 | 700 |", text)
        self.assertIn("[Muss] Kasse: Kauf auf Rechnung, teilweise", text)
        self.assertIn("+ Kann (alles)", text)

    def test_cli_with_cost(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(parity.main([self.path, "--markdown", "--buffer", "10",
                                          "--day-rate", "650"]), 0)
        self.assertIn("| scope | features | person-days | EUR |", buf.getvalue())
        self.assertIn("Contingency: 10% on the feature effort.", buf.getvalue())


class Offer(unittest.TestCase):
    """Estimate-only output, overheads, fixed items, unknown originals."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = write(self.tmp.name, "features.csv", MATRIX)

    def tearDown(self):
        self.tmp.cleanup()

    def test_overhead_and_fixed_items(self):
        r = parity.estimate(parity.score(parity.load(self.path)), buffer_pct=0, day_rate=100,
                            overhead=parity.parse_items("QA=10,PM=10", percent=True),
                            fixed=parity.parse_items("Setup=2-3;Design=1"))
        mvp = r["effort"]["tiers"][0]
        # features 1.25-3.5, overhead 20% = 0.25-0.7, fixed 3-4
        self.assertEqual((mvp["feature_low"], mvp["feature_high"]), (1.2, 3.5))
        self.assertEqual((mvp["overhead_low"], mvp["overhead_high"]), (0.2, 0.7))
        self.assertEqual((mvp["fixed_low"], mvp["fixed_high"]), (3.0, 4.0))
        self.assertEqual((mvp["days_low"], mvp["days_high"]), (4.5, 8.2))
        self.assertEqual((mvp["cost_low"], mvp["cost_high"]), (450, 820))

    def test_estimate_only_has_no_parity_lines(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            parity.main([self.path, "--estimate-only", "--markdown", "--lang", "de",
                         "--overhead", "QA=15", "--fixed", "Setup=2", "--day-rate", "650"])
        text = buf.getvalue()
        self.assertIn("# Aufwandsschätzung", text)
        self.assertIn("| Umfang | Features | Feature-PT | Zuschläge | Pauschal | Gesamt-PT | EUR |", text)
        self.assertIn("| + Soll | 3 |", text)   # SMS (own) is already done
        self.assertNotIn("Parität", text)
        self.assertNotIn("auslieferbar", text)
        self.assertIn("Their partner marketplace", text)

    def test_only_own_rows_says_parity_not_measurable(self):
        p = write(self.tmp.name, "own.csv",
                  "feature,priority,original,clone,effort\nSMS,must,no,no,S\n")
        r = parity.combine(parity.estimate(parity.score(parity.load(p))), [])
        text = parity.render(r, lang="de")
        self.assertIn("Parität ist daher nicht messbar", text)
        self.assertNotIn("Jedes gezählte Feature ist fertig", text)
        self.assertIn("[Muss] SMS: offen", text)
        self.assertIn("| MVP (Muss) | 1 (davon 1 eigene) |", text)

    def test_unknown_original_is_counted_but_flagged(self):
        p = write(self.tmp.name, "unk.csv",
                  "feature,priority,original,clone,effort\nA,must,?,no,M\nB,must,ja,no,S\n")
        r = parity.score(parity.load(p))
        self.assertEqual(r["counted"], 2)
        self.assertEqual(r["unverified"], ["A"])
        r = parity.combine(parity.estimate(r), [])
        self.assertIn("Unverified: 1 rows", parity.render(r))

    def test_out_file(self):
        out = os.path.join(self.tmp.name, "estimate.md")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(parity.main([self.path, "--estimate-only", "--out", out]), 0)
        with open(out, encoding="utf-8") as fh:
            self.assertIn("Effort estimate", fh.read())

    def test_bad_items_are_an_error(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(parity.main([self.path, "--fixed", "Setup"]), 2)
            self.assertEqual(parity.main([self.path, "--fixed", "Setup=lots"]), 2)


if __name__ == "__main__":
    unittest.main()
