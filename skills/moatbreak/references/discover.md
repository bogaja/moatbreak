# Discover mode (step 0)

Find the product to take apart when the user names a market instead of a
product: "Buchungs-App für Friseure", "a CRM for roofers", "Onlineshop für
Kaffee in Österreich". The result is a short, sourced list of reference
products and the user's choice among them. It is not market research for
its own sake: no market sizing in euros, no SWOT, no verdict on who "wins".
If the user asks how big the market is, give at most a sourced count of the
target businesses from official statistics (Destatis, Statistik Austria,
the Swiss BFS; the table, its year and the link), never a revenue estimate.

Run it only when no reference product is named. "Like Calendly, but for
hairdressers" names one: go straight to recon (`references/recon.md`) and
handle the niche there. Discover ends with the user's answer. Recon starts
with the products the user confirmed, never with the agent's own pick.

Output: `teardown/competitors.csv` (from `$SKILL/templates/competitors.csv`;
delete its sample row), then `teardown/landscape.md` and
`teardown/landscape.svg`, both written by `landscape.py`.

## Step 1: pin down the market

Agree on four facts in one message, or propose them and get a yes:

1. **Job**: the one thing the customer gets done ("salon clients book an
   appointment online, the salon fills its calendar").
2. **Customer**: who pays (salon owners with 1 to 10 chairs), and who uses
   it if that is someone else.
3. **Market**: countries and language (Germany only, DACH, EU). It decides
   which sources count and what `--market` checks.
4. **Type**: app, SaaS, website or shop, as in recon.

## Step 2: search wide, in the market's language

Aim for 8 to 15 names, so the filter has something to drop. Search results
and directory listings are leads. They are not evidence.

| where | how |
| --- | --- |
| web search in the customer's words | the trade's own terms in German and English ("Online-Terminbuchung Friseur", "Friseursoftware", "Kassensystem Friseursalon", "salon booking software"), spelling and regional variants (Friseur, Frisör; in Switzerland Coiffeur), plus "Österreich" or "Schweiz" |
| alternative and comparison pages | "X Alternative", "Alternative zu X", "X vs" for each name found; they surface products that do not rank on their own |
| software directories | OMR Reviews (strong for DACH B2B), Capterra Germany (capterra.com.de), GetApp, G2; filter by category and country |
| app stores | the German, Austrian or Swiss store (apps.apple.com/de, /at, /ch; Google Play with `gl=DE` and `hl=de`) |
| the trade itself | partner and member pages of trade associations, trade press, exhibitor lists of trade fairs |
| shops | marketplaces and price comparison sites (Amazon, idealo), the Trusted Shops directory |
| the user | "Which products do your customers mention, or switch from?" Users know the local player that search misses. |
| earlier teardown files | if voice of customer or visibility already ran: the alternatives named under "Why they leave" in `teardown/feedback.md` (where customers say they went, each with its review link) and the brands named in the AI-answer and search samples of `teardown/visibility.md` |

While reading, note the DACH signals: a German UI, prices in EUR or CHF
and whether VAT is included ("zzgl. MwSt."), an Impressum with a company
seat in Germany, Austria or Switzerland, German support, hosting in the EU.
The Impressum is a public page that names who is behind the product and
where; it is good evidence for the market column.

Budget: about three pages per candidate (home, the page that shows job and
customer, pricing). Deeper reading is recon's job.

## Step 3: record what you read

One row per product in `teardown/competitors.csv`:

| column | what goes in |
| --- | --- |
| `name`, `url` | product name and homepage |
| `evidence_url` | the page that shows what it does and for whom, ideally its own feature or industry page ("for hair salons"); a directory profile only if its own site does not say. Without it the row is unverified |
| `category`, `customer` | in the product's own words, from that page |
| `market`, `languages` | country codes in capitals (DE, AT, CH) or DACH, EU, global; UI languages (de, en) |
| `price_from`, `price_model`, `price_url` | the entry price as printed ("ab 29 € / Monat", "kostenlos"), what it is per (location, seat, booking), net or gross, and the pricing page |
| `axis_x`, `axis_y`, `axis_url` | two numbers for the map (step 5) and the page they come from; if x and y come from two pages, both URLs separated by a space, x first |
| `status` | from step 4 |
| `read_on` | the date the pages were read, YYYY-MM-DD |
| `notes` | one line: why it fits, or which criterion it fails |
| `company`, `seat`, `founded`, `size`, `company_url` (optional) | who is behind the product, as printed on a public page: the Impressum (company and seat), the Handelsregister or Unternehmensregister entry, Firmenbuch or Zefix, or the company's own press page (founded, team size as it states it); `company_url` holds the page or pages, separated by a space. `landscape.py` lists these under "Companies" and marks facts without a source. No funding rounds or revenue from press rumours or memory |

A cell you could not read stays empty. Never estimate a price or fill a
cell from what you remember about a product. This holds for every row,
not only the proposed ones, and for every part of a cell: a price the page
does not print (a monthly price when it shows only the yearly one, a
"vermutlich" or "ca.") stays out, and `landscape.py` flags such words as a
guess. A product known only from
general knowledge may be listed, because the user may know it, but without
`evidence_url`: `landscape.py` marks it unverified, lists it last and never
proposes it.

## Step 4: filter

| # | criterion | passes when | evidence |
| --- | --- | --- | --- |
| 1 | same job | it does the core job end to end, not one part of it (a calendar alone is not booking software) | `evidence_url` |
| 2 | same customer | it sells to the user's customer (hair salons), not to another one (clinics, restaurants) | `evidence_url`, industry pages, plan names |
| 3 | active | a public sign of life in the last 12 months: a changelog entry, an app store update, a dated blog or press post | the dated page, named in `notes` ("active: changelog 2026-09") |
| 4 | readable sources | the homepage and at least one feature, help or pricing page open without a login | the URLs in the row |
| 5 | user's market | it sells there: country pages, currency, language, Impressum | `market`; `landscape.py --market` checks it |

Then set `status`:

- `fit`: passes all five.
- `adjacent`: the same job for a broader or different customer (a generic
  booking tool, a spreadsheet template, a marketplace). It stays in the
  matrix because customers compare against it, but it is not proposed.
- `out`: fails a criterion; `notes` says which ("inactive: last update
  2023-04", "US only, no EUR prices").
- `candidate`: not checked yet. Nothing should still be a candidate when
  the user sees the list.
- `confirmed`: only after the user picks it in step 7.
- `planned`: optional, the user's own product as intended, for the map. It
  is a plan, not a finding, and needs no evidence.

German values work too: Kandidat, passt, angrenzend, raus, bestätigt,
geplant.

## Step 5: choose two axes

A positioning map is only as honest as its axes. Pick two numbers that can
be read from public pages, by the same rule for every row:

- **Price from**: entry plan per month (`price_from`, sourced by
  `price_url`). Compare like with like and say in the label whether net or
  gross. A price per booking or per seat is not a monthly price: leave the
  cell empty rather than convert it. Keep one currency; convert CHF only
  with a rate from a linked source (the ECB reference rate) and say so in
  `notes`.
- **Breadth**: how many of the niche's core jobs the public pages list. Fix
  the list first (six to ten jobs, from step 1 and the niche's needs), write
  it into the report, and count the same list for every row.
- **Reviews**: the number of reviews or the rating on one named platform
  (Capterra Germany, OMR Reviews, the German App Store), read on one day.
- **Reach**: integrations listed, countries served, UI languages.

Never a gut score ("ease of use 1-10") and never a weighted composite. If a
number cannot be read for a row, leave it empty: the row is listed as "not
on the map" instead of being placed by guess. Put the rule into the axis
label (`--y-label "Kernaufgaben laut Website (von 8)"`).

## Step 6: run landscape.py

```bash
python3 $SKILL/scripts/landscape.py teardown/competitors.csv --lang de --market DACH \
  --title "Buchungs-App für Friseure" --svg teardown/landscape.svg \
  --x price_from --y axis_y --x-label "Preis ab (EUR/Monat, netto)" \
  --y-label "Kernaufgaben laut Website (von 8)" --out teardown/landscape.md
```

It sorts verified rows in the user's market first, then by status, and puts
unverified rows last. It proposes at most five verified rows marked fit or
confirmed, marks prices and axis values that have no source, checks the
market column against `--market` (DACH = DE, AT, CH; EU = the 27 member
states; global = everywhere), lists filtered-out rows with their reason,
and draws the map: filled points are sourced, hollow dashed points are not
(and are not findings), a ring marks a confirmed product, a diamond the
planned position. Fix everything under "Fix in the CSV" and run it again
before showing anything. `--json` gives the same result for further work.

## Step 7: propose and wait

Show the user, in their language:

1. the proposal: 3 to 5 products, each with its link, its evidence link and
   a one-line reason. Fewer than three only when the market is thin, and
   then say so.
2. the landscape matrix and the map.
3. the adjacent alternatives and what was filtered out, one line each.
4. the question: which one (or up to three) to tear down, and is a product
   missing?

Then stop. Do not start recon on your own pick, and do not fall back to the
first row if the user does not answer. When the user names a missing
product, read it, add a row and run step 6 again. When the user confirms,
set those rows to `confirmed`, run `landscape.py` once more, and start
recon.

## Handing off to recon

- One confirmed product is recon's reference. Several follow recon's
  "several references" rule.
- The job, customer and market from step 1 become recon's scope, and the
  niche delta in recon starts from what the landscape showed.
- `evidence_url` and `price_url` with their `read_on` dates are the first
  rows of recon's sources table. Re-read anything older than a month.
- Voice of customer can start from the directory pages found here. Brand
  mode screens the new name against every name in `competitors.csv`, not
  only the reference.

## No browser or web access

Ask the user which products they know, with links. Products you know only
from general knowledge go into the CSV without `evidence_url`, and the user
is told they are unchecked; `landscape.py` will not propose them. If the
user confirms one anyway, that is their decision: recon then works from
what the user can supply, and starts as a requirements draft if nothing can
be read ("No sources" in `references/recon.md`).

## In client material

The matrix and the map can go into a report as the market overview: every
cell links to its source, and unverified rows are marked or left out. A
map with a review or rating axis, or with the `planned` point, stays
internal to the client: star ratings of other products do not go on a
public page, and a planned position is a claim about something not
shipped. A published map uses only verified, dated, non-review axes. A
published comparison (an "alternatives" page, a sales deck, a public map)
is comparative advertising: it must compare relevant, verifiable facts
objectively (§ 6 UWG, `references/legal-eu-dach.md` section 4) and needs a
legal review before it goes out.

## Output

`teardown/competitors.csv`, `teardown/landscape.md`, `teardown/landscape.svg`,
and the user's confirmed choice. Next step: recon.
