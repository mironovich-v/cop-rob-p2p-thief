# PROGRESS — current state, blockers, next steps

_Last updated: 2026-08-05 (end of Stage 7 engineering)._

## Where we are

All seven build stages are engineering-complete. The two-peer game plays end to
end (verified through a full **6-sub-game series**: role alternation, agreeing
results, clean mutual audits, shared `game_uid`), seals every move with
commit-reveal, emits the four JSON artifacts, builds + (draft-)sends the official
report as the exact hashed bytes, ships a live GUI + replay viewer, and exports two
self-contained submission repos.

- **Tests:** 225 passing, offline; **coverage 98.32%** (≥85 gate); ruff clean; every
  file ≤150 code lines.
- **Interop:** all 6 league CORE vectors reproduced by our production functions.
- **RTS gate:** see `docs/PRD.md` §4 — 13 of 17 AC fully satisfied.

## RTS gate summary (AC1–AC17)

| Bucket | ACs |
|--------|-----|
| ✅ Done (engineering) | AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC13, AC15, AC16, AC17 |
| ◑ Dev follow-up | AC1 (CI drift check) |
| ☐ Owner runtime / submission | AC2, AC12, AC14 |

## Owner actions to reach full submission (only these remain)

1. **Member IDs (OD-2)** — replace the `members = ["id-0001", "id-0002"]`
   placeholders in `config/police/game.toml` **and** `config/thief/game.toml` with
   the real student IDs (then re-run the export).
2. **Gmail OAuth (OD-3)** — provide `secrets/credentials.json` + `secrets/token.json`
   (send-only) and set `email.enabled = true`, `email.mode = "send"` only for the
   deliberate final send. Default stays disabled/draft. Recipient is already fixed.
3. **Live tunnel run (AC12)** — start a peer behind the documented public tunnel and
   confirm the pre-match connectivity probe passes.
4. **Cross-implementation game (AC2)** — play ≥1 game over the tunnel against another
   team / sparring peer; confirm it settles byte-identically with zero false
   tamper-forfeits.
5. **Screenshots (AC14)** — capture the live GUI + replay windows on a display
   (WSLg/X) for the submission (`PRD_gui_replay` §8 has the commands).
6. **Export + push (AC13/AC14)** — `uv run python scripts/export_repos.py`, then push
   `dist/police-agent` → `cop-rob-p2p-police` and `dist/thief-agent` →
   `cop-rob-p2p-thief`.
7. **Submission tag** — create the annotated submission tag on each repo (owner git
   action; not delegated).

## Optional dev follow-ups (not blocking submission)

- Wire a CI workflow running the gate + the kit `gen_vectors` drift check (AC1).
- _(done)_ Adversarial robustness: strict step-monotonic dedup drops stale /
  duplicate / out-of-order opponent messages; a dead peer fails closed via timeout
  (AC7). Mid-game restart-resume remains out of scope by design.
