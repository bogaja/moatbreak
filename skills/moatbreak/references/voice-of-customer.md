# Voice-of-customer mode

A straight copy has no reason to exist. This mode finds the reason: what the
original's customers hate, in their own words, and turns it into fixes and a
position you can sell.

Output: `teardown/reviews.csv`, `teardown/feedback.md`, `teardown/fixes.md`,
new rows in `teardown/features.csv`.

## Rules that are not negotiable

- **Never fabricate.** No invented reviews, quotes, ratings, counts or
  sources. If a source cannot be reached, say so and move on. If there are
  14 reviews, say 14.
- **Every quote is verbatim and linked.** Copied exactly, with the URL of the
  review or thread. `reviews.py` drops any row without a link and never
  paraphrases or translates. If you translate a quote for a report, show the
  original next to it and label the translation.
- **Reading, not scraping.** Read review pages the way a person does and copy
  rows into the sheet, or use official feeds and APIs within their terms.
  Most review platforms forbid scraping in their terms, and a review corpus
  is a protected database in the EU, so collect a research sample, not a
  copy of their database.
- **Reviewers are research, not testimonials.** Their words never go on the
  new product's website or ads.
- **No fake reviews, ever.** Not for the new product, not against the
  original. Illegal in the EU (UWG Annex no. 23b/23c in Germany) and the US
  (FTC rule, 2024).

## Step 1: collect

Aim for 100+ reviews across at least three sources, recent first. Read the 3
and 4 star reviews too: "love it, but..." is where the best fixes hide. If
the user can only supply fewer, go ahead: state the sample size up front,
call every theme directional, and list collecting more as the first next
step.

| product type | sources |
| --- | --- |
| mobile app | App Store (per country; Apple's customer-reviews RSS feed `https://itunes.apple.com/{country}/rss/customerreviews/id={APP_ID}/sortBy=mostRecent/json`, use `de` for Germany, if it still responds), Google Play (sort by newest, filter by stars) |
| SaaS / B2B software | G2, Capterra (capterra.com.de for German reviews), OMR Reviews (strong for DACH B2B), GetApp, Trustpilot, Reddit, Hacker News (Algolia API `hn.algolia.com/api/v1/search?query=...`), the product's own feature-request board and its vote counts |
| online shop / D2C brand | Trustpilot, Trusted Shops, Google reviews of the business, product reviews on marketplaces (Amazon, idealo), Reddit, comments under the brand's social posts |
| local or service business | Google reviews, ProvenExpert, Yelp, sector portals (e.g. Jameda for health) |
| any | its changelog, so you do not "fix" what is already fixed |

Searches that find the honest ones: "X alternative", "switched from X",
"X vs", "X Erfahrungen", "X Alternative", "X kündigen", "X Probleme".

Each row in `teardown/reviews.csv` (from `$SKILL/templates/reviews.csv`):
`source,url,date,rating,text`, text copied
exactly. German headers and semicolon-separated Excel exports work too.
Ratings like `4,5`, `4/5`, `8/10` or `★★★★☆` are normalised to 1-5 stars.

## Step 2: tune the themes

`$SKILL/scripts/themes.json` ships with themes in English and German: price,
payments and cancellation, bugs, performance, data loss, UX, support,
login, notifications, ads, bad updates, privacy, shipping (including
shipping costs), returns, product quality, size and fit, checkout and
payment methods, integrations (including DATEV, lexoffice, sevdesk),
platforms, customisation, teams. Copy it into `teardown/themes.json` and add
the category's own words before running (for a booking app: double booking,
time zone, no-show; for a fashion shop: fabric, colour differs from the
photos). When you add a more specific theme, remove its words from the
general theme they were in, or the same review is counted twice. Pass it
with `--themes teardown/themes.json`.

## Step 3: rank

```bash
python3 $SKILL/scripts/reviews.py teardown/reviews.csv --lang de --target "X" \
  --themes teardown/themes.json --today 2026-10-17 --out teardown/feedback.md
```

(`--today` makes the run reproducible; the recency weighting depends on it.)

It weights low ratings and recent reviews higher, marks themes with fewer
than 3 reviews or one source as thin, warns when one platform supplies more
than 60% of the sample, and lists every request in the customers' own words.
Praise is kept apart: 4.5-5 star reviews never count as complaints, 4 star
reviews only when the sentence has a "but" (aber, leider, ...), and the
report lists what customers praise, which shows where not to attack. It also
lists ratings of 3 stars or less that matched no theme. Read that list by
hand: it is often where the real insight is. One review can match several
themes, so shares add up to more than 100%.

## Step 4: three lists

From `feedback.md`, write three ranked lists. Each item: the problem in one
line, number of reviews, number of sources, one or two linked quotes.

1. **What they hate.** Complaints about things the product does.
2. **What is missing.** Features people ask for by name.
3. **What is unsolved.** Whole jobs or groups the product ignores ("not built
   for teams", "useless for therapists", "no invoice purchase for B2B").
   These become positioning.

Thin themes are listed as thin. Three angry Reddit comments are not a trend.

## Step 5: the fix plan

Pick the top 5 to 8 by evidence times how cheaply they can be fixed. For
each: what to build or change, effort (XS-XL), and the evidence. Add each to
`teardown/features.csv` with `original` = `no` and `clone` = `no`, so
parity.py counts it as work and the offer includes it. If recon has not run
yet, create the file from `$SKILL/templates/features.csv` (header only). Pricing and billing complaints feed the
pricing of the new product.

## Step 6: the angle

Three positioning options, each grounded in a top theme:

```
For {who} who {hate this about the original, in plain words},
{new product} {does this instead}.
Evidence: {theme}, {n} reviews across {n} sources.
```

Recommend one. It drives the name and voice in brand mode and the headline
of the landing page. Never put the original's name in the new product's
name, ads or store listing; a factual comparison page is a legal question
(see `legal-eu-dach.md`, comparative advertising).

## Output

`teardown/reviews.csv`, `teardown/feedback.md`, `teardown/fixes.md` (three
lists, fix plan, angle), new rows in `features.csv`, and a summary that
states the sample size and the sources.
