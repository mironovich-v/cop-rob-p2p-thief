"""The evader must be able to stand still, and must do so when cornered.

Every test here is anchored to the imreeyal counted series (2026-08-23), where
we lost all six sub-games. The reconstruction of sub-game 2, from our own sealed
log and the scent peaks in their turn messages:

    step   our cell   their cop   distance
      8     (4,6)       (3,5)        2      safe
      9     (5,6)       (4,5)        2      safe
     10     (6,6)       (5,5)        2      safe   <- cornered
     11     (6,5)       (6,5)        0      CAPTURED

Staying at (6,6) was safe. The evader could not choose it.
"""

import random

from cop_thief_core.constants import ORTHOGONAL, MoveType, Role
from cop_thief_core.domain.evader import ThiefBrain
from cop_thief_core.domain.own_state import OwnGameState


class _Belief:
    def __init__(self, cell):
        self.cell = cell

    def most_likely(self):
        return self.cell


def _thief(cell, barriers=()):
    state = OwnGameState(Role.THIEF, cell, 7, list(ORTHOGONAL) + ["STAY"])
    state.barriers.update(barriers)
    return state


def _decide(state, threat, seed=1):
    return ThiefBrain(rng=random.Random(seed))._decide_move(state, _Belief(threat), 14)


def test_the_counted_death_position_now_holds_instead_of_stepping_into_reach():
    """g2 step 10: at (6,6) with the cop at (5,5), both steps are fatal."""
    state = _thief((6, 6))
    move_type, direction = _decide(state, (5, 5))
    assert move_type is MoveType.HOLD, "stepped out of the corner into the cop's reach"
    assert direction is None


def test_it_holds_for_every_seed_in_that_position():
    """Not luck: the corner escape must not depend on the tie-break RNG."""
    for seed in range(25):
        move_type, _ = _decide(_thief((6, 6)), (5, 5), seed=seed)
        assert move_type is MoveType.HOLD


def test_stay_is_offered_alongside_the_legal_moves():
    """The option set must contain the cell we already stand on."""
    state = _thief((3, 3))
    brain = ThiefBrain(rng=random.Random(0))
    options = list(state.board.legal_moves(state.position, state.barriers))
    options.append((None, state.position))
    assert (None, (3, 3)) in options
    assert brain._pick_move(options, state, _Belief((0, 0))) in options


def test_it_still_runs_when_running_is_better_than_standing():
    """A cop one step away makes STAY fatal: standing still must not be dogma."""
    state = _thief((3, 3))
    move_type, direction = _decide(state, (3, 2))
    assert move_type is MoveType.MOVE
    assert state.board.distance(state.board.step((3, 3), direction), (3, 2)) > 1


def test_it_refuses_a_cell_the_threat_can_land_on():
    """The core safety rule, unchanged: never end inside the pursuer's reach."""
    state = _thief((4, 4))
    move_type, direction = _decide(state, (4, 2))
    landed = state.position if move_type is MoveType.HOLD else state.board.step((4, 4), direction)
    assert landed not in {(4, 2), *state.board.neighbors((4, 2), set())}


def test_it_prefers_room_to_the_corner_when_the_threat_is_far():
    """Exits scored a corner and an open cell alike; territory does not.

    All three captures against us were on an edge (row 6 twice, column 0 once),
    which is the exit-count term measured (imreeyal §1b).
    """
    state = _thief((5, 5))
    move_type, direction = _decide(state, (0, 0))
    landed = state.position if move_type is MoveType.HOLD else state.board.step((5, 5), direction)
    assert landed != (6, 6)


def test_a_stale_belief_still_does_not_get_it_killed():
    """Robustness key: with the peak a move old, avoid the whole envelope.

    Arena, 96 unseen seeds: shipped evader caught 91/96 by a containment cop on
    a one-move-stale belief; this one, 0/96.
    """
    state = _thief((3, 3))
    move_type, direction = _decide(state, (3, 1))     # believed 2 away; could be 1
    landed = state.position if move_type is MoveType.HOLD else state.board.step((3, 3), direction)
    assert state.board.distance(landed, (3, 1)) >= 2
