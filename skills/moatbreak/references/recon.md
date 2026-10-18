# Recon mode

Map the original so a better version can be planned, built and priced.
Everything else reads what this writes, so take the time here.

Output: `teardown/recon.md` (template `$SKILL/templates/recon-map.md`),
`teardown/features.csv` (template `$SKILL/templates/features.csv`; a filled
example is `features.example.csv`), reference screenshots in
`teardown/screens/`, and for offers `teardown/estimate.md`. With the
visibility add-on also `teardown/visibility.md` and `teardown/sitemap.md`.

## Step 1: scope

Agree on four things, or propose answers and get a yes:

1. **Which product, which type, which platform.** App (iOS, Android), SaaS
   (web app), website (lead generation, service business, content), or
   online shop (and on which platform, if visible). Each type has its own
   inventory below. If the user named only a niche or a market and no
   product, run discover first (`references/discover.md`). Recon starts with
   the product(s) the user confirmed there, and their `evidence_url` and
   `price_url` rows (with `read_on`) open the sources table in step 2.
2. **Which slice.** "All of Notion" is not a project; "pages, blocks and
   sharing" is. Default to the core loop: the one flow people pay for. For a
   shop: browse, product page, cart, checkout.
3. **Who it is for.** The user's own product, a client, a niche, a market
   (DACH, EU, US). The market decides the legal checklist and the review
   sources.
4. **What the result is for.** A build plan, an offer for a client, or a
   go/no-go decision. An offer needs the effort column; a go/no-go may need
   only steps 1, 2 and 9 plus voice of customer.

**Several references** ("like Treatwell or Calendly", or several products
confirmed in discover): map each one briefly, then merge into one feature
matrix. `original` is `yes` if any of them has it; the notes name which
("Treatwell, Calendly"). Signature elements are collected from all of them.
More candidates turn up along the way: the rivals on the original's
comparison pages, the brands named in the AI-answer and search samples
(`references/visibility.md`, steps 6 and 7), and the alternatives named
under "Why they leave" in `teardown/feedback.md`, each with the review link
that names it. The user confirms them before any is mapped.

**"Like X, but for niche Y"**: the niche matters more than X. After the
inventory, add a niche delta: what the niche needs that X lacks (for hair
salons: processing time during which the stylist is free, several services
in one booking, stylist levels with different prices, allergy notes), and
what X has that the niche does not need. Niche rows go into the matrix with
`original` = `no`.

**No sources** (no web access and nothing from the user): recon becomes a
requirements draft. Say so in the first line of `recon.md`, set every
`original` to `unknown`, give every evidence line as "assumption", and list
the sources still to read as the first next step. Offers based on a draft
carry wider ranges and say why.

## Step 2: sources

Build a sources table first, with a URL and the date read on every row. In
order of value:

| source | what it gives you |
| --- | --- |
| help center / docs / FAQ | the most complete feature list there is, settings, limits |
| pricing page | which features matter (they are gated), plan limits, the price anchor |
| changelog / release notes | what is new, what the team thinks is important |
| app store listing | screenshots of key screens, the pitch, ratings, "what's new" |
| public walkthrough videos | real flows, click by click |
| marketing site | positioning and the core loop in their words |
| robots.txt and sitemap.xml | page types and their counts, language folders, what is hidden from search; run `sitemap.py` on them (`references/visibility.md`) |
| key pages' titles, meta descriptions, structured data | the words it bets on and how it wants to be found (`references/visibility.md`, step 3) |
| the user's own account or test order | every state, driven by the user |
| public API docs | the data model, almost for free |
| shop: shipping, returns, payment and terms pages | the commercial promise customers compare |
| shop: a real purchase or newsletter signup by the user | checkout, transactional emails, abandoned-cart flow |

If discover ran, start the table from `teardown/competitors.csv` and re-read
anything older than a month. For a website, a shop or a SaaS marketing
site, run the visibility add-on (`references/visibility.md`) next to this
step: it reads the public files above and samples search and AI answers.

**Messaging.** While the marketing site and the app store listing are open,
fill the messaging table in `recon.md`, one row per reference product:

| column | what goes in |
| --- | --- |
| hero claim | the main headline and the line under it, verbatim, with the URL and the date read |
| audience signal | who the page speaks to, in its own words ("für Salons mit Team", "Enterprise", the industries in the navigation) |
| promise type | saves time, saves money, more revenue, fewer no-shows or errors, easier, control, trust and compliance, or another one, named |
| what it leaves out | a need from `teardown/fixes.md` the claim does not touch, with the need's number; "not researched" until voice of customer has run |

Their claim is quoted for the analysis, never reused: the new product's
headline is written fresh from the angle (voice of customer step 8), and
the battle card's "In one line" aims at what the claim leaves out.

**Recent moves.** From the changelog, the pricing page, the press page and
the app store's version history, the dated moves of the last 12 months:
a price change, a shipped feature, a new market or language, a new plan,
a partnership, funding, as the company itself announced it. One row each
with the date, what changed and the link. They feed the battle card: a
move that touches a verified row in `features.csv` makes that row due for
a recheck, and a move that closes one of our gaps or copies a
differentiator is a threat in the SWOT. Only public, dated sources; no
rumours, no guesses about plans.

## Step 3: inventory

Use the inventory that fits the product type. IDs are stable (S01, S02...);
every other file refers to them.

**App or SaaS: screens.**
`ID | screen | route or how to reach it | purpose | key components | states seen`

**Website: page templates.** Home, service or product pages, landing pages,
about, proof (cases, testimonials), blog or resources, contact, legal pages.
For each: purpose, main call to action, forms (which fields), proof
elements, and where it sits in the navigation.

**Online shop: page types.** Home, category listing (filters, sorting,
pagination), product page (gallery, variants, price display, stock, delivery
time, reviews, cross-sell), search, cart (shipping threshold, coupon field),
checkout (steps, guest checkout, address, shipping options, payment methods
such as PayPal, Klarna, Kauf auf Rechnung, SEPA, Apple Pay), account, order
tracking, returns portal. Note the platform if it is publicly visible (a
"powered by" line, the CDN host in image links); never copy theme or app
code.

For a website, a shop or a SaaS marketing site, save the sitemap and run
`sitemap.py` first (`references/visibility.md`, step 2). Every page type
with pages is one template to inventory, and the counts are the content
volume (catalogue import, help articles, programmatic pages).

States matter for all types: empty, loading, filled, error, no permission,
out of stock, mobile. An empty state you did not record is an empty state
nobody will build.

## Step 4: flows

F01, F02... Each is a goal and the screens or pages it passes through:

```
F01 Guest books a meeting
    S07 booking page -> S08 pick a time -> S09 details form -> S10 confirmed
    happy path clicks: 4
    edge: no slots this week, different time zone, slot taken while filling the form
```

For a shop, the purchase flow is F01 and the clicks from product page to
"order placed" are the number to beat. Count the clicks on every happy
path.

## Step 5: components

Every repeated UI part: buttons, inputs, date pickers, modals, tables,
toasts, navigation, product cards, filters. Name, variants, states, where
used. This becomes the design system's component list.

## Step 6: signature elements

List what makes the original recognisable at a glance: a mascot, an unusual
colour pair, a custom typeface, a distinctive layout of the main screen, a
memorable interaction, a slogan, product names. These are the elements that
give it its "competitive individuality" (wettbewerbliche Eigenart), which is
what imitation law protects. They go into `features.csv` as `skip` rows with
the reason "signature element, do not imitate" and into `brand.json` later.
Rebuilding the function behind a signature element is fine; rebuilding its
look is not.

## Step 7: inferred data model

Entities, fields and relationships, each with its evidence and confidence:

```
Booking  id, event_type_id, start_at, end_at, guest_name, guest_email,
         status (confirmed | cancelled | rescheduled), answers (json)
         evidence: S09 form fields, S10 confirmation, help article "Cancel a booking"
         confidence: high
```

Mark guesses as guesses. Note personal data and especially health data
(allergies, treatments, notes about a person's body) here: it changes the
legal checklist. The build brief (`references/build-handoff.md`, step 3)
turns this model into the data model and API sketch the build starts from,
so keep evidence and confidence on every entity.

## Step 8: feature matrix

`teardown/features.csv` with columns
`feature,area,priority,original,clone,effort,notes,source,checked`.

- **priority**: must / should / could (German muss / soll / kann works).
  Must = without it the core loop does not work or nobody would switch.
- **clone**: starts at `no`; `skip` for anything out of scope, with a reason.
- **effort**: XS (up to half a day), S (half to one day), M (1 to 3 days),
  L (3 to 6 days), XL (6 to 12 days), or person-days like `2-4`. Estimate
  for the user's team and stack, not an ideal one. Anything above XL is too
  big for one row: split it.
- **original**: `yes`, `no` (an addition of your own, such as a niche need
  or a fix) or `unknown` (not verified; parity.py counts it but lists it as
  unverified).
- **source, checked**: for each row whose `original` value you checked, the
  link where you saw it and the date (YYYY-MM-DD), taken from the sources
  table in step 2. parity.py ignores both. battlecard.py needs them to tag a
  claim about the original as verified; without them the claim stays
  "assumed" and never goes into sales material or onto a comparison page.
- Add the fixes from voice of customer later as rows with `original` = `no`,
  one or two per need in `teardown/fixes.md`.

## Step 9: what cannot or should not be rebuilt

Honest `skip` rows with a reason: licensed content (a music catalogue, stock
photos), the network and its users, data the original owns, partner deals,
hardware, regulated licences (banking, health, payments as a licensed
institution), and the signature elements from step 6.

## Step 10: size and estimate

Screens or page types, flows, entities, and the hard parts (realtime, sync,
payments, calendar or email integrations, offline, search, multi-tenant,
imports from the original). If visibility ran, add the programmatic page
sets and content volume from `teardown/visibility.md` to the hard parts and
to `features.csv`. Give a size: S (a weekend), M (a few weeks),
L (a quarter), XL (rescope it). Then run:

```bash
python3 $SKILL/scripts/parity.py teardown/features.csv --estimate-only --lang de --markdown \
  --buffer 20 --out teardown/estimate.md
```

At recon time nothing is built, so the remaining effort is the whole
estimate: MVP (must), + should, + could. `--estimate-only` leaves out the
parity lines, which mean nothing yet. For client work, add `--overhead`
(QA, project management as % of the feature effort), `--fixed` (setup,
design, go-live as person-days) and `--day-rate`; see
`references/client-deliverables.md`. In the answer and the offer, copy
every range from `teardown/estimate.md` exactly as printed (76,2 - 128
stays 76,2 - 128, 49.530 € stays 49.530 €), in person-days and money; no
rounding, no "about".

## Output

`teardown/recon.md` (with the messaging and recent-moves tables),
`teardown/features.csv`, screenshots logged in `teardown/sources.csv`, and,
if the visibility add-on ran, `teardown/visibility.md` and
`teardown/sitemap.md`, and a short summary: the core loop, counts (screens
or pages, flows, entities), the three hardest parts, signature elements to
avoid, what the original's messaging leaves out, what is out of scope, the
size and effort range, and the next step (voice of
customer, the offer, or the build brief in `references/build-handoff.md`);
once voice of customer has run, a battle card (`references/battlecard.md`)
if sales will compete against the original.
