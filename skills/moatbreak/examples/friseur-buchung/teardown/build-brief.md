> **fiktiv / synthetic demo data**: Kammfux und Taktilo sind erfunden, ebenso der Nachbau und sein Stand. Werte in den Kriterien sind Testdaten.

# Build-Brief: Taktilo (aus der Analyse von Kammfux, fiktiv)

Für: den Nutzer (Agentur, Kunde: Friseursalons mit 1 bis 10 Stühlen in DACH)
Datum: 2026-10-17
Eingaben: recon.md (2026-10-03), features.csv (29 Zeilen), fixes.md (2026-10-17), brand.md (2026-10-17)

## Ziel

Eine Kundin bucht online eine Leistung bei einer Stylistin, und der Salon sieht den Termin sofort im Kalender, ohne Doppeltermin.
Besser als das Original wegen: Winkel A aus `fixes.md`, Bedürfnis 1 (11 Bewertungen aus 5 Quellen); dazu Einwirkzeit (Bedürfnis 3) und monatliche Kündigung mit SMS ohne Aufpreis (Bedürfnis 2).

## Meilensteine

| Meilenstein | Features (Zeilen in features.csv) | Personentage, kumuliert | endet mit (Demo) |
| --- | --- | --- | --- |
| M1 MVP | Muss: Zeilen 2 bis 12 | 31,2 - 66,5 | F01 und F02 von Anfang bis Ende auf Handy und Desktop, ohne Doppeltermin |
| M2 + Soll | Soll: Zeilen 13 bis 22 | 56,8 - 123,5 | Erinnerungen, Einwirkzeit, Stufen, Kündigen im Konto, Online-Zahlung mit Anzahlung |
| M3 + Kann | Kann: Zeilen 23 bis 27 | 66,5 - 147,5 | Google-Kalender, mehrere Standorte, Auswertung, Gutscheine, Rückruf |

Personentage aus `estimate.md`: 20 % Puffer auf die Feature-Arbeit, QA 15 %, PM 10 %, Pauschalen für Workshop, Setup, Design und Go-live in jeder Zeile enthalten.
Bau-Reihenfolge in M1: Datenmodell und Anmeldung (Zeile 2), Leistungen (3), Team (4), Kalender mit Sperre (9, 12, 10), Buchungsseite und Gastbuchung für F01 (5, 6), Bestätigung (7), Absagen (8), Kundenkartei (11).

Frage an den Nutzer: Zeile 22 (Abgleich aller Geräte in unter 5 Sekunden) trägt Winkel A und ist Soll. Kommt sie in M1? Antwort: offen. Erst die Priorität in `features.csv` ändern, dann diesen Brief.

Stand am 17.10.2026 (`parity.md`): 10 von 11 Muss-Zeilen fertig, Zeile 8 teilweise (Verschieben fehlt). M1 ist nicht abgeschlossen.

## Akzeptanzkriterien (Muss-Features)

### Salon-Konto mit E-Mail anlegen (onboarding, S12, Zeile 2)

```
Angenommen niemand ist angemeldet
Wenn eine Inhaberin „Salon anlegen“ wählt und Salonname, E-Mail und ein Passwort mit 12 Zeichen eingibt
Dann erhält sie innerhalb von 2 Minuten eine E-Mail mit Bestätigungslink
  und sieht nach dem Klick den leeren Kalender (S07) mit „Heute noch keine Termine.“

Angenommen die E-Mail-Adresse hat schon ein Konto
Wenn sie sich damit noch einmal registriert
Dann steht neben dem Feld, dass es schon ein Konto gibt, mit einem Link zur Anmeldung
  und es entsteht kein zweites Konto
```

### Leistungen mit Dauer und Preis anlegen (leistungen, S09, Zeile 3)

```
Angenommen ein Salon ohne Leistungen
Wenn die Inhaberin „Damenhaarschnitt“ mit 45 Minuten und 48,00 € speichert
Dann zeigt die Buchungsseite (S01) „Damenhaarschnitt, 45 Min., 48,00 €“ als Endpreis inkl. USt.

Angenommen das Feld Dauer ist leer
Wenn sie speichert
Dann steht neben dem Feld, dass die Dauer in Minuten fehlt, und nichts wird gespeichert
```

### Mitarbeiterinnen mit Arbeitszeiten (team, S10, Zeile 4)

```
Angenommen Mitarbeiterin A arbeitet dienstags bis samstags von 09:00 bis 18:00
Wenn eine Kundin Montag, den 09.11.2026, in S03 öffnet
Dann zeigt S03 für A keine freie Zeit

Angenommen A trägt Urlaub vom 03.11. bis 07.11.2026 ein und hat am 04.11. einen Termin
Wenn die Inhaberin speichert
Dann zeigt S10 den Termin am 04.11. als Konflikt, und S03 zeigt für A in der Zeit keine Zeiten
```

### Öffentliche Buchungsseite mit freien Zeiten (buchungsseite, S01 bis S03, F01, Zeile 5)

```
Angenommen A ist am Dienstag, 10.11.2026, von 09:00 bis 18:00 frei, und „Damenhaarschnitt“ dauert 45 Minuten
Wenn eine Kundin S03 für diesen Tag öffnet
Dann sieht sie freie Zeiten von 09:00 bis 17:15 im Abstand von 15 Minuten
  innerhalb von 2 Sekunden auf einem Mittelklasse-Handy über 4G

Angenommen in dieser Woche ist keine Zeit frei
Wenn sie S03 öffnet
Dann sieht sie „In dieser Woche ist keine Zeit frei“ und einen Button zur nächsten Woche mit freier Zeit
```

### Termin als Gast ohne Konto buchen (buchungsseite, S04 und S05, F01, Zeile 6)

```
Angenommen eine Kundin hat Dienstag, 10.11.2026, 10:00 bei A gewählt
Wenn sie Name, E-Mail und Telefon eingibt und „Termin buchen“ wählt
Dann sieht sie S05 mit Datum, Uhrzeit, Leistung und Mitarbeiterin, ohne ein Konto anzulegen

Angenommen sie gibt „anna@“ als E-Mail ein
Wenn sie bucht
Dann steht neben dem Feld, was fehlt, ihre Eingaben bleiben erhalten, und kein Termin wird gespeichert
```

### Bestätigung per E-Mail an Kundin und Salon (benachrichtigungen, Zeile 7)

```
Angenommen eine Buchung für Dienstag, 10.11.2026, 10:00 ist gespeichert
Wenn S05 erscheint
Dann erhält die Kundin innerhalb von 2 Minuten eine E-Mail mit Termin, Adresse und Absage-Link
  und der Salon eine E-Mail mit Kundin, Leistung und Mitarbeiterin

Angenommen der E-Mail-Dienst antwortet nicht
Wenn die Buchung gespeichert wird
Dann bleibt der Termin gespeichert, der Versand wird 24 Stunden lang wiederholt
  und S07 markiert den Termin mit „Bestätigung nicht zugestellt“
```

### Termin per Link verschieben oder absagen (buchungsseite, S06, F03, Zeile 8)

```
Angenommen eine Kundin hat einen Termin am Dienstag, 10.11.2026, 10:00
Wenn sie am Montag den Link aus der E-Mail öffnet und „Termin absagen“ wählt
Dann ist 10:00 bei A wieder frei, und beide Seiten erhalten eine E-Mail

Angenommen sie wählt „Verschieben“ und Donnerstag, 12.11.2026, 11:00
Wenn sie bestätigt
Dann ist der neue Termin gebucht und der alte frei, in einem Schritt
  und zu keinem Zeitpunkt sind beide Termine gespeichert
```

Stand 17.10.2026: Absagen erfüllt, Verschieben fehlt (`parity.md`).

### Salon-Kalender Tag und Woche pro Mitarbeiterin (kalender, S07, Zeile 9)

```
Angenommen drei Mitarbeiterinnen haben am 10.11.2026 zusammen 14 Termine
Wenn die Inhaberin die Tagesansicht auf einem Handy mit 390 px Breite öffnet
Dann sieht sie eine Spalte je Mitarbeiterin mit allen 14 Terminen
  und die Seite scrollt nicht waagerecht (die Spalten lassen sich wischen)

Angenommen am Tag gibt es keine Termine
Wenn sie die Tagesansicht öffnet
Dann steht „Heute noch keine Termine. Freie Zeiten sehen Ihre Kundinnen und Kunden auf Ihrer Buchungsseite.“
```

### Telefon-Termine von Hand eintragen (kalender, S08, F02, Zeile 10)

```
Angenommen 14:00 bei A ist frei
Wenn die Inhaberin 14:00 antippt, „Damenhaarschnitt“ und eine Kundin aus der Kartei wählt und speichert
Dann steht der Termin in S07, und S03 zeigt 14:00 bei A nicht mehr als frei

Angenommen 14:00 bei A ist schon vergeben
Wenn sie 14:00 antippt
Dann zeigt S08 „Diese Zeit wurde gerade vergeben. Hier sind die nächsten freien Zeiten.“
```

### Kundenkartei mit Terminverlauf (kunden, S11, Zeile 11)

```
Angenommen Kundin K hatte drei Termine
Wenn die Inhaberin K in S11 öffnet
Dann sieht sie die drei Termine mit Datum, Leistung und Mitarbeiterin, den neuesten zuerst

Angenommen die Kartei ist leer
Wenn sie S11 öffnet
Dann steht dort, dass Kundinnen und Kunden mit der ersten Buchung entstehen
```

### Zeit beim Buchen sperren, kein Doppeltermin (kalender, F01 und F02, Zeile 12)

Beweist, dass die Beschwerde aus Bedürfnis 1 in `fixes.md` weg ist.

```
Angenommen eine Kundin hat S04 für Dienstag, 10.11.2026, 10:00 bei A offen
Wenn die Inhaberin in diesem Moment 10:00 bei A als Telefon-Termin speichert und die Kundin danach bucht
Dann sieht die Kundin „Diese Zeit wurde gerade vergeben. Hier sind die nächsten freien Zeiten.“
  und für 10:00 bei A ist genau ein Termin gespeichert

Angenommen 50 Buchungen auf dieselbe Zeit kommen gleichzeitig an (Lasttest)
Wenn alle verarbeitet sind
Dann ist genau ein Termin gespeichert, und 49 erhalten die Meldung mit den nächsten Zeiten
```

### Pflichten aus `legal.md` als Kriterien

```
Angenommen eine Kundin öffnet S01 bis S05
Wenn sie nach unten scrollt
Dann findet sie auf jeder Seite Links zu Impressum und Datenschutz des Salons und von Taktilo

Angenommen eine Kundin öffnet S01 zum ersten Mal
Wenn die Seite geladen ist
Dann wurde nichts gespeichert oder gelesen, das eine Einwilligung braucht, bevor sie zugestimmt hat
```

## Datenmodell

```
Salon         id (uuid, Pflicht), name (text, Pflicht), adresse (text, Pflicht), tarif (text, Pflicht)
              Beziehungen: 1-n Mitarbeiterin, 1-n Leistung, 1-n Kundin
              Sicherheit: hoch
Mitarbeiterin id, salon_id -> Salon, name (text, Pflicht) [personenbezogen], stufe (text, optional),
              arbeitszeiten (json, Pflicht)
              Sicherheit: hoch
Leistung      id, salon_id -> Salon, name (text, Pflicht), dauer_min (int, Pflicht),
              preis_cent je stufe (json, Pflicht), einwirkzeit_min (int, optional, ab M2)
              Sicherheit: hoch; einwirkzeit_min ist neu (Zeile 16)
Kundin        id, salon_id -> Salon, name (text, Pflicht) [personenbezogen], e_mail (text, Pflicht) [personenbezogen],
              telefon (text, optional) [personenbezogen], notizen (text, optional) [personenbezogen],
              allergie_notiz (text, optional, ab M2) [besondere Kategorie], einwilligung_allergie_am (Zeitstempel)
              Sicherheit: hoch
Termin        id, salon_id, mitarbeiterin_id, kundin_id, start (UTC, Pflicht), ende (UTC, Pflicht),
              status (bestätigt | abgesagt), leistungen (n-m Leistung), quelle (online | telefon)
              Regel: keine zwei bestätigten Termine einer Mitarbeiterin überlappen (Zeile 12, in der Datenbank erzwungen)
              Sicherheit: hoch
Benachrichtigung id, termin_id, art (e_mail | sms), geplant_für, zugestellt_am
              Sicherheit: mittel (zu bestätigen)
```

Personenbezogen: Mitarbeiterin.name; Kundin.name, e_mail, telefon, notizen; Termin über die Kundin.
Besondere Kategorien (Art. 9 DSGVO): Kundin.allergie_notiz, nur mit ausdrücklicher Einwilligung, sichtbar nur für Inhaberin und die Mitarbeiterin des Termins.

## API-Skizze (Muss-Abläufe)

| Operation | wer darf | Ablauf | verlässt das System |
| --- | --- | --- | --- |
| GET /salons/{slug}/leistungen | Gast, ohne Anmeldung | F01 | - |
| GET /salons/{slug}/zeiten?leistung=&datum= | Gast, ohne Anmeldung | F01 | - |
| POST /salons/{slug}/termine | Gast, ohne Anmeldung | F01 | E-Mail an Kundin und Salon |
| POST /termine | Salon, angemeldet | F02 | - |
| DELETE /termine/{id}?token= | Gast über signierten Link | F03 | E-Mail an beide Seiten |
| GET /kalender?tag= | Salon, angemeldet | F02 | - |

## Stack

| Frage | Antwort | entschieden von, Datum (oder „Annahme“) |
| --- | --- | --- |
| Team und was es schon betreibt | offen | Frage an den Nutzer |
| Web, PWA oder nativ; welche Stores | Vorschlag: installierbare Web-App (PWA), keine nativen Apps in M1 | Annahme |
| Hosting-Region | Vorschlag: EU | Annahme |
| Plattform oder eigene Entwicklung | eigene Entwicklung (Kalenderlogik ist der Kern) | Annahme |
| Anmeldung | Vorschlag: E-Mail und Passwort, Einfügen und Passwortmanager erlaubt | Annahme |
| Zahlungsanbieter und Zahlungsarten | offen, erst für M2 | Frage an den Nutzer |
| E-Mail- und SMS-Anbieter | offen, Anbieter mit Sitz oder Servern in der EU bevorzugt | Frage an den Nutzer |
| Schnittstellen | Google-Kalender in M3 | features.csv Zeile 23 |
| Sprachen und Märkte zum Start | Deutsch, DACH | recon.md |
| ein Kunde oder viele | viele Salons (mandantenfähig) | recon.md |
| Betrieb und monatliche Kosten | offen | Frage an den Nutzer |
| Kleinstunternehmen (BFSG) | offen | Frage an den Nutzer |

## Barrierefreiheit (Bauziel WCAG 2.2 AA; Bezug für das BFSG: EN 301 549, die auf WCAG 2.1 AA verweist)

| Punkt | Kriterium | Status | getestet auf, Datum |
| --- | --- | --- | --- |
| Kontrast: `contrast.py` endet mit 0, Zustände eingeschlossen | 1.4.3, 1.4.11 | erfüllt für 8 Paare der Palette; Hover, Fokus und Fehlerzustände zu prüfen | `contrast.md`, 17.10.2026 |
| Farbe nie das einzige Signal (freie Zeit hat den Text „frei“) | 1.4.1 | zu prüfen | |
| nur Tastatur, sinnvolle Reihenfolge, keine Falle | 2.1.1, 2.1.2, 2.4.3 | zu prüfen | |
| Fokus sichtbar und nicht verdeckt | 2.4.7, 2.4.11 | zu prüfen | |
| Sprunglink oder Landmarken | 2.4.1 | zu prüfen | |
| Ziele mindestens 24 x 24 px (Zeitraster) | 2.5.8 | zu prüfen | |
| kein Ziehen nötig (Termine verschieben im Kalender) | 2.5.7 | zu prüfen | |
| Beschriftungen und Fehlermeldungen | 1.3.1, 3.3.1, 3.3.2, 3.3.3 | zu prüfen | |
| autocomplete, keine doppelte Eingabe | 1.3.5, 3.3.7 | zu prüfen | |
| Anmeldung ohne Rätsel, Einfügen geht | 3.3.8 | zu prüfen | |
| Hilfe immer am selben Ort | 3.2.6 | zu prüfen | |
| Zeitlimits verlängerbar (gehaltene Zeit in S04) | 2.2.1 | zu prüfen | |
| echte Überschriften und Listen, Sprache gesetzt | 1.3.1, 3.1.1 | zu prüfen | |
| Alternativtext, Namen für Icon-Buttons | 1.1.1, 4.1.2 | zu prüfen | |
| Statusmeldungen werden vorgelesen („Termin gebucht“) | 4.1.3 | zu prüfen | |
| 320 px Umbruch, 200 % Zoom, Textabstände | 1.4.10, 1.4.4, 1.4.12 | zu prüfen | |
| Bewegung pausierbar, kein Blinken | 2.2.2, 2.3.1 | zu prüfen | |
| Untertitel und Transkripte | 1.2.2, 1.2.1 | entfällt: keine Videos geplant | |
| automatischer Scan in CI | - | zu prüfen | |
| Tastatur und Screenreader durch F01 bis F03 | - | zu prüfen | |
| Informationen zur Barrierefreiheit (§ 14 BFSG mit Anlage 3), in den AGB oder auf einer Seite; Inhalt bestätigt der Anwalt | BFSG | zu prüfen | |

## Testplan

| Ebene | was | wie | wann |
| --- | --- | --- | --- |
| Abnahme | die Kriterien oben | End-to-End-Tests für F01, F02 und F03; der Rest von Hand nach diesem Brief | jeder Meilenstein |
| Regeln | Preise in Cent, USt., Zeitzone Europe/Berlin, Arbeitszeiten, Überlappung | Unit-Tests mit festen Daten (10.11.2026) und Beträgen | mit dem Code |
| Sonderfälle | keine freie Zeit, Zeit während des Ausfüllens vergeben, Versand fällt aus | in den End-to-End-Tests | jeder Meilenstein |
| Recht | Impressum und Datenschutz auf jeder Seite, Einwilligung vor Tracking, ab M2 Button „Zahlungspflichtig buchen“ und Kündigen im Konto | von Hand | M1 und vor dem Start |
| Barrierefreiheit | Liste oben | contrast.py, Scan, Tastatur, Screenreader | jeder Meilenstein |
| Geräte | 1440 x 900, 390 x 844, ein echtes Handy | Screenshots nach `teardown/new-screens/` | jeder Meilenstein |
| Leistung | S01 und S03 mobil | öffentlicher PageSpeed-Lauf, mit dem Original verglichen | vor dem Start |
| Testdaten | alles | frisch geschriebene Testdaten; nie Daten des Originals, nie echte Kundendaten | immer |

Nimmt jeden Meilenstein ab: der Nutzer.
Blockiert einen Meilenstein: ein offener kritischer Fehler, ein Muss-Kriterium, das scheitert, ein Doppeltermin im Lasttest.

## Prüfung vor dem Start

Stand nach M1 und dem Markenmodus. Beim ersten Schreiben des Briefs stand jede Zeile auf „zu prüfen“; eine Zeile ändert sich erst, wenn die Prüfung am gebauten Produkt läuft.

| Prüfung | Beleg | Status | Datum |
| --- | --- | --- | --- |
| Parität auslieferbar | `teardown/parity.md` | nicht erfüllt: 82,6, ein Muss-Feature teilweise (Zeile 8) | 17.10.2026 |
| jedes Muss-Kriterium abgehakt | dieser Brief | nicht erfüllt: Verschieben fehlt | 17.10.2026 |
| kein hoher Layout-Wert auf einem Signature-Screen | `teardown/diffs/` | zu prüfen | |
| Markenprüfungen gelaufen und datiert | `teardown/brand.md` | zu prüfen: Register offen | |
| Kontrast endet mit 0 | `teardown/contrast.md` | erfüllt | 17.10.2026 |
| Sweep endet mit 0, nahe Farben angesehen | sweep.py | zu prüfen: es gibt noch keinen Code | |
| Abstandsprüfung: alle geforderten Zeilen verschieden | `teardown/legal.md` | zu prüfen: 8 Zeilen offen | |
| Pflichten zum Start abgehakt | `teardown/legal.md` | zu prüfen | |
| Barrierefreiheit abgehakt | dieser Brief | zu prüfen | |
| Anwaltsprüfung entschieden | Entscheidung des Nutzers | zu prüfen | |

Start, wenn jede Zeile erfüllt ist. Der Nutzer entscheidet und startet.

## Offene Fragen

- Kommt Zeile 22 (Abgleich in unter 5 Sekunden) in M1? Der Nutzer, vor dem Ende von M1.
- Zahlungsanbieter für Online-Zahlung und Anzahlung (Zeilen 20 und 21)? Der Nutzer, vor dem Start von M2.
- Gilt das BFSG für den Betreiber von Taktilo (Kleinstunternehmen)? Der Nutzer mit seinem Anwalt.
