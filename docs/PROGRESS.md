# PROGRESS — current state, blockers, next steps

_Last updated: 2026-08-17 evening (Stage 8 COMPLETE; §0 sparring pass clean;
reply to imreeyal ready to send)._

## Stage 8 COMPLETE — league-kit resync (kit HEAD `ad65576`)

All 13 tasks (D8, 8.1–8.13) merged in one day: rule-46/47 endings + thief
concession, capture corroboration (`disputed_capture`), commit-keyed delivery
contract with loud equivocation + reorder window, audit live-binding to
arrived commits, negotiate extras + locked-model hashes +
`counted_games_played`, wire value validation, §6.2 graded league fields +
`links.github` + committed rule-52 ledger, email body+attachment + auto-fire +
recipient-shaped double-arming gate (ADR-20, `--counted`), MCP session
lifecycle + 10s per-call cap, behavior-table conformance (every kit decision
row answered by production code), pairing config (`config/imreeyal/`, derived
ids pinned), and the §0 sparring pass fix (foreign identity without `spec`).
Kit oracle 125/125, zero fixture drift. 315 tests, coverage ≥98%.

**§0 SPARRING PASS (2026-08-17): 6/6 sub-games settled vs the kit's sparring
peer, every mutual audit Verified OK both directions, one `game_uid`;
`check_artifacts` per-directory ALL PASS + cross-team join ALL SETS AGREE.**

**PAIRING LIVE: imreeyal — deadline 2026-08-20.** First contact + disposition:
`docs/pairing/imreeyal_first_contact.md`. Our reply is READY TO SEND:
`docs/pairing/imreeyal_reply_draft.md` (owner reviews windows and sends).
Pinned pairing ids: game_id `imreeyal-vs-vm__fabi`, game_uid
`0e07bcda-4bfd-3668-1fec-86833963b58c`. Confirmed by them 2026-08-18: ids re-derived
independently and MATCH; **parity corrected — vm__fabi = POLICE in sub-games
1/3/5 (launch `police_agent`, they open as thief)**; skip F1, go straight to
the full 6-sub-game friendly (num_games is a signed term); friendly report to
BOTH their addresses; their counted count is now 6. Windows: they're free this
evening + tomorrow all day; counted (T ~21:00 Aug 19, doubly armed:
`game.counted=true` + `--counted`, recipient = lecturer alone, set by hand
before the T), Aug 20 backup. Archive friendly artifacts BEFORE the counted T;
exchange exact playing commits on clean pushed trees at EVERY T.
Window-day tunnel: `ngrok http 8802 --domain=cop-rob-p2p.ngrok.app
--host-header=rewrite` (note: pairing config listens on 8802).

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
   deliberate final send. Default stays disabled/dry-run (ADR-20). ⚠️ Google
   testing-mode refresh tokens expire after ~7 days — mint the token at most a few
   days before the final send. The Cloud project + consent screen +
   `credentials.json` can be prepared any time.
3. **Live tunnel run (AC12)** — start a peer behind the documented public tunnel and
   confirm the pre-match connectivity probe passes.
4. **Cross-implementation game (AC2)** — play ≥1 game over the tunnel against another
   team / sparring peer; confirm it settles byte-identically with zero false
   tamper-forfeits. **Blocked on Stage 8** (conformance gaps would risk zeroing
   the one counted meeting); run the playbook friendly ladder first.
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
