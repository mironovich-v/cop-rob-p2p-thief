"""A circling cop in a parity lock must change the parity, not shuffle.

Live evidence (vibecode g1, 2026-08-21): our cop's best reachable territory fell
27 -> 21 -> 19 -> 14 -> 11 -> 9 over six steps, then read 21 for the remaining
twenty-eight turns while it shuttled between two cells. The distance to the
believed thief was EVEN on 29 of 34 turns and all 14 barriers went unused.

Both peers move each round, so every move changes the Manhattan distance by one:
an evader that keeps the distance even before our move can never be landed on by
a cop that always moves. STAY is in the agreed move set and our cop never used
it — one HOLD flips the parity and makes capture reachable again.

The rule is unit-tested directly. A static harness cannot reproduce the live
dynamics (against a stationary belief the cop simply closes), so driving the
predicate is more honest than staging a fake chase.
"""

import random

from cop_thief_core.constants import ORTHOGONAL, Role
from cop_thief_core.domain.brains import PoliceBrain
from cop_thief_core.domain.own_state import OwnGameState

FLAT = [21, 21, 21, 21]          # the live plateau
PROGRESS = [27, 21, 19, 14]      # the live approach


def _brain(history):
    brain = PoliceBrain(rng=random.Random(0))
    brain._best_history = list(history)
    return brain


def _state(trail):
    state = OwnGameState(Role.POLICE, trail[-1], 7, list(ORTHOGONAL))
    state.log.extend({"position": list(cell)} for cell in trail)
    return state


PING_PONG = [(3, 3), (2, 3), (3, 3), (2, 3)]     # revisits its own cells
STRAIGHT = [(0, 0), (1, 0), (2, 0), (3, 0)]      # never revisits


def test_circling_at_even_distance_is_a_lock():
    state = _state(PING_PONG)                     # cop ends on (2,3)
    assert _brain(FLAT)._parity_locked(state, (2, 5)) is True   # distance 2


def test_a_straight_approach_is_not_a_lock_even_when_it_plateaus():
    """Plateauing while genuinely closing is normal; never interrupt progress."""
    state = _state(STRAIGHT)
    assert _brain(FLAT)._parity_locked(state, (3, 2)) is False


def test_odd_distance_is_not_a_lock():
    """Odd distance is already reachable — there is nothing to break."""
    state = _state(PING_PONG)
    assert _brain(FLAT)._parity_locked(state, (2, 4)) is False   # distance 1


def test_improving_territory_is_not_a_lock():
    state = _state(PING_PONG)
    assert _brain(PROGRESS)._parity_locked(state, (2, 5)) is False


def test_too_little_history_is_not_a_lock():
    state = _state(PING_PONG)
    assert _brain([21, 21])._parity_locked(state, (2, 5)) is False


def test_holding_happens_once_and_resets_the_history():
    """Holding is a parity flip, not a strategy — a second one would stall us.

    Driven rather than pre-loaded: `_decide_move` appends the turn's reading
    before testing the window, so the lock is only visible after enough turns.
    """
    from cop_thief_core.constants import MoveType
    state = _state(PING_PONG)
    brain = _brain([])
    seen_hold = False
    for _ in range(8):
        move_type, _ = brain._decide_move(state, _Belief((2, 5)), 14)
        if move_type is MoveType.HOLD:
            seen_hold = True
            break
    assert seen_hold, "a circling cop at even distance never flipped parity"
    assert brain._best_history == []                     # cleared on the hold
    again, _ = brain._decide_move(state, _Belief((2, 5)), 14)
    assert again is not MoveType.HOLD                    # never twice running


class _Belief:
    def __init__(self, cell):
        self.cell = cell

    def most_likely(self):
        return self.cell
