"""Win / terminal conditions, evaluated on a peer's OWN state (no referee).

The thief judges its own survival claim; the police issues capture claims and the
thief answers honestly from its true position. A false answer is later exposed by
the cryptographic audit (the sealed true state is revealed), forfeiting the game.
"""

from cop_thief_core.constants import RESULT_SURVIVAL, Cell
from cop_thief_core.domain.own_state import OwnGameState


class GameRules:
    """Configured terminal conditions for one sub-game."""

    def __init__(self, max_steps: int) -> None:
        self.max_steps = max_steps

    def thief_result(self, state: OwnGameState) -> str | None:
        """The thief's win claim, if any: 'survival' once the step cap is reached."""
        if state.step_number >= self.max_steps:
            return RESULT_SURVIVAL
        return None

    @staticmethod
    def is_captured(state: OwnGameState, claim: Cell) -> bool:
        """Honest answer to a capture claim: is my true position the claimed cell?"""
        return state.position == tuple(claim)

    @staticmethod
    def is_enclosed(state: OwnGameState) -> bool:
        """Capture by enclosure (book rules 46-47): a barrier sits on my own cell,
        or every orthogonal neighbour is a barrier / off the board. STAY does not
        rescue — an ending only the thief can see, so the thief must SAY it
        (league SPEC §3.1: silent settling forks the game into capture-vs-timeout).
        """
        if state.position in state.barriers:
            return True
        return not state.board.neighbors(state.position, state.barriers)
