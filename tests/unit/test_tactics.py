"""Tactical brains v2 (counted-game forensics, 2026-08-18): the v1 thief
argmaxed distance and self-cornered at (6,6) in every game; the v1 police
walled randomly and ping-ponged against a distance-keeper. v2: exit-freedom
dominates once distance is safe (capped), recent-trail penalty kills
oscillation, and the police walls to CORNER (rule-46 strike / exit sealing),
never at random."""

import random

from cop_thief_core.constants import MoveType, Role
from cop_thief_core.domain.belief import BeliefGrid
from cop_thief_core.domain.brains import PoliceBrain, ThiefBrain
from cop_thief_core.domain.own_state import OwnGameState
from cop_thief_core.domain.tactics import DEFAULTS, exit_count, thief_score

MOVE_SET = ["N", "S", "E", "W", "STAY"]


def _state(role, pos, barriers=(), trail=()):
    state = OwnGameState(role, pos, 7, MOVE_SET)
    for cell in barriers:
        state.note_barrier(cell)
    for cell in trail:
        state.log.append({"step": len(state.log) + 1, "position": list(cell),
                          "move": "MOVE:N", "unique_cells": 1, "barrier": None})
    return state


def _belief(peak):
    belief = BeliefGrid(7, 4.0)
    belief.observe_smell({f"{peak[0]},{peak[1]}": 0.9})
    return belief


def test_exit_count_corner_edge_center():
    board = _state(Role.THIEF, (3, 3)).board
    assert exit_count(board, (0, 0), set()) == 2
    assert exit_count(board, (0, 3), set()) == 3
    assert exit_count(board, (3, 3), set()) == 4


def test_thief_score_prefers_freedom_over_deep_corner():
    board = _state(Role.THIEF, (6, 5)).board
    threat, recent = (0, 0), set()
    corner = thief_score(board, (6, 6), threat, set(), recent, DEFAULTS)
    open_cell = thief_score(board, (5, 5), threat, set(), recent, DEFAULTS)
    assert open_cell > corner  # distance is capped; the corner's 2 exits lose


def test_thief_brain_never_enters_the_corner_trap():
    """The exact counted-game death: at (6,5), threat far away, v1 chose (6,6).

    STAY is now in the option set, and here it is the roomiest answer of all
    (territory 27, against 26/25 for the open steps and 21 for the corner), so
    a HOLD is a correct outcome. What must never happen is the corner.
    """
    state = _state(Role.THIEF, (6, 5))
    brain = ThiefBrain(rng=random.Random(1))
    move_type, direction = brain._decide_move(state, _belief((0, 0)), 14)
    if move_type is MoveType.HOLD:
        return                                        # stood still: not the corner
    assert state.board.step(state.position, direction) != (6, 6)


def test_thief_still_flees_an_adjacent_threat():
    state = _state(Role.THIEF, (3, 3))
    brain = ThiefBrain(rng=random.Random(1))
    _, direction = brain._decide_move(state, _belief((3, 2)), 14)
    target = state.board.step(state.position, direction)
    assert state.board.distance(target, (3, 2)) > 1  # away, never toward


def test_thief_recent_trail_penalty_breaks_oscillation():
    board = _state(Role.THIEF, (5, 6)).board
    threat = (0, 0)
    fresh = thief_score(board, (5, 5), threat, set(), set(), DEFAULTS)
    stale = thief_score(board, (5, 5), threat, set(), {(5, 5)}, DEFAULTS)
    assert fresh > stale


def test_police_strikes_rule46_barrier_when_adjacent_to_peak():
    state = _state(Role.POLICE, (3, 2))
    brain = PoliceBrain(rng=random.Random(1), tactics={"spend_barriers": True})
    move_type, direction = brain._decide_move(state, _belief((3, 3)), 14)
    assert move_type is MoveType.BARRIER
    assert state.board.step(state.position, direction) == (3, 3)  # wall ON the peak


def test_police_seals_a_pocketed_thiefs_exit():
    # Believed thief at (6,6) (2 exits); we stand at (5, 5): (5,6) and (6,5)
    # are its exits' neighbours... we are adjacent to NEITHER exit directly —
    # place from (6, 5): sealing E puts a wall on (6, 6)? that's the strike.
    # Pocket case: we at (4, 6), thief believed (6, 6) with (5,6) open:
    state = _state(Role.POLICE, (4, 6), barriers=[(6, 5)])
    brain = PoliceBrain(rng=random.Random(1), tactics={"spend_barriers": True})
    move_type, direction = brain._decide_move(state, _belief((6, 6)), 14)
    assert move_type is MoveType.BARRIER
    assert state.board.step(state.position, direction, state.barriers) == (5, 6)


def test_police_chases_in_the_open_and_never_walls_randomly():
    brain = PoliceBrain(rng=random.Random(1))
    for _ in range(20):  # v1 walled ~15% of rolls; v2 must never wall the open
        state = _state(Role.POLICE, (1, 1))
        move_type, direction = brain._decide_move(state, _belief((5, 5)), 14)
        assert move_type is MoveType.MOVE
        target = state.board.step(state.position, direction)
        assert state.board.distance(target, (5, 5)) == 7  # strictly closing


def test_police_never_seals_its_own_last_exit():
    # Cop in a pocket itself: (0,0) with (1,0) walled; only exit (0,1). The
    # believed thief sits at (0, 2) — sealing (0,1) would gain, but strands us.
    state = _state(Role.POLICE, (0, 0), barriers=[(1, 0)])
    brain = PoliceBrain(rng=random.Random(1))
    move_type, direction = brain._decide_move(state, _belief((0, 2)), 14)
    target = state.board.step(state.position, direction, state.barriers)
    assert (move_type, target) == (MoveType.MOVE, (0, 1))  # move, don't self-strand
