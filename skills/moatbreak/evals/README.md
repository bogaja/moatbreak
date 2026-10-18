# Moatbreak evals

These evals test what the agent does with the skill, not only its scripts
(the script tests are in `../tests/`). Each eval is a user prompt, the
behaviour expected, and 5 to 9 assertions that can be checked from the
agent's answer and the files it writes.

## What the suite covers

| id | mode | language | web | fixtures | what it checks |
| --- | --- | --- | --- | --- | --- |
| 1 | trigger, recon of a shop | de | yes | - | triggers without the words "competitor analysis"; recon, not discover; shop page types, payment methods and commercial promise from dated sources; niche rows; no copied text or theme code |
| 2 | trigger, voice of customer | en | yes | - | "why do people leave X" with a build goal; three or more sources incl. German ones; verbatim linked quotes; sample size; alternatives only as named; `--verify` |
| 3 | discover (step 0) | de | yes | - | only a niche named: sourced candidates in `competitors.csv`, `landscape.py --market`, 3 to 5 proposals, then a question and a stop, no recon |
| 4 | recon with estimate | de | yes | - | niche delta, effort on every row, `parity.py --estimate-only --day-rate`: Personentage, Tagessatz and Puffer as ranges |
| 5 | voice of customer | de | no | `build/` reviews | tuned themes, sample and source bias, thin themes kept out, switching triggers, needs backed by two sources, `--verify` |
| 6 | voice of customer without sources | en | no | - | no web, no file: asks for reviews, invents no quote or count, marks it "to run" |
| 7 | battle card | en | no | `build/` | tags kept, stale checks flagged, only shipped claims, praise in plain words, objection answers without reviewer quotes, `--verify` |
| 8 | "X Alternative" page | de | no | `build/` | § 6 UWG checklist "to check", page-ready rows only, a fair table, dated like-for-like prices, no denigration, no "Klon" |
| 9 | parity | en | no | `build/` matrix | exact score (53.4), not shippable, unestimated and unverified rows, no layout score without screenshots |
| 10 | brand | de | no | `brand/` | DPMA and EUIPO screening "to run", screening is not clearance, `sweep.py` leftovers and near colour, hue distance, `contrast.py` fix |
| 11 | clean-room trap | en | no | - | refuses copying texts and logo and the private API, explains why, offers the legal way, keeps working on the rest |
| 12 | legal launch in Germany | de | no | - | Impressum (§ 5 DDG), DSGVO incl. Art. 9, TDDDG, prior express consent (double opt-in as proof), BFSG with the micro-enterprise question, deposits, distance check |
| 13 | negative trigger | de | no | - | generic market research without a build or compete goal: the skill must not run |
| 14 | client offer | de | no | `offer/`, `build/` reviews | `offer.md` with the numbers from `parity.py`, ranges, exclusions, build or buy, running costs, legal notes, `offer-notes.md` |
| 15 | visibility without an SEO tool | de | no | `visibility/` | `sitemap.py` counts as the script gives them, rivals from comparison pages to confirm, every search metric "not measured", the five AI questions handed to the user, AI answers never customer evidence |
| 16 | build handoff | en | no | `build/` matrix, `brand/` palette | milestones and person-days from `parity.py`, Given/When/Then for all 7 must features, personal-data flags, stack and micro-enterprise questions, `contrast.py` fail at 2.53:1 with its fix, WCAG 2.2 AA build target vs EN 301 549 legal reference, gate "to run" |
| 17 | negative trigger, near miss | de | yes | - | a named product but only a price question: the skill must not run |
| 18 | negative trigger, near miss | de | no | - | generic branding with no original to keep a distance from: the skill must not run |

## Fields

The format follows
[coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/blob/main/skills/competitors/evals/evals.json):
`id`, `prompt`, `expected_output`, `assertions`, `files`. Two fields are
added:

- `web`: true if the eval needs read-only web access. When it is false, run
  the eval without web access; evals 6 and 10 test exactly what the agent
  does then.
- `should_trigger`: false when the skill must not run, or may only narrow
  the request (evals 13, 17 and 18).

`files` are paths relative to the skill folder.

## Fixtures

`files/` holds synthetic data only: fictional products, example.com URLs,
reviews written for the tests (see `files/README.md`). Before a run, copy
each listed file into an empty working directory at the path that follows
`evals/files/<set>/`, so `evals/files/build/teardown/reviews.csv` becomes
`teardown/reviews.csv`:

```bash
# from the skill folder; WORK is an empty directory; the files of eval 7
for f in evals/files/build/teardown/reviews.csv evals/files/build/teardown/features.csv; do
  dest="$WORK/${f#evals/files/*/}"; mkdir -p "$(dirname "$dest")"; cp "$f" "$dest"
done
```

## How to run

With any agent:

1. Start a fresh session with this skill folder installed (not an older
   copy of the skill) and nothing left over from an earlier run.
2. For each eval, use an empty working directory, copy its fixtures, and
   give read-only web access only when `web` is true.
3. Send `prompt` verbatim as the user's message. If the agent stops to
   confirm the scope, answer once with "Ja, passt so, mach weiter." (or
   "Yes, go ahead.") and let it finish. In eval 3, do not answer: the stop is
   what is graded.
4. Keep the answer, the transcript (commands run and their exit codes) and
   the working directory.
5. Grade every assertion pass or fail, with evidence: a quote from the
   answer, a file path with the line, or a command with its exit code. Where
   an assertion compares numbers or exit codes, rerun the script yourself
   (`parity.py`, `reviews.py --verify`, `contrast.py`, `sweep.py`). An
   assertion without evidence fails. An eval with `should_trigger: false`
   passes only if the skill did not run, or only narrowed the request as its
   assertions describe.
6. If you can, let someone who did not run the eval do the grading: a second
   agent or a person.

Agents vary from run to run. When comparing two versions of the skill, run
each eval at least twice per version.

With skill-creator's eval tooling: its format calls the assertion list
`expectations` and is otherwise the same. Convert it, and build a trigger
set for its `scripts/run_eval.py` from `prompt` and `should_trigger`; write
both outside the skill folder (`OUT` is any directory there):

```bash
python3 -c "import json; d=json.load(open('evals/evals.json')); [e.update(expectations=e['assertions']) for e in d['evals']]; print(json.dumps(d, ensure_ascii=False, indent=2))" > "$OUT/evals-skill-creator.json"
python3 -c "import json; d=json.load(open('evals/evals.json')); print(json.dumps([{'query': e['prompt'], 'should_trigger': e['should_trigger']} for e in d['evals']], ensure_ascii=False, indent=2))" > "$OUT/trigger-set.json"
```

skill-creator passes `files` as paths, so tell its executor the copy rule
above. The trigger set has three negative prompts, two of them near misses
(a named product without a build goal, generic branding); add more of your
own before tuning the description with it.

## Results

Record results in `evals/RESULTS.md` (create it with the first run), newest
run first. Per run: the date, the skill version (from `CHANGELOG.md`) and
git commit, the agent and model, whether web access matched the `web`
field, and for every eval passed / total with each failed assertion and its
evidence. Record only runs that happened; an eval that was not run says
"not run". Add a new run instead of editing an old one. Two runs are
recorded there: run 1 (2026-10-17, evals 1 to 14, one run each) and run 2
(2026-10-18, all 18 evals in rounds A to D; round D, on the final state, is
its result of record).

## Changing the suite

- When a mode changes on purpose, change its assertions in the same commit.
  Keep the ids; a new eval gets the next free id.
- Fixtures stay synthetic: fictional names, example.com URLs, no real
  reviews.
- `tests/test_evals.py` checks the format and the fixture facts the
  assertions rely on (parity 53.4, 26 reviews, the failing contrast pair, the
  offer's MVP range, ...). Run it after every change to the evals, the
  fixtures or the scripts.
