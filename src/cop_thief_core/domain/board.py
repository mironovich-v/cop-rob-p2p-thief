"""Discrete N×N board geometry: bounds, movement, barriers, and distance.

Pure and stateless — each peer holds its own ``Board`` configured with the agreed
``move_set``. Barriers block movement for both players. The distance metric
follows the move set: Chebyshev when diagonals are allowed (king), else Manhattan.
"""

from cop_thief_core.constants import DELTAS, DIAGONALS, Cell, Direction


class Board:
    """A square grid with a configurable set of allowed step directions."""

    def __init__(self, size: int, moves: tuple[Direction, ...] | None = None) -> None:
        if size <= 0:
            raise ValueError("board size must be a positive integer")
        self._size = size
        # Default to all eight king directions; games pass ORTHOGONAL.
        self._moves: tuple[Direction, ...] = tuple(moves) if moves is not None else tuple(Direction)

    @property
    def size(self) -> int:
        return self._size

    @property
    def moves(self) -> tuple[Direction, ...]:
        return self._moves

    @property
    def diagonal(self) -> bool:
        """True if any allowed move is diagonal (selects the distance metric)."""
        return any(move in DIAGONALS for move in self._moves)

    def in_bounds(self, cell: Cell) -> bool:
        row, col = cell
        return 0 <= row < self._size and 0 <= col < self._size

    def distance(self, a: Cell, b: Cell) -> int:
        """Chebyshev distance for king moves, Manhattan for orthogonal."""
        drow, dcol = abs(a[0] - b[0]), abs(a[1] - b[1])
        return max(drow, dcol) if self.diagonal else drow + dcol

    def step(self, origin: Cell, direction: Direction, barriers: set[Cell] | None = None) -> Cell | None:
        """The target cell of one step, or None if off-board or blocked."""
        drow, dcol = DELTAS[direction]
        target = (origin[0] + drow, origin[1] + dcol)
        if not self.in_bounds(target):
            return None
        if barriers and target in barriers:
            return None
        return target

    def neighbors(self, cell: Cell, barriers: set[Cell] | None = None) -> list[Cell]:
        """All cells reachable from ``cell`` in one allowed, unblocked step."""
        return [t for t in (self.step(cell, d, barriers) for d in self._moves) if t is not None]

    def legal_moves(self, origin: Cell, barriers: set[Cell] | None = None) -> list[tuple[Direction, Cell]]:
        """(direction, target) pairs for every legal step from ``origin``."""
        moves: list[tuple[Direction, Cell]] = []
        for direction in self._moves:
            target = self.step(origin, direction, barriers)
            if target is not None:
                moves.append((direction, target))
        return moves
