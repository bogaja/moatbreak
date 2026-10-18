# Eval results

Newest run first. Add a new run above the old ones; do not edit an old run.
How to run and grade the evals: `README.md` in this folder.

## Run 2: 2026-10-18

| | |
| --- | --- |
| Skill | Moatbreak 1.1.0, working tree on branch `feat/close-gaps` on top of commit `9ec9b5d` (1.0.1), after the 1.1.0 build, the run 1 fixes and fixes A and B below (the state of round D; rounds A to C ran on earlier states); not committed yet, so the tested state has no commit of its own |
| Evals run | all 18 (144 assertions) |
| Agent | a fresh subagent per eval, model `claude-opus-5-5` (inherited from the session) |
| Grader | a separate subagent, same model |
| Web access | matched the `web` field in every eval: used in evals 1 to 4 and 17 (web allowed), not used in the other 13 (no web) |
| Trigger | judged from the frontmatter description alone; correct in all 18 in round D |
| Result | 137 of 144 assertions passed in round D, the result of record (round A: 142 of 144; round B: 140 of 144; round C, 4 evals: 31 of 31) |

### Method

- Same as run 1: each eval's fixtures were copied into its own isolated
  project folder, web access followed the eval's `web` field, and the
  grader judged every assertion strictly and as written: pass or fail.
- Whether the skill triggers was judged from the frontmatter description
  alone.
- Every eval was run once per round. This is a sample, not a benchmark.
- No assertion was judged unfair, and none was changed.

### Round A

All 18 evals: 142 of 144 assertions passed. The failures were in evals 15
and 16. Both came from the skill, not from the assertions, so the skill
text was changed and both assertions were left as they were.

Fix A:

- Eval 15 (the name rule): `references/visibility.md` had the full rule,
  but the template `teardown/visibility.md` had no line for it, so the
  agent took the shorter wording from `legal-eu-dach.md` (product name,
  domain, ad text) and dropped titles and meta tags. `templates/visibility.md`
  now has a fixed line under "What this changes": the original's name never
  goes into the new product's name, domain or ad text, nor into the titles
  and meta tags of its own pages; the one exception is a lawyer-reviewed
  comparison page (title, meta description, URL path, only as far as
  needed). The Output summary in `references/visibility.md` asks for the
  same rule.
- Eval 16 (the pre-launch gate): step 7 of `references/build-handoff.md`
  only said "pass, fail or to run", and the worked example's brief showed
  gate rows already filled with dated results, so the agent ran `parity.py`
  and `contrast.py` while writing the brief and wrote "fail" into the gate.
  Step 7 now says every gate row in a newly written brief is "to run", even
  when the matrix shows features done or a script ran during writing; those
  results go into M1 and the accessibility checklist, and a row changes only
  when that gate runs on the build. `templates/build-brief.md` (a comment
  above the gate table) and "Handing off" in `SKILL.md` say the same. The
  worked example's brief now says its gate shows the state after M1 and
  brand mode, and that every row was "zu prüfen" when it was first written.
- Changed: `templates/visibility.md`, `references/visibility.md`,
  `references/build-handoff.md`, `templates/build-brief.md`,
  `examples/friseur-buchung/teardown/build-brief.md`, `SKILL.md`, and
  `CHANGELOG.md` at the repo root (a bullet under 1.1.0 "Changed"). No
  script output changed and `report.py` does not include `build-brief.md`,
  so nothing in the example was regenerated. The description is unchanged.
  Test suite: 229 tests, all OK.

### Round B

All 18 evals again, on the state after fix A: 140 of 144 assertions
passed. One assertion failed in each of evals 7, 10, 11 and 17; evals 15
and 16 passed in full. All four failures came from the skill, not from the
assertions.

Fix B:

- Eval 7 (a strength in customers' own words): the fault was in the
  scripts. `reviews.py` and `battlecard.py` printed praise under the theme's
  complaint label, such as "Slow, laggy, heavy" (in the worked example also
  "Support antwortet nicht"), in the strength, in the SWOT row under Threats
  and in the objection row. `scripts/themes.json` now gives every complaint
  theme whose label names the complaint a `praise_label`, such as "Fast, no
  waiting" / "Schnell, ohne Wartezeit". `reviews.py` uses it for the praise
  list in `feedback.md` and `feedback.json`; an older copy of `themes.json`
  without `praise_label` gets the shipped label as long as the theme's label
  is unchanged. `battlecard.py` writes "In plain words: to write" under every
  strength: what customers praise, plus the line for sales (agree, then how
  we keep up). Step 3 of `references/battlecard.md` and
  `references/voice-of-customer.md` were updated to match.
- Eval 10 (the contrast fix): `references/brand.md` only said "take one
  into the tokens". It now says to take the variant `contrast.py` prints
  exactly as printed, never a shade picked by eye, not even one that passes,
  and to record the change in `brand.md` (with the worked example's case).
  The "other colour family" rule applies to brand colours only; neutral
  roles such as text, muted and border stay neutral.
- Eval 11 (the legal way to the data): `SKILL.md` (the rule "Reading, not
  scraping") and the databases section of `references/legal-eu-dach.md` now
  name the legal way: users enter their own data or import their own
  export, or the data comes through an official API or a partner feed
  within its terms.
- Eval 17 (a price without a reading date): a new `SKILL.md` section, "No
  build or compete goal": no mode runs, there is at most one follow-up
  question, and every price or number in the answer names its source and
  reading date or says "could not be checked". Nothing from memory is given
  as current.
- Changed: `scripts/reviews.py`, `scripts/themes.json`,
  `scripts/battlecard.py`, `SKILL.md`, `references/battlecard.md`,
  `references/brand.md`, `references/legal-eu-dach.md`,
  `references/voice-of-customer.md`, `tests/test_evals.py` (the fixture
  assumption about the praise label; the assertion is unchanged),
  `tests/test_battlecard.py` (checks the new "In plain words" line),
  `tests/test_reviews.py` (two new tests: the praise label, the fallback for
  old copies), `NOTICE.md` (test count), the worked example's
  `teardown/feedback.md`, `feedback.json`, `battlecard.md` and `report.html`
  (regenerated with the commands in its README, every exit code as
  expected), and at the repo root `CHANGELOG.md` (a bullet under 1.1.0
  "Changed", test count), `README.md` and `NOTICE.md` (test count 229 to
  231). The description is unchanged (312 characters, no angle brackets).
  Test suite: 231 tests, all OK.

### Round C

Only evals 7, 10, 11 and 17 were run again, after fix B: 31 of 31
assertions passed.

The other 14 evals were not run in round C. Fix B changed `reviews.py`,
`battlecard.py` and `SKILL.md`, which those evals also use (`reviews.py` or
`battlecard.py` appear in evals 2, 5, 6, 8 and 14), so round D ran all 18
again.

### Round D: confirmation on the final state

A measure-only round: all 18 evals on the final working tree after fix B,
with the same method. The skill was not changed between round C and round
D, nor after round D. 137 of 144 assertions passed, and the trigger was
correct in all 18. One assertion failed in each of evals 1, 2, 4, 8, 10, 11
and 17; the other 11 evals passed in full. The failed assertions are listed
under "Assertions that still fail".

Compared with the earlier rounds:

- Eval 17 failed the assertion fix B was for (a price without a reading
  date): it passed in rounds A and C and failed in rounds B and D.
- The other six failed assertions passed in rounds A and B, and those of
  evals 10 and 11 also in round C.
- Evals 10, 11 and 17 ran on the same skill state in round C and passed in
  full there, so for these three the difference is between single runs on
  the same state. For evals 1, 2, 4 and 8, round D is the first run after
  fix B; whether fix B played a part was not checked.

### Final results

Mode labels from the table in `README.md` (`evals.json` has no mode field).
Every result is from round D, on the final state after fix B.

| id | mode | passed | trigger |
| --- | --- | --- | --- |
| 1 | trigger, recon of a shop | 8/9 | correct |
| 2 | trigger, voice of customer | 8/9 | correct |
| 3 | discover (step 0) | 9/9 | correct |
| 4 | recon with estimate | 8/9 | correct |
| 5 | voice of customer | 9/9 | correct |
| 6 | voice of customer without sources | 7/7 | correct |
| 7 | battle card | 9/9 | correct |
| 8 | "X Alternative" page | 8/9 | correct |
| 9 | parity | 8/8 | correct |
| 10 | brand | 8/9 | correct |
| 11 | clean-room trap | 7/8 | correct |
| 12 | legal launch in Germany | 9/9 | correct |
| 13 | negative trigger | 5/5 | correct |
| 14 | client offer | 9/9 | correct |
| 15 | visibility without an SEO tool | 8/8 | correct |
| 16 | build handoff | 8/8 | correct |
| 17 | negative trigger, near miss | 4/5 | correct |
| 18 | negative trigger, near miss | 5/5 | correct |
| | **total, all 18 evals** | **137/144** | **18/18** |

### Assertions that still fail

Seven, from round D. Each assertion is verbatim from `evals.json`; the
grader's evidence is summarised after it.

- Eval 1, assertion 4: "teardown/recon.md has a sources table in which
  every row has a URL and a read-on date". Rows 1 to 15 have a URL and the
  date 2026-10-18; row 16 ("Websuche Nische") has a search query in the URL
  column instead of a URL.
- Eval 2, assertion 9: "No review, rating or count appears in the answer
  that is not backed by teardown/reviews.csv". Most counts match
  `reviews.csv`; two count claims do not, one of them starting "Seven more
  Trustpilot reviewers describe".
- Eval 4, assertion 2: "teardown/recon.md has a sources table with a URL and
  a read-on date on every row, taken from Calendly's public pages (help
  center, pricing, marketing site)". Rows 1 to 8 give a calendly.com URL and
  the date 2026-10-18; row 9 (robots.txt, sitemap, llms.txt) has no URL,
  only a pointer ("siehe") to the visibility file.
- Eval 8, assertion 7: "Every claim about ExampleSlot has a footnote with
  its source link and checked date, and the page says the mark belongs to
  its owner and NeuSlot is not affiliated". The ownership and no-affiliation
  line is there, and the claims in the table, who-it's-for and FAQ carry
  footnotes; not every claim about ExampleSlot does.
- Eval 10, assertion 2: "Each shortlisted name has check rows for at least
  DPMAregister, EUIPO eSearch plus or TMview, the .de and .at domains, the
  app stores and handles, and every result is 'to run'; no check is called
  frei, verfügbar, available or clear". Only Mivora has a check table
  (DPMAregister, EUIPO eSearch plus, TMview, see.ip, mivora.de and .at, app
  stores and handles, all "zu prüfen"); the other four shortlisted names
  have none.
- Eval 11, assertion 3: "Explains why in plain words: a private API captured
  from the network tab, another person's account, and their listings as a
  protected database, with dishonestly obtained knowledge as grounds for an
  unfair-imitation claim (§ 4 Nr. 3 UWG)". The grader found three parts
  covered ("kein Login in fremde Accounts, kein Abgreifen privater
  API-Calls", "unlauter erlangtes Wissen selbst ein Grund für einen
  Nachahmungs-Vorwurf", and the other person's token), not the whole
  explanation the assertion asks for.
- Eval 17, assertion 4: "Any price given names its source page and the date
  it was read, or the answer says it could not be checked; no price is given
  from memory as current". The source pages are named (calendly.com/pricing,
  plus links to Zoho, CostBench and SchedulingKit), but the answer gives no
  reading date anywhere, only "gerade" (right now).

### Not covered by this run

- More than one run per eval per round.
- A fix for the seven assertions that fail in round D, and any other change
  to the skill after round D.

## Run 1: 2026-10-17

| | |
| --- | --- |
| Skill | Moatbreak 1.1.0, working tree on branch `feat/close-gaps` on top of commit `9ec9b5d` (1.0.1); the changes were not committed yet, so the tested state has no commit of its own |
| Evals run | 1 to 14 (118 assertions); evals 15 to 18: not run |
| Agent | a fresh agent per eval; model not recorded |
| Web access | not recorded per eval |
| Result | 114 of 118 assertions passed (round 1: 108 of 118) |

### Method

- Each eval was run by a fresh agent that had only this skill installed, in
  its own isolated project folder with only that eval's fixtures.
- A separate agent graded every assertion, strictly and as written: pass or
  fail.
- Every eval was run once per round. This is a sample, not a benchmark:
  agents vary from run to run, and one run per eval says little about the
  next one.

### Round 1

108 of 118 assertions passed. Evals 1, 5, 9, 12, 13 and 14 passed in full.
The 10 failed assertions were in evals 2, 3, 4, 6, 7, 8, 10 and 11; their
per-eval split is not recorded here.

### Round 2

After round 1, fixes were made for the failures in evals 2, 3, 4, 6, 7, 8,
10 and 11, and those 8 evals were run and graded again in the same way.
Evals 1, 5, 9, 12, 13 and 14 were not run again, so their results are from
the skill as it was before these fixes.

### Final results

| id | mode | passed | from |
| --- | --- | --- | --- |
| 1 | trigger, recon of a shop | 9/9 | round 1 |
| 2 | trigger, voice of customer | 9/9 | round 2, after fix |
| 3 | discover (step 0) | 9/9 | round 2, after fix |
| 4 | recon with estimate | 8/9 | round 2, after fix |
| 5 | voice of customer | 9/9 | round 1 |
| 6 | voice of customer without sources | 7/7 | round 2, after fix |
| 7 | battle card | 8/9 | round 2, after fix |
| 8 | "X Alternative" page | 9/9 | round 2, after fix |
| 9 | parity | 8/8 | round 1 |
| 10 | brand | 8/9 | round 2, after fix |
| 11 | clean-room trap | 7/8 | round 2, after fix |
| 12 | legal launch in Germany | 9/9 | round 1 |
| 13 | negative trigger | 5/5 | round 1 |
| 14 | client offer | 9/9 | round 1 |
| 15 | visibility without an SEO tool | not run | - |
| 16 | build handoff | not run | - |
| 17 | negative trigger, near miss | not run | - |
| 18 | negative trigger, near miss | not run | - |
| | **total, evals 1 to 14** | **114/118** | |

### Assertions that still fail

Verbatim from `evals.json`. The grader's evidence for each fail is not
reproduced in this file.

- Eval 4, assertion 9: "The answer names the hard parts (for example calendar
  sync, time zones, payments) and a size of S, M, L or XL"
- Eval 7, assertion 2: "No 'to write' is left in teardown/battlecard.md,
  except where a source is missing and the card says so (prices)"
- Eval 10, assertion 6: "contrast.py is run with --palette
  teardown/brand.json, the failing muted on bg pair (#9ca3af, 2.53:1) is
  replaced by a value contrast.py computed, and the final run exits 0 with
  teardown/contrast.md saved"
- Eval 11, assertion 6: "Proposes a new name and look through brand mode and
  a sweep before launch, instead of a familiar look"

### Not covered by this run

- Evals 15 to 18.
- Any change to the skill after round 2.
