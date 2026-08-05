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

**Progress:** Stage -1 ✅ · Stage 1 ✅ · **Stage 2 ✅** (MCP + runtime + SDK/series) · Stage 3 ✅ (belief + brains) · Stage 4 ✅ · Stage 5 ✅ · Stage 6 ✅ (commit-reveal, audit, report sig). Two-peer distributed match runs end-to-end; **all 6/6 CORE vectors pass**. Stage 7 in progress (7.1 artifact builders ✅, 7.2 emit-to-disk + SDK wiring ✅, 7.3a official Hebrew emailed-report body ✅; a full series writes its four JSON artifacts, peers agree on the mutual signature, and the exact-bytes email body is built). 7.3b Gmail send-only (raw-HTTPS, draft/disabled-default, gatekeeper-routed, fully mockable) ✅. 7.4a GUI view-model ✅, 7.4b runtime live event stream ✅, 7.4c Tk shell (board_view/window/player/__main__, `python -m cop_thief_core.gui`) ✅ — the live GUI is complete. 7.5a replay data layer ✅, 7.5b replay Tk viewer (`--replay`, both revealed trajectories, per-step commit verification) ✅ — the GUI (live + replay) is complete. 7.6a headless role CLI entry points (`python -m police_agent` / `-m thief_agent` play a series via the SDK, filling the long-standing stubs) ✅. 7.6b two-repo export ✅. 7.7a email step wired into `SDK.run_peer` (builds the official report, sends the EXACT `report_body` bytes; draft/disabled by default) ✅. 7.7b academic README (install / all run commands / architecture / config / security / credits) ✅. Remaining: 7.7c RTS gate review (AC1–AC17) + submission tag → RTS. Reporting layer is feature-complete pending final CLI/SDK wiring of the email step (7.7) and owner OAuth secrets (OD-3). **Owner manual step:** capture a live-GUI screenshot (WSLg/X display) for FR-21/AC-G4 evidence — run command in `PRD_gui_replay` §8.

> **Build order (ADR-16, Option A):** belief (3.1) → brains (3.2) → smell (4.1)
> are built **before** the runtime (2.5/2.6), which integrates them. Tasks keep
> their IDs; only execution order changed.

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
| [x] | 2.4 | FastMCP server (4 tools) + client | `infra/mcp_server.py`, `infra/mcp_client.py` | ~180 | mcp_protocol | `test_mcp_server`, `test_mcp_client` |
| [x] | 2.5a | sealing + handshake + FakeTransport | `orchestration/{sealing,handshake}.py`, `conftest` | ~110 | orchestrator_fsm, pregame_agreement | `test_sealing`, `test_handshake` |
| [x] | 2.5b | PeerRuntime FSM (turn loop, handler/sender, audit/summary) | `orchestration/{runtime,turn_handler,summary}.py` | ~200 | orchestrator_fsm, player_agents | `test_runtime` (2 peers, FakeTransport) |
| [x] | 2.6 | SDK + series runner (role alternation) | `sdk/*.py` | ~150 | player_agents | `test_series` (2-game series + SDK.run_peer) |

## Stage 3 — Strategy & belief
Exit: strategy always returns a legal action; pluggable brain seam works.

| Done | Task | Scope | Key files | ~LOC | PRD | Tests |
|------|------|-------|-----------|------|-----|-------|
| [ ] | D3 | design PRDs | — | — | belief_map, strategy_brains | — |
| [x] | 3.1 | Bayesian belief map | `domain/belief.py` | ~120 | belief_map | `test_belief` |
| [x] | 3.2 | brains + seam | `domain/brains.py`, `strategy/__init__.py` | ~150 | strategy_brains | `test_brains`, `test_strategy` |

## Stage 4 — Language + Scent
Exit: scent emit/decay matches CORE vector; hints capped & audited.

| Done | Task | Scope | Key files | ~LOC | PRD | Tests |
|------|------|-------|-----------|------|-----|-------|
| [ ] | D4 | design PRDs | — | — | pheromone_scent, llm_verbal_layer | — |
| [x] | 4.1 | pheromone/scent field | `domain/smell.py` | ~120 | pheromone_scent | conformance `pheromone`; `test_smell` |
| [x] | 4.2 | trash-talk template + provider factory | `strategy/trash_talk.py`, `strategy/talk_providers.py` | ~150 | llm_verbal_layer | `test_trash_talk` |
| [x] | 4.3 | LLM providers (ollama/api/cli), offline-mockable | `strategy/{trash_talk,talk_providers}.py` | ~150 | llm_verbal_layer | `test_llm_provider` |

## Stage 5 — Cloud + Tunnel
Exit: peer reachable via a documented public tunnel; pre-match probe passes.

| Done | Task | Scope | Key files | ~LOC | PRD | Tests |
|------|------|-------|-----------|------|-----|-------|
| [x] | D5 | design PRD | — | — | cloud_tunnel | — |
| [x] | 5.1 | tunnel mode + Host-header + connectivity probe | `infra/connectivity.py`, `PRD_cloud_tunnel` | ~30 | cloud_tunnel | `test_connectivity`; manual live run (AC12) |

## Stage 6 — Security (commit-reveal + interop finalize)
Exit: sealed logs; mutual audit; tamper→forfeit; report consensus signature; all
CORE vectors pass from our code.

| Done | Task | Scope | Key files | ~LOC | PRD | Tests |
|------|------|-------|-----------|------|-----|-------|
| [x] | D6 | design PRDs | — | — | commit_reveal (6.1), interop_serialization (6.3) | — |
| [x] | 6.1 | sysinfo + Step-0 host-spec sealed record + PRD_commit_reveal | `shared/sysinfo.py`, `orchestration/sealing.py` | ~60 | commit_reveal | `test_sysinfo`; conformance `commit_reveal` (2.3a) |
| [x] | 6.2 | adversarial audit: tampered log -> tamper_forfeit | `tests/integration/test_audit.py` | ~50 | commit_reveal | `test_audit` (valid/tamper/skip) |
| [x] | 6.3 | report consensus signature (spaced) | `reporting/report_writer.py` | ~40 | interop_serialization | conformance `report_consensus`; `test_report_writer` |

## Stage 7 — Reporting Shell
Exit: four artifacts + report + Gmail draft + GUI + replay + two-repo export.

| Done | Task | Scope | Key files | ~LOC | PRD | Tests |
|------|------|-------|-----------|------|-----|-------|
| [ ] | D7 | design PRDs | — | — | logging_audit_reporting, email_reporting, gui_replay, two_repo_export | — |
| [x] | 7.1 | four artifact builders + schemas + filenames | `reporting/artifacts*.py` | ~180 | logging_audit_reporting | `test_artifacts` |
| [x] | 7.2 | artifact emit-to-disk + SDK wiring | `reporting/emit.py`, `sdk/sdk.py` | ~120 | logging_audit_reporting | `test_emit`, `test_series` (4 files) |
| [x] | 7.3a | official Hebrew emailed report + exact body bytes | `reporting/report_builder.py` | ~70 | email_reporting | `test_report_builder` |
| [x] | 7.3b | Gmail send-only OAuth (raw-HTTPS, draft default, gatekeeper) | `infra/email_sender.py`, `infra/gmail_client.py` | ~140 | email_reporting | `test_email_sender`, `test_gmail_client` |
| [x] | 7.4a | GUI view-model (event→window, game-mode, local-truth boundary) | `gui/{live_apply,game_mode}.py` (coverage-omit) | ~110 | gui_replay | `test_live_apply`, `test_game_mode` |
| [x] | 7.4b | runtime emits live event stream (moved / game_over) | `orchestration/runtime.py` | ~15 | gui_replay | `test_runtime` (event stream) |
| [x] | 7.4c | Tk shell (board_view / window / player / __main__) renders the stream | `gui/{board_view,window,player,__main__}.py` | ~210 | gui_replay | `test_gui_shell` (display-guarded); manual + screenshot |
| [x] | 7.5a | replay data layer: normalize + crypto re-verify + reconstruct both trajectories | `gui/replay_data.py` | ~80 | gui_replay | `test_replay_data`, `test_replay_normalize` |
| [x] | 7.5b | replay Tk viewer (playback of both revealed positions) | `gui/replay.py`, `gui/__main__.py` | ~140 | gui_replay | `test_replay_view` (display-guarded); manual |
| [x] | 7.6a | headless role CLI entry points (fill police/thief `__main__` stubs) | `cop_thief_core/agent_cli.py`, `{police,thief}_agent/__main__.py` | ~40 | two_repo_export | `test_agent_cli` |
| [x] | 7.6b | two-repo export + drift check | `scripts/export_repos.py`, `scripts/export_lib.py` | ~150 | two_repo_export | `test_export`; vendored suite runs standalone |
| [x] | 7.7a | wire the email step into the SDK (exact report_body, draft/disabled default) | `sdk/sdk.py` | ~20 | email_reporting | `test_email_wiring` |
| [x] | 7.7b | academic README (install/usage/architecture/run) | `README.md` | docs | — | manual |
| [ ] | 7.7c | RTS gate review (AC1–AC17) + submission tag | `docs/*` | docs | — | manual submission checklist |

## RTS gate
- [ ] All PRD §4 acceptance criteria (AC1–AC17) satisfied → declare Ready-To-Submit.

## Cross-cutting (continuous)
- [ ] Update `docs/requirements_matrix.md` status per merged slice.
- [ ] Update `docs/PROMPTS.md` + `COSTS.md` on **every** PR (standing rule).
- [ ] Keep `tests/conformance/` green against the fetched league kit; CI drift check.
- [ ] No-hardcode grep gate + secret scan on every PR.
- [ ] Update `docs/PRD.md` §14 Open Decisions whenever a decision is made.
