"""Tests for GameRules terminal conditions (PRD_game_state, TODO slice 1.3)."""

from cop_thief_core.constants import RESULT_SURVIVAL, Role
from cop_thief_core.domain.own_state import OwnGameState
from cop_thief_core.domain.rules import GameRules

MOVE_SET = ["N", "S", "E", "W", "STAY"]


def _state(step=0, pos=(2, 2)):
    state = OwnGameState(Role.THIEF, pos, 5, MOVE_SET)
    state.step_number = step
    return state


def test_thief_result_none_before_threshold():
    assert GameRules(35).thief_result(_state(step=34)) is None


def test_thief_result_survival_at_threshold():
    assert GameRules(35).thief_result(_state(step=35)) == RESULT_SURVIVAL


def test_thief_result_survival_after_threshold():
    assert GameRules(35).thief_result(_state(step=40)) == RESULT_SURVIVAL


def test_is_captured_true_when_position_matches_claim():
    assert GameRules.is_captured(_state(pos=(3, 4)), [3, 4]) is True


def test_is_captured_false_when_position_differs():
    assert GameRules.is_captured(_state(pos=(3, 4)), [3, 5]) is False


def test_is_captured_accepts_tuple_claim():
    assert GameRules.is_captured(_state(pos=(1, 1)), (1, 1)) is True


def test_enclosure_barrier_on_own_cell_is_capture():
    # Rule 46: a barrier placed on the thief's own cell captures it.
    state = _state(pos=(2, 2))
    state.note_barrier((2, 2))
    assert GameRules.is_enclosed(state) is True


def test_enclosure_all_neighbours_walled_is_capture():
    # Rule 47: no legal orthogonal move — STAY does not rescue.
    state = _state(pos=(2, 2))
    for cell in [(1, 2), (3, 2), (2, 1), (2, 3)]:
        state.note_barrier(cell)
    assert GameRules.is_enclosed(state) is True


def test_enclosure_corner_needs_only_two_barriers():
    state = _state(pos=(0, 0))
    state.note_barrier((0, 1))
    state.note_barrier((1, 0))
    assert GameRules.is_enclosed(state) is True


def test_enclosure_false_while_an_escape_remains():
    state = _state(pos=(2, 2))
    for cell in [(1, 2), (3, 2), (2, 1)]:  # (2, 3) stays open
        state.note_barrier(cell)
    assert GameRules.is_enclosed(state) is False


def test_enclosure_false_on_open_board():
    assert GameRules.is_enclosed(_state(pos=(2, 2))) is False
