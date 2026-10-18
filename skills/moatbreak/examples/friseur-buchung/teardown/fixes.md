> **fiktiv / synthetic demo data**: Kammfux ist erfunden, alle Bewertungen sind synthetisch, alle Links zeigen auf example.org. Kein Zitat stammt von einem echten Menschen.

# Kammfux (fiktiv): Bedürfnisse, Fix-Plan und Winkel

Stand: 17.10.2026. Grundlage: `feedback.md` und `feedback.json` (reviews.py, `--as-of 2026-10-17`, `--themes teardown/themes.json`).

## Stichprobe

40 Bewertungen aus 5 Quellen, alle mit Sternen und Datum, vom 25.03.2025 bis 12.10.2026. 1 Zeile ohne Link verworfen, 1 doppelte Bewertung entfernt. Das sind mehr als 30, aber weniger als die angestrebten 100: Die Rangfolge zeigt eine Richtung. Die Daten ballen sich nicht (15 von 40 aus den letzten 90 Tagen, 2 älter als 18 Monate).

- capterra: 9 Bewertungen, Ø 4,2 Sterne. Erwartet: B2B-Käufer, eventuell eingeladene zufriedene Kunden. Bestätigt: 1,3 Sterne über dem Schnitt (2,9). Die Kritik dort (Doppelbuchung, SMS-Kosten, Kündigungsfrist) steht auch in anderen Quellen.
- google-play: 9 Bewertungen, Ø 2,2 Sterne. Erwartet: Ärger direkt nach Updates. Bestätigt: 2 der 9 nennen ein Update mit Absturz; Synchronisation und Datenverlust kommen nur hier vor (dünn, eine Quelle).
- trustpilot: 8 Bewertungen, Ø 1,8 Sterne. Erwartet: Ärger über Abrechnung. Bestätigt: 1,1 Sterne unter dem Schnitt; 4 der 6 Bewertungen zu Zahlung und Kündigung stammen von hier.
- app-store: 7 Bewertungen, Ø 2,9 Sterne. Erwartet: Ärger nach Updates, kurze Urteile. Teilweise bestätigt: 1 Bewertung nennt eine neue Version; dazu kommen 2 der 3 Wünsche nach Anzahlung von hier.
- omr: 7 Bewertungen, Ø 3,3 Sterne. Erwartet: B2B-Käufer mit höheren Sternen. Nicht bestätigt: der Schnitt liegt nur 0,4 Sterne über dem Gesamtschnitt.

## Bedürfnisse

### Bedürfnis 1: Sich auf den Kalender verlassen können
Spread: über Quellen. Themen: double_booking, data, bugs, updates. Bewertungen: 11 aus 5 Quellen. Gehen: 2.
- "Zweimal in einem Monat doppelt gebucht, zwei Kundinnen standen gleichzeitig im Laden." (capterra, 2*) https://example.org/capterra/kammfux/107
- "Wieder doppelt gebucht." (trustpilot, 2*) https://example.org/trustpilot/kammfux/308
- "Kalender seit gestern leer, alle Termine verschwunden." (google-play, 1*) https://example.org/google-play/kammfux/408
Warum ein Bedürfnis: Doppelbuchung, verzögerter Abgleich und Abstürze nach Updates treffen dieselbe Aufgabe. Der Kalender muss stimmen, sonst stehen zwei Kundinnen im Laden.
Was das Original stattdessen tut: Online- und Telefonbuchungen landen im selben Kalender (recon.md, F01 und F02). Eine Sperre gegen gleichzeitige Buchungen steht auf keiner gelesenen Seite. Das ist nicht geprüft, deshalb hat features.csv Zeile 12 keine Quelle.

### Bedürfnis 2: Wissen, was es kostet, und gehen können
Spread: über Quellen, mit Schwerpunkt trustpilot (6 von 9). Themen: pricing, billing. Bewertungen: 9 aus 3 Quellen (ohne omr/205, siehe Hinweis). Gehen: 4.
- "Kündigung nur per Brief, und dann wurde trotzdem noch ein Jahr abgebucht." (trustpilot, 1*) https://example.org/trustpilot/kammfux/301
- "Leider kosten die SMS-Erinnerungen extra, das summiert sich." (capterra, 4*) https://example.org/capterra/kammfux/102
- "Die Preiserhöhung im Frühjahr kam per E-Mail, mit drei Wochen Vorlauf." (omr, 2*) https://example.org/omr/kammfux/202
Warum ein Bedürfnis: SMS-Kosten pro Nachricht, Preiserhöhung und schwere Kündigung sind dieselbe Sorge. Man weiß nicht, was es kostet, und kommt nicht heraus.
Was das Original stattdessen tut: SMS erst im Tarif Plus (69 €), 0,09 € pro SMS (features.csv Zeile 14); 12 Monate Laufzeit, Kündigung schriftlich 3 Monate vor Ende (Zeile 19).
Hinweis: Die Bewertung omr/205 zählt das Skript als Preis-Beschwerde. Sie lobt aber das Preis-Leistungs-Verhältnis und kritisiert die Statistik. Sie ist hier kein Beleg und steht deshalb nicht in den 9 Bewertungen.

### Bedürfnis 3: Die Einwirkzeit für die nächste Kundin nutzen
Spread: über Quellen. Themen: processing_time, ux. Bewertungen: 4 aus 3 Quellen. Gehen: 0.
- "Für einen Friseursalon fehlt mir die Einwirkzeit: Bei Strähnen ist die Kollegin 45 Minuten blockiert, obwohl sie in der Zeit schneiden könnte." (omr, 3*) https://example.org/omr/kammfux/201
- "Für Colorationen mit Einwirkzeit muss ich zwei Termine anlegen, das ist umständlich." (app-store, 3*) https://example.org/app-store/kammfux/507
- "Was fehlt: Einwirkzeiten beim Färben, in der Zeit könnte die Kollegin eine andere Kundin schneiden." (capterra, 4*) https://example.org/capterra/kammfux/104
Warum ein Bedürfnis: Alle drei wollen denselben Ablauf. Die Farbe wirkt ein, und die Stylistin nimmt in der Zeit die nächste Kundin.
Was das Original stattdessen tut: Laut Kammfux-Hilfe werden Einwirkzeiten nicht unterstützt (features.csv Zeile 16, geprüft am 02.10.2026). Salons legen zwei Termine an.

### Bedürfnis 4: Nicht auf Ausfällen sitzen bleiben
Spread: über Quellen, knapp an der Schwelle (3 Bewertungen, 2 Quellen). Themen: no_show. Bewertungen: 3 aus 2 Quellen. Gehen: 0.
- "Letzte Woche drei No-Shows, das sind 180 Euro Umsatz weg." (app-store, 2*) https://example.org/app-store/kammfux/501
- "Leider gibt es keine Anzahlung, No-Shows bleiben unser Risiko." (omr, 4*) https://example.org/omr/kammfux/203
- "I wish it had a deposit option for no-shows." (app-store, 3*) https://example.org/app-store/kammfux/505 [DE: Ich wünschte, es gäbe eine Anzahlung gegen No-Shows.]
Warum ein Bedürfnis: Alle drei nennen dasselbe Geld, das bei einem Ausfall fehlt, und dieselbe Lösung, eine Anzahlung.
Was das Original stattdessen tut: Laut Kammfux-Hilfe gibt es keine Anzahlungen (features.csv Zeile 21). Gelobt werden die E-Mail-Erinnerungen, die Ausfälle senken (capterra/101). Dort mithalten.

### Bedürfnis 5: Schnell Hilfe bekommen, wenn der Kalender hakt
Spread: über Quellen. Themen: support. Bewertungen: 4 aus 3 Quellen. Gehen: 2.
- "Support nicht erreichbar, drei E-Mails ohne Antwort." (trustpilot, 1*) https://example.org/trustpilot/kammfux/302
- "Der Support antwortet freundlich, aber oft erst nach zwei Tagen." (omr, 3*) https://example.org/omr/kammfux/207
- "Support antwortet nicht, und die App hängt sich auf, sobald ich eine Buchung verschiebe." (app-store, 1*) https://example.org/app-store/kammfux/504
Warum ein Bedürfnis: Alle drei warten auf Antwort, während der Salon läuft. capterra/103 lobt den Support am Telefon. Das Problem ist die Wartezeit, nicht der Ton.
Was das Original stattdessen tut: nicht recherchiert (Support-Zeiten und Kanäle nicht gelesen).

## Warum sie gehen

6 Bewertungen sagen, dass jemand gegangen ist oder gehen will. Dieselben Bewertungen kritisieren Zahlung und Kündigung (3), Doppelbuchungen (2), Preis (2) und Support (2). Genannte Ziele: Föhnora (1) und Strähnwerk (1). Das sind Einzelfälle, keine Aussage über den Markt. Beide stehen in `landscape.md` als passend.

Zu Kammfux gewechselt sind 2 Bewertungen: eine vom Terminbuch, eine von Strähnwerk wegen der Buchungsseite. Die Buchungsseite ist der Grund, warum Salons kommen. Das neue Produkt muss dort mithalten.

## Fix-Plan

Sortiert nach Beleg (Bewertungen, Quellen, Gehen) mal Aufwand. Jede Zeile steht in `features.csv` mit original = no.

| # | Änderung | Aufwand | Bedürfnis | Beleg | features.csv |
| --- | --- | --- | --- | --- | --- |
| 1 | Zeit beim Buchen sperren, kein Doppeltermin | M | 1 | 11 Bewertungen, 5 Quellen, 2 gehen | Zeile 12, Muss |
| 2 | Abo im Konto selbst kündigen, monatlich | S | 2 | 9 Bewertungen, 3 Quellen, 4 gehen | Zeile 19, Soll |
| 3 | SMS-Erinnerung im Grundpreis | M | 2 | wie 2 | Zeile 14, Soll |
| 4 | Einwirkzeit: Mitarbeiterin in der Zeit buchbar | L | 3 | 4 Bewertungen, 3 Quellen | Zeile 16, Soll |
| 5 | Abgleich aller Geräte in unter 5 Sekunden | L | 1 | wie 1 | Zeile 22, Soll |
| 6 | Anzahlung oder Ausfallgebühr bei Online-Buchung | L | 4 | 3 Bewertungen, 2 Quellen | Zeile 21, Soll |
| 7 | Rückruf-Wunsch an den Support aus dem Kalender | S | 5 | 4 Bewertungen, 3 Quellen, 2 gehen | Zeile 27, Kann |

Zeile 14 hat original = partial, weil Kammfux SMS im Tarif Plus anbietet. Für den Preis des neuen Produkts: monatlich kündbar, SMS ohne Aufpreis. Die Preisentscheidung trifft der Nutzer.

Nicht angreifen, sondern mithalten: die Buchungsseite (4-mal gelobt, Grund für Wechsel zu Kammfux), die E-Mail-Erinnerungen und die Preise nach Stylist-Stufe (features.csv Zeile 17).

## Winkel

A (empfohlen)
Für Salons mit 1 bis 10 Stühlen, die sich auf ihren Kalender verlassen wollen,
vergibt das neue Produkt jede Zeit nur einmal und hält Handy, PC und Online-Buchung in Sekunden gleich.
Beleg: Bedürfnis 1, 11 Bewertungen aus 5 Quellen, 2 davon gehen deswegen.

B
Für Salons, die wissen wollen, was die Software kostet,
ist das neue Produkt monatlich kündbar, mit SMS-Erinnerungen ohne Aufpreis.
Beleg: Bedürfnis 2, 9 Bewertungen aus 3 Quellen, 4 davon gehen. 6 der 9 stammen von trustpilot.

C
Für Salons mit vielen Farb- und Strähnenterminen,
plant das neue Produkt die Einwirkzeit ein, und die Stylistin bleibt in der Zeit buchbar.
Beleg: Bedürfnis 3, 4 Bewertungen aus 3 Quellen. Kammfux kann das laut eigener Hilfe nicht.

Empfehlung A: der breiteste Beleg, über alle 5 Quellen. B ist der stärkste Wechselgrund, aber einseitig verteilt. B und C dienen als Belege im Verkauf.

## Offene Fragen

- Gutscheine online einlösen: 1 Bewertung (google-play/409, "Von Hand lesen"). Bestätigen mit einer Interviewfrage: "Wie lösen Ihre Kundinnen heute Gutscheine ein?"
- Tagesansicht auf dem iPad: Die Zeile hatte keinen Link und wurde verworfen. Erst mit Link sammeln, dann zählen.

## Annahmen für die ersten Interviews

1. Salons mit Doppelbuchungen haben Online- und Telefonbuchung zur selben Zeit (omr/204 sagt das, die anderen nicht).
2. Salons zahlen für SMS-Erinnerungen lieber einen festen Monatspreis als pro Nachricht.
3. Salons würden eine Anzahlung verlangen, auch wenn ein Teil der Stammkundinnen das ablehnt.

## Zitatprüfung

`python3 $SKILL/scripts/reviews.py teardown/reviews.csv --verify teardown/fixes.md --lang de`: 15 verlinkte Zitate geprüft, alle stehen wörtlich in teardown/reviews.csv (17.10.2026).
