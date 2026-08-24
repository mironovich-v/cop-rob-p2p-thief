"""Offline arena: play brains against brains with no protocol, no network.

Built to the measurement discipline imreeyal set out in their debrief (§4) after
the counted series: several OPPONENT ARMS rather than self-play, many seeds,
whole distributions instead of a capture rate, and a champion gate that ships a
brain only if it is no worse on ANY arm. Our earlier 12-seed self-play runs were
the right instinct measured the wrong way — a brain tuned only against our own
cop learns our own cop's blind spots.

Modelling notes, because they decide what the numbers are worth:

* BELIEF is injected, not simulated. ``thief_lag`` models the one thing that
  turned out to matter: the scent peak marking where the pursuer WAS. At lag 0
  the shipped evader is never caught; at lag 1 it is caught 91/96. Reality sits
  between, so both are reported.
* CAPTURE is graded as the wire grades it — overlap after either side's move,
  thief first each round.
* A BARRIER costs the police its move for that round, as on the wire.

This lives in the domain layer (not scripts/) so tests can import it and the
numbers in the brain docstrings stay reproducible.
"""

import random
import statistics

from cop_thief_core.constants import ORTHOGONAL, MoveType, Role
from cop_thief_core.domain.own_state import OwnGameState

BOARD, HORIZON, WALLS = 7, 35, 14
THIEF_START, COP_START = (3, 3), (0, 0)


class InjectedBelief:
    """A belief the arena sets directly — see the belief note above."""

    def __init__(self) -> None:
        self.cell: tuple[int, int] | None = None

    def most_likely(self):
        return self.cell


def play(thief, police, board=BOARD, horizon=HORIZON, walls=WALLS, thief_lag=0):
    """Run one sub-game. Returns ``(result, steps, walls_used)``."""
    moves = list(ORTHOGONAL) + ["STAY"]
    runner = OwnGameState(Role.THIEF, THIEF_START, board, moves)
    chaser = OwnGameState(Role.POLICE, COP_START, board, moves)
    seen_by_thief, seen_by_cop = InjectedBelief(), InjectedBelief()
    stale = chaser.position
    for step in range(1, horizon + 1):
        seen_by_thief.cell = stale if thief_lag else chaser.position
        stale = chaser.position
        move_type, direction = thief._decide_move(runner, seen_by_thief, 0)
        runner.apply_move(move_type, direction, 0)
        if runner.position == chaser.position:
            return "capture", step, chaser.my_barriers
        seen_by_cop.cell = runner.position
        move_type, direction = police._decide_move(chaser, seen_by_cop, walls)
        placed_before = chaser.my_barriers
        chaser.apply_move(move_type, direction, walls)
        if move_type is MoveType.BARRIER and chaser.my_barriers > placed_before:
            runner.note_barrier(chaser.last_barrier())      # declared on the wire
        if chaser.position == runner.position:
            return "capture", step, chaser.my_barriers
    return "survival", horizon, chaser.my_barriers


def measure(thief_cls, police_cls, seeds, **kw) -> dict:
    """Play one arm over ``seeds``; report the distribution, not just a rate."""
    rows = [play(thief_cls(rng=random.Random(seed)),
                 police_cls(rng=random.Random(seed + 7717)), **kw) for seed in seeds]
    steps = [row[1] for row in rows]
    captures = sum(1 for row in rows if row[0] == "capture")
    return {
        "n": len(rows),
        "captures": captures,
        "capture_rate": captures / len(rows),
        "median_steps": statistics.median(steps),
        "mean_steps": round(statistics.mean(steps), 1),
        "max_steps": max(steps),
        "walls": statistics.median([row[2] for row in rows]),
    }


def gate(champion: dict, challenger: dict, lower_is_better: bool) -> bool:
    """Champion gate: a challenger ships only if it is no worse on THIS arm."""
    if lower_is_better:
        return challenger["captures"] <= champion["captures"]
    return challenger["captures"] >= champion["captures"]
