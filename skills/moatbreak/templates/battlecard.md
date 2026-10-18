# Battle card: {{ours}} vs {{target}}

<!-- Start from the output of battlecard.py (teardown/battlecard.md) and replace
every "to write". Keep every tag, link and date. Never upgrade a tag: an
"assumed" claim becomes "verified" only after someone checked it and filled
source and checked in features.csv. Write in the sales team's language.
Internal: reviewer quotes stay on this card and never go to a prospect. -->

As of {{YYYY-MM-DD}}. Owner: {{name}}. Next review: {{YYYY-MM-DD, at the latest 90 days later, or when their pricing or changelog changes}}.

## In one line

{{For {who} who {pain from a top complaint theme}, {ours} {does this instead}. Evidence: {theme}, {n} reviews across {n} sources; {differentiator}, features.csv line {n}. Gap in their messaging: {what their hero claim leaves out, from the messaging table in recon.md}.}}

## Where they are weak

<!-- Up to five complaint themes. Each: label, tag, one or two verbatim quotes
with links, and a discovery question the rep asks instead of making a claim. -->

1. **{{theme}}** [reported: {{n}} reviews, {{n}} sources]
   - "{{verbatim quote}}" ({{source}}, {{stars}}) {{url}}
   - Discovery question: {{an open question that lets the prospect name the pain, e.g. "How long does a support ticket take today?"}}

## Where they are strong

<!-- Praise themes. The rep agrees here and moves on; no counter-attack. -->

- **{{theme}}** [reported: {{n}} reviews, {{n}} sources]: {{what they do well, one line}}. Our line: {{how we match it, or "we match it" only if true}}

## Our differentiators

| priority | feature | {{target}} | claim about {{target}} | proof for the prospect |
| --- | --- | --- | --- | --- |
| {{must}} | {{feature}} | {{no / partial}} | [verified, checked {{date}}: {{url}}] | {{demo step, screen, doc link of ours}} |

Do not claim yet: {{own features that are not done}}.

## Objection handling

<!-- One block per objection from the script, plus the ones sales hears in
calls (price, switching effort, risk of a new vendor). Answer: acknowledge,
the fact, the proof, a question back. Two or three sentences. -->

1. "{{objection}}"
   - Answer: {{true, short, no unverified claim about them}}
   - Proof: {{our verified feature, a demo, a document; never a reviewer quote about them}}
   - Data: {{features.csv line n or feedback.json theme}}

## Prices

<!-- Same plan level, same billing period, net or gross on both sides, all
mandatory extras included. No price without a date and a link. Nobody read
their pricing page: write "no price source supplied" and no figure. Prices
that reviewers mention are not their prices and never go here. -->

| plan level | {{target}} | {{ours}} | billing | net or gross | checked | source |
| --- | --- | --- | --- | --- | --- | --- |
| {{entry}} | {{price}} | {{price}} | {{monthly / yearly}} | {{net}} | {{YYYY-MM-DD}} | {{pricing page url}} |

---

## SWOT: {{ours}} against {{target}}

<!-- Copy from the script output. Every line keeps its source reference. -->

**Strengths** ({{ours}}): {{lines with features.csv line n}}

**Weaknesses** ({{ours}}): {{lines with features.csv line n}}

**Opportunities**: {{lines with feedback.json themes/id}}

**Threats**: {{lines with feedback.json praise/id; recent moves from recon.md with date and link}}

## Sources and sample

{{sample sizes, sources, the date range of the checks, the card date, from the script footer}}

---

# Comparison page draft (optional): {{ours}} or {{target}}

<!-- Only for a public "{{target}} alternative" or "{{target}} vs {{ours}}"
page. Use only the rows under "For a comparison page" in the script output:
verified, checked within 90 days, public link. No reviewer quotes, no review
themes, no star ratings of theirs, no screenshots of their product, no logo.
Before publishing, every box of the checklist in references/battlecard.md is
"checked" by a lawyer. Until then the page stays a draft. -->

Status: draft, not reviewed. As of {{YYYY-MM-DD}}. Owner: {{name}}. Next review: {{YYYY-MM-DD}}.
Format: {{singular alternative | plural alternatives (4 to 7 real ones) | {ours} vs {target}}}. URL path: {{/...}}.
Keyword target: {{one primary search, its volume, tool and date, from seo.md or visibility.md | not measured}}.

## {{headline: what {ours} does differently, without their name in a slogan, no "clone", "copy" or "like {target}"}}

{{two sentences: who {ours} is for and the job both products do (same need)}}

## Who each one is best for

- {{ours}}: {{who, and the need from fixes.md it serves}}
- {{target}}: {{who should stay with them, only from page-ready rows of the table, each with that row's footnote number; nothing here that is not in the table}}

| feature | {{ours}} | {{target}}¹ |
| --- | --- | --- |
| {{feature}} | {{yes / partial / no}} | {{yes / partial / no}} |
| {{a feature where they are ahead, so the table is fair}} | {{no}} | {{yes}} |

<!-- Prices like for like: same plan level and billing period, net or gross on
both sides; for consumers, gross total prices incl. VAT (PAngV). -->

| price, {{plan level}}, {{billing}}, {{net or gross}} | {{ours}} | {{target}}² |
| --- | --- | --- |
| {{plan}} | {{price}} | {{price}} |

## Switching from {{target}}

{{what moves over and how: import, export formats, what the customer does, how long it takes; only what {ours} has shipped, built from the switching data in feedback.md and the needs in fixes.md}}

## Questions

<!-- Three to six real questions (sales calls, AI-answer sample Q3 and Q4,
the alternatives keywords). Each answer is a verified fact about them or a
fact about us. FAQPage markup only for what is on the page. -->

**{{question}}**
{{answer}}

¹ As shown on {{their page}}, {{url}}, checked {{YYYY-MM-DD}}.
² Price list of {{target}}, {{url}}, as of {{YYYY-MM-DD}}. Prices change; the current price is on their page.

{{target}} is a {{registered trademark, checked in DPMAregister or EUIPO eSearch on YYYY-MM-DD | name}} of {{owner}}. {{ours}} is not affiliated with, endorsed or sponsored by {{owner}}.

<!-- Proof file (internal): for each row, a dated PDF or archive copy of the
source page, kept in teardown/proof/ and listed in teardown/sources.csv,
never published. -->

## Audit (pages already published, internal)

| page | claim about {{target}} | features.csv line | status: current / stale / unverifiable | action |
| --- | --- | --- | --- | --- |
