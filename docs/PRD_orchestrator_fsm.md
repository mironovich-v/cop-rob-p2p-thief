# PRD — Orchestrator State Machine & Reliability

> Dedicated PRD (guideline §1.3). **Build stage:** 2/6 (TODO slice 2.5; audit
> wiring 6.2). Ground truth: reference `peer/runtime*.py`, `turn_handler.py`,
> `turn_sender.py`, `handshake.py`, `summary.py`, `controls.py`; book ch.8.

## 1. Background

Each peer runs an explicit finite-state machine for one sub-game. It is the only
component allowed to mutate domain state, and only after validating an accepted
message. It must never stall: a rejected move falls back to HOLD.

## 2. Requirements (FR-8)

Explicit states + transitions; idempotency/duplicate protection; monotonically
validated step & sub-game ids; per-turn timeouts and bounded retries;
watchdog/deadline tracking; gatekeeper integration; safe restart or fail-closed;
structured error reasons (never ambiguous exceptions).

## 3. States & lifecycle

Status set: `WAITING, THINKING, PLAYING, PAUSED, STOPPED, GAME_OVER, QUIT`.
Lifecycle: startup → network readiness → **negotiate** → per-sub-game setup →
turn loop (thief first; ping-pong turn token) → capture/win claims → **audit /
reveal** → result consensus → report → completion / abort / technical-failure.

## 4. Turn cycle (per step)

Receive TurnMessage → `TurnHandler.process`: append history, note barriers,
diffuse belief, absorb scent (decay), check claim_response (my win) and win_claim
(opponent win); if capture_claim, answer honestly from own state. If still my
turn → `take_turn`: brain decides (pure Python) within the step deadline (miss →
HOLD/random), seal `(state,move,verdict)` under commit, emit scent, send. Deadline
resets on each incoming turn.

## 5. Reliability & settlement

Watchdog on `turn_timeout_seconds`; silence beyond it → `("timeout", role)`.
Duplicate/stale/out-of-order tolerated (state advances by id, inboxes drained on
restart). End-of-game: exchange `AuditPayload`; each re-hashes the opponent's
records; a failed audit overrides the result to `tamper_forfeit`. Result totals
are **derived**, never trusted. Restart raises a `RestartSeries` signal the series
loop catches (bounded attempts); quit ends cleanly and notifies the opponent.

## 6. Alternatives considered

Implicit control flow instead of an explicit FSM → **rejected** (book ch.8 and
reliability). Trusting claimed results → **rejected** (derive + audit).

## 7. Success criteria & tests

Two runtimes over a fake transport agree on result/winner; audits pass both ways;
timeout/duplicate/stale/skip/crash paths produce structured outcomes; loop never
stalls. Tests: `test_runtime`, `test_runtime_control`, `test_turn_handler`,
`test_deadline_controls`, adversarial cases; integration `test_mcp_match`.
