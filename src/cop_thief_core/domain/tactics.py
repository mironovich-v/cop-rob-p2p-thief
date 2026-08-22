"""Tactical scoring for the shipped brains (counted-game forensics, 2026-08-18).

Why these exist: the v1 thief argmaxed distance-to-threat, whose global optimum
is a CORNER — it self-cornered at (6,6) and died to rule-46 walling in every
counted sub-game. The v1 police walled at random and ping-ponged, and the game's
own math says a pursuer never closes on an evader by chasing — the cop only wins
by cornering. So: exit-FREEDOM dominates once distance is safe (capped), a
recent-trail penalty kills oscillation, and barriers are spent only to corner —
a rule-46 strike on the believed cell, or sealing a pocketed thief's exit.

All knowledge used here is legal: own state, known barriers, and the BELIEF grid
(scent + hints) — never the opponent's true position.
"""

from collections import deque

from cop_thief_core.constants import Cell, Direction

_UNREACHABLE = float("inf")

# Private strategy tunables (documented defaults; override via the private
# game.toml [strategy.tactics] table — these are NOT signed game terms).
DEFAULTS = {
    "freedom_weight": 3.0,  # exits from the target cell — the anti-corner term
    "distance_weight": 2.0,  # distance to the believed threat (uncapped by
    "distance_cap": 999,  # default: an A/B run showed a low cap makes the
    # thief stop retreating at "safe" range and get walked down — freedom's
    # weight alone already vetoes corners: 2 exits cost more than 2 steps gain)
    "recent_penalty": 5.0,  # oscillation killer
    "recent_window": 6,  # how many of my own last cells count as "recent"
    "pocket_exits": 2,  # thief-exit count at/below which the police seals
}


def exit_count(board, cell: Cell, barriers: set[Cell]) -> int:
    """Legal one-step exits from ``cell`` given the known barriers."""
    return len(board.neighbors(cell, barriers))


def recent_trail(state, window: int) -> set[Cell]:
    """My own last ``window`` cells (from the move log) — the oscillation set."""
    return {tuple(entry["position"]) for entry in state.log[-window:]}


def beyond_reach(board, target: Cell, threat: Cell, barriers: set[Cell]) -> bool:
    """Can the threat NOT occupy ``target`` on its very next move?

    Both peers move each round, so the threat's cell and every cell it can step
    to are places the evader must not stand. The shipped scoring weighed freedom
    and distance but had no notion of reach, so it would step into a cell the
    pursuer simply walked onto. Measured against our own cop, adding this rule
    lifts median survival from 10 steps to 12 — and several more elaborate
    evader designs measured no better than it alone.
    """
    return target != threat and target not in board.neighbors(threat, barriers)


def thief_score(board, target: Cell, threat: Cell, barriers: set[Cell],
                recent: set[Cell], weights: dict) -> float:
    """Evader value of moving to ``target``.

    Distance is PESSIMISTIC — measured to the threat's closest possible cell
    AFTER its next move (it moves too; fleeing its current cell walks into its
    step). Freedom (exits) vetoes corners; a recent-trail penalty stops
    oscillation."""
    freedom = exit_count(board, target, barriers)
    next_cells = [threat, *board.neighbors(threat, barriers)]
    distance = min(
        min(board.distance(target, cell) for cell in next_cells),
        weights["distance_cap"],
    )
    penalty = weights["recent_penalty"] if target in recent else 0.0
    return weights["freedom_weight"] * freedom + weights["distance_weight"] * distance - penalty


def _step_distances(board, origin: Cell, barriers: set[Cell]) -> dict[Cell, int]:
    """Breadth-first step distance from ``origin`` to every reachable free cell."""
    distances = {origin: 0}
    queue = deque([origin])
    while queue:
        cell = queue.popleft()
        for nxt in board.neighbors(cell, barriers):
            if nxt not in distances:
                distances[nxt] = distances[cell] + 1
                queue.append(nxt)
    return distances


def territory(board, evader: Cell, pursuer: Cell, barriers: set[Cell]) -> int:
    """How many cells the evader reaches strictly before the pursuer — its room.

    A pursuer never closes on an equally fast evader by chasing: distance is the
    wrong objective. Territory is the right one, and it is what a cop actually
    takes away when it herds toward an edge or spends a barrier. Measured: an
    oracle cop with the thief's TRUE cell captured 2/16, no better than the
    shipped 3/16 — so our police was never short of information, only of this.
    """
    to_evader = _step_distances(board, evader, barriers)
    to_pursuer = _step_distances(board, pursuer, barriers)
    return sum(1 for cell, d in to_evader.items() if d < to_pursuer.get(cell, _UNREACHABLE))


def police_barrier(board, state, threat: Cell, weights: dict) -> Direction | None:
    """The cornering barrier to place now, or None (then: chase).

    Priority 1 — rule-46 strike: wall the believed cell itself when adjacent.
    Priority 2 — seal: the believed thief is pocketed (few exits) and one of
    those exits is adjacent to me. Never place a wall that strands ME.
    """
    my_exits = board.neighbors(state.position, state.barriers)
    placeable: list[tuple[Direction, Cell]] = []
    for direction in board.moves:
        target = board.step(state.position, direction, state.barriers)
        if target is None:
            continue
        if my_exits == [target]:
            continue  # sealing my own last exit strands the pursuit
        placeable.append((direction, target))
    for direction, target in placeable:
        if target == threat:
            return direction  # the strike: a barrier ON the thief's cell captures
    if exit_count(board, threat, state.barriers) <= weights["pocket_exits"]:
        threat_exits = set(board.neighbors(threat, state.barriers))
        for direction, target in placeable:
            if target in threat_exits:
                return direction  # seal the pocket one exit at a time
    return None
