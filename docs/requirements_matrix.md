# Requirements Traceability Matrix

> Every requirement → its authoritative source → build stage → status → the test
> or evidence that verifies it. IDs match `docs/PRD.md`. Sources: **Book** =
> `instructions/police_thief_p2p.pdf` v3.0.0 (App. F = binding table); **SPEC** =
> `copthief-league-protocol/SPEC.md`; **Ref** = `../Game-P2P-Cop-Chase` v3.0.0;
> **Assign** = `instructions/assignment.md`; **Guide** =
> `instructions/software-project-guidelines.md`. Status: TODO / WIP / DONE.
> Confirmed constants/constructions are in `CLAUDE.md` §36.

## Functional requirements

| ID | Requirement | Source | Stage | Status | Test / evidence |
|----|-------------|--------|-------|--------|-----------------|
| FR-1 | Grid, orthogonal move set (+STAY), king opt-in, barriers block both | Book App.F; Ref `domain/board.py` | 1 | TODO | `tests/unit/test_board` — neighbors, distance metric, blocked step |
| FR-2 | Barriers police-only, adjacent, budget-capped (14 min) | Book App.F; Ref `own_state.py` | 1 | TODO | `test_own_state` — quota, illegal placement |
| FR-3 | Capture = coord overlap (own-state honest); survival at step≥max; technical otherwise | Book ch.3; Ref `rules.py` | 1 | TODO | `test_rules` — capture, survival threshold, terminal |
| FR-4 | Scoring 20/5/5/10, tie 2, series aggregation, diversity; totals derived | Book App.F; Ref `scoring.py` | 1 | TODO | `test_scoring` — score_subgame, aggregate, tie path |
| FR-5 | Separate public/private/inferred/audit-only state | Book ch.1,5; Assign §6.2 | 1 | TODO | `test_own_state`; integration no-leak assertion |
| FR-6 | FastMCP 4 tools; typed schemas; reject bad/stale/dup/out-of-order | Book ch.2; Ref `infra/mcp_*`, `protocol.py` | 2 | WIP (schemas 2.1 + 4-tool server/client 2.4; stale/dup/out-of-order routing 2.5) | `test_protocol`, `test_mcp_*`, `test_runtime` |
| FR-7 | Terms exchange, mutual signature, `game_uid`/`game_id`; refuse on mismatch | SPEC §4; Ref `negotiation.py`,`game_ids.py` | 2 | WIP (sign/verify/refuse/minimum-validation 2.3; handshake over transport + shared-id derivation 2.5a; live MCP run 2.5b) | `test_negotiation`, `test_handshake`, `game_uid.json` |
| FR-8 | Orchestrator FSM; idempotency, monotonic ids, timeouts, retries, watchdog, restart | Book ch.8; Ref `peer/runtime*` | 2/6 | WIP (turn loop + handshake + watchdog timeout + mutual audit/tamper_forfeit done 2.5b; series restart 2.6, control channel later) | `test_runtime` (2-peer match), `test_series` |
| FR-9 | Central gatekeeper; FIFO queue on overflow; transient retry | Book App.F; Guide §4; Ref `shared/gatekeeper.py` | 2 | WIP (impl done 2.2; wired per-service later) | `test_gatekeeper`, `test_rate_limiter` |
| FR-10 | Belief heatmap from scent, diffused per movement | Book ch.6; Ref `belief.py` | 3 | WIP (BeliefGrid done 3.1; wired into runtime 2.5) | `test_belief` — observe, diffuse, exclude, normalize |
| FR-11 | Legal-action set in code; strategy picks legal only; `BrainBase` seam | Book ch.6; Assign §6.5; Ref `brains.py` | 3 | WIP (brains + config-driven seam done 3.2; wired into runtime 2.5) | `test_brains`, `test_strategy` (injected brain) |
| FR-12 | Pheromone emission/decay/wire (subtractive_chebyshev_v1) | SPEC §5; Ref `smell.py` | 4 | WIP (SmellField done + `pheromone` vector passes 4.1; wired into runtime 2.5) | `test_smell`, `pheromone.json` vector |
| FR-13 | LLM only for hint; offline default; word-limit + deadline fallback; move pure Python | Book ch.6, Table 21; Ref `strategy/*` | 4 | DONE (template default + 4 providers + every_n_steps + deadline/parse fallback; move pure Python) | `test_trash_talk`, `test_llm_provider`, `test_brains` |
| FR-14 | Commit-reveal per step; nonce reveal; mutual audit; tamper→forfeit | SPEC §3; Ref `crypto.py`,`summary.py` | 6 | WIP (per-step + Step-0 sealing, mutual audit, tamper_forfeit, CORE vector done; adversarial audit test 6.2) | `commit_reveal.json`, `test_sysinfo`, `test_runtime` |
| FR-15 | One canonical JSON fn; 4 serializations; CORE vectors from our code | SPEC §2,§6; Assign §7 | 6 | WIP (canonical/commit/terms/game_uid pass 2.3a + pheromone 4.1; only report_consensus S6 remains) | `tests/conformance/*` vs `vectors/*` |
| FR-16 | Local + public-tunnel; Host-header; pre-match probe; no security weakening | SPEC App.D; Assign §10 | 5 | WIP (probe + Host-header/tunnel docs done 5.1; live cross-tunnel run is manual AC12) | `test_connectivity`; manual/live (AC12) |
| FR-17 | Sealed logs; mutual audit; replay integrity + reconstruction | Book ch.7; Ref `gui/replay*` | 7 | TODO | `test_replay_data`, `test_replay_normalize` |
| FR-18 | Four artifacts share one `game_uid`; correct filenames; config_sha256 | SPEC §4; Ref `report/artifacts.py` | 7 | TODO | `test_artifacts`, `test_series` (4 files) |
| FR-19 | Report consensus signature (spaced, sign-then-insert Hebrew key); email = exact bytes | SPEC §6; Ref `report_writer.py` | 7 | TODO | `test_report_writer`, `report_consensus.json` |
| FR-20 | Gmail send-only OAuth; draft default; fixed recipient | Book App.A; Ref `email_sender.py` | 7 | TODO | `test_email_sender` (mocked; never sends) |
| FR-21 | Live GUI shows only local truth; full truth only in replay | Book ch.7; Ref `gui/board_view.py` | 7 | TODO | `test_live_apply`; GUI screenshot evidence |
| FR-22 | Deterministic two-repo export; vendored core; cross-links; drift check | Assign §5,§11 | 7 | TODO | export smoke test; each export's own suite |

## Non-functional requirements

| ID | Requirement | Source | Status | Test / evidence |
|----|-------------|--------|--------|-----------------|
| NFR-1 | Determinism (domain/crypto/serialization pure) | Guide §5; Assign §6.1 | TODO | conformance + unit reproducibility |
| NFR-2 | Offline tests; unit ≤60s, integration ≤300s; mock externals | Guide §5; Assign §9 | TODO | CI timing; no live deps |
| NFR-3 | Coverage ≥85% | Guide §5.2 | TODO | `pytest --cov --cov-fail-under=85` |
| NFR-4 | Zero ruff; files ≤150 code lines | Guide §2.2,§6.1 | WIP | `ruff check`; line-count check |
| NFR-5 | `uv` only; pyproject + uv.lock | Guide §7.4 | DONE | `pyproject.toml`, `uv.lock` committed |
| NFR-6 | No hard-coded game/config params; `CFG`; never lower a minimum | Book App.F; CLAUDE §13 | TODO | grep gate; config-driven tests |
| NFR-7 | SDK architecture; role-agnostic single core; no logic in GUI/CLI | Guide §3; Assign §5 | WIP (SimulationSdk.run_peer single entry + role-agnostic PeerRuntime done 2.6; CLI/GUI delegate later) | `test_series` (SDK.run_peer) |
| NFR-8 | No secrets; `.env`/`secrets/`; HTTPS+token auth; revocation | Guide §6.4; Book ch.2 | WIP | secret scan; `.env-example` present |
| NFR-9 | Byte-exact interop on 6 CORE surfaces | SPEC §1 | TODO | `tests/conformance/*` |
| NFR-10 | PR size 50–200 (soft cap 300), one purpose | Guide §7.2.1 | WIP | PR review / commit body |
| NFR-11 | Version tracking + runtime compat check | Guide §7.1 | WIP | `shared/version.py`; config-version test |

## Acceptance criteria (Definition of Done — Assign §13)

| ID | Criterion | Status | Evidence |
|----|-----------|--------|----------|
| AC1 | CORE vectors reproduced by our code; zero kit drift | TODO | conformance suite + `gen_vectors` diff |
| AC2 | Separate processes/dirs; no shared truth | TODO | integration test; architecture review |
| AC3 | Local E2E finishes + audits clean; totals derived | TODO | `test_mcp_match` |
| AC4 | Public endpoint via tunnel; ≥1 cross-impl game settles byte-identically | TODO | live cross-team run log |
| AC5 | Emailed/draft bytes = agreed hashed bytes | TODO | `test_report_writer` + email byte check |
| AC6 | ENH off by default, negotiation-gated | TODO | negotiation tests |
| AC7 | GUI local-truth; replay integrity + reconstruction | TODO | GUI/replay tests + screenshots |
| AC8 | Both exports self-contained + traceable to core commit | TODO | export + drift check |
| AC9 | Coverage/ruff/≤150/uv/no-hardcode/no-secrets gates | WIP | CI gates |
| AC10 | README, PRDs, four artifacts, submission tag present in both repos | TODO | submission checklist |
