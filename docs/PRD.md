# PRD — Distributed Cop-Thief P2P Agent System (team vm__fabi)

> Master Product Requirements Document. Version 1.0 (Stage -1).
> Authority order: the Hebrew book (`instructions/police_thief_p2p.pdf`, v3.0.0)
> → the league SPEC/vectors (`copthief-league-protocol/`) for the listed interop
> surfaces → the lecturer's reference implementation (`../Game-P2P-Cop-Chase`,
> code v3.0.0) as the practical ground truth. Confirmed numeric parameters and
> byte-level constructions are pinned in `CLAUDE.md` §36; this PRD does not
> restate them but references them. Per-mechanism detail lives in the dedicated
> PRDs indexed in §11.

## 1. Overview & context

A fully **decentralized** two-player pursuit game. A **Police** peer and a
**Thief** peer each run as their own OS process, expose a **FastMCP** server, and
call the opponent's FastMCP server as a client. Positions are hidden; each peer
maintains only its **own** private truth and infers the opponent's location from
a decaying **pheromone/scent** field and free-language **hints** (which may lie).
Every move is sealed with **commit-reveal (SHA-256)**; at end of game both peers
**mutually audit** the revealed logs and settle on **byte-identical** results.
There is **no central server, referee, or shared board state**. The system must
interoperate with independently-implemented peers from other teams.

## 2. Problem statement & goals

Build a reliable distributed system (not a game simulation): two autonomous peers
that agree, play, audit, and settle byte-identically with *any* conformant peer.
Primary goals:

- **G1 — Interoperability:** pass all league CORE vectors from our own code; a
  cross-implementation game audits and settles with zero false tamper-forfeits.
- **G2 — Correctness & determinism:** a pure, exhaustively-tested domain layer;
  results **derived** from logged events, never trusted from claims.
- **G3 — Reliability:** safe behavior under malformed/stale/duplicate/out-of-order
  messages, timeouts, and network interruptions; the game loop never stalls.
- **G4 — Local-truth security:** no peer can access the opponent's private truth
  through imports, files, or shared memory; honesty enforced by audit.
- **G5 — Reproducible submission:** two self-contained repos generated from one
  canonical core; complete artifacts, GUI, replay, and Gmail reporting.
- **G6 — Professional quality:** SDK architecture, ≤150-line files, ≥85% coverage,
  zero ruff violations, `uv`-only, no hard-coded game parameters.

## 3. Stakeholders / audience

Course grader (Dr. Segal); opponent student teams (interop partners / sparring
server); the vm__fabi team (both role deployments). Report recipient is fixed:
`rmisegal+uoh26finalgame@gmail.com`.

## 4. Acceptance criteria — Ready-To-Submit (RTS) gate

The product is **Ready-To-Submit (RTS) only when EVERY criterion below is
satisfied.** This is the single gate for submission — it makes the assignment's
Definition of Done (§13) measurable. Boxes are checked here as criteria are met
(and mirrored in `docs/requirements_matrix.md`).

**Interoperability**
- [~] AC1 — every league CORE vector reproduced by *our* production functions *(all 6 pass, `test_core_vectors`, 6.3)*; kit-regeneration drift check in CI still to wire (dev follow-up).
- [ ] AC2 — ≥1 cross-implementation game over a real tunnel audits and settles byte-identically with another team / sparring peer; zero false tamper-forfeits. **OWNER/runtime** (needs a live opponent + tunnel).
- [x] AC3 — the emitted email body equals the exact hashed canonical report bytes. *(`test_email_wiring`: a played match's drafted MIME body decodes to exactly `report_body`, 7.7a)*

**Distribution & local truth**
- [x] AC4 — Police & Thief run as separate processes (`python -m police_agent` / `-m thief_agent`) with separate config dirs; comms are transport-only (commits + scent, never positions); no shared mutable state; the live snapshot key-set carries no opponent truth. *(role CLIs 7.6a; `test_live_apply` boundary; transport-only runtime)*
- [x] AC5 — no central referee/server/board; results are derived from logged events, never trusted from a claim. *(two-peer runtime match, 2.5b; scoring derived in `emit`)*

**Gameplay & reliability**
- [x] AC6 — a full 6-sub-game series finishes and audits cleanly with role alternation. *(verified: 6/6 sub-games, alternating roles, agreeing results, all audits pass, shared `game_uid`; `test_series` covers 2-game alternation)*
- [x] AC7 — safe under malformed / missing-required / unknown-field / **stale / duplicate / out-of-order** messages, timeouts, and tamper; the loop never stalls (HOLD fallback). The handler folds each opponent step exactly once (strict step-monotonic guard); a dead peer fails closed (opponent times out). *(`test_turn_handler`, `test_runtime` dup-delivery + timeout, `test_protocol`, `test_audit`)* Mid-game restart-resume is out of scope (fail-closed by design).
- [x] AC8 — no optional ENH features are implemented (CORE-only), so ENH is off by default; a CORE-only peer plays a full match. *(the whole suite is CORE)*

**Reporting & UX**
- [x] AC9 — the four JSON artifacts (declaration / config / log / result) share one `game_uid`, use the correct filenames, and carry `config_sha256` + `mutual_agreement`. *(`test_artifacts`, `test_emit`)*
- [x] AC10 — Gmail reporting works, draft/dry-run + disabled by default, fixed recipient; a real send needs a config opt-in + owner OAuth (OD-3). *(`test_email_sender`, `test_gmail_client`, `test_email_wiring`)*
- [x] AC11 — live GUI respects local truth; replay verifies integrity (`verified OK` / `TAMPERED`) and reconstructs both trajectories. *(`test_live_apply`, `test_replay_data`, `test_replay_view`)*

**Deployment & submission**
- [~] AC12 — the pre-match connectivity probe + Host-header handling are built and tested (`test_connectivity`); a live public-tunnel run is **OWNER/runtime**.
- [x] AC13 — both exported repos are self-contained, testable, cross-linked, and traceable to one canonical core commit/hash. *(`test_export`; vendored suite runs standalone; matching `core_manifest.json`)*
- [ ] AC14 — README + all 19 PRDs + the four artifacts are present; **OWNER** submission steps remain: GUI screenshots, the annotated submission tag, and pushing the two `dist/` trees to the submission repos.

**Engineering quality (enforced on every PR)**
- [x] AC15 — coverage ≥85% *(98.32%)*; zero ruff violations; every Python file ≤150 code lines.
- [x] AC16 — `uv` only; no hard-coded game/config params (via `CFG`); no secrets committed.
- [x] AC17 — every mechanism has a dedicated PRD; `docs/PROMPTS.md` + `COSTS.md` updated on every PR; `docs/TODO.md` task boxes checked as work completes.

**RTS status (2026-08-05):** engineering complete — 14 AC satisfied (AC7 robustness
closed); AC1 has a small CI dev follow-up; AC2 / AC12 / AC14 are owner runtime +
submission actions. See `docs/PROGRESS.md` for the owner checklist.

## 5. Functional requirements

Grouped; each has a dedicated PRD (§11) and a row in `requirements_matrix.md`.

**Domain (Stage 1)**
- FR-1 Board/coordinates/movement: N×N grid, `["N","S","E","W","STAY"]` orthogonal
  (Manhattan), king mode opt-in; barriers block both; config-driven.
- FR-2 Barriers: police-only, adjacent cell, capped by budget.
- FR-3 Capture/terminal: capture = coordinate overlap (own-state honest answer);
  thief survival at `step ≥ max_steps`; timeout/tamper/stopped = technical.
- FR-4 Scoring/league: fixed table, tie rule, series aggregation, diversity;
  totals **derived**.
- FR-5 Local-truth model: separate public / private / inferred / audit-only state.

**Protocol & orchestration (Stage 2)**
- FR-6 FastMCP peer: server + client; exactly the 4 tools (`negotiate`,
  `receive_turn`, `submit_audit`, `receive_control`); typed schemas; reject
  unknown/malformed/stale/duplicate/out-of-order.
- FR-7 Pre-game agreement: exchange terms, mutual signature, derive
  `game_uid`/`game_id`; refuse to start on any mismatch.
- FR-8 Orchestrator FSM: startup → readiness → agreement → per-sub-game →
  turns → claims → audit → consensus → report → completion/abort; idempotency,
  monotonic ids, timeouts, bounded retries, watchdog, safe restart / fail-closed.
- FR-9 Gatekeeper: all external calls via a central rate-limiter; FIFO queue on
  overflow, backpressure, transient-retry.

**Intelligence (Stages 3–4)**
- FR-10 Belief map: Bayesian heatmap updated from scent, diffused per movement.
- FR-11 Strategy: legal-action set computed in code; strategy selects only legal
  actions; pluggable `BrainBase` seam (`_pick_move`/`_decide_move`).
- FR-12 Pheromone/scent: emission, decay, wire representation (CORE math).
- FR-13 Verbal layer: LLM only for the hint; provider abstraction with a
  deterministic offline default; word-limit + deadline fallback; the **move is
  always pure Python** (LLM-driven moves only by mutual prior agreement).

**Security & interop (Stage 6)**
- FR-14 Commit-reveal: per-step sealing, nonce reveal at audit, mutual re-verify;
  failed audit → `tamper_forfeit`.
- FR-15 Interop serialization: one production canonical-JSON function; the four
  serializations (compact hash form; spaced report-consensus form); pass CORE
  vectors from our code.

**Deployment (Stage 5)**
- FR-16 Cloud tunnel: local + documented public-tunnel modes; Host-header
  handling; pre-match connectivity probe; no weakening of FastMCP security.

**Reporting & delivery (Stage 7)**
- FR-17 Logging/audit/replay: sealed per-step logs; mutual audit; replay viewer
  showing integrity (`Verified OK`/tamper) and reconstructing the match.
- FR-18 Four JSON artifacts: `declaration`, `config` (+`config_sha256`), `log`,
  `result` (+`mutual_agreement`), sharing one `game_uid`; correct filenames.
- FR-19 Report canonicalization + consensus signature (spaced form, sign-then-
  insert under the Hebrew key); emitted email body = exact hashed bytes.
- FR-20 Gmail reporting: send-only OAuth, draft/dry-run default, fixed recipient.
- FR-21 Live GUI: shows only local knowledge; full truth only in retrospective
  replay.
- FR-22 Two-repo export: deterministic export of `police-agent`/`thief-agent`,
  vendored core snapshot, cross-links, drift check; self-contained.

## 6. Non-functional requirements

- NFR-1 Determinism: domain/crypto/serialization are pure and reproducible.
- NFR-2 Offline-testable: unit ≤60 s, integration ≤300 s; mock network/LLM/Gmail/
  tunnel; no test needs a live cloud model or opponent.
- NFR-3 Coverage ≥85% (statement + branch + critical paths); suite fails below.
- NFR-4 Zero ruff violations; every Python file ≤150 code lines.
- NFR-5 `uv` only; `pyproject.toml` + `uv.lock` are the dependency source.
- NFR-6 No hard-coded game/config params; load via `CFG`; never lower a minimum.
- NFR-7 SDK architecture: all business logic reachable via the SDK; no logic in
  GUI/CLI; role-agnostic single core.
- NFR-8 Security: no secrets committed; `.env`/`secrets/` only; HTTPS + token auth
  for public MCP; token revocation supported.
- NFR-9 Byte-exact interop on the six CORE surfaces (per `CLAUDE.md` §36.3).
- NFR-10 Reviewability: PRs 50–200 LOC target (soft cap 300); one purpose each.
- NFR-11 Versioning: code/config versions tracked; runtime compatibility check.

## 7. Assumptions & dependencies

- Book + reference + league kit are **v3.0.0** and mutually consistent on interop
  (verified). The league kit is external, owned by another team, git-ignored, and
  fetched via `scripts/fetch_interop.sh` (see `docs/INTEROP.md`).
- Runtime dependency: `fastmcp>=3.4.3`; Python 3.13. LLM/tunnel/Gmail are optional
  boundaries, mocked in tests.
- Personal values pending: student member IDs; Gmail sender account/OAuth owner.

## 8. Constraints

- No central referee / shared authoritative state. One canonical core; the two
  submission repos are generated and must be self-contained (no runtime dep on
  each other or a private third repo). Action declarations are English natural
  language; the declared action is authoritative, coordinates non-authoritative;
  agents must be honest.

## 9. Out of scope

- Real cloud-LLM usage in automated tests; a central lobby/matchmaking service
  (optional league infra); ENH features unless a partner negotiates them; any GUI
  business logic (presentation only).

## 10. Milestones (7-stage incremental build; each end-to-end before the next)

1 Base Logic (domain) · 2 MCP Infra + orchestration · 3 Strategy/belief ·
4 Language + Scent · 5 Cloud + Tunnel · 6 Security (commit-reveal + interop) ·
7 Reporting Shell (artifacts, Gmail, GUI, replay, export). Full task breakdown in
`docs/TODO.md`; design in `docs/PLAN.md`; contradictions in `docs/decisions.md`.

## 11. Dedicated PRD catalog (guideline §1.3)

The book's Chapter 10 defines seven *build stages* (§10); the assignment §3 and
guideline §1.3 require a dedicated PRD per *mechanism*. The stages live in the
plan; the mechanisms each get a PRD:

| PRD | Mechanism | Stage |
|-----|-----------|-------|
| `PRD_game_state` | board, movement, barriers, capture, local-truth | 1 |
| `PRD_scoring_league` | scoring table, tie rule, aggregation, diversity | 1 |
| `PRD_config_constitution` | signed `game.json` + private `game.toml`, versioning | 1 |
| `PRD_mcp_protocol` | FastMCP tools, schemas, message validation | 2 |
| `PRD_player_agents` | role-agnostic peer runtime, entry points | 2 |
| `PRD_orchestrator_fsm` | state machine, deadlines, watchdog, restart | 2/6 |
| `PRD_gatekeeper_rate_limit` | token-bucket, queue, backpressure | 2 |
| `PRD_pregame_agreement` | negotiation, terms signature, `game_uid` | 2/6 |
| `PRD_belief_map` | Bayesian heatmap, diffusion | 3 |
| `PRD_strategy_brains` | legal-action set, `BrainBase` seam, heuristics | 3 |
| `PRD_pheromone_scent` | emission, decay, wire | 4 |
| `PRD_llm_verbal_layer` | hint providers, word-limit, fallback | 4 |
| `PRD_cloud_tunnel` | tunnel, Host-header, connectivity probe | 5 |
| `PRD_interop_serialization` | canonical JSON, 4 serializations, vectors | 6 |
| `PRD_commit_reveal` | sealing, nonce, mutual audit | 6 |
| `PRD_logging_audit_reporting` | logs, audit, four JSON artifacts | 7 |
| `PRD_email_reporting` | Gmail OAuth send-only, exact bytes | 7 |
| `PRD_gui_replay` | live GUI (local-truth), replay integrity | 7 |
| `PRD_two_repo_export` | export + drift check + submission | 7 |

Each is authored (from TODO stub → full PRD with theory, I/O, metrics,
alternatives, success criteria, test scenarios) before its stage begins.

## 12. Deliverables

Source + tests; shared/private config templates; the 19 PRDs + PLAN/TODO/
requirements_matrix/decisions/architecture; live GUI; replay/verification tool;
the four JSON artifacts; Gmail reporting; README (academic); submission evidence;
annotated submission tag; deterministic two-repo export.

## 13. References

`instructions/police_thief_p2p.pdf` (book v3.0.0, Appendix F binding table);
`copthief-league-protocol/SPEC.md` + `vectors/`; `../Game-P2P-Cop-Chase` (code
v3.0.0); `instructions/assignment.md`; `instructions/software-project-guidelines.md`;
`CLAUDE.md` (§36 ground truth).

## 14. Open decisions

Decisions still open; **this section is updated the moment a decision is made**
(and promoted to an ADR in `docs/decisions.md`). Resolved items move to `decisions.md`.

| # | Open decision | Options / default | Needed by | Status |
|---|---------------|-------------------|-----------|--------|
| OD-1 | Public tunnel provider | Cloudflare named tunnel (default) vs ngrok | Stage 5 | OPEN (ADR-15 proposed) |
| OD-2 | Student member IDs for artifacts | real IDs vs `id-0001` placeholders | before submission | OPEN (placeholders in use) |
| OD-3 | Gmail sender account + OAuth owner | which account; who runs OAuth setup | Stage 7 (email) | OPEN |
| OD-4 | First interop opponent | ImreEyal sparring / reference peer / partner team | Stage 5 cross-play | OPEN |
| OD-5 | Opt-in ENH features | none (default, CORE-only) vs specific ENH | any (negotiation-gated) | OPEN — default none |
| OD-6 | LLM verbal provider for demos | `template` (default) vs ollama/claude_api | Stage 4 | OPEN — default template |

Resolved so far (see `docs/decisions.md`): ground-truth source (ADR-1), the five
interop contradictions (ADR-2..6), package layout (ADR-7), Python 3.13 (ADR-8),
league-kit external (ADR-9), three-repo topology (ADR-10), per-mechanism PRDs
(ADR-11), LLM-verbal-only (ADR-12), config model (ADR-13).
