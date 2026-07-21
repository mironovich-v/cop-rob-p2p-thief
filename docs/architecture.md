# Architecture — Components, Trust Boundaries, Runtime & Data Flow

> Concrete runtime view (assignment §3). Complements `docs/PLAN.md` (C4/design)
> and `docs/PRD.md` (requirements). Facts are pinned in `CLAUDE.md` §36.

## Runtime processes

Two independent OS processes, one per role, with **no shared memory, file, or
mutable state** between them. Each owns:

- a private config dir (`config/police/` or `config/thief/`): private `game.toml`
  + the signed shared `game.json` + `rate_limits.json`;
- a FastMCP **server** (its inbox, 4 tools) on its own port (thief 8801 / police
  8802);
- a FastMCP **client** that calls the opponent's server;
- its own logs/artifacts directory keyed by `group_id`.

Roles alternate across the 6-sub-game series (odd = natural role, even = swapped),
so the stable per-peer key is the **group**, not the role.

## Component layers (strict separation of concerns)

```
CLI / Tkinter GUI / Replay      presentation only — delegates to SDK, no logic
        │
   SimulationSdk                single business entry point (SDK architecture)
        │
   PeerRuntime + Orchestrator   per-sub-game state machine, turn loop, reliability
        │
   cop_thief_core layers        domain · interop · protocol · audit · reporting · llm
        │
   infra (boundaries)           FastMCP server/client · LLM provider · Gmail · tunnel
        │
   shared                       CFG config · gatekeeper + rate limiter · sysinfo · version
```

Network handlers never mutate domain state directly — every accepted message is
routed through the orchestrator/state machine after validation.

## Trust boundaries (local-truth model)

Four state classes, structurally separated so a strategy or GUI cannot reach
forbidden opponent truth:

| Class | Examples | Crosses wire? |
|-------|----------|---------------|
| Private self | own position, strategy state, nonces | no (nonces revealed only at audit) |
| Public agreed | signed terms, declared barriers | yes (barriers announced) |
| Sent/received | commits, scent maps, hints, capture/win claims | yes (commit hides truth) |
| Inferred | belief heatmap of opponent position | local only |
| Audit-only | revealed payloads+nonces | only after reveal phase |

- The opponent's true position **never** crosses the wire — it is inferred from
  scent + hints (which may lie).
- Honesty is enforced cryptographically: a false capture/claim answer is exposed
  when the sealed true state is revealed at audit → `tamper_forfeit`.
- Live GUI renders only local knowledge (own position, own scent, belief). Full
  truth (both positions) appears only in retrospective replay, after audit
  material exists and the sibling log is available.

## Data flow — one turn

```mermaid
sequenceDiagram
  participant Opp as Opponent
  participant Srv as My FastMCP server (inbox)
  participant Orc as Orchestrator/FSM
  participant Dom as Domain (belief, smell, rules, brain)
  participant Cli as My FastMCP client
  Opp->>Srv: receive_turn(TurnMessage: commit, scent, hint, claims)
  Srv->>Orc: enqueue; validate schema/order/dup
  Orc->>Dom: absorb scent (decay), diffuse belief, note barriers
  Orc->>Dom: check capture/win claims (honest, own state)
  Orc->>Dom: legal actions → strategy picks move (pure Python)
  Dom-->>Orc: Decision(move, hint, verdict)
  Orc->>Dom: seal (state,move,verdict) under commit; emit own scent
  Orc->>Cli: send_turn(TurnMessage: my commit + scent + hint + claims)
  Cli->>Opp: receive_turn(...)
```

## Data flow — lifecycle & settlement

Startup → network readiness → **negotiate** (terms exchange, mutual signature,
derive shared `game_uid`/`game_id`; refuse on mismatch) → per-sub-game turn loop
(thief first) → capture/win claims → **mutual audit** (`submit_audit`: exchange
revealed logs + nonces; each re-hashes the other's records) → result consensus
(derived, not declared) → build the four artifacts + report → Gmail draft →
completion / abort / technical-failure. A failed audit overrides the result to
`tamper_forfeit`.

## Reliability

Idempotency/duplicate protection; monotonic step & sub-game ids; per-turn
timeouts and bounded retries; watchdog/deadline tracking; the API **gatekeeper**
(FIFO queue + backpressure + transient retry) fronts all external calls; the game
loop never stalls (rejected move → HOLD); structured error reasons; safe restart
of a whole series (drain stale inboxes before re-negotiating) or fail-closed.

## External boundaries (mocked in tests)

FastMCP transport, LLM verbal provider (offline default), Gmail (draft/dry-run),
and the public tunnel are the only external boundaries; all are mocked in
automated tests. Domain, protocol, crypto, audit, and serialization logic is
always real, never mocked.
