# Visibility: {{product}} ({{domain}})

Market: {{country, language, search engine domain}}
Date: {{YYYY-MM-DD}}
Search data: {{tool name and database | user-provided export, tool, date | not measured}}
AI answers: {{n assistants, 5 questions | not sampled}}

<!-- Every number carries its source and date. Kinds: read (public files),
tool (connected SEO tool, its estimate), user-provided (export). Nothing
estimated by the agent. No tool, no export: "not measured". -->

## Public files

| file | URL | read on | finding |
| --- | --- | --- | --- |
| robots.txt | | | Sitemap lines, disallowed areas, AI crawler lines verbatim |
| sitemap | | | {{n}} pages, see `sitemap.md` ({{complete | partial: x of y child sitemaps}}) |
| llms.txt | | | present / not found |

## Page inventory (from sitemap.md)

| type | pages | example | template in recon | notes |
| --- | --- | --- | --- | --- |
| product | | | S{{nn}} | {{programmatic set? content volume?}} |

Programmatic page sets: {{type, count, example, what data fills them | none}}
Comparison pages name: {{rivals | none}}

## Markets

| language / country | how (folder, subdomain, domain) | pages | notes |
| --- | --- | --- | --- |
| de | /de/ | | {{du/Sie, local proof, partial translation?}} |

hreflang: {{values and x-default, from sitemap and key pages | none}}

## Key pages

| ID | page | URL | read on | title (verbatim) | meta description (verbatim) | H1 | structured data types | hreflang | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K01 | home | | | | | | | | |

Navigation (verbatim, in order): {{main menu labels}}
Footer: {{column headings and labels}}

## Search data

Source: {{tool, database (engine, country, language), retrieved YYYY-MM-DD | user-provided export | not measured}}

| metric | value | source | date |
| --- | --- | --- | --- |
| organic keywords | not measured | | |
| estimated organic traffic per month | not measured | | |
| branded share of traffic | not measured | | |
| referring domains | not measured | | |
| Core Web Vitals, mobile (LCP, INP, CLS; field or lab), home and one template | not measured | {{PageSpeed Insights, URL, device}} | |

Keyword themes, branded share, top pages and keyword gap: {{see `seo.md` (seo.py, tool, export date) | not measured}}

Top keywords (by estimated traffic):

| keyword | position | volume | URL | source, date |
| --- | --- | --- | --- | --- |

Top pages and top referring domains: {{tables as above | not measured}}

## Local search (local businesses, or software for them)

| business | Google Business Profile categories | reviews, rating (as shown) | booking or order button (whose service) | date |
| --- | --- | --- | --- | --- |
| | | | | |

| search ("{category} {city}") | domain, location | date | the three businesses in the pack | software their profiles link to |
| --- | --- | --- | --- | --- |
| | | | | |

Local pages in sitemap.md: {{type locations, count, example | none}}

## AI answers (a sample, not a measurement)

| # | question (as asked, market language) |
| --- | --- |
| Q1 | {{Which {category} do you recommend for {audience}?}} |
| Q2 | {{How can I {job} as {audience}, and which tool should I use?}} |
| Q3 | {{What are the best alternatives to {original}?}} |
| Q4 | {{Is {original} worth it for {audience}? What are its downsides?}} |
| Q5 | {{Which {category} meets {market requirement}?}} |

| Q | assistant | model / mode | web search | date | original named (position) | brands named, in order | sources cited |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | | | on / off | | no / yes (n) | | |

Summary: named in {{x}} of {{y}} answers (5 questions, {{n}} assistants, {{date}}).
Downsides named in Q4 (hypotheses for voice of customer, not findings): {{...}}

### Q1, {{assistant}}, {{date}}

> {{the answer, verbatim}}

## Search sample by hand (optional)

| query | engine, domain, language, location | date | original's position | top 10 organic domains | ads on the original's name |
| --- | --- | --- | --- | --- | --- |

## What this changes

- Feature matrix: {{rows added to features.csv, with counts}}
- Positioning: {{where the angle should show up: searches, market, questions}}
- Brand: {{brands to keep distance from; candidates checked as keywords}}
- The original's name on our pages: never in the new product's name, domain or ad text, nor in the titles and meta tags of its own pages. Only a comparison page drafted under `references/battlecard.md` and reviewed by a lawyer names it, in its title, meta description and URL path, as far as needed to say who is compared.
- Competitors to confirm with the user: {{names from answers and searches | none}}
- Not measured or not sampled, and what would measure it: {{...}}
