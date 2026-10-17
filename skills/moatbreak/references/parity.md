# Parity mode

How close is the new product to the original, what is missing, and how much
work is left. Parity means it does the same job, not that it looks the same.

Output: `teardown/parity.md`, diff images in `teardown/diffs/`, and the top
five things to build next.

## Step 1: feature parity and remaining effort

Make sure `teardown/features.csv` is current: every row's `clone` column is
`yes`, `partial` (with a note), `no`, or `skip` (with a reason), and open
rows have an effort. Then:

```bash
python3 $SKILL/scripts/parity.py teardown/features.csv --lang de --markdown --buffer 20 --out teardown/parity.md
```

It weights must 3, should 2, could 1, counts partial as half, leaves `skip`
rows and the new product's own additions out of the score (but counts the
additions as work), and reports: the score, must-haves done, each area
weakest first, the missing list by priority (order the actual build by
dependencies, core loop first), and the remaining effort as MVP / + should /
+ could. The effort tiers also count the new product's own additions, so a
tier can list more features than the must-have count. Rows without an effort are listed as unestimated,
so the totals are never quietly too low. Must-haves not done means not
shippable, and it says so.

## Step 2: layout diff

For each key screen or page, take two screenshots at the **same viewport**
(1440x900 desktop, 390x844 mobile) in the **same state** (same data shape,
same tab open, logged in the same way). The original's go in
`teardown/screens/`, the new product's in `teardown/new-screens/`.

```bash
python3 $SKILL/scripts/imgdiff.py teardown/screens/S07.png teardown/new-screens/S07.png --out teardown/diffs/S07.png
python3 $SKILL/scripts/imgdiff.py teardown/screens/S07.png teardown/new-screens/S07.png --json > teardown/diffs/S07.json
python3 $SKILL/scripts/parity.py teardown/features.csv --visual teardown/diffs/*.json --markdown
```

Layout mode compares structure (edge maps on a grid), not colour, because
the rebrand changes every colour on purpose. It reports the score (90+
matches, 75+ close, 50+ partly, below that different), the regions that
differ in the original's pixel coordinates, and height differences. Retina
and normal screenshots compare fine.

Read a high layout score correctly: matching common patterns (a header, a
grid of cards, a two-column checkout) is fine and helps people who switch.
A high score on a screen that is one of the original's **signature
elements** is a warning, not a win. Check it against the distance check in
`legal-eu-dach.md`. Do not chase pixel parity.

`--mode pixel` is exact comparison. Use it for the new product's own
regressions (today against last week), never against the original.

## Step 3: behaviour diff

Walk each flow in both products and compare what the scores cannot see:
clicks to finish the core flow, error handling, what is remembered between
visits, which emails arrive and when, load time on mobile (a public
PageSpeed run is fine for both). Fewer clicks than the original is a win.
Write each difference as: flow, original does, new product does, fix or
keep.

## Step 4: verdict

- **not shippable**: any must-have missing, or any open critical bug
- **shippable**: all must-haves done, feature score 80+, no open critical or
  major bugs
- **better than the original**: shippable, plus the fixes from voice of
  customer. This is the goal; a copy has no reason to exist.

Give honest numbers. A rebuild at 62 is at 62.

## Output

`teardown/parity.md` with the overall score, feature score, layout score per
screen, missing features in build order, behaviour differences, remaining
effort, the verdict, and the top five things to build next.
