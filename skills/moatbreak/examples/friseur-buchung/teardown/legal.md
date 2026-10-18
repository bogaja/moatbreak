> **fiktiv / synthetic demo data**: Kammfux und Taktilo sind erfunden. Diese Datei ist eine Prüfliste für einen Anwalt, keine Rechtsberatung. Kein Punkt wurde von einem Anwalt geprüft.

# Recht: Abstandsprüfung und Pflichten zum Start (Taktilo gegen Kammfux, fiktiv)

Stand: 17.10.2026. Markt: Deutschland, Österreich, Schweiz. Grundlage: `references/legal-eu-dach.md`, Abschnitte 3 und 5. Vor dem Start prüft ein Fachanwalt für gewerblichen Rechtsschutz oder IT-Recht die Abstandsprüfung und die Startseiten.

## Abstandsprüfung

Bewertung je Zeile: gleich, ähnlich oder verschieden, mit Beleg. Eine Zeile ohne Beleg bleibt „zu prüfen“.

| Dimension | gefordert | Bewertung | Beleg |
| --- | --- | --- | --- |
| Name | verschieden | zu prüfen | `brand.md`: Websuche am 17.10.2026 ohne Treffer, Registerprüfungen noch offen |
| Logo und App-Icon | verschieden | zu prüfen | Logo-Brief in `brand.md`; Entwürfe gibt es noch nicht |
| Signature-Elemente (Fuchs, Farbpaar, „Kammfux Finder“) | verschieden, keins übernommen | zu prüfen | `features.csv` Zeilen 29 und 30 stehen auf skip; der Nachbau ist noch neben das Original zu legen |
| Primärfarbe und Farbpaar | verschieden | verschieden | Violett #5a3d9a; kleinster Abstand der Palette zu den Kammfux-Farben ΔE 27,3 (Schwelle 10), `brand.md` |
| Schrift | verschieden, falls ihre eigen ist | zu prüfen | Schrift des Originals nicht erfasst |
| Texte und Mikrotexte | verschieden | zu prüfen | 10 Texte neu geschrieben (`brand.md`); Stichprobe im fertigen Produkt fehlt |
| Bilder, Icons, Illustrationen | verschieden | zu prüfen | Lizenzliste im Projekt fehlt noch |
| Gesamteindruck der Hauptscreens | ähnlich nur, wenn alle Zeilen oben verschieden sind | zu prüfen | imgdiff.py braucht Screenshots beider Produkte (`parity.md` enthält keinen Layout-Vergleich) |
| Domain, Handles, Store-Eintrag | verschieden | zu prüfen | Domains und Handles in `brand.md` noch offen; kein „Kammfux“ im App-Namen |
| Herkunft des Wissens | nur öffentlich oder eigenes Konto | öffentlich und eigenes Konto | Quellentabelle in `recon.md`: öffentliche Seiten und das Testkonto des Nutzers |

Ergebnis: nicht startbereit. 8 Zeilen sind noch zu prüfen.

## Pflichten zum Start

Taktilo verkauft an Salons (B2B). Die Buchungsseite benutzen aber Verbraucherinnen und Verbraucher. Welche Pflicht beim Salon liegt und welche bei Taktilo, klärt der Anwalt.

- [ ] zu prüfen: Impressum auf Website und Buchungsseite (§ 5 DDG; Österreich § 5 ECG und § 25 MedienG; Schweiz Art. 3 Abs. 1 lit. s UWG).
- [ ] zu prüfen: Datenschutzerklärung (Art. 13 DSGVO) und Auftragsverarbeitungsvertrag mit jedem Salon (Art. 28), dazu Verträge mit Hosting, E-Mail- und SMS-Versand.
- [ ] zu prüfen: Allergie-Notiz ist ein Gesundheitsdatum (Art. 9 DSGVO): ausdrückliche Einwilligung, enge Zugriffsrechte, Datenschutz-Folgenabschätzung erwägen (`features.csv` Zeile 18).
- [ ] zu prüfen: Erinnerungen an gebuchte Termine sind Transaktionsnachrichten; Werbung per E-Mail oder SMS braucht die vorherige ausdrückliche Einwilligung (§ 7 Abs. 2 UWG), in der Praxis per Double-Opt-in nachgewiesen.
- [ ] zu prüfen: Cookies und Tracking nur nach Einwilligung (§ 25 TDDDG), oder Analyse ohne Cookies.
- [ ] zu prüfen: Barrierefreiheit: Gilt das BFSG für die Buchungsseite? Kleinstunternehmen sind für Dienstleistungen ausgenommen. Gebaut wird ohnehin nach WCAG 2.2 AA (`build-brief.md`). Informationen zur Barrierefreiheit nach § 14 BFSG mit Anlage 3 (wie die Dienstleistung die Anforderungen erfüllt), in den AGB oder auf einer Seite; eine nicht erfüllte Anforderung ist nur unter den Ausnahmen des Gesetzes zulässig (grundlegende Veränderung, unverhältnismäßige Belastung), mit dokumentierter Beurteilung. Den Inhalt bestätigt der Anwalt.
- [ ] zu prüfen: Buchung mit Anzahlung: Button-Text „Zahlungspflichtig buchen“ (§ 312j Abs. 3 BGB) und Informationen vor dem Vertrag (Art. 246a EGBGB).
- [ ] zu prüfen: Ausfallgebühren für No-Shows: vorher klar vereinbart, angemessen zum tatsächlichen Schaden, Nachweis eines geringeren Schadens möglich (§ 309 Nr. 5 BGB). Die Vorlage für die AGB der Salons gehört dazu.
- [ ] zu prüfen: Preise auf der Buchungsseite als Endpreise inkl. Umsatzsteuer (PAngV).
- [ ] zu prüfen: Kündigungsbutton (§ 312k BGB) gilt für Verbraucherverträge. Für Salons ist er keine Pflicht, aber Teil des Winkels (`features.csv` Zeile 19).
- [ ] zu prüfen: E-Rechnung: Taktilo muss E-Rechnungen empfangen können; die Pflicht zum Versenden an Salons beginnt stufenweise ab 2027.
- [ ] zu prüfen: Schweiz: revidiertes Datenschutzgesetz (revDSG), falls Salons in der Schweiz Kunden werden.

## Werbung gegen Kammfux

Eine Vergleichsseite ist nicht beauftragt. `battlecard.md` ist intern. Bevor etwas mit dem Namen Kammfux nach außen geht (Vergleichsseite, Präsentation, Anzeige), gilt die Checkliste in `references/battlecard.md` (§ 6 UWG), Punkt für Punkt vom Anwalt geprüft.

## Entscheidung des Nutzers

Ob ein Anwalt die Abstandsprüfung und die Startseiten prüft: noch nicht entschieden (zu prüfen).
