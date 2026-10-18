# Legal checklist: EU, Germany, Austria, Switzerland

Flags for the user and their lawyer, not legal advice. Laws change; this
reflects the state of late 2026. Before launching anything with money at
stake, have a lawyer (in Germany: Fachanwalt für gewerblichen Rechtsschutz
or IT-Recht) review the distance check and the launch pages.

Contents: 1 what is free to rebuild, 2 what is protected, 3 the distance
check, 4 marketing against the original, 5 launch obligations, 6 research
conduct.

## 1. What is free to rebuild

- **Functionality and ideas.** Copyright protects a program's code, not its
  ideas, principles, functions or file formats (EU Software Directive; in
  Germany § 69a UrhG; confirmed by the CJEU in SAS Institute, 2012). This is
  the legal basis of clean-room rebuilding: study what it does, write your
  own code.
- **Common patterns.** Standard UI conventions (a cart icon top right, a
  two-step checkout, a calendar grid) belong to everyone.
- **Prices, plans, feature lists** as facts to position against.

## 2. What is protected

- **Code, texts, images, icons, illustrations, photos, videos** (copyright).
  Never reuse, not even "just for now".
- **Names, logos, slogans, product names** (trademarks; in Germany also
  company names and work titles without registration, § 5 MarkenG, and an
  app's name can be a work title).
- **The look of interfaces, icons and graphic symbols** (design law). EU
  designs are protected when registered, and unregistered for 3 years from
  first disclosure in the EU. Check EUIPO DesignView for the original's
  registered designs.
- **Databases** (EU database right, § 87a ff. UrhG): taking a substantial
  part of a catalogue, listing set or review corpus can infringe even if no
  single entry is protected. Do not import the original's product data.
  The legal way to fill the new product: its users enter their own data or
  import their own export, or an official API or partner feed is used
  within its terms.
- **Imitation as unfair competition.**
  - Germany, § 4 Nr. 3 UWG: offering an imitation of a product with
    "wettbewerbliche Eigenart" (competitive individuality) is unfair if it
    (a) causes avoidable confusion about who made it, (b) exploits or
    damages the original's reputation unfairly, or (c) uses knowledge or
    documents obtained dishonestly. Point (c) is why recon uses only public
    sources and the user's own account within its terms.
  - Austria: the general clause of the UWG (§ 1) covers slavish imitation
    with unfair circumstances in a similar way.
  - Switzerland: Art. 5 lit. c UWG forbids taking over another's
    market-ready work result by technical reproduction without reasonable
    own effort. Rebuilding from scratch is own effort; copying files is not.

## 3. The distance check

Fill this in as `teardown/legal.md` before launch. Rate each row
**same**, **similar** or **distinct**, with evidence (a screenshot pair, the
sweep output, the trademark search with date).

| dimension | required | how to check |
| --- | --- | --- |
| name | distinct | brand mode step 2, all checks run |
| logo and app icon | distinct | side by side with the original's |
| signature elements (from recon step 6) | distinct, none reused | list each and what replaced it |
| primary colour and colour pair | distinct | sweep.py near-colour warnings, by eye |
| typeface | distinct if theirs is custom or signature | font names in both |
| copy and microcopy | distinct | written fresh, spot-check the 10 most-seen strings |
| images, icons, illustrations | distinct | own, licensed or open-licensed only, with licence noted |
| overall impression of key screens | similar is acceptable only if every row above is distinct | imgdiff layout score plus the screens side by side, colour included |
| domain, handles, store listing | distinct | no typo domains, no "X alternative" in the app name |
| source of knowledge | public or own account only | the recon sources table and the line under it for the user's own account |

The rule of thumb: the more rows are "similar", the higher the risk, and a
"similar" overall impression combined with similar colours, typeface or
signature elements is the classic case for confusion about origin. Any
"same" in a row that requires "distinct" blocks the launch.

## 4. Marketing against the original

Any advertising that makes the competitor or its products identifiable is
comparative advertising (Germany § 6 (1) UWG): an "X alternative" page, an
"X vs us" table, a sales slide, what a rep sends to a prospect. Austria
(§ 2a UWG) and Switzerland (Art. 3 (1) lit. e UWG) have their own rules;
the EU baseline is Directive 2006/114/EC, Art. 4. `references/battlecard.md`
turns this section into a checklist for the lawyer, and `battlecard.py`
lists which feature claims are verified, fresh and backed by a public link.

- **Comparative advertising is allowed only if all six hold** (§ 6 (2)
  UWG):
  1. the products meet the same need or serve the same purpose;
  2. the comparison is objective and about one or more material, relevant,
     verifiable and typical features, or the price;
  3. it causes no confusion between the advertiser and the competitor, their
     products or their marks;
  4. it does not take unfair advantage of, or damage, the reputation of the
     competitor's mark;
  5. it does not denigrate the competitor's products, activities or
     business;
  6. it does not present the product as an imitation or replica of one sold
     under a protected mark. "X clone", "like X but cheaper" and "our X
     copy" fail here, which matters for every rebuild.
- **Misleading claims and omissions** apply on top. § 5 UWG covers
  statements in comparative advertising too: every statement about them and
  about you must be true and current when it is seen, and "the only", "the
  first" or "the best" need proof of a clear lead. § 5a UWG makes leaving out
  what the reader needs misleading as well: the feature they have and you
  lack, the add-on price of your feature, the plan a feature requires. A
  table that shows only the rows you win can mislead when the left-out rows
  matter for the decision; a selection as such is allowed (CJEU, Lidl
  Belgium, C-356/04).
- **Verifiable means checkable.** Say where and how the reader can check
  each claim (CJEU, Lidl Belgium, C-356/04, 2006), and keep the proof: a
  dated PDF or archive copy of their page, so a challenge can be answered.
  Reviews of their product are not proof of a fact about it, and quoting
  them on a page invites a denigration claim (also § 4 nos. 1 and 2 UWG:
  disparaging a competitor, or spreading claims about it that cannot be
  proven).
- **Price comparisons** compare like with like: same plan level, scope and
  billing period, the same currency, net or gross on both sides, mandatory
  extras included; consumers see total prices including VAT (PAngV). Give
  the date and the source ("Stand: 17.10.2026", their pricing page). When
  their prices change, update or remove the comparison: an outdated price
  comparison is misleading.
- **Their name and mark on your page.** Use the word as far as needed to say
  who is compared (title, table header, URL path on your own domain). No
  logo, colours, trade dress, screenshots or copied text; add that the mark
  belongs to its owner and that there is no affiliation. A comparison that
  meets all conditions of comparative advertising cannot be stopped under
  trademark law (CJEU, O2 v Hutchison, C-533/06, 2008); one that presents
  your product as a replica takes unfair advantage of the mark (CJEU,
  L'Oréal v Bellure, C-487/07, 2009). Their mark never goes into your
  domain, product name or app name. Have every comparison page reviewed
  before it goes live.
- **Search ads.** Bidding on the competitor's brand as a keyword is
  generally allowed in the EU (CJEU, Google France, 2010) as long as the ad
  makes clear it is not from them. Do not use their mark in the ad text,
  display URL or domain.
- **Reviews you show** (Germany § 5b (3) UWG): say whether and how you check
  that reviews come from real customers. Buying, faking or selectively
  hiding reviews is prohibited.

## 5. Launch obligations the original's market expects

US templates usually miss these. Check the ones that apply to the product.

**Every website or app (DE/AT/CH)**
- Imprint: Germany § 5 DDG (replaced § 5 TMG in 2024), plus § 18 MStV for
  editorial content; Austria § 5 ECG and § 25 MedienG; Switzerland Art. 3
  (1) lit. s UWG for online offers.
- Privacy: privacy notice (Art. 13 GDPR/DSGVO), a data processing agreement
  (Art. 28) with every processor (hosting, email, analytics, payment,
  support tools), a legal basis for transfers outside the EU (EU-US Data
  Privacy Framework or standard contractual clauses), records of processing
  (Art. 30). Switzerland: revised FADP (revDSG, since 2023).
- Special categories (Art. 9 GDPR): health data such as allergies,
  treatments, medication or notes about a person's body (salons, studios,
  practices, fitness) need an Art. 9 basis, usually explicit consent, plus
  tight access rights; consider a data protection impact assessment.
- Marketing email and SMS: prior express consent (Germany § 7 UWG), in
  practice proven by double opt-in; transactional messages (confirmation,
  reminder of a booked appointment) are not advertising.
- Cookies and tracking: consent before non-essential storage or access on
  the device (Germany § 25 TDDDG, formerly TTDSG). A cookieless,
  privacy-friendly analytics setup avoids most of it.
- Accessibility: Germany's BFSG applies since 28 June 2025 to many consumer
  e-commerce services (online shops, booking and banking services, apps used
  to conclude consumer contracts). Micro-enterprises (under 10 employees and
  at most EUR 2 million turnover or balance sheet) are exempt for services.
  Practical bar: WCAG 2.1 AA (EN 301 549). For the lawyer: accessibility
  information under § 14 BFSG with Anlage 3 (a description of the service
  and how it meets the requirements), in the terms or in another clearly
  visible way. A requirement that is not met is allowed only under the
  Act's exceptions (fundamental alteration, disproportionate burden), with a
  documented assessment. The lawyer confirms the content.

**Selling to consumers online (shops, subscriptions, paid apps)**
- Withdrawal: cancellation policy (Widerrufsbelehrung) and model withdrawal
  form; exceptions for digital content need explicit consent and
  acknowledgement.
- Order button: it must say "zahlungspflichtig bestellen" or something
  equally unambiguous (§ 312j (3) BGB).
- Refunds and returns after withdrawal (§ 357 BGB): payments are refunded
  within 14 days, the original payment method is used, the trader may hold
  the refund until the goods are back or the return is proven, and the
  consumer bears the direct return costs only if told so beforehand. Long
  refund delays are a legal problem, not only a service one.
- Subscriptions: a cancellation button on the website for contracts
  concluded online (§ 312k BGB, "Kündigungsbutton").
- Deposits, no-show and cancellation fees: agree them clearly before the
  booking, keep them proportionate to the actual loss, and let the customer
  prove a lower loss (flat-rate damages in standard terms, § 309 no. 5 BGB).
- Prices: total prices incl. VAT, unit prices where required, and for any
  price reduction the lowest price of the previous 30 days (§ 11 PAngV).
- Pre-contract information (Art. 246a EGBGB), terms and conditions, delivery
  times, accepted payment methods. In DACH, customers expect PayPal, Klarna
  or invoice purchase (Kauf auf Rechnung) and SEPA.
- Consumer dispute resolution: Germany § 36 VSBG statement if the business
  has more than 10 employees. The EU online dispute resolution (OS) platform
  was discontinued in 2025; remove old OS links from templates.

**Product categories with extra rules**
- Platforms with user content or marketplaces: Digital Services Act
  (notice and action, transparent terms; marketplaces must verify traders).
- AI features: EU AI Act Art. 50 transparency obligations (people must be
  told they are talking to an AI; synthetic content marked) apply from
  2 August 2026; check whether the EU's simplification package moved any
  of these dates.
- Invoicing and accounting tools: GoBD; in Germany businesses must be able
  to receive e-invoices (XRechnung, ZUGFeRD) since 2025, with sending
  obligations phased in from 2027.
- Health, finance, payments, legal advice: regulated; usually out of scope
  for a rebuild without the licence.

## 6. Research conduct

- Respect the terms of every source; use official feeds and APIs.
- Short verbatim quotes with source in an analysis are normally covered by
  the quotation right (Germany § 51 UrhG); do not republish review sets.
- Screenshots of the original are for internal comparison. Do not put them
  into public material, ads or the store listing.
- Do not contact the original's employees for internal information, and do
  not use documents from former employees or partners.
- **Research data is personal data** (DSGVO), for the lawyer to confirm: the
  review sample (`teardown/reviews.csv`; its URLs often lead to a reviewer's
  profile), the quotes in every report and battle card, the saved files in
  `teardown/visibility/` (AI answers verbatim) and `teardown/proof/`. The
  legal basis is usually legitimate interests (Art. 6 (1) (f) DSGVO); write
  the balancing down once per project. Data minimisation: no author names or
  handles in any file; names of staff, customers or reviewers left out of
  quotes with "..." (`reviews.py --verify` accepts the cut). A battle card
  hands reviewer quotes to a client's sales team: it stays internal to that
  team. Keep `teardown/` out of public repositories, and delete the review
  sample, the saved answers and the proof copies when the project ends,
  unless a claim still in use needs its proof; then keep only that proof,
  with the date it may be deleted.
