"""The pursuer must take away ANSWERS, not floor space.

Six live windows against imreeyal converted nothing while the cop minimised the
thief's territory. Their §2a explains it: a competent evader keeps three exits
forever, so the pocket-seal trigger never fires and the cop shadows at distance
2 while the region shrinks and grows again. Our own earlier experiment had
already ruled out information as the cause — an ORACLE cop holding the thief's
true cell captured 2/16 against the blind cop's 3/16.
"""

import random

from cop_thief_core.constants import ORTHOGONAL, MoveType, Role
from cop_thief_core.domain.own_state import OwnGameState
from cop_thief_core.domain.pursuer import PoliceBrain
from cop_thief_core.domain.tactics import escapes


class _Belief:
    def __init__(self, cell):
        self.cell = cell

    def most_likely(self):
        return self.cell


def _cop(cell, barriers=()):
    state = OwnGameState(Role.POLICE, cell, 7, list(ORTHOGONAL) + ["STAY"])
    state.barriers.update(barriers)
    return state


def _decide(state, threat, seed=1, barriers_max=14):
    return PoliceBrain(rng=random.Random(seed))._decide_move(
        state, _Belief(threat), barriers_max)


def test_escapes_counts_replies_outside_my_reach():
    board = _cop((0, 0)).board
    # Adjacent: the evader's own cell is covered, but it can step away.
    assert escapes(board, (3, 2), (3, 3), set()) > 0
    # Sitting ON it covers the cell and all four neighbours: nothing escapes.
    assert escapes(board, (3, 3), (3, 3), set()) == 0


def test_escapes_falls_as_the_evader_is_pinned_to_a_corner():
    """The metric must reward the shape that actually converts."""
    board = _cop((0, 0)).board
    open_field = escapes(board, (3, 2), (3, 3), set())
    cornered = escapes(board, (1, 0), (0, 0), set())
    assert cornered < open_field


def test_it_lands_on_the_evader_when_the_evader_is_reachable():
    """The whole point: an adjacent believed cell must be taken, not circled."""
    state = _cop((3, 2))
    move_type, direction = _decide(state, (3, 3), barriers_max=0)
    assert move_type is MoveType.MOVE
    assert state.board.step((3, 2), direction) == (3, 3)


def test_it_prefers_the_containing_cell_over_the_merely_closer_one():
    """Distance is the tie-break, never the objective."""
    state = _cop((0, 0))
    chosen = []
    for seed in range(15):
        move_type, direction = _decide(_cop((0, 0)), (3, 3), seed=seed, barriers_max=0)
        cell = state.position if move_type is MoveType.HOLD else state.board.step(
            (0, 0), direction)
        chosen.append(escapes(state.board, cell, (3, 3), set()))
    best = min(escapes(state.board, c, (3, 3), set())
               for _, c in state.board.legal_moves((0, 0), set()))
    assert min(chosen) == best


def test_the_rule_46_strike_is_still_taken():
    """A barrier placed ON the believed cell is a capture — never give it up."""
    state = _cop((3, 2))
    move_type, direction = _decide(state, (3, 3))
    assert move_type in (MoveType.BARRIER, MoveType.MOVE)
    assert state.board.step((3, 2), direction) == (3, 3)


def test_stay_is_available_to_the_pursuer_too():
    """STAY is in the signed move set for both roles; the option set must hold it."""
    state = _cop((3, 3))
    brain = PoliceBrain(rng=random.Random(0))
    options = list(state.board.legal_moves((3, 3), set())) + [(None, (3, 3))]
    assert brain._pick_move(options, state, _Belief((0, 0))) in options


def test_our_last_exit_is_walked_through_not_walled_shut():
    """Sealing ourselves in ends the pursuit, even when the seal would be a strike.

    Walls leave (3,4) as our ONLY exit and the believed thief stands there. The
    rule-46 strike would wall exactly that cell — legal, but it strands us. The
    guard must decline it and take the capture by stepping instead.
    """
    walls = {(2, 3), (4, 3), (3, 2)}
    state = _cop((3, 3), barriers=walls)
    move_type, direction = _decide(state, (3, 4))
    assert move_type is MoveType.MOVE
    assert state.board.step((3, 3), direction, state.barriers) == (3, 4)
