# COSTS.md — AI / Runtime / Review Cost Ledger

> Project: **vm__fabi** Cop-Thief P2P (University of Haifa final project).
> Tracks the cost of AI-assisted development and expensive operations, per
> `instructions/software-project-guidelines.md` §10.3 and `CLAUDE.md` §8.
>
> Record every meaningful AI-assisted session and any long-running command,
> experiment, or match. Exact token counts when available; otherwise practical
> proxies (wall-clock time, session count, review burden, rework).

## Ledger

| Date | Phase/PR | Branch | PR | Commit(s) | Agent/Model | Effort | Task | Wall Time | Human Review | Runtime/Compute | Tokens (in/out) | Accepted? | Notes |
|------|----------|--------|----|-----------|-------------|--------|------|-----------|--------------|-----------------|-----------------|-----------|-------|
| 2026-07-21 | Stage -1 | phase-0-agent-control | (pending) | (pending) | Claude Opus 4.8 (1M) | xhigh | Read guidelines + book PDF + reference repo (Game-P2P-Cop-Chase) via 5 parallel explorer agents; extract binding parameters and interop constructions; scaffold agent-control files | ~1 session | (pending) | 5 background subagents (~200k subagent tokens total) | n/a (plan-usage) | (pending) | Hebrew PDF unreadable by text layer; reference repo adopted as ground truth. Confirmed all CORE interop constructions match the league SPEC. |

## Notes on methodology
- This project is billed via a Claude Code plan/subscription, so exact per-call
  token accounting is not always available. When it is (e.g. subagent token
  totals reported by the workflow harness), record it; otherwise use wall-clock
  time, session count, and review burden as proxies.
- Cost is not only financial — it also measures **review debt** (PR size),
  **runtime debt** (long matches, tunnel runs), and **agent efficiency**
  (rework caused by AI output).
- Long-running or expensive items to log here as they occur: full 6-sub-game
  match runs, cross-implementation tunnel games, any opt-in LLM (`claude_api` /
  `claude_cli`) banter usage against the token budget (200,000 / series).
