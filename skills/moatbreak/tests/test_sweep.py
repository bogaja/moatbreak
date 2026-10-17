import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from _load import load

sweep = load("sweep")


def put(root, rel, text, binary=False):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if binary else "w", **({} if binary else {"encoding": "utf-8"})) as fh:
        fh.write(text)
    return path


class Sweep(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        r = self.root = self.tmp.name
        put(r, "src/app/page.tsx", "export default function Page() {\n"
                                   "  return <h1>Slotwise</h1>\n}\n")
        put(r, "src/components/CalendlyEmbed.tsx", "// left over\n")
        put(r, "src/lib/copy.ts", "export const hero = 'The calendly alternative'\n")
        put(r, "src/styles/tokens.css", ":root { --accent: #006BFF; --bg: #fff; }\n")
        put(r, "src/lib/links.ts", "const help = 'https://help.calendly.com/x'\n")
        put(r, "src/lib/team.ts", "export const AcuitySchedulingSync = 1\n")
        put(r, "teardown/recon.md", "# Recon: Calendly\n")
        put(r, "node_modules/x/index.js", "calendly\n")
        put(r, "public/logo.png", b"\x89PNG\0calendly", binary=True)
        put(r, "package-lock.json", '{"calendly": 1}\n')

    def tearDown(self):
        self.tmp.cleanup()

    def run_sweep(self, **kw):
        return sweep.sweep(self.root, avoid=["Calendly", "Acuity Scheduling"],
                           domains=["calendly.com"], colors=["#006bff"], **kw)

    def test_finds_names_paths_domains_and_colours(self):
        hits = self.run_sweep()
        kinds = {(h["kind"], os.path.basename(h["file"].rstrip("/"))) for h in hits}
        self.assertIn(("path", "CalendlyEmbed.tsx"), kinds)
        self.assertIn(("name", "copy.ts"), kinds)
        self.assertIn(("domain", "links.ts"), kinds)
        self.assertIn(("color", "tokens.css"), kinds)
        self.assertIn(("name", "team.ts"), kinds)   # AcuitySchedulingSync

    def test_skips_planning_folders_deps_locks_and_binaries(self):
        files = {h["file"] for h in self.run_sweep()}
        self.assertFalse(any(f.startswith("teardown") for f in files))
        self.assertFalse(any("node_modules" in f for f in files))
        self.assertNotIn("package-lock.json", files)
        self.assertNotIn(os.path.join("public", "logo.png"), files)
        self.assertNotIn(os.path.join("src", "app", "page.tsx"), files)

    def test_include_planning(self):
        files = {h["file"] for h in self.run_sweep(include_planning=True)}
        self.assertIn(os.path.join("teardown", "recon.md"), files)

    def test_short_hex_and_alpha_hex_match_long(self):
        put(self.root, "src/a.css", "a { color: #06f }\nb { color: #0066ffcc }\n")
        hits = [h for h in sweep.sweep(self.root, colors=["#0066FF"])
                if h["file"].endswith("a.css")]
        self.assertEqual([h["kind"] for h in hits], ["color", "color"])

    def test_rgb_function_matches(self):
        put(self.root, "src/b.css", "a { color: rgb(0, 107, 255) }\nb { color: rgba(0 107 255 / .5) }\n")
        hits = [h for h in sweep.sweep(self.root, colors=["#006bff"])
                if h["file"].endswith("b.css")]
        self.assertEqual([h["kind"] for h in hits], ["color", "color"])

    def test_near_colour_is_a_warning_not_a_failure(self):
        clean = tempfile.mkdtemp(dir=self.root)
        put(clean, "theme.css", ":root { --brand: #0a6cf5; --other: #e4572e; }\n")
        hits = sweep.sweep(clean, colors=["#006bff"], near=10)
        self.assertEqual([h["kind"] for h in hits], ["near-color"])
        self.assertLess(hits[0]["delta_e"], 10)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(sweep.main([clean, "--colors", "#006bff"]), 0)
            self.assertEqual(sweep.main([clean, "--colors", "#006bff", "--strict"]), 1)
            self.assertEqual(sweep.main([clean, "--colors", "#006bff", "--near", "0"]), 0)

    def test_german_spelling_variants(self):
        clean = tempfile.mkdtemp(dir=self.root)
        put(clean, "a.ts", "const a = 'Mueller Moebel'\n")
        put(clean, "b.ts", "const b = 'müller-möbel.de'\n")
        put(clean, "c.ts", "export const MullerMobelBanner = 1\n")
        put(clean, "d.ts", "const d = 'Grosse Strasse'\n")
        hits = sweep.sweep(clean, avoid=["Müller Möbel", "Große Straße"])
        files = sorted({os.path.basename(h["file"]) for h in hits})
        self.assertEqual(files, ["a.ts", "b.ts", "c.ts", "d.ts"])
        hits = sweep.sweep(clean, avoid=["Mueller Moebel"])
        files = sorted({os.path.basename(h["file"]) for h in hits})
        self.assertEqual(files, ["a.ts", "b.ts"])

    def test_allow_list_for_attribution(self):
        clean = tempfile.mkdtemp(dir=self.root)
        put(clean, "LICENSE", "Copyright (c) 2026 Calendly fan (the original work)\n")
        put(clean, "docs/compare-calendly.md", "How we differ from Calendly\n")
        put(clean, "src/app.ts", "const name = 'Slotwise'\n")
        hits = sweep.sweep(clean, avoid=["Calendly"], allow=["LICENSE", "docs/compare-*.md"])
        self.assertEqual(len(hits), 3)            # file name + 2 lines, all allowed
        self.assertTrue(all(h.get("allowed") for h in hits))
        self.assertEqual(sweep.blocking(hits), [])
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(sweep.main([clean, "--avoid", "Calendly",
                                         "--allow", "LICENSE,docs/compare-*.md"]), 0)
        self.assertIn("Clean.", buf.getvalue())
        self.assertIn("3 allowed hits", buf.getvalue())
        with redirect_stdout(io.StringIO()):
            self.assertEqual(sweep.main([clean, "--avoid", "Calendly"]), 1)

    def test_delta_e_sanity(self):
        self.assertEqual(sweep.delta_e((10, 20, 30), (10, 20, 30)), 0)
        self.assertGreater(sweep.delta_e((0, 0, 0), (255, 255, 255)), 99)

    def test_cli_exit_codes_and_config(self):
        cfg = put(self.root, "brand.json", json.dumps({"avoid": ["Calendly"], "near": 5}))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(sweep.main([self.root, "--config", cfg]), 1)
        clean = tempfile.mkdtemp(dir=self.root)
        put(clean, "index.html", "<h1>Slotwise</h1>")
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(sweep.main([clean, "--avoid", "Calendly"]), 0)
        self.assertIn("Clean", buf.getvalue())
        with redirect_stderr(io.StringIO()):
            self.assertEqual(sweep.main([clean]), 2)


if __name__ == "__main__":
    unittest.main()
