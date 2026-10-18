"""The worked examples in examples/ are reproducible: every script command in an
example's README runs again in a temporary copy, and each file it writes must
equal the committed file byte for byte. Also checks the honesty rules of the
examples: every input and agent-written file is labelled as synthetic, and
every link points to a reserved example domain."""

import csv
import difflib
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

from _load import ROOT

EXAMPLES = os.path.join(ROOT, "examples")
LABEL = "fiktiv / synthetic demo data"
LINK = re.compile(r"https?://([^/\s\"'<>()\[\]|]+)")
RESERVED = re.compile(r"(^|\.)example\.(com|org)$")
XMLNS = re.compile(r'\sxmlns(:\w+)?="[^"]*"')


def example_dirs():
    if not os.path.isdir(EXAMPLES):
        return []
    return sorted(os.path.join(EXAMPLES, d) for d in os.listdir(EXAMPLES)
                  if os.path.isfile(os.path.join(EXAMPLES, d, "README.md")))


def commands(readme):
    """The python3 lines of the README's "## Commands" section, as
    (argv, stdout file or None, expected exit code, output files)."""
    with open(readme, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"^## Commands\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        raise AssertionError("%s has no '## Commands' section" % readme)
    out = []
    for line in m.group(1).splitlines():
        if not line.startswith("python3 "):
            continue
        code = 1 if re.search(r"#\s*Exit 1\s*$", line) else 0
        argv = shlex.split(line, comments=True)
        stdout = None
        if ">" in argv:
            i = argv.index(">")
            stdout, argv = argv[i + 1], argv[:i]
        argv = [sys.executable] + [a.replace("$SKILL", ROOT) for a in argv[1:]]
        files = [argv[i + 1] for i, a in enumerate(argv[:-1]) if a in ("--out", "--svg")]
        files += [stdout] if stdout else []
        out.append((argv, stdout, code, files))
    return out


def all_files(folder):
    for base, _, names in os.walk(folder):
        for n in sorted(names):
            if n.startswith(".") or n.endswith(".pyc"):
                continue
            path = os.path.join(base, n)
            yield os.path.relpath(path, folder), path


class Examples(unittest.TestCase):
    def test_there_is_an_example(self):
        self.assertTrue(example_dirs(), "no example with a README.md in %s" % EXAMPLES)

    def test_outputs_are_reproduced_byte_for_byte(self):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        for ex in example_dirs():
            cmds = commands(os.path.join(ex, "README.md"))
            self.assertTrue(cmds, "%s: no commands found" % ex)
            outputs = [f for _, _, _, files in cmds for f in files]
            with tempfile.TemporaryDirectory() as tmp:
                work = os.path.join(tmp, "example")
                shutil.copytree(ex, work)
                for f in outputs:      # nothing may pass because it was already there
                    if os.path.exists(os.path.join(work, f)):
                        os.remove(os.path.join(work, f))
                for argv, stdout, code, _ in cmds:
                    run = subprocess.run(argv, cwd=work, env=env, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
                    shown = " ".join(argv[1:])
                    self.assertEqual(run.returncode, code, "%s: %s\n%s%s" % (
                        os.path.basename(ex), shown, run.stdout.decode("utf-8", "replace"),
                        run.stderr.decode("utf-8", "replace")))
                    if stdout:
                        with open(os.path.join(work, stdout), "wb") as fh:
                            fh.write(run.stdout)
                for f in outputs:
                    with self.subTest(example=os.path.basename(ex), file=f):
                        committed = os.path.join(ex, f)
                        self.assertTrue(os.path.isfile(committed), "%s is not committed" % f)
                        with open(committed, "rb") as fh:
                            want = fh.read()
                        with open(os.path.join(work, f), "rb") as fh:
                            got = fh.read()
                        if got != want:
                            diff = difflib.unified_diff(
                                want.decode("utf-8", "replace").splitlines(),
                                got.decode("utf-8", "replace").splitlines(),
                                "committed/" + f, "regenerated/" + f, lineterm="")
                            self.fail("%s differs from a fresh run; rerun the README "
                                      "commands:\n%s" % (f, "\n".join(list(diff)[:40])))

    def test_inputs_and_agent_files_are_labelled_synthetic(self):
        for ex in example_dirs():
            outputs = {f for _, _, _, files in commands(os.path.join(ex, "README.md"))
                       for f in files}
            for rel, path in all_files(ex):
                if rel in outputs:
                    continue
                with open(path, encoding="utf-8") as fh:
                    head = fh.read(400)
                with self.subTest(file=rel):
                    self.assertIn(LABEL, head, "%s must say '%s' at the top" % (rel, LABEL))

    def test_links_point_to_reserved_example_domains(self):
        for ex in example_dirs():
            for rel, path in all_files(ex):
                with open(path, encoding="utf-8") as fh:
                    text = XMLNS.sub("", fh.read())     # an SVG namespace is not a link
                hosts = set(LINK.findall(text))
                bad = sorted(h for h in hosts if not RESERVED.search(h.lower()))
                with self.subTest(file=rel):
                    self.assertEqual(bad, [], "%s links to real hosts" % rel)

    def test_matrix_snapshots_list_the_same_features(self):
        for ex in example_dirs():
            before = os.path.join(ex, "teardown", "features-before-build.csv")
            after = os.path.join(ex, "teardown", "features.csv")
            if not (os.path.isfile(before) and os.path.isfile(after)):
                continue

            def features(path):
                with open(path, newline="", encoding="utf-8") as fh:
                    return [(r["feature"], r["priority"], r["original"])
                            for r in csv.DictReader(fh)]
            self.assertEqual(features(before), features(after))


if __name__ == "__main__":
    unittest.main()
