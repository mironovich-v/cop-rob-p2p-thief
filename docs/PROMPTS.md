# PROMPTS — AI-Assisted Work Log

> AI-assisted work log (guideline §7.3). **Standing rule: one entry per PR.**
> Kinds: Planning · Implementation · Review/Audit · Fix · Submission.

## 2026-07-21 · Stage -1 · Planning · Merge guidelines into CLAUDE.md
- **Context/Goal:** fold every requirement from `software-project-guidelines.md`
  into a comprehensive project `CLAUDE.md`.
- **Output:** `CLAUDE.md` §1–§35 (operational layer + full engineering standard).
- **Lesson:** the guideline is the global standard; CLAUDE.md is the execution
  layer and may only add, never weaken. **Approved.**

## 2026-07-21 · Stage -1 · Planning · Assess book + league kit
- **Context/Goal:** read `police_thief_p2p.pdf` + `copthief-league-protocol/`;
  decide if requirements are clear enough to start.
- **Issue:** the Hebrew PDF text layer is not machine-readable (RTL scrambling);
  only numbers/English/tables survive. Extracted Appendix-F binding table.
- **Refinement:** owner supplied the lecturer's reference repo as ground truth.
- **Lesson:** treat the reference code as the practical source of truth (ADR-1).

## 2026-07-21 · Stage -1 · Review/Audit · Read reference implementation
- **Context/Goal:** read all of `../Game-P2P-Cop-Chase` (~7.8k LOC) to pin the
  spec. **Method:** 5 parallel explorer subagents (domain / peer+infra /
  report+config / gui+strategy+tests / docs) + first-hand read of the interop core.
- **Output:** confirmed params + the 4 interop serializations + MCP surface + FSM
  + artifact scheme → pinned in `CLAUDE.md` §36; 5 contradictions resolved.
- **Lesson:** parallel read agents cover a large repo fast; verify crown-jewel
  constructions first-hand. **Approved.**

## 2026-07-21 · Stage -1 · Implementation · Bootstrap repo (Stage-0, main)
- **Goal:** generate the repo tree + agent-control files; seed empty `main`.
- **Output:** commit `ff97425` (owner-authorized one-time direct-to-main); scaffold
  builds, ruff clean, imports OK.
- **Decision:** league kit kept external/git-ignored + fetch script (ADR-9).

## 2026-07-21 · Stage -1 · Planning · PR #1 PRD + requirements matrix
- **Goal:** master PRD + traceability matrix; expand PRDs per mechanism.
- **Output:** `docs/PRD.md`, `docs/requirements_matrix.md`, 19 mechanism PRD stubs
  (commit `db889f0`). **Refinement:** replaced the 7 stage stubs (ADR-11).

## 2026-07-21 · Stage -1 · Planning · PR #2 PLAN + architecture + decisions
- **Goal:** C4/design, runtime architecture, ADR log with the 5 contradictions.
- **Output:** `docs/PLAN.md`, `docs/architecture.md`, `docs/decisions.md`
  (ADR-1..15; commit `6a9792f`).

## 2026-07-21 · Stage -1 · Planning · PR #3 TODO + PROMPTS + REVIEW_POLICY
- **Goal:** decompose the 7 stages into PR-sized slices; process docs.
- **Output:** `docs/TODO.md`, `docs/PROMPTS.md`, `docs/REVIEW_POLICY.md` (commit `3421a60`).

## 2026-07-21 · Stage 1 · Planning · PR #4 Stage-1 design PRDs
- **Output:** `PRD_game_state`, `PRD_scoring_league`, `PRD_config_constitution`
  (commit `a833fbd`). Design gate before code.

## 2026-07-21 · Stage 1 · Implementation · PR #5 board + constants (1.1)
- **Output:** `constants.py`, `domain/board.py`, `test_board` (15). Cov 92%. Commit `3badbaa`.

## 2026-07-21 · Stage 1 · Implementation · PR #6 own_state (1.2)
- **Output:** `domain/own_state.py` + `directions_from_move_set`; `test_own_state`
  (12). Cov 96%. Commit `e8e7b07`.

## 2026-07-21 · Stage 1 · Implementation · PR #7 rules (1.3)
- **Output:** `domain/rules.py` + result tokens; `test_rules` (6). Cov 96%. Commit `e432455`.

## 2026-07-22 · Stage 1 · Implementation · PR #8 scoring (1.4)
- **Output:** `domain/scoring.py`; `test_scoring` (8). Cov 97%. Commit `4e06278`.

## 2026-07-22 · Stage 1 · Implementation · PR #9 config loader + templates (1.5)
- **Output:** `shared/config.py`, `exceptions.py`, per-role config templates;
  `test_config` (7). Cov 98%. Commit `84bd6a3`. Completes Stage 1.

## 2026-07-22 · Stage 2 · Planning · Stage-2 design PRDs
- **Output:** `mcp_protocol`, `gatekeeper_rate_limit`, `pregame_agreement`,
  `orchestrator_fsm`, `player_agents` PRDs (branch `stage-2-design-prds`, in review).

## 2026-07-22 · Stage -1 · Docs · Process & tracking upgrade
- **Goal (owner request):** per-PR `PROMPTS.md`/`COSTS.md` rule; `TODO.md` task
  checkboxes; `PRD.md` RTS acceptance + Open Decisions; `PLAN.md` Phase Plan.
- **Output:** this PR (branch `docs-process-and-tracking`).
- **Lesson:** encode tracking/transparency as standing gates, not ad-hoc habits.

## 2026-07-22 · Stage 2 · Implementation · protocol schemas (2.1)
- **Output:** `protocol/messages.py` (TurnMessage/ControlMessage/AuditPayload with
  a defensive `to_dict`/`from_dict` mixin), `protocol/__init__` exports;
  `test_protocol` (7). Cov 98%. Missing-required → TypeError; unknown fields ignored.
- **Lesson:** tolerate extra inbound fields (cross-team payloads) but reject missing
  required — robust interop without a rigid schema.

## 2026-07-22 · Stage 2 · Implementation · gatekeeper + rate limiter (2.2)
- **Output:** `shared/rate_limiter.py` (sliding-window token bucket + FIFO wait
  queue, injectable clock), `shared/gatekeeper.py` (`execute` with transient
  retry + call stats), `ProviderError`/`RateLimitError`; `test_rate_limiter` (4),
  `test_gatekeeper` (4). Cov 98%.
- **Lesson:** an injectable clock makes queue/timeout/window-slide tests
  deterministic and instant (no real sleeping).

## 2026-07-22 · Stage 2 · Implementation · interop primitives + CORE vectors (2.3a)
- **Output:** `interop/canonical.py` (canonical_json/bytes), `interop/hashing.py`
  (commit_of/verify/new_nonce), `interop/game_ids.py` (derive_game_ids);
  `NONCE_BYTES`, `CryptoError`; `test_interop_primitives` (7) + **conformance**
  `test_core_vectors` (4) loading the league fixtures. Cov 98%.
- **Result:** OUR functions reproduce the CORE vectors byte-exactly —
  `canonical_json` (Hebrew/emoji/float), `commit_reveal` reference form,
  `terms_signature`, order-independent `game_uid`. 3 of 6 CORE surfaces done.
- **Lesson:** conformance test skips gracefully if the (git-ignored) kit is not
  fetched, keeping `pytest` green everywhere; unit tests keep coverage regardless.

## 2026-07-22 · Stage 2 · Implementation · negotiation (2.3b)
- **Output:** `interop/negotiation.py` — `terms_from_config` (14-key extraction),
  `Negotiation` (sign/verify, unsigned identity), `validate_minimums` refusing
  below-App-F-floor terms; App-F floors in `interop/limits.json` (data, not source
  literals); `AgreementError`; `test_negotiation` (9). Cov 98%.
- **Lesson:** keep the App-F floors as package DATA (`limits.json`) so the
  no-hardcode grep stays clean and minimums can be raised (never lowered) by config.

## 2026-07-22 · Stage 2 · Implementation · FastMCP server + client (2.4)
- **Output:** `infra/mcp_server.py` (`PeerInboxes`, `build_peer_server` 4 tools,
  `_ensure_port_free`, `start_peer_server`), `infra/mcp_client.py` (`McpTransport`:
  exchange_agreement/send_turn/poll_turn/send_control/poll_control/drain/exchange_audit
  + retry); `infra/__init__` (was missing). `test_mcp_server` (3) + `test_mcp_client`
  (9). Cov 98%.
- **Lesson:** fastmcp's in-memory `Client(server_object)` round-trips the real
  server+client with NO network/port — deterministic tests without a live server.
  (`start_peer_server` is the only network boundary; marked `# pragma: no cover`.)

## 2026-07-23 · Stage 3 · Implementation · belief map (3.1)
- **Context:** owner approved Option A (ADR-16) — build belief/brains/smell before
  the runtime, so the runtime integrates real components once (no rework).
- **Output:** `domain/belief.py` (`BeliefGrid`: uniform init, observe_smell,
  diffuse (von Neumann/king), exclude, most_likely, degenerate reset);
  `test_belief` (8). Cov 98%.
- **Lesson:** diffusion neighbourhood must match the move set (4 vs 8) — passed in.

## 2026-07-23 · Stage 3 · Implementation · brains + strategy seam (3.2)
- **Output:** `domain/brains.py` (`Decision`, `BrainBase` with a null-trash default,
  `ThiefBrain` flee, `PoliceBrain` chase+occasional-barrier), `strategy/__init__.py`
  (`load_brain_cls`, `resolve_brain_cls`, `resolve_brain`); `VERDICT_TRUTH/LIE`;
  `test_brains` (6) + `test_strategy` (7). Cov 98%.
- **Lesson:** a `_NullTrash` default keeps brains decoupled from the (Stage-4)
  trash-talk layer; a `BoomLLM` test asserts the LLM is never touched for a move.

## 2026-07-23 · Stage 4 · Implementation · scent field + CORE vector (4.1)
- **Output:** `domain/smell.py` (`SmellField`: radial Chebyshev emit, max-merge
  absorb, subtractive decay clamp/round, snapshot wire form); `test_smell` (7) +
  `test_pheromone_vectors` in conformance. Cov 98%.
- **Result:** the `pheromone` CORE vector passes from our code — 5 of the 6 CORE
  surfaces done; only `report_consensus` (Stage 6) remains.
- **Lesson:** conformance compares decay via `intensity_at` (snapshot drops the
  clamped 0.0 that the vector's `after` still lists).

## 2026-07-23 · Stage 2 · Implementation · sealing + handshake + FakeTransport (2.5a)
- **Output:** `interop/hashing.seal`; `orchestration/sealing.py` (now_iso,
  identity_from_config, sealed_step_record, build_turn_message);
  `orchestration/handshake.py` (`run_handshake` — exchange/verify/derive ids,
  refuse below-minimum); `tests/conftest.py` FakeTransport + fixtures;
  `test_sealing` (4) + `test_handshake` (2, incl. a threaded two-peer exchange).
  Cov 98%. Runtime (2.5) split into 2.5a (this) / 2.5b (PeerRuntime FSM).
- **Lesson:** host-spec `collect_spec` (sysinfo) is deferred to 6.1, so identity/
  step records omit `spec` for now — added when Step-0 sealing lands.
