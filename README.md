# Moatbreak

Take an existing product apart and plan a better one. Moatbreak is a Claude
skill for competitor teardowns of apps, SaaS products, websites and online
shops: it maps what the original does, ranks what its customers complain
about, measures how close a rebuild is, and gives the new product an identity
that keeps a safe distance. Built for agencies and founders working in the EU
and DACH, with English and German throughout.

## The four modes

| mode | ask for it like this | you get |
| --- | --- | --- |
| **recon** | "something like Calendly, but for hairdressers" | screens or page types, flows, data model, signature elements, feature matrix with person-day and price estimate |
| **voice of customer** | "what do customers hate about Zalando?" | ranked complaints and requests from linked public reviews, fix plan, positioning angle |
| **parity** | "how close is our rebuild to the original?" | parity score, missing list, layout diff, remaining effort and cost |
| **brand** | "we need a new name and palette before launch" | name with trademark screening, palette distance check, logo brief, voice, leftover sweep |

Each mode runs on its own or as a sequence: recon, voice of customer, the
build, parity, then brand and the legal check. Results are written to a
`teardown/` folder in your project, and each mode reads what the previous one
wrote. For client work there is an offer template and a report outline.

## Install

### claude.ai (upload)

1. Download `moatbreak.skill` from the
   [latest release](https://github.com/bogaja/moatbreak/releases/latest), or
   build it from this repository:
   `cd skills && zip -r ../moatbreak.skill moatbreak -x '*/__pycache__/*'`
2. In claude.ai, open the skills settings (Settings → Capabilities → Skills at
   the time of writing), upload the file and switch the skill on. The scripts
   need code execution to be enabled.

### Claude Code (plugin)

```
/plugin marketplace add bogaja/moatbreak
/plugin install moatbreak@moatbreak
```

### Manual copy

```bash
git clone https://github.com/bogaja/moatbreak.git
cp -r moatbreak/skills/moatbreak ~/.claude/skills/      # all your projects
cp -r moatbreak/skills/moatbreak .claude/skills/        # or one project only
```

## Example prompts

- "Build something like Calendly, but for hairdressers. Start with recon and
  an effort estimate."
- "What do customers complain about at Zalando? Here are links to Trustpilot
  and the App Store reviews."
- "Here are screenshots of the original and of our rebuild. How close are we,
  and how much work is left?"
- "We launch next month. Find a new name and palette, and check that nothing
  of the original is left in the code."
- "Angebot für einen Onlineshop wie X, mit Personentagen und Tagessatz 650 €."

## The tools

Four scripts, standard-library Python 3.8+, no installs and no network
access. They live in `skills/moatbreak/scripts/`.

| script | what it does |
| --- | --- |
| `reviews.py` | ranks review themes (pricing, bugs, UX, support, shipping, returns, checkout, ...) in English and German, keeps every quote verbatim with its link, keeps praise apart from complaints, flags thin themes and one-platform samples |
| `parity.py` | parity score weighted by must/should/could, missing list by priority, remaining effort as MVP / + should / + could in person-days and money; `--estimate-only` for offers |
| `imgdiff.py` | compares the layout of two screenshots while ignoring colour, so a rebrand does not count against parity |
| `sweep.py` | finds the original's names (with German spelling variants), domains and colours in a codebase, and warns on colours too close to theirs |

```bash
S=skills/moatbreak/scripts
python3 $S/reviews.py teardown/reviews.csv --lang de --out teardown/feedback.md
python3 $S/parity.py teardown/features.csv --estimate-only --lang de --markdown \
  --buffer 20 --overhead "QA=15,PM=10" --fixed "Setup=2-3" --day-rate 650
python3 $S/imgdiff.py original.png new.png --out diff.png
python3 $S/sweep.py . --config teardown/brand.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/moatbreak/tests
```

## Limits

- **Not legal advice.** The EU/DACH checklist (UWG imitation, Impressum,
  DSGVO, BFSG) and the trademark screening are flags for a lawyer, not a
  clearance.
- **It never invents anything.** No made-up reviews, quotes, numbers, sources
  or check results. A source it could not reach is reported as such, and a
  check nobody ran is marked "to run", never "clear".
- **It rebuilds what a product does, not what it owns.** No copied code,
  texts, images, logos or distinctive look; public sources and your own
  account only, read the way a person reads them.
- **You decide, buy and sign.** Moatbreak writes names, checklists and
  commands; you register domains and file trademarks.
- It needs a named reference product. Generic branding or market research
  without one is out of scope.

## Origin

Derived from Replica by Jake Schincariol (MIT); see [NOTICE.md](NOTICE.md).

## Licence

MIT, see [LICENSE](LICENSE). Changes and additions © 2026 Bogaja LLC
(Sheridan, Wyoming, USA), author Bogachan Önal. Release notes are in
[CHANGELOG.md](CHANGELOG.md).

## Deutsch

Moatbreak nimmt ein bestehendes Produkt auseinander (App, SaaS, Website oder
Onlineshop) und plant ein besseres. Die vier Modi:

- **recon**: Seiten oder Screens, Abläufe, Datenmodell und Feature-Matrix mit
  Aufwand in Personentagen und Preis, als Grundlage für ein Angebot
- **voice of customer**: was Kunden an öffentlichen Bewertungen am meisten
  stört, gerankt, jedes Zitat wörtlich mit Link
- **parity**: wie nah der Nachbau am Original ist, was fehlt, wie viel Arbeit
  bleibt
- **brand**: neuer Name mit Markenrecherche (DPMA, EUIPO, TMview), Farbabstand
  zum Original und Restesuche im Code

Berichte und Skripte gibt es auf Deutsch (`--lang de`). Installation wie oben
beschrieben: als `.skill`-Datei in claude.ai hochladen, als Plugin in Claude
Code oder den Ordner `skills/moatbreak` nach `~/.claude/skills/` kopieren.
Moatbreak ist keine Rechtsberatung: Die Checkliste zu UWG, Impressum, DSGVO
und BFSG zeigt, was ein Anwalt prüfen sollte. Bewertungen, Zahlen oder
Prüfergebnisse werden nie erfunden.
