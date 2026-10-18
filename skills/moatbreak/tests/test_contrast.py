import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from _load import load, ROOT

contrast = load("contrast")
P = contrast.parse_colour


def ratio(fg, bg):
    return contrast.ratio(P(fg), P(bg))


class Formula(unittest.TestCase):
    def test_luminance_end_points_and_mid_grey(self):
        self.assertEqual(contrast.luminance(P("#ffffff")), 1.0)
        self.assertEqual(contrast.luminance(P("#000000")), 0.0)
        self.assertAlmostEqual(contrast.luminance(P("#808080")), 0.2158605, places=6)

    def test_known_ratios(self):
        self.assertEqual(contrast.shown(ratio("#000000", "#ffffff")), 21.0)
        self.assertEqual(contrast.shown(ratio("#ffffff", "#ffffff")), 1.0)
        self.assertEqual(contrast.shown(ratio("#767676", "#ffffff")), 4.54)
        self.assertAlmostEqual(ratio("#1a1a1a", "#ffffff"), ratio("#ffffff", "#1a1a1a"))

    def test_never_rounds_up_to_pass(self):
        r = ratio("#777777", "#ffffff")          # 4.478...
        self.assertEqual(contrast.shown(r), 4.47)
        self.assertFalse(contrast.passes(r, 4.5))
        self.assertEqual(contrast.shown(4.4999), 4.49)
        self.assertFalse(contrast.passes(4.4999, 4.5))
        self.assertTrue(contrast.passes(4.5, 4.5))

    def test_levels(self):
        res = contrast.check(P("#777777"), P("#ffffff"), "text")
        self.assertEqual(res["levels"], {"aa_text": False, "aa_large": True, "aaa_text": False,
                                         "aaa_large": False, "ui": True})
        self.assertEqual(res["good_for"], ["large", "ui"])
        self.assertFalse(res["pass"])
        res = contrast.check(P("#000000"), P("#ffffff"), "text")
        self.assertTrue(all(res["levels"].values()))
        self.assertIsNone(res["fix"])

    def test_use_sets_the_bar(self):
        fg, bg = P("#949494"), P("#ffffff")      # about 3.03
        self.assertTrue(contrast.check(fg, bg, "ui")["pass"])
        self.assertTrue(contrast.check(fg, bg, "large")["pass"])
        self.assertFalse(contrast.check(fg, bg, "text")["pass"])


class Colours(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(P("#abc"), P("#AABBCC"))
        self.assertEqual(P("rgb(26, 26, 26)"), P("#1a1a1a"))
        self.assertEqual(P("rgb(26 26 26)"), P("#1a1a1a"))
        self.assertAlmostEqual(P("#00000080")[3], 128 / 255.0)
        self.assertEqual(P("rgba(0, 0, 0, 0.5)")[3], 0.5)
        self.assertEqual(P("rgb(0 0 0 / 50%)")[3], 0.5)
        for bad in ("blue", "#12345", "rgb(300, 0, 0)", "rgba(0, 0, 0, 2)", ""):
            with self.assertRaises(contrast.InputError):
                P(bad)

    def test_transparent_foreground_is_flattened(self):
        res = contrast.check(P("rgba(0, 0, 0, 0.5)"), P("#ffffff"), "text")
        self.assertEqual(res["fg_flat"], "#808080")
        self.assertEqual(res["fg"], "#00000080")
        self.assertLessEqual(res["ratio"], contrast.shown(ratio("#7f7f7f", "#ffffff")))
        self.assertGreaterEqual(res["ratio"], contrast.shown(ratio("#808080", "#ffffff")))

    def test_transparent_background_is_refused(self):
        with self.assertRaises(contrast.InputError):
            contrast.check(P("#000000"), P("#ffffff80"), "text")


class Fixes(unittest.TestCase):
    def assert_minimal(self, fg, bg, need, side):
        f = contrast.fix(P(fg)[:3], P(bg), need)[side]
        self.assertTrue(contrast.passes(ratio(f["color"], bg), need))
        # one step less of black or white must still fail, so the fix is the nearest
        t = f["mix"] / 100.0 - 0.001
        toward = 0 if side == "darker" else 255
        prev = tuple(int(c + (toward - c) * t + 0.5) for c in P(fg)[:3])
        self.assertFalse(contrast.passes(contrast.ratio(prev, P(bg)), need))
        return f

    def test_darker_fix_for_light_grey_on_white(self):
        res = contrast.check(P("#999999"), P("#ffffff"), "text")
        self.assertIsNone(res["fix"]["lighter"])
        self.assertEqual(res["fix"]["nearest"], "darker")
        f = self.assert_minimal("#999999", "#ffffff", 4.5, "darker")
        self.assertEqual(f["with"], "black")

    def test_one_step_fix(self):
        f = contrast.fix(P("#777777")[:3], P("#ffffff"), 4.5)
        self.assertEqual(f["darker"]["color"], "#767676")
        self.assertEqual(f["darker"]["ratio"], 4.54)

    def test_lighter_fix_on_dark_background(self):
        res = contrast.check(P("#808080"), P("#404040"), "ui")
        self.assertIsNone(res["fix"]["darker"])
        self.assertEqual(res["fix"]["nearest"], "lighter")
        self.assert_minimal("#808080", "#404040", 3.0, "lighter")

    def test_nearest_is_smaller_delta_e(self):
        f = contrast.fix(P("#7a7a7a")[:3], P("#7a7a7a"), 3.0)   # same colour: both ways work
        self.assertIsNotNone(f["darker"])
        self.assertIsNotNone(f["lighter"])
        best = min(("darker", "lighter"), key=lambda s: f[s]["delta_e"])
        self.assertEqual(f["nearest"], best)

    def test_delta_e(self):
        self.assertEqual(contrast.delta_e((10, 20, 30), (10, 20, 30)), 0)
        self.assertGreater(contrast.delta_e((0, 0, 0), (255, 255, 255)), 99)


class Palette(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, data, name="palette.json"):
        path = os.path.join(self.tmp.name, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(data) if not isinstance(data, str) else data)
        return path

    def palette(self):
        return self.write({
            "palette": {"text": "#1a1a1a", "muted": "#9ca3af", "bg": "#ffffff",
                        "primary": "#0f766e"},
            "pairs": [["text", "bg"], "muted on bg", ["primary", "bg", "ui"]]})

    def test_named_pairs_from_file(self):
        res = contrast.run(palette=self.palette())
        self.assertFalse(res["grid"])
        self.assertEqual([(r["fg_name"], r["bg_name"], r["use"]) for r in res["results"]],
                         [("text", "bg", "text"), ("muted", "bg", "text"),
                          ("primary", "bg", "ui")])
        self.assertEqual(res["failed"], 1)
        self.assertEqual(res["results"][1]["fix"]["nearest"], "darker")

    def test_command_line_pairs_replace_file_pairs(self):
        res = contrast.run(["primary on bg", "#000 on bg"], palette=self.palette(), use="ui")
        self.assertEqual(len(res["results"]), 2)
        self.assertEqual(res["results"][1]["fg_name"], None)
        self.assertEqual(res["results"][1]["bg_name"], "bg")
        self.assertEqual(res["failed"], 0)

    def test_grid_without_pairs(self):
        path = self.write({"palette": {"a": "#ffffff", "b": "#000000", "c": "#777777",
                                       "d": "#0f766e"}})
        res = contrast.run(palette=path)
        self.assertTrue(res["grid"])
        self.assertEqual(len(res["results"]), 6)
        self.assertEqual(res["failed"], 0)
        ratios = [r["ratio"] for r in res["results"]]
        self.assertEqual(ratios, sorted(ratios, reverse=True))
        self.assertTrue(all(r["fix"] is None and r["pass"] is None for r in res["results"]))

    def test_grid_puts_the_opaque_colour_behind_and_skips_two_transparent(self):
        path = self.write({"palette": {"text": "#111111", "overlay": "rgba(0,0,0,0.5)",
                                       "bg": "#ffffff", "veil": "#ffffff80"}})
        res = contrast.run(palette=path)
        pairs = {(r["fg_name"], r["bg_name"]) for r in res["results"]}
        self.assertEqual(pairs, {("text", "bg"), ("overlay", "text"), ("overlay", "bg"),
                                 ("veil", "text"), ("veil", "bg")})
        self.assertEqual(res["skipped"], [["overlay", "veil"]])
        self.assertIn("both transparent", contrast.render(res, markdown=True))

    def test_reads_brand_json_template(self):
        template = os.path.join(ROOT, "templates", "brand.json")
        key, entries, pairs, is_brand = contrast.load_palette(template)
        self.assertIn(key, ("palette", "colors"))
        self.assertTrue(is_brand)
        self.assertTrue(entries)
        res = contrast.run(["%s on #ffffff" % contrast.to_hex(entries[0][1])], palette=template)
        self.assertEqual(res["brand_json"], template if key == "colors" else None)
        self.assertEqual(len(res["results"]), 1)
        if len(entries) < 2 and not pairs:
            with self.assertRaises(contrast.InputError):
                contrast.run(palette=template)

    def test_brand_json_with_own_palette(self):
        path = self.write({"avoid": ["Original"], "colors": ["#006bff"],
                           "palette": {"brand": "#c2410c", "bg": "#ffffff"}})
        res = contrast.run(palette=path)
        self.assertIsNone(res["brand_json"])     # "palette" read, not the original's colours
        self.assertEqual(res["results"][0]["fg_name"], "brand")

    def test_bad_input(self):
        path = self.palette()
        for pairs in (["mutd on bg"], ["#000 over #fff"], ["#000 on #fff on #000"]):
            with self.assertRaises(contrast.InputError):
                contrast.run(pairs, palette=path)
        with self.assertRaises(contrast.InputError):
            contrast.run(palette=self.write({"palette": {"a": "#fff"},
                                             "pairs": [["a", "a", "huge"]]}, "u.json"))
        with self.assertRaises(contrast.InputError):
            contrast.run(palette=self.write("[]", "list.json"))
        with self.assertRaises(contrast.InputError):
            contrast.run()


class Cli(unittest.TestCase):
    def main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = contrast.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_exit_codes(self):
        self.assertEqual(self.main("#1a1a1a on #ffffff")[0], 0)
        self.assertEqual(self.main("#999999 on #ffffff")[0], 1)
        self.assertEqual(self.main("#999999 on #ffffff", "--use", "large")[0], 1)
        self.assertEqual(self.main("#949494 on #ffffff", "--use", "ui")[0], 0)
        code, _, err = self.main("#99 on #fff")
        self.assertEqual(code, 2)
        self.assertIn("contrast:", err)

    def test_json(self):
        code, out, _ = self.main("#777777 on #ffffff", "--json")
        data = json.loads(out)
        self.assertEqual(code, 1)
        self.assertEqual(data["results"][0]["ratio"], 4.47)
        self.assertEqual(data["results"][0]["fix"]["darker"]["color"], "#767676")

    def test_german_markdown_and_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "contrast.md")
            code, out, _ = self.main("#777777 auf #ffffff", "--lang", "de", "--markdown",
                                     "--out", path)
            self.assertEqual(code, 1)
            self.assertIn("wrote", out)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        self.assertIn("# Kontrastprüfung (WCAG 2.2)", text)
        self.assertIn("4,47:1", text)
        self.assertIn("#777777 auf #ffffff", text)
        self.assertIn("## Korrekturen", text)
        self.assertIn("#767676", text)

    def test_plain_text(self):
        _, out, _ = self.main("#808080 on #404040", "--use", "ui")
        self.assertIn("UI: FAIL, needs 3", out)
        self.assertIn("darker: none passes on this background", out)
        self.assertIn("lighter: #", out)


if __name__ == "__main__":
    unittest.main()
