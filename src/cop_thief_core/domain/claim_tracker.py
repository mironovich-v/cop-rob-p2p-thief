"""Track the police's own declared position out of its capture claims.

Co-location is the only way a cop takes the thief, so a conforming cop's
`capture_claim` names the cell it is standing on — its exact position, published
on the wire every turn it moves. Our thief ignored it and fled a scent estimate
instead, which lags by construction: scent marks where the opponent *was*.
Measured on a live-shaped game, the thief's believed threat matched the cop's
true cell on 3 of 14 turns, and the shipped evader scoring given the true cell
instead survives 6/10 against a cornering cop where it otherwise survives 1/10.

The claim is trusted only when it BEHAVES like a position: a cop covers at most
one cell per step, so each claim must be reachable from the last one within the
steps that elapsed. A cop whose claims are guesses about the thief wanders
further than that, fails the test, and is ignored — belief falls back to scent.
Nothing here assumes the opponent is honest; it assumes physics, and checks.
"""

from cop_thief_core.constants import Cell


class ClaimTracker:
    """Turns a sequence of capture claims into a trusted opponent position."""

    def __init__(self) -> None:
        self._cell: Cell | None = None
        self._step: int | None = None

    def accept(self, cell: Cell, step: int, board) -> Cell | None:
        """The cell to believe the cop is on, or None to keep the scent estimate.

        A refused claim still re-anchors: a cop we merely mis-tracked earns trust
        again on its next consistent step instead of being written off for the
        rest of the game.
        """
        if not board.in_bounds(cell):
            return None
        previous, previous_step = self._cell, self._step
        self._cell, self._step = cell, step
        if previous is None or previous_step is None:
            return None  # one claim proves nothing: anchor, do not steer
        elapsed = max(1, step - previous_step)
        return cell if board.distance(cell, previous) <= elapsed else None
