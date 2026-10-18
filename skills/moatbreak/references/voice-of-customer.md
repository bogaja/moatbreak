# Voice-of-customer mode

A straight copy has no reason to exist. This mode finds the reason: what the
original's customers hate, why they leave, in their own words, and turns it
into the needs behind the complaints, fixes and a position you can sell.

Output: `teardown/reviews.csv`, `teardown/feedback.md`, `teardown/fixes.md`,
new rows in `teardown/features.csv`.

## Rules that are not negotiable

- **Never fabricate.** No invented reviews, quotes, ratings, counts or
  sources. If a source cannot be reached, say so and move on. If there are
  14 reviews, say 14.
- **Every quote is verbatim and linked.** Copied exactly, with the URL of the
  review or thread. `reviews.py` drops any row without a link and never
  paraphrases or translates. If you translate a quote for a report, keep the
  original in quote marks and put the translation after it in square
  brackets without quote marks: `"Viel zu teuer." (trustpilot, 1*) https://...
  [EN: Far too expensive.]`.
- **Quotes are checked by code, not by trust.** Before `fixes.md`, an offer
  or a battle card goes anywhere, run `reviews.py --verify` on it (step 9).
  A quote that does not stand word for word in the review behind its link
  fails, and so does a link that is not in `reviews.csv`.
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
- **Reviewers are people.** The sample is personal data under the DSGVO.
  Store no author names or handles, cut the names of staff, customers or
  reviewers out of a quote with "..." (`--verify` accepts it), keep
  `teardown/` out of public repositories, and delete the sample when the
  project ends. The lawyer's item for this is in `legal-eu-dach.md`,
  section 6.

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

Searches that find the honest ones, and the people who left: "X
alternative", "switched from X", "X vs", "cancel X", "X Erfahrungen", "X
Alternative", "X kündigen", "X Probleme", "von X gewechselt".

Each row in `teardown/reviews.csv` (from `$SKILL/templates/reviews.csv`):
`source,url,date,rating,segment,text`, text copied exactly. German headers
and semicolon-separated Excel exports work too (saved as "CSV UTF-8"; the
script says so when a file is not UTF-8). Ratings like `4,5`, `4/5`,
`8/10` or `★★★★☆` are normalised to 1-5 stars. Three columns matter more
than they look:

- **source**: one name per platform in every row (`app-store`, not
  `App Store` here and `apple` there; spaces and case are evened out, other
  spellings are not). The bias check counts per source.
- **date**: keep it whenever the page shows one. Without dates nobody can
  tell whether the sample is one bad month.
- **segment** (optional): who wrote it, exactly as the platform shows it.
  G2, Capterra and OMR show the reviewer's role, industry or company size
  ("Inhaber, 2-10 Mitarbeiter"); copy that text, one spelling per segment.
  Never guess it from the review text, and leave it empty where the
  platform shows nothing. In B2B the segment often decides the angle: the
  owner of a two-chair salon and the manager of a chain hate different
  things.

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

The same file holds `switch_patterns`: the words that say someone left or
wants to (I switched to, we cancelled, going back to, looking for an
alternative; bin gewechselt, gekündigt, Abo beendet, nutze jetzt, suche eine
Alternative, steige um). The shipped ones are written in the first person,
because "the salon cancelled my appointment" or "let me switch to dark mode"
is not someone leaving. Add the category's own the same way: for a shop
"I'm never ordering again", "ich bestelle jetzt bei {alt}"; for an app "I
deleted my account". `{alt}` marks where a named alternative stands. The
words there count as a name only when they start with a capital letter or a
digit, never a number alone or a common word that German or a UI
capitalises (Konkurrenten, Anbieter, Dark Mode), and a pattern with `{alt}`
counts only when it finds one, so the script never invents where someone
went. A themes file copied before `switch_patterns` existed gets the shipped
ones.

## Step 3: rank

```bash
python3 $SKILL/scripts/reviews.py teardown/reviews.csv --lang de --target "X" \
  --themes teardown/themes.json --as-of 2026-10-17 --out teardown/feedback.md
```

`--as-of` is the day the ages are counted from (default today). Pass it, so
the same sheet gives the same report next week; a run without it says so in
the report (and `"as_of_today": true` in the JSON). `--today` still works as the
old name. `--json` gives the same result as data for other tools, such as a
battle card (`themes`, `source_bias`, `switching`, `by_segment` and
`as_of`); with `--out` it is written as UTF-8 (use that rather than `>`,
which a Windows console writes in its own code page).

`feedback.md` has these parts, in this order:

1. **Sample by source**: reviews, share, average stars and date range per
   source, a row for all sources together, and where the sample leans (step 4).
   With a segment column, also the **sample by segment**, thin below 3
   reviews.
2. **What they hate** and **what they ask for**: themes ranked by weight.
   Low ratings and recent reviews weigh more, reviews older than `--months`
   (default 18) count half. Themes with fewer than 3 reviews or one source
   are marked thin. With a segment column, every theme ends with "Who says
   it": the segments of its reviews with counts.
3. **Why they leave**: the switching triggers (step 5).
4. **What they praise**: 4.5-5 star reviews never count as complaints, 4
   star reviews only when the sentence has a "but" (aber, leider, ...). This
   shows where not to attack. A theme shows here under its `praise_label`
   ("Fast, no waiting", not "Slow, laggy, heavy"), so give a complaint theme
   you add to `teardown/themes.json` one too.
5. **Asked for in their own words**: every request sentence.
6. **Read these by hand**: ratings of 3 stars or less that matched no theme.
   It is often where the real insight is.

One review can match several themes, so shares add up to more than 100%,
and theme counts never add up to a number of reviews. Every count you write
(in `fixes.md`, the answer, an offer) is one the report prints. To report
two themes as one, merge them in `teardown/themes.json` and run again, so
each review counts once.

## Step 4: read the sample before the ranking

The ranking is only as good as the sample. The script checks four leans and
says each one in plain words:

| warning | what it means | what to do |
| --- | --- | --- |
| one source has more than 60% of the reviews | the ranking is that platform's audience, not the market | say "what {source} reviewers say" in the report, collect from two more sources |
| a source's average is 1 star or more from the overall average | a different crowd writes there (or a different moment: right after delivery, right after a crash) | check that the top themes of that source also appear in others; if not, mark them as that audience's issue |
| more than 70% of the dated reviews are from the last 90 days | one update, outage or price change may be talking | look for it in the changelog or status page; call it an event, not a trend, until older reviews say the same |
| more than 70% of the dated reviews are older than `--months` | the product may have changed since | check the changelog; mark old themes "may be fixed" until a recent review confirms them |

Every source also leans by its nature. Suspect these, then confirm or drop
the suspicion with the numbers in the table:

| source | often leans toward | check |
| --- | --- | --- |
| App Store, Google Play | anger right after an update, crashes, short one-line verdicts | dates against the release notes |
| G2, Capterra, OMR, GetApp | B2B buyers; vendors can invite their happiest customers, so stars may run high | complaints inside 4 star reviews; labels such as invited or incentivized where the platform shows them |
| Trustpilot, Trusted Shops, ProvenExpert | invited buyers right after purchase next to unsolicited angry ones (billing, delivery) | the gap between invited and other reviews where the page marks them |
| Reddit, Hacker News, forums | power users, sharp, often unrated, many "alternative" threads | rich in switching triggers; weak for how often something happens |
| the product's own community or feature board | loyal users, requests rather than hate | good for requests and vote counts, not for what people hate |
| Google reviews of a place | one location, one team, one day | names of staff or branches before calling it a pattern |

Write one line per source into `fixes.md`: how many reviews, what it leans
toward, and whether the table confirms it. If no lean was found, the report
says so; repeat that sentence, do not add one.

## Step 5: why they leave

The "Why they leave" section lists every review that says the writer left,
cancelled, or is looking for something else: the sentence as written, the
link, and the alternative when the review names one. Above the list:

- **The same reviews complain about**: the themes of the leaving reviews.
  These are the push: what drives people out.
- **Where they say they went**: the named alternatives with counts. This is
  the pull: who wins the customers the original loses. Look at what those
  alternatives do differently; that is a ready-made fix list.
- **Switched to the original**: switching reviews with 4.5 stars or more (4
  stars without a "but"), and reviews that name the original itself (the
  `--target` name) as where they went. That is why people come, and the new
  product has to match it.

An alternative is only what the review names. Never add "probably
Calendly" to a review that says "switched to another tool". The script
names an alternative only where a pattern finds it, so read every leaving
review in the list: a name it missed ("from Evernote, Trello and Notion to
Joplin") is added by hand with that review's link, and a count of reviews
that name where they went is taken from those texts, not only from the
script's list. Fewer than 3
leaving reviews are anecdotes: list them, do not build a claim on them. If
none are found, write "no switching evidence in this sample" and run the
searches from step 1 that find people who left.

## Step 6: from themes to needs

Keyword themes say where it hurts. The fix needs to know what the customer
was trying to get done when it hurt. The script does not invent needs: you
write them, from its evidence, and every claim stays linked to a quote.

1. Start from the ranked complaint and request themes, the push and pull of
   step 5, and the "Read these by hand" list.
2. For each theme ask: what was this person trying to get done when it went
   wrong? Write that as a need in the customer's terms, 4 to 8 words, with
   no solution in it. "Know the full price before I commit", not "a
   transparent pricing page"; "Get paid without chasing clients", not
   "automatic reminders".
3. Group themes that serve the same need. Price, surprise charges and
   cancelling pain can be one need ("Pay only for what I use, leave
   without a fight"); bugs and lost data can be another ("Trust my bookings
   are still there tomorrow").
4. Keep 3 to 6 needs. Each needs at least 2 linked quotes from at least 2
   different sources, copied unchanged from `feedback.md` or `reviews.csv`.
   A group that does not reach that bar is not a need: list it under
   "Open questions" with what would confirm it (more reviews from another
   source, or one interview question). If fewer than 3 needs reach the bar,
   write fewer. Never pad.
5. Label the spread from the numbers in `feedback.md`: **across sources**
   (not thin), **one place** (all from one source), **isolated** (fewer than
   3 reviews). A vivid single complaint is never a need.
6. Say who has the need, from the "Who says it" lines: the segments of its
   reviews with counts, a thin segment marked thin, or "not shown" when the
   platforms show none. A need that comes from one segment is that segment's
   need; say so instead of generalising it.
7. Keep fact and inference apart. Quotes, counts and sources are facts. The
   need is your inference: say in one line why these themes belong together.

Write each need in `fixes.md` like this:

```
### Need: {4 to 8 words, the customer's job, no solution}
Spread: {across sources | one place | isolated}. Themes: {ids}. Reviews: {n} from {n} sources. Leaving: {n}.
Who says it: {segments with counts, from feedback.md | not shown}
- "{quote}" ({source}, {stars}) {url}
- "{quote}" ({source}, {stars}) {url}
Why one need: {one line}
What the original does instead: {one line from recon or the quotes, or "not researched"}
```

Requests named by feature ("no DATEV export", "I wish it had SMS
reminders") stay concrete: they go into the fix plan as rows, under the need
they serve.

## Step 7: the fix plan

Fix needs, not keywords. For each need pick the one or two changes that
solve it, then rank all of them by evidence (reviews, sources, leaving
reviews) times how cheaply they can be built, and keep the top 5 to 8. For
each: what to build or change, effort (XS-XL), the need it serves, and the
evidence. Add each to `teardown/features.csv` with `original` = `no` and
`clone` = `no`, so parity.py counts it as work and the offer includes it. If
recon has not run yet, create the file from `$SKILL/templates/features.csv`
(header only). Pricing and billing complaints feed the pricing of the new
product. Do not compete where "What they praise" shows the original is
loved: match it.

## Step 8: the angle

Three positioning options, each grounded in a need and, where there is any,
in the switching evidence. Read the messaging table in `teardown/recon.md`
first: what the original's hero claim promises, to whom, and what it leaves
out. The strongest angle is a need the reviews prove and the original's
claim does not cover. Quote their claim in the analysis; never reuse its
wording, structure or slogan for the new product.

```
For {who} who {the need, in the customer's own words},
{new product} {does this instead}.
Evidence: {need}, {n} reviews across {n} sources, {n} of them say they left over it.
Gap in their messaging: {what the original's hero claim leaves out, from recon.md | not researched}
```

Recommend one. It drives the name and voice in brand mode and the headline
of the landing page. Never put the original's name in the new product's
name, ads or store listing; a factual comparison page is a legal question
(see `legal-eu-dach.md` section 4 and `references/battlecard.md`). End
`fixes.md` with three assumptions an interview with real customers should
test first.

## Step 9: check every quote

```bash
python3 $SKILL/scripts/reviews.py teardown/reviews.csv --verify teardown/fixes.md --lang de
```

It reads every line that has quote marks and a link, and checks that the
quoted text stands word for word in a review with that link, whole words
only, so "helpful" cut out of "unhelpful" fails (`...` may stand for
left-out words, in order). It lists each line that fails and exits
with 1. Fix or remove every listed quote, then run it again until it passes.
Run it on every document that quotes reviews: the offer, the report, a
battle card. On a line with a link, use quote marks only for the reviewer's
words; write names of themes or needs without them.

## Output

`teardown/reviews.csv`, `teardown/feedback.md`, `teardown/fixes.md`
(sample note with one line per source, needs, why they leave, fix plan,
angle, open questions and assumptions), new rows in `features.csv`, and a
summary that states the sample size, the sources, the as-of date, the
`reviews.py` commands as run (with `--as-of`) and the `--verify` result.
For a battle card, also save the same run as JSON
(`--json --out teardown/feedback.json`); `battlecard.py` reads it.

## No reviews in reach

No web access and no file from the user: no review can be read, so none is
quoted, counted or ranked. In the answer:

- Say plainly that no reviews could be read in this session, and give the
  status: voice of customer **to run**. Write no `feedback.md` or
  `fixes.md`.
- Ask for an export, screenshots or links, name the sources for the
  product type (the table in step 1, the German ones for a German market),
  and give the columns `source,url,date,rating,segment,text` or the
  template `$SKILL/templates/reviews.csv`.
- A complaint you name from general knowledge goes under "Hypotheses to
  check (general knowledge, not findings)", each worded as a hypothesis
  ("Hypothesis: billing is a top complaint"), with no number, rating or
  quote.
- Quotes for a deck or an offer come only from the collected sample,
  verbatim with their link, and pass `reviews.py --verify` first.
