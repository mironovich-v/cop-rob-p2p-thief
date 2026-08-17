"""TurnHandler: fold an opponent's TurnMessage into MY local view.

The only knowledge a peer ever gains about its opponent flows through here — the
NL hint, the scent grid, declared barriers, and claims. There is no shared board.
"""

from dataclasses import dataclass

from cop_thief_core.constants import Role
from cop_thief_core.domain.belief import BeliefGrid
from cop_thief_core.domain.own_state import OwnGameState
from cop_thief_core.domain.rules import GameRules
from cop_thief_core.domain.smell import SmellField
from cop_thief_core.protocol import TurnMessage


@dataclass
class IncomingOutcome:
    """Flags raised by an incoming message."""

    i_won: bool = False  # opponent confirmed my capture claim
    i_am_caught: bool = False  # opponent's capture claim hit my true cell
    opponent_won: bool = False  # opponent raised a win claim
    win_type: str | None = None
    claim_response: dict | None = None  # honest answer to attach to my next message
    ignored: bool = False  # stale / duplicate / out-of-order message — safely dropped


class TurnHandler:
    """Folds opponent messages into belief / smell / barrier knowledge."""

    def __init__(
        self, state: OwnGameState, belief: BeliefGrid, smell_field: SmellField, rules: GameRules
    ) -> None:
        self.state = state
        self.belief = belief
        self.smell_field = smell_field
        self.rules = rules
        self.history: list[dict] = []  # every received message, for GUI / replay
        self._last_step = 0  # highest opponent step folded in (monotonic guard)

    def process(self, message: TurnMessage) -> IncomingOutcome:
        # Opponent steps arrive strictly increasing (1, 2, 3, …). Any step we have
        # already seen or passed is stale / duplicate / out-of-order: drop it without
        # mutating belief, smell, or history, so a network re-send never double-counts.
        if message.step <= self._last_step:
            return IncomingOutcome(ignored=True)
        self._last_step = message.step
        self.history.append(message.to_dict())
        if message.barrier_placed:
            self.state.note_barrier(tuple(message.barrier_placed))
        # Opponent moved: spread belief, then sharpen it with the fresh scent.
        self.belief.diffuse()
        self.belief.observe_smell(message.smell_grid)
        self.smell_field.absorb(message.smell_grid)
        self.smell_field.decay_all()

        outcome = IncomingOutcome()
        if message.claim_response and message.claim_response.get("caught"):
            outcome.i_won = True
        if message.win_claim:
            outcome.opponent_won = True
            outcome.win_type = message.win_claim.get("type")
        if message.capture_claim:
            caught = self.rules.is_captured(self.state, tuple(message.capture_claim))
            outcome.claim_response = {"claim": list(message.capture_claim), "caught": caught}
            outcome.i_am_caught = caught
        # Rules 46-47: only the thief can see an enclosure capture, so it must be
        # SAID — the concession final names MY cell (≠ echoing a claimed cell).
        if (
            self.state.role is Role.THIEF
            and not outcome.i_am_caught
            and self.rules.is_enclosed(self.state)
        ):
            outcome.claim_response = {"claim": list(self.state.position), "caught": True}
            outcome.i_am_caught = True
        return outcome
