# Configuration

Three files per peer, following the reference model (see `CLAUDE.md` §36.4):

- `<role>/game.toml` — **private**, per-peer: group identity, MCP port + opponent
  URL, LLM / strategy / email / GUI settings, RNG seed. Never signed, never shared.
- `shared/game.json` — the **signed shared constitution** (schema 1.3): the agreed
  game terms both peers must hold byte-identically (board, movement, scoring,
  pheromones, league, gatekeeper). The terms signature covers a 14-key subset.
- `<role>/rate_limits.json` — gatekeeper limits (version 1.10).

Concrete templates with the confirmed binding values are added in the dedicated
config PR. Binding parameter values and the 14 signed-terms keys are pinned in
`CLAUDE.md` §36.2–§36.3. **Never hard-code these in source** — load via the `CFG`
singleton (`cop_thief_core.shared.config`), validated against the official
minimums (never lower a minimum).

Secrets (Gmail OAuth, API keys, tunnel tokens) live in `.env` / `secrets/`,
never here.
