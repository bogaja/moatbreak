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
| source of knowledge | public or own account only | the recon sources table |

The rule of thumb: the more rows are "similar", the higher the risk, and a
"similar" overall impression combined with similar colours, typeface or
signature elements is the classic case for confusion about origin. Any
"same" in a row that requires "distinct" blocks the launch.

## 4. Marketing against the original

- **Comparative advertising** (Germany § 6 UWG, based on the EU directive)
  is allowed if it compares relevant, verifiable features objectively,
  without denigrating, causing confusion or riding on the original's
  reputation. A comparison or "alternative to X" page is possible, but
  have it reviewed.
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
  Practical bar: WCAG 2.1 AA (EN 301 549), plus an accessibility statement.

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
