# Brand mode

Nothing launches under the original's identity, and nothing launches so
close to it that customers could mix them up. This mode is the line between
"a copy" and "your product".

Output: `teardown/brand.md` (name with checks, palette, logo brief, voice),
`teardown/brand.json` (from `$SKILL/templates/brand.json`), updated design tokens, rewritten strings, a clean
contrast check (`teardown/contrast.md`), a clean sweep.

Read `references/legal-eu-dach.md` first if the product will be sold in the
EU or Switzerland.

## Step 1: the name

Read the angle from `teardown/fixes.md`. Generate 20 candidates across
styles: descriptive (Booklink), compound (Slotwise), invented (Calvo),
metaphor (Harbor), verb (Book). Cut to 5 with these filters:

- **Not confusingly similar to the original** in sound, look or meaning, nor
  to any other product in the same category. That is the test trademark
  offices and courts use, so it is the test here. No puns on their name, no
  "-ly" twin, no shared distinctive syllable. If discover ran, screen
  against every name in `teardown/competitors.csv`, not only the original;
  if visibility ran, also against the brands named in its AI-answer and
  search samples.
- Short, spellable after hearing it once, no awkward meaning in German,
  English, Turkish, French, Spanish or the target market's languages.
- Says something about the angle, or at least does not fight it.
- Purely descriptive names ("Online Booking") are weak trademarks and hard
  to defend; prefer something distinctive.

## Step 2: the checks, run, not assumed

For each of the 5, a row per check. Mark each **to run**, or the result with
the date it was run. Never write "available" or "clear" for a check nobody
ran.

| check | where |
| --- | --- |
| Germany trademarks | DPMAregister, register.dpma.de |
| EU trademarks | EUIPO eSearch plus, euipo.europa.eu/eSearch |
| many offices at once (incl. DE, AT, CH) | TMview, tmdn.org/tmview |
| international | WIPO Global Brand Database, branddb.wipo.int |
| Switzerland, Austria | Swissreg (swissreg.ch), see.ip (see.ip.gv.at) |
| US | USPTO trademark search, tmsearch.uspto.gov |
| company names | Handelsregister / Unternehmensregister (DE), Firmenbuch (AT), Zefix (CH) |
| registered designs (logo, icons, UI) | EUIPO DesignView |
| domains | .de via DENIC whois, .com via any registrar, plus .at/.ch/.eu as needed |
| app stores | search the exact name in App Store and Google Play |
| handles | Instagram, TikTok, LinkedIn, X, YouTube, GitHub |
| the web | search "name + category" |

Classes to search: 9 (apps and downloadable software), 42 (SaaS), 35
(online retail, advertising), plus the goods class for a shop (for example
25 for clothing). In Germany, company names and work titles (an app's name
can be a work title) are protected without registration, so the company
register and the app stores are real checks, not formalities.

These are screening checks, not clearance. Before money is spent on the
name, a trademark lawyer should run a proper search.

## Step 3: palette

A new palette in the same token roles the design system uses. Pick the
primary brand hue from a different family than the original's (if theirs is
blue, yours is not a nearby blue). Put the original's brand colours into
`teardown/brand.json`; sweep.py warns on any colour within Delta E 10 of
them, which reads as "the same colour" at a glance.

Then check contrast with the script, not by eye. Add the new palette to
`teardown/brand.json` as `palette` (token role to colour) and the
combinations the design uses as `pairs`, with `ui` as a third element for
borders, focus rings and icons:

```json
"palette": {"text": "#1c1917", "muted": "#57534e", "bg": "#ffffff",
            "primary": "#c2410c", "on-primary": "#ffffff"},
"pairs": [["text", "bg"], ["muted", "bg"], ["on-primary", "primary"],
          ["primary", "bg", "ui"]]
```

```bash
python3 $SKILL/scripts/contrast.py --palette teardown/brand.json --lang de --markdown --out teardown/contrast.md
```

Text needs 4.5:1, large text (24px, or about 18.7px bold) and UI components
3:1 (WCAG 2.2 AA, the bar to build to for the German BFSG). For every
failing pair the report gives the nearest darker and lighter variant of the
first colour that passes; put one of them into `palette` and the tokens
exactly as printed, and run again until it exits 0. Never swap in a shade
picked by eye instead, even one that passes: the printed variant is the
closest to the draft that passes, and anything else is a guess. Write the
change into `teardown/brand.md` (as in the example: muted #8a8494 failed at
3,41:1, contrast.py gave #76707e at 4,51:1). The different hue family is
for the brand colours (primary, accent); neutral roles such as text, muted
and border stay neutral and keep the computed fix when the primary changes.
To keep a label colour and change the brand colour behind it, list the
brand colour first. sweep.py ignores these two keys, and with `palette`
present contrast.py does not read the original's `colors`.

**Design tokens.** Once contrast.py exits 0, map the palette to the token
roles the build uses, so nobody picks colours by eye later. One role, one
palette key; every pair a role needs is in `pairs`:

| token role | palette key | used for | checked as |
| --- | --- | --- | --- |
| `color-text` | text | body text | text on bg and on surface |
| `color-text-muted` | muted | secondary text, placeholders that carry information | text on bg |
| `color-bg`, `color-surface` | bg, surface | page and cards | - |
| `color-border` | border | input and card boundaries | ui on bg |
| `color-primary`, `color-on-primary` | primary, on-primary | main buttons and links | text: on-primary on primary; ui: primary on bg |
| `color-focus` | focus | focus ring | ui on bg and on primary |
| `color-error`, `color-success`, `color-warning` | error, success, warning | messages, always with text or an icon too | text on bg |

Write the map into `teardown/brand.md` and hand it to the build as CSS
custom properties or the design tool's token file, under the new product's
names. The original's token names, if they ever showed, are theirs: never
reuse them.

## Step 4: logo brief

Not a logo, a brief for whoever makes it (the user, a designer, an image
model):

- the idea in one line, tied to the name and angle
- mark type: wordmark, symbol plus wordmark, or monogram
- works at 16px (favicon) and as a 1024px app icon
- deliverables: SVG, app icon 1024x1024 without transparency for iOS,
  favicon set, social image 1200x630
- **must not resemble the original's mark**: no shared shape, colour pair or
  letterform trick. Put the original's logo next to the drafts and compare.

## Step 5: voice

Three words for how it sounds, with what each does not mean ("direct, not
blunt"). Five do and don't pairs. For German, decide du or Sie up front,
with a one-line reason from the customers (business owners and older
customers: usually Sie; a young consumer audience: often du), and keep it
everywhere. Then write out in `teardown/brand.md` the 10 most-seen strings
in that voice (sign up, empty states, the main button, the confirmation,
the error, the checkout or booking button). A button that starts a payment,
a deposit included, must name it, like "zahlungspflichtig bestellen" or
"zahlungspflichtig buchen" (§ 312j (3) BGB). All fresh, none echoing the
original's phrasing. If there is no angle yet (no `fixes.md`), still write
the voice and the strings as a proposal for the user to confirm, and mark
the lines to revisit once the angle exists; do not leave the section open.

## Step 6: the sweep

Replace every placeholder name, colour and string. Then:

```bash
python3 $SKILL/scripts/sweep.py . --config teardown/brand.json
```

It searches file contents and file names for the original's names (also
inside identifiers like `CalendlyEmbed`, and in German spelling variants
such as Müller, Mueller, Muller), domains and colours (hex, rgb(), rgba()),
skipping dependencies, build output and the `teardown/` planning folder.
Exit 1 means something is left: fix until it is clean. Near-colour warnings
need a look by eye. If the original's name must stay somewhere on purpose
(a licence attribution when the new product is derived from open-source
code, or a comparison page a lawyer has reviewed), list those files under
`allow` in `brand.json`; they are reported as allowed and do not fail the
run. Also check by eye what code cannot: the favicon, page
titles, email templates, the OG image, the app icon, screenshots in the
store listing.

## Step 7: the distance check

Fill in the distance check from `references/legal-eu-dach.md` and save it
as `teardown/legal.md`. Brand mode is finished when every row that must be
"distinct" is distinct.

## Output

`teardown/brand.md`, `teardown/brand.json`, updated tokens, rewritten
strings, `teardown/contrast.md` with every pair passing, a clean sweep, and
`teardown/legal.md` with the distance check.
