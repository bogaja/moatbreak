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
2. **Ranges, not points.** Every number is low-high. State the contingency.
   If the ranges are wide (recon from assumptions, many unknown rows), say so
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

## The report

Structure for a competitor teardown report (also works as the first chapter
of an offer):

1. **Summary**: five bullets. What the original does, what its customers
   hate (with sample size), the opportunity, the recommended scope, the
   effort range.
2. **Product map**: core loop, screens or page types, flows, with counts.
3. **What customers hate and ask for**: top themes with numbers and one or
   two linked quotes each; thin themes marked thin. If voice of customer was
   not run, write "not researched" and offer it as a next step; never fill
   it from general knowledge.
4. **Opportunity and positioning**: the recommended angle and why.
5. **Scope options**: MVP / Plus / Full with features, person-days and price
   range.
6. **Build or buy**.
7. **Risks**: technical hard parts, legal flags, dependencies.
8. **Next steps**: what the client decides, what happens after.

Deliver it in whatever format the session supports best: a document or page
artifact, a PDF, or a Word file if the client wants to edit it.

## Things that do not go into client material

- Screenshots of the original in anything public (internal reports to the
  client are fine).
- Reviewer quotes as testimonials.
- Claims about the original that are not backed by a linked source.
- Internal notes, margins, doubts about the team's estimates.
- Promises of a "perfect copy" or of legal safety.
