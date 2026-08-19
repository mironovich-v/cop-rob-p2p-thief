# Configuration

Three files per peer, following the reference model (see `CLAUDE.md` §36.4).
`ConfigManager(config/<role>)` loads all three from the role directory:

- `<role>/game.toml` — **private**, per-peer: group identity, MCP port + opponent
  URL, LLM / strategy / email / GUI settings, RNG seed. Never signed, never shared.
- `<role>/game.json` — the **signed shared constitution** (schema 1.3): the agreed
  game terms. **Both peers hold a byte-identical copy** (police and thief copies
  here have the same SHA-256); the pre-game signature refuses to play on mismatch.
  Overlays the private TOML. The terms signature (Stage 2) covers a 14-key subset.
- `<role>/rate_limits.json` — gatekeeper limits (version 1.10).

The templates ship the confirmed binding values (grid 7, barriers 14, steps 35,
scent 0.9/0.10/5×5, scoring 20/5/5/10, tie 2). These are defaults/minimums that
may be **raised** by mutual agreement, never lowered. **Never hard-code them in
source** — load via `CFG` (`cop_thief_core.shared.config`). Minimum-validation
lands in a follow-up slice (loads App-F floors from data, not source literals).

Secrets (Gmail OAuth, API keys, tunnel tokens) live in `.env` / `secrets/`,
never here.
