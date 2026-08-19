# PRD — Role-Agnostic Player Agents & Runtime

> Dedicated PRD (guideline §1.3). **Build stage:** 2 (TODO slices 2.5 runtime,
> 2.6 SDK+series). Ground truth: reference `sdk/sdk.py`, `sdk/series.py`,
> `peer/runtime.py`, `police_agent`/`thief_agent` entry points; assignment §4–§5.

## 1. Background

One canonical, **role-agnostic** implementation plays both Police and Thief; the
role is injected, not hard-coded into separate systems. Two thin entry points
(`police_agent`, `thief_agent`) each start a peer with their private config dir.
The SDK is the single business entry point; GUI/CLI only delegate to it.

## 2. Requirements (NFR-7, FR-8 series)

Single shared core; role selected by config/CLI; each peer runs as its own OS
process with its own private config, logs, and runtime state; no shared mutable
state between peers; a series of `num_games` sub-games with role alternation.

## 3. Interfaces

- **`SimulationSdk.run_peer(role, stub_llm=False, transport=None, listener=None,
  controls=None) → dict`** — plays the whole series; returns summaries + result +
  paths (artifacts/email wired in Stage 7). Single entry point.
- **`run_series(...)`** — loop over `num_games`; `role_for(natural, n)` =
  natural on odd sub-games, swapped on even; build the MCP transport once and
  reuse across sub-games; rebuild a fresh `PeerRuntime` per sub-game; handle
  `RestartSeries` (bounded).
- **Entry points** `python -m police_agent --config config/police` (and thief):
  load `CFG`, start server, run the SDK; strategy seam resolved from config
  (`[strategy] thief_class`/`police_class`, else shipped brain).

## 4. Role-agnosticism & local truth

Role is a parameter to `OwnGameState`/brains; the same code paths serve both.
Neither entry point imports the other's private package; no shared file/singleton/
object; a peer holds only its own truth (enforced structurally, PRD_game_state).

## 5. Alternatives considered

Separate cop-only / thief-only systems → **rejected** (duplication, assignment
forbids). Logic in the CLI/GUI → **rejected** (SDK is the single entry).

## 6. Success criteria & tests

`run_peer` plays a full stubbed series and returns the expected structure; roles
alternate correctly; two peers run in separate processes/dirs with no shared
state; a custom brain injected via config is used. Tests: `test_sdk`,
`test_series`, `test_runtime` (injected brain), integration `test_mcp_match`.
