# Moatbreak

Take an existing product apart and plan a better one. Moatbreak is an agent
skill for competitor teardowns of apps, SaaS products, websites and online
shops: it finds the reference products when you only have a niche, maps
what the original does and how it is found, ranks what its customers
complain about and why they leave, prices the rebuild, writes the build
brief, measures how close the rebuild is, gives sales a sourced battle card,
gives the new product an identity that keeps a safe distance, writes its
launch pages and store texts, and hands the client one offline HTML report.
Built for agencies and founders working in the EU and DACH, with English and
German throughout.

- **Evidence rules enforced by code, not only by text.** Reviews without a
  link are dropped, `reviews.py --verify` fails any report whose quotes are
  not word for word (whole words only) in the linked review, candidate
  products without an evidence link are never proposed, every battle-card
  claim about the competitor is tagged verified, reported or assumed with
  source and date, every SEO number carries its tool and export date, and
  `sources.py` fails on a screenshot, a proof copy or a row of the recon
  sources table without its own page URL and date.
- **EU/DACH legal checklist**: UWG imitation and comparative advertising
  (§ 6 UWG), Impressum, DSGVO (including the research data itself), BFSG
  (EN 301 549 / WCAG 2.1 AA; the build brief targets WCAG 2.2 AA), as flags
  for a lawyer.
- **Effort in person-days and money**, with contingency, overheads, a day
  rate and an offer template.
- **English and German** reviews, themes and reports (`--lang de`).
- **Twelve standard-library Python scripts with 239 tests**, no installs, no
  API keys and no network access. The agent reads pages with the session's
  browser; the scripts check what it brings back.

It uses the open [Agent Skills](https://agentskills.io) format (a `SKILL.md`
plus plain Python scripts), so it installs into Claude, Codex, Cursor, Gemini
CLI, GitHub Copilot and other agents that read that format.

## The modes

| mode | ask for it like this | you get |
| --- | --- | --- |
| **discover** (step 0) | "Buchungs-App für Friseure" (a niche, no product named yet) | 3 to 5 candidate reference products, each with a public evidence link, a landscape matrix and a positioning map; you confirm which ones to tear down before recon starts |
| **recon** | "something like Calendly, but for hairdressers" | screens or page types, flows, data model, signature elements, feature matrix with person-day and price estimate |
| **visibility** (recon add-on) | "we're building something like Calendly: how is it found?" | page types and counts from its sitemap, markets and hreflang, titles and structured data of key pages, keyword themes, branded share and keyword gap from your SEO tool's export (with tool and date), local search for local businesses, Core Web Vitals, a fixed five-question sample of what AI assistants tell buyers, recorded word for word |
| **voice of customer** | "what do customers hate about Zalando?" | ranked complaints and requests from linked public reviews, a source-bias check, who says it (reviewer segment, where the platform shows it), why customers leave and where they go, the needs behind it, fix plan, positioning angle against the gap in the original's messaging |
| **build handoff** | "recon is done, write the brief for the developers" | milestones from the matrix, Given/When/Then acceptance criteria, data model and API sketch, stack questions, BFSG / EN 301 549 / WCAG 2.2 AA checklist, test plan, pre-launch gate |
| **parity** | "how close is our rebuild to the original?" | parity score, missing list, layout diff, remaining effort and cost |
| **brand** | "we need a new name and palette before launch" | name with trademark screening, palette distance and contrast check, logo brief, voice, leftover sweep |
| **battle card** | "make a battle card against Calendly for our sales team" or "write a Calendly alternative page" | one-page sales card (weaknesses with verbatim linked quotes, strengths not to attack, differentiators, objection stubs, dated prices), a SWOT where every line names its source, comparison page drafts (alternative, alternatives, vs) with who each product is best for, switching and FAQ, an audit of pages already live, and a § 6 UWG checklist for a lawyer |
| **launch** | "we go live next month: landing page, pricing page and App Store texts" | landing and pricing page copy from the angle, with the clean-room and § 6 UWG rules, design tokens from the new palette, and a store listing check against the limits and the original's names |

Each mode runs on its own or as a sequence: discover (only when no product
is named), recon with the visibility add-on, voice of customer, the build
brief and the build, parity, then brand, launch and the legal check; the
battle card once voice of customer has run. Results are written to a
`teardown/` folder in your project, and each mode reads what the previous
one wrote. For client work there is an offer template, a report outline and
`report.py`, which turns the teardown into one offline HTML page.

## Install

### Any agent (skills CLI)

```bash
npx skills add bogaja/moatbreak
```

The [skills CLI](https://github.com/vercel-labs/skills) finds the agents you
have installed (Codex, Cursor, Gemini CLI, GitHub Copilot, Claude Code and
many more) and installs the skill for each one. Add `-g` to install it for
your user instead of the current project.

### claude.ai (upload)

1. Download `moatbreak.skill` from the
   [latest release](https://github.com/bogaja/moatbreak/releases/latest), or
   build it from this repository:
   `cd skills && zip -qr ../moatbreak.skill moatbreak -x '*/__pycache__/*' -x '*.pyc' -x '*/.DS_Store'`
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
cp -r moatbreak/skills/moatbreak ~/.claude/skills/      # Claude Code, all your projects
cp -r moatbreak/skills/moatbreak .claude/skills/        # Claude Code, one project only
cp -r moatbreak/skills/moatbreak .agents/skills/        # Codex, Cursor and other agents that read .agents/skills
```

## Example prompts

- "Ich will eine Buchungs-App für Friseure bauen. Welche Produkte sollten wir
  uns als Vorbild ansehen?"
- "Build something like Calendly, but for hairdressers. Start with recon and
  an effort estimate."
- "Wir bauen etwas wie Calendly. Wie wird Calendly gefunden? Seitentypen aus
  der Sitemap, Märkte, und was ChatGPT und Perplexity Käufern empfehlen."
- "What do customers complain about at Zalando, and why do they leave? Here
  are links to Trustpilot and the App Store reviews."
- "Recon is done. Write the build brief for our developers, with acceptance
  criteria and the accessibility checklist."
- "Here are screenshots of the original and of our rebuild. How close are we,
  and how much work is left?"
- "We launch next month. Find a new name and palette, and check that nothing
  of the original is left in the code."
- "Make a battle card against Calendly for our sales team, and draft a
  Calendly alternative page we could publish."
- "Angebot für einen Onlineshop wie X, mit Personentagen und Tagessatz 650 €."
- "Unser Calendly-Nachbau geht nächsten Monat live: Landingpage, Preisseite
  und die Texte für den App Store."

## The tools

Twelve scripts, standard-library Python 3.8+, no installs and no network
access. They live in `skills/moatbreak/scripts/`.

| script | what it does |
| --- | --- |
| `landscape.py` | landscape matrix and positioning map (SVG) from a list of candidate products; rows without an evidence link are flagged and never proposed, and each market column is checked against yours (`--market DACH`) |
| `sitemap.py` | counts a competitor's public pages from a saved sitemap (page types, sections, language folders, hreflang), offline |
| `seo.py` | reads a keyword export from Semrush, Ahrefs, DataForSEO, SISTRIX, Similarweb or Search Console: keyword themes, branded share, top pages, keyword gap against your own export; every number labelled with tool, database and export date |
| `reviews.py` | ranks review themes (pricing, bugs, UX, support, shipping, returns, checkout, ...) in English and German, keeps every quote verbatim with its link, keeps praise apart from complaints, shows the sample by source with its bias (one platform over 60%, a source 1 star or more off the average, dates bunched in the last 90 days or older than `--months`) and by reviewer segment, lists why people leave with the alternative they name; `--verify` checks that every linked quote in a report stands word for word in the reviews; `--as-of` for reproducible runs |
| `parity.py` | parity score weighted by must/should/could, missing list by priority, remaining effort as MVP / + should / + could in person-days and money; `--estimate-only` for offers |
| `imgdiff.py` | compares the layout of two screenshots while ignoring colour, so a rebrand does not count against parity |
| `contrast.py` | WCAG 2.2 contrast check for colour pairs or a whole palette (AA/AAA text, large text, UI components), with the nearest passing shade or tint calculated for every failing pair |
| `sweep.py` | finds the original's names (with German spelling variants), domains and colours in a codebase, and warns on colours too close to theirs |
| `battlecard.py` | turns feedback.json and features.csv into a battle card: every claim about the competitor tagged verified, reported or assumed with source and date, a SWOT with the source of each line, and the claims fit for a public comparison page |
| `sources.py` | fails when a screenshot or proof copy in `teardown/` has no URL and date in `teardown/sources.csv`, or a row of the sources table in `teardown/recon.md` has no single page URL and date |
| `listing.py` | App Store and Google Play texts against the stores' limits, empty fields and the original's names (German spelling variants and near spellings) |
| `report.py` | the teardown as one self-contained, accessible HTML report in the client's language, with the battle card marked internal and "not researched" where a mode did not run |

```bash
S=skills/moatbreak/scripts
python3 $S/landscape.py teardown/competitors.csv --lang de --market DACH --svg teardown/landscape.svg \
  --x price_from --y axis_y --out teardown/landscape.md
python3 $S/sitemap.py teardown/visibility/sitemap.xml --lang de --out teardown/sitemap.md
python3 $S/seo.py teardown/visibility/semrush.csv --tool semrush --brand Calendly \
  --as-of 2026-10-17 --lang de --out teardown/seo.md
python3 $S/reviews.py teardown/reviews.csv --lang de --as-of 2026-10-17 --out teardown/feedback.md
python3 $S/reviews.py teardown/reviews.csv --as-of 2026-10-17 --json --out teardown/feedback.json
python3 $S/reviews.py teardown/reviews.csv --verify teardown/fixes.md
python3 $S/parity.py teardown/features.csv --estimate-only --lang de --markdown \
  --buffer 20 --overhead "QA=15,PM=10" --fixed "Setup=2-3" --day-rate 650
python3 $S/imgdiff.py original.png new.png --out diff.png
python3 $S/contrast.py --palette teardown/brand.json --lang de
python3 $S/sweep.py . --config teardown/brand.json
python3 $S/battlecard.py --feedback teardown/feedback.json --features teardown/features.csv \
  --target Calendly --ours Slotty --as-of 2026-10-17 --lang de --out teardown/battlecard.md
python3 $S/sources.py teardown --as-of 2026-10-17
python3 $S/listing.py teardown/listing.json --config teardown/brand.json
python3 $S/report.py teardown --lang de --as-of 2026-10-17 --out teardown/report.html
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/moatbreak/tests
```

## Worked example and evals

The tests check the scripts. Two folders check what the agent writes:

- [`skills/moatbreak/examples/`](skills/moatbreak/examples/): a complete,
  reproducible run for a German user (so its deliverables are German), with
  its inputs, the outputs the scripts produce from them, the HTML client
  report, and the files the agent writes (recon, fixes, build brief, brand,
  legal), so you can see what a finished teardown looks like before you
  start one.
- [`skills/moatbreak/evals/evals.json`](skills/moatbreak/evals/evals.json):
  18 test prompts with the behaviour expected of the agent, three of them
  prompts the skill must not take, for checking the skill after a change.
- [`skills/moatbreak/evals/RESULTS.md`](skills/moatbreak/evals/RESULTS.md): latest run (2026-10-18), run 3 on 1.1.1: all 18 evals, 142 of 144 assertions passed, 18 of 18 triggers correct, one run per eval plus two more runs each of evals 1 and 4, 36 of 36 (a sample, not a benchmark).

## Limits

- **Not legal advice.** The EU/DACH checklist (UWG imitation, comparative
  advertising, Impressum, DSGVO, BFSG) and the trademark screening are flags
  for a lawyer, not a clearance.
- **It never invents anything.** No made-up reviews, quotes, numbers, sources
  or check results. A source it could not reach is reported as such, and a
  check nobody ran is marked "to run", never "clear".
- **It rebuilds what a product does, not what it owns.** No copied code,
  texts, images, logos or distinctive look; public sources and your own
  account only, read the way a person reads them.
- **You decide, buy and sign.** Moatbreak writes names, checklists and
  commands; you pick the reference products, register domains and file
  trademarks.
- **Search data comes from your tools.** Moatbreak reads public files and
  samples AI answers by hand. Keyword, traffic and backlink numbers come only
  from an SEO tool connected to your agent or from your own export (which
  `seo.py` groups), with tool and date; without one they say "not
  measured".
- **Live pages come from your agent's browser.** The scripts never fetch
  anything; screenshots and proof copies are taken with the session's
  browser tools and logged with URL and date in `teardown/sources.csv`.
- **Comparison pages are drafts.** Moatbreak builds them only from verified,
  dated claims and adds a checklist for § 6 UWG and Directive 2006/114/EC. A
  lawyer checks the page before it goes live.
- **Contrast is one part of accessibility.** contrast.py checks colours; the
  rest of the WCAG 2.2 AA checklist in the build brief needs a keyboard and
  screen-reader pass by a person.
- Without a named product it starts with discover: it proposes sourced
  candidates and waits for your pick. Generic branding, market sizing in
  euros or market research without a build in view is out of scope.
- **No code.** Moatbreak writes the brief, the copy and the checks; the
  build itself is done by the build and design tools of your agent.

## Origin

Derived from Replica by Jake Schincariol (MIT); see [NOTICE.md](NOTICE.md).
The scripts, references, templates, the worked example and the evals added
in 1.1.0 are new work.

## Licence

MIT, see [LICENSE](LICENSE). Changes and additions © 2026 Bogaja LLC
(Sheridan, Wyoming, USA), author Bogachan Önal. Release notes are in
[CHANGELOG.md](CHANGELOG.md).

## Deutsch

Moatbreak nimmt ein bestehendes Produkt auseinander (App, SaaS, Website oder
Onlineshop) und plant ein besseres. Die Modi:

- **discover** (Schritt 0): wenn nur eine Nische genannt ist, 3 bis 5
  Referenzprodukte mit Beleg-Link, Marktmatrix und Positionierungskarte;
  Recon startet erst nach deiner Auswahl
- **recon**: Seiten oder Screens, Abläufe, Datenmodell und Feature-Matrix mit
  Aufwand in Personentagen und Preis, als Grundlage für ein Angebot
- **visibility** (Zusatz zu recon): wie das Original gefunden wird.
  Seitentypen aus der Sitemap, Märkte und hreflang; Suchdaten nur aus einem
  angebundenen SEO-Tool oder dessen Export (`seo.py` ordnet die Keywords),
  mit Quelle und Datum; lokale Suche für lokale Betriebe; eine feste Stichprobe von fünf
  Käuferfragen an KI-Assistenten, wörtlich und mit Datum. Ohne Tool steht
  dort „nicht gemessen“.
- **voice of customer**: was Kunden an öffentlichen Bewertungen am meisten
  stört, gerankt, jedes Zitat wörtlich mit Link. Dazu: Schieflage pro Quelle,
  warum Kunden gehen und wohin (nur genannte Alternativen), die Bedürfnisse
  dahinter, und `--verify` prüft jedes Zitat im Bericht wörtlich gegen die
  Bewertung hinter dem Link.
- **build handoff**: Bau-Briefing mit Meilensteinen, Abnahmekriterien
  (Angenommen / Wenn / Dann), Datenmodell und API-Skizze, Stack-Fragen,
  Checkliste zur Barrierefreiheit (Bauziel WCAG 2.2 AA, für das BFSG gilt
  EN 301 549 mit WCAG 2.1 AA; mit Kontrastprüfung), Testplan und Freigabe
  vor dem Launch
- **parity**: wie nah der Nachbau am Original ist, was fehlt, wie viel Arbeit
  bleibt
- **brand**: neuer Name mit Markenrecherche (DPMA, EUIPO, TMview), Farbabstand
  zum Original, Kontrast und Restesuche im Code
- **battle card**: Einseiter für den Vertrieb (Schwächen mit wörtlichem Zitat
  und Link, Stärken, eigene Vorteile, Einwände, datierte Preise), SWOT mit
  Quelle pro Zeile, Entwürfe für Vergleichsseiten (Alternative,
  Alternativen, Vergleich) mit fairer Tabelle, Wechsel-Abschnitt und FAQ,
  Prüfung bereits veröffentlichter Seiten und Checkliste zu § 6 UWG für den
  Anwalt
- **launch**: Landingpage und Preisseite aus dem Winkel, Design-Tokens aus
  der neuen Palette und eine Prüfung der Store-Texte (Zeichengrenzen, Namen
  des Originals)

Berichte und Skripte gibt es auf Deutsch (`--lang de`); `report.py` macht
aus dem Ordner `teardown/` einen HTML-Bericht für den Kunden, der offline
funktioniert. Ein Beispiel-Lauf liegt in `skills/moatbreak/examples/`, Evals
für das Ergebnis des Agenten in `skills/moatbreak/evals/`. Moatbreak nutzt das offene Agent-Skills-Format
und läuft in Claude, Codex, Cursor, Gemini CLI, GitHub Copilot und anderen
Agents. Installation wie oben beschrieben: mit
`npx skills add bogaja/moatbreak` für alle installierten Agents, als
`.skill`-Datei in claude.ai hochladen, als Plugin in Claude Code oder den
Ordner `skills/moatbreak` in den Skill-Ordner des Agents kopieren
(`~/.claude/skills/` oder `.agents/skills/`).
Moatbreak ist keine Rechtsberatung: Die Checkliste zu UWG, Impressum, DSGVO
und BFSG zeigt, was ein Anwalt prüfen sollte. Bewertungen, Zahlen oder
Prüfergebnisse werden nie erfunden.
