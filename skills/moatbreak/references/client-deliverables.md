# Client deliverables

For agencies and freelancers: how to turn a teardown into an offer or a
report a client can read and sign. Write it in the client's language (German
for DACH clients), without jargon, and keep the competitor's name factual.

Files: the client document goes to `teardown/offer.md` (from
`$SKILL/templates/offer.md`) or `teardown/report.md`. Internal notes
(assumptions you are unsure of, margin thoughts, open questions for the
team) go to `teardown/offer-notes.md`, never into the client document.

## The offer

The feature matrix with effort is the core. Build the offer in this order:

1. **Scope packages from parity.py.** At recon time nothing is built, so the
   remaining effort is the whole build:

   ```bash
   python3 $SKILL/scripts/parity.py teardown/features.csv --estimate-only --lang de --markdown \
     --buffer 20 --overhead "QA=15,PM=10" --fixed "Workshop=2-3;Setup=2-3;Design=5-8;Go-live=2-3" \
     --day-rate 650 --out teardown/estimate.md
   ```

   This gives three packages: MVP (must), Plus (+ should), Full (+ could).
   Offer them as such; clients like choosing.
   - `--buffer` is the contingency on the feature effort.
   - `--overhead` adds work that grows with scope (QA, project management) as
     a percentage of the feature effort including the contingency.
   - `--fixed` adds work that does not grow with scope (discovery workshop,
     project setup, design system, content and legal pages set up, go-live,
     training) in person-days, without contingency.
   Use the agency's own historical numbers. If there are none, the values
   above are placeholders: say in the offer notes that they are assumptions,
   so the team can challenge them.
2. **Ranges, not points.** Every number is low-high, copied from
   `teardown/estimate.md` exactly as printed, without rounding, in the
   offer and in the answer. State the contingency. If the ranges are wide (recon from assumptions, many unknown rows), say so
   and offer a paid discovery phase that turns them into a fixed price.
3. **Assumptions and exclusions.** List the `skip` rows (with reasons), the
   unverified and unestimated rows, the hard parts from recon, and what the
   client must supply (texts, images, accounts, API keys, legal review).
4. **Build or buy.** One honest paragraph: which off-the-shelf products
   already do this, what they cost, and why a custom build is (or is not)
   worth it for this client. It builds trust and protects the agency from a
   project that should not exist.
5. **Running costs** the client pays separately: hosting, email and SMS
   sending, payment fees, app store accounts (Apple 99 USD per year, Google
   25 USD once), SaaS tools, maintenance. Give ranges; do not invent exact
   prices.
6. **Legal flags**, short: what the distance check requires and which
   launch obligations apply (`legal-eu-dach.md`). Recommend a legal review;
   do not give legal advice.
7. **What done means.** For a build offer, attach the milestones and
   must-feature acceptance criteria from `teardown/build-brief.md`, so the
   client signs off on testable criteria, not on a feeling.

## The report

Structure for a competitor teardown report (also works as the first chapter
of an offer). A section whose mode or add-on was not run says "not
researched" and offers it as a next step; it is never filled from general
knowledge.

1. **Summary**: five bullets. What the original does, what its customers
   hate (with sample size), the opportunity, the recommended scope, the
   effort range.
2. **Market overview** (when discover ran, or the client asks who else is
   out there): the landscape matrix and positioning map from
   `teardown/landscape.md` and `teardown/landscape.svg`, every cell linked
   to its source; unverified rows marked or left out. When the client named
   the reference product, one line saying so is enough.
3. **Product map**: core loop, screens or page types, flows, with counts.
4. **How it is found** (the visibility add-on): page types and counts,
   markets, search data with tool and date, the AI-answer sample as "named
   in x of y". Values nobody measured say "not measured".
5. **What customers hate and ask for**: top themes with numbers and one or
   two linked quotes each, thin themes marked thin, the sample bias by
   source, and why customers leave and where they go. Run
   `reviews.py --verify` on the report before it is sent.
6. **Opportunity and positioning**: the needs and the recommended angle,
   and why. If the client's sales team competes against the original,
   attach the battle card (`references/battlecard.md`); it is internal to
   the client, because reviewer quotes are on it.
7. **Scope options**: MVP / Plus / Full with features, person-days and price
   range.
8. **Build or buy**.
9. **Risks**: technical hard parts, legal flags (including accessibility
   under the BFSG), dependencies.
10. **Next steps**: what the client decides, what happens after.

Write the report as `teardown/report.md` in the client's language, then
build one HTML file from it and the teardown files behind it:

```bash
python3 $SKILL/scripts/report.py teardown --lang de --title "Wettbewerbsanalyse: X" \
  --as-of 2026-10-17 --out teardown/report.html
```

`report.html` is self-contained (no external fonts, scripts or images, so it
opens offline and can be forwarded or printed to PDF) and accessible
(language set, landmarks, a skip link, real headings and table headers). It
puts `report.md` first, then the market overview with the map inlined, the
product map, how the original is found, the reviews analysis, the needs and
fixes, the estimate, the battle card marked internal, and the legal
checklist. A section whose mode did not run says "not researched". Run
`reviews.py --verify` on `report.md` and the other quoted files before
building it. If the client wants to edit the report, hand over a document
or Word file made from `report.md` instead.

## Things that do not go into client material

- Screenshots of the original in anything public (internal reports to the
  client are fine).
- Reviewer quotes as testimonials.
- Claims about the original that are not backed by a linked source, and in
  anything public (a comparison page, a sales deck) any claim that is not
  verified and dated (`references/battlecard.md`).
- Internal notes, margins, doubts about the team's estimates.
- Promises of a "perfect copy" or of legal safety.
