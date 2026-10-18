# Changelog

All notable changes to Moatbreak. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-10-18

### Added

- Discover mode (step 0, `references/discover.md`): when the user names only
  a niche or a market, Moatbreak searches in the market's language (DACH
  directories, local app stores, .de/.at/.ch), records candidates with the
  public page every claim comes from, filters them by five criteria (same
  job, same customer, active, readable sources, the user's market), shows a
  landscape matrix and a positioning map, and waits for the user to confirm
  which products to tear down before recon starts.
- `scripts/landscape.py` with `templates/competitors.csv`: landscape matrix
  (verified rows in the user's market first, rows without an evidence link
  marked unverified and never proposed, unsourced prices and axis values
  marked), market check with DACH/EU/global aliases, a proposal of up to
  five verified fits, a positioning map as a standalone SVG on two numeric
  axes, `--lang de`, `--json`. 24 tests.
- Visibility add-on for recon (`references/visibility.md`,
  `templates/visibility.md`): public files (robots.txt, sitemap, llms.txt),
  titles, meta descriptions and structured data of key pages, markets and
  hreflang, search data only from a connected SEO tool or a user export with
  tool and date ("not measured" otherwise), and a fixed five-question
  AI-answer sample recorded verbatim with assistant and date, never counted
  as customer evidence.
- `scripts/sitemap.py`: offline page inventory from a saved sitemap, sitemap
  index, .xml.gz or URL list (page types, sections, language folders,
  hreflang, partial-index and stamped-lastmod warnings), with `--lang de`,
  `--as-of`, `--json` and `--out`; refuses DOCTYPE/ENTITY declarations and
  files over 60 MB. 10 tests.
- Build handoff (`references/build-handoff.md`, `templates/build-brief.md`):
  turns the teardown into a build brief with milestones from the matrix
  priorities (MVP / + should / + could), Given/When/Then acceptance criteria
  for every must feature, a data model and API sketch from recon, stack
  questions to ask instead of assuming, a BFSG / EN 301 549 / WCAG 2.2 AA
  checklist, a test plan and a pre-launch gate (parity, brand mode,
  contrast.py, sweep.py, distance check).
- `scripts/contrast.py`: WCAG 2.2 contrast checker written from the WCAG
  formula. It takes colour pairs or a palette (reads `teardown/brand.json`),
  reports AA/AAA for text and large text and 3:1 for UI components, never
  rounds up to pass, calculates the nearest passing shade and tint for every
  failing pair, and supports `--json`, `--markdown` and `--lang de`; exit 1
  on a fail. 23 tests.
- Battle card mode (`references/battlecard.md`, `templates/battlecard.md`):
  `scripts/battlecard.py` turns `feedback.json` (`reviews.py --json`) and
  `features.csv` into a one-page sales battle card with a SWOT appendix.
  Weak themes carry verbatim quotes with links, praise themes show where not
  to attack, differentiators come from the feature matrix, and objection
  answers are stubs marked "to write". Every claim about the competitor is
  tagged verified, reported or assumed with source and date, using the new
  optional `source` and `checked` columns in `features.csv`. Checks older
  than 90 days are flagged stale. A comparison-page list takes only
  verified, fresh rows with a public link, never reviews, and warns about
  one-sided tables (§ 5a UWG). The reference adds objection-answer rules,
  comparison-page rules and a lawyer checklist. 14 tests.
- `reviews.py --verify FILE`: checks that every linked quote in a report
  stands word for word in the review behind its link and exits 1 if not.
- `reviews.py`: "Why they leave" section with reviews that say the writer
  switched, cancelled or is looking for an alternative (EN/DE
  `switch_patterns` in themes.json), each with the verbatim sentence and
  link, the alternative only where the review names it, and the themes
  those reviews complain about (`switching` in `--json`).
- `reviews.py`: the sample by source shows share, average stars and date
  range per source, and warns in plain words when one source has over 60%,
  a source is 1 star or more off the overall average, or over 70% of dated
  reviews are from the last 90 days or older than `--months` (`source_bias`
  in `--json`).
- `reviews.py`: an optional `segment` column (the reviewer's role or company
  size exactly as the platform shows it, never guessed). The report adds a
  sample by segment, thin below 3 reviews, and a "Who says it" line under
  every theme (`by_segment` and `segments` in `--json`).
- `examples/friseur-buchung/`: a complete synthetic run for a German user,
  from discover to the legal check and the client report, with the inputs,
  every script output and the files the agent writes. `tests/test_examples.py`
  (5 tests) reruns the commands in its README and compares every output byte
  for byte, and checks that every file is labelled synthetic and links only
  to example domains.
- `evals/evals.json`: 18 agent evals (prompt, expected_output, assertions,
  files, web, should_trigger), three of them prompts the skill must not take
  (two near misses: a named product with only a price question, generic
  branding), with synthetic fixtures in `evals/files/`, a run and grading
  guide in `evals/README.md`, and `tests/test_evals.py` (12 tests) for the
  format and the fixture facts the assertions rely on. Results are in
  `evals/RESULTS.md`: in run 2, round D (all 18 evals on the final state,
  one run per eval; a sample, not a benchmark), 137 of 144 assertions
  passed and 18 of 18 triggers were correct.
- `scripts/seo.py`: reads a keyword export from Semrush, Ahrefs (UTF-16
  too), DataForSEO, SISTRIX, Similarweb or Search Console; keyword themes
  (alternatives and vs, branded, local, how-to, category), branded share,
  top keywords and pages, and with `--ours` the keyword gap; every number
  labelled with tool, database and the export date (`--as-of`, required).
  11 tests.
- Visibility: a local search step (Google Business Profile categories, a
  dated local pack sample by hand) and a dated Core Web Vitals row.
- `SKILL.md`: "When a browser is available": read pages with the session's
  browser tools, capture the parity viewports into `teardown/screens/`, save
  dated PDF proof copies, and log every file in `teardown/sources.csv`
  (`templates/sources.csv`). `scripts/sources.py` fails when a screenshot or
  proof copy has no URL and date, a date is after `--as-of`, or a listed
  file is gone. 5 tests. The scripts stay offline by design.
- `scripts/report.py`: the teardown as one self-contained, accessible HTML
  file in the client's language (`report.md` first, the map inlined, the
  battle card marked internal, "not researched" for every mode that did not
  run, no external assets). The worked example builds its `report.html`
  with it. 8 tests.
- Launch mode (`references/launch.md`): landing and pricing pages from the
  angle with the clean-room, claim-only-what-is-shipped and § 6 UWG rules,
  design tokens from the new palette (brand mode step 3), and
  `scripts/listing.py` with `templates/listing.json`: App Store and Google
  Play texts against the stores' limits, empty fields and the original's
  names in German spelling variants and near spellings. 7 tests.
- Recon: a messaging table (the original's hero claim verbatim with link
  and date, audience signal, promise type, what it leaves out) that feeds
  the angle and the battle card's "In one line", and a dated "recent moves"
  table that feeds the battle card's rechecks and SWOT threats.
- Discover: optional company columns in `competitors.csv` (`company`,
  `seat`, `founded`, `size`, `company_url` from the Impressum, a register or
  the company's press page), listed by `landscape.py` with source marks;
  market sizing stays out, at most a sourced count of target businesses
  from official statistics.
- Battle card: comparison page formats (alternative, alternatives with 4 to
  7 real ones, us vs them), who each product is best for, a switching
  section, a keyword target, an FAQ, and an audit of pages already
  published (current, stale, unverifiable).
- `references/legal-eu-dach.md` section 6: the research data (review sample,
  quotes, saved AI answers, proof copies) as personal data under the DSGVO,
  with legal basis, minimisation, keeping `teardown/` private and deletion,
  linked from voice of customer, the battle card and the ground rules.
- Test count: 231 (was 71).

### Changed

- `SKILL.md`: discover, visibility, build handoff, battle card and launch in
  the mode table, the full path, "Where things go" (now also `new-screens/`,
  `diffs/`, `report.md`, `offer-notes.md`, `sources.csv`, `seo.md`,
  `listing.json`, `report.html`), the commands and the script table. The
  description is 312 characters (was 1,015): the two triggers (a named
  product with a build or compete goal, or only a niche to build for), one
  German example and the negative; the outputs moved to the body.
- `reviews.py --verify` matches whole words: "helpful" no longer passes
  inside "unhelpful", nor "slow" inside "slowly"; only a quote that starts
  or ends with "..." may start or end inside a word, as the script's own
  snippets do. A text cut in "Read these by hand" ends with "...".
- `themes.json`: the shipped `switch_patterns` are written in the first
  person, so "the salon cancelled my appointment", "moving to the next
  week" or "let me switch to Dark Mode" no longer count as someone leaving,
  and a number alone or a common capitalised word (Konkurrenten, Anbieter,
  Dark Mode) is never reported as the alternative.
- `reviews.py --json --out FILE` writes the JSON as UTF-8 (a `>` redirect
  used the console's code page on Windows); the docs use it.
- `parity.py` (and so `battlecard.py`) stops with the line number when a row
  has more cells than the header, instead of a traceback; the CSV readers
  of `landscape.py`, `parity.py` and `reviews.py` say "save it as CSV UTF-8"
  for a Windows-1252 Excel export.
- `battlecard.py`: the objection data line puts the tag next to the
  competitor's own value ("Data: line n; X: yes [verified ...]; Y: partial").
- `themes.json` and `reviews.py`: a complaint theme can carry a
  `praise_label`, used wherever 4-5 star reviews praise its topic ("Fast, no
  waiting" instead of "Slow, laggy, heavy") in `feedback.md`,
  `feedback.json` and so the battle card; a copied themes file without it
  gets the shipped one for every theme whose label is unchanged.
  `battlecard.py` adds an "In plain words: to write" line to every strength,
  for what customers praise and the rep's line (agree, then how we match it).
- Brand mode: a failing contrast pair takes the variant contrast.py prints,
  exactly as printed, never a shade picked by eye; neutral roles (text,
  muted, border) stay neutral when the primary moves to a new hue family.
- `SKILL.md`: when the user wants the original's listings or catalogue in
  the new product, the answer names the legal way in (users enter or import
  their own data, or an official API or partner feed within its terms). A
  new section for requests without a build or compete goal: no mode runs, at
  most one question, and any price or figure in the answer carries its
  source and the date it was read, or says it could not be checked.
- `sitemap.py`: the index file never counts as a given child sitemap, a
  child is matched by its URL path (`de/sitemap.xml`), children that share a
  file name are not guessed and the report says so; a BOM in a URL list and
  a damaged .xml.gz are handled.
- `landscape.py`: D/A/CH, "D, A, CH" and DE-AT-CH count as DACH, and a
  custom numeric column works for the map.
- `contrast.py`: in grid mode a transparent colour is laid over the opaque
  one, and two transparent colours are listed as not compared.
- `references/voice-of-customer.md`: reading the sample bias, switching
  triggers, grouping themes into 3-6 needs with 2 linked quotes from 2
  sources each, a fix plan and angle built on needs, and a quote check
  before anything is sent.
- `reviews.py`: `--as-of` replaces `--today` (the old name still works;
  `as_of` in `--json`). Source names are evened out ("App Store" =
  app-store). JSON keys were only added, none renamed or removed.
- `themes.json`: `switch_patterns`, and "gekündigt" now counts for payments
  and cancelling.
- `references/legal-eu-dach.md` section 4 now spells out comparative
  advertising: the six conditions of § 6 (2) UWG, § 5 and § 5a UWG,
  verifiability (CJEU Lidl Belgium), dated like-for-like price comparisons,
  and use of the competitor's mark (CJEU O2 v Hutchison, L'Oréal v Bellure),
  with Austria § 2a UWG and Switzerland Art. 3 (1) lit. e UWG.
- Brand mode step 3 checks the new palette with contrast.py (`palette` and
  `pairs` in `teardown/brand.json`) instead of a manual contrast note, and
  targets WCAG 2.2 AA. The name check screens against every product in
  `competitors.csv` when discover ran.
- `references/recon.md` links discover (step 1), the visibility add-on
  (steps 2, 3 and 10), the build brief (step 7 and the output) and the
  battle card; step 8 documents the `source` and `checked` columns.
- `references/client-deliverables.md`: the report has a market overview,
  a "how it is found" section, why customers leave, the battle card for
  sales teams and a `--verify` step; every part not run says "not
  researched". The offer attaches the acceptance criteria.
- Templates: `features.csv` and the filled `features.example.csv` have the
  `source` and `checked` columns; `brand.json` has `palette` and `pairs` for
  contrast.py (sweep.py ignores them); `reviews.csv` has the optional
  `segment` column; `recon-map.md` the messaging and recent-moves tables;
  `visibility.md` local search and Core Web Vitals; `battlecard.md` the page
  formats, owner and review date, switching, FAQ and audit, a trademark line
  that says "registered" only after a dated register check, and the
  consumer gross-price reminder; `build-brief.md` separates the build
  target (WCAG 2.2 AA) from the BFSG reference (EN 301 549 / WCAG 2.1 AA).
- Legal wording: accessibility information under § 14 BFSG with Anlage 3
  (a gap is lawful only under the Act's exceptions), prior express consent
  for marketing email with double opt-in as the usual proof, a selection of
  compared features as allowed unless the left-out rows matter (Lidl
  Belgium), the trademark rule in visibility aligned with the comparison
  page exception, published maps without rating axes or the planned point,
  and ratings shown for the new product under § 5b (3) UWG.
- Build handoff: in the brief as first written every pre-launch gate row is
  "to run", even when parity.py or contrast.py ran while writing it (their
  readings go into the milestones and the accessibility checklist); a row
  changes only when that gate runs on the build. The visibility template
  and summary carry the full rule for the original's name: not in the new
  product's name, domain, ad text, titles or meta tags, except on a
  lawyer-reviewed comparison page.
- README, plugin and marketplace manifests describe the new modes, the
  worked example and the evals; version 1.1.0. The `.skill` build command
  leaves out `.pyc` and `.DS_Store` files.

## [1.0.1] - 2026-10-17

### Changed

- README and `SKILL.md` no longer describe Moatbreak as Claude-only. The skill
  uses the open Agent Skills format and installs into Codex, Cursor, Gemini
  CLI, GitHub Copilot and other agents as well as Claude.

### Added

- Install instructions for any agent with `npx skills add bogaja/moatbreak`,
  and a manual copy path for `.agents/skills/`.

## [1.0.0] - 2026-10-17

First public release.

### Changed

- New name: Moatbreak, skill ID `moatbreak`. The skill was previously used
  privately as `competitor-teardown` 1.1. The four modes, the references, the
  templates and the scripts are unchanged from that version apart from the
  name.
- The working folder for user data is still `teardown/`, so existing projects
  keep working.

### Added

- Claude Code plugin and marketplace manifests in `.claude-plugin/`, so the
  skill installs with `/plugin marketplace add bogaja/moatbreak`.
- GitHub Actions workflow that runs the 71 tests on Python 3.8 to 3.13.
- README with install instructions for claude.ai, Claude Code and manual
  copy, plus a short German section.
