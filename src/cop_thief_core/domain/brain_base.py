"""Shared brain machinery: the decision record and the policy base class.

The MOVE is chosen by a pure-Python strategy (the student's seam) — the LLM is
NEVER consulted for it. The LLM only writes optional trash-talk banter; a null
provider yields an empty, truthful hint so the move path is complete and the
game runs fast, free and offline.

Split out of ``brains.py`` when the role brains grew past the 150-line file
limit; ``brains.py`` still re-exports everything, so every existing import and
every ``strategy.thief_class`` config string keeps working.

Student override points (see docs/PRD_strategy_brains):
  * ``_pick_move(moves, state, belief)`` — pick a legal move (the core heuristic).
  * ``_decide_move(state, belief, barriers_max)`` — full move incl. BARRIER (police).
"""

import random
import time
from dataclasses import dataclass

from cop_thief_core.constants import VERDICT_TRUTH, Direction, MoveType, Role
from cop_thief_core.domain.belief import BeliefGrid
from cop_thief_core.domain.own_state import OwnGameState
from cop_thief_core.domain.tactics import DEFAULTS


@dataclass
class Decision:
    """What the brain chose this turn (move = Python, hint = trash talk)."""

    move_type: MoveType
    direction: Direction | None
    hint: str
    verdict: str
    fallback: bool = False
    random_move: bool = False
    response_seconds: float = 0.0
    prompt_text: str = ""
    reasoning: str = ""


class _NullTrash:
    """Default zero-token banter: an empty, truthful hint (real provider = Stage 4)."""

    def say(self, role, state, belief, setting, opponent_hint, deadline_seconds=None):
        return "", VERDICT_TRUTH, "", ""


class BrainBase:
    """Decision policy. ``_pick_move`` / ``_decide_move`` is the student's seam;
    ``decide`` chooses the move in pure Python and never asks the LLM for it."""

    role: Role

    def __init__(self, llm=None, rng: random.Random | None = None, trash=None,
                 tactics: dict | None = None) -> None:
        self._llm = llm  # kept for an opt-in trash-talk provider; never used for a move
        self._rng = rng or random.Random()
        self._trash = trash or _NullTrash()
        self._tactics = {**DEFAULTS, **(tactics or {})}

    def decide(
        self,
        state: OwnGameState,
        belief: BeliefGrid,
        opponent_hint: str,
        setting: str,
        barriers_max: int,
        deadline_seconds: float | None = None,
        short_threshold: float = 0.0,
    ) -> Decision:
        # 1) MOVE — pure Python; the LLM is NEVER consulted, so it is instant/free.
        move_type, direction = self._decide_move(state, belief, barriers_max)
        # 2) HINT — trash talk (template/null by default; opt-in LLM in Stage 4).
        started = time.perf_counter()
        hint, verdict, reasoning, prompt = self._trash.say(
            self.role, state, belief, setting, opponent_hint, deadline_seconds
        )
        return Decision(
            move_type,
            direction,
            hint,
            verdict,
            fallback=(move_type is MoveType.HOLD and direction is None),
            reasoning=reasoning,
            prompt_text=prompt,
            response_seconds=round(time.perf_counter() - started, 2),
        )

    def _decide_move(
        self, state: OwnGameState, belief: BeliefGrid, barriers_max: int
    ) -> tuple[MoveType, Direction | None]:
        moves = state.board.legal_moves(state.position, state.barriers)
        if not moves:
            return MoveType.HOLD, None
        direction, _ = self._pick_move(moves, state, belief)
        return MoveType.MOVE, direction

    def _pick_move(self, moves, state, belief):
        raise NotImplementedError
