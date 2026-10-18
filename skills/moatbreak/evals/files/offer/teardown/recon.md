<!-- Synthetic eval fixture for the Moatbreak evals. ExampleSlot, its pages and
all data below are fictional; every URL is on example.com. -->

# Recon: ExampleSlot (SaaS, web app with iOS app)

Scope: online booking for hair salons: booking page, availability, notifications, deposits
For: Friseur Beispiel GmbH, three hair salons in Cologne, market Germany
Purpose: client offer
Date: 2026-10-01

## Sources

| # | source | URL | read on | notes |
| --- | --- | --- | --- | --- |
| 1 | help center | https://exampleslot.example.com/hilfe | 2026-10-01 | 48 articles |
| 2 | pricing page | https://exampleslot.example.com/preise | 2026-10-01 | Basic, Pro; deposits and three locations only in Pro |
| 3 | changelog | https://exampleslot.example.com/changelog | 2026-10-01 | last entry 2026-09-15 |
| 4 | app store listing | https://example.com/apps/exampleslot | 2026-10-01 | iOS only |

## Core loop

A salon client picks one or more services, a stylist and a free slot, and books without an account; the salon sees the booking in its calendar.

## Inventory

12 screens (S01-S12): booking page, service picker, slot picker, details form, confirmation, salon calendar, client file, staff, services, opening hours, settings, statistics.

## Flows

```
F01 Client books two services
    S01 booking page -> S02 services -> S03 slot -> S04 details -> S05 confirmed
    happy path clicks: 6
    edge: no free slot this week, slot taken while filling the form, deposit declined
F02 Client reschedules from the email link
F03 Salon blocks a stylist's afternoon
F04 Salon records an allergy note on a client file
```

## Signature elements (do not imitate)

| element | where | why it is distinctive |
| --- | --- | --- |
| mascot "Slotti" | booking page, emails | recognisable at a glance |
| blue and yellow colour pair | everywhere | brand colours |

## Inferred data model

```
Client   id, name, email, phone, allergy_notes [special category: health data], visits
         evidence: S07 client file, help article "Kundenkartei"
         confidence: high
Booking  id, client_id, stylist_id, services[], start_at, end_at, deposit_status
         evidence: S04 details form, S05 confirmation
         confidence: high
```

## Out of scope

- the marketplace of salons (their network)
- the mascot and the colour pair (signature elements)

## Size and effort

Screens 12, flows 4, entities 6.
Hard parts: two-way calendar sync, deposits through a payment provider, three locations under one account, health data in client files.
Size: M.
