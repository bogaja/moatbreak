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

    def test_source_spellings_are_one_source(self):
        p = os.path.join(self.tmp.name, "mixed.csv")
        write_csv(p, [("App Store", "https://a/1", "", "1", "Too expensive."),
                      ("app_store", "https://a/2", "", "1", "Crashes."),
                      ("app-store", "https://a/3", "", "1", "Slow.")])
        self.assertEqual({r["source"] for r in reviews.load_reviews(p)[0]}, {"app-store"})

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

    def test_praise_carries_the_praise_label_not_the_complaint(self):
        res = self.analyse([("capterra", 5.0, "Läuft flott, keine Ladezeit.")])
        self.assertEqual(reviews.label_for(res["praise"][0]["label"], "en"), "Fast, no waiting")
        self.assertIn("**Schnell, ohne Wartezeit** (1)", reviews.render(res, lang="de"))

    def test_old_copy_without_praise_label_gets_the_shipped_one_if_unchanged(self):
        with open(reviews.DEFAULT_THEMES, encoding="utf-8") as fh:
            data = json.load(fh)
        for t in data["themes"]:
            t.pop("praise_label", None)
            if t["id"] == "support":
                t["label"] = "Hotline"           # changed by the user: keeps its own label
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "themes.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh)
            themes, _ = reviews.load_themes(path)
        labels = {t["id"]: t["praise_label"] for t in themes}
        self.assertEqual(labels["performance"]["en"], "Fast, no waiting")
        self.assertEqual(labels["support"], "Hotline")

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


AS_OF = datetime.date(2026, 10, 17)


def rows_of(items):
    """(source, rating, date or None, text) tuples to review dicts."""
    return [{"source": s, "url": "https://%s.example/%d" % (s, i), "date": d, "rating": r,
             "text": t} for i, (s, r, d, t) in enumerate(items)]


class SourceBias(unittest.TestCase):
    def analyse(self, items, months=18):
        themes, req = reviews.load_themes()
        return reviews.analyse(rows_of(items), themes, req, today=AS_OF, months=months)

    def kinds(self, result):
        return [w["kind"] for w in result["source_bias"]["warnings"]]

    def test_per_source_share_rating_and_dates(self):
        res = self.analyse([("g2", 4.0, datetime.date(2026, 3, 1), "ok"),
                            ("g2", 2.0, datetime.date(2026, 9, 1), "meh"),
                            ("reddit", None, None, "hm"),
                            ("app-store", 3.0, datetime.date(2025, 1, 5), "fine")])
        g2 = next(s for s in res["by_source"] if s["source"] == "g2")
        self.assertEqual((g2["count"], g2["share_pct"], g2["avg_rating"], g2["rated"]),
                         (2, 50.0, 3.0, 2))
        self.assertEqual((g2["first_date"], g2["last_date"]), ("2026-03-01", "2026-09-01"))
        reddit = next(s for s in res["by_source"] if s["source"] == "reddit")
        self.assertIsNone(reddit["first_date"])
        bias = res["source_bias"]
        self.assertEqual((bias["overall_avg_rating"], bias["dated"]), (3.0, 3))
        self.assertEqual((bias["first_date"], bias["last_date"]), ("2025-01-05", "2026-09-01"))
        self.assertEqual(bias["warnings"], [])
        text = reviews.render(res)
        self.assertIn("| g2 | 2 | 50% | 3.0 | 2026-03-01 | 2026-09-01 |", text)
        self.assertIn("| all | 4 | 100% | 3.0 | 2025-01-05 | 2026-09-01 |", text)
        self.assertIn("No lean found", text)

    def test_rating_gap_of_one_star_is_flagged_and_less_is_not(self):
        spread = datetime.date(2026, 1, 1)
        res = self.analyse([("g2", 5.0, spread, "a"), ("g2", 5.0, spread, "b"),
                            ("app-store", 3.0, spread, "c"), ("app-store", 3.0, spread, "d"),
                            ("app-store", 4.0, spread, "e"), ("app-store", 4.0, spread, "f")])
        gaps = [w for w in res["source_bias"]["warnings"] if w["kind"] == "rating_gap"]
        self.assertEqual([(w["source"], w["gap"]) for w in gaps], [("g2", 1.0)])
        self.assertIn("g2 gives 5.0 stars on average, 1.0 stars higher than all rated reviews",
                      reviews.render(res))
        res = self.analyse([("g2", 4.5, spread, "a"), ("app-store", 3.7, spread, "b")])
        self.assertNotIn("rating_gap", self.kinds(res))

    def test_dates_bunched_in_last_90_days(self):
        recent = AS_OF - datetime.timedelta(days=30)
        res = self.analyse([("g2", 2.0, recent, "a"), ("reddit", 2.0, recent, "b"),
                            ("omr", 2.0, recent, "c"),
                            ("capterra", 2.0, datetime.date(2025, 1, 1), "d")])
        self.assertEqual(self.kinds(res), ["mostly_recent"])
        self.assertEqual(res["source_bias"]["recent_share_pct"], 75.0)
        self.assertIn("75% der datierten Bewertungen stammen aus den letzten 90 Tagen "
                      "(seit 19.07.2026)", reviews.render(res, lang="de"))

    def test_dates_older_than_the_months_window(self):
        old = datetime.date(2024, 1, 1)
        res = self.analyse([("g2", 2.0, old, "a"), ("reddit", 2.0, old, "b"),
                            ("omr", 2.0, old, "c"), ("capterra", 2.0, None, "d")], months=12)
        self.assertEqual(self.kinds(res), ["mostly_old"])
        self.assertIn("100% of the dated reviews are older than 12 months", reviews.render(res))

    def test_one_source_over_60_percent_even_in_a_small_sample(self):
        res = self.analyse([("app-store", 2.0, None, "a"), ("app-store", 2.0, None, "b"),
                            ("g2", 2.0, None, "c")])
        self.assertEqual(self.kinds(res), ["one_source"])
        self.assertIsNone(res["dominant_source"])  # the old key keeps its 10-review rule
        self.assertIn("No review has a date", reviews.render(res))


class Switching(unittest.TestCase):
    """Why they leave: verbatim sentence, link, and only a named alternative."""

    def analyse(self, items, target=None, themes_path=None):
        themes, req = reviews.load_themes()
        switch = reviews.load_switching(themes_path or reviews.DEFAULT_THEMES)
        rows = rows_of([(s, r, None, t) for s, r, t in items])
        res = reviews.analyse(rows, themes, req, today=AS_OF, switch_patterns=switch,
                              target=target)
        return rows, res["switching"]

    def test_named_alternatives_are_copied_not_guessed(self):
        _, sw = self.analyse([
            ("g2", 1.0, "Way too expensive. I switched to Calendly and never looked back."),
            ("g2", 2.0, "We moved from Acme to Cal.com. Much better."),
            ("trustpilot", 1.0, "Viel zu teuer, deshalb bin ich zu Doctolib gewechselt."),
            ("trustpilot", 2.0, "Bin zu einem anderen Anbieter gewechselt."),
            ("app-store", 1.0, "Switched to the free plan and then cancelled."),
            ("reddit", None, "Looking for an alternative that has SMS reminders."),
        ])
        self.assertEqual([q["alternative"] for q in sw["away"]],
                         ["Calendly", "Cal.com", "Doctolib", None, None, None])
        self.assertEqual([(a["name"], a["count"]) for a in sw["alternatives"]],
                         [("Cal.com", 1), ("Calendly", 1), ("Doctolib", 1)])
        self.assertEqual(sw["away"][0]["quote"], "I switched to Calendly and never looked back.")

    def test_every_switch_quote_is_verbatim_and_linked(self):
        rows, sw = self.analyse([
            ("g2", 2.0, "Cancelled after the price went up again. Support never replied."),
            ("omr", None, "Abo gekündigt. Ich nutze jetzt lieber Excel."),
            ("reddit", None, "Going back to Google Calendar, this is unusable."),
        ])
        by_url = {r["url"]: r["text"] for r in rows}
        self.assertEqual(len(sw["away"]), 3)
        for q in sw["away"]:
            self.assertIn(q["quote"], by_url[q["url"]])
            if q["alternative"]:
                self.assertIn(q["alternative"], q["quote"])
        self.assertEqual([q["alternative"] for q in sw["away"]],
                         [None, "Excel", "Google Calendar"])

    def test_reasons_are_the_themes_of_the_leaving_reviews(self):
        _, sw = self.analyse([
            ("g2", 1.0, "Way too expensive, so I cancelled."),
            ("capterra", 2.0, "It crashes daily and the price is a joke. Switched to Acuity."),
            ("app-store", 1.0, "It crashes all the time."),
        ])
        reasons = {r["id"]: r["count"] for r in sw["reasons"]}
        self.assertEqual((reasons["pricing"], reasons["bugs"]), (2, 1))
        self.assertEqual(len(sw["away"]), 2)

    def test_people_coming_to_the_original_are_listed_apart(self):
        _, sw = self.analyse([
            ("g2", 5.0, "Switched from Doodle and love it."),
            ("g2", 3.0, "We switched from Doodle to Acme last year."),
            ("g2", 2.0, "We switched from Acme to Calendly last year."),
        ], target="Acme")
        self.assertEqual([q["alternative"] for q in sw["toward_original"]], [None, "Acme"])
        self.assertEqual([q["alternative"] for q in sw["away"]], ["Calendly"])

    def test_loyal_users_are_not_switchers(self):
        _, sw = self.analyse([
            ("omr", 4.0, "Ich nutze jetzt seit zwei Jahren die App."),
            ("g2", 3.0, "I now use the app every day."),
        ])
        self.assertEqual((sw["away"], sw["toward_original"]), ([], []))

    def test_old_themes_file_without_switch_patterns_uses_the_shipped_ones(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "themes.json")
            with open(reviews.DEFAULT_THEMES, encoding="utf-8") as fh:
                data = json.load(fh)
            del data["switch_patterns"]
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh)
            _, sw = self.analyse([("g2", 1.0, "Switched to Calendly.")], themes_path=path)
        self.assertEqual(sw["away"][0]["alternative"], "Calendly")

    def test_report_section(self):
        _, sw = self.analyse([("g2", 1.0, "Way too expensive. Switched to Calendly.")])
        text = "\n".join(reviews.render_switching(sw, reviews.TEXT["en"], "en"))
        self.assertIn("## Why they leave", text)
        self.assertIn('- "Switched to Calendly." (g2, 1*, named: Calendly) https://g2.example/0',
                      text)
        self.assertIn("Where they say they went: Calendly (1).", text)
        self.assertIn("Price and value (1)", text)
        _, sw = self.analyse([("g2", 1.0, "Too expensive.")])
        de = "\n".join(reviews.render_switching(sw, reviews.TEXT["de"], "de"))
        self.assertIn("## Warum sie gehen", de)
        self.assertIn("Keine Bewertung sagt, dass jemand gewechselt", de)

    def test_no_patterns_means_not_checked_not_none_found(self):
        themes, req = reviews.load_themes()
        res = reviews.analyse(rows_of([("g2", 1.0, None, "Switched to Calendly.")]), themes, req,
                              today=AS_OF)
        self.assertIsNone(res["switching"])
        self.assertNotIn("Why they leave", reviews.render(res))

    def test_name_in(self):
        self.assertEqual(reviews.name_in("Cal.com. Never again"), "Cal.com")
        self.assertEqual(reviews.name_in("Google Calendar and never"), "Google Calendar")
        self.assertIsNone(reviews.name_in("the free plan"))
        self.assertIsNone(reviews.name_in("3 different apps before"))
        self.assertIsNone(reviews.name_in("Konkurrenten gewechselt"))
        self.assertIsNone(reviews.name_in("Dark Mode."))
        self.assertEqual(reviews.name_in("123FormBuilder now"), "123FormBuilder")

    def test_ordinary_ui_and_booking_words_are_not_leaving(self):
        switch = reviews.load_switching()
        for text in ("The salon cancelled my appointment twice.",
                     "Moving to the next week in the calendar takes forever.",
                     "Please let me switch to Dark Mode.",
                     "I moved to Berlin and the app has no German.",
                     "I cancelled the booking in the app and still got a reminder.",
                     "I unsubscribed from the newsletter.",
                     "Uninstalling and reinstalling did not help."):
            self.assertIsNone(reviews.find_switch(text, switch), text)

    def test_numbers_and_common_nouns_are_not_alternatives(self):
        _, sw = self.analyse([
            ("g2", 2.0, "I switched to 3 different apps before this one."),
            ("trustpilot", 1.0, "Ich bin zu Konkurrenten gewechselt."),
            ("g2", 1.0, "We moved to Strähnwerk."),
        ])
        self.assertEqual([q["alternative"] for q in sw["away"]], [None, None, "Strähnwerk"])
        self.assertEqual([a["name"] for a in sw["alternatives"]], ["Strähnwerk"])


class Verify(unittest.TestCase):
    """--verify: a report's linked quotes must stand word for word in the reviews."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.csv = os.path.join(self.tmp.name, "reviews.csv")
        write_csv(self.csv, ROWS + GERMAN)
        self.rows, _, _ = reviews.load_reviews(self.csv, dedupe=False)

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, report):
        return reviews.verify(report, self.rows)

    def test_verbatim_quotes_pass_paraphrases_and_unknown_links_fail(self):
        res = self.check("\n".join([
            '- "Way too expensive for what it is." (app-store, 1*) https://apps.apple.com/r/1',
            '- „Viel zu teuer für das, was man bekommt.“ [Trustpilot](https://de.trustpilot.com/r/1)',
            '- "...Support never replied..." https://play.google.com/r/9',
            '- "Way too expensive for small teams." https://apps.apple.com/r/1',
            '- "Way too expensive for what it is." https://example.com/elsewhere',
            'Search for "X alternative" first.',
        ]))
        self.assertEqual((res["checked"], res["ok"]), (5, 3))
        self.assertEqual([(p["line"], p["problem"]) for p in res["problems"]],
                         [(4, "not_found"), (5, "unknown_url")])

    def test_meaning_flips_inside_a_word_fail(self):
        rows = rows_of([("g2", 1.0, None, "The support is unhelpful and slow to close tickets."),
                        ("g2", 2.0, None, "The app is slowly getting better.")])
        support, app = rows[0]["url"], rows[1]["url"]
        res = reviews.verify("\n".join([
            '- "helpful and slow" %s' % support,
            '- "The support is ... helpful" %s' % support,
            '- "app is slow" %s' % app,
            '- "The support is unhelpful" %s' % support,
            '- "...nhelpful and slow..." %s' % support,
            '- "The app is ... getting better" %s' % app,
        ]), rows)
        self.assertEqual([p["line"] for p in res["problems"]], [1, 2, 3])
        self.assertEqual(res["ok"], 3)

    def test_left_out_words_must_keep_their_order(self):
        url = "https://www.g2.com/r/3"
        self.assertEqual(self.check('"Overpriced per seat. ... buffer times" %s' % url)["ok"], 1)
        self.assertEqual(self.check('"buffer times ... Overpriced" %s' % url)["ok"], 0)

    def test_generated_report_passes_its_own_check(self):
        out = os.path.join(self.tmp.name, "feedback.md")
        with redirect_stdout(io.StringIO()):
            reviews.main([self.csv, "--as-of", "2026-10-17", "--out", out])
            self.assertEqual(reviews.main([self.csv, "--verify", out]), 0)
        with open(out, encoding="utf-8") as fh:
            res = self.check(fh.read())
        self.assertGreater(res["checked"], 10)
        self.assertEqual(res["problems"], [])

    def test_cli_exit_codes_and_german(self):
        bad = os.path.join(self.tmp.name, "fixes.md")
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write('- "Viel zu billig." https://de.trustpilot.com/r/1\n')
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(reviews.main([self.csv, "--verify", bad, "--lang", "de"]), 1)
        self.assertIn("Zeile 1:", buf.getvalue())
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write("No quotes here.\n")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(reviews.main([self.csv, "--verify", bad]), 1)


class Segments(unittest.TestCase):
    """The reviewer segment, as the platform shows it: counted, never guessed."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.csv = os.path.join(self.tmp.name, "reviews.csv")
        rows = [("g2", "https://g2.example/%d" % i, "2026-09-01", "2", seg, text)
                for i, (seg, text) in enumerate([
                    ("Owner, 1-10 employees", "Way too expensive for a small salon."),
                    ("Owner, 1-10 employees", "The price went up again."),
                    ("Owner, 1-10 employees", "Too expensive and the app crashes."),
                    ("Receptionist", "It crashes when I open the calendar."),
                    ("", "Overpriced for what it does."),
                ])]
        write_csv(self.csv, rows, header=("source", "url", "date", "rating", "segment", "text"))
        self.themes, self.req = reviews.load_themes()
        self.kept = reviews.load_reviews(self.csv)[0]
        self.result = reviews.analyse(self.kept, self.themes, self.req, today=AS_OF)

    def tearDown(self):
        self.tmp.cleanup()

    def test_sample_by_segment_with_thin_segments(self):
        segs = {s["segment"]: (s["count"], s["thin"]) for s in self.result["by_segment"]}
        self.assertEqual(segs, {"Owner, 1-10 employees": (3, False), "Receptionist": (1, True),
                                None: (1, True)})
        self.assertIsNone(self.result["by_segment"][-1]["segment"])   # "not shown" goes last

    def test_themes_per_segment(self):
        pricing = next(t for t in self.result["themes"] if t["id"] == "pricing")
        self.assertEqual([(s["segment"], s["count"]) for s in pricing["segments"]],
                         [("Owner, 1-10 employees", 3), (None, 1)])
        text = reviews.render(self.result)
        self.assertIn("## Sample by segment", text)
        self.assertIn("| Receptionist (thin) | 1 | 20% | 2.0 |", text)
        self.assertIn("- Who says it: Owner, 1-10 employees (3), not shown (1).", text)
        de = reviews.render(self.result, lang="de")
        self.assertIn("- Wer das sagt: Owner, 1-10 employees (1), Receptionist (1, dünn).", de)

    def test_no_segment_column_means_no_segment_section(self):
        res = reviews.analyse(rows_of([("g2", 1.0, None, "Too expensive.")]), self.themes,
                              self.req, today=AS_OF)
        self.assertIsNone(res["by_segment"])
        self.assertEqual(res["themes"][0]["segments"], [])
        self.assertNotIn("segment", reviews.render(res))


class AsOf(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.csv = os.path.join(self.tmp.name, "reviews.csv")
        write_csv(self.csv, ROWS)

    def tearDown(self):
        self.tmp.cleanup()

    def run_json(self, *args):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = reviews.main([self.csv, "--json"] + list(args))
        return code, buf.getvalue()

    def test_as_of_and_the_old_today_name_give_the_same_run(self):
        code, a = self.run_json("--as-of", "2026-10-17")
        _, b = self.run_json("--today", "2026-10-17")
        self.assertEqual(code, 0)
        self.assertEqual(a, b)
        self.assertEqual(json.loads(a)["as_of"], "2026-10-17")

    def test_bad_as_of_is_refused(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(reviews.main([self.csv, "--as-of", "17.10.2026"]), 2)

    def test_a_run_without_as_of_says_so(self):
        _, fixed = self.run_json("--as-of", "2026-10-17")
        _, today = self.run_json()
        self.assertNotIn("as_of_today", json.loads(fixed))
        self.assertTrue(json.loads(today)["as_of_today"])
        for lang, words in (("en", "No --as-of was given"), ("de", "Ohne --as-of")):
            for args, seen in ((["--as-of", "2026-10-17"], False), ([], True)):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    reviews.main([self.csv, "--lang", lang] + args)
                self.assertEqual(words in buf.getvalue(), seen, (lang, args))

    def test_json_goes_to_out_as_utf8(self):
        out = os.path.join(self.tmp.name, "feedback.json")
        with redirect_stdout(io.StringIO()) as buf:
            self.assertEqual(reviews.main([self.csv, "--json", "--as-of", "2026-10-17",
                                           "--out", out]), 0)
        self.assertEqual(buf.getvalue(), "wrote %s\n" % out)
        with open(out, encoding="utf-8") as fh:
            self.assertEqual(json.load(fh)["as_of"], "2026-10-17")

    def test_json_only_adds_keys(self):
        data = json.loads(self.run_json("--as-of", "2026-10-17")[1])
        for key in ("reviews", "sources", "rated", "by_source", "dominant_source", "themes",
                    "praise", "requests", "unthemed_negative", "dropped", "duplicates",
                    "as_of", "source_bias", "switching", "by_segment"):
            self.assertIn(key, data)
        self.assertTrue(set(data["by_source"][0]).issuperset({"source", "count", "avg_rating"}))
        self.assertEqual(set(data["switching"]),
                         {"away", "toward_original", "reasons", "alternatives"})


if __name__ == "__main__":
    unittest.main()
