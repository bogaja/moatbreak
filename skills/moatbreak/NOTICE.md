# Notice

Moatbreak is a derivative work of **Replica** by Jake Schincariol
(https://github.com/Jakeschincariol/replica-skill, version 1.0, October 2026),
used under the MIT License. The original copyright notice is kept in
`LICENSE`, as the licence requires.

Changes and additions: Copyright (c) 2026 Bogaja LLC, Sheridan, Wyoming,
USA. Author: Bogachan Önal.

Former name: until October 2026 this skill was used privately as
`competitor-teardown` (version 1.1). Moatbreak 1.0.0 is the same work under
its new name and its first public release; see `CHANGELOG.md`.

Taken from Replica and changed: the recon, entrepreneur (now voice of
customer), diff (now parity) and brand skills, merged into one skill with
four modes, and the scripts `reviews.py`, `parity.py`, `sweep.py` and
`imgdiff.py` (imgdiff.py is unchanged apart from its header).

Not taken: architect, design, build, backend, test, launch and deploy. The
launch reference and `listing.py` added in 1.1.0 were written fresh from the
stores' published limits and Moatbreak's own rules, without using Replica's
launch skill or its `listing.py`.

New in 1.1.0 and not derived from Replica: discover mode and
`landscape.py`, the visibility add-on and `sitemap.py`, the build handoff
(`references/build-handoff.md`, `templates/build-brief.md`), `contrast.py`
(written fresh from the WCAG 2.2 definitions of relative luminance and
contrast ratio, without using Replica's `contrast.py`), the battle card
(`battlecard.py`, `references/battlecard.md`, `templates/battlecard.md`),
`seo.py`, `sources.py`, `report.py`, `listing.py` and `references/launch.md`,
the quote check, source-bias, segment and switching parts of `reviews.py`,
the worked example in `examples/` and the evals in `evals/`. All of it is
new work by Bogaja LLC. The build handoff writes a brief for whatever
build tools the session has; it does not take over Replica's architect,
build, test or deploy skills.

## What changed

- One skill with a mode router and narrow triggers instead of four separate
  skills, so it does not fire on generic branding or positioning requests.
- Websites and online shops as first-class targets next to apps and SaaS
  (page-type inventory, checkout and payment methods, shipping and returns).
- Signature elements: recon lists what makes the original recognisable, so
  it is rebuilt in function but never in look.
- EU, Germany, Austria and Switzerland legal checklist with a distance check
  (imitation under UWG, design and database rights, Impressum, DSGVO, BFSG,
  consumer-sales rules, comparative advertising, search ads).
- Agency deliverables: offer template, scope packages, build-or-buy section,
  report outline, guidance for several references, "like X but for niche
  Y", and recon without any readable source.
- reviews.py: German themes and request patterns (including compounds such
  as Versandkosten), shop themes (shipping, returns, quality, size and fit,
  checkout, invoice purchase), praise kept apart from complaints (4.5-5 star
  reviews never count as complaints), a "what they praise" section, German
  CSV headers and semicolon exports, rating formats (4,5 / 4/5 / 8/10 /
  stars), German dates, per-source summary, one-platform warning, German
  report (--lang de).
- parity.py: German values (muss/soll/kann, ja/teilweise/nein/entfällt),
  original = unknown for unverified rows, effort column (XS-XL or
  person-days), remaining effort as MVP / + should / + could, contingency,
  overheads in percent, fixed items, day rate and cost range,
  --estimate-only for offers, --out, a clear message when parity cannot be
  measured yet, German report.
- sweep.py: German spelling variants (ä/ae/a, ß/ss), rgb()/rgba() and
  8-digit hex, near-colour warnings by Delta E, an allow-list for files
  where the name is there on purpose (licence attribution), teardown/
  planning folder.
- Brand checks extended with DPMA, TMview, Swissreg, see.ip, company
  registers, EUIPO DesignView and German work-title protection.
- Tests for every change (239 tests, standard library only).
