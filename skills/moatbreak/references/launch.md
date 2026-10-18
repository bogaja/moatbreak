# Launch

Turn the angle into the pages and store texts that sell the new product,
and check them before they go live. Writing the code stays with the build
skills of the session; this mode writes the words and the checks.

Read first: `teardown/fixes.md` (needs and angle), the messaging table in
`teardown/recon.md`, `teardown/brand.md` (name, voice, tokens),
`teardown/parity.md` (what is shipped), and for anything that names the
original `references/battlecard.md` and `references/legal-eu-dach.md`
section 4. Output: `teardown/launch.md` (landing and pricing page copy, the
token map), `teardown/listing.json` and `teardown/listing.md` for an app.

## Rules for every launch text

- **Clean room.** Write fresh from the angle. Common page patterns (hero,
  how it works, pricing table, FAQ) are free; their headline, slogan, page
  copy, testimonials, screenshots and icons are not. The messaging table
  quotes their claim for the analysis; it never becomes ours.
- **Claim only what is shipped.** A feature on the page is `clone` = `yes`
  in `features.csv` (parity mode). Partial means saying what is missing; a
  roadmap item needs a date the product owner committed to.
- **Prefer claims about ourselves.** The moment a page names or clearly
  points to the original ("the X alternative", "faster than X", "unlike the
  big tools"), it is comparative advertising: only verified, dated claims,
  the § 6 UWG checklist in `references/battlecard.md`, and a lawyer before
  it goes live. "The only", "the first", "the fastest" need proof of a
  clear lead.
- **Proof is ours.** Our demo, numbers we measured with their date, quotes
  from our own customers with their permission. Never their reviews, never
  reviews we bought, filtered or invented; ratings we show say how they are
  checked (§ 5b (3) UWG).
- **Prices the market expects.** For consumers, total prices including VAT
  (PAngV), and the lowest price of the last 30 days next to any reduction
  (§ 11 PAngV); for businesses, net with "zzgl. MwSt.". Subscriptions sold
  online to consumers need the cancellation button (§ 312k BGB).
- **One voice.** Du or Sie as decided in brand mode, everywhere, and the
  10 most-seen strings from brand step 5.

## Step 1: the landing page

One page per main audience segment, in this order. Write each part in the
user's language into `teardown/launch.md`, with its source next to it.

| part | from | rule |
| --- | --- | --- |
| headline and the line under it | the recommended angle (voice of customer step 8) | the need in the customer's words, not a feature list; their claim is the thing to avoid |
| call to action | the core loop (recon F01) | one action, the same on every screen size |
| proof | our demo, our measured numbers with date, our customers' quotes with permission | none yet: leave the part out rather than fill it |
| how it works | the core loop, three steps | screens of our product only (`teardown/new-screens/`) |
| the fixes | the fix plan in `fixes.md`, shipped rows only | each fix with the need it solves, in plain words |
| who it is for | the segments in `fixes.md` ("who says it") | say who it is not for, too |
| pricing teaser | step 2 | a "from" price with the period and VAT note |
| questions | the objections on the battle card, the AI-answer sample | answers about us; a question that names them follows the comparison rules |
| footer | `legal-eu-dach.md` section 5 | Impressum, privacy notice, accessibility information, terms |

## Step 2: the pricing page

The user decides prices; this step writes the page for them. Start from the
pricing and billing needs in `fixes.md` (for example: monthly cancellation,
no extras per message) and from the estimate's running costs. Per plan:
price per period with VAT note, what is included, limits, what an extra
costs, the trial terms, how to cancel. A comparison with their prices on
this page is a price comparison: like for like, dated, linked, or not at
all (`references/battlecard.md`).

## Step 3: the store listing (apps)

Copy `$SKILL/templates/listing.json` to `teardown/listing.json`, write each
field fresh in the store's language (one block per store language under
`locales`), and check it:

```bash
python3 $SKILL/scripts/listing.py teardown/listing.json --config teardown/brand.json \
  --lang de --markdown --out teardown/listing.md
```

It fails on a field over the store's limit (App Store name and subtitle 30,
keywords 100, promotional text 170, description 4000; Google Play title 30,
short description 80, full description 4000), an empty field, and any of
the original's names from `brand.json`, in German spelling variants or a
near spelling. The stores' own rules forbid other apps' names in the
metadata (App Store Review Guideline 2.3.7, Google Play's metadata policy),
and in the EU it is a confusion and trademark risk. Fix until it exits 0.
Store screenshots show only the new product; check them by eye (brand mode
step 6). The limits are the stores' published ones as of late 2026: check
them again before a release.

## Step 4: design tokens

Take the token map from brand mode step 3 into `teardown/launch.md` for the
build: every role with its colour, its contrast pair and the
`contrast.py` result. A colour that is not in the map does not go into the
product.

## Step 5: before it goes live

The pre-launch gate in `references/build-handoff.md` step 7, plus:
`listing.py` exits 0 for an app, every claim on the landing and pricing
pages traces to a shipped `features.csv` row, every page that names the
original has passed the battle card checklist with a lawyer, and
`sources.py` exits 0 if a page relies on a proof copy.

## Output

`teardown/launch.md` with the landing and pricing copy and the token map,
`teardown/listing.json` and `teardown/listing.md` for an app, and a short
summary: the headline and the need behind it, what is claimed and from which
rows, what was left out because it is not shipped, and what still needs a
lawyer.
