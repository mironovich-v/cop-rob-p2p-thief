# PRD — Game State & Rules

> Dedicated PRD (guideline §1.3). **Build stage:** 1. Covers TODO slices 1.1
> (constants + board), 1.2 (own-state), 1.3 (rules/terminal). Ground truth:
> `CLAUDE.md` §36, reference `domain/{board,own_state,rules,constants}.py`, book
> Appendix F. All numbers are **config-driven**, validated against App-F minimums.

## 1. Background

A discrete N×N grid pursuit. There is **no referee**: each peer evaluates rules
on its **own** state only; correctness is later proven by cryptographic audit.
This PRD specifies the pure, deterministic domain layer (no networking, LLM, or
I/O) that all higher layers build on.

## 2. Requirements

- FR-1 board & movement; FR-2 barriers; FR-3 capture/terminal; FR-5 local-truth
  separation (see `docs/requirements_matrix.md`).
- Pure functions/classes, exhaustively unit-tested (boundary, invalid-action,
  terminal); deterministic; every file ≤150 code lines.

## 3. Model & interfaces

**Coordinates:** `Cell = tuple[int,int]` = `(row, col)`, origin top-left, index 0.

**Directions & deltas (`constants.py`):** `Direction` ∈ {N,S,E,W} (+diagonals for
king mode); `DELTAS[dir] → (drow,dcol)` (N=(-1,0), S=(1,0), E=(0,1), W=(0,-1),
plus NE/NW/SE/SW). `ORTHOGONAL = (N,S,E,W)`. `MoveType` ∈ {MOVE, BARRIER, HOLD}.
`Role` ∈ {POLICE, THIEF}. Verdict strings {"truth","lie"}.

**Board (`board.py`):**
- `Board(size, moves=None)` — `moves` defaults to king (8-dir); the game passes the
  orthogonal `move_set` (N/S/E/W). STAY is a HOLD, not a direction.
- `in_bounds(cell) → 0 ≤ row,col < size`.
- `distance(a,b)` → **Chebyshev** if diagonal moves allowed, else **Manhattan**.
- `step(origin, dir, barriers) → Cell|None` (None if off-board or into a barrier).
- `neighbors(cell, barriers) → list[Cell]`; `legal_moves(origin, barriers) →
  list[(Direction, Cell)]`.

**Own state (`own_state.py`):** `OwnGameState(role, start, board_size, move_set)`
tracks `position`, `visited` (start included), `barriers` (own + declared),
`my_barriers` count, `step_number`, `log`. `apply_move(move_type, direction,
barriers_max) → bool` executes and logs; returns False on illegal. Barrier
placement is **police-only**, requires a direction, target in-bounds, not already
a barrier, and `my_barriers < barriers_max`. STAY (HOLD) increments the step but
not `visited`. Log row: `{step, position:[r,c], move:"TYPE:DIR", unique_cells,
barrier:[r,c]|null}`.

**Rules (`rules.py`):** `GameRules(max_steps)`;
- `thief_result(state) → "survival"|None` (survival when `step_number ≥ max_steps`);
- `is_captured(state, claim) → bool` = `state.position == tuple(claim)` (honest
  answer to a police capture claim; lying is exposed at audit → `tamper_forfeit`).

**Local-truth separation:** own true position/nonces are private; only declared
barriers and capture claims are public; opponent position is never stored as
truth — only inferred (belief map, Stage 3).

## 4. Parameters (config-driven; App-F)

`grid_size` 7 (min), `move_set` N/S/E/W/STAY (fixed), `max_barriers` 14 (min),
`max_moves`/`survival_threshold` 35 (min), `thief_start` [3,3], `cop_start` [0,0]
(negotiable), `axis_origin_corner` top-left, `axis_start_index` 0. **No literal
may duplicate a config value** — read via `CFG`.

## 5. Alternatives considered

- King (8-dir) vs orthogonal movement → default orthogonal (App-F `move_set`),
  king retained as opt-in for compatibility (distance metric switches with it).
- Storing opponent position for convenience → **rejected** (breaks local-truth).

## 6. Success criteria

Deterministic; every public method tested on happy + error paths; illegal moves
never mutate state; capture/survival exactly match the reference; ≥85% coverage
for the module; ruff-zero; files ≤150 lines.

## 7. Test scenarios

Board: in/out-of-bounds; orthogonal 4-neighbours vs king 8; barrier blocks step;
Manhattan vs Chebyshev distance. Own-state: legal MOVE updates position+visited;
HOLD holds; police BARRIER decrements budget and is rejected when exhausted or
duplicated; thief may never place a barrier; log shape. Rules: survival at
`step ≥ max_steps`; capture true/false by cell equality; boundary at exactly
`max_steps`.
