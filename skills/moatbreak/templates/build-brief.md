# Build brief: {{new product}} (from the teardown of {{original}})

<!-- Write in the user's language. Features and effort come from teardown/features.csv;
     change the matrix first, then this brief. See references/build-handoff.md. -->

For: {{user or client}}
Date: {{YYYY-MM-DD}}
Inputs: recon.md ({{date}}), features.csv ({{n}} rows), fixes.md ({{date | not researched}}),
brand.md ({{date | not yet}})

## Goal

{{the core loop in one sentence}}
Better than the original because: {{the angle from fixes.md, with its theme | not researched}}

## Milestones

| milestone | features (matrix rows) | person-days | ends with (demo) |
| --- | --- | --- | --- |
| M1 MVP | {{open must rows}} | {{a-b}} | {{F01 end to end on a phone and a desktop}} |
| M2 + should | {{open should rows}} | {{c-d}} | {{...}} |
| M3 + could | {{open could rows}} | {{e-f}} | {{...}} |

Person-days from `teardown/estimate.md`, {{n}} % contingency on feature work.
Build order in M1: {{data model, sign-in, F01 in flow order, ...}}

## Acceptance criteria (must features)

### {{feature}} ({{area}}, {{S07}}, {{F01}})

```
Given {{starting state, with concrete values}}
When {{action}}
Then {{observable result}}

Given {{edge or error state from recon}}
When {{action}}
Then {{observable result}}
```

## Data model

```
{{Entity}}  {{field}} ({{type}}, {{required | optional}}) [{{personal | special category}}]
            relations: {{...}}
            confidence: {{high | medium | to confirm}}
```

Personal data: {{entities and fields}}
Special categories (Art. 9 GDPR): {{none | fields, consent, who may see them}}

## API sketch (must flows)

| operation | who may call it | flow | leaves the system |
| --- | --- | --- | --- |
| {{POST /bookings}} | {{guest, no sign-in}} | {{F01}} | {{email to both sides}} |

## Stack

| question | answer | decided by, date (or "assumption") |
| --- | --- | --- |
| team and what it already runs | | |
| web, PWA or native; which stores | | |
| hosting region | | |
| platform or custom (shop, website) | | |
| sign-in | | |
| payment providers and methods | | |
| email and SMS provider | | |
| integrations | | |
| languages and markets at launch | | |
| one customer or many | | |
| operations and monthly running costs | | |
| micro-enterprise (BFSG) | | |

## Accessibility (build target WCAG 2.2 AA; legal reference for the BFSG: EN 301 549, which points to WCAG 2.1 AA)

| item | criterion | status | tested on, date |
| --- | --- | --- | --- |
| contrast: `contrast.py` exits 0, states included | 1.4.3, 1.4.11 | to run | |
| colour is not the only signal | 1.4.1 | to run | |
| keyboard only, logical order, no trap | 2.1.1, 2.1.2, 2.4.3 | to run | |
| focus visible and not hidden | 2.4.7, 2.4.11 | to run | |
| skip link or landmarks | 2.4.1 | to run | |
| targets at least 24x24 px | 2.5.8 | to run | |
| no drag-only actions | 2.5.7 | to run | |
| labels and error messages | 1.3.1, 3.3.1, 3.3.2, 3.3.3 | to run | |
| autocomplete, no redundant entry | 1.3.5, 3.3.7 | to run | |
| sign-in without puzzles, paste works | 3.3.8 | to run | |
| help in the same place | 3.2.6 | to run | |
| time limits adjustable | 2.2.1 | to run | |
| real headings and lists, page language | 1.3.1, 3.1.1 | to run | |
| alt text, names for icon buttons | 1.1.1, 4.1.2 | to run | |
| status messages announced | 4.1.3 | to run | |
| 320px reflow, 200% zoom, text spacing | 1.4.10, 1.4.4, 1.4.12 | to run | |
| pause moving content, no flashing | 2.2.2, 2.3.1 | to run | |
| captions and transcripts | 1.2.2, 1.2.1 | to run | |
| automated scan in CI | - | to run | |
| keyboard and screen reader walk of the core flows | - | to run | |
| accessibility information (§ 14 BFSG with Anlage 3: the service and how it meets the requirements), in the terms or on a page; content confirmed by the lawyer | BFSG | to run | |

## Test plan

| layer | what | how | when |
| --- | --- | --- | --- |
| acceptance | the criteria above | {{end-to-end tests for F01, ...; the rest by hand}} | each milestone |
| rules | {{money, VAT, time zones, availability, stock, permissions}} | unit tests with fixed dates and amounts | with the code |
| edge cases | {{flow edges and states from recon}} | | each milestone |
| legal flows | {{order button, withdrawal, cancellation button, consent, double opt-in}} | by hand | M1 and before launch |
| accessibility | the checklist above | contrast.py, scan, keyboard, screen reader | each milestone |
| devices | 1440x900, 390x844, {{real phone}} | screenshots into `teardown/new-screens/` | each milestone |
| performance | {{key pages}} | public PageSpeed run, compared with the original's | before launch |
| test data | everything | fresh seed data only | always |

Signs off each milestone: {{who}}
Blocks a milestone: an open critical bug, a must criterion that fails, {{...}}

## Pre-launch gate

<!-- Every row stays "to run" in the brief as first written, even if a check
ran while writing it (its result goes into its own section). Fill a row only
when that gate runs on the build, with the date and the evidence. -->

| gate | evidence | status | date |
| --- | --- | --- | --- |
| parity verdict shippable | `teardown/parity.md` | to run | |
| every must criterion ticked | this brief | to run | |
| no high layout score on a signature screen | `teardown/diffs/` | to run | |
| brand checks run and dated | `teardown/brand.md` | to run | |
| contrast exits 0 | `teardown/contrast.md` | to run | |
| sweep exits 0, near colours checked by eye | sweep.py output | to run | |
| distance check: every required row distinct | `teardown/legal.md` | to run | |
| launch obligations ticked | `teardown/legal.md` | to run | |
| accessibility checklist ticked | this brief | to run | |
| legal review decided | {{user's decision, date}} | to run | |

Launch when every row passes. The user decides and launches.

## Open questions

- {{question, who answers it, by when}}
