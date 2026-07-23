"""Opponent-location belief heatmap.

Nobody sees the opponent's true position: each peer keeps a probability grid over
the board, updated from received scent grids (Bayesian-ish) and diffused each turn
(the opponent moved one step). The diffusion neighbourhood must match how the
opponent can move — von Neumann (4) for orthogonal play, 3×3 king otherwise.
"""

from cop_thief_core.constants import Cell

_EPSILON = 1e-9


class BeliefGrid:
    """Probability distribution over an N×N board for the opponent's cell."""

    def __init__(self, board_size: int, smell_trust: float = 4.0, orthogonal: bool = False) -> None:
        self._size = board_size
        self._smell_trust = smell_trust
        if orthogonal:
            self._offsets = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
        else:
            self._offsets = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)]
        uniform = 1.0 / (board_size * board_size)
        self._probs = [[uniform] * board_size for _ in range(board_size)]

    def _normalize(self) -> None:
        total = sum(sum(row) for row in self._probs)
        if total < _EPSILON:  # degenerate: reset to uniform rather than divide by ~0
            uniform = 1.0 / (self._size * self._size)
            self._probs = [[uniform] * self._size for _ in range(self._size)]
            return
        self._probs = [[p / total for p in row] for row in self._probs]

    def observe_smell(self, cells: dict) -> None:
        """Scale each scented cell's probability by (1 + trust*intensity); no explicit
        position is supplied — belief is inferred from the decaying scent field alone."""
        for key, value in cells.items():
            row, col = (int(part) for part in key.split(","))
            if 0 <= row < self._size and 0 <= col < self._size:
                self._probs[row][col] *= 1.0 + self._smell_trust * value
        self._normalize()

    def diffuse(self) -> None:
        """Opponent moved one step: spread each cell's mass over its neighbourhood."""
        fresh = [[0.0] * self._size for _ in range(self._size)]
        for row in range(self._size):
            for col in range(self._size):
                mass = self._probs[row][col]
                if mass < _EPSILON:
                    continue
                targets = [
                    (row + dr, col + dc)
                    for dr, dc in self._offsets
                    if 0 <= row + dr < self._size and 0 <= col + dc < self._size
                ]
                share = mass / len(targets)
                for tr, tc in targets:
                    fresh[tr][tc] += share
        self._probs = fresh
        self._normalize()

    def exclude(self, cell: Cell) -> None:
        """Rule out a cell (e.g. I stand here and no capture happened)."""
        self._probs[cell[0]][cell[1]] = 0.0
        self._normalize()

    def most_likely(self) -> Cell:
        best, best_p = (0, 0), -1.0
        for row in range(self._size):
            for col in range(self._size):
                if self._probs[row][col] > best_p:
                    best, best_p = (row, col), self._probs[row][col]
        return best

    def as_matrix(self) -> list[list[float]]:
        return [row[:] for row in self._probs]
