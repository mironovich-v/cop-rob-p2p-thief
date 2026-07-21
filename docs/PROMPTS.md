# PROMPTS — AI-Assisted Work Log

> Significant AI-assisted sessions (guideline §7.3). Trivial manual edits omitted.
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
- **Output:** `docs/TODO.md`, `docs/PROMPTS.md`, `docs/REVIEW_POLICY.md` (this PR).
