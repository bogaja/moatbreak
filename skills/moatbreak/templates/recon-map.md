# Recon: {{product}} ({{type: app | SaaS | website | shop}}, {{platform}})

Scope: {{the slice being analysed}}
For: {{who the new product is for, which market}}
Purpose: {{build plan | client offer | go/no-go}}
Date: {{YYYY-MM-DD}}

## Sources

| # | source | URL | read on | notes |
| --- | --- | --- | --- | --- |
| 1 | help center | | | |

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
