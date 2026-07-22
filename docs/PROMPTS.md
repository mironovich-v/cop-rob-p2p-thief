# PROMPTS — AI-Assisted Work Log

> AI-assisted work log (guideline §7.3). **Standing rule: one entry per PR.**
> Kinds: Planning · Implementation · Review/Audit · Fix · Submission.

## 2026-07-21 · Stage -1 · Planning · Merge guidelines into CLAUDE.md
- **Context/Goal:** fold every requirement from `software-project-guidelines.md`
  into a comprehensive project `CLAUDE.md`.
- **Output:** `CLAUDE.md` §1–§35 (operational layer + full engineering standard).
- **Lesson:** the guideline is the global standard; CLAUDE.md is the execution
  layer and may only add, never weaken. **Approved.**

## 2026-07-21 · Stage -1 · Planning · Assess book + league kit
- **Context/Goal:** read `police_thief_p2p.pdf` + `copthief-league-protocol/`;
  decide if requirements are clear enough to start.
- **Issue:** the Hebrew PDF text layer is not machine-readable (RTL scrambling);
  only numbers/English/tables survive. Extracted Appendix-F binding table.
- **Refinement:** owner supplied the lecturer's reference repo as ground truth.
- **Lesson:** treat the reference code as the practical source of truth (ADR-1).

## 2026-07-21 · Stage -1 · Review/Audit · Read reference implementation
- **Context/Goal:** read all of `../Game-P2P-Cop-Chase` (~7.8k LOC) to pin the
  spec. **Method:** 5 parallel explorer subagents (domain / peer+infra /
  report+config / gui+strategy+tests / docs) + first-hand read of the interop core.
- **Output:** confirmed params + the 4 interop serializations + MCP surface + FSM
  + artifact scheme → pinned in `CLAUDE.md` §36; 5 contradictions resolved.
- **Lesson:** parallel read agents cover a large repo fast; verify crown-jewel
  constructions first-hand. **Approved.**

## 2026-07-21 · Stage -1 · Implementation · Bootstrap repo (Stage-0, main)
- **Goal:** generate the repo tree + agent-control files; seed empty `main`.
- **Output:** commit `ff97425` (owner-authorized one-time direct-to-main); scaffold
  builds, ruff clean, imports OK.
- **Decision:** league kit kept external/git-ignored + fetch script (ADR-9).

## 2026-07-21 · Stage -1 · Planning · PR #1 PRD + requirements matrix
- **Goal:** master PRD + traceability matrix; expand PRDs per mechanism.
- **Output:** `docs/PRD.md`, `docs/requirements_matrix.md`, 19 mechanism PRD stubs
  (commit `db889f0`). **Refinement:** replaced the 7 stage stubs (ADR-11).

## 2026-07-21 · Stage -1 · Planning · PR #2 PLAN + architecture + decisions
- **Goal:** C4/design, runtime architecture, ADR log with the 5 contradictions.
- **Output:** `docs/PLAN.md`, `docs/architecture.md`, `docs/decisions.md`
  (ADR-1..15; commit `6a9792f`).

## 2026-07-21 · Stage -1 · Planning · PR #3 TODO + PROMPTS + REVIEW_POLICY
- **Goal:** decompose the 7 stages into PR-sized slices; process docs.
- **Output:** `docs/TODO.md`, `docs/PROMPTS.md`, `docs/REVIEW_POLICY.md` (commit `3421a60`).

## 2026-07-21 · Stage 1 · Planning · PR #4 Stage-1 design PRDs
- **Output:** `PRD_game_state`, `PRD_scoring_league`, `PRD_config_constitution`
  (commit `a833fbd`). Design gate before code.

## 2026-07-21 · Stage 1 · Implementation · PR #5 board + constants (1.1)
- **Output:** `constants.py`, `domain/board.py`, `test_board` (15). Cov 92%. Commit `3badbaa`.

## 2026-07-21 · Stage 1 · Implementation · PR #6 own_state (1.2)
- **Output:** `domain/own_state.py` + `directions_from_move_set`; `test_own_state`
  (12). Cov 96%. Commit `e8e7b07`.

## 2026-07-21 · Stage 1 · Implementation · PR #7 rules (1.3)
- **Output:** `domain/rules.py` + result tokens; `test_rules` (6). Cov 96%. Commit `e432455`.

## 2026-07-22 · Stage 1 · Implementation · PR #8 scoring (1.4)
- **Output:** `domain/scoring.py`; `test_scoring` (8). Cov 97%. Commit `4e06278`.

## 2026-07-22 · Stage 1 · Implementation · PR #9 config loader + templates (1.5)
- **Output:** `shared/config.py`, `exceptions.py`, per-role config templates;
  `test_config` (7). Cov 98%. Commit `84bd6a3`. Completes Stage 1.

## 2026-07-22 · Stage 2 · Planning · Stage-2 design PRDs
- **Output:** `mcp_protocol`, `gatekeeper_rate_limit`, `pregame_agreement`,
  `orchestrator_fsm`, `player_agents` PRDs (branch `stage-2-design-prds`, in review).

## 2026-07-22 · Stage -1 · Docs · Process & tracking upgrade
- **Goal (owner request):** per-PR `PROMPTS.md`/`COSTS.md` rule; `TODO.md` task
  checkboxes; `PRD.md` RTS acceptance + Open Decisions; `PLAN.md` Phase Plan.
- **Output:** this PR (branch `docs-process-and-tracking`).
- **Lesson:** encode tracking/transparency as standing gates, not ad-hoc habits.
