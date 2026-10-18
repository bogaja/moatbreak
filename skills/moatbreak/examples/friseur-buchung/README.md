# Worked example: a booking app for hair salons (fiktiv / synthetic demo data)

A complete Moatbreak run for a German-speaking user, from the market overview to the pre-launch check. The deliverables in `teardown/` are in German on purpose: deliverables follow the user's language. Every script output in `teardown/` comes from the inputs with the commands below, byte for byte, and `tests/test_examples.py` checks that on every test run.

## Everything here is invented

- **Products**: Kammfux, Föhnora, Strähnwerk, Bürstbar, Terminkoje, ShearDock, Frisoplan, Frisierbox and the new product Taktilo do not exist. A web search on 2026-10-17 found no software product under any of these names. Prices, help pages, terms and changelogs are invented too. Every product link points to example.com.
- **Reviews**: the 42 rows in `teardown/reviews.csv` are synthetic, written for this example in German and English. No person wrote them and none comes from a platform. The names in the `source` column (capterra, omr, trustpilot, google-play, app-store) only stand for the kind of source, so the bias by source has something to show. Every review link points to example.org.
- **The rebuild**: the build status in `features.csv` (column `clone`) does not exist either.
- **Labels**: every input and every file the agent wrote says "fiktiv / synthetic demo data" at the top. In the CSV files that is the first column; the scripts ignore extra columns. In the JSON files it is the key `_demo`. The script outputs carry "fiktiv" in the title where the script has a title option (`--title`, `--target`, `--ours`). `estimate.md`, `parity.md`, `contrast.md` and `feedback.json` have no title option and no label; they only live in this folder.

Data from this example never goes into a real analysis (see `SKILL.md`, "Examples and evals").

## What the run shows

The user wants to build a booking app for hair salons in DACH and names no reference product. The run is compressed into one day: every script runs as of 2026-10-17, and the sources were read before. In a real run, weeks pass between recon, build and parity.

| step | mode | file | shows |
| --- | --- | --- | --- |
| 0 | discover | `landscape.md`, `landscape.svg` | a proposal from verified, fitting rows only; a product without an evidence link listed last as unverified; a price per booking kept off the map; rows filtered out with a reason; the user's planned position as a diamond |
| 1 | recon | `recon.md`, `features.csv` | sources with dates, screens, flows, signature elements, a data model with a health field, the niche delta |
| 2 | voice of customer | `feedback.md`, `feedback.json`, `fixes.md` | a row without a link dropped, a duplicate removed; bias by source; why they leave and where they go; 5 needs, each with three checked quotes from several sources; the fix plan as new rows in the matrix; three angles |
| 3 | offer | `estimate.md` | MVP, + should, + could in person-days and euros, with contingency, overheads and fixed items, the fix rows included; one unknown row marked |
| 4 | build handoff | `build-brief.md` | milestones from the estimate, acceptance criteria for every must feature, data model, API sketch, stack questions, WCAG 2.2 AA, test plan, pre-launch gate |
| 5 | parity | `parity.md` | 82.6 of 100 and still not shippable, because one must feature is only partly done |
| 6 | brand | `brand.md`, `brand.json`, `contrast.md` | 20 names, 5 shortlisted, register checks honestly "to check"; a new palette at a distance from the original's colours; one draft failed the contrast check and contrast.py calculated the fix |
| 7 | battle card | `battlecard.md` | claims about the original tagged verified, stale, not public or assumed, each tag next to the competitor's own value; a fair table for a comparison page in which the original is ahead too |
| 8 | legal | `legal.md` | the distance check and the launch obligations as a checklist for a lawyer |
| 9 | client report | `report.html` | the files above in one offline HTML page in German, the map inlined, the battle card marked internal, visibility "not researched" |

`battlecard.md` is the plain script output. In a real run the agent then replaces every "zu schreiben"; here it stays as it is, so the test can compare it.

## Files

| file | kind |
| --- | --- |
| `teardown/competitors.csv` | input, written by the agent from the pages it read (discover) |
| `teardown/reviews.csv` | input, collected reviews (synthetic) |
| `teardown/themes.json` | input, a copy of `scripts/themes.json` with four themes of the trade, two leaving phrases ("back to the paper diary") and without "doppelt" in the general data theme |
| `teardown/features-before-build.csv` | input, the feature matrix on the day of the offer (clone everywhere no) |
| `teardown/features.csv` | input, the same matrix after milestone M1 (clone filled), with `source` and `checked` |
| `teardown/brand.json` | input, the original's names and colours and the new palette |
| `teardown/landscape.md`, `teardown/landscape.svg` | script: landscape.py |
| `teardown/feedback.md`, `teardown/feedback.json` | script: reviews.py |
| `teardown/estimate.md`, `teardown/parity.md` | script: parity.py |
| `teardown/contrast.md` | script: contrast.py |
| `teardown/battlecard.md` | script: battlecard.py |
| `teardown/report.html` | script: report.py |
| `teardown/recon.md`, `teardown/fixes.md`, `teardown/build-brief.md`, `teardown/brand.md`, `teardown/legal.md` | written by the agent, only with facts from the inputs |

Not in the example: visibility (`sitemap.py`, `seo.py`, `visibility.md`), screenshots with `sources.csv` and `imgdiff.py` (`sources.py` checks only the sources table in `recon.md` here), `sweep.py` and `listing.py` (there is no code and no store listing), `offer.md` and a comparison page (`compare.md`). The files say "nicht recherchiert" or "zu prüfen" for them.

## Commands

From this folder, with `SKILL` as the path to the skill folder. The test runs every line of this block that starts with `python3` and expects exit 0, unless the line ends with `# Exit 1`.

```bash
cd skills/moatbreak/examples/friseur-buchung
SKILL=../..

# Step 0: market overview and positioning map
python3 $SKILL/scripts/landscape.py teardown/competitors.csv --lang de --market DACH --title "Buchungs-App für Friseure (fiktiv / synthetic demo data)" --svg teardown/landscape.svg --x price_from --y axis_y --x-label "Preis ab (EUR/Monat, netto)" --y-label "Kernaufgaben laut Website (von 8)" --out teardown/landscape.md

# Step 1: every row of the sources table in recon.md has one page URL and its date
python3 $SKILL/scripts/sources.py teardown --as-of 2026-10-17 --lang de

# Step 2: voice of customer as a report and as JSON, then check the quotes in fixes.md
python3 $SKILL/scripts/reviews.py teardown/reviews.csv --lang de --target "Kammfux (fiktiv)" --themes teardown/themes.json --as-of 2026-10-17 --out teardown/feedback.md
python3 $SKILL/scripts/reviews.py teardown/reviews.csv --themes teardown/themes.json --as-of 2026-10-17 --json --out teardown/feedback.json
python3 $SKILL/scripts/reviews.py teardown/reviews.csv --verify teardown/fixes.md --lang de

# Step 3: estimate for the offer, from the matrix before the build (with the fix rows)
python3 $SKILL/scripts/parity.py teardown/features-before-build.csv --estimate-only --lang de --markdown --buffer 20 --overhead "QA=15,PM=10" --fixed "Workshop=2-3;Setup=2-3;Design=5-8;Go-live=2-3" --day-rate 650 --out teardown/estimate.md

# Step 5: parity after milestone M1
python3 $SKILL/scripts/parity.py teardown/features.csv --lang de --markdown --buffer 20 --out teardown/parity.md

# Step 6: the first draft for muted fails, then the palette in brand.json
python3 $SKILL/scripts/contrast.py "#8a8494 on #faf8f5" --lang de   # Exit 1
python3 $SKILL/scripts/contrast.py --palette teardown/brand.json --lang de --markdown --out teardown/contrast.md

# Step 7: battle card, then check its quotes
python3 $SKILL/scripts/battlecard.py --feedback teardown/feedback.json --features teardown/features.csv --target "Kammfux (fiktiv)" --ours "Taktilo (fiktiv)" --as-of 2026-10-17 --lang de --out teardown/battlecard.md
python3 $SKILL/scripts/reviews.py teardown/reviews.csv --verify teardown/battlecard.md --lang de

# Step 9: the client report as one HTML file
python3 $SKILL/scripts/report.py teardown --lang de --title "Wettbewerbsanalyse: Kammfux (fiktiv / synthetic demo data)" --as-of 2026-10-17 --out teardown/report.html
```

Check that everything still holds (from the repository folder):

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/moatbreak/tests -p 'test_examples.py'
```

## When a script changes

If a script changes its output, `test_examples.py` fails and shows the difference. Then run the commands above again, read the difference and check that the files the agent wrote still hold: they repeat numbers from the script outputs (reviews, person-days, parity, contrast). Only then commit the new outputs.
