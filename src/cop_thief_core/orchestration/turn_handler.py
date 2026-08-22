"""TurnHandler: fold an opponent's TurnMessage into MY local view.

The only knowledge a peer ever gains about its opponent flows through here — the
NL hint, the scent grid, declared barriers, and claims. There is no shared board.

Delivery contract (league SPEC §7.1, PROMOTED): HTTP is at-least-once, so a
correct client redelivers. Dedup keys on the COMMIT — the one field a retry
cannot vary. A same-commit redelivery absorbs silently; a DIFFERENT commit for a
played step is equivocation (two sealed moves for one step — tampering evidence,
kept loud); one step ahead buffers within the reorder window and replays in
order; past the window is the flood rule; below `next` and never played is
discarded. Transport tolerance, no rules tolerance.
"""

from dataclasses import dataclass

from cop_thief_core.constants import RESULT_TAMPER, RESULT_TECHNICAL, Role
from cop_thief_core.domain.belief import BeliefGrid
from cop_thief_core.domain.claim_tracker import ClaimTracker, peak_cell
from cop_thief_core.domain.own_state import OwnGameState
from cop_thief_core.domain.rules import GameRules
from cop_thief_core.domain.smell import SmellField
from cop_thief_core.protocol import TurnMessage
from cop_thief_core.protocol.messages import validate_turn_values


@dataclass
class IncomingOutcome:
    """Flags raised by an incoming message."""

    i_won: bool = False  # opponent confirmed my capture claim
    i_am_caught: bool = False  # opponent's capture claim hit my true cell
    opponent_won: bool = False  # opponent raised a win claim
    win_type: str | None = None
    claim_response: dict | None = None  # honest answer to attach to my next message
    ignored: bool = False  # absorbed / buffered / discarded — no state change
    settle: str | None = None  # loud verdict: equivocation / flood ends the game


class TurnHandler:
    """Folds opponent messages into belief / smell / barrier knowledge."""

    def __init__(self, state, belief, smell_field, rules, reorder_window: int = 1) -> None:
        self.state: OwnGameState = state
        self.belief: BeliefGrid = belief
        self.smell_field: SmellField = smell_field
        self.rules: GameRules = rules
        self.history: list[dict] = []  # every applied message, for GUI / replay
        self.evidence: list[dict] = []  # loud events (equivocation), for the record
        self._window = reorder_window  # 0 is nonconformant (retry race = violation)
        self._played: dict[int, str] = {}  # step -> commit that was applied
        self._buffer: dict[int, TurnMessage] = {}
        self._claims = ClaimTracker()  # the cop's own declared cell, when credible
        self._scent = ClaimTracker()  # the scent map's peak = the sender's cell

    @property
    def _next(self) -> int:
        return max(self._played, default=0) + 1

    @property
    def received_commits(self) -> dict[int, str]:
        """step -> commit that arrived live: the audit's binding source (§5d)."""
        return dict(self._played)

    def receive(self, raw: dict) -> IncomingOutcome:
        """Parse + value-validate an inbound raw dict, then process it.

        A malformed or invalid-valued turn is REFUSED before any state change
        (never defaulted, never a crash) — the sender's deadline keeps burning.
        """
        try:
            message = validate_turn_values(TurnMessage.from_dict(raw))
        except (TypeError, ValueError):
            return IncomingOutcome(ignored=True)  # refused: adversarial input
        return self.process(message)

    def process(self, message: TurnMessage) -> IncomingOutcome:
        step = message.step
        if step in self._played:
            if message.commit == self._played[step]:
                return IncomingOutcome(ignored=True)  # an HTTP retry, by design
            self.evidence.append({"kind": "equivocation", "step": step,
                                  "seen": self._played[step], "got": message.commit})
            return IncomingOutcome(settle=RESULT_TAMPER)
        if step < self._next:
            return IncomingOutcome(ignored=True)  # below next, never played: discard
        if step > self._next:
            if step - self._next > self._window:
                return IncomingOutcome(settle=RESULT_TECHNICAL)  # the flood rule
            self._buffer[step] = message
            return IncomingOutcome(ignored=True)  # held for in-order replay
        outcome = self._fold(message)
        while self._next in self._buffer:  # the gap filled: replay in step order
            outcome = self._merge(outcome, self._fold(self._buffer.pop(self._next)))
        return outcome

    @staticmethod
    def _merge(first: IncomingOutcome, second: IncomingOutcome) -> IncomingOutcome:
        second.i_won = first.i_won or second.i_won
        second.i_am_caught = first.i_am_caught or second.i_am_caught
        second.opponent_won = first.opponent_won or second.opponent_won
        second.win_type = second.win_type or first.win_type
        second.claim_response = second.claim_response or first.claim_response
        return second

    def _fold(self, message: TurnMessage) -> IncomingOutcome:
        self._played[message.step] = message.commit
        self.history.append(message.to_dict())
        if message.barrier_placed:
            self.state.note_barrier(tuple(message.barrier_placed))
        # Opponent moved: spread belief, then sharpen it with the fresh scent.
        self.belief.diffuse()
        self.belief.observe_smell(message.smell_grid)
        # The sender deposits on the cell it STANDS on just before sending, so
        # the map's peak is that cell exactly — an observation the probabilistic
        # update smears away. Trusted only while the peaks walk like a peer.
        sighting = peak_cell(message.smell_grid)
        if sighting is not None:
            seen = self._scent.accept(sighting, message.step, self.state.board)
            if seen is not None:
                self.belief.observe_declared(seen)
        # A cop claims co-location, so its claim names the cell it STANDS on —
        # evidence about NOW, unlike scent, which marks where it was. Trusted
        # only while the claims walk like a cop (ClaimTracker).
        if message.capture_claim:
            declared = self._claims.accept(
                tuple(message.capture_claim), message.step, self.state.board)
            if declared is not None:
                self.belief.observe_declared(declared)
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
