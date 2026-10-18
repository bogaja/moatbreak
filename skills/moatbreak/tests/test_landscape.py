import io
import json
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout, redirect_stderr

from _load import load, ROOT

landscape = load("landscape")

HEADER = ("name,url,evidence_url,category,customer,market,languages,price_from,price_model,"
          "price_url,axis_x,axis_y,axis_url,status,read_on,notes\n")

# "Aaa Memory" sorts first by name, but has no evidence link, so it must come last.
CSV = HEADER + """\
Salonia,https://salonia.test/,https://salonia.test/friseur,Online-Terminbuchung,Friseursalons,"DE, AT",de,ab 29 € / Monat,pro Standort netto,https://salonia.test/preise,3,7,https://salonia.test/funktionen,fit,2026-10-17,booking for salons only
Haarzeit,https://haarzeit.test/,https://haarzeit.test/,Kasse und Termine,Friseure,DACH,"de, en",kostenlos,Freemium,https://haarzeit.test/preise,4,5,https://haarzeit.test/,confirmed,2026-10-17,POS plus booking
BookAll,https://bookall.test/,https://bookall.test/,Booking software,any service business,global,en,12,per seat,,2,8,,adjacent,2026-10-16,generic booking tool
Aaa Memory,https://memory.test/,,Terminbuchung,Friseure,DE,de,19,,,1,6,,confirmed,,known from general knowledge only
US Cuts,https://uscuts.test/,https://uscuts.test/,Salon booking,Salons,US,en,25,,https://uscuts.test/pricing,5,4,https://uscuts.test/,fit,2026-10-16,US only
OldSalon,https://old.test/,https://old.test/,Terminbuchung,Friseure,DE,de,,,,,,,out,2026-10-16,inactive: last changelog 2023-04
NoReason,https://noreason.test/,https://noreason.test/,,,DE,,,,,,,,out,,
Ours,,,,,,,15,,,6,8,,planned,,our target
Sample,https://booking.example/,https://booking.example/x,,,,,,,,,,,fit,,
SALONIA,https://salonia.test/,https://salonia.test/,,,,,,,,,,,fit,,
"""


def write(d, name, text):
    path = os.path.join(d, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def fit_row(name, market="DE"):
    return "%s,https://%s.test/,https://%s.test/x,,,%s,,,,,,,,fit,,\n" % (
        name, name.lower(), name.lower(), market)


class Analyse(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = write(self.tmp.name, "competitors.csv", CSV)
        self.rows, self.fields = landscape.load(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def names(self, result):
        return [r["name"] for r in result["rows"]]

    def test_unverified_is_never_first_and_never_proposed(self):
        r = landscape.analyse(self.rows, market="DACH")
        self.assertEqual(self.names(r)[-1], "Aaa Memory")
        self.assertNotIn("Aaa Memory", r["proposal"])
        self.assertEqual(r["counts"]["unverified"], 1)
        self.assertTrue(any("Aaa Memory is marked confirmed but has no evidence_url" in p
                            for p in r["problems"]))

    def test_verified_in_market_first_then_status(self):
        r = landscape.analyse(self.rows, market="DACH")
        self.assertEqual(self.names(r), ["Haarzeit", "Salonia", "BookAll", "US Cuts",
                                         "Aaa Memory"])

    def test_proposal_is_verified_fit_or_confirmed_in_the_users_market(self):
        r = landscape.analyse(self.rows, market="DACH")
        self.assertEqual(r["proposal"], ["Haarzeit", "Salonia"])
        self.assertEqual(r["confirmed"], ["Haarzeit"])
        self.assertTrue(any("US Cuts is marked fit, but its market 'US' does not include DACH"
                            in p for p in r["problems"]))

    def test_without_market_every_verified_fit_is_proposed(self):
        r = landscape.analyse(self.rows)
        self.assertEqual(r["proposal"], ["Haarzeit", "Salonia", "US Cuts"])

    def test_row_without_market_is_not_proposed_when_market_is_checked(self):
        rows, _ = landscape.load(write(self.tmp.name, "m.csv", HEADER + fit_row("Nomarket", "")))
        r = landscape.analyse(rows, market="DE")
        self.assertEqual(r["proposal"], [])
        self.assertIn("has no market", r["problems"][0])

    def test_proposal_is_capped_at_five(self):
        text = HEADER + "".join(fit_row("P%d" % i) for i in range(7))
        rows, _ = landscape.load(write(self.tmp.name, "many.csv", text))
        r = landscape.analyse(rows, market="DACH")
        self.assertEqual(len(r["proposal"]), 5)

    def test_out_planned_duplicates_and_sample(self):
        r = landscape.analyse(self.rows)
        self.assertEqual([x["name"] for x in r["out"]], ["NoReason", "OldSalon"])
        self.assertEqual([x["name"] for x in r["planned"]], ["Ours"])
        self.assertNotIn("Sample", self.names(r))
        self.assertNotIn("SALONIA", self.names(r))
        joined = "\n".join(r["problems"])
        self.assertIn("SALONIA is already on line 2, dropped", joined)
        self.assertIn("Sample is the sample row (.example), dropped", joined)

    def test_problems_are_sorted_by_line(self):
        r = landscape.analyse(self.rows, market="DACH", axes=("axis_x", "axis_y"))
        lines = [int(p.split()[1].rstrip(":")) for p in r["problems"]]
        self.assertEqual(lines, sorted(lines))

    def test_bad_values_are_reported_not_fatal(self):
        text = HEADER + ("Odd,https://odd.test/,not-a-link,,,DE,,9,,,,,,maybe,17.10.2026,\n")
        rows, _ = landscape.load(write(self.tmp.name, "odd.csv", text))
        r = landscape.analyse(rows)
        joined = "\n".join(r["problems"])
        self.assertIn("evidence_url 'not-a-link' is not an http(s) link", joined)
        self.assertIn("status 'maybe'", joined)
        self.assertIn("read_on '17.10.2026'", joined)
        self.assertIn("Odd has a price but no price_url", joined)
        self.assertFalse(r["rows"][0]["verified"])
        self.assertEqual(r["rows"][0]["status"], "candidate")

    def test_a_guessed_price_is_flagged_in_every_row(self):
        text = HEADER + (
            'Bookily,https://bookily.test/,https://bookily.test/a,,,AT,,"ab 19,90 € / Monat '
            '(jährlich; monatlich vermutlich 29,90 €)",,https://bookily.test/p,,,,adjacent,,\n'
            "Tilda,https://tilda.test/,https://tilda.test/a,,,AT,,ca. 25 €,,https://tilda.test/p,"
            ",,,out,,too broad\n"
            "Mira,https://mira.test/,https://mira.test/a,,,AT,,~30 EUR,netto?,https://mira.test/p,"
            ",,,fit,,\n"
            "Clean,https://clean.test/,https://clean.test/a,,,AT,,ab 18 € / Monat netto,"
            "pro Standort,https://clean.test/p,,,,fit,,\n")
        rows, _ = landscape.load(write(self.tmp.name, "guess.csv", text))
        joined = "\n".join(landscape.analyse(rows)["problems"])
        self.assertIn("Bookily price_from", joined)
        self.assertIn("has 'vermutlich', a guess", joined)
        self.assertIn("Tilda price_from 'ca. 25 €' has 'ca.'", joined)
        self.assertIn("Mira price_from '~30 EUR' has '~'", joined)
        self.assertIn("Mira price_model 'netto?' has '?'", joined)
        self.assertNotIn("Clean", joined)
        de = "\n".join(landscape.analyse(rows, lang="de")["problems"])
        self.assertIn("enthält 'vermutlich', eine Vermutung", de)

    def test_german_values_and_semicolons(self):
        text = ("name;url;evidence_url;market;price_from;price_url;status;notes\n"
                "Termino;https://termino.test/;https://termino.test/a;DE;29,90;"
                "https://termino.test/p;bestätigt;passt\n"
                "Kalendo;https://kalendo.test/;https://kalendo.test/a;Österreich;;;passt;\n"
                "Alt;https://alt.test/;https://alt.test/;DE;;;raus;eingestellt\n")
        rows, _ = landscape.load(write(self.tmp.name, "de.csv", text))
        r = landscape.analyse(rows, lang="de", market="DACH")
        self.assertEqual(r["proposal"], ["Termino", "Kalendo"])
        self.assertEqual(r["confirmed"], ["Termino"])
        self.assertEqual(r["problems"], [])
        md = landscape.render(r, lang="de", title="Buchungs-App für Friseure")
        self.assertIn("# Marktüberblick: Buchungs-App für Friseure", md)
        self.assertIn("## Marktmatrix", md)
        self.assertIn("- [x] [Termino](https://termino.test/)", md)
        self.assertIn("- Alt: eingestellt", md)
        self.assertIn("Für die Analyse bestätigt: Termino", md)


class Parsing(unittest.TestCase):
    def test_parse_number(self):
        cases = {"29": 29.0, "ab 29 € / Monat": 29.0, "29,90": 29.9, "29.90 EUR": 29.9,
                 "1.200": 1200.0, "1'200 CHF": 1200.0, "1,200": 1200.0, "1.234,56": 1234.56,
                 "1,234.56": 1234.56, "29,- €": 29.0, "kostenlos": 0.0,
                 "Free up to 2 staff": 0.0, "29 € (14 Tage kostenlos testen)": 29.0,
                 "4,6 / 5": 4.6, "auf Anfrage": None, "": None}
        for text, want in cases.items():
            self.assertEqual(landscape.parse_number(text), want, text)

    def test_parse_market(self):
        pm = landscape.parse_market
        self.assertEqual(pm("DACH"), {"DE", "AT", "CH"})
        self.assertEqual(pm("D-A-CH"), {"DE", "AT", "CH"})
        self.assertEqual(pm("Deutschland und Österreich"), {"DE", "AT"})
        self.assertEqual(pm("nur in DE"), {"DE"})
        self.assertEqual(pm("de, at"), {"DE", "AT"})
        self.assertEqual(pm("IN"), {"IN"})
        self.assertIn("DE", pm("EU"))
        self.assertNotIn("CH", pm("EU"))
        self.assertEqual(pm("weltweit"), {"*"})
        self.assertEqual(pm(""), set())
        for dach in ("D/A/CH", "D, A, CH", "DE-AT-CH", "d / a / ch"):
            self.assertEqual(pm(dach), {"DE", "AT", "CH"}, dach)

    def test_covers(self):
        dach = landscape.parse_market("DACH")
        self.assertTrue(landscape.covers({"DE"}, dach))
        self.assertTrue(landscape.covers({"*"}, dach))
        self.assertTrue(landscape.covers(landscape.parse_market("EU"), dach))
        self.assertFalse(landscape.covers({"US"}, dach))
        self.assertIsNone(landscape.covers(set(), dach))

    def test_axis_url_with_two_pages(self):
        row = {"price_url": "https://a.test/p", "evidence_url": "https://a.test/e",
               "axis_url": "https://a.test/x https://capterra.test/y"}
        self.assertEqual(landscape.axis_source(row, "axis_x"), "https://a.test/x")
        self.assertEqual(landscape.axis_source(row, "axis_y"), "https://capterra.test/y")
        self.assertEqual(landscape.axis_source(row, "price_from"), "https://a.test/p")
        row["axis_url"] = "https://a.test/both"
        self.assertEqual(landscape.axis_source(row, "axis_y"), "https://a.test/both")

    def test_ticks_start_at_zero_and_leave_headroom(self):
        self.assertEqual(landscape.ticks([0.0, 29.0]), [0, 10, 20, 30])
        t = landscape.ticks([8.0, 5.0])
        self.assertEqual(t[0], 0)
        self.assertGreater(t[-1], 8.0)
        self.assertEqual(len(landscape.ticks([3.0, 3.0])) > 1, True)


class Render(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        rows, _ = landscape.load(write(self.tmp.name, "c.csv", CSV))
        self.result = landscape.analyse(rows, market="DACH", axes=("price_from", "axis_y"))
        self.labels = ("Price from (EUR/month)", "Core jobs on website (of 8)")

    def tearDown(self):
        self.tmp.cleanup()

    def test_matrix_links_every_sourced_cell_and_marks_the_rest(self):
        md = landscape.render(self.result, labels=self.labels)
        self.assertIn("[ab 29 € / Monat](https://salonia.test/preise)", md)
        self.assertIn("12 (no source)", md)
        self.assertIn("| **unverified** |", md)
        self.assertIn("US (not in DACH)", md)
        self.assertIn("[7](https://salonia.test/funktionen)", md)
        self.assertIn("- NoReason: no reason given, add one", md)
        self.assertIn("- OldSalon: inactive: last changelog 2023-04", md)
        self.assertIn("Verified and fit: only 2", md)
        # price_from is already a matrix column: the axis label is not added twice
        self.assertNotIn("Price from (EUR/month)", md)
        self.assertIn("Core jobs on website (of 8)", md)

    def test_no_proposal_without_a_verified_fit(self):
        rows, _ = landscape.load(write(self.tmp.name, "u.csv", HEADER +
                                       "Lead,https://lead.test/,,,,DE,,,,,,,,fit,,\n"))
        md = landscape.render(landscape.analyse(rows))
        self.assertIn("Nothing to propose yet", md)

    def test_map_points_and_unplotted_rows(self):
        m = self.result["map"]
        names = [p["name"] for p in m["points"]]
        self.assertIn("Ours", names)
        self.assertNotIn("OldSalon", names)
        by = {p["name"]: p for p in m["points"]}
        self.assertTrue(by["Salonia"]["sourced"])
        self.assertFalse(by["BookAll"]["sourced"])      # no price_url, no axis_url
        self.assertFalse(by["Aaa Memory"]["sourced"])   # no evidence_url
        self.assertTrue(by["Ours"]["sourced"])          # a plan, drawn as a plan
        self.assertEqual(by["Haarzeit"]["x"], 0.0)      # "kostenlos"
        self.assertEqual(m["not_plotted"], [])

    def test_svg_is_valid_deterministic_and_labelled(self):
        rows, _ = landscape.load(write(self.tmp.name, "amp.csv", CSV.replace(
            "BookAll,", "Book & <All>,")))
        result = landscape.analyse(rows, market="DACH", axes=("price_from", "axis_y"))
        svg = landscape.render_svg(result["map"], title="Salons", labels=self.labels)
        self.assertEqual(svg, landscape.render_svg(result["map"], title="Salons",
                                                   labels=self.labels))
        root = ET.fromstring(svg)
        texts = [t.text for t in root.iter("{http://www.w3.org/2000/svg}text")]
        self.assertIn("Price from (EUR/month)", texts)
        self.assertIn("Core jobs on website (of 8)", texts)
        self.assertIn("Book & <All>", texts)
        self.assertIn("Positioning map: Salons", texts)
        self.assertIn("no source, not a finding", texts)
        self.assertIn("planned (yours)", texts)
        self.assertIn('stroke-dasharray="3 2"', svg)
        self.assertIn("<polygon", svg)

    def test_svg_in_german_uses_decimal_comma(self):
        rows, _ = landscape.load(write(self.tmp.name, "dec.csv", HEADER + (
            "A,https://a.test/,https://a.test/,,,DE,,,,,0.5,1.5,https://a.test/f,fit,,\n"
            "B,https://b.test/,https://b.test/,,,DE,,,,,1.25,0.25,https://b.test/f,fit,,\n")))
        result = landscape.analyse(rows, lang="de", axes=("axis_x", "axis_y"))
        svg = landscape.render_svg(result["map"], lang="de")
        self.assertIn(">0,5<", svg)
        self.assertIn("Positionierungskarte", svg)


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = write(self.tmp.name, "competitors.csv", CSV)

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = landscape.main(args)
        return code, out.getvalue(), err.getvalue()

    def test_writes_report_and_map(self):
        md = os.path.join(self.tmp.name, "landscape.md")
        svg = os.path.join(self.tmp.name, "landscape.svg")
        code, out, _ = self.run_main([self.path, "--lang", "de", "--market", "DACH",
                                      "--svg", svg, "--x", "price_from", "--y", "axis_y",
                                      "--x-label", "Preis ab", "--y-label", "Kernaufgaben",
                                      "--out", md])
        self.assertEqual(code, 0)
        self.assertIn("wrote %s" % svg, out)
        with open(md, encoding="utf-8") as fh:
            self.assertIn("## Marktmatrix", fh.read())
        with open(svg, encoding="utf-8") as fh:
            ET.fromstring(fh.read())

    def test_json(self):
        code, out, _ = self.run_main([self.path, "--json", "--market", "DACH"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["proposal"], ["Haarzeit", "Salonia"])
        self.assertEqual(data["rows"][-1]["name"], "Aaa Memory")

    def test_errors(self):
        nocol = write(self.tmp.name, "nocol.csv", "name,url\nX,https://x.test/\n")
        self.assertEqual(self.run_main([nocol])[0], 2)
        svg = os.path.join(self.tmp.name, "m.svg")
        self.assertEqual(self.run_main([self.path, "--svg", svg, "--x", "rating"])[0], 2)
        empty = write(self.tmp.name, "nonum.csv", HEADER + fit_row("Nonum"))
        self.assertEqual(self.run_main([empty, "--svg", svg])[0], 2)
        self.assertFalse(os.path.exists(svg))
        self.assertEqual(self.run_main([self.path, "--market", "somewhere"])[0], 2)

    def test_custom_numeric_column_for_the_map(self):
        csv_ = write(self.tmp.name, "seats.csv", HEADER.replace(",notes\n", ",notes,seats\n") +
                     "A,https://a.test/,https://a.test/x,,,DE,,,,,,3,https://a.test/f,fit,,,12\n"
                     "B,https://b.test/,https://b.test/x,,,DE,,,,,,5,https://b.test/f,fit,,,40\n")
        svg = os.path.join(self.tmp.name, "m.svg")
        code, _, err = self.run_main([csv_, "--svg", svg, "--x", "seats", "--y", "axis_y"])
        self.assertEqual(code, 0, err)
        rows, _ = landscape.load(csv_)
        pts = landscape.analyse(rows, axes=("seats", "axis_y"))["map"]["points"]
        self.assertEqual([(p["name"], p["x"]) for p in pts], [("A", 12.0), ("B", 40.0)])

    def test_company_facts_with_source_marks(self):
        csv_ = write(self.tmp.name, "firms.csv", HEADER.replace(
            ",notes\n", ",notes,company,seat,founded,size,company_url\n") +
            "A,https://a.test/,https://a.test/x,,,DE,,,,,,,,fit,,,A GmbH,Berlin,2019,11-50,"
            "https://a.test/impressum\n"
            "B,https://b.test/,https://b.test/x,,,DE,,,,,,,,fit,,,B AG,Wien,,,\n")
        rows, _ = landscape.load(csv_)
        result = landscape.analyse(rows, lang="de")
        md = landscape.render(result, lang="de")
        self.assertIn("## Firmen hinter den Produkten", md)
        self.assertIn("- A: Firma A GmbH, Sitz Berlin, gegründet 2019, Größe 11-50 "
                      "(Quelle: [a.test](https://a.test/impressum))", md)
        self.assertIn("- B: Firma B AG, Sitz Wien (ohne Beleg)", md)
        self.assertIn("Zeile 3: B hat Firmenangaben, aber keine company_url", md)

    def test_not_utf8_says_how_to_save(self):
        p = os.path.join(self.tmp.name, "excel.csv")
        with open(p, "wb") as fh:
            fh.write((HEADER + fit_row("Grün")).encode("cp1252"))
        code, _, err = self.run_main([p])
        self.assertEqual(code, 2)
        self.assertIn("CSV UTF-8", err)

    def test_shipped_template(self):
        path = os.path.join(ROOT, "templates", "competitors.csv")
        rows, fields = landscape.load(path)
        for col in ("name", "url", "evidence_url", "category", "customer", "market",
                    "languages", "price_from", "price_model", "price_url", "axis_x", "axis_y",
                    "axis_url", "status", "read_on", "notes", "company", "seat", "founded",
                    "size", "company_url"):
            self.assertIn(col, fields)
        r = landscape.analyse(rows)
        self.assertEqual(r["rows"], [])          # the sample row never reaches a report
        self.assertEqual(len(r["problems"]), 1)


if __name__ == "__main__":
    unittest.main()
