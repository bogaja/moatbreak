---
name: moatbreak
description: Competitor teardown and rebuild plan for apps, SaaS, sites and shops. Use when the user names a product to build like or compete with (even without saying competitor analysis), or only a niche to build for. E.g. "so etwas wie Calendly, aber für Friseure". Not for market research without a build or compete goal.
license: MIT (see LICENSE and NOTICE.md)
---

# Moatbreak

Take a product apart to build a better one. The output is never a copy: it
is a map of what the original does, evidence of what its users hate, a plan
that fixes it, and a new identity that keeps a safe distance.

## Modes

| mode | use it when | read first |
| --- | --- | --- |
| **discover** (step 0) | only a niche or market is named, no product ("Buchungs-App für Friseure", "a CRM for roofers"); it ends with the user's pick | `references/discover.md` |
| **recon** | someone wants "something like X", a rebuild, or an offer for one | `references/recon.md` |
| **visibility** (recon add-on) | "how is X found", which markets, keywords or AI answers; any recon of a website, shop or SaaS marketing site | `references/visibility.md` |
| **voice of customer** | "what do people hate about X", "why do people leave X", "is there a gap", "how do we position against X" | `references/voice-of-customer.md` |
| **build handoff** | recon is done and the build is about to start: milestones, acceptance criteria, data model and API sketch, stack questions, accessibility (BFSG, WCAG 2.2 AA), test plan, pre-launch gate | `references/build-handoff.md` |
| **parity** | a rebuild exists and the question is "how close are we, what is missing, how much work is left" | `references/parity.md` |
| **brand** | the new product needs a name, palette, voice, or a leftover check before launch | `references/brand.md` |
| **battle card** | sales needs a battle card against X, objection handling, a SWOT against X, or a public "X alternative" / "X vs us" page, or an audit of such pages | `references/battlecard.md` |
| **launch** | the rebuild is about to go live: landing and pricing pages from the angle, store listing texts, design tokens from the new palette | `references/launch.md` |

Read the reference of each mode you actually run, not all of them. Two more
references are shared:

- `references/legal-eu-dach.md`: read it before brand mode, before any
  comparison page or ad that names the competitor, before anything
  launches, and whenever the target market includes the EU, Germany, Austria
  or Switzerland. It holds the distance check, which decides how close is
  too close.
- `references/client-deliverables.md`: read it when the result goes to
  someone else (a client offer, a report, a pitch to a boss or investor), so
  it is something that can be sent. It says which modes a report needs; if
  one was not run, the report says "not researched" instead of guessing.

The full path is discover (only when no reference product is named), then
recon (with the visibility add-on when the original lives on search), then
voice of customer, then the build brief and the build itself (with whatever
build or design skills the session has), then parity, then brand, launch and
the legal check. Once voice of customer has run (and parity, if the product
exists), battle card mode turns `feedback.json` and `features.csv` into a
sales card, and on request into a comparison page draft for a lawyer to
check. Any mode also runs on its own: voice of customer alone is a good way
to decide whether a product is worth building at all, and recon plus the
effort estimate is a complete offer.

## No build or compete goal

If the request only names a product or a market (a price lookup like "what
does Calendly cost", market research for a paper, a brand for a new business
with no original), no mode runs: no `teardown/` folder, no script, no
products proposed to rebuild. Ask at most once whether the user plans to
build or compete; otherwise answer the question as asked. The honesty rules
still hold there: a price or plan comes from the pricing page with its link
and the date it was read, a market figure from a named source with its date,
and what could not be read says "could not be checked". Nothing from memory
is given as current.

## Where things go

Everything is written into a `teardown/` folder in the user's project (or
the working directory). Each mode reads what the previous one wrote. In this
skill, `$SKILL` means this skill's own folder (the one containing this
SKILL.md); scripts and templates live there, the user's data never does.

```
teardown/competitors.csv   candidate products with evidence links, discover only
                           (from $SKILL/templates/competitors.csv)
teardown/landscape.md      landscape matrix and proposal, from landscape.py
teardown/landscape.svg     positioning map, from landscape.py --svg
teardown/recon.md          product map (from $SKILL/templates/recon-map.md)
teardown/features.csv      feature matrix with effort (from $SKILL/templates/features.csv,
                           a filled example is in templates/features.example.csv; the
                           columns source,checked hold the evidence for claims about the original)
teardown/screens/          reference screenshots of the original, never shipped
teardown/sources.csv       url and read_on for every file in screens/ and proof/, checked by
                           sources.py (from $SKILL/templates/sources.csv)
teardown/visibility/       public files read by hand: robots.txt, sitemap.xml (and child
                           sitemaps), llms.txt, SEO tool exports
teardown/sitemap.md        page types, sections, language folders and hreflang, from sitemap.py
teardown/seo.md            keyword themes, branded share, top pages, keyword gap, from seo.py
teardown/visibility.md     markets, key pages, search data, local search, AI-answer sample
                           (from $SKILL/templates/visibility.md)
teardown/reviews.csv       collected reviews, optional segment column
                           (from $SKILL/templates/reviews.csv)
teardown/themes.json       copy of $SKILL/scripts/themes.json, tuned to the category
teardown/feedback.md       ranked themes, sample bias by source, why they leave, from reviews.py
teardown/feedback.json     the same analysis as JSON (reviews.py --json), read by battlecard.py
teardown/fixes.md          needs (3-6, two linked quotes from two sources each), fix plan,
                           angle; checked with reviews.py --verify
teardown/estimate.md       effort estimate for an offer, from parity.py --estimate-only
teardown/offer.md          the client offer (from $SKILL/templates/offer.md)
teardown/offer-notes.md    internal notes for the offer, never sent to the client
teardown/report.md         the client report (references/client-deliverables.md)
teardown/report.html       the report and the teardown files as one offline HTML page,
                           from report.py
teardown/build-brief.md    milestones, acceptance criteria, data model, stack, accessibility,
                           test plan, launch gate (from $SKILL/templates/build-brief.md)
teardown/new-screens/      screenshots of the rebuild, for parity
teardown/diffs/            imgdiff.py images and JSON
teardown/parity.md         parity score, missing list, remaining effort
teardown/brand.md          name, checks, palette, logo brief, voice
teardown/brand.json        what sweep.py must not find, and the new palette for contrast.py
                           (from $SKILL/templates/brand.json)
teardown/contrast.md       palette contrast check, from contrast.py
teardown/battlecard.md     sales battle card with SWOT appendix, from battlecard.py
                           (layout in $SKILL/templates/battlecard.md)
teardown/compare.md        comparison page draft (second part of $SKILL/templates/battlecard.md)
teardown/proof/            dated copies of the sources behind verified claims, never published
teardown/launch.md         landing and pricing page copy, design tokens (references/launch.md)
teardown/listing.json      store listing texts, checked by listing.py
                           (from $SKILL/templates/listing.json)
teardown/legal.md          distance check and launch checklist
```

## Ground rules

These exist because the whole point is a product the user can sell without
being sued or embarrassed. Explain them to the user when they come up; do
not just refuse.

- **Rebuild what it does, not what it owns.** Functions, flows and common UI
  patterns are free to rebuild: copyright protects code and expression, not
  ideas or functionality. Code, texts, images, icons, logos, names and the
  distinctive overall look belong to the original. Write everything fresh.
  Never call or market the new product a clone, copy or "like X, only
  cheaper": presenting it as an imitation of a branded product is unlawful
  comparative advertising (§ 6 (2) no. 6 UWG). When the user says "clone",
  say so and use the new name or "our product" instead.
- **Public sources and the user's own account only.** No logging into
  accounts that are not the user's, no paywall tricks, no reading or saving
  the original's code bundles, no capturing private API calls. In Germany,
  knowledge obtained dishonestly is itself grounds for an unfair-imitation
  claim, so this rule protects the user, not just the original. If the
  user's account terms forbid building a competitor with it, say so and work
  from public sources.
- **Reading, not scraping.** Read pages the way a person does. Use official
  feeds and APIs within their terms. No crawlers against sites whose terms
  forbid it, and no bulk copying of the original's catalogue or review
  database. When the user wants the original's listings, catalogue or
  customer data in the new product, decline and name the legal way in: the
  new product's own users enter their data or import their own export
  (onboarding, a CSV import), or an official API or partner feed used
  within its terms.
- **Never fabricate.** No invented reviews, quotes, numbers, sources or check
  results. Every quote is verbatim and linked. If a source could not be
  reached, say so. A check nobody ran is marked "to run", never "clear".
  Before a document that quotes reviews leaves the session (fixes.md, an
  offer, a battle card), run `reviews.py --verify` on it; it fails on any
  quote that is not word for word in the review behind its link.
- **Reviewers are people.** Reviews, quotes and saved AI answers are
  personal data under the DSGVO: keep no author names or handles, cut names
  of people out of quotes with "...", keep `teardown/` out of public
  repositories, and delete the sample when the project ends
  (`references/legal-eu-dach.md`, section 6).
- **Honest numbers.** State sample sizes, give effort as ranges, give a
  parity of 62 as 62. A search or traffic number comes from a named tool
  with its date, or it says "not measured". Copy a script's numbers as it
  prints them, in the answer too: no rounding (76,2 stays 76,2), and no
  adding up of counts it keeps apart (one review can sit in two themes).
- **Legal points are flags, not advice.** Whenever an answer raises legal
  points, say in the answer itself, not only in `teardown/legal.md`, that
  this is a checklist and not legal advice, and that a lawyer reviews it
  before anything is published or launched.
- **Screenshots are reference.** They live in `teardown/screens/`, are used
  to compare layouts, and never go into the product or a public document.
- **The user decides, buys and signs.** Write names, records, commands and
  checklists; the user picks the reference products, registers domains,
  enters payment details and files trademarks.
- **Write deliverables in the user's language.** German user, German
  reports (the scripts take `--lang de`). Keep code identifiers in English.

## Scripts

All standard-library Python 3.8+, no installs, no network access. Run them
from the user's project folder, with the script path inside `$SKILL`:

```bash
python3 $SKILL/scripts/landscape.py teardown/competitors.csv --lang de --market DACH --title "Buchungs-App für Friseure" --svg teardown/landscape.svg --x price_from --y axis_y --x-label "Preis ab (EUR/Monat, netto)" --y-label "Kernaufgaben laut Website (von 8)" --out teardown/landscape.md
python3 $SKILL/scripts/sitemap.py teardown/visibility/*.xml --lang de --as-of 2026-10-17 --out teardown/sitemap.md
python3 $SKILL/scripts/seo.py teardown/visibility/semrush.csv --tool semrush --database "Google DE, de" --brand "X" --as-of 2026-10-17 --lang de --out teardown/seo.md
python3 $SKILL/scripts/reviews.py teardown/reviews.csv --lang de --target "X" --themes teardown/themes.json --as-of 2026-10-17 --out teardown/feedback.md
python3 $SKILL/scripts/reviews.py teardown/reviews.csv --themes teardown/themes.json --as-of 2026-10-17 --json --out teardown/feedback.json
python3 $SKILL/scripts/reviews.py teardown/reviews.csv --verify teardown/fixes.md --lang de
python3 $SKILL/scripts/parity.py teardown/features.csv --estimate-only --lang de --markdown --buffer 20 --overhead "QA=15,PM=10" --fixed "Setup=2-3" --day-rate 650 --out teardown/estimate.md
python3 $SKILL/scripts/parity.py teardown/features.csv --lang de --markdown --out teardown/parity.md
python3 $SKILL/scripts/imgdiff.py teardown/screens/S07.png teardown/new-screens/S07.png --out teardown/diffs/S07.png
python3 $SKILL/scripts/contrast.py --palette teardown/brand.json --lang de --markdown --out teardown/contrast.md
python3 $SKILL/scripts/sweep.py . --config teardown/brand.json
python3 $SKILL/scripts/battlecard.py --feedback teardown/feedback.json --features teardown/features.csv --target "X" --ours "Y" --as-of 2026-10-17 --lang de --out teardown/battlecard.md
python3 $SKILL/scripts/sources.py teardown --as-of 2026-10-17 --lang de
python3 $SKILL/scripts/listing.py teardown/listing.json --config teardown/brand.json --lang de --markdown --out teardown/listing.md
python3 $SKILL/scripts/report.py teardown --lang de --title "Wettbewerbsanalyse: X" --as-of 2026-10-17 --out teardown/report.html
```

| script | what it does |
| --- | --- |
| `landscape.py` | landscape matrix from `competitors.csv`: verified rows in the user's market first, rows without an evidence link marked unverified and never proposed, prices and axis values without a source marked, guessed prices ("vermutlich", "ca.") flagged, market check (`--market DACH`), a proposal of up to five verified fits for the user to confirm, and a positioning map as a standalone SVG on two numeric axes (`--svg --x --y`) |
| `sitemap.py` | counts the original's public pages from a saved sitemap.xml, sitemap index, .xml.gz or URL list: page types (blog, product, category, help, pricing, comparison, integrations, ...), sections, language and country folders, hreflang; flags partial indexes and stamped lastmod dates; never fetches anything |
| `seo.py` | reads a keyword export from Semrush, Ahrefs, DataForSEO, SISTRIX, Similarweb or Search Console: keyword themes (alternatives and vs, branded, local, how-to, category), branded share, top keywords and pages, and with `--ours` the keyword gap; every number labelled with tool, database and the export date (`--as-of`, required); estimates nothing |
| `reviews.py` | ranks review themes (pricing, bugs, UX, support, shipping, returns, checkout, ...) in English and German, keeps every quote verbatim with its link, keeps praise apart from complaints, shows the sample by source with its bias (one platform over 60%, a source 1 star or more off the average, dates bunched in the last 90 days or older than `--months`) and by reviewer segment where the platform shows one ("who says it"), lists why people leave with the alternative they name; `--verify` checks that every linked quote in a report stands word for word, whole words only, in the reviews; `--as-of` for reproducible runs |
| `parity.py` | parity score weighted by must/should/could, missing list by priority, remaining effort as MVP / + should / + could in person-days and money, with contingency, overheads and fixed items; `--estimate-only` for offers |
| `imgdiff.py` | compares the layout of two screenshots while ignoring colour, so a rebrand does not count against parity |
| `contrast.py` | WCAG 2.2 contrast ratio for colour pairs or a palette (`palette` and `pairs` in `teardown/brand.json`): AA and AAA for text and large text, 3:1 for UI components, never rounded up to pass; for every failing pair the nearest darker and lighter variant that passes, calculated not guessed; exit 1 on a fail |
| `sweep.py` | finds the original's names (with German spelling variants), domains and colours in the codebase, and warns on colours too close to theirs |
| `battlecard.py` | one-page sales battle card from `feedback.json` and `features.csv`: weak themes with verbatim linked quotes, praise not to attack, our differentiators, objection stubs marked "to write", a SWOT whose every line cites its source row or theme; every claim about the competitor tagged verified / reported / assumed with source and date, checks older than 90 days flagged stale, and the claims fit for a comparison page (verified, fresh, public link) with a warning when the table shows only rows we win |
| `sources.py` | checks the paper trail: every screenshot in `teardown/screens/` and every proof copy in `teardown/proof/` needs a row in `teardown/sources.csv` with its URL and the day it was read; exit 1 on a file without one, a bad URL or date, or a row whose file is gone |
| `listing.py` | App Store and Google Play texts against the stores' limits (name and subtitle 30, keywords 100, promotional text 170, description 4000; title 30, short 80, full 4000), empty fields, and the original's names from `brand.json`, with German spelling variants and near spellings; exit 1 on a fail |
| `report.py` | the teardown's Markdown files as one self-contained, accessible HTML page for the client (`--lang de`): the written report first, the map inlined, the battle card marked internal, "not researched" for every mode that did not run; no external assets |

Never edit files inside `$SKILL`: copy `scripts/themes.json` to
`teardown/themes.json`, add the product category's own words there (for a
booking app: double booking, time zone, no-show) and the category's leaving
words to `switch_patterns`, in the first person like the shipped ones (for a
shop: I'm never ordering again, ich bestelle jetzt bei {alt}), and pass
`--themes`.
Tests: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s $SKILL/tests`.

## Examples and evals

- `$SKILL/examples/`: a complete worked run for a German user (so its
  deliverables are in German), with its input files, the outputs the scripts
  produce from them, and the files the agent writes (recon, fixes, build
  brief, brand, legal). Read it when unsure what a finished file should look
  like; never copy its data into a user's teardown.
- `$SKILL/evals/evals.json`: test prompts with the behaviour expected of the
  agent, for checking the skill's output (not only its scripts) after a
  change.

## When a browser is available

Use the session's browser tools (Claude in Chrome, a Playwright MCP server,
or whatever the session offers) to read pages the way a person does, one at
a time, within the source's terms; no crawling, no logging into accounts
that are not the user's.

- **Screenshots** of the screens in the recon inventory go to
  `teardown/screens/` at the two viewports parity mode compares, 1440x900
  and 390x844, named by screen ID and width (`S07-booking-1440.png`).
- **Proof copies**: for every claim that becomes `verified` (a `source` and
  `checked` in `features.csv`, a price on a battle card), save the page as a
  dated PDF in `teardown/proof/` (`2026-10-17-pricing.pdf`).
- **The paper trail**: one row per file in `teardown/sources.csv` (file, url,
  read_on), then `sources.py teardown --as-of {today}`; it exits 1 while any
  file has no URL and date. A screenshot without a source is not evidence.
- The scripts stay offline on purpose: the agent fetches, the scripts check,
  and nothing needs an API key.

## When there is no browser or web access

Ask the user for what you cannot fetch: screenshots of the key screens, a
screen recording, an export of reviews, the pricing page as PDF, the saved
sitemap. Work from that and mark everything you could not verify. A mode
that cannot run without that material is marked "to run" in the answer.
Do not fill gaps from memory and present them as findings; label anything
from general knowledge as an assumption to check, and set `original` to
`unknown` in the feature matrix for every row you could not verify. If nothing about the
original can be read at all, recon becomes a requirements draft (see "No
sources" in `references/recon.md`) and says so in its first line. In
discover, products known only from general knowledge go into
`teardown/competitors.csv` without `evidence_url`; `landscape.py` lists them
as unverified and never proposes them.

## Handing off

Recon output is written so a build can start from it. Before the build,
write the build brief (`references/build-handoff.md`): milestones from the
matrix priorities, Given/When/Then acceptance criteria for every must
feature, a data model and API sketch, the stack questions to ask the user,
the accessibility checklist (BFSG, EN 301 549, WCAG 2.2 AA, with
contrast.py), a test plan and the pre-launch gate. If visibility ran, the
brief keeps the search rows the build must not lose (pages per language
with hreflang, structured data, sitemap and robots.txt, redirects). Hand the
build the needs from `teardown/fixes.md`, not the raw keyword themes. Then
use the session's build, design or animation skills for the build, one
milestone at a time, and come back to parity mode with screenshots of the
new product. Before launch, the gate in the brief (parity, brand mode,
contrast.py, sweep.py, listing.py for a store app, and the distance check in
`references/legal-eu-dach.md`) is not optional; in the brief as first
written every gate row is "to run". `references/launch.md` covers
the landing and pricing pages and the store texts.
