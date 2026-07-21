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
