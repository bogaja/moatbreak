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

battlecard = load("battlecard")
reviews = load("reviews")

AS_OF = datetime.date(2026, 10, 17)

# line 2 tie, 3 gap, 4 gap without evidence, 5 differentiator (pipe in the name),
# 6 stale differentiator, 7 own feature not done, 8 unknown original, 9 skip,
# 10 gap with a private source, 11 bad checked date
MATRIX = """feature,area,priority,original,clone,effort,notes,source,checked
Pick a time slot,booking,must,yes,yes,M,,https://help.x.com/slots,2026-10-01
Reschedule link,booking,must,yes,no,M,,https://help.x.com/reschedule,2026-09-20
Round-robin,team,should,yes,no,L,,,
SMS | WhatsApp reminders,notifications,should,no,yes,M,ours,https://help.x.com/notify,2026-10-02
Waitlist,booking,could,partial,yes,S,,https://help.x.com/waitlist,2026-03-01
Deposit at booking,payments,must,no,partial,M,ours,,
Stylist levels,team,should,?,yes,S,niche,,
Their marketplace,integrations,could,yes,skip,XL,their network,,
Calendar sync,integrations,must,ja,teilweise,L,,teardown/screens/S04.png,2026-10-01
Analytics,reports,could,yes,yes,M,,https://help.x.com/analytics,soon
"""


def quote(n, rating=1):
    return {"quote": "quote %d" % n, "url": "https://example.com/r/%d" % n,
            "source": "g2", "rating": rating}


def theme(id_, kind="complaint", count=5, thin=False, label=None):
    return {"id": id_, "label": label or {"en": id_.title(), "de": id_.upper()}, "kind": kind,
            "score": float(count), "count": count, "share_pct": 10.0, "avg_rating": 1.5,
            "sources": ["g2", "app-store"], "thin": thin,
            "quotes": [quote(count * 10 + i) for i in range(3)]}


FEEDBACK = {
    "reviews": 40, "sources": ["app-store", "g2"], "rated": 38, "by_source": [],
    "dominant_source": {"source": "g2", "share_pct": 70.0},
    "themes": [theme("pricing", count=12), theme("integrations", kind="request", count=9),
               theme("bugs", count=8), theme("support", count=2, thin=True),
               theme("ux", count=4), theme("data", count=3), theme("ads", count=2)],
    "praise": [{"id": "performance", "label": {"en": "Fast, no waiting", "de": "Schnell"},
                "count": 6, "sources": ["g2"], "quotes": [quote(900, 5)]}],
    "requests": [], "unthemed_negative": [], "dropped": 2, "duplicates": 1,
}


def write(d, name, text):
    path = os.path.join(d, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = battlecard.main(argv)
    return code, out.getvalue(), err.getvalue()


class Card(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.rows = battlecard.parity.load(write(self.tmp.name, "features.csv", MATRIX))
        self.card = battlecard.build(FEEDBACK, self.rows, "Calendly", "Slotty", AS_OF)

    def tearDown(self):
        self.tmp.cleanup()

    def lines(self, key):
        return [i["line"] for i in self.card[key]]

    def test_rows_are_sorted_into_the_right_lists(self):
        self.assertEqual(self.lines("differentiators"), [5, 6])     # should before could
        self.assertEqual(self.lines("gaps"), [3, 10, 4])            # must, open first
        self.assertEqual(self.lines("unchecked"), [8])
        self.assertEqual(self.lines("not_yet"), [7])

    def test_tags(self):
        tags = {i["line"]: i["tag"] for i in self.card["gaps"] + self.card["differentiators"]
                + self.card["unchecked"]}
        self.assertEqual(tags[3]["status"], "verified")
        self.assertFalse(tags[3]["stale"])
        self.assertEqual((tags[6]["status"], tags[6]["stale"]), ("verified", True))
        self.assertEqual(tags[4]["missing"], ["source", "checked"])
        self.assertEqual(tags[8]["missing"], ["unknown", "source", "checked"])
        self.assertFalse(tags[10]["public"])

    def test_page_only_takes_verified_fresh_public_rows(self):
        page = self.card["page"]
        self.assertEqual([i["line"] for i in page["rows"]], [2, 3, 5])
        self.assertEqual((page["wins"], page["losses"], page["ties"]), (1, 1, 1))
        self.assertEqual(page["lopsided"], 0)
        why = {i["line"]: i["why"] for i in page["excluded"]}
        self.assertEqual(why[6], ["stale"])
        self.assertEqual(why[10], ["private"])
        self.assertEqual(why[11], ["checked"])
        self.assertNotIn(9, why)                                  # skip rows are no claims

    def test_page_with_only_wins_warns(self):
        rows = battlecard.parity.load(write(self.tmp.name, "wins.csv", (
            "feature,priority,original,clone,source,checked\n"
            "SMS,should,no,yes,https://help.x.com/n,2026-10-01\n"
            "Reschedule,must,yes,no,,\n")))
        card = battlecard.build(None, rows, "Calendly", "Slotty", AS_OF)
        self.assertEqual(card["page"]["lopsided"], 1)
        self.assertIn("§ 5a UWG", battlecard.render(card))

    def test_weak_is_top_complaints_with_two_linked_quotes(self):
        weak = self.card["weak"]
        self.assertEqual([t["id"] for t in weak], ["pricing", "bugs", "support", "ux", "data"])
        self.assertTrue(all(len(t["quotes"]) == 2 for t in weak))
        self.assertEqual([t["id"] for t in self.card["asked"]], ["integrations"])
        text = battlecard.render(self.card)
        self.assertIn('- "quote 120" (g2, 1*) https://example.com/r/120', text)
        self.assertNotIn("quote 122", text)                       # third quote left out
        self.assertIn("**Support** (thin) [reported: 2 reviews, 2 sources, avg 1.5 stars]", text)

    def test_strong_comes_from_praise(self):
        text = battlecard.render(self.card)
        strong = text.split("## Where they are strong")[1].split("##")[0]
        self.assertIn("**Fast, no waiting** [reported: 6 reviews, 1 source]", strong)
        self.assertIn("https://example.com/r/900", strong)
        # the rep gets a line to say the praise in plain words, not only a label and a quote
        self.assertIn("  - In plain words: to write: what customers praise Calendly for here", strong)
        self.assertIn("- Fast, no waiting: praised in 6 reviews (feedback.json praise/performance)",
                      text)

    def test_swot_lines_name_their_source(self):
        text = battlecard.render(self.card)
        swot = text.split("## SWOT")[1].split("## For a comparison page")[0]
        for line in swot.splitlines():
            if line.startswith("- ") and line != "- none in the data":
                self.assertRegex(line, r"\((features\.csv line \d+|feedback\.json \w+/\w+)\)")
        self.assertIn("- [must] Calendar sync: Calendly yes, Slotty partial (features.csv line 10)",
                      swot)
        self.assertEqual(self.card["swot"]["strengths"], ["features.csv:5", "features.csv:6"])
        self.assertIn("themes/integrations", self.card["swot"]["opportunities"])

    def test_objections_are_stubs_to_write(self):
        kinds = [o["kind"] for o in self.card["objections"]]
        self.assertEqual(kinds, ["gap", "gap", "gap", "praise"])
        self.assertTrue(all(o["answer"] is None for o in self.card["objections"]))
        text = battlecard.render(self.card)
        block = text.split("## Objection handling")[1].split("## Prices")[0]
        self.assertEqual(block.count("Answer: to write"), 4)
        self.assertIn('"Calendly has this: Reschedule link. Does Slotty?"', block)
        # the tag sits with the claim about them, not after our own status
        self.assertIn("Data: features.csv line 3; Calendly: yes [verified, checked 2026-09-20: "
                      "https://help.x.com/reschedule]; Slotty: no. Answer: to write", block)
        self.assertIn("Calendly: yes [assumed: no source, no checked date]; Slotty: no.", block)

    def test_rendered_card(self):
        text = battlecard.render(self.card)
        self.assertIn("| should | SMS \\| WhatsApp reminders | no | [verified, checked "
                      "2026-10-02: https://help.x.com/notify] | 5 |", text)
        self.assertIn("Check first: Slotty has it, nobody checked Calendly: Stylist levels "
                      "(line 8).", text)
        self.assertIn("Deposit at booking (line 7, partial)", text)
        self.assertIn("Ahead: Slotty 1, Calendly 1; equal: 1.", text)
        self.assertIn("- stale, recheck: Waitlist (line 6)", text)
        self.assertIn("claims about Calendly: 5 verified (1 stale), 4 assumed.", text)
        self.assertIn("Checked between 2026-03-01 and 2026-10-02.", text)
        self.assertIn("70% of the reviews come from g2", text)
        self.assertIn("line 11: checked 'soon' is not a date", text)
        self.assertNotIn("Their marketplace", text)

    def test_german(self):
        text = battlecard.render(battlecard.build(FEEDBACK, self.rows, "Calendly", "Slotty",
                                                  AS_OF, lang="de"), lang="de")
        self.assertIn("# Battle Card: Slotty gegen Calendly", text)
        self.assertIn("**PRICING** [berichtet: 12 Bewertungen, 2 Quellen, Ø 1,5 Sterne]", text)
        self.assertIn("[geprüft am 20.09.2026: https://help.x.com/reschedule]", text)
        self.assertIn("Antwort: zu schreiben", text)
        self.assertIn("- [Muss] Reschedule link: Calendly ja, Slotty nein (features.csv Zeile 3)",
                      text)
        self.assertNotIn("to write", text)

    def test_missing_input_is_not_researched(self):
        only_features = battlecard.render(battlecard.build(None, self.rows, "A", "B", AS_OF))
        self.assertIn("Not researched: run voice of customer", only_features)
        only_feedback = battlecard.render(battlecard.build(FEEDBACK, None, "A", "B", AS_OF))
        self.assertIn("Not researched: no features.csv", only_feedback)
        self.assertIn('"We are happy with A."', only_feedback)


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_quotes_are_verbatim_from_the_review_rows(self):
        rows = [
            ("app-store", "https://apps.apple.com/r/1", "2026-08-01", "1",
             "Way too expensive for what it is. I wish it had SMS reminders."),
            ("g2", "https://www.g2.com/r/2", "2026-07-01", "2", "Overpriced per seat."),
            ("capterra", "https://www.capterra.com/r/3", "2026-07-02", "1",
             "It crashes every time I open the calendar view."),
            ("app-store", "https://apps.apple.com/r/4", "2026-08-10", "5",
             "Love it. Support is fast and friendly."),
        ]
        src = os.path.join(self.tmp.name, "reviews.csv")
        with open(src, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(("source", "url", "date", "rating", "text"))
            w.writerows(rows)
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(reviews.main([src, "--json", "--today", "2026-10-17"]), 0)
        fb = write(self.tmp.name, "feedback.json", buf.getvalue())
        feats = write(self.tmp.name, "features.csv", MATRIX)
        out = os.path.join(self.tmp.name, "battlecard.md")
        code, stdout, _ = run(["--feedback", fb, "--features", feats, "--target", "X",
                               "--ours", "Y", "--as-of", "2026-10-17", "--out", out])
        self.assertEqual(code, 0)
        self.assertIn("wrote", stdout)
        with open(out, encoding="utf-8") as fh:
            text = fh.read()
        by_url = {r[1]: r[4] for r in rows}
        found = re.findall(r'- "(.+?)" \([^)]*\) (https://\S+)$', text, re.M)
        self.assertTrue(found)
        for q, url in found:
            self.assertIn(q, by_url[url])

    def test_json(self):
        feats = write(self.tmp.name, "features.csv", MATRIX)
        code, stdout, _ = run(["--features", feats, "--target", "X", "--ours", "Y",
                               "--as-of", "2026-10-17", "--json"])
        self.assertEqual(code, 0)
        data = json.loads(stdout)
        self.assertEqual(data["as_of"], "2026-10-17")
        self.assertFalse(data["has_feedback"])
        self.assertEqual(data["claims"]["verified"], 5)

    def test_errors(self):
        feats = write(self.tmp.name, "features.csv", MATRIX)
        md = write(self.tmp.name, "feedback.md", "# not json\n")
        other = write(self.tmp.name, "other.json", '{"score": 80}')
        base = ["--target", "X", "--ours", "Y"]
        self.assertEqual(run(base)[0], 2)
        self.assertEqual(run(base + ["--feedback", md])[0], 2)
        self.assertEqual(run(base + ["--feedback", other])[0], 2)
        self.assertEqual(run(base + ["--features", feats, "--as-of", "17.10.2026"])[0], 2)
        self.assertEqual(run(base + ["--features", os.path.join(self.tmp.name, "nope.csv")])[0], 2)

    def test_unquoted_comma_in_notes_is_an_error_not_a_crash(self):
        feats = write(self.tmp.name, "commas.csv", (
            "feature,area,priority,original,clone,effort,notes,source,checked\n"
            "Online booking,core,must,yes,yes,3,Note, with a comma,https://x.com/f,2026-09-01\n"))
        code, _, err = run(["--features", feats, "--target", "X", "--ours", "Y"])
        self.assertEqual(code, 2)
        self.assertIn("line 2 has more fields than the header", err)


if __name__ == "__main__":
    unittest.main()
