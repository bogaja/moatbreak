---
name: moatbreak
description: Competitor teardown and rebuild planning. Use whenever the user names an existing app, SaaS, website or online shop and wants to build something like it, compete with it, find out what its users complain about, compare a rebuild against it, rebrand a clone of it, or estimate or quote such a project - even if they never say competitor analysis. Examples - "so etwas wie Calendly, aber für Friseure", "was nervt Kunden an Zalando", "Angebot für einen Shop wie X", "clone this app", "how close is our rebuild to the original". Four modes - recon (screens or page types, flows, data model, feature matrix with person-day and price estimate), voice of customer (ranked complaints and wishes from linked public reviews, English and German), parity (score, missing features, remaining effort) and brand (new name with DPMA/EUIPO screening, palette distance, leftover sweep). Clean-room rules and an EU/DACH legal checklist (UWG imitation, Impressum, DSGVO, BFSG) built in. Not for work without a named reference product.
license: MIT (see LICENSE and NOTICE.md)
---

# Moatbreak

Take a product apart to build a better one. The output is never a copy: it
is a map of what the original does, evidence of what its users hate, a plan
that fixes it, and a new identity that keeps a safe distance.

## Modes

| mode | use it when | read first |
| --- | --- | --- |
| **recon** | someone wants "something like X", a rebuild, or an offer for one | `references/recon.md` |
| **voice of customer** | "what do people hate about X", "is there a gap", "how do we position against X" | `references/voice-of-customer.md` |
| **parity** | a rebuild exists and the question is "how close are we, what is missing, how much work is left" | `references/parity.md` |
| **brand** | the new product needs a name, palette, voice, or a leftover check before launch | `references/brand.md` |

Read the reference of each mode you actually run, not all of them. Two more
references are shared:

- `references/legal-eu-dach.md`: read it before brand mode, before anything
  launches, and whenever the target market includes the EU, Germany, Austria
  or Switzerland. It holds the distance check, which decides how close is
  too close.
- `references/client-deliverables.md`: read it when the result goes to
  someone else (a client offer, a report, a pitch to a boss or investor), so
  it is something that can be sent. It says which modes a report needs; if
  one was not run, the report says "not researched" instead of guessing.

The full path is recon, then voice of customer, then the build (with
whatever build or design skills the session has), then parity, then brand
and the legal check. Any mode also runs on its own: voice of customer alone
is a good way to decide whether a product is worth building at all, and
recon plus the effort estimate is a complete offer.

## Where things go

Everything is written into a `teardown/` folder in the user's project (or
the working directory). Each mode reads what the previous one wrote. In this
skill, `$SKILL` means this skill's own folder (the one containing this
SKILL.md); scripts and templates live there, the user's data never does.

```
teardown/recon.md          product map (from $SKILL/templates/recon-map.md)
teardown/features.csv      feature matrix with effort (from $SKILL/templates/features.csv,
                           a filled example is in templates/features.example.csv)
teardown/screens/          reference screenshots of the original, never shipped
teardown/reviews.csv       collected reviews (from $SKILL/templates/reviews.csv)
teardown/themes.json       copy of $SKILL/scripts/themes.json, tuned to the category
teardown/feedback.md       ranked themes, from reviews.py
teardown/fixes.md          what they hate, what is missing, the fix plan, the angle
teardown/estimate.md       effort estimate for an offer, from parity.py --estimate-only
teardown/offer.md          the client offer (from $SKILL/templates/offer.md)
teardown/parity.md         parity score, missing list, remaining effort
teardown/brand.md          name, checks, palette, logo brief, voice
teardown/brand.json        what sweep.py must not find (from $SKILL/templates/brand.json)
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
  database.
- **Never fabricate.** No invented reviews, quotes, numbers, sources or check
  results. Every quote is verbatim and linked. If a source could not be
  reached, say so. A check nobody ran is marked "to run", never "clear".
- **Honest numbers.** State sample sizes, give effort as ranges, give a
  parity of 62 as 62.
- **Screenshots are reference.** They live in `teardown/screens/`, are used
  to compare layouts, and never go into the product or a public document.
- **The user decides, buys and signs.** Write names, records, commands and
  checklists; the user registers domains, enters payment
  details and files trademarks.
- **Write deliverables in the user's language.** German user, German
  reports (the scripts take `--lang de`). Keep code identifiers in English.

## Scripts

All standard-library Python 3.8+, no installs, no network access. Run them
from the user's project folder, with the script path inside `$SKILL`:

```bash
python3 $SKILL/scripts/reviews.py teardown/reviews.csv --lang de --target "X" --themes teardown/themes.json --out teardown/feedback.md
python3 $SKILL/scripts/parity.py teardown/features.csv --estimate-only --lang de --markdown --buffer 20 --overhead "QA=15,PM=10" --fixed "Setup=2-3" --day-rate 650 --out teardown/estimate.md
python3 $SKILL/scripts/parity.py teardown/features.csv --lang de --markdown --out teardown/parity.md
python3 $SKILL/scripts/imgdiff.py teardown/screens/S07.png teardown/new-screens/S07.png --out teardown/diffs/S07.png
python3 $SKILL/scripts/sweep.py . --config teardown/brand.json
```

| script | what it does |
| --- | --- |
| `reviews.py` | ranks review themes (pricing, bugs, UX, support, shipping, returns, checkout, ...) in English and German, keeps every quote verbatim with its link, keeps praise apart from complaints, flags thin themes and one-platform samples |
| `parity.py` | parity score weighted by must/should/could, missing list by priority, remaining effort as MVP / + should / + could in person-days and money, with contingency, overheads and fixed items; `--estimate-only` for offers |
| `imgdiff.py` | compares the layout of two screenshots while ignoring colour, so a rebrand does not count against parity |
| `sweep.py` | finds the original's names (with German spelling variants), domains and colours in the codebase, and warns on colours too close to theirs |

Never edit files inside `$SKILL`: copy `scripts/themes.json` to
`teardown/themes.json`, add the product category's own words there (for a
booking app: double booking, time zone, no-show) and pass `--themes`.
Tests: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s $SKILL/tests`.

## When there is no browser or web access

Ask the user for what you cannot fetch: screenshots of the key screens, a
screen recording, an export of reviews, the pricing page as PDF. Work from
that and mark everything you could not verify. Do not fill gaps from memory
and present them as findings; label anything from general knowledge as an
assumption, and set `original` to `unknown` in the feature matrix for every
row you could not verify. If nothing about the original can be read at all,
recon becomes a requirements draft (see "No sources" in
`references/recon.md`) and says so in its first line.

## Handing off

Recon output is written so a build can start from it: screen inventory,
flows, data model and a prioritised feature matrix. Use the session's build,
design or animation skills for the build itself, and come back to parity
mode with screenshots of the new product. Before launch, brand mode and the
distance check in `references/legal-eu-dach.md` are not optional.
