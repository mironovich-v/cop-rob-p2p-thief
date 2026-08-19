"""Scent / pheromone field: each peer emits a local M×M grid and absorbs the
opponent's. Radial emission falls off with Chebyshev distance; every game step all
known intensities decay by a configured constant (clamped to 0, rounded to 3).
Only positive intensities cross the wire as {"r,c": value} — never a position
(hidden-opponent model). This is the CORE construction pinned by SPEC §5.
"""

from cop_thief_core.constants import Cell


class SmellField:
    """Board-wide scent intensities known to one peer, with M×M radial emission."""

    def __init__(self, board_size: int, grid_size: int, decay: float, min_center: float) -> None:
        self._board_size = board_size
        self._grid_size = grid_size
        self._decay = decay
        self._min_center = min_center
        self._values: dict[Cell, float] = {}

    def _radial(self, center: Cell, intensity: float) -> dict[Cell, float]:
        half = self._grid_size // 2
        falloff = intensity / (half + 1)
        out: dict[Cell, float] = {}
        for dr in range(-half, half + 1):
            for dc in range(-half, half + 1):
                cell = (center[0] + dr, center[1] + dc)
                if 0 <= cell[0] < self._board_size and 0 <= cell[1] < self._board_size:
                    out[cell] = round(max(0.0, intensity - falloff * max(abs(dr), abs(dc))), 3)
        return out

    def deposit(self, center: Cell, intensity: float) -> None:
        """Lay a fresh radial scent around ``center`` into the trail (max-merge)."""
        if intensity < self._min_center:
            raise ValueError(
                f"Center intensity {intensity} below required minimum {self._min_center}"
            )
        for cell, value in self._radial(center, intensity).items():
            self._values[cell] = max(self._values.get(cell, 0.0), value)

    def absorb(self, cells: dict) -> None:
        """Merge a received scent map {'r,c': intensity} into the field (max wins)."""
        for key, value in cells.items():
            row, col = (int(part) for part in key.split(","))
            if 0 <= row < self._board_size and 0 <= col < self._board_size:
                self._values[(row, col)] = max(self._values.get((row, col), 0.0), value)

    def decay_all(self) -> None:
        """One game step passed: every intensity drops by the decay constant."""
        for cell in list(self._values):
            self._values[cell] = max(0.0, round(self._values[cell] - self._decay, 3))

    def intensity_at(self, cell: Cell) -> float:
        return self._values.get(cell, 0.0)

    def strongest_cell(self) -> Cell | None:
        """The most fragrant known cell — the naive opponent-location guess."""
        if not self._values:
            return None
        cell, value = max(self._values.items(), key=lambda item: item[1])
        return cell if value > 0.0 else None

    def snapshot(self) -> dict[str, float]:
        """Serializable wire copy: {'r,c': intensity} for positive intensities only."""
        return {f"{r},{c}": v for (r, c), v in self._values.items() if v > 0.0}
