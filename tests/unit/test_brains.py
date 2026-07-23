"""Tests for the strategy brains (PRD_strategy_brains, TODO slice 3.2)."""

from cop_thief_core.constants import VERDICT_TRUTH, MoveType, Role
from cop_thief_core.domain.belief import BeliefGrid
from cop_thief_core.domain.brains import Decision, PoliceBrain, ThiefBrain
from cop_thief_core.domain.own_state import OwnGameState

MOVE_SET = ["N", "S", "E", "W", "STAY"]


class BoomLLM:
    """Any access explodes — proves the move path never touches the LLM."""

    def __getattr__(self, name):
        raise AssertionError("the LLM must never be consulted for a move")


class FixedRng:
    def __init__(self, value):
        self._value = value

    def random(self):
        return self._value


def _belief_peaked_at(cell, size=5):
    belief = BeliefGrid(size, orthogonal=True)
    belief.observe_smell({f"{cell[0]},{cell[1]}": 0.9})
    return belief


def _state(role, pos=(2, 2), size=5):
    return OwnGameState(role, pos, size, MOVE_SET)


def test_thief_flees_from_believed_threat():
    state = _state(Role.THIEF)
    brain = ThiefBrain(BoomLLM())
    move_type, direction = brain._decide_move(state, _belief_peaked_at((0, 0)), 0)
    assert move_type is MoveType.MOVE
    target = state.board.step(state.position, direction)
    assert state.board.distance(target, (0, 0)) > state.board.distance(state.position, (0, 0))


def test_police_chases_believed_thief():
    state = _state(Role.POLICE)
    brain = PoliceBrain(rng=FixedRng(1.0))  # never rolls a barrier
    move_type, direction = brain._decide_move(state, _belief_peaked_at((0, 0)), 14)
    assert move_type is MoveType.MOVE
    target = state.board.step(state.position, direction)
    assert state.board.distance(target, (0, 0)) < state.board.distance(state.position, (0, 0))


def test_police_places_barrier_when_roll_hits():
    state = _state(Role.POLICE)
    brain = PoliceBrain(rng=FixedRng(0.0))  # roll < barrier_chance -> BARRIER
    move_type, _ = brain._decide_move(state, _belief_peaked_at((0, 0)), 14)
    assert move_type is MoveType.BARRIER


def test_police_moves_when_barrier_budget_exhausted():
    state = _state(Role.POLICE)
    state.my_barriers = 14
    brain = PoliceBrain(rng=FixedRng(0.0))
    move_type, _ = brain._decide_move(state, _belief_peaked_at((0, 0)), 14)
    assert move_type is MoveType.MOVE


def test_hold_when_no_legal_moves():
    state = _state(Role.THIEF)
    for cell in [(1, 2), (3, 2), (2, 1), (2, 3)]:
        state.note_barrier(cell)
    assert ThiefBrain()._decide_move(state, _belief_peaked_at((0, 0)), 0) == (MoveType.HOLD, None)


def test_decide_returns_decision_and_never_uses_llm_for_move():
    state = _state(Role.THIEF)
    decision = ThiefBrain(BoomLLM()).decide(state, _belief_peaked_at((0, 0)), "", "New York", 14)
    assert isinstance(decision, Decision)
    assert decision.move_type is MoveType.MOVE
    assert decision.hint == ""  # null trash provider until Stage 4
    assert decision.verdict == VERDICT_TRUTH
