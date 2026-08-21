# Match evidence — played games

This tree is the record that the games in this project **actually took place**.
Every file here was emitted by the production peers at play time (the four
artifacts of the book's scheme: `declaration_*`, `config_*_gNN`, `log_*_gNN`,
`result_*`), not reconstructed afterwards.

`logs/` and `results/` are `.gitignore`d so that routine local runs stay out of
git. The sets below are deliberate, force-added **evidence snapshots**: they are
tracked, while any future run remains ignored. Do not "fix" the ignore rules to
make new artifacts appear — add the next snapshot explicitly, the same way.

## Inter-group games (against other teams)

| Set | Date | Opponent | Counted | Outcome |
| --- | --- | --- | --- | --- |
| `counted/nis-yar1-2026-08-18/` | 2026-08-18 | nis-yar1 | **yes** (rule-52 series 1) | 6 sub-games, vm__fabi 30 – nis-yar1 90 |
| `friendlies/nis-yar1-2026-08-18/` | 2026-08-18 | nis-yar1 | no | 6 sub-games, friendly |
| `friendlies/nis-yar1-2026-08-18-refriendly/` | 2026-08-18 | nis-yar1 | no | 6 sub-games, re-friendly before the counted series |
| `friendlies/il-nv-ai-2026-08-21/` | 2026-08-21 | il-nv-ai | no | 1 sub-game warm-up, vm__fabi 20 – il-nv-ai 5 |

Only the `counted/` set is a league game under rule 52; the ledger of counted
series is `rule52_ledger.json`. The friendlies are qualifying/warm-up games that
partners required before agreeing to a counted series.

The il-nv-ai warm-up is also the record of a live interoperability finding: that
peer's game-ending `caught: true` final omits the `claim` key that SPEC §3.1
pins, so `log_*_g01.json` carries a **degraded** capture corroboration
(`kind: "unknown"`) rather than a resolved answer/concession verdict. The
capture itself is sound — our own step-15 `BARRIER:N` from `[2,1]` walls `[1,1]`,
the cell their team reported as the rule-46 ending.

## Intra-group games (our own police vs our own thief)

`../logs/vm__fabi-police/` and `../logs/vm__fabi-thief/` hold a 25-sub-game
self-play series run as two independent OS processes with separate private
directories — one artifact set per side, which is why the same games appear
twice. These prove the engine plays itself end to end with clean mutual audits;
they are not league games and carry no league score.

## Verifying a set

Each `log_*_gNN.json` carries sealed commit–reveal `records` and a
`mutual_agreement` block; each `result_*.json` derives its totals from those
logged events rather than from any claim. Both sides of a match hold
independently produced copies, and the agreement hash is what makes them
comparable.
