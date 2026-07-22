# PRD — FastMCP Peer Protocol & Tool Surface

> Dedicated PRD (guideline §1.3). **Build stage:** 2 (TODO slices 2.1 schemas,
> 2.4 server+client). Ground truth: reference `infra/mcp_server.py`,
> `infra/mcp_client.py`, `domain/protocol.py`; `CLAUDE.md` §36.4.

## 1. Background

Each peer is **both** a FastMCP HTTP server (its inbox) and a client (calls the
opponent). There is no shared bus; all coordination is message-passing over four
tools. Network handlers never touch domain state directly — they enqueue, and the
orchestrator (PRD_orchestrator_fsm) validates and applies.

## 2. Requirements (FR-6)

Typed request/response schemas; exactly four tools; reject unknown / malformed /
stale / duplicate / out-of-order messages safely; retry until the peer is up;
non-blocking polling; drain stale inboxes on restart. Public endpoints use HTTPS +
token auth (Stage 5); no security check weakened for tunnels.

## 3. Message schemas (`protocol/`)

Dataclasses with `to_dict`/`from_dict` (missing required field → error):
- **TurnMessage**: `step, sender, hint, smell_grid{"r,c":intensity}, commit,
  timestamp, barrier_placed|None, capture_claim|None, claim_response|None,
  win_claim|None`.
- **ControlMessage**: `kind∈{enable,status,restart,quit}, sender,
  sub_game_number, status, step_budget, payload`.
- **AuditPayload**: `sender, records[{payload,nonce,commit}], result_claim`.

## 4. Tool surface & client

**Server** (`build_peer_server`) exposes 4 tools, each returning `{"ok": true}`
and enqueuing to a thread-safe inbox: `negotiate`, `receive_turn`,
`submit_audit`, `receive_control`. HTTP transport; ports thief 8801 / police 8802
on 127.0.0.1; startup verifies the port is free.

**Client** (`McpTransport`): `exchange_agreement`, `send_turn`,
`poll_turn(timeout)`, `exchange_audit`, `send_control`/`poll_control`,
`drain_inboxes`. `_call_with_retry` retries until a deadline (peers may start
seconds apart); control sends are best-effort (short timeout, suppress errors).

## 5. Reliability constructions

Typed `from_dict` rejects malformed; the turn loop processes only new messages
(duplicate/out-of-order tolerated via belief/state advance + step ids);
`drain_inboxes` discards stale turns/controls/audits before re-negotiating.
Timeouts: connect 60 s, audit-send 10 s, control-send 2 s, poll interval 0.5 s.

## 6. Alternatives considered

A single shared message bus / central relay → **rejected** (breaks P2P/no-referee).
Direct domain mutation in handlers → **rejected** (must route via orchestrator).

## 7. Success criteria & tests

Schemas round-trip; missing field raises; server enqueues per tool; client
retry/poll/drain behave; a fake transport drives two runtimes to agreement. Tests:
`test_protocol`, `test_control_message`, `test_transport_drain`, and the real
two-server integration in `test_mcp_match` (Stage 2.5+). External transport mocked;
no live network in unit tests.
