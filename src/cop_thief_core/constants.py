"""Immutable domain constants: roles, move types, directions, and deltas.

These are physical/structural constants of the game, not tunable parameters —
tunable values (grid size, budgets, thresholds) live in config and are read via
``CFG`` (see PRD_config_constitution). STAY is modelled as ``MoveType.HOLD``,
never as a ``Direction``.
"""

from enum import StrEnum

Cell = tuple[int, int]  # (row, col)


class Role(StrEnum):
    """The two roles a peer can play; alternates across the series."""

    POLICE = "police"
    THIEF = "thief"


class MoveType(StrEnum):
    """A turn's action kind. BARRIER is police-only; HOLD is STAY."""

    MOVE = "MOVE"
    BARRIER = "BARRIER"
    HOLD = "HOLD"


class Direction(StrEnum):
    """The eight compass directions; games restrict to ORTHOGONAL by config."""

    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"


# Row/col delta per direction (origin top-left, row increases downward).
DELTAS: dict[Direction, Cell] = {
    Direction.N: (-1, 0),
    Direction.NE: (-1, 1),
    Direction.E: (0, 1),
    Direction.SE: (1, 1),
    Direction.S: (1, 0),
    Direction.SW: (1, -1),
    Direction.W: (0, -1),
    Direction.NW: (-1, -1),
}

ORTHOGONAL: tuple[Direction, ...] = (Direction.N, Direction.S, Direction.E, Direction.W)
DIAGONALS: frozenset[Direction] = frozenset(
    {Direction.NE, Direction.SE, Direction.SW, Direction.NW}
)
