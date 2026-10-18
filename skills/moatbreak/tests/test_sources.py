import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from _load import load

sources = load("sources")

AS_OF = "2026-10-17"


def put(root, rel, data=b"x"):
    path = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    return path


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = sources.main(argv)
    return code, out.getvalue(), err.getvalue()


class Sources(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.tmp.name, "teardown")
        put(self.root, "screens/S01-home-1440.png")
        put(self.root, "screens/S01-home-390.png")
        put(self.root, "proof/2026-10-17-pricing.pdf")
        put(self.root, "screens/.DS_Store")

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self, text):
        put(self.root, "sources.csv", "file,url,read_on,notes\n" + text)

    def test_complete_manifest_passes(self):
        self.manifest("screens/S01-home-1440.png,https://x.example.com/,2026-10-17,1440x900\n"
                      "teardown/screens/S01-home-390.png,https://x.example.com/,2026-10-17,\n"
                      "proof/2026-10-17-pricing.pdf,https://x.example.com/preise,2026-10-17,\n")
        code, out, _ = run([self.root, "--as-of", AS_OF])
        self.assertEqual(code, 0)
        self.assertIn("3 files in screens/, proof/; 3 rows in sources.csv.", out)
        self.assertIn("Every file has its URL and date.", out)

    def test_every_gap_in_the_paper_trail_fails(self):
        self.manifest("screens/S01-home-1440.png,,2026-10-17,\n"
                      "proof/2026-10-17-pricing.pdf,https://x.example.com/preise,17.10.2026,\n"
                      "screens/S02.png,https://x.example.com/b,2026-10-01,\n"
                      "screens/S01-home-1440.png,https://x.example.com/,2026-10-17,\n")
        code, out, _ = run([self.root, "--as-of", AS_OF, "--json"])
        self.assertEqual(code, 1)
        kinds = [(p["kind"], p["file"]) for p in json.loads(out)["problems"]]
        self.assertEqual(kinds, [("untracked", "screens/S01-home-390.png"),
                                 ("no_url", "screens/S01-home-1440.png"),
                                 ("no_date", "proof/2026-10-17-pricing.pdf"),
                                 ("gone", "screens/S02.png"),
                                 ("twice", "screens/S01-home-1440.png")])

    def test_future_and_old_dates(self):
        self.manifest("screens/S01-home-1440.png,https://x.example.com/,2026-10-18,\n"
                      "screens/S01-home-390.png,https://x.example.com/,2026-05-01,\n"
                      "proof/2026-10-17-pricing.pdf,https://x.example.com/preise,2026-10-17,\n")
        code, out, _ = run([self.root, "--as-of", AS_OF, "--lang", "de"])
        self.assertEqual(code, 1)
        self.assertIn("Zeile 2: screens/S01-home-1440.png wurde am 2026-10-18 gelesen, "
                      "nach dem 17.10.2026", out)
        self.assertIn("## Mehr als 90 Tage vor dem 17.10.2026 gelesen", out)
        self.assertIn("- screens/S01-home-390.png (2026-05-01)", out)

    def test_no_manifest_lists_every_file(self):
        out_file = os.path.join(self.tmp.name, "sources.md")
        code, stdout, _ = run([self.root, "--as-of", AS_OF, "--out", out_file])
        self.assertEqual((code, stdout), (1, "wrote %s\n" % out_file))
        with open(out_file, encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("No sources.csv", text)
        self.assertEqual(text.count("no row in sources.csv"), 3)

    def test_nothing_to_check_and_errors(self):
        empty = os.path.join(self.tmp.name, "empty")
        os.mkdir(empty)
        code, out, _ = run([empty, "--as-of", AS_OF])
        self.assertEqual(code, 0)
        self.assertIn("nothing to check", out)
        self.assertEqual(run([os.path.join(self.tmp.name, "nope")])[0], 2)
        self.assertEqual(run([self.root, "--as-of", "17.10.2026"])[0], 2)
        put(self.root, "sources.csv", "file,link\nx,y\n")
        code, _, err = run([self.root, "--as-of", AS_OF])
        self.assertEqual(code, 2)
        self.assertIn("no 'url' column", err)


if __name__ == "__main__":
    unittest.main()
