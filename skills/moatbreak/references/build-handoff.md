# Build handoff

Turn the teardown into a brief a build can start from: what to build in
which order, how to know each piece is done, what data the product keeps,
which decisions the user makes before any code, and the gate before launch.
The brief is the contract between the teardown and the build; parity mode
later checks the build against it.

Output: `teardown/build-brief.md` (template `$SKILL/templates/build-brief.md`)
and `teardown/contrast.md` from contrast.py.

Read first: `teardown/recon.md` and `teardown/features.csv`, and if they
exist `teardown/fixes.md`, `teardown/estimate.md` and `teardown/brand.md`.
Without a feature matrix there is nothing to hand off: run recon first. A
feature that is not in the matrix does not go into the brief; add it to the
matrix first, with an effort, so the offer, the brief and parity count the
same work.

## Step 1: milestones

Three milestones, straight from the matrix and the same tiers as the offer:

| milestone | rows | ends with |
| --- | --- | --- |
| M1 MVP | every `must` row whose `clone` is not `yes` or `skip` | the core loop (F01) works end to end for a real user |
| M2 + should | the open `should` rows | the next most used flows and the fixes that carry the angle |
| M3 + could | the open `could` rows | the rest; often cut or moved to a later version |

Take the person-days per milestone from `teardown/estimate.md` (or run
`parity.py --estimate-only` as in recon step 10), so the brief and the offer
show the same numbers. Inside a milestone, order by dependencies: data model
and sign-in first, then the core loop in flow order, then what hangs off it.

Rows with `original` = `no` (niche needs, fixes from voice of customer) are
the reason the product exists. If a fix that carries the angle is a
`should`, ask the user whether it moves into M1; if yes, change its
priority in the matrix, not only in the brief.

Each milestone ends with a demo: the flows it finishes, walked on a phone and
on a desktop, with its acceptance criteria ticked.

## Step 2: acceptance criteria

Every `must` feature gets testable lines in Given / When / Then form (in
German: Angenommen / Wenn / Dann). Write them in the user's language.

- At least one happy path and one edge or error case per feature, taken from
  the flow edges and the states recon recorded (empty, loading, error, no
  permission, out of stock, mobile).
- Observable outcomes only: what the person sees, which email arrives, what
  is stored. "Fast", "intuitive" and "works well" are not criteria; "the
  free slots show within 2 seconds on a mid-range phone on 4G" is.
- Concrete values: dates, amounts, time zones, counts.
- Name the IDs: the feature row, the screen (S07), the flow (F01), so parity
  mode can tick them off.
- A fix from voice of customer gets a criterion that proves the complaint is
  gone, with a pointer to its need in `fixes.md` (the need, with its linked
  quotes, not the raw keyword theme).
- If the visibility add-on ran, its rows in the matrix (pages per language
  with hreflang, structured data, sitemap and robots.txt, redirects) get
  criteria like any other feature, so the rebuild is not launched invisible.
- Launch obligations that apply (`legal-eu-dach.md` section 5) become
  criteria too: the order button text, the withdrawal link, consent before
  tracking, double opt-in for marketing email, the cancellation button.

```
F01 Guest books a meeting (S07 -> S10)
Feature: Book a slot as a guest without an account

Given a host available Mon-Fri 09:00-17:00 Europe/Berlin with a 30-minute event type
When a guest whose browser is set to Europe/London opens the booking page for a Monday
Then the first slot shown is 08:00
  and the page says the times are in the guest's time zone

Given a guest has the details form for 10:00 open
When another guest books 10:00 first and the first guest submits
Then the first guest sees that the time was just taken, with the next free slots
  and only one booking for 10:00 is stored
```

## Step 3: data model and API sketch

Start from "Inferred data model" in `recon.md`. For each entity: fields with
types, required or optional, relationships, and two flags: personal data
(DSGVO) and special category (Art. 9 GDPR, such as health data, which brings
consent, tight access rights and possibly a data protection impact
assessment into the brief). Keep the confidence: a `guess` stays marked "to
confirm" until the build proves it.

Then an API sketch for the must flows only: the operations each flow needs,
who may call them, and what leaves the system (emails, webhooks, calendar
writes). Keep it at the level of `POST /bookings`: enough to agree on, not a
specification to freeze.

```
Booking   id, event_type_id -> EventType, start_at (UTC), end_at (UTC),
          guest_name [personal], guest_email [personal],
          status (confirmed | cancelled), answers (json) [personal; special
          category if a question asks about health]
          confidence: high (S09, S10)

GET    /event-types/{id}/slots      guest, no sign-in        F01
POST   /event-types/{id}/bookings   guest, no sign-in        F01  -> email to both sides
PATCH  /bookings/{id}               guest via signed link    F03  -> email to both sides
```

Clean room: design the model from what the product visibly does and from
its public API docs, with your own names. Never take schemas, field lists or
endpoints from the original's code bundles or captured private API calls
(see the ground rules in `SKILL.md`).

## Step 4: stack questions

Ask, do not assume. The stack decides cost, hosting region and who can
maintain the product, and it is the user's decision. Put the open questions
to the user in one message, with what each answer changes; skip the ones
recon already answered.

| question | why it matters |
| --- | --- |
| What does the team (or the client's team) already build and run? | the cheapest stack is the one someone can maintain after launch |
| Web app, installable web app (PWA) or native apps, and which stores? | native roughly doubles the UI work; store accounts and reviews add time and running costs |
| Where may data be hosted, EU only? | transfers under the DSGVO, data processing agreements, what the client's customers expect |
| Shop or website: an existing platform (Shopify, Shopware, WooCommerce) or custom? | a platform turns many matrix rows into configuration, custom turns them into code |
| How do people sign in: password, magic link, passkeys, Google, company SSO? | changes the sign-in effort and how accessible sign-in is (WCAG 3.3.8) |
| Which payment providers and methods? | DACH customers expect PayPal, Klarna or invoice purchase, and SEPA; each one is an integration |
| Which email and SMS provider, from which region? | deliverability, a data processing agreement, running costs |
| Which systems must it talk to (calendar, ERP, accounting such as DATEV, CRM)? | integrations are usually among the hard parts recon found |
| Which languages and markets at launch? | translations planned from day one are cheap, added later they are a rework |
| One customer or many (multi-tenant)? | tenancy changes the data model and every query |
| Who runs it after launch, and what may it cost per month? | hosting, monitoring, maintenance contract |
| Is the operator a micro-enterprise (under 10 people and at most EUR 2 million turnover or balance sheet)? | decides whether the BFSG applies to the service (see `legal-eu-dach.md`); build to the checklist below anyway |

If the user says "you decide", propose a stack with one line of reasoning per
choice and write it into the brief as assumptions, which the user confirms.
If an answer changes the effort, update the matrix and rerun the estimate.

## Step 5: accessibility

Germany's BFSG (applies since 28 June 2025) makes many consumer services
accessible by law: online shops, booking services, apps used to conclude
consumer contracts (scope and the micro-enterprise exemption are in
`legal-eu-dach.md`). Its harmonised standard is EN 301 549, which points to
WCAG 2.1 AA for web content. Build to WCAG 2.2 AA: it contains every 2.1 AA
criterion except 4.1.1 Parsing, which 2.2 dropped as obsolete, plus six new
A and AA criteria marked "new" below. The checklist is a set of build and
test items, not a legal assessment.

**Colour**

- Text 4.5:1, large text 3:1, component boundaries, focus indicators and
  meaningful icons or chart marks 3:1 (1.4.3, 1.4.11). Check it with the
  script (brand mode step 3 explains the palette entry), and include the
  states: hover, focus, error, selected, and placeholder text that carries
  information. Disabled controls are exempt.

  ```bash
  python3 $SKILL/scripts/contrast.py --palette teardown/brand.json --lang de --markdown --out teardown/contrast.md
  ```

- Colour is never the only signal: errors, required fields, free or booked
  slots, stock and chart series also have text or a shape (1.4.1).

**Keyboard and focus**

- Every function works with the keyboard alone, in a sensible order, with no
  trap: date pickers, menus, modals, the cart, the checkout (2.1.1, 2.1.2,
  2.4.3).
- Focus is always visible (2.4.7) and never completely hidden behind a
  sticky header, a cookie banner or a chat widget (2.4.11, new).
- A skip link or landmarks get past repeated navigation (2.4.1).

**Pointer and touch**

- Targets are at least 24 by 24 CSS pixels, or have that much space around
  them (2.5.8, new).
- Whatever works by dragging (calendar slots, sliders, reordering, maps)
  also works with single clicks or taps (2.5.7, new).

**Forms and sign-in**

- Every field has a visible label; an error says what is wrong and how to
  fix it, next to the field (1.3.1, 3.3.1, 3.3.2, 3.3.3).
- Personal fields have `autocomplete` (1.3.5), and data entered earlier in
  the same process is filled in or offered again instead of typed twice,
  such as "billing address same as delivery" (3.3.7, new).
- Sign-in needs no puzzle or memory test: pasting and password managers
  work, or there is a magic link or a passkey (3.3.8, new). A CAPTCHA that
  asks for distorted text needs an alternative.
- Help (contact, chat, FAQ link) is in the same place on every page that
  has it (3.2.6, new).
- Time limits, such as a held slot or a checkout session, can be turned off,
  adjusted or extended (2.2.1).

**Content and structure**

- Headings, lists and tables are real markup and the page language is set
  (1.3.1, 3.1.1).
- Images have alternative text; icon-only buttons have an accessible name
  (1.1.1, 4.1.2).
- Status messages ("added to cart", "saved") reach screen readers without
  moving the focus (4.1.3).
- The page works at 320 CSS pixels wide without horizontal scrolling, at
  200% zoom and with wider text spacing (1.4.10, 1.4.4, 1.4.12).
- Moving content can be paused and nothing flashes more than three times a
  second (2.2.2, 2.3.1). Respecting `prefers-reduced-motion` is good
  practice, not an AA criterion.
- Videos have captions, audio has a transcript (1.2.2, 1.2.1).

**Statement**

- A lawyer item, not a build item: accessibility information under § 14
  BFSG with Anlage 3 (a description of the service and how it meets the
  requirements), in the terms or on a page. A requirement that is not met is
  allowed only under the BFSG exceptions (fundamental alteration,
  disproportionate burden), with a documented assessment; listing a gap with
  a date does not make it lawful. The lawyer confirms the content.

Test it three ways before each milestone demo: an automated scan (axe,
Lighthouse or WAVE) in CI, which catches only part of the problems; the core
flows with the keyboard alone; and the core flows with a screen reader
(VoiceOver on iOS and macOS, TalkBack on Android, NVDA on Windows). Record
what was tested, on which device, and when. A check nobody ran is "to run".

The original's accessibility is an angle. Run contrast.py on its brand
colours (`teardown/brand.json` without a `palette` key reads them from
`colors`) and walk its core flow with the keyboard. What fails there is a fix
to beat it on: add it to `fixes.md` and as a row with `original` = `no`.
Claims about the original's accessibility in marketing are comparative
advertising (`legal-eu-dach.md` section 4).

## Step 6: test plan

One table in the brief: what is tested, how, and when.

| layer | what | how | when |
| --- | --- | --- | --- |
| acceptance | every Given / When / Then line | automated end-to-end tests for the core flows (F01 first), the rest by hand from the brief | each milestone |
| rules | money, VAT, prices, time zones, availability, stock, permissions | unit tests with fixed dates and amounts | with the code |
| edge cases | the flow edges and states from recon | in the end-to-end tests, or by hand | each milestone |
| legal flows | order button, withdrawal, cancellation button, consent before tracking, double opt-in, imprint and privacy links on every page | acceptance criteria, checked by hand | M1 and before launch |
| accessibility | the step 5 checklist | contrast.py, automated scan, keyboard and screen reader | each milestone |
| devices | the viewports parity mode uses, 1440x900 and 390x844, plus a real phone | screenshots into `teardown/new-screens/`, which parity mode reuses | each milestone |
| performance | key pages on mobile: Core Web Vitals (LCP, INP, CLS) | a public PageSpeed Insights run with URL, device and date, compared with the original's row in `teardown/visibility.md` (parity step 3) | before launch |
| test data | everything | seed data written fresh; never the original's catalogue or reviews, never real customer data in test systems | always |

Name who signs off each milestone (the user or the client) and what blocks
one: an open critical bug, or a must criterion that fails.

## Step 7: the pre-launch gate

Launch only when every row passes. Each row is pass, fail or to run, with
the date and the evidence. Nothing passes because it is probably fine.

The brief is written before the gate runs, so every row in it starts as
"to run", even when the matrix already shows features done or you ran
parity.py or contrast.py while writing it. Those readings go into their own
sections with the date (contrast.py into the accessibility checklist, the
open must rows into M1), not into the gate. A row changes only when that
gate is run on the build, after a milestone or before launch.

| gate | command or file | passes when |
| --- | --- | --- |
| parity | `python3 $SKILL/scripts/parity.py teardown/features.csv --lang de --markdown --out teardown/parity.md` | verdict shippable: every must done, feature score 80+, no open critical or major bug (`references/parity.md` step 4) |
| acceptance | `teardown/build-brief.md` | every must criterion ticked |
| signature screens | `imgdiff.py` per signature screen (`references/parity.md` step 2) | no high layout score on a signature element |
| brand | `teardown/brand.md` (brand mode) | every name check run and dated, none left "to run" |
| contrast | `python3 $SKILL/scripts/contrast.py --palette teardown/brand.json --markdown --out teardown/contrast.md` | exit 0 |
| leftovers | `python3 $SKILL/scripts/sweep.py . --config teardown/brand.json` | exit 0, near-colour warnings looked at by eye |
| store listing (apps) | `python3 $SKILL/scripts/listing.py teardown/listing.json --config teardown/brand.json` | exit 0 (`references/launch.md`) |
| sources | `python3 $SKILL/scripts/sources.py teardown --as-of {today}` | exit 0: every screenshot and proof copy has its URL and date |
| distance check | `teardown/legal.md` (`legal-eu-dach.md` section 3) | every row that must be distinct is distinct, no "same" |
| launch obligations | `teardown/legal.md` (`legal-eu-dach.md` section 5) | every obligation that applies is ticked |
| accessibility | step 5 checklist in the brief | every item ticked, with the test date |
| legal review | the user's decision | the user decided whether a lawyer reviews the distance check and launch pages, and the decision is written down |

parity.py (`--fail-under 80`), contrast.py and sweep.py exit 1 on a failure,
so all three can run in CI and block a deploy. The gate records facts; it is
not legal clearance. The user decides and launches.

## Handing the brief to the build

Give the build (a build skill in the session, a developer, an agency) the
brief, one milestone at a time, plus `recon.md` for screen and flow details.
Never `teardown/screens/`: the original's screenshots are reference and must
not become assets. After each milestone, update `clone` in `features.csv`,
take the new screenshots and run parity mode.

## Output

`teardown/build-brief.md` with milestones, acceptance criteria, data model
and API sketch, stack answers or open questions, the accessibility checklist,
the test plan and the gate; `teardown/contrast.md`. A short summary: the
milestones with person-days, the open stack questions, and the riskiest
criteria.
