# PRD — Configuration Constitution

> Dedicated PRD (guideline §1.3). **Build stage:** 1 (TODO slice 1.5). Ground
> truth: reference `shared/config.py`, book Appendix B/F. Establishes the single
> source of every game parameter so **no numeric literal is ever hard-coded**.

## 1. Background

The game is governed by a **signed shared constitution** (`game.json`) both peers
must hold byte-identically, plus a **private per-peer** file (`game.toml`) that
can never weaken a signed term, plus gatekeeper `rate_limits.json`. A typed
loader (`CFG`) is the only way source code reads parameters.

## 2. Requirements (FR/NFR: FR-7 terms, NFR-6 no-hardcode, NFR-11 versioning)

- Load + merge the three files with correct precedence; expose dotted-key access.
- Validate config + protocol **versions** at runtime; refuse incompatible.
- Validate values against Appendix-F **minimums** (never silently lower).
- Provide the 14-key **signed-terms** subset for the agreement signature.
- Deterministic; no I/O beyond reading these files; secrets never live here.

## 3. Files & schema

- `config/<role>/game.toml` (private, `version` "1.10"): group identity
  (`group_id`, `group_name`, `members`, `repos`, `mcp_servers`), network
  (`my_port`, `opponent_url`, timeouts), `[llm]`, optional `[strategy]` /
  `[trash_talk]`, `[email]`, GUI/seed.
- `config/shared/game.json` (signed, `schema_version` "1.3"): `board_and_agents`,
  `world` (`map_area`, `hint_max_words`), `movement_and_barriers`, `scoring`,
  `pheromones`, `network_and_league`, `rate_limiter_gatekeeper`.
- `config/<role>/rate_limits.json` (`version` "1.10"): per-service limits + queue.

## 4. Loader interface (`CFG` / ConfigManager)

- `ConfigManager(config_dir)` loads `game.toml` (required) + `rate_limits.json`
  (required) + `game.json` (shared, optional-but-required for a match), deep-
  merges the shared terms over local, checks versions.
- `get(dotted_key, default)` → nested lookup (e.g. `get("board.size")`); internal
  accessor mapping bridges names (`board.size↔grid_size`,
  `smell.*↔pheromones.*`, `rules.max_steps↔survival_threshold`).
- Properties: `rate_limits`, `shared`, `service_limits(service)`.
- **Precedence:** a signed `game.json` value overrides any local `game.toml` key,
  so the private file can never weaken an agreed term.

## 5. Signed terms (14 keys) & versions

Terms subset for the signature (order-independent via canonical JSON): `board_size,
smell_grid_size, decay_per_step, emit_intensity, min_center_intensity, max_steps,
barriers_max, setting, hint_max_words, axis_origin_corner, axis_start_index,
thief_start, cop_start, num_games`. Versions: code `1.0.0`, book/protocol `3.0.0`,
config `1.10` (`SUPPORTED_CONFIG_VERSIONS`), `game.json` schema `1.3`
(`shared/version.py`). Runtime refuses unsupported versions.

## 6. Minimum-validation & no-hardcode rule

On load, assert each App-F **minimum** field ≥ its floor (grid 7, barriers 14,
steps/survival 35, gatekeeper rpm 30 / concurrent 2 / backoff 5 / retries 3 /
queue 100); **fixed** fields must equal their pinned value. Source code MUST read
via `CFG`; a grep gate rejects literals duplicating config values.

## 7. Alternatives considered

- One merged config file → **rejected**; signed-vs-private separation is required
  so a peer cannot alter agreed terms.
- Env vars for game params → **rejected**; only secrets use `.env`/`secrets/`.
- TOML for the shared constitution → **rejected**; `game.json` is the signed,
  canonical-JSON-hashable form (book App. B).

## 8. Success criteria

Loads the reference-shaped config; dotted access + name mapping stable; version
mismatch and below-minimum values are rejected with clear errors; signed-terms
extraction is exactly the 14 keys; ≥85% coverage; ruff-zero; file ≤150 lines.

## 9. Test scenarios

Load + dotted get (`board.size`, `pheromones.decay_per_step`); shared overrides
local; missing required file → error; unsupported `version` → error;
below-minimum `grid_size`/`barriers` → rejected; `terms_from_config` returns the
14 keys; `rate_limits["queue"]["max_depth"]` present.
