# TODO — Task Breakdown & PR Plan

> The 7-stage build decomposed into PR-sized slices. Status: `[ ]` not started ·
> `[~]` in progress · `[x]` done. Each implementation PR: TDD (tests first/with),
> ≤150 code lines/file, ruff-zero, coverage ≥85%, no hard-coded game params
> (`CFG` only), one primary purpose, 50–200 changed LOC (soft cap 300). The
> dedicated PRD (`docs/PRD_*.md`) for a mechanism is authored *before* its slice.
> **Strict linear progression:** finish and merge every slice of a stage before
> the next stage. Ground-truth: `CLAUDE.md` §36; design: `docs/PLAN.md`.

## Shared validation (every implementation PR)

```bash
uv sync
uv run ruff check src tests
uv run pytest tests -q
uv run pytest tests --cov=src --cov-fail-under=85
```
Plus: no-hardcode grep gate; secret scan; conformance run for interop slices
(`scripts/fetch_interop.sh` then `tests/conformance/`). **Stop conditions** (any
slice): scope would exceed 300 LOC → decompose; a new dependency is needed; a
requirement conflicts; an interop vector would need changing → escalate.

## Stage -1 — Planning & setup  `[~]`

- [x] Agent-control files (`CLAUDE.md`+§36, `COSTS.md`, `.env-example`, `.gitignore`)
- [x] Repo tree scaffold, `pyproject.toml`+`uv.lock` (py3.13), README skeleton
- [x] `docs/PRD.md` + `docs/requirements_matrix.md` + 19-PRD catalog (PR #1)
- [x] `docs/PLAN.md` + `docs/architecture.md` + `docs/decisions.md` (PR #2)
- [~] `docs/TODO.md` + `docs/PROMPTS.md` + `docs/REVIEW_POLICY.md` (PR #3, this)
- [ ] Owner inputs when required: student member IDs; Gmail sender/OAuth owner
- Per-mechanism PRDs are authored just-in-time at the head of each stage.

## Stage 1 — Base Logic (pure domain, no I/O)  `[ ]`
Exit: a deterministic, exhaustively-tested domain + config loader runs end-to-end
(a scripted game advances by rules), no networking.

| PR | Scope | Key files | ~LOC | PRD | Tests |
|----|-------|-----------|------|-----|-------|
| 1.1 | constants + board geometry | `domain/constants.py`, `domain/board.py` | ~120 | game_state | `test_board` (neighbors, distance, blocked step, king/orth) |
| 1.2 | own-state machine | `domain/own_state.py` | ~120 | game_state | `test_own_state` (move/barrier/hold, visited, log, budget) |
| 1.3 | rules / terminal | `domain/rules.py` | ~60 | game_state | `test_rules` (capture, survival, terminal) |
| 1.4 | scoring + aggregation | `domain/scoring.py` | ~110 | scoring_league | `test_scoring` (subgame, aggregate, tie) |
| 1.5 | config loader + templates | `shared/config.py`, `config/**` | ~150 | config_constitution | `test_config` (merge, dotted get, version, minimums) |

## Stage 2 — MCP Infra + orchestration  `[ ]`
Exit: two peers negotiate and play a full scripted sub-game over a mocked/real
transport; results/audit agree.

| PR | Scope | Key files | ~LOC | PRD | Tests |
|----|-------|-----------|------|-----|-------|
| 2.1 | protocol schemas | `protocol/*.py` | ~120 | mcp_protocol | `test_protocol` (roundtrip, optional fields, reject bad) |
| 2.2 | gatekeeper + rate limiter | `shared/gatekeeper.py`, `shared/rate_limiter.py` | ~150 | gatekeeper_rate_limit | `test_gatekeeper`, `test_rate_limiter` (queue, retry) |
| 2.3 | canonical JSON + game_ids + negotiation | `interop/*.py` | ~140 | interop_serialization, pregame_agreement | conformance: `canonical_json`, `terms_signature`, `game_uid`; `test_negotiation` |
| 2.4 | FastMCP server (4 tools) + client | `infra/mcp_server.py`, `infra/mcp_client.py` | ~180 | mcp_protocol | `test_transport` (poll/retry/drain), fake transport |
| 2.5 | orchestrator FSM + turn handler/sender + handshake | `orchestration/*.py` | ~200 | orchestrator_fsm, player_agents | `test_runtime` (2 peers, fake transport), reliability |
| 2.6 | SDK + series runner (role alternation) | `sdk/sdk.py`, `sdk/series.py` | ~150 | player_agents | `test_sdk`, `test_series` |

## Stage 3 — Strategy & belief  `[ ]`
Exit: strategy always returns a legal action; pluggable brain seam works.

| PR | Scope | Key files | ~LOC | PRD | Tests |
|----|-------|-----------|------|-----|-------|
| 3.1 | Bayesian belief map | `domain/belief.py` | ~120 | belief_map | `test_belief` (observe, diffuse, exclude, normalize) |
| 3.2 | brains + seam | `domain/brains.py`, `strategy/__init__.py` | ~150 | strategy_brains | `test_brains`, `test_strategy` (injected brain, no-LLM-on-move) |

## Stage 4 — Language + Scent  `[ ]`
Exit: scent emit/decay matches CORE vector; hints capped & audited; game plays
with belief driven by scent + hints.

| PR | Scope | Key files | ~LOC | PRD | Tests |
|----|-------|-----------|------|-----|-------|
| 4.1 | pheromone/scent field | `domain/smell.py` | ~120 | pheromone_scent | conformance `pheromone`; `test_smell` |
| 4.2 | trash-talk template + provider factory | `strategy/trash_talk.py`, `strategy/talk_providers.py` | ~150 | llm_verbal_layer | `test_trash_talk` (template, word cap, bluff) |
| 4.3 | LLM providers (ollama/api/cli), offline-mockable | `llm/*.py` | ~150 | llm_verbal_layer | `test_llm_provider` (mocked; deadline/parse fallback) |

## Stage 5 — Cloud + Tunnel  `[ ]`
Exit: peer reachable via a documented public tunnel; pre-match probe passes.

| PR | Scope | Key files | ~LOC | PRD | Tests |
|----|-------|-----------|------|-----|-------|
| 5.1 | tunnel mode + Host-header + connectivity probe | `infra/*`, `docs/PRD_cloud_tunnel` | ~120 | cloud_tunnel | probe unit test; manual live run (marked) |

## Stage 6 — Security (commit-reveal + interop finalize)  `[ ]`
Exit: sealed logs; mutual audit; tamper→forfeit; report consensus signature; all
CORE vectors pass from our code.

| PR | Scope | Key files | ~LOC | PRD | Tests |
|----|-------|-----------|------|-----|-------|
| 6.1 | commit-reveal sealing + audit + sysinfo step-0 | `interop/commit_reveal.py`, `audit/*`, `shared/sysinfo.py` | ~160 | commit_reveal | conformance `commit_reveal`; `test_crypto`, `test_sysinfo` |
| 6.2 | seal every step + mutual audit integration | `orchestration/*`, `audit/*` | ~120 | commit_reveal | `test_runtime` (audit passes/tamper_forfeit) |
| 6.3 | report consensus signature (spaced) | `reporting/report_writer.py` | ~120 | interop_serialization | conformance `report_consensus`; `test_report_writer` |

## Stage 7 — Reporting Shell  `[ ]`
Exit: four artifacts + report + Gmail draft + GUI + replay + two-repo export;
submission-ready.

| PR | Scope | Key files | ~LOC | PRD | Tests |
|----|-------|-----------|------|-----|-------|
| 7.1 | four artifact builders + schemas + filenames | `reporting/artifacts*.py` | ~180 | logging_audit_reporting | `test_artifacts`, `test_series` (4 files, one uid) |
| 7.2 | Hebrew report emit + emitters wiring | `reporting/emit.py`, `report_writer.py` | ~120 | logging_audit_reporting | `test_report_writer` |
| 7.3 | Gmail send-only OAuth (draft default) | `infra/email_sender.py` | ~130 | email_reporting | `test_email_sender` (mocked; exact bytes) |
| 7.4 | live GUI (local-truth only) | `gui/*` (coverage-omit) | ~200 | gui_replay | `test_live_apply`, `test_game_mode` |
| 7.5 | replay viewer + integrity verify | `gui/replay*.py` | ~180 | gui_replay | `test_replay_data`, `test_replay_normalize` |
| 7.6 | two-repo export + drift check | `scripts/export_repos.py` | ~150 | two_repo_export | export smoke; each export's own suite |
| 7.7 | academic README + submission checklist + tag | `README.md`, `docs/*` | ~docs | — | manual submission checklist |

## Cross-cutting (continuous)
- [ ] Update `docs/requirements_matrix.md` status per merged slice.
- [ ] Update `docs/PROMPTS.md` + `COSTS.md` for significant sessions.
- [ ] Keep `tests/conformance/` green against the fetched league kit; CI drift check.
- [ ] No-hardcode grep gate + secret scan on every PR.
- [ ] Author each mechanism's `PRD_*.md` at the head of its stage.
