# PRD — Scoring, Tie Rule & League Aggregation

> Dedicated PRD (guideline §1.3). **Build stage:** 1 (TODO slice 1.4). Ground
> truth: reference `domain/scoring.py`, book Appendix F scoring table. Pure
> functions, no I/O. All point values are **config-driven** (never hard-coded).

## 1. Background

Each sub-game yields an outcome string; league standing needs per-group points
and a series aggregate with the book's tie rule. Totals must be **derived** from
per-sub-game results and the fixed scoring table — never trusted from a claim
(agreement on sub-games ⇒ agreement on totals).

## 2. Requirements (FR-4)

- Map a sub-game outcome + role assignment → per-group points.
- Aggregate a series → totals, sub-games won, ties, winner (or series tie).
- Apply the two-group tie rule. Deterministic, pure, exhaustively tested.

## 3. Interface & algorithm

**`score_subgame(result, roles, scoring) → dict[group_id,int]`**
- `roles`: `{group_id: "police"|"thief"}` for this sub-game.
- `result == "capture"`: police-group `scoring.capture_cop`, thief-group
  `scoring.capture_thief`. `result == "survival"`: `survival_cop` / `survival_thief`.
- **Any other** result (timeout / tamper_forfeit / stopped) → **0/0** (technical
  loss).

**`aggregate(subgame_scores, tie_score) → dict`** → `{total_score, sub_games_won,
ties, winner_group, series_tie}`.
- `total_score[g]` = sum across sub-games; `sub_games_won[g]` = count where g is
  the sole max; equal-top sub-games increment `ties`.
- **Tie rule:** for exactly two groups with equal totals → add `tie_score` to
  each, `winner_group=None`, `series_tie=True`. Otherwise winner = arg-max total.

## 4. Parameters (App-F, fixed; via `CFG`)

`capture_cop` 20, `capture_thief` 5, `survival_cop` 5, `survival_thief` 10,
`tie_score` 2, `technical_loss` 0. Series: `num_games` (signed; league = 6),
`diversity_reward` 10, `min_games_to_pass` 2, `max_games_per_team` 10.

## 5. Alternatives considered

- Declaring totals on the wire → **rejected**; totals are derived (audit-proof).
- Special-casing role alternation inside scoring → handled by the caller passing
  the actual `roles` per sub-game (scoring stays role-agnostic).

## 6. Success criteria

Byte-for-byte identical aggregates to the reference for the same inputs; tie rule
correct for 2-group equal totals; technical outcomes score 0/0; ≥85% coverage;
ruff-zero; file ≤150 lines.

## 7. Test scenarios

Capture with police=g1 → 20/5; survival with thief=g2 → correct split; timeout →
0/0; multi-sub-game aggregate with role alternation; forced equal totals → each
gets `tie_score`, `series_tie=True`; clear winner path; single-group / empty
edge cases.
