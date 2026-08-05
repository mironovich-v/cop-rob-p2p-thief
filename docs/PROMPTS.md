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

## 2026-07-23 · Stage 2 · Implementation · PeerRuntime FSM (2.5b)
- **Output:** `orchestration/{runtime,turn_handler,summary}.py` (turn loop wiring
  belief+smell+brain+sealing, capture/win claims, watchdog timeout, mutual audit →
  tamper_forfeit); `interop.audit_records`; `FINAL_CAUGHT_HINT`; config `override`;
  integration `tests/integration/test_runtime.py` (6). Cov 98%.
- **Result:** two PeerRuntimes play a full sub-game in-process over FakeTransport —
  both agree on result/winner, audits pass both ways, sealed per step, shared
  game_uid derived, timeout handled. AC5 (no referee, results derived) met.
- **Lesson:** dropped the GUI control channel + LLM token accounting for a focused
  runtime; the reference's per-file split keeps each module ≤150 lines.

## 2026-07-23 · Stage 2 · Implementation · SDK + series runner (2.6)
- **Output:** `sdk/series.py` (`role_for` alternation, `run_series`, `SeriesResult`),
  `sdk/sdk.py` (`SimulationSdk.run_peer` single entry, `StubLlm`, `_build_transport`
  network boundary); `test_series` (role_for, 2-game series, SDK.run_peer). Cov 98%.
  **Closes Stage 2.**
- **Result:** a 2-sub-game series alternates roles, reuses one transport, and both
  peers agree per sub-game and share one game_uid. Artifacts/report/email deferred
  to the reporting stage; a real LLM provider to the language stage.
- **Lesson:** num_games is a signed term, so a test must override it on BOTH
  configs to keep the handshake terms value-equal.

## 2026-07-23 · Stage 4 · Implementation · trash-talk template (4.2)
- **Output:** `strategy/trash_talk.py` (`TrashTalk`: setting-keyed landmarks, thief
  40% bluff, word-cap-before-wire), `strategy/talk_providers.py`
  (`resolve_trash_talk`, template default); wired into `resolve_brain` (replaces the
  null provider); `test_trash_talk` (7). Cov 98%.
- **Lesson:** the verdict (truth/lie) is decided by the provider and sealed into the
  commit; the opt-in LLM providers + deadline/parse fallback come in the next slice.

## 2026-07-23 · Stage 4 · Implementation · opt-in LLM providers (4.3)
- **Output:** `LlmTrashTalk` (every_n_steps gating, `_ask_bounded` worker-thread
  deadline, template fallback on any error/timeout/parse); `resolve_trash_talk`
  claude_cli/ollama/claude_api branches with lazy `anthropic`; `test_llm_provider`
  (9, fake askers — no live model). Cov 98%. **Closes Stage 4.**
- **Lesson:** the network askers are `# pragma: no cover`; `anthropic` stays an
  OPTIONAL dep via lazy import, so `pyproject` is unchanged. Any LLM failure falls
  back to the free template — the game never stalls.

## 2026-07-23 · Stage 5 · Implementation · cloud tunnel + connectivity probe (5.1)
- **Output:** `infra/connectivity.py` `probe_opponent` (harmless `list_tools` via
  FastMCP Client — in-memory or URL); authored `docs/PRD_cloud_tunnel.md`
  (Host-header HTTP-421 fix at the tunnel, not in code); `test_connectivity` (2).
  Cov 98%. **Closes Stage 5.**
- **Lesson:** the tunnel Host-header fix is config-only (Cloudflare
  `httpHostHeader` / ngrok `--host-header=rewrite`); FastMCP's DNS-rebinding check
  is never weakened. The probe is testable in-memory (reachable) + refused-URL.

## 2026-07-23 · Stage 6 · Implementation · sysinfo + Step-0 record (6.1)
- **Output:** `shared/sysinfo.py` `collect_spec` (portable, cached, stdlib-only —
  unknown values stay 'unknown'); `orchestration/sealing.sealed_spec_record`
  (Step-0 host-spec sealed record) wired into `PeerRuntime.records[0]` + identity
  `spec`; authored `PRD_commit_reveal`; `test_sysinfo` (3). Cov 98%.
- **Lesson:** the Step-0 record is sealed like any step and re-verified in the
  mutual audit; the integration match still audits clean with it prepended.

## 2026-07-23 · Stage 6 · Review/Audit · adversarial audit (6.2)
- **Output:** `tests/integration/test_audit.py` (3): a valid opponent log settles
  normally; a tampered record (flipped position → stale commit) forces
  `tamper_forfeit` for the honest peer (`failed_steps == [1]`); a missing opponent
  audit skips (no forfeit). Cov 99% on `finish`. FR-14 DONE.
- **Lesson:** tamper_forfeit is board-independent — the honest peer wins by
  technical decision regardless of the survival/capture result.

## 2026-07-23 · Stage 6 · Implementation · report consensus signature (6.3)
- **Output:** `reporting/report_writer.py` (`consensus_signature` SPACED form,
  `sign_report` sign-then-insert under `חתימת_קונסנזוס_משותפת`, `verify_report`);
  conformance `test_report_consensus_vectors`; `test_report_writer` (4); authored
  `PRD_interop_serialization`. Cov 99%. **ALL 6 CORE surfaces now pass.** Closes Stage 6.
- **Lesson:** the report signature is the deliberate 2nd (spaced) serializer; the
  vector's `compact_form_sha256` proves the compact form would fail settlement.

## 2026-07-24 · Stage 7 · Implementation · four JSON artifact builders (7.1)
- **Output:** `reporting/{artifact_schemas,artifact_helpers,artifacts}.py` — pure
  `build_{declaration,config_artifact,log,result}` (all share one `game_uid`,
  cross-link via `links`); `config_sha256` = compact-canonical lock over terms;
  `log`/`result` `mutual_agreement.sha256` = SPACED `consensus_signature`;
  declaration group blocks self-signed with the six book hardware fields. Authored
  `PRD_logging_audit_reporting` (AC-R1..R7); `test_artifacts` (6). Cov 98%.
- **Lesson:** the two locks use different serializers on purpose — `config_sha256`
  compact (App-F byte-identity), `mutual_agreement` spaced (report consensus) — so
  the pure builders reuse the exact CORE-vector functions and can't drift.

## 2026-07-25 · Stage 7 · Implementation · artifact emit-to-disk + SDK wiring (7.2)
- **Output:** `reporting/emit.py` `emit_series` — writes declaration + result +
  per-sub-game config/log into `<logs_dir>/<group_id>/`, deriving per-group scores
  from `domain.scoring`; wired into `SimulationSdk.run_peer` (emits under workdir,
  returns `report`+`artifacts_dir`). `test_emit` (3) + `test_series` now asserts 4
  files on disk and cross-peer mutual-signature agreement. Cov 98.55%.
- **Lesson:** the mutual signature must hash ONLY the symmetric outcome
  (roles/result/score/aggregate) — never per-peer tokens or wall-clock timestamps —
  so both peers, seeing mirrored roles, still produce byte-identical `sha256`.

## 2026-07-25 · Stage 7 · Implementation · official emailed report body (7.3a)
- **Context:** studying SPEC §5/§6 + the kit revealed TWO surfaces — the cross-peer
  consensus SIGNATURE (spaced, Hebrew key; done 6.3) vs. the EMAILED report body.
  Per §36 the v3.0.0 reference is ground truth: each team emails its own rich Hebrew
  `build_report`, self-signed; the body must be exact hashed canonical bytes.
- **Output:** `reporting/report_builder.py` — `build_report(summary, terms)` (book
  ch.8 Hebrew schema, spec/token declaration from the sealed step-0 record,
  sign-then-insert) + `report_body` (spaced canonical, never indent=2). Authored
  `PRD_email_reporting` (AC-E1..E6). `test_report_builder` (5). Cov 98.56%.
- **Lesson:** the emailed body reuses the SPACED consensus serializer (not compact),
  keeps Hebrew literal (`ensure_ascii=False`), and a re-serialized/pretty email
  nearly scored 0 in EX06 — so `report_body` returns the exact preimage-form bytes.

## 2026-07-29 · Stage 7 · Implementation · Gmail send-only (raw-HTTPS) (7.3b)
- **Goal (owner):** portable Gmail send-only OAuth, raw HTTPS, no new deps.
- **Output:** `infra/gmail_client.py` (stdlib urllib/base64/email: refresh token →
  create draft/send; injectable `http`; `credentials_from_dicts`) + `infra/
  email_sender.py` (disabled/draft-default gates, gatekeeper-routed, structured
  result, creds from git-ignored `secrets/` via env). `test_gmail_client` (3) +
  `test_email_sender` (5, FakeHttp — never sends). Cov 98.28%.
- **Lesson:** injecting the `http` callable makes the whole OAuth+Gmail path
  offline-testable (token refresh, draft vs send URL, retry-then-give-up) with zero
  network and zero credentials; `build_raw` MIME round-trips to the exact body bytes.

## 2026-08-04 · Stage 7 · Implementation · live-GUI view-model (7.4a)
- **Output:** `gui/game_mode.py` (`mode_and_model` / `mode_from_recorded_model`,
  Table-22 verbal-mode labels) + `gui/live_apply.py` (`apply_event(state, event)`
  dispatching runtime events onto a window protocol; `LiveState` clock). Authored
  `PRD_gui_replay` (event schema + local-truth contract). `test_game_mode` (5) +
  `test_live_apply` (7, FakeWindow — no Tk). Cov 98.28% (gui coverage-omitted).
- **Lesson:** the local-truth boundary is STRUCTURAL, not a display convention —
  `test_live_apply` asserts the runtime snapshot key-set carries no opponent
  position/role, so the live board cannot leak truth even by mistake. Splitting the
  pure view-model from the Tk shell keeps the graded invariant fully unit-tested.

## 2026-08-05 · Stage 7 · Implementation · runtime live event stream (7.4b)
- **Output:** `orchestration/runtime.py` now emits `moved` (after each sealed send)
  and `game_over` (after `finish`) listener events, completing the live stream the
  GUI consumes. Additive — listener defaults to no-op, so headless runs/tests are
  unchanged. `test_runtime` gains an event-stream test (ordered
  negotiated→moved…→game_over; no `moved` view carries opponent truth). Cov 98.29%.
- **Lesson:** emitting the stream in the orchestration layer (tested) BEFORE the Tk
  shell (7.4c, coverage-omit) keeps the local-truth boundary and event ordering
  under real integration test, not just synthetic-event unit tests. runtime.py is
  now 141 code lines — near the 150 cap; the next runtime change may need a split.

## 2026-08-05 · Stage 7 · Implementation · live Tk shell (7.4c)
- **Output:** `gui/board_view.py` (canvas: my truth + barriers + visited + belief
  heatmap; cell_px injected from config), `gui/window.py` (PeerWindow chrome +
  window protocol), `gui/player.py` (LivePeerApp: threads `sdk.run_peer`, queues
  events, drains via the 7.4a view-model), `gui/__main__.py`
  (`python -m cop_thief_core.gui`). Display-guarded `test_gui_shell` (2). Cov 98.29%.
- **Lesson:** `DISPLAY=:0` (WSLg) is present here, so the smoke test builds a REAL
  window and asserts labels/board — but it `pytest.importorskip`s tkinter and skips
  on `TclError`, so headless CI stays green. No PIL/scrot for a PNG, so the committed
  screenshot is an honest owner manual step; I verified the full LivePeerApp renders
  end-to-end (board exported to PostScript) rather than fabricating an image.

## 2026-08-05 · Stage 7 · Implementation · replay data layer (7.5a)
- **Output:** `gui/replay_data.py` — `verify_record` (commit-reveal re-verification →
  OK/TAMPERED via our production `hashing.verify`), `reconstruct_positions` (my
  trajectory from sealed records, step-0 spec skipped), `opponent_positions` (the
  OPPONENT's trajectory from its sibling revealed log), `normalize_log`,
  `discover_subgames`, `subgame_log_path`. `test_replay_data` (5) +
  `test_replay_normalize` (4), tests seal real records then tamper one. Cov 98.29%.
- **Lesson:** full opponent truth is reconstructed ONLY in replay, ONLY from the
  mutually-revealed sibling log under `logs/<opponent_group_id>/` — the same emit
  layout 7.2 wrote. Re-verifying with the SAME production `verify` the live audit
  uses means the replay can't "pass" a log the audit would reject.

## 2026-08-05 · Stage 7 · Implementation · replay Tk viewer (7.5b)
- **Output:** `gui/replay.py` (`ReplayApp`: play/pause/step/restart; draws both
  revealed trajectories on one board; `barriers_from_state` parses the sealed state
  string; per-step commit verify status) + `--replay` in `gui/__main__.py`.
  `test_replay_view` (3: pure barrier-parse always runs; display-guarded ReplayApp
  smoke × 2). Verified ReplayApp on a REAL emitted 34-step log. Cov 98.29%.
- **Lesson:** our standardized log is leaner than the reference's (no received-smell
  history), so replay honestly shows both trajectories + visited + parsed barriers +
  commit integrity with a FLAT belief field, rather than faking a heatmap it has no
  data for. The opponent overlay needs both sibling logs colocated (2-machine games
  keep only their own until gathered) — documented, not silently empty.
