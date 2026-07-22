# TODO — Task Breakdown & PR Plan

> The 7-stage build decomposed into PR-sized tasks. The **Done** column is the
> per-task checkbox: `[x]` = merged, `[~]` = in review, `[ ]` = not started.
> **The PR that completes a task checks its box in the same PR.**
>
> Standing rules for **every** PR (see `CLAUDE.md` §7–§8, `docs/REVIEW_POLICY.md`):
> - TDD (tests first/with); ruff-zero; coverage ≥85%; every file ≤150 code lines;
>   no hard-coded game params (`CFG` only); one primary purpose; 50–200 LOC (soft
>   cap 300).
> - **Update `docs/PROMPTS.md` (one entry) and `COSTS.md` (one row) every PR.**
> - **Check the completed task's box in `docs/TODO.md` in the same PR.**
> - Author a mechanism's `docs/PRD_*.md` before its slice; strict linear stage
>   progression (finish + merge a stage before the next).

**Progress:** Stage -1 ✅ · Stage 1 ✅ · Stage 2 ◻ (in progress).

## Shared validation (every implementation PR)

```bash
uv sync
uv run ruff check src tests
uv run pytest tests -q
uv run pytest tests --cov=src --cov-fail-under=85
```
Plus: no-hardcode grep gate; secret scan; conformance run for interop slices
(`scripts/fetch_interop.sh` then `tests/conformance/`). **Stop conditions:** scope
> 300 LOC → decompose; a new dependency; a requirement conflict; an interop vector
would need changing → escalate.

## Stage -1 — Planning & setup

| Done | Task | Deliverable |
|------|------|-------------|
| [x] | -1.1 | Agent-control files (`CLAUDE.md`+§36, `COSTS.md`, `.env-example`, `.gitignore`) |
| [x] | -1.2 | Repo tree scaffold, `pyproject.toml`+`uv.lock` (py3.13), README skeleton |
| [x] | -1.3 | `PRD.md` + `requirements_matrix.md` + 19-PRD catalog (PR #1) |
| [x] | -1.4 | `PLAN.md` + `architecture.md` + `decisions.md` (PR #2) |
| [x] | -1.5 | `TODO.md` + `PROMPTS.md` + `REVIEW_POLICY.md` (PR #3) |
| [x] | -1.6 | Process upgrade: RTS acceptance, open decisions, phase plan, task checkboxes, per-PR PROMPTS/COSTS |
| [ ] | -1.7 | Owner inputs when required: student member IDs; Gmail sender/OAuth owner |

## Stage 1 — Base Logic (pure domain, no I/O)
Exit: deterministic, exhaustively-tested domain + config; a scripted game advances
by rules; no networking.

| Done | Task | Scope | Key files | ~LOC | PRD | Tests |
|------|------|-------|-----------|------|-----|-------|
| [x] | D1 | design PRDs | — | — | game_state, scoring_league, config_constitution | — |
| [x] | 1.1 | constants + board geometry | `constants.py`, `domain/board.py` | ~120 | game_state | `test_board` |
| [x] | 1.2 | own-state machine | `domain/own_state.py` | ~120 | game_state | `test_own_state` |
| [x] | 1.3 | rules / terminal | `domain/rules.py` | ~60 | game_state | `test_rules` |
| [x] | 1.4 | scoring + aggregation | `domain/scoring.py` | ~110 | scoring_league | `test_scoring` |
| [x] | 1.5 | config loader + templates | `shared/config.py`, `config/**` | ~150 | config_constitution | `test_config` |

## Stage 2 — MCP Infra + orchestration
Exit: two peers negotiate and play a full scripted sub-game over a mocked/real
transport; results/audit agree.

| Done | Task | Scope | Key files | ~LOC | PRD | Tests |
|------|------|-------|-----------|------|-----|-------|
| [x] | D2 | design PRDs | — | — | mcp_protocol, gatekeeper_rate_limit, pregame_agreement, orchestrator_fsm, player_agents | — |
| [x] | 2.1 | protocol schemas | `protocol/*.py` | ~120 | mcp_protocol | `test_protocol` |
| [x] | 2.2 | gatekeeper + rate limiter | `shared/gatekeeper.py`, `shared/rate_limiter.py` | ~150 | gatekeeper_rate_limit | `test_gatekeeper`, `test_rate_limiter` |
| [x] | 2.3a | canonical JSON + hashing + game_ids (CORE vectors) | `interop/{canonical,hashing,game_ids}.py` | ~90 | interop_serialization | `test_interop_primitives`, `test_core_vectors` |
| [x] | 2.3b | negotiation + terms extraction + minimum-validation | `interop/negotiation.py` | ~90 | pregame_agreement | `test_negotiation` |
| [ ] | 2.4 | FastMCP server (4 tools) + client | `infra/mcp_server.py`, `infra/mcp_client.py` | ~180 | mcp_protocol | `test_transport` |
| [ ] | 2.5 | orchestrator FSM + turn handler/sender + handshake | `orchestration/*.py` | ~200 | orchestrator_fsm, player_agents | `test_runtime` |
| [ ] | 2.6 | SDK + series runner (role alternation) | `sdk/*.py` | ~150 | player_agents | `test_sdk`, `test_series` |

## Stage 3 — Strategy & belief
Exit: strategy always returns a legal action; pluggable brain seam works.

| Done | Task | Scope | Key files | ~LOC | PRD | Tests |
|------|------|-------|-----------|------|-----|-------|
| [ ] | D3 | design PRDs | — | — | belief_map, strategy_brains | — |
| [ ] | 3.1 | Bayesian belief map | `domain/belief.py` | ~120 | belief_map | `test_belief` |
| [ ] | 3.2 | brains + seam | `domain/brains.py`, `strategy/__init__.py` | ~150 | strategy_brains | `test_brains`, `test_strategy` |

## Stage 4 — Language + Scent
Exit: scent emit/decay matches CORE vector; hints capped & audited.

| Done | Task | Scope | Key files | ~LOC | PRD | Tests |
|------|------|-------|-----------|------|-----|-------|
| [ ] | D4 | design PRDs | — | — | pheromone_scent, llm_verbal_layer | — |
| [ ] | 4.1 | pheromone/scent field | `domain/smell.py` | ~120 | pheromone_scent | conformance `pheromone`; `test_smell` |
| [ ] | 4.2 | trash-talk template + provider factory | `strategy/trash_talk.py`, `strategy/talk_providers.py` | ~150 | llm_verbal_layer | `test_trash_talk` |
| [ ] | 4.3 | LLM providers (ollama/api/cli), offline-mockable | `llm/*.py` | ~150 | llm_verbal_layer | `test_llm_provider` |

## Stage 5 — Cloud + Tunnel
Exit: peer reachable via a documented public tunnel; pre-match probe passes.

| Done | Task | Scope | Key files | ~LOC | PRD | Tests |
|------|------|-------|-----------|------|-----|-------|
| [ ] | D5 | design PRD | — | — | cloud_tunnel | — |
| [ ] | 5.1 | tunnel mode + Host-header + connectivity probe | `infra/*` | ~120 | cloud_tunnel | probe unit test; manual live run (marked) |

## Stage 6 — Security (commit-reveal + interop finalize)
Exit: sealed logs; mutual audit; tamper→forfeit; report consensus signature; all
CORE vectors pass from our code.

| Done | Task | Scope | Key files | ~LOC | PRD | Tests |
|------|------|-------|-----------|------|-----|-------|
| [ ] | D6 | design PRD | — | — | commit_reveal, interop_serialization | — |
| [ ] | 6.1 | commit-reveal sealing + audit + sysinfo step-0 | `interop/commit_reveal.py`, `audit/*`, `shared/sysinfo.py` | ~160 | commit_reveal | conformance `commit_reveal`; `test_crypto`, `test_sysinfo` |
| [ ] | 6.2 | seal every step + mutual audit integration | `orchestration/*`, `audit/*` | ~120 | commit_reveal | `test_runtime` (audit/tamper) |
| [ ] | 6.3 | report consensus signature (spaced) | `reporting/report_writer.py` | ~120 | interop_serialization | conformance `report_consensus`; `test_report_writer` |

## Stage 7 — Reporting Shell
Exit: four artifacts + report + Gmail draft + GUI + replay + two-repo export.

| Done | Task | Scope | Key files | ~LOC | PRD | Tests |
|------|------|-------|-----------|------|-----|-------|
| [ ] | D7 | design PRDs | — | — | logging_audit_reporting, email_reporting, gui_replay, two_repo_export | — |
| [ ] | 7.1 | four artifact builders + schemas + filenames | `reporting/artifacts*.py` | ~180 | logging_audit_reporting | `test_artifacts`, `test_series` |
| [ ] | 7.2 | Hebrew report emit + emitters wiring | `reporting/emit.py`, `report_writer.py` | ~120 | logging_audit_reporting | `test_report_writer` |
| [ ] | 7.3 | Gmail send-only OAuth (draft default) | `infra/email_sender.py` | ~130 | email_reporting | `test_email_sender` |
| [ ] | 7.4 | live GUI (local-truth only) | `gui/*` (coverage-omit) | ~200 | gui_replay | `test_live_apply`, `test_game_mode` |
| [ ] | 7.5 | replay viewer + integrity verify | `gui/replay*.py` | ~180 | gui_replay | `test_replay_data`, `test_replay_normalize` |
| [ ] | 7.6 | two-repo export + drift check | `scripts/export_repos.py` | ~150 | two_repo_export | export smoke; each export's own suite |
| [ ] | 7.7 | academic README + submission checklist + tag | `README.md`, `docs/*` | docs | — | manual submission checklist |

## RTS gate
- [ ] All PRD §4 acceptance criteria (AC1–AC17) satisfied → declare Ready-To-Submit.

## Cross-cutting (continuous)
- [ ] Update `docs/requirements_matrix.md` status per merged slice.
- [ ] Update `docs/PROMPTS.md` + `COSTS.md` on **every** PR (standing rule).
- [ ] Keep `tests/conformance/` green against the fetched league kit; CI drift check.
- [ ] No-hardcode grep gate + secret scan on every PR.
- [ ] Update `docs/PRD.md` §14 Open Decisions whenever a decision is made.
