"""Tests for OwnGameState (PRD_game_state, TODO slice 1.2)."""

from cop_thief_core.constants import Direction, MoveType, Role, directions_from_move_set
from cop_thief_core.domain.own_state import OwnGameState

ORTHO = ["N", "S", "E", "W", "STAY"]


def _thief(start=(2, 2)):
    return OwnGameState(Role.THIEF, start, 5, ORTHO)


def _police(start=(2, 2)):
    return OwnGameState(Role.POLICE, start, 5, ORTHO)


def test_directions_from_move_set_drops_stay():
    assert directions_from_move_set(ORTHO) == (Direction.N, Direction.S, Direction.E, Direction.W)
    assert directions_from_move_set(None) is None


def test_initial_state():
    state = _thief()
    assert state.position == (2, 2)
    assert state.visited == {(2, 2)}
    assert state.unique_cells == 1
    assert state.step_number == 0
    assert state.my_barriers == 0
    assert state.log == []


def test_legal_move_updates_position_and_log():
    state = _thief()
    assert state.apply_move(MoveType.MOVE, Direction.N) is True
    assert state.position == (1, 2)
    assert (1, 2) in state.visited
    assert state.step_number == 1
    entry = state.log[-1]
    assert entry == {
        "step": 1,
        "position": [1, 2],
        "move": "MOVE:N",
        "unique_cells": 2,
        "barrier": None,
    }


def test_illegal_move_off_board_leaves_state_unchanged():
    state = _thief(start=(0, 0))
    assert state.apply_move(MoveType.MOVE, Direction.N) is False
    assert state.position == (0, 0)
    assert state.step_number == 0
    assert state.log == []


def test_move_into_barrier_blocked():
    state = _thief()
    state.note_barrier((1, 2))
    assert state.apply_move(MoveType.MOVE, Direction.N) is False
    assert state.position == (2, 2)


def test_hold_advances_step_without_visiting():
    state = _thief()
    assert state.apply_move(MoveType.HOLD, None) is True
    assert state.position == (2, 2)
    assert state.unique_cells == 1
    assert state.step_number == 1
    assert state.log[-1]["move"] == "HOLD:-"


def test_police_places_barrier_without_moving():
    state = _police()
    assert state.apply_move(MoveType.BARRIER, Direction.E, barriers_max=5) is True
    assert state.position == (2, 2)  # stays put
    assert (2, 3) in state.barriers
    assert state.my_barriers == 1
    assert state.log[-1]["barrier"] == [2, 3]
    assert state.last_barrier() == (2, 3)


def test_thief_cannot_place_barrier():
    state = _thief()
    assert state.apply_move(MoveType.BARRIER, Direction.E, barriers_max=5) is False
    assert state.my_barriers == 0
    assert state.log == []


def test_barrier_budget_exhausted():
    state = _police()
    assert state.apply_move(MoveType.BARRIER, Direction.E, barriers_max=0) is False
    assert state.my_barriers == 0


def test_barrier_off_board_rejected():
    state = _police(start=(0, 0))
    assert state.apply_move(MoveType.BARRIER, Direction.N, barriers_max=5) is False
    assert state.my_barriers == 0


def test_last_barrier_none_after_plain_move():
    state = _police()
    state.apply_move(MoveType.MOVE, Direction.S)
    assert state.last_barrier() is None


def test_revisiting_cell_keeps_unique_count():
    state = _thief()
    state.apply_move(MoveType.MOVE, Direction.N)  # (1,2)
    state.apply_move(MoveType.MOVE, Direction.S)  # back to (2,2), already visited
    assert state.unique_cells == 2
    assert state.step_number == 2
