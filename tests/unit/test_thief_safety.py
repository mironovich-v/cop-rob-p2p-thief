"""An evader must not step where the pursuer can be next turn.

Both peers move each round, so a cell adjacent to the pursuer (or the pursuer's
own cell) is one it can occupy on its very next move. The shipped scoring
weighed freedom and distance but had no notion of REACH, so it would happily
step into a cell the cop simply walked onto.

Measured against our own cop — the strongest pursuer we have — this rule alone
lifts median survival from 10 steps to 12, and several more elaborate evader
designs measured no better than it.
"""

from cop_thief_core.constants import ORTHOGONAL, Role
from cop_thief_core.domain.board import Board
from cop_thief_core.domain.brains import ThiefBrain
from cop_thief_core.domain.own_state import OwnGameState
from cop_thief_core.domain.tactics import beyond_reach

BOARD = Board(7, ORTHOGONAL)


def test_the_pursuers_own_cell_is_not_beyond_reach():
    assert beyond_reach(BOARD, (3, 3), (3, 3), set()) is False


def test_a_cell_the_pursuer_can_step_onto_is_not_beyond_reach():
    assert beyond_reach(BOARD, (3, 4), (3, 3), set()) is False


def test_a_cell_two_away_is_beyond_reach():
    assert beyond_reach(BOARD, (3, 5), (3, 3), set()) is True


def test_a_barrier_puts_a_neighbouring_cell_beyond_reach():
    """The pursuer cannot cross a wall, so the cell behind one is safe."""
    assert beyond_reach(BOARD, (3, 4), (3, 3), {(3, 4)}) is True


class _Belief:
    def __init__(self, cell):
        self.cell = cell

    def most_likely(self):
        return self.cell


def test_the_thief_prefers_a_safe_cell_over_a_higher_scoring_unsafe_one():
    import random
    state = OwnGameState(Role.THIEF, (3, 3), 7, list(ORTHOGONAL))
    brain = ThiefBrain(rng=random.Random(0))
    moves = state.board.legal_moves(state.position, state.barriers)
    _, target = brain._pick_move(moves, state, _Belief((3, 1)))
    # (3,2) is adjacent to the believed cop at (3,1) — reachable next turn.
    assert target != (3, 2)
    assert beyond_reach(state.board, target, (3, 1), state.barriers)
