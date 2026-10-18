# Recon: {{product}} ({{type: app | SaaS | website | shop}}, {{platform}})

Scope: {{the slice being analysed}}
For: {{who the new product is for, which market}}
Purpose: {{build plan | client offer | go/no-go}}
Date: {{YYYY-MM-DD}}

## Sources

| # | source | URL | read on | notes |
| --- | --- | --- | --- | --- |
| 1 | help center | | | |

## Messaging

<!-- Quote their claim; never reuse it. Promise type: saves time, saves money,
more revenue, fewer no-shows or errors, easier, control, trust and
compliance, or another one, named. -->

| product | hero claim (verbatim) | URL | read on | audience signal | promise type | what it leaves out (need in fixes.md) |
| --- | --- | --- | --- | --- | --- | --- |
| | "" | | | | | {{need n | not researched}} |

## Recent moves (last 12 months)

<!-- Only public, dated sources: changelog, pricing page, press page, app store
version history. A move that touches a verified features.csv row: recheck it.
A move that closes our gap or copies our differentiator: a threat in the SWOT. -->

| date | what changed | type (price, feature, market, plan, partnership, funding) | link | touches features.csv line |
| --- | --- | --- | --- | --- |
| | | | | |

## Core loop

{{one sentence: the thing customers pay for}}

## Inventory

<!-- App/SaaS: screens. Website: page templates. Shop: page types. -->

| ID | screen / page | route or how to reach it | purpose | key components | states seen |
| --- | --- | --- | --- | --- | --- |
| S01 | | | | | empty, filled, error, mobile |

## Flows

```
F01 {{goal}}
    S01 -> S02 -> S03
    happy path clicks: {{n}}
    edge: {{cases}}
```

## Components

| component | variants | states | used on |
| --- | --- | --- | --- |
| Button | primary, secondary, ghost, danger | default, hover, focus, disabled, loading | all |

## Signature elements (do not imitate)

| element | where | why it is distinctive |
| --- | --- | --- |
| {{e.g. mascot, colour pair, custom typeface, slogan}} | | |

## Inferred data model

```
{{Entity}}  {{fields}}
            evidence: {{screen IDs, help articles}}
            confidence: high | medium | guess
```

Relationships: {{User 1-n EventType, EventType 1-n Booking, ...}}

## Commercial promise (shops and subscriptions)

Prices and plans: {{...}}
Shipping: {{costs, free-shipping threshold, delivery time}}
Returns: {{period, who pays}}
Payment methods: {{PayPal, Klarna, Rechnung, SEPA, cards, Apple Pay}}

## Feature matrix

See `features.csv`. Must: {{n}}, should: {{n}}, could: {{n}}, skip: {{n}}.

## Out of scope (cannot or should not be rebuilt)

- {{licensed content, the network, partner deals, signature elements, ...}}

## Size and effort

Screens/pages {{n}}, flows {{n}}, entities {{n}}.
Hard parts: {{list}}.
Size: {{S | M | L | XL}}.
Effort (person-days, from parity.py): MVP {{a-b}}, + should {{c-d}}, + could {{e-f}}.
