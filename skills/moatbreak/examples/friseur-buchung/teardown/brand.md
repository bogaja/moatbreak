> **fiktiv / synthetic demo data**: Kammfux und Taktilo sind erfundene Namen. Markenregister wurden für dieses Beispiel nicht abgefragt; jede Registerprüfung steht deshalb auf „zu prüfen“.

# Marke: Taktilo (fiktiv)

Stand: 17.10.2026. Winkel aus `fixes.md`: A, „Sich auf den Kalender verlassen können“.

## Name

20 Kandidaten:

| Stil | Kandidaten |
| --- | --- |
| beschreibend | Salontermin, Färbezeit, Stuhlplan, Terminfest |
| zusammengesetzt | Kammwerk, Föhnzeit, Strähnplan, Scheitelzeit, Spiegeltakt, Stuhlgang |
| erfunden | Taktilo, Ondevia, Merivo, Kalvanto, Frisoly |
| Metapher | Uhrwerk, Pendel, Gezeiten |
| Verb | Einwirken, Buchdirekt |

Gestrichen, mit Grund:

- Kammwerk: teilt „Kamm“ mit Kammfux.
- Föhnzeit, Strähnplan: teilen „Föhn“ mit Föhnora und „Strähn“ mit Strähnwerk (`competitors.csv`).
- Frisoly: ein „-ly“-Zwilling, dazu nah an Frisoplan.
- Stuhlgang: unpassende Bedeutung im Deutschen.
- Salontermin, Färbezeit, Stuhlplan, Terminfest, Einwirken, Buchdirekt: rein beschreibend, als Marke schwach.
- Uhrwerk, Pendel, Gezeiten: allgemeine Wörter, als Marke schwer zu verteidigen.
- Scheitelzeit: zwei beschreibende Wortteile, lang.

Engere Wahl: **Taktilo**, Spiegeltakt, Ondevia, Merivo, Kalvanto.

Empfehlung: **Taktilo**. „Takt“ steht für einen Salontag, der nach Plan läuft, und passt zu Winkel A. Kurz, nach einmal Hören schreibbar. Eine unpassende Bedeutung ist nicht bekannt; Muttersprachler für Türkisch, Französisch und Spanisch sollen das bestätigen (zu prüfen).

## Prüfungen für Taktilo

Screening, keine Freigabe. Vor Ausgaben für den Namen sucht ein Markenanwalt richtig. Klassen: 9 (Apps), 42 (SaaS), 35 (Werbung).

| Prüfung | wo | Ergebnis |
| --- | --- | --- |
| Marken Deutschland | DPMAregister (register.dpma.de) | zu prüfen |
| Marken EU | EUIPO eSearch plus | zu prüfen |
| viele Ämter mit DE, AT, CH | TMview | zu prüfen |
| international | WIPO Global Brand Database | zu prüfen |
| Schweiz, Österreich | Swissreg, see.ip | zu prüfen |
| USA | USPTO | entfällt: kein US-Markt geplant |
| Firmennamen | Handelsregister (DE), Firmenbuch (AT), Zefix (CH) | zu prüfen |
| Designs | EUIPO DesignView | zu prüfen |
| Domains | .de über DENIC, .com, .at, .ch, .eu | zu prüfen |
| App Stores | App Store und Google Play, genauer Name | zu prüfen |
| Handles | Instagram, TikTok, LinkedIn, X, YouTube, GitHub | zu prüfen |
| Web | Websuche „Taktilo“ und „Taktilo“ mit Terminbuchung, Software, App | 17.10.2026: kein Produkt dieses Namens gefunden, nur ähnlich klingende Treffer aus der Sensorik |
| Abstand zu allen Namen in `competitors.csv` | Kammfux, Föhnora, Strähnwerk, Bürstbar, Terminkoje, ShearDock, Frisoplan, Frisierbox | verschieden: keine gemeinsame Silbe, kein ähnlicher Klang |

Die vier anderen Namen der engeren Wahl: alle Prüfungen zu prüfen.

## Farben

Die Primärfarbe kommt aus einer anderen Farbfamilie als Kammfux (Orange #f26b1d, Petrol #0e5a63): Violett.

| Rolle | Farbe | Einsatz |
| --- | --- | --- |
| text | #1d1a22 | Fließtext |
| muted | #76707e | Nebentext |
| bg | #faf8f5 | Seitenhintergrund |
| surface | #ffffff | Karten, Kalender |
| primary | #5a3d9a | Hauptbutton, Fokusring |
| on-primary | #ffffff | Text auf dem Hauptbutton |
| free | #2f7a4f | freie Zeit im Kalender (immer mit Text „frei“) |
| error | #b3261e | Fehlertext |
| border | #8b8496 | Rahmen von Eingabefeldern |

Abstand zu den Kammfux-Farben (CIE76 ΔE, wie sweep.py rechnet): am kleinsten ist muted zu Petrol mit 27,3, die Warnschwelle in `brand.json` ist 10. Die Primärfarbe liegt bei 63,5 zu Petrol und 114,1 zu Orange.

Kontrast: `contrast.md`, 8 Paare, alle erfüllen AA für ihren Zweck. Der erste Entwurf für muted war #8a8494 und fiel mit 3,41:1 auf bg durch. contrast.py schlug #76707e vor (4,51:1, 14,8 % Schwarz beigemischt). Dieser Wert steht jetzt in `brand.json`.

## Logo-Brief

- Idee: zwei kurze Balken mit einer Lücke dazwischen, wie ein Taktstrich. Die Lücke ist die Einwirkzeit, in der die Stylistin frei ist.
- Art: Bildzeichen plus Wortmarke „taktilo“ in Kleinbuchstaben.
- Muss bei 16 px (Favicon) und als App-Icon mit 1024 px funktionieren.
- Lieferung: SVG, App-Icon 1024 x 1024 ohne Transparenz für iOS, Favicon-Set, Social-Bild 1200 x 630.
- Darf Kammfux nicht ähneln: kein Tier, kein Fuchs, keine Kammform, kein Orange, kein Petrol. Entwürfe neben das Original-Logo legen und vergleichen.

## Stimme

Drei Wörter: verlässlich (nicht steif), klar (nicht knapp), ruhig (nicht langweilig). Anrede: Sie, überall.

| so | nicht so |
| --- | --- |
| „Diese Zeit wurde gerade vergeben.“ | „Ups! Da war jemand schneller.“ |
| Uhrzeit und Datum ausschreiben | „bald“, „demnächst“ |
| sagen, was als Nächstes passiert | nur „Fehler“ melden |
| ein Satz pro Gedanke | Schachtelsätze |
| Fachwörter des Salons (Einwirkzeit, Stufe) | Software-Wörter (Slot, Ressource) |

Die 10 meistgesehenen Texte, neu geschrieben:

1. Registrieren: „Salon anlegen“
2. Leerer Kalender: „Heute noch keine Termine. Freie Zeiten sehen Ihre Kundinnen und Kunden auf Ihrer Buchungsseite.“
3. Hauptbutton der Buchungsseite: „Termin buchen“
4. Bestätigung: „Ihr Termin am {Datum} um {Uhrzeit} ist gebucht. Diese Zeit ist nur für Sie reserviert.“
5. Fehler, Zeit vergeben: „Diese Zeit wurde gerade vergeben. Hier sind die nächsten freien Zeiten.“
6. Absage: „Ihr Termin ist abgesagt. Der Salon ist informiert.“
7. Erinnerung: „Morgen um {Uhrzeit}: {Leistung} bei {Mitarbeiterin}.“
8. Kündigen im Konto: „Abo kündigen“, danach „Ihr Abo endet am {Datum}. Bis dahin läuft alles weiter.“
9. Buchung mit Anzahlung: „Zahlungspflichtig buchen“ (Wortlaut nach § 312j Abs. 3 BGB vom Anwalt prüfen lassen)
10. Einwirkzeit im Kalender: „Einwirkzeit: {Mitarbeiterin} ist von {Uhrzeit} bis {Uhrzeit} frei.“

## Sweep

zu prüfen, sobald Code existiert: `python3 $SKILL/scripts/sweep.py . --config teardown/brand.json`. Dieses Beispiel enthält keinen Code.

## Abstandsprüfung

Siehe `legal.md`.
