# Battle card mode

Turn the teardown into what sales and marketing use against the competitor:
a one-page battle card (where they are weak, where they are strong, what only
we have, answers to objections, dated prices) with a SWOT appendix, and,
when asked, a draft comparison page ("X alternative", "X vs us") that is
built to pass the EU/DACH rules on comparative advertising.

Reads: `teardown/feedback.json` (reviews.py --json) and
`teardown/features.csv`. Either one is enough to start; the part that needs
the other says "not researched". Output: `teardown/battlecard.md`
(template `$SKILL/templates/battlecard.md`), optionally `teardown/compare.md`
(the comparison page draft from the second part of that template), the
checklist below in `teardown/legal.md`, and dated copies of the sources in
`teardown/proof/`.

## Rules that are not negotiable

- **Every claim about the competitor carries a tag.** `verified`: checked in
  a primary source, with the link and the date. `reported`: what reviewers
  say, with the links of the quotes. `assumed`: everything else, including
  every row with `original` = `unknown`. An assumed claim is never said to a
  prospect and never goes on a page.
- **Reviews are evidence for questions, not facts about them.** "12 reviews
  across 3 sources complain about support" justifies asking a prospect how
  support works for them. It does not justify saying "their support is
  bad". Reviewer quotes stay on the internal card.
- **Claim only what is shipped.** A differentiator is a row with `clone` =
  `yes`. Partial means saying what is missing. A roadmap item is a claim only
  with a date the product owner has committed to.
- **Name their strengths.** The card lists what customers praise, so the rep
  agrees there instead of attacking.
- **Everything is dated.** A check older than 90 days before the card date
  is stale and is checked again before use.
- **Reviewer quotes are personal data.** They stay on the internal card and
  in the client's sales team, without author names or handles; names of
  people in a quote are cut with "..." (`legal-eu-dach.md`, section 6).

## Step 1: inputs

1. **The review analysis as JSON.** The same run as `feedback.md`, with
   `--json`, and the same `--as-of` as the card date:

   ```bash
   python3 $SKILL/scripts/reviews.py teardown/reviews.csv --themes teardown/themes.json \
     --as-of 2026-10-17 --json --out teardown/feedback.json
   ```

2. **Evidence in the feature matrix.** Add two columns to
   `teardown/features.csv`: `source` and `checked` (YYYY-MM-DD). parity.py
   ignores them. Fill them for every row you want to say something about:
   a differentiator ("they do not have it") and a gap ("they have it").
   - Primary sources only: their help center or docs, pricing page,
     changelog, app store listing, terms, or the user's own trial account
     within its terms. A review, a blog post, a comparison site or an AI
     answer is not a primary source for what their product does.
   - Absence is hard to prove. "They do not have X" is verified only when
     their own material shows the limit (a plan table without it, a help
     article saying it is not supported, the trial account). Not finding it
     in the docs keeps the row `assumed`.
   - `original` = `partial` (teilweise) when they do it only in part or only
     in a higher plan; say which in `notes`.
   - For each verified row, save a dated PDF or archive copy of the source
     page in `teardown/proof/`. It is the proof if the claim is challenged,
     and it is never published.

## Step 2: run

```bash
python3 $SKILL/scripts/battlecard.py --feedback teardown/feedback.json \
  --features teardown/features.csv --target "X" --ours "Y" --as-of 2026-10-17 \
  --lang de --out teardown/battlecard.md
```

It lists the top five complaint themes with two verbatim, linked quotes
each; the praise themes; our differentiators with the tag of each claim
about them; features we have that nobody checked on their side ("check
first") and own features that are not done ("do not claim yet"); objection
stubs from their must and should features we lack and from their praise; a
SWOT in which every line names its source row or theme; the rows fit for a
comparison page and why the others are not; and a footer with the sample
size, the dates of the checks and the card date. `--json` gives the same as
data. It invents nothing, so everything a person must write says "to write"
("zu schreiben" with `--lang de`).

## Step 3: write what says "to write"

Use the layout in `$SKILL/templates/battlecard.md`. The card is the part
before the line; it fits one page, so cut rather than shrink. The SWOT and
the sources are the appendix.

- **In one line**: the angle from `teardown/fixes.md` (voice of customer
  step 8), with its evidence, aimed at the gap in their messaging (the
  messaging table in `teardown/recon.md`: what their hero claim promises and
  leaves out). Their claim is quoted there, never reused here.
- **Discovery questions**: one open question per weak theme that lets the
  prospect name the pain ("How long does a support ticket take for you
  today?"), never a statement about them.
- **Where they are strong**: per praise theme, say in plain words of your
  own what customers praise, taken from its quotes ("customers praise it as
  fast, with no loading time"), not only the theme label or a quote in
  another language, and give the rep's line: agree there, then how we match
  it. The same plain words go into the SWOT threat line and the "We are
  happy with them" answer.
- **Objection answers**: see below.
- **Prices**: from their pricing page, plan by plan, with the date and the
  link, next to our comparable plan. If there is no comparable plan, say so
  instead of comparing different things. If nobody read their pricing page,
  the section says "no price source supplied" and holds no figure. A price
  a reviewer mentions is not their price: it never goes into this section,
  and a quote elsewhere on the card that names a price figure carries the
  review's date from `reviews.csv` next to its link.
- **Threats from recent moves**: add each dated move from the "Recent moves"
  table in `teardown/recon.md` (a price change, a shipped feature, a new
  market) that weakens one of our lines, with its date and link. A move
  that touches a verified row makes that row due for a recheck now,
  whatever its `checked` date says.

When the card is written, check every quote on it against the reviews; it
exits 1 on any quote that is not word for word in the review behind its
link:

```bash
python3 $SKILL/scripts/reviews.py teardown/reviews.csv --verify teardown/battlecard.md --lang de
```

## How to write objection answers

Acknowledge, state the fact, show the proof, ask back. Two or three
sentences in the rep's words.

- **True first.** If we lack it, say "not today". Mention the roadmap only
  with a committed date. If the gap is a must for this buyer, say we are not
  the right fit yet: it is cheaper than a churned customer.
- **About them, only verified facts**, and with their date in mind ("as of
  October their entry plan has no SMS reminders"). No "they are bad at", no
  reviewer quote as a fact, no guesses about their company, staff or
  finances.
- **Agree where they are strong**, then move to the buyer's need.
- **Proof is ours**: a demo step, our documentation, a customer story we
  have permission to tell. Never a review of theirs.
- **No superlatives without proof**: "the only", "the first", "the
  fastest" need evidence of a clear lead.
- **German B2B buyers** expect "Sie", facts and no combat language.

Pattern (placeholders, not data):

> "{target} has {feature}. Do you?"
> "Not today. {ours} does {what we do instead}, which covers {job} for most
> teams we work with. How do you use {feature} now?"
> Data: features.csv line {n}, ours = no, theirs verified on {date}.

## Step 4: keep it current

Recheck verified rows every 90 days, or as soon as their pricing page or
changelog changes (the "Recent moves" table in `teardown/recon.md`); update
`checked`, rerun the script, and move the card's next review date. A stale card misleads the rep before it misleads anyone
else.

## The comparison page

Only when the user asks for a public "X alternative" or "X vs us" page. It
is comparative advertising for every competitor it names; the law is in
`references/legal-eu-dach.md` section 4. Draft it in `teardown/compare.md`
from the second part of the template. Pick the format first:

| format | URL path and title | contents |
| --- | --- | --- |
| singular alternative | `/{target}-alternative`, "{target} alternative" | why people look for one (the needs in `fixes.md`, never their review quotes), what we do differently, the fair table, who should stay with {target}, switching |
| plural alternatives | `/{target}-alternatives` | 4 to 7 real alternatives, ours among them and not always first, each from verified rows with the same fields, one line on who each is best for; every product named gets the same care, because each one is compared |
| us vs them | `/{ours}-vs-{target}` | the fair table, prices like for like, who each is best for, switching |

Then build it:

1. **Only page-ready rows**: the script's "For a comparison page" table
   (verified, checked within 90 days, public link). Reviews, review themes
   and their star ratings never go on the page.
2. **A fair table.** Include material features where they are ahead. The
   script warns when the table shows only rows we win; a one-sided selection
   can mislead.
3. **Who each one is best for**, honestly: "{target} is the better choice
   if you need {a lead of theirs that is verified}", next to who we are for.
   Take their leads from the page-ready rows of the script's gaps, each with
   the same footnote as its table row; what customers praise tells you
   which leads to name, but is not itself a claim for the page. A lead
   without a page-ready row stays off the page. A page that never says when
   the other product fits is the one-sided page § 5a UWG warns about.
4. **Switching**: what moves over and how (import, export formats, what the
   user must do, how long it takes), built from the switching data in
   `feedback.md` (why people leave and what they miss) and the needs in
   `fixes.md`, and only from what we have shipped. Never "hundreds have
   switched" from reviews, and no promise of a migration nobody built.
5. **Keyword target**: one primary search per page from `seo.md` or
   `visibility.md` (the alternatives and vs theme), with its volume, tool
   and date, or "not measured". Their mark appears as often as is needed to
   say who is compared, not to rank.
6. **FAQ**: three to six real questions (from sales calls, the AI-answer
   sample's Q3 and Q4, the alternatives keywords), each answered with a
   verified fact about them or a fact about us. FAQPage markup only for
   questions and answers that are on the page; it is not a ranking promise.
7. **Footnotes**: every claim about them, wherever it stands (intro,
   who-it's-for, table, switching, FAQ), with its source link and the date
   checked; every price with plan level, billing period, net or gross (gross
   totals for consumers), date and link; an "as of" date for the page.
8. **Their name**: the word only, as needed to say who is compared (title,
   meta description, table header, URL path on our own domain). No logo, no
   colours, no screenshots, no copied text. A line that names and marks
   belong to their owners and that we are not affiliated; call it a
   registered trademark only after a register check with its date. Never
   their mark in our domain, product name, app name or the display URL of
   an ad.
9. **Never present the product as a copy**: no "clone", "replica", "like X
   but cheaper".
10. **Neutral tone.** Facts in a table beat adjectives.
11. **Proof file** in `teardown/proof/` for every row, listed in
    `teardown/sources.csv`.
12. **Lawyer review**, then publish; recheck before every edit and take the
    page down or update it when their product or prices change. The answer
    that hands over the draft says so too: a draft and a checklist for a
    lawyer, not legal advice.

Every element (headline, who-it's-for, switching, keyword target, FAQ)
goes through the checklist below, not only the table.

## Auditing pages already published

When the user already has comparison or alternative pages, or a sales deck
that compares: list every claim about the competitor on them (feature,
limit, plan, price, integration), one row each with the page and the date
it shows. Each claim needs a row in `features.csv` with `source` and
`checked`; rerun `battlecard.py` and mark every claim:

- **current**: on the script's comparison-page list (verified, checked
  within 90 days, public link) and the page says the same;
- **stale**: verified, but checked more than 90 days ago, or touched by a
  recent move in `recon.md`, or the page says something else than the
  source now: recheck, then fix the page;
- **unverifiable**: no primary source (`assumed`): verify it or take it off.

Write the audit into `teardown/compare.md` under "Audit", with the page,
the claim, the status and the features.csv line. Stale and unverifiable
claims come off the live page until they are fixed; the lawyer gets the
list with the checklist below.

## Legal checklist for a comparison page

Flags for the user's lawyer, not legal advice. Copy it into
`teardown/legal.md`. Every box stays "to check" until the lawyer has
checked it; never mark a box yourself. Details and sources:
`references/legal-eu-dach.md` section 4.

- [ ] to check: **It is comparative advertising.** The page makes the
  competitor identifiable, so the rules apply: Germany § 6 UWG, Austria
  § 2a UWG, Switzerland Art. 3 (1) lit. e UWG, EU Directive 2006/114/EC
  Art. 4. The target markets are named.
- [ ] to check: **Same need.** Both products meet the same need or serve
  the same purpose (§ 6 (2) no. 1 UWG; Art. 4 (b)).
- [ ] to check: **Objective, material, relevant, verifiable, typical.**
  Each compared feature matters for the purchase and is typical of the
  products, not an edge case picked to win (§ 6 (2) no. 2 UWG; Art. 4 (c)).
- [ ] to check: **Verifiable.** Each claim says where the reader can check
  it, with the date (CJEU, Lidl Belgium, C-356/04), and the proof file holds
  a dated copy of the source.
- [ ] to check: **Representative selection.** Material features where the
  competitor is ahead are in the table; nothing the reader needs for the
  decision is left out (§ 5a UWG).
- [ ] to check: **True and current.** Every statement about both products is
  true on the day it is seen; no superlative or "only" or "first" without
  proof (§ 5 UWG; Art. 4 (a)).
- [ ] to check: **Prices.** Same plan level, scope and billing period, net
  or gross on both sides, mandatory extras included, consumer prices as
  totals incl. VAT (PAngV), date and source on the page, and a process to
  update or remove the comparison when their prices change.
- [ ] to check: **No confusion.** Name, logo, colours, layout and domain of
  the page keep the two companies and products clearly apart (§ 6 (2) no. 3
  UWG; § 5 UWG; Art. 4 (h)).
- [ ] to check: **Their mark.** The word mark only, as far as needed to
  identify them; no logo or trade dress; an ownership and no-affiliation
  line; not in our domain, product name or ad display URL (§ 6 (2) no. 4
  UWG; Art. 4 (f); CJEU, O2 v Hutchison, C-533/06).
- [ ] to check: **No denigration.** No disparaging words, no reviewer quotes
  or review themes about them, no statements about their company, staff or
  finances that cannot be proven (§ 6 (2) no. 5 UWG; § 4 nos. 1 and 2 UWG;
  Art. 4 (d)).
- [ ] to check: **Not presented as an imitation.** No "clone", "copy",
  "replica", "like X but cheaper" (§ 6 (2) no. 6 UWG; Art. 4 (g); CJEU,
  L'Oréal v Bellure, C-487/07).
- [ ] to check: **Nothing of theirs copied.** No screenshots, texts, icons or
  images from the competitor (copyright; see section 2 of
  `legal-eu-dach.md`).
- [ ] to check: **Own reviews.** If the page shows reviews or ratings of our
  own product, it says whether and how they are checked (§ 5b (3) UWG).
- [ ] to check: **Austria and Switzerland.** If those markets are targeted,
  a lawyer from there has checked the page against the local rules.
- [ ] to check: **Sales material.** The battle card stays internal, and what
  reps say or send to prospects follows the same rules as the page.
- [ ] to check: **Dates.** The page has an "as of" date, an owner and a next
  review date.
- [ ] to check: **Every part of the page.** Headline, who-it's-for lines,
  switching section, FAQ and meta description meet the same rules as the
  table; on a page with several alternatives, for each product named.

## Output

`teardown/battlecard.md` with every "to write" replaced, optionally
`teardown/compare.md` marked as a draft, the checklist in `teardown/legal.md`,
and a summary that states the sample size, how many claims are verified,
stale and assumed, and what must be checked before the card or page is used.
