import csv
import datetime
import io
import json
import os
import re
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from _load import load

reviews = load("reviews")

ROWS = [
    ("app-store", "https://apps.apple.com/r/1", "2026-08-01", "1",
     "Way too expensive for what it is. I wish it had SMS reminders."),
    ("google-play", "https://play.google.com/r/2", "2026-07-15", "2",
     "The price doubled this year. Support never replied to my ticket."),
    ("g2", "https://www.g2.com/r/3", "2026-06-01", "2",
     "Overpriced per seat. No way to set buffer times between meetings."),
    ("reddit", "https://www.reddit.com/r/x/comments/4", "2026-05-01", "",
     "Honestly the subscription is the dealbreaker for my small team."),
    ("app-store", "https://apps.apple.com/r/5", "2026-08-10", "5",
     "Love it, works great every day."),
    ("capterra", "https://www.capterra.com/r/6", "2026-07-01", "1",
     "It crashes every time I open the calendar view."),
    ("app-store", "https://apps.apple.com/r/7", "2026-08-02", "1",
     "Booked twice for the same slot and the client was furious."),
    # no url: must be dropped, never counted
    ("app-store", "", "2026-08-01", "1", "Expensive and buggy."),
    # duplicate text: counted once
    ("google-play", "https://play.google.com/r/9", "2026-07-16", "2",
     "The price doubled this year.  Support never replied to my ticket."),
]

GERMAN = [
    ("trustpilot", "https://de.trustpilot.com/r/1", "03.08.2026", "1",
     "Viel zu teuer für das, was man bekommt. Leider keine Möglichkeit zum Export."),
    ("omr", "https://omr.com/de/reviews/r/2", "15.07.2026", "4/5",
     "Gute Software, aber die Bedienung ist umständlich. Ich wünschte, es gäbe eine DATEV-Schnittstelle."),
    ("trusted-shops", "https://www.trustedshops.de/r/3", "2026-06-01", "2",
     "Die Lieferung hat zwei Wochen gedauert und die Retoure war ein Albtraum."),
    ("google-maps", "https://maps.google.com/r/4", "2026-05-01", "★★☆☆☆",
     "Kauf auf Rechnung nicht möglich, Kundenservice nicht erreichbar."),
    ("capterra", "https://www.capterra.com.de/r/5", "2026-08-12", "2,5",
     "Seit dem Update stürzt die App ständig ab."),
]


def write_csv(path, rows, header=("source", "url", "date", "rating", "text"), delimiter=","):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=delimiter)
        w.writerow(header)
        w.writerows(rows)


class Feedback(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "reviews.csv")
        write_csv(self.path, ROWS)
        self.themes, self.req = reviews.load_themes()
        self.kept, self.dropped, self.dupes = reviews.load_reviews(self.path)
        self.result = reviews.analyse(self.kept, self.themes, self.req,
                                      today=datetime.date(2026, 10, 1))

    def tearDown(self):
        self.tmp.cleanup()

    def test_unsourced_rows_are_dropped_and_duplicates_removed(self):
        self.assertEqual(self.dropped, 1)
        self.assertEqual(self.dupes, 1)
        self.assertEqual(len(self.kept), 7)

    def test_price_is_the_top_complaint(self):
        top = [t for t in self.result["themes"] if t["kind"] == "complaint"][0]
        self.assertEqual(top["id"], "pricing")
        self.assertEqual(top["count"], 4)
        self.assertFalse(top["thin"])
        self.assertEqual(len(top["sources"]), 4)

    def test_every_quote_is_verbatim_and_linked(self):
        by_url = {r["url"]: r["text"] for r in self.kept}
        quotes = [q for t in self.result["themes"] for q in t["quotes"]]
        quotes += self.result["requests"]
        self.assertTrue(quotes)
        for q in quotes:
            self.assertIn(q["url"], by_url)
            self.assertIn(q["quote"].strip(".").strip(), by_url[q["url"]])

    def test_requests_are_found_in_their_own_words(self):
        texts = [q["quote"] for q in self.result["requests"]]
        self.assertTrue(any("SMS reminders" in t for t in texts))
        self.assertTrue(any("buffer times" in t for t in texts))

    def test_single_source_theme_is_thin(self):
        bugs = next(t for t in self.result["themes"] if t["id"] == "bugs")
        self.assertTrue(bugs["thin"])

    def test_unthemed_low_ratings_are_surfaced(self):
        urls = [r["url"] for r in self.result["unthemed_negative"]]
        self.assertIn("https://apps.apple.com/r/7", urls)

    def test_old_reviews_count_half(self):
        rv = {"rating": 1.0, "date": datetime.date(2023, 1, 1)}
        self.assertEqual(reviews.weight(rv, datetime.date(2026, 10, 1), 18), 0.5)
        rv = {"rating": None, "date": None}
        self.assertEqual(reviews.weight(rv, datetime.date(2026, 10, 1), 18), 0.6)

    def test_render_has_small_sample_warning_sources_and_links(self):
        text = reviews.render(self.result, self.dropped, self.dupes)
        self.assertIn("Small sample", text)
        self.assertIn("1 rows dropped", text)
        self.assertIn("## Sample by source", text)
        self.assertIn("https://www.g2.com/r/3", text)

    def test_cli_requires_url_column(self):
        p = os.path.join(self.tmp.name, "nourl.csv")
        write_csv(p, [("app-store", "great")], header=("source", "text"))
        with redirect_stderr(io.StringIO()):
            self.assertEqual(reviews.main([p]), 2)

    def test_cli_json_and_out(self):
        out = os.path.join(self.tmp.name, "feedback.md")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(reviews.main([self.path, "--today", "2026-10-01",
                                           "--out", out]), 0)
        with open(out, encoding="utf-8") as fh:
            self.assertIn("# The original: what customers hate and ask for", fh.read())
        buf = io.StringIO()
        with redirect_stdout(buf):
            reviews.main([self.path, "--json", "--today", "2026-10-01"])
        data = json.loads(buf.getvalue())
        self.assertEqual(data["dropped"], 1)

    def test_snippet_truncates_around_the_match(self):
        text = "x" * 400 + " too expensive " + "y" * 400
        s = reviews.snippet(text, re.compile("expensive"), limit=100)
        self.assertIn("expensive", s)
        self.assertLessEqual(len(s), 106)


class German(unittest.TestCase):
    """German reviews, German Excel export (semicolons, German headers)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "bewertungen.csv")
        write_csv(self.path, GERMAN, header=("Quelle", "Link", "Datum", "Bewertung", "Text"),
                  delimiter=";")
        self.themes, self.req = reviews.load_themes()
        self.kept, _, _ = reviews.load_reviews(self.path)
        self.result = reviews.analyse(self.kept, self.themes, self.req,
                                      today=datetime.date(2026, 10, 1))
        self.ids = {t["id"] for t in self.result["themes"]}

    def tearDown(self):
        self.tmp.cleanup()

    def test_semicolon_csv_with_german_headers_loads(self):
        self.assertEqual(len(self.kept), 5)
        self.assertEqual(self.kept[0]["source"], "trustpilot")
        self.assertEqual(self.kept[0]["date"], datetime.date(2026, 8, 3))

    def test_ratings_are_normalised(self):
        ratings = [r["rating"] for r in self.kept]
        self.assertEqual(ratings, [1.0, 4.0, 2.0, 2.0, 2.5])

    def test_german_and_shop_themes_match(self):
        for theme in ("pricing", "ux", "shipping", "returns", "checkout", "support",
                      "bugs", "updates", "integrations"):
            self.assertIn(theme, self.ids, theme)

    def test_german_requests_found(self):
        texts = " | ".join(q["quote"] for q in self.result["requests"])
        self.assertIn("Leider keine Möglichkeit zum Export", texts)
        self.assertIn("DATEV-Schnittstelle", texts)

    def test_german_report(self):
        text = reviews.render(self.result, lang="de", target="Shop X")
        self.assertIn("# Shop X: was Kunden stört", text)
        self.assertIn("Versand und Lieferung", text)
        self.assertIn("Kleine Stichprobe", text)


class Praise(unittest.TestCase):
    """Praise is reported as praise, not counted as a complaint."""

    def analyse(self, rows):
        themes, req = reviews.load_themes()
        reviews_ = [{"source": s, "url": "https://x/%d" % i, "date": None,
                     "rating": r, "text": txt} for i, (s, r, txt) in enumerate(rows)]
        return reviews.analyse(reviews_, themes, req, today=datetime.date(2026, 10, 1))

    def test_five_star_praise_is_not_a_complaint(self):
        res = self.analyse([("trusted-shops", 5.0, "Super Qualität, schneller Versand, gerne wieder.")])
        self.assertEqual(res["themes"], [])
        self.assertEqual({p["id"] for p in res["praise"]}, {"quality", "shipping"})
        self.assertIn("## Was gelobt wird", reviews.render(res, lang="de"))

    def test_four_stars_with_but_is_a_complaint(self):
        res = self.analyse([("omr", 4.0, "Gute Software, aber die Bedienung ist umständlich."),
                            ("omr", 4.0, "Übersichtlich und nicht kompliziert.")])
        ux = next(t for t in res["themes"] if t["id"] == "ux")
        self.assertEqual(ux["count"], 1)
        self.assertEqual([p["id"] for p in res["praise"]], ["ux"])

    def test_german_compounds_and_size(self):
        res = self.analyse([
            ("trusted-shops", 3.0, "Versandkosten von 6,95 € sind zu hoch, Gratisversand erst ab 100 €."),
            ("google-maps", 2.0, "Die Größe fällt klein aus und die Größentabelle fehlt komplett."),
        ])
        ids = {t["id"] for t in res["themes"]}
        self.assertIn("shipping", ids)
        self.assertIn("size_fit", ids)
        self.assertNotIn("quality", ids)

    def test_phone_complaint_is_not_a_platform_request(self):
        res = self.analyse([("reddit", None, "Der Shop ist auf dem Handy total unübersichtlich.")])
        ids = {t["id"] for t in res["themes"]}
        self.assertIn("ux", ids)
        self.assertNotIn("platforms", ids)

    def test_three_star_unthemed_goes_to_read_by_hand(self):
        res = self.analyse([("g2", 3.0, "Meh. Not what I expected at all.")])
        self.assertEqual(len(res["unthemed_negative"]), 1)


class Parsing(unittest.TestCase):
    def test_rating_formats(self):
        p = reviews.parse_rating
        self.assertEqual(p("4"), 4.0)
        self.assertEqual(p("4,5"), 4.5)
        self.assertEqual(p("4/5"), 4.0)
        self.assertEqual(p("10/10"), 5.0)
        self.assertEqual(p("0/10"), 1.0)
        self.assertEqual(p("4 Sterne"), 4.0)
        self.assertEqual(p("★★★☆☆"), 3.0)
        self.assertIsNone(p("7"))
        self.assertIsNone(p("great"))
        self.assertIsNone(p(""))

    def test_date_formats(self):
        d = reviews.parse_date
        self.assertEqual(d("2026-08-01"), datetime.date(2026, 8, 1))
        self.assertEqual(d("2026-08"), datetime.date(2026, 8, 1))
        self.assertEqual(d("01.08.2026"), datetime.date(2026, 8, 1))
        self.assertEqual(d("1.8.26"), datetime.date(2026, 8, 1))
        self.assertEqual(d("2026/08/01"), datetime.date(2026, 8, 1))
        self.assertIsNone(d("last week"))

    def test_dominant_source_is_flagged(self):
        rows = [{"source": "app-store", "url": "https://a/%d" % i, "date": None,
                 "rating": 1.0, "text": "too expensive %d" % i} for i in range(9)]
        rows.append({"source": "g2", "url": "https://b/1", "date": None, "rating": 1.0,
                     "text": "too expensive"})
        themes, req = reviews.load_themes()
        result = reviews.analyse(rows, themes, req, today=datetime.date(2026, 10, 1))
        self.assertEqual(result["dominant_source"]["source"], "app-store")
        self.assertIn("90% of the reviews come from app-store", reviews.render(result))

    def test_saas_return_is_not_a_shop_return(self):
        themes, req = reviews.load_themes()
        rows = [{"source": "g2", "url": "https://g2/1", "date": None, "rating": 2.0,
                 "text": "The API returned an error and I had to return to the old tool."}]
        ids = {t["id"] for t in reviews.analyse(rows, themes, req)["themes"]}
        self.assertNotIn("returns", ids)


if __name__ == "__main__":
    unittest.main()
