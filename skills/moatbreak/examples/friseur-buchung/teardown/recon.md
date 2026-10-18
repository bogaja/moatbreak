> **fiktiv / synthetic demo data**: Kammfux ist ein erfundenes Produkt. Alle Quellen unten sind erfunden und zeigen auf example.com. Nichts hier beschreibt eine echte Firma.

# Recon: Kammfux (SaaS mit Web-App und Apps für iOS und Android)

Umfang: der Kernablauf von der Online-Buchung bis zum Termin im Salon-Kalender, dazu Leistungen, Team, Kundenkartei und Tarif. Kasse und Salon-Verzeichnis nur als Grenze.
Für: Friseursalons mit 1 bis 10 Stühlen in Deutschland, Österreich und der Schweiz (DACH)
Zweck: Bauplan und Angebot
Datum: 2026-10-03 (Quellen gelesen am 02. und 03.10.2026)

Marktüberblick: `landscape.md` und `landscape.svg`. Der Nutzer hat Kammfux am 02.10.2026 als Vorbild bestätigt.

## Quellen

| # | Quelle | URL | gelesen am | Notizen |
| --- | --- | --- | --- | --- |
| 1 | Branchenseite | https://kammfux.example.com/friseure | 2026-10-02 | Job und Zielkunde, Beleg in competitors.csv |
| 2 | Funktionsseite | https://kammfux.example.com/funktionen | 2026-10-02 | Buchungsseite, Kalender, mehrere Leistungen, Online-Zahlung, Auswertung, Kasse |
| 3 | Preisseite | https://kammfux.example.com/preise | 2026-10-02 | Tarife Basis, Plus, Premium |
| 4 | Hilfe: Registrierung | https://kammfux.example.com/hilfe/registrierung | 2026-10-02 | Salon-Konto mit E-Mail |
| 5 | Hilfe: Leistungen | https://kammfux.example.com/hilfe/leistungen | 2026-10-02 | Dauer und Preis, Preise nach Stylist-Stufe |
| 6 | Hilfe: Team | https://kammfux.example.com/hilfe/team | 2026-10-02 | Mitarbeiterinnen mit Arbeitszeiten |
| 7 | Hilfe: Benachrichtigungen | https://kammfux.example.com/hilfe/benachrichtigungen | 2026-10-02 | Bestätigung per E-Mail, Erinnerung 24 Stunden vorher |
| 8 | Hilfe: Absagen | https://kammfux.example.com/hilfe/absagen | 2026-10-02 | Termin per Link verschieben oder absagen |
| 9 | Hilfe: Kundenkartei | https://kammfux.example.com/hilfe/kundenkartei | 2026-10-02 | Terminverlauf, Notizen, Allergie-Notiz |
| 10 | Hilfe: Einwirkzeit | https://kammfux.example.com/hilfe/einwirkzeit | 2026-10-02 | Einwirkzeiten werden nicht unterstützt |
| 11 | Hilfe: Zahlungen | https://kammfux.example.com/hilfe/zahlungen | 2026-10-02 | keine Anzahlungen |
| 12 | Integrationen | https://kammfux.example.com/integrationen | 2026-10-02 | Google-Kalender |
| 13 | AGB | https://kammfux.example.com/agb | 2026-10-02 | 12 Monate Laufzeit, Kündigung schriftlich 3 Monate vor Ende |
| 14 | Salon-Verzeichnis | https://kammfux.example.com/finder | 2026-10-02 | Verzeichnis für Endkunden |
| 15 | Funktionsseite, Vorab-Prüfung | https://kammfux.example.com/funktionen | 2026-06-30 | Online-Zahlung; älter als 90 Tage, vor Verwendung neu prüfen |

Ohne Seiten-URL und daher nicht in der Tabelle: das Testkonto des Nutzers (eigener Zugang, kein öffentlicher Link), gelesen am 2026-10-03, Beleg für Telefon-Termine von Hand (S08).

Changelog-Eintrag 2026-09 (laut competitors.csv): das Produkt ist aktiv. Sichtbarkeit (Sitemap, Suche, KI-Antworten): nicht recherchiert.

## Kernablauf

Eine Kundin bucht online eine Leistung bei einer Stylistin, und der Salon sieht den Termin sofort im Kalender.

## Kernaufgaben der Nische (Achse der Positionierungskarte)

Für jede Zeile in `competitors.csv` gleich gezählt, von den öffentlichen Seiten:

1. Online-Buchung rund um die Uhr
2. mehrere Leistungen in einer Buchung
3. Einwirkzeit, in der die Stylistin frei ist
4. Preise nach Stylist-Stufe
5. Erinnerungen per E-Mail oder SMS
6. Anzahlung oder Ausfallgebühr bei No-Show
7. Kundenkartei mit Notizen
8. mehrere Standorte

Kammfux: 6 von 8 (es fehlen 3 und 6).

## Inventar

| ID | Screen | Route oder Weg | Zweck | Komponenten | Zustände gesehen |
| --- | --- | --- | --- | --- | --- |
| S01 | Buchungsseite des Salons | öffentlicher Link des Salons | Einstieg für Kundinnen | Salon-Kopf, Leistungsliste | gefüllt, mobil |
| S02 | Leistung wählen | S01 | eine oder mehrere Leistungen | Leistungskarten, Stylist-Auswahl | gefüllt, mehrere gewählt |
| S03 | Zeit wählen | S02 | freie Zeiten | Datumsleiste, Zeitraster | gefüllt, keine Zeit diese Woche |
| S04 | Kontaktdaten | S03 | Name, E-Mail, Telefon | Formular | leer, Fehler |
| S05 | Bestätigung | S04 | Termin bestätigt | Zusammenfassung | gefüllt |
| S06 | Termin absagen | Link in der Bestätigungs-E-Mail | Absage durch die Kundin | Bestätigungsdialog | gefüllt |
| S07 | Salon-Kalender | Anmeldung, Start | Tag und Woche pro Mitarbeiterin | Kalenderraster, Spalten je Mitarbeiterin | leer, gefüllt, mobil |
| S08 | Termin eintragen | S07, freie Zeit antippen | Telefon-Termin von Hand | Dialog, Kundensuche | leer, Fehler |
| S09 | Leistungen und Preise | Einstellungen | Dauer und Preis je Stufe | Tabelle, Formular | leer, gefüllt |
| S10 | Team und Arbeitszeiten | Einstellungen | Mitarbeiterinnen und Zeiten | Liste, Wochenraster | leer, gefüllt |
| S11 | Kundenkartei | Menü | Verlauf und Notizen | Liste, Detailseite | leer, gefüllt |
| S12 | Konto und Tarif | Menü | Tarif, Rechnungen | Tarifkarte | gefüllt |

## Abläufe

```
F01 Kundin bucht online
    S01 -> S02 -> S03 -> S04 -> S05
    Klicks im Normalfall: 4
    Sonderfälle: keine freie Zeit diese Woche, Zeit wird während des Ausfüllens vergeben,
                 mehrere Leistungen, Farbe mit Einwirkzeit (bei Kammfux zwei Termine)

F02 Salon trägt einen Telefon-Termin ein
    S07 -> S08
    Klicks im Normalfall: 3
    Sonderfälle: gleiche Zeit wird gleichzeitig online gebucht (Bedürfnis 1 in fixes.md)

F03 Kundin sagt ab
    E-Mail-Link -> S06
    Klicks im Normalfall: 2
    Sonderfälle: Verschieben statt Absagen

F04 Salon kündigt den Tarif
    kein Screen: laut AGB nur schriftlich, 3 Monate vor Ende der Laufzeit
```

## Komponenten

| Komponente | Varianten | Zustände | verwendet auf |
| --- | --- | --- | --- |
| Button | primär, sekundär, Text | normal, Hover, Fokus, deaktiviert, lädt | alle |
| Zeitraster | Tag, Woche | frei, belegt, gewählt | S03, S07 |
| Leistungskarte | einfach, mit Stufe | normal, gewählt | S02, S09 |
| Formularfeld | Text, E-Mail, Telefon | leer, gefüllt, Fehler | S04, S08 |
| Dialog | Bestätigung, Formular | offen | S06, S08 |

## Signature-Elemente (nicht nachahmen)

| Element | wo | warum unverwechselbar |
| --- | --- | --- |
| Fuchs-Maskottchen | Logo, leere Zustände | Bildmarke und Name gehören zusammen |
| Farbpaar Orange #f26b1d und Petrol #0e5a63 | überall | auf einen Blick Kammfux |
| Name „Kammfux Finder“ für das Verzeichnis | Startseite, S01 | Produktname des Originals |

Alle drei stehen in `features.csv` als skip und in `brand.json` unter avoid und colors.

## Abgeleitetes Datenmodell

```
Salon        name, adresse, tarif (basis | plus | premium)
             Beleg: S12, Preisseite
             Sicherheit: high
Mitarbeiterin name, stufe (z. B. Junior, Senior), arbeitszeiten
             Beleg: S10, Hilfe Team, Hilfe Leistungen
             Sicherheit: high
Leistung     name, dauer, preis je stufe
             Beleg: S09, Hilfe Leistungen
             Sicherheit: high
Kundin       name, e_mail, telefon, notizen, allergie_notiz
             Beleg: S04, S11, Hilfe Kundenkartei
             Sicherheit: high; allergie_notiz ist ein Gesundheitsdatum (Art. 9 DSGVO)
Termin       start, ende, status (bestätigt | abgesagt), mitarbeiterin, leistungen[], kundin
             Beleg: S05, S06, S07
             Sicherheit: high; Einwirkzeit gibt es beim Original nicht
Benachrichtigung art (E-Mail | SMS), zeitpunkt, termin
             Beleg: Hilfe Benachrichtigungen, Preisseite
             Sicherheit: medium
```

Beziehungen: Salon 1-n Mitarbeiterin, Salon 1-n Leistung, Kundin 1-n Termin, Termin n-m Leistung, Termin 1-n Benachrichtigung.

Personenbezogen: Kundin, Mitarbeiterin, Termin. Besondere Kategorie: allergie_notiz.

## Kommerzielles Versprechen

Preise und Tarife (netto, pro Monat und Standort): Basis ab 39 € bis 2 Mitarbeiterinnen; Plus 69 € mit SMS-Erinnerungen zu 0,09 € pro SMS; Premium 119 € mit mehreren Standorten.
Laufzeit: 12 Monate, Kündigung schriftlich 3 Monate vor Ende.
Zahlungsarten der Kundinnen: Online-Zahlung bei der Buchung (Vorab-Prüfung 30.06.2026, neu prüfen). Keine Anzahlung.

## Nischen-Delta

Was Friseure brauchen und Kammfux nicht hat: Einwirkzeit (Zeile 16) und Anzahlung gegen No-Shows (Zeile 21). Was Kammfux für Friseure schon hat: Preise nach Stylist-Stufe, mehrere Leistungen in einer Buchung, Allergie-Notiz. Was die Nische nicht braucht: das Salon-Verzeichnis für Endkunden (Netzwerk des Originals, skip).

## Feature-Matrix

Siehe `features.csv`. Muss: 11, Soll: 10, Kann: 8, davon entfällt: 3. 6 Zeilen mit original = no sind eigene Lösungen aus `fixes.md`. 1 Zeile ist unbekannt (Gutscheine).

`features-before-build.csv` ist dieselbe Matrix am Tag des Angebots, mit clone = no. Daraus stammt `estimate.md`.

## Nicht im Umfang

- Kasse mit TSE: eigenes, zertifizierungspflichtiges Produkt, besser eine Schnittstelle
- Salon-Verzeichnis für Endkunden: Netzwerk und Reichweite des Originals
- Fuchs-Maskottchen und Farbpaar: Signature-Elemente

## Größe und Aufwand

Screens 12, Flows 4, Entitäten 6.
Schwierige Teile: Kalender ohne Doppelbuchung bei gleichzeitiger Online- und Telefonbuchung, Abgleich aller Geräte, Termine mit Einwirkzeit (Lücken im Termin), Online-Zahlung und Anzahlung, Versand von E-Mail und SMS, Gesundheitsdaten in der Kundenkartei.
Größe: M (einige Wochen).
Aufwand (Personentage, aus `estimate.md`, mit 20 % Puffer, QA 15 %, PM 10 % und Pauschalen): MVP 31,2 - 66,5, + Soll 56,8 - 123,5, + Kann 66,5 - 147,5.
