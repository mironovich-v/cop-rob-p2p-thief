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

STAY = "STAY"  # config move-set token for a HOLD; not a Direction

# Terminal-outcome tokens (anything else scores as a technical loss, 0/0).
RESULT_CAPTURE = "capture"
RESULT_SURVIVAL = "survival"
RESULT_DISPUTED = "disputed_capture"  # capture whose audit corroboration failed

NONCE_BYTES = 16  # secrets.token_hex(NONCE_BYTES) -> a 32-hex-char nonce

# A hint's self-declared honesty (sealed into the commit and revealed at audit).
VERDICT_TRUTH = "truth"
VERDICT_LIE = "lie"

FINAL_CAUGHT_HINT = "You got me."  # the mandatory final message once captured


def directions_from_move_set(move_set: list[str] | None) -> tuple[Direction, ...] | None:
    """Map a config ``move_set`` (e.g. ["N","S","E","W","STAY"]) to Directions.

    ``STAY`` is a HOLD, not a direction, so it is dropped. ``None`` returns
    ``None`` so the board falls back to its king-move default.
    """
    if move_set is None:
        return None
    names = {direction.value for direction in Direction}
    return tuple(Direction(token) for token in move_set if token in names)
