# Visibility (recon add-on)

How the original is found: which pages it publishes, which markets it
serves, which searches it wins, and what AI assistants tell a buyer who asks.
Run it inside recon (after step 1, next to step 2 sources), or on its own
when the question is "how do we get found against X".

Output: `teardown/visibility.md` (template `$SKILL/templates/visibility.md`),
`teardown/sitemap.md` (from `sitemap.py`), `teardown/seo.md` (from `seo.py`,
when there is a tool export), and the public files you read, saved in
`teardown/visibility/`.

## Rules for this add-on

- **Every number has a source and a date.** "1,240 pages, sitemap.xml read
  2026-10-17". A number without both is not written down.
- **Three kinds of data, always labelled.** *Read*: counted by you or by
  `sitemap.py` from public files. *Tool*: from an SEO data tool connected to
  the session, with the tool's name, the database (search engine, country,
  language) and the date; third-party traffic, volume and backlink figures
  are the tool's estimates, so write "estimated by {tool}". *User-provided*:
  an export the user hands over, with its tool and date. There is no fourth
  kind. Never estimate traffic, rankings, backlinks or search volume
  yourself, and never fill them from memory. Without a tool or an export the
  cell says **not measured**.
- **AI answers are a sample, not a measurement, and never customer
  evidence.** They show what one assistant told one buyer on one day. Never
  count them as reviews, quote them as what customers say, or use them to
  prove a pain point.
- **Reading, not scraping.** robots.txt, the sitemap files and 5 to 15 key
  pages, read one at a time like a person. Never request every URL in the
  sitemap: the counts come from the sitemap itself. Do not fetch paths that
  robots.txt disallows. No scripted queries against search engines or AI
  assistants; their terms forbid automated use, and the samples below are a
  handful, by hand.
- **Their words stay theirs.** Titles, meta descriptions, navigation labels
  and structured data are the original's text: quote them in the analysis,
  write the new product's own. The original's name and marks never go into
  the new product's name, domain or ad text, or the titles and meta tags of
  its own product pages. The one exception is a comparison page drafted
  under `references/battlecard.md` and reviewed by a lawyer: it may name
  them in its title, meta description and URL path, only as far as needed
  to identify them (see `legal-eu-dach.md`, section 4).

## Step 1: public files

Open each file, save it into `teardown/visibility/` and note the URL and the
date read in the template's first table.

| file | where | what to note |
| --- | --- | --- |
| robots.txt | `/robots.txt` | the `Sitemap:` lines; disallowed areas (they often reveal the app, account, checkout and internal search); rules for AI crawlers such as GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, CCBot. Copy those lines verbatim; crawler names change, so do not read more into them than they say |
| sitemap | the `Sitemap:` line, else `/sitemap.xml` or `/sitemap_index.xml` | an index lists child sitemaps; save the index and the children you need under their own file names |
| llms.txt | `/llms.txt` | present or not found. It is a proposal that assistants may or may not read: presence shows effort, not visibility |

Large shops publish dozens of child sitemaps. Save the index plus the
children for the types you need (products, categories, pages, blog);
`sitemap.py` marks the rest as not given and says the counts are partial.
The child names already hint at the types (`product-sitemap.xml`,
`sitemap_collections_1.xml`).

## Step 2: page inventory from the sitemap

```bash
python3 $SKILL/scripts/sitemap.py teardown/visibility/*.xml --lang de \
  --as-of 2026-10-17 --out teardown/sitemap.md
```

It counts pages by type (home, comparison, legal, help, blog, product,
category, pricing, integrations, templates, customers, features, locations,
company, other), by first folder, by language or country folder and by
hreflang, with examples. `--as-of` adds how many pages of each type changed
in the 90 days up to that date; if most lastmod dates are the same day, the
report says so and they mean nothing. `.xml.gz` and plain URL lists work
too; `--json` gives the raw counts.

How to use it:

- **Website or shop:** each page type with pages is a template for recon
  step 3. One product page template, not 4,000 product pages. The counts are
  the content volume: a 4,000-product catalogue or 300 help articles is an
  import or a writing job, and goes into `features.csv` as its own row.
- **SaaS:** the sitemap covers the marketing site, docs and blog, not the
  app. Screens still come from recon step 3.
- **Programmatic page sets** (hundreds of integration, template, location or
  comparison pages from one template) are often the original's real search
  moat. Note type, count, one example and the data that fills them.
- **Comparison pages** name the rivals the original fights. Add the names to
  the list of references for the user to confirm.
- Types are read from the address only. Check the examples before you trust
  a type, and treat "other" as pages to look at, not as noise.

## Step 3: key pages, read by hand

Pick 5 to 15: home, pricing, one example of each large type in
`sitemap.md`, the main category and product page for a shop, a top help
article, and any comparison page. Read the page and its source (reading the
head of a page is reading; saving its code bundles is not). For each,
record:

- title tag and meta description, verbatim
- H1
- canonical, and robots meta if it says noindex
- hreflang alternates
- structured data types from the JSON-LD `@type` (Organization, Product,
  Offer, AggregateRating, Review, FAQPage, BreadcrumbList,
  SoftwareApplication, LocalBusiness, Article). Types only, not the content
- Open Graph title, the text people see when the page is shared

Then the main navigation and footer labels, verbatim and in order. They show
how the original segments its buyers ("for teams", "Enterprise", "Branchen")
and which words it bets on.

## Step 4: markets

Language and country folders, subdomains (`de.example.com`), country domains
(`.de`, `.at`, `.ch`), hreflang including `x-default`, and for shops the
currencies and shipping countries (recon's commercial promise). Compare the
page counts per language: 400 English pages next to 40 German ones means a
partial translation, which can be an opening for a DACH product. Read one
German page by hand and note what you see: du or Sie, local proof (DACH
customers, German reviews), an Impressum. Write what a quote can back, not a
verdict on translation quality.

## Step 5: search data, only with a connected tool

Check the session's tools first. Usable: an SEO data tool or MCP server such
as DataForSEO, OpenSEO, Ahrefs, Semrush or Similarweb, or an export the user
downloaded from their own account. Google Search Console only shows sites
the user has verified: use it for the user's own site (a baseline before
launch, the rebuild after), never for the original.

Pull for the original's domain, in the market's database (for example
Google, Germany, German):

| metric | why |
| --- | --- |
| organic keywords (count), and the top 20 by estimated traffic with position, volume and URL | which demand it captures, and with which page types |
| branded versus non-branded share of that traffic | what it owes its name, which no rebuild can take |
| estimated organic traffic per month | size, as the tool's estimate |
| top pages by estimated traffic | which templates earn the visits |
| referring domains (count) and the top 10 | the authority a newcomer has to match; partner and press links show its network |
| keyword gap against the user's site, if one exists | what to win first |
| Core Web Vitals (LCP, INP, CLS) of the home page and one key template, mobile | how fast the original feels; a public PageSpeed Insights run is a tool reading too: write the URL, device, field or lab data, and the date |

With a keyword export (a CSV from the tool, or the user's own download),
save it in `teardown/visibility/` and let the script do the grouping:

```bash
python3 $SKILL/scripts/seo.py teardown/visibility/semrush-original.csv --tool semrush \
  --database "Google DE, de" --brand "X" --local "berlin,münchen" \
  --ours teardown/visibility/gsc-ours.csv --as-of 2026-10-17 --lang de --out teardown/seo.md
```

`--as-of` is the day the export was pulled and is required: every number in
`seo.md` carries the tool, the database and that date. It sorts keywords
into themes (alternatives and vs, branded, local, how-to, category),
computes the branded share (what the original owes its name), the top
keywords and pages, and with `--ours` the gap: keywords where the original
ranks in the top 20 and the user's site does not. It estimates nothing and
fetches nothing; without an export there is no `seo.md`, and the rows say
"not measured". Search Console data is measured, not estimated, and only
ever for the user's own site.

Write each value as the tool gives it, with tool, database and date:
"estimated organic visits per month: {n} (Semrush, Google DE, retrieved
2026-10-17)". Do not round an estimate into a fact. Paid tools bill per
request: keep to this list and ask the user before larger pulls. If a call
fails or returns nothing, write "not measured" and why.

No tool and no export: every row is "not measured", and the next step says
what would measure it (connect a tool, or an export from the user's
account). The rest of this add-on still runs.

## Step 6: AI-visibility sample

Five fixed questions, so the sample can be repeated later and for the new
product after launch. Write them in the market's language and fill in
category, audience and market from recon step 1; adjust articles and grammar
to the category. Q1, Q2 and Q5 do not name the original: they test whether
assistants bring it up on their own.

| # | English | German |
| --- | --- | --- |
| Q1 | Which {category} do you recommend for {audience}? | Welche {Kategorie} empfiehlst du für {Zielgruppe}? |
| Q2 | How can I {job} as {audience}, and which tool should I use? | Wie kann ich als {Zielgruppe} {Aufgabe}, und welches Tool nehme ich dafür? |
| Q3 | What are the best alternatives to {original}? | Was sind die besten Alternativen zu {Original}? |
| Q4 | Is {original} worth it for {audience}? What are its downsides? | Lohnt sich {Original} für {Zielgruppe}? Was sind die Nachteile? |
| Q5 | Which {category} meets {market requirement}, for example GDPR-compliant with servers in the EU? | Welche {Kategorie} erfüllt {Marktanforderung}, zum Beispiel DSGVO-konform mit Servern in der EU? |

**Who to ask:** the assistants this session can reach, in the browser with
the user's own account or a public version without login (ChatGPT, Gemini,
Copilot, Perplexity, and the AI answer on a search results page), or an AI
tool connected to the session. A fresh session or sub-agent without the
project's context is a fair sample of its model. Your own answer in this
conversation is not: the conversation has primed it. One run per question
and assistant, each in a new chat; switch off memory and custom instructions
where the user can, and note it where not.

**Record per answer:** assistant, and model or mode as shown; date;
language; web search on or off (or whether sources are cited); the exact
prompt; the answer verbatim (save it in full, quote passages from it); the
brands named, in order; whether the original is named and at which
position; the source URLs it cites.

**Summarise honestly:** "named in {x} of {y} answers (5 questions, {n}
assistants, {date})". No percentages, no "share of voice", no trend from one
run. Downsides an assistant lists in Q4 are hypotheses to check in voice of
customer, not findings.

If no assistant can be reached: write "AI answers: not sampled" and give the
user the five questions to run and paste back verbatim, with the assistant's
name and the date.

## Step 7: search sample by hand (optional)

The same five questions, or the three main keywords, in a normal search
engine: private window, the market's domain and language (google.de,
German). Per search: date, location if shown, the top 10 organic domains
(not ads), the original's position or "not on page 1", and whether ads
appear when you search for the original's name (someone bids on it). One
search is one sample: location and personalisation change results.

## Step 8: local search (local businesses, and software that serves them)

For a local business (a salon, a practice, a shop with branches), or
software whose customers are local businesses, the map pack decides more
than the organic results. By hand, dated:

- **Google Business Profile**: for the original, or for three of its
  customers when the original is software: primary and secondary
  categories as shown, review count and rating as shown on that day, and
  whether a booking or order button is there and whose service it uses
  (the button names it). Ratings stay a note in the analysis, never on a
  page of the new product (`references/battlecard.md`).
- **Local pack sample**: "{category} {city}" for two or three cities of the
  market, in the market's Google domain, private window, location as shown.
  Per search: the date, the three businesses in the pack, and which booking
  or shop software their profiles link to, if any. One search is one
  sample.
- **Local pages**: location or city pages in `sitemap.md` (type
  `locations`), with one example each.

Write it into the template's local search table. No tool and no browser:
"not sampled", and the searches to run go to the user.

## Step 9: what it feeds

- **Feature matrix (`features.csv`):** rows for what the rebuild needs to
  be found: pages per language with hreflang if the market needs them,
  structured data for the main page types (Product, Offer and
  AggregateRating for shops; SoftwareApplication for apps; ratings shown or
  marked up for the new product follow `legal-eu-dach.md` section 4 "Reviews
  you show" (§ 5b (3) UWG): say how reviews are checked, and never buy, fake
  or filter them), a booking or order link on local profiles if the local
  pack sample shows it matters, Core Web Vitals at least as good as the
  original's row, sitemap and
  robots.txt, a blog or help center if the original wins with them,
  redirects if a domain moves, and content rows for the volume (product
  import, help articles, programmatic pages, all written fresh). Use
  `original` = `yes` with the count in `notes` ("visibility.md: 312
  integration pages"); a market the original serves poorly gets a row with
  `original` = `no`. Programmatic sets and content volume also go into the
  size in recon step 10.
- **Positioning (`fixes.md`, the angle):** navigation labels, titles and the
  keywords it wins show how the original positions itself; comparison pages
  and keyword gaps show where it fights; AI answers show how assistants
  describe it. The angle still needs a pain from voice of customer.
  Visibility says where to put it: which searches, which market, which
  questions the assistants answer without naming the original.
- **Brand and name check (`brand.md`):** search every name candidate as a
  keyword too. A candidate that is a common search term is hard to rank for
  and a weak trademark; one that already ranks for another product in the
  category is a confusion risk. Keep the brands named in AI answers and
  searches next to the candidates, so no name sounds like one of them.
  Search ads on the original's name follow `legal-eu-dach.md`, section 4.
- **Competitors:** brands that answers and searches name but recon does not
  have go to the user as candidates. The user confirms before any of them is
  mapped.
- **Reports and offers:** a visibility section with read, tool or
  user-provided values only. Whatever was not run says "not measured" or
  "not researched", never a guess.

## Output

`teardown/visibility.md`, `teardown/sitemap.md`, `teardown/seo.md` if there
was an export, the saved files in `teardown/visibility/`, new rows in
`features.csv`, and a short summary: page types and counts, markets, search
data with tool and date or "not measured", local search if it applies, the
AI sample ("named in x of y"), the rule for the original's name (not in the
new product's name, domain, ad text, titles or meta tags; only a
lawyer-reviewed comparison page names it), and the three findings that
change the plan.
