# Eval fixtures

Synthetic test data for `../evals.json`. Nothing here is real:

- ExampleSlot, ExampleSlot GmbH, the mascot Slotti, NeuSlot, AltSlot,
  OtherSlot and Friseur Beispiel GmbH are fictional.
- Every URL is on example.com (`exampleslot.example.com`,
  `example.com/reviews/...`). No review here was written by a customer of a
  real product; the texts were written for these tests.
- Use the files only to test the skill. Never copy them into a user's
  teardown or present them as findings.

| set | files | used by | what is in it |
| --- | --- | --- | --- |
| `build/` | `teardown/reviews.csv`, `teardown/features.csv` | evals 5, 7, 8, 9, 14, 16 | a rebuild in progress: 27 review rows from capterra, app-store and reddit (one without a link, capterra over 60 %, thin themes, two switches to AltSlot, one to ExampleSlot, words the shipped themes miss); a feature matrix with verified, stale, unknown, partial, skip and screenshot-only rows |
| `offer/` | `teardown/features.csv`, `teardown/recon.md` | eval 14 | recon state for a client offer: nothing built yet, one row without effort, two skip rows, health data in client files |
| `brand/` | `teardown/brand.json`, `src/tokens.css` | evals 10, 16 | the original's names, domain and colours, a draft palette with a failing contrast pair, and draft tokens with a leftover name and a near colour |

| `visibility/` | `teardown/visibility/sitemap.xml` | eval 15 | a saved sitemap of the original: 16 pages in /de/ and /en/ with hreflang, two comparison pages naming AltSlot and OtherSlot, two location pages |

Every CSV starts with a `synthetic test data` column, the XML with a comment, and the JSON
with `_about`, so a copied file still says what it is; the scripts ignore the extra column.

Before a run, copy `<set>/<path>` to `<path>` in an empty working directory:
`build/teardown/reviews.csv` becomes `teardown/reviews.csv`.
