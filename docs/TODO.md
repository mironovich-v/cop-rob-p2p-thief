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

**Progress:** Stages -1 → 7 all ✅ (engineering complete). Base logic, MCP infra +
orchestration, strategy/belief, language/scent, cloud probe, commit-reveal security,
and the full reporting shell (four artifacts, emailed report, Gmail draft, live GUI,
replay, two-repo export) are done. Two-peer distributed match runs end-to-end
(verified through a full **6-sub-game series**); **all 6/6 CORE vectors pass**; 225
tests, 98.32% coverage. **RTS: engineering complete (13/17 AC); full submission
awaits owner actions — see `docs/PROGRESS.md`.**

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
| [x] | 7.7c | RTS gate review (AC1–AC17) + PROGRESS owner checklist | `docs/PRD.md`, `docs/PROGRESS.md` | docs | — | manual submission checklist |

## Post-engineering dev follow-ups (AC-hardening)

| Done | Task | Scope | Key files | ~LOC | AC | Tests |
|------|------|-------|-----------|------|-----|-------|
| [x] | 7.8 | strict step-monotonic dedup (stale/duplicate/out-of-order); fix caught-branch step advance | `orchestration/{turn_handler,runtime}.py` | ~10 | AC7 | `test_turn_handler`, `test_runtime` (dup) |
| [x] | 7.9 | CI workflow: full gate (ruff, pytest+cov incl. conformance vs fetched kit, kit oracle, `gen_vectors` drift check) | `.github/workflows/gate.yml` | ~35 yaml | AC1 | CI run on this PR |

## Stage 8 — League-Kit Resync (kit HEAD `ad65576`, re-read 2026-08-17)
Exit: conformant against the updated `copthief-league-protocol` — all three
capture families played and corroborated, delivery/audit hardened to the
PROMOTED tables, §6.2 graded league fields emitted, negotiate declarative,
email gate rule-30-conformant, new-vector conformance green. Context: the kit
gained a real cross-team campaign (two counted series, six audit passes, four
best2934 WARNINGS); our 6 CORE vectors still pass and our 5-key consensus
scope already matches kit #55 — the gaps are behavioral, not byte-level.

| Done | Task | Scope | Key files | ~LOC | Tests |
|------|------|-------|-----------|------|-------|
| [ ] | D8 | plan + ADR-17..20 + email-PRD update (this PR) | docs only | docs | — |
| [x] | 8.1 | rule-46/47 endings: thief detects barrier-on-own-cell + boxed-in (STAY doesn't rescue) and SENDS the concession final `claim_response={claim:[own cell],caught:true}`; cop settles CAPTURE on any thief `caught:true` (existing caught-branch — zero runtime changes) | `domain/rules.py`, `orchestration/turn_handler.py` | ~35 src | `test_rules`, `test_turn_handler`, `test_enclosure` (2-peer cornering) |
| [x] | 8.2 | capture corroboration at audit: answer (cell = revealed trail end) vs concession (cell captured under cop's OWN barrier record); failure → `disputed_capture` (winner null, tie false, 0/0), never counted clean; strict-parse-or-degrade | `orchestration/{audit_checks (new),summary}.py`, `constants.py`, `reporting/emit.py` | ~70 src | `test_audit_checks` (10), `test_enclosure` |
| [x] | 8.3 | delivery-contract upgrade: dedup on COMMIT (`{step: commit}`), same-step-different-commit → loud equivocation (evidence recorded, settles tamper_forfeit), reorder window 1 (buffer + in-order replay; past window → technical_loss), below-next discard, deadline checked every lap and never renewed by tolerated junk | `orchestration/{turn_handler,runtime}.py`, `constants.py` | ~60 src | `test_turn_handler` (delivery table), `test_runtime` (junk flood) |
| [x] | 8.4 | audit live-binding: disclosed commit == commit that ARRIVED per step + completeness (every received step disclosed), then re-hash; step-0 spec self-verified only; `bound_steps` in the audit record proves the binding ran live | `interop/hashing.py`, `orchestration/{turn_handler,summary}.py` | ~25 src | `test_interop_primitives` (5), `test_audit` (reseal caught / bound pass) |
| [x] | 8.5 | negotiate extras: declare `role`/`sub_game_number`/`game_uid` + locked-model hashes BESIDE terms; `identity.counted_games_played` (exact key — imreeyal §3.8); truth tables (refuse only both-declared-and-differ; omission/uncomparable → play); expected-opponent-group guard; push-first + accept agreement from response body OR inbound push (WARNINGS §2b); registry docs vendored + hash-drift conformance test | `interop/{extras,locked_models,negotiation}.py` (+data json), `orchestration/{handshake,sealing,runtime}.py`, `infra/mcp_client.py` | ~120 src | `test_extras` (11), `test_handshake` (+5), conformance registry test |
| [x] | 8.6 | wire value validation before any state change: `validate_turn_values` (empty timestamp, non-lowercase-64-hex commit, string smell intensities, negative/bool step, invalid sender) + `TurnHandler.receive()` refusal path (never defaulted, never a crash; unknown keys tolerated) | `protocol/messages.py`, `orchestration/{turn_handler,runtime}.py` | ~45 src | `test_protocol` (refusal rows), `test_turn_handler` (receive) |
| [x] | 8.7 | §6.2 league fields (`games_played_including_this` null=unclaimed never 0, `first_meeting_between_groups`, `diversity_reward_applied` derived winner-true — +10 never in totals; friendlies truthful-but-disarmed) + `links.github` both teams (rule 49) + committed rule-52 ledger (`results/rule52_ledger.json`, tracked; advanced in the counted settlement path) | `reporting/{league (new),emit,artifacts,artifact_helpers}.py`, `.gitignore` | ~65 src | `test_league` (5), `test_emit` (+2) |
| [x] | 8.8 | email shape + gate: result JSON as body AND same file as single named attachment (byte-identical); reference subject form; auto-fire at settlement (rule 32); draft mode REMOVED (send-only scope, ADR-20) → `dry_run` default; structural recipient gate (lecturer unreachable unless doubly-armed `game.counted` + `--counted`; arming mismatch refuses; armed-but-undeliverable refuses to start) | `infra/{email_sender,gmail_client}.py`, `sdk/sdk.py`, `agent_cli.py`, tomls | ~110 src | `test_email_sender` (10), `test_gmail_client` (+1), `test_email_wiring` (3) |
| [x] | 8.9 | behavior-table conformance: every `delivery_contract` arrival row, every `turn_message` validation row, every `pairing_declaration`/`uid_declaration` truth-table row answered by OUR production code; `game_id` asserted in the uid vector; kit oracle 125/125 + zero drift (`locked_model` registry pinned since 8.5) | `tests/conformance/test_behavior_tables.py` (new) | ~75 (tests) | 4 table suites + kit `verify_vectors.py` |
| [x] | 8.10 | MCP session lifecycle (imreeyal §3.4/3.16): fresh Client per call (no session survives a boundary — documented); handshake patience 150s spans the inter-sub-game door gap; greeting RE-pushed every 5s until the game starts; arriving negotiate opens the sub-game; role guard bound at runtime construction (pre-handshake, structural) | `infra/mcp_client.py`, `config/*/game.toml` | ~40 src | `test_mcp_client` (repush, down-door patience) |
| [x] | 8.11 | per-call timeout cap 10s strictly < signed `response_timeout_sec` 30 (imreeyal §3.5); ConfigManager refuses to load a violating config | `infra/mcp_client.py`, `shared/config.py` | ~20 src | `test_mcp_client` (hung call capped), `test_config` (refusal) |

| [x] | 8.12 | imreeyal pairing readiness: `config/imreeyal/` (their constitution byte-identical, `agreed_between ["imreeyal","vm__fabi"]`, num_games 6; group_id `vm__fabi`, opponent guard, ngrok servers, friendly auto-fire recipients, tie_rule declared); real member names in all configs (OD-2); reply draft + derived ids (`imreeyal-vs-vm__fabi` / `0e07bcda-4bfd-3668-1fec-86833963b58c`) | `config/imreeyal/*`, `config/{police,thief}/game.toml`, `docs/pairing/` | config+docs | `test_config` (pairing pin) |

| [x] | 8.13 | §0 sparring pass (imreeyal's checklist): full 6-sub-game series vs the kit sparring peer — 6/6 settled, all mutual audits OK both ways, one game_uid; `check_artifacts` per-dir ALL PASS + cross-team join ALL SETS AGREE; found+fixed: declaration builder crashed on a foreign identity without `spec` | `reporting/artifact_helpers.py` + throwaway config (scratchpad) | ~15 src | `test_artifacts` regression; live sparring run |

| [x] | 8.14 | nis-yar1 pairing readiness: role-split opponent support (`set_opponent` + per-sub-game dial of their fixed-role processes), `config/nis-yar1/` (constitution byte-identical — terms digest `a284082d…` confirmed both ways; ids pinned: `nis-yar1-vs-vm__fabi` / `b38f33f3-3ec8-be1d-a464-4fa5c9cb35df`), reply draft + league first-contact template | `infra/mcp_client.py`, `sdk/series.py`, `config/nis-yar1/*`, `docs/pairing/` | ~30 src | `test_mcp_client` (swap), `test_config` (pin) |

| [x] | 8.15 | .env loader (stdlib, ~12 lines): `agent_cli.load_dotenv` sets Gmail secret paths unless the shell already exported them (shell wins) — pre-window catch: nothing loaded `.env`, so the auto-fired friendly report would have stranded as `no_credentials`; live token-refresh preflight passed | `agent_cli.py`, local `.env` (untracked) | ~12 src | `test_dotenv` (2); live OAuth refresh |

| [x] | 8.16 | tactical brains v2 (counted-game forensics: v1 thief argmaxed distance → self-cornered at (6,6) every game; v1 police walled randomly): freedom-dominant thief scoring (exits veto corners, pessimistic distance, recent-trail anti-oscillation, random tie-breaks — a deterministic evader is pin-able), cornering police (rule-46 barrier strike / pocket sealing, never random walls); tunables in `[strategy.tactics]`; A/B: thief 0/5→3-4/5 survival, cop corners the kit's "uncatchable" greedy evader 3/3 — kit sparring series 0-6 → 3-3 (75-75) | `domain/{tactics (new),brains}.py`, `strategy/__init__.py` | ~100 src | `test_tactics` (9), `test_brains` updated; A/B + sparring benchmark |

| [x] | 8.17 | capture corroboration degrades on an unreadable final (live il-nv-ai warm-up crash, 2026-08-21): their thief's `caught: true` final omits `claim` — SPEC §3.1 mandates the key, but our `corroborate_capture` indexed it unguarded and raised `KeyError` inside `finish()`, killing the peer AFTER a fully played sub-game (no artifacts emitted, whole game lost). Strict `_parsed_cell` (2-int sequence, `bool` excluded) → `kind: "unknown"` + degraded note; a malformed cell like `[3]` previously reached board math and raised `IndexError` too. Missing evidence is not proof of a lie: degrade, never accuse, never crash | `orchestration/audit_checks.py` | ~15 src | `test_audit_checks` (claimless final, 6 malformed shapes) |

| [x] | 8.18 | played-match evidence committed: `logs/*`+`results/*` were fully ignored, so no played game was in git (not even the counted nis-yar1 series). 170 artifact files force-added as deliberate SNAPSHOTS — ignore rules unchanged so routine runs stay out, next series added explicitly; `results/README.md` documents provenance, inter- vs intra-group split, and the il-nv-ai degraded-corroboration note | `results/README.md`, `.gitignore`, `logs/**`, `results/**` | artifacts (counted separately) | secret scan + no-absolute-path scan on all 170 |

| [x] | 8.19 | final audit ack survives shutdown: the MCP server thread is `daemon=True`, so exiting the instant the runtime drained the audit inbox killed it mid-response — the opponent's `submit_audit` was received and acted on while THEY logged `audit_send_unacknowledged` (il-nv-ai, both runs 2026-08-21). Reproduced out-of-tree: no-ack at exactly 15.00s vs ack in 0.22s with a linger. `network.shutdown_grace_seconds` (5.0, all five peer configs) + `_linger_for_final_ack`; an injected transport owns no server and never waits | `sdk/sdk.py`, `config/*/game.toml` | ~15 src | `test_series` (owned-server lingers, injected does not) |

| [x] | 8.20 | thief reads the cop's DECLARED cell: the police sets `capture_claim` to its own position every move, and we used it only to answer "am I caught" — the thief fled scent, which marks where the cop WAS (measured: believed threat correct on 3/14 turns, lagging 2-3 steps). New `ClaimTracker` trusts a claim only while claims walk like a cop (reachable within elapsed steps; first claim anchors only, refusal re-anchors) + `BeliefGrid.observe_declared`. Diagnosis order mattered: a `HerderCop` bench first REPRODUCED the live loss (1/10, median 10 steps = the live capture step), then an oracle run proved scoring was innocent and belief guilty (a territory-scoring candidate was 0/10 and was discarded). After: vs herder 1/10 -> 11/24 with every game reaching step 35; vs our police 5/10 -> 8/10 = oracle parity | `domain/claim_tracker.py` (new), `domain/belief.py`, `orchestration/turn_handler.py` | ~40 src | `test_claim_tracker` (7), `test_thief_belief_claims` (2); 24-seed bench |

| [x] | 8.21 | police herds instead of chasing: oracle test FIRST proved information was not the limit (true-cell cop captured 2/16 vs blind 3/16 — so the never-called `BeliefGrid.exclude` channel would have bought nothing). A pursuer cannot close on an equally fast evader by chasing, so the step now minimises the thief's reachable `territory` (BFS both sides, cells the thief reaches first); rule-46 strike / pocket-seal barrier logic unchanged. Captures 3/16 -> 8/16 vs our strengthened thief. NOTE the reversal: re-running the oracle AFTER this gives 16/16 in a median 13 steps, so police BELIEF is now worth improving where an hour earlier it measured as worthless | `domain/tactics.py`, `domain/brains.py` | ~30 src | `test_territory` (5); 16-seed bench |

| [x] | 8.22 | read the scent map's PEAK as the sender's exact cell: a peer deposits on the cell it stands on just before sending, so the map maximum IS that cell — probed 35/35 correct, while the belief grid the same map produced was 0/35. `peak_cell` (strict parse; a sparse/foreign map yields no sighting rather than a guessed one) + the walks-like-a-peer trust check + collapse. Police captures 8/16 -> 16/16, median 10 steps, beating the oracle's 13. ASYMMETRY: favours the pursuer — the thief already had the cop's cell from `capture_claim` on every cop move, so it gains only barrier turns; our thief's bench numbers fell only because the BENCH's cops got the same upgrade | `domain/claim_tracker.py`, `orchestration/turn_handler.py` | ~30 src | `test_scent_peak` (4); 16-seed bench |

| [x] | 8.23 | author the four stub PRDs (mandatory per guideline §1.3 / checklist §34 — a dedicated PRD per algorithm): `PRD_strategy_brains`, `PRD_belief_map`, `PRD_pheromone_scent`, `PRD_llm_verbal_layer`, all four previously 4-line placeholders. Written to the house five-section shape and recording the EVIDENCE from today's rewrite (peak-vs-truth 35/35 vs belief 0/35; thief 1/10 -> 11/24; police 3/16 -> 8/16 -> 16/16) plus the rejected alternatives (territory-thief 0/10; `BeliefGrid.exclude` measured worthless while the tactics were wrong). Cited test names fact-checked against the tree. **Zero PRD stubs remain** | `docs/PRD_{strategy_brains,belief_map,pheromone_scent,llm_verbal_layer}.md` | docs (~370 lines) | N/A — documentation |

| [x] | 8.24 | persist the opponent's applied turns: `records` are what WE sealed, so a settled game could not be re-examined from our own archive — when il-nv-ai's final arrived without a `claim` key there was no way to check their claim semantics across the game. Added `received_messages` to the log artifact. Risk checked FIRST: the per-sub-game signature is `consensus_signature(records)` (records alone) and the series one is over a symmetric aggregate, so a new key cannot move a shared hash — pinned by a regression test. Verified live (10 messages filed with `capture_claim` + `smell_grid`), cost ~20 KB per 35-step game | `reporting/artifacts.py`, `reporting/artifact_schemas.py` | ~10 src | `test_artifacts` (3, incl. hash-invariance guard) |

| [x] | 8.25 | vibecode pairing readiness (Ron Marom, Amit Kuperminz): `config/vibecode/` with the constitution relabeled `agreed_between` ["vibecode","vm__fabi"] (terms digest reproduces their `a284082d…`), ids pinned `vibecode-vs-vm__fabi` / `6268e7d5-3ece-cb39-e25b-767cc8c3e735`, num_games 6 for BOTH friendly and counted. PARITY FLIPPED to their option (a) — vm__fabi POLICE on odd 1/3/5, opposite the alphabetical default, so launch `police_agent`; costs no code since `role_for` takes the natural role from the entry point. Role-split dial to their two STATIC doors (police 61224 / thief 61223 — no quick tunnel, URLs stable). Their scent-precision question answered from code: full-precision floats pass `validate_turn_values`, `absorb`, `observe_smell` and `peak_cell` — 3 decimals describes our writer, not our reader | `config/vibecode/*` | config | `test_config` (pairing pin); float-shape probe |

| [x] | 8.26 | rule-35 filing guard (vibecode counted-runbook parity): an ARMED run withholds its report unless every signed sub-game settled AND every audit verified — previously a crash filed nothing, but 6/6 settled with one FAILED audit would still have been filed, manufacturing exactly the contradictory-report shape rule 35 zeroes. `sdk/filing.filable` names the offending sub-game so the operator knows which log to compare. Deliberate boundaries, both tested at the real send path: friendlies still fire (a partner gate needs a friendly report at settlement) and a disputed capture still files (its crypto audit passed; SPEC §3.1 — "reported, never a unilateral rewrite") | `sdk/filing.py` (new), `sdk/sdk.py` | ~35 src | `test_filing_guard` (8: predicate + wiring) |

| [x] | 8.29 | report the playing commit AND verify it is reachable: our artifacts carried no commit at all (the wire identity declared one that never reached a submitted file), so a grader with only the two role repos could not tie a result to code. `github_commit` now rides the declaration group block and every result sub-game row. Checked FIRST that `_symmetric` scopes the consensus signature to five keys, so the new field cannot move a hash partners compare — pinned by regression test. An ARMED run additionally refuses unless the commit is reachable from `workspace-history` in every configured role repo (undecidable counts as unpublished; friendlies never blocked). Caught a real drift on first live run: main `6d090e2` vs mirrors `c7dce1f` | `shared/provenance.py` (new), `reporting/{emit,artifact_helpers}.py`, `sdk/sdk.py` | ~90 src | `test_provenance` (8), `test_emit` (2 incl. consensus-invariance) |

| [x] | 8.30 | republishing the submission repos becomes step 10 of the git loop: they are GENERATED exports that do not track main, so every merge silently strands the commit we declare on the wire (drifted 11 PRs once, then twice more today). `scripts/publish_submissions.sh` exports, pushes each role tree to its `main`, mirrors workspace main onto `workspace-history` in both, verifies the playing commit resolves and exits non-zero if not; refuses a dirty tree. Three layers now: the script does it, step 10 remembers it, the armed-run gate catches it | `scripts/publish_submissions.sh` (new), `CLAUDE.md` §2.9/§11 | ~55 | exercised live: both mirrors -> c0aa29a, gate green |

| [x] | 8.32 | answer from the BOOK whether each role must be RUN from its own repo (owner asked for an honest, cited answer). Re-read `police_thief_p2p.pdf` directly — 160pp, Hebrew visual-order reversed per line. **No such rule.** Binding rule 1 (sanction *total failure*) mandates separate **processes** under separate config dirs; rule 2 forbids shared memory/variables, narrowed by §2.4.2 p31 to *"a shared module that holds live state"*; rule 49 says **submit** two cross-linked repos; rule 50 lists their contents "to let the examiner reconstruct the way of working". Honest divergence recorded: ch. 9.4 p96 *describes* development as happening in two repos while we develop in one core and generate two — motivated by the guideline's ban on duplicated modules, the interop risk, and the lecturer's own mono-repo reference; mitigated by the `workspace-history` mirror in both repos | `README.md` (cited compliance section, exports into BOTH submission repos), `docs/decisions.md` (ADR-24) | docs | citations verified against the PDF |

| [x] | 8.33 | il-nv-ai counted-series config: num_games 1 -> 6 (terms `a284082d…` and uid `566d2396-…` both reproduce and match theirs), counted_games_played 1 -> 2 so an armed run declares 3, and the header rewritten because ROLE PARITY INVERTS versus the warm-up — `kit_sorted_first_police_odd_v1` puts il-nv-ai police on odd, so we launch `thief_agent`, never police_agent. Tie behaviour verified against book Table 18: a level series settles 67-67 (65 + the 2-point award). OPEN: their game.json is schema 1.2/911B/`034a0687…` vs our 1.3/1302B/`c5f1f11b…` — signed terms agree, file does not, adopt their bytes before playing; and their compare-then-send rule-35 protocol conflicts with our auto-fired mail | `config/il-nv-ai/{game.json,game.toml}` | config | terms/uid/tie/counters verified in code |

| [x] | 8.34 | export the evidence a grader was written for: the export copied a HAND-LISTED subset of `results/` (ledger + `counted/`), so `results/README.md` and `results/played_commits.md` — the two documents written for someone holding only a submission repo — never shipped into one. Now driven by `git ls-files`, so anything deliberately tracked publishes and untracked scratch copies still do not; 3 result files -> 69. Also fixed `test_il_nv_ai_pairing_config_is_playable`, which pinned the warm-up uid that the num_games 1 -> 6 change correctly moved — a gate the previous commit body claimed passing without re-running it | `scripts/export_repos.py`, `tests/unit/test_config.py` | ~25 | 382 passed; export re-verified (both grader docs present, scratch copies absent) |

| [x] | 8.35 | the evidence was never reaching the submission repos: the export copies the workspace `.gitignore`, which hides `results/*`, so `git add -A` in the export tree silently skipped every artifact — the published repos held only `.gitkeep` and the ledger, through every republish today. #90 fixed what the EXPORT writes into `dist/` and I verified `dist/`; the PUBLISH dropped them one step later, so verifying the intermediate artifact was not verifying the deliverable. Fix: `git add -f results` (matching what the workspace does for the same files) and print the published results-file count on every run so a silent drop cannot recur unseen | `scripts/publish_submissions.sh` | ~10 | verified by listing `results/` in the PUBLISHED tree, not the local one |

| [x] | 8.36 | deferred report send for compare-then-send partners (il-nv-ai rule-35 ordering: exchange the six per-sub-game hashes and the series hash BEFORE anyone mails; our peer auto-fires at settlement, the opposite order). `scripts/send_filed_report.py` sends an already-filed artifact's BYTES VERBATIM (artifact and auto-send body are the same `json.dumps(indent=2)` call, so no re-serialisation question — ADR-21) and re-applies `filable_report`, the same 6/6 rule, so it cannot bypass the guard. Prints the Gmail message-id, closing the gap the vibecode counted exposed. Subject role derived from the last sub-game's roles, as the auto-send does | `scripts/send_filed_report.py` (new), `sdk/filing.py`, `CLAUDE.md` §11 | ~90 | `test_filing_guard` (3 added, 11 total); verified live on real artifacts, refusal exits 1 |

| [x] | 8.37 | numeric hardware declaration: we emitted `"cpu_freq_mhz": "unknown"` / `"vram_gb": "unknown"`, which il-nv-ai's declaration validator refuses — a quantity is not prose, and as sent our declaration could not be loaded at all. `/proc/cpuinfo` gives 2918.4 MHz (WSL2 exposes no cpufreq sysfs and lscpu prints no max-MHz row), absence is 0, and an absent GPU is declared `"none"` rather than claiming ignorance about a device we deliberately do not subprocess-probe. Fixed at the source so the ARTIFACTS carry numbers, not just the message we paste | `shared/sysinfo.py` | ~25 src | `test_sysinfo` (4 added, 7 total) |

| [x] | 8.38 | adopt il-nv-ai's constitution — and find that it omits a SIGNED term. Their 911-byte schema-1.2 file reproduces `034a0687…` exactly, but its `pheromones` block lacks `pheromone_min_center_intensity`, one of the 14 signed terms, so our loader refuses it and the file cannot reproduce the terms hash they themselves cite. Proved the internal default instead of asking them to guess: their file + `"pheromone_min_center_intensity": 0.5` = 948 bytes, sha256 `b9c20e38…`, reproducing BOTH declared values (terms `a284082d…`, uid `566d2396-…`). Kept the working file so the repo stays playable; they must adopt the 948-byte version for the configs to be byte-identical | `config/il-nv-ai/{game.json,game.toml}` | config | 389 passed; hashes verified both ways |

| [x] | 8.39 | evader reach-avoidance: the thief had no notion of REACH and would step into a cell the cop occupies next turn — both peers move each round, so the pursuer's cell and all its neighbours are forbidden. `beyond_reach` becomes the first sort key, the existing freedom/distance score the second, degrading to score-only when every cell is reachable so a cornered thief still plays its best. Median survival against our OWN cop (the strongest pursuer we have) 10 -> 12 steps; four more elaborate designs (roomy / central / parity-locking) measured no better than this one rule. Cop unaffected (still 12/12). NOT shipped, all measured and documented: lagged-belief and tied-peak theories for the live cop failure (both disproved), a minimax cop (WORSE at 6/12), a staying cop (no effect), and a wall-squeeze (barriers sit adjacent to the POLICE, where a wall raises thief territory 9 -> 11) | `domain/tactics.py`, `domain/brains.py` | ~25 src | `test_thief_safety` (5); 12-seed sweeps |

| [x] | 8.40 | cop breaks a parity lock by STAYING: every move changes Manhattan distance by one, so an evader holding an EVEN distance before our move can never be landed on by a cop that always moves — and ours never used STAY, though it is in the agreed move set. Trigger needs THREE signals together (revisiting our own recent cells, flat best-territory, even distance) after a first version keyed on flat territory alone produced a false positive in an existing test. Validated on the RECORDED live game: fires at steps 10, 14, 18, 22, 26, 30 inside the 28-turn deadlock; bench unchanged at 12/12. Also settled by measurement and NOT shipped: a depth-8 and depth-12 memoised search evader reproduces the shipped one-ply result exactly (12 steps, 0/10), so the thief is at its practical ceiling | `domain/brains.py`, `domain/tactics.py` | ~40 src | `test_stall_break` (6); live-replay validation |

| [x] | 8.41 | Appendix B and the signed terms are DIFFERENT SCOPES — il-nv-ai were right. Verified against the PDF: the book defines exactly three `pheromone_*` keys and never mentions `min_center` anywhere, so an Appendix-B file legitimately omits it and their validator was right to refuse our 948-byte addition. The term belongs to the reference-v3 negotiation body (kit SPEC: `default 0.5`; pinned CORE game_uid vector carries 0.5). Our `terms_from_config` conflated the shared FILE with the negotiation BODY. `APP_B_OPTIONAL_TERMS` now fills min_center from the documented default when absent; an explicit value still wins and every other missing term is still refused. Their 911-byte file adopted VERBATIM (sha `034a0687…`), terms `a284082d…` and uid `566d2396-…` both still reproduce | `interop/negotiation.py`, `config/il-nv-ai/{game.json,game.toml}` | ~20 src | `test_appendix_b_scope` (5) |

| [x] | 8.42 | imreeyal pairing refresh before first play: the config was written 2026-08-18 and never exercised, and had two faults. `counted_games_played` still read 1 though we have banked TWO counted series since, so an armed run would have under-declared a graded field both teams publish. And only one of their two doors was configured — they run `cop.` and `thief.imreeyal.com`, we play POLICE on odd, so they are THIEF on odd and we must dial their thief door in 1/3/5; the single URL aimed at their cop door for the whole series, which would have failed mid-series rather than at the start | `config/imreeyal/game.toml` | config | 405 passed; dial map verified per role |

| [x] | 8.43 | filed `started_at` was the PEER LAUNCH, not the sub-game open: our imreeyal g1 reported 12:12:16Z against their correct 12:27:06Z — the fifteen minutes our peer spent holding in the handshake for their doors. `_started_monotonic` was already reset post-handshake so `duration_seconds` was right, but the wall-clock stamp never was, and `ended_at` derives from it, so both ends of every filed row were shifted earlier. The error GROWS with how long we courteously hold, and a counted report starting before the agreed T is a discrepancy an auditor may question. Caught by the two-implementation cross-diff, which neither side's tests could see | `orchestration/runtime.py` | ~12 src | `test_start_timestamp` (2) |

| [x] | 8.44 | il-nv-ai counted series BANKED (2026-08-24): 6/6 settled 14:06–14:11, all audits verified both ways, tie 47:47 (six thief survivals, series_add +2 each), uid `566d2396-…`, series consensus `381f268c…` byte-identical both directions, report = filed bytes mailed lecturer-only, message-id `1a0337c3d013aa7b` exchanged. Evidence force-added under `results/counted/il-nv-ai-2026-08-24/`; rule-52 ledger auto-advanced (il-nv-ai: 1). Window surfaced two defects for follow-up PRs: `preflight_armed` refuses the documented §11 held-mail arming, and `smell.min_center_intensity` is None at runtime when the constitution omits it (8.41's fill covers the terms scope only) — first move crashes; both were config-papered for the window on the declared commit | `results/counted/il-nv-ai-2026-08-24/` (15 files), `results/rule52_ledger.json`, docs | archive + docs | played on merged main c83d81e; consensus + audits verified live |

Dependencies: 8.2 needs 8.1; the rest are independent (8.9 lands with or after
its behaviors). ENH vectors (`joint_seed`, `derive_starts`) and `smell_binding`
are deliberately NOT implemented (opt-in / zero-implementation per kit
governance). Ops items (declare turn order + `tie_rule=series_add` at first
contact, playbook ladder) live in `docs/PROGRESS.md`, not code.

**Pairing deadline pressure (2026-08-17):** imreeyal proposes friendlies then
one counted series before the **20/08 deadline** — see
`docs/pairing/imreeyal_first_contact.md` (verbatim message + disposition map).
Priority order under the deadline: 8.1/8.2 (they audit enclosure captures) →
8.5 (their handshake expects the extras) → 8.10/8.11 (their runner's session
model) → 8.3/8.6/8.4 → 8.7/8.8 (report fields + auto-fire gate before the
qualifying friendly) → 8.9. Also: align `config` constitution to theirs
(setting "New York", starts, `agreed_between`) and run the kit sparring series
+ `check_artifacts` join (their §0).

## RTS gate
- [~] PRD §4 acceptance criteria (AC1–AC17): **engineering complete** — 14/17
  satisfied (AC7 closed); AC1 has a small CI dev follow-up (7.9); AC2/AC12/AC14 are
  owner runtime + submission actions (see `docs/PROGRESS.md`). Full RTS is declared
  once the owner checklist is done.

## Cross-cutting (continuous)
- [ ] Update `docs/requirements_matrix.md` status per merged slice.
- [ ] Update `docs/PROMPTS.md` + `COSTS.md` on **every** PR (standing rule).
- [ ] Keep `tests/conformance/` green against the fetched league kit; CI drift check.
- [ ] No-hardcode grep gate + secret scan on every PR.
- [ ] Update `docs/PRD.md` §14 Open Decisions whenever a decision is made.
