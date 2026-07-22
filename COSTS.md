# COSTS.md — AI / Runtime / Review Cost Ledger

> Project: **vm__fabi** Cop-Thief P2P. Tracks AI-assisted development and expensive
> operations, per guideline §10.3 and `CLAUDE.md` §8. **Standing rule: one ledger
> row per PR.** Billing is via a Claude Code plan/subscription, so exact per-call
> token counts are usually unavailable — we record practical proxies (session
> count, wall-clock, review burden, subagent tokens when reported).

## Ledger

| Date | PR / Phase | Branch | Commit | Model · Effort | Task | Cost proxy | Accepted |
|------|-----------|--------|--------|----------------|------|-----------|----------|
| 2026-07-21 | Setup | phase-0-agent-control | ff97425 | Opus 4.8 (1M) · xhigh | Read guidelines + book PDF + reference repo via 5 explorer subagents; extract ground truth; bootstrap scaffold | ~1 session; ~200k subagent tokens | merged |
| 2026-07-21 | PR #1 | docs-prd-requirements | db889f0 | Opus 4.8 · high | Master PRD + requirements matrix + 19-PRD catalog | ~0.3 session | merged |
| 2026-07-21 | PR #2 | docs-plan-architecture-decisions | 6a9792f | Opus 4.8 · high | PLAN (C4) + architecture + decisions (ADRs) | ~0.3 session | merged |
| 2026-07-21 | PR #3 | docs-todo-and-process | 3421a60 | Opus 4.8 · high | TODO breakdown + PROMPTS + REVIEW_POLICY | ~0.2 session | merged |
| 2026-07-21 | PR #4 | stage-1-design-prds | a833fbd | Opus 4.8 · high | Stage-1 design PRDs | ~0.2 session | merged |
| 2026-07-21 | PR #5 (1.1) | stage-1-board | 3badbaa | Opus 4.8 · high | board + constants (TDD, cov 92%) | ~0.2 session | merged |
| 2026-07-21 | PR #6 (1.2) | stage-1-own-state | e8e7b07 | Opus 4.8 · high | own_state (TDD, cov 96%) | ~0.2 session | merged |
| 2026-07-21 | PR #7 (1.3) | stage-1-rules | e432455 | Opus 4.8 · high | rules (TDD, cov 96%) | ~0.1 session | merged |
| 2026-07-22 | PR #8 (1.4) | stage-1-scoring | 4e06278 | Opus 4.8 · high | scoring (TDD, cov 97%) | ~0.2 session | merged |
| 2026-07-22 | PR #9 (1.5) | stage-1-config | 84bd6a3 | Opus 4.8 · high | config loader + templates (TDD, cov 98%) | ~0.3 session | merged |
| 2026-07-22 | Stage-2 PRDs | stage-2-design-prds | ea6d59f | Opus 4.8 · high | 5 Stage-2 mechanism PRDs | ~0.3 session | merged |
| 2026-07-22 | Process docs | docs-process-and-tracking | f29a6a0 | Opus 4.8 · high | RTS acceptance, open decisions, phase plan, task checkboxes, per-PR PROMPTS/COSTS | ~0.2 session | merged |
| 2026-07-22 | PR (2.1) | stage-2-protocol | 672db1c | Opus 4.8 · high | protocol wire schemas (TDD, cov 98%) | ~0.2 session | merged |
| 2026-07-22 | PR (2.2) | stage-2-gatekeeper | 1b8bd95 | Opus 4.8 · high | gatekeeper + token-bucket rate limiter (TDD, cov 98%) | ~0.2 session | merged |
| 2026-07-22 | PR (2.3a) | stage-2-interop-primitives | 48ba793 | Opus 4.8 · high | canonical JSON + hashing + game_uid; 4 CORE vectors pass from our code | ~0.3 session | merged |
| 2026-07-22 | PR (2.3b) | stage-2-negotiation | 1c5d5e8 | Opus 4.8 · high | Negotiation (sign/verify), terms_from_config, data-driven App-F minimum-validation | ~0.2 session | merged |
| 2026-07-22 | PR (2.4) | stage-2-mcp-server | (pending) | Opus 4.8 · high | FastMCP server (4 tools) + McpTransport client; in-memory Client(server) tests (no network) | ~0.3 session | in review |

## Notes on methodology
- Exact token accounting used when available (e.g. subagent token totals from the
  workflow harness); otherwise wall-clock time, session count, and review burden.
- Cost is not only financial — it also measures **review debt** (PR size),
  **runtime debt** (long matches, tunnel runs), and **agent efficiency** (rework).
- Log here as they occur: full 6-sub-game match runs, cross-implementation tunnel
  games, and any opt-in LLM (`claude_api` / `claude_cli`) banter usage against the
  token budget (200,000 / series).
