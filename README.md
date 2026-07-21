# cop-rob-p2p — Distributed Cop-Thief P2P Agent System (team vm__fabi)

University of Haifa final project (Orchestration of AI Agents). Two autonomous
FastMCP peers — **Police** and **Thief** — play a hidden-position pursuit game
over a peer-to-peer network, seal every move with commit-reveal, audit each
other, and settle on byte-identical results with independently-implemented peers
from other teams.

> **Status:** Stage -1 (project setup). This README is a skeleton; the full
> academic README is authored at the reporting stage. Authoritative operating
> instructions are in [`CLAUDE.md`](CLAUDE.md); the confirmed spec (parameters,
> interop constructions, artifacts) is pinned in `CLAUDE.md` §36; the staged
> build plan is in [`docs/PLAN.md`](docs/PLAN.md).

## Repositories

- **Workspace (this repo):** canonical core + development — `mironovich-v/cop-rob-p2p`
- **Police submission (generated):** `mironovich-v/cop-rob-p2p-police`
- **Thief submission (generated):** `mironovich-v/cop-rob-p2p-thief`

## Layout

- `src/cop_thief_core/` — shared, role-agnostic core: `domain`, `interop`,
  `protocol`, `orchestration`, `audit`, `reporting`, `llm`, `shared`.
- `src/police_agent/`, `src/thief_agent/` — role entry points.
- `config/` — per-role private `game.toml` + signed shared `game.json` + `rate_limits.json`.
- `tests/` — `unit/`, `integration/`, `conformance/` (league CORE vectors).
- `docs/` — PRD / PLAN / TODO, per-stage PRDs, decisions, architecture.
- `copthief-league-protocol/` — external league kit, **not vendored**
  (see [`docs/INTEROP.md`](docs/INTEROP.md); fetch via `scripts/fetch_interop.sh`).

## Toolchain

`uv` only. Once implementation begins:

```bash
uv sync
uv run ruff check src tests
uv run pytest tests -q
uv run pytest tests --cov=src --cov-fail-under=85
```

## Build plan (7 stages, each end-to-end before the next)

Base Logic → MCP Infra → Strategy → Language + Scent → Cloud + Tunnel → Security
→ Reporting Shell. See [`docs/PLAN.md`](docs/PLAN.md) and [`docs/TODO.md`](docs/TODO.md).

## License / credits

Independent student implementation for University of Haifa. Targets book /
reference **v3.0.0** (© Dr. Yoram Segal) and the league interop kit — both cited,
never copied. See `docs/INTEROP.md`.
