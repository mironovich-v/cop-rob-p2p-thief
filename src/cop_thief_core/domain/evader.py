"""The thief brain: stand still when standing still is the safe move.

WHY THIS SHAPE — forensic on the imreeyal counted series, sub-game 2
(2026-08-23), reconstructed from our own sealed log and their scent peaks:

    step   our cell   their cop   distance
      8     (4,6)       (3,5)        2      safe
      9     (5,6)       (4,5)        2      safe
     10     (6,6)       (5,5)        2      safe   <- cornered
     11     (6,5)       (6,5)        0      CAPTURED

At step 10 we stood in the corner (6,6) with their cop at (5,5). Our options
were (6,6) — distance 2, SAFE — and (5,6) and (6,5), both inside the cop's
reach. We moved to (6,5) and died on their next move. The evader never
considered staying: ``_decide_move`` offered only ``board.legal_moves``, so HOLD
was not in the option set, even though STAY is a signed term of the agreed move
set and our own police already used it to break a parity lock.

A cornered evader was therefore FORCED to step into the pursuer's reach. That is
precisely the containment imreeyal described — "within ten steps we hold a
position where every cell your rule can pick is within our reach" — and the
reason it worked is that our rule could not pick the safe one.

Three further changes, each measured in the arena (see docs/PRD_strategy_brains
and tests/unit/test_evader.py), 96 unseen seeds per pursuer arm:

* ROOM, not exits. Two exits on the bottom row and two in the open centre score
  identically under an exit count, so the evader drifted to edges where a
  pursuer's lines converge — all three captures against us were on an edge.
  Territory (the BFS Voronoi region) prices edges correctly for free.
* A FLIGHT FLOOR. Room alone makes an evader complacent: STAY often looks
  roomiest, and a naive chaser simply walks up to it (64/64 caught in the
  arena). Inside the floor, distance beats room.
* A LAG-ROBUST second safety key, in case the believed cell is a move old.

Result: caught 0/96 by every pursuer arm at every belief lag tested, where the
shipped evader was caught 83–91/96.
"""

from cop_thief_core.constants import MoveType, Role
from cop_thief_core.domain.brain_base import BrainBase
from cop_thief_core.domain.tactics import reachable_within, territory


class ThiefBrain(BrainBase):
    """Safety first (including the option to stand still), then room, then flight."""

    role = Role.THIEF

    def _decide_move(self, state, belief, barriers_max):
        """Offer STAY alongside every legal move — see the module docstring."""
        options = list(state.board.legal_moves(state.position, state.barriers))
        options.append((None, state.position))  # STAY: legal, signed, and often the only safe cell
        direction, _ = self._pick_move(options, state, belief)
        if direction is None:
            return MoveType.HOLD, None
        return MoveType.MOVE, direction

    def _pick_move(self, moves, state, belief):
        board, barriers = state.board, state.barriers
        seen = belief.most_likely()
        # Where it can land next move if the belief is exact, and if it is stale.
        lethal = {seen, *board.neighbors(seen, barriers)}
        envelope = reachable_within(board, seen, self._tactics["belief_lag"] + 1, barriers)
        centre = (board.size - 1) / 2
        hunted = board.distance(state.position, seen) <= self._tactics["flight_floor"]
        shuffled = list(moves)
        self._rng.shuffle(shuffled)  # tie-break randomly: a deterministic evader is pin-able

        def value(move):
            cell = move[1]
            safe = cell not in lethal  # nothing can land on me here
            robust = cell not in envelope  # nor if the peak is a move old
            room = territory(board, cell, seen, barriers)
            far = board.distance(cell, seen)
            margin = -(abs(cell[0] - centre) + abs(cell[1] - centre))
            if hunted:  # up close, distance beats room (complacency kills)
                return (safe, robust, far, room, margin)
            return (safe, robust, room, margin, far)

        return max(shuffled, key=value)
