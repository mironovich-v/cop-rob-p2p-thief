"""The police brain: take away the evader's ANSWERS, not its floor space.

WHY THIS SHAPE. The shipped cop minimised the thief's territory and spent
barriers only on a rule-46 strike or a pocketed thief. Across six live windows
against imreeyal it converted nothing, and their debrief (§2a) explains why: a
competent evader keeps three exits forever, so the seal trigger never fires and
the cop shadows at distance 2 while the region shrinks and grows again. Our own
docstring already recorded the decisive experiment — an ORACLE cop holding the
thief's true cell captured 2/16 against the blind cop's 3/16 — so the missing
ingredient was never information.

What converts is ``escapes``: how many of the evader's replies land outside the
cop's own next reach. Drive it to zero and the evader's choice stops mattering.
Room becomes the tie-break rather than the objective.

Measured (96 unseen seeds per evader arm, champion gate — never worse than the
shipped cop on ANY arm): 96/96 against a random walker where the shipped cop
took 89/96 and two steps longer, and 87–91/96 against every competent evader
under a one-move-stale belief where the shipped cop managed 0–3/96.

AND THE BARRIERS ARE OFF BY DEFAULT (``spend_barriers``), which is the single
biggest measured change here:

    arm            with 14 walls      with walls off
    greedy-run     0/32  med 35        32/32  med 17
    territory      0/32  med 35        32/32  med 15
    doctrine       0/32  med 35        32/32  med 15
    random        29/32  med 8.5       32/32  med 8.5

A wall costs the cop its MOVE, and it may only be placed on a cell adjacent to
the cop — which is a cell the cop could simply step onto. So a barrier can never
capture anything a step could not capture more cheaply, while the pocket-seal
trigger fires repeatedly, spends the tempo that would have closed the distance,
and lets the evader walk away. Live, our cop burned 5–9 walls per window and
converted nothing; imreeyal's used ZERO and won three. Their own §3 says it:
"our cop won three windows with positioning alone".

Two related ideas from their §2 fix 1 were tested and refused by measurement:
the territory-based ``wall_gain`` is IDENTICALLY ZERO over 840 turns (a wall
next to the cop lies in the cop's own Voronoi region and cannot shrink the
thief's), and sealing an escape is structurally impossible for the same reason —
the wall cell is already inside the cop's next reach.

The capability is kept and configurable, not deleted: a future opponent, a
larger board or a diagonal move set could make walls pay.
"""

from cop_thief_core.constants import MoveType, Role
from cop_thief_core.domain.brain_base import BrainBase
from cop_thief_core.domain.tactics import escapes, police_barrier, recent_trail, territory


class PoliceBrain(BrainBase):
    """Contain, don't chase: minimise the evader's escaping replies."""

    role = Role.POLICE

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._best_history: list[int] = []  # best reachable territory per turn
        self._just_held = False

    def _parity_locked(self, state, threat) -> bool:
        """Are we circling an evader we can never land on?

        Three signals together, because any one alone gives false positives: we
        are REVISITING our own recent cells (the live pathology was a two-cell
        ping-pong), the best reachable territory has not improved, and the
        distance is EVEN. Every move changes the Manhattan distance by one, so an
        evader holding an even distance before our move cannot be landed on by a
        cop that always moves — and STAY is the only way out.

        Live (vibecode g1): best territory read 27, 21, 19, 14, 11, 9 and then 21
        for twenty-eight straight turns while the cop shuttled between two cells,
        distance even on 29 of 34 turns, 14 barriers unused.
        """
        window = self._tactics["stall_window"]
        if len(self._best_history) < window or len(set(self._best_history[-window:])) != 1:
            return False  # still making progress
        visited = [tuple(entry["position"]) for entry in state.log[-window:]]
        if len(visited) < window or len(set(visited)) == len(visited):
            return False  # not circling — a straight approach may plateau briefly
        return (state.board.distance(state.position, threat) % 2) == 0

    def _decide_move(self, state, belief, barriers_max):
        moves = state.board.legal_moves(state.position, state.barriers)
        if not moves:
            return MoveType.HOLD, None
        threat = belief.most_likely()
        if self._tactics["spend_barriers"] and state.my_barriers < barriers_max:
            strike = police_barrier(state.board, state, threat, self._tactics)
            if strike is not None:
                return MoveType.BARRIER, strike
        self._best_history.append(min(
            territory(state.board, threat, target, state.barriers)
            for _, target in moves))
        # Hold ONCE to flip the parity; holding again would just stall the hunt.
        if not self._just_held and self._parity_locked(state, threat):
            self._just_held = True
            self._best_history.clear()
            return MoveType.HOLD, None
        self._just_held = False
        direction, _ = self._pick_move(list(moves) + [(None, state.position)], state, belief)
        if direction is None:
            return MoveType.HOLD, None
        return MoveType.MOVE, direction

    def _pick_move(self, moves, state, belief):
        """Take the cell that leaves the evader the fewest escaping answers."""
        target = belief.most_likely()
        board, barriers = state.board, state.barriers
        recent = recent_trail(state, self._tactics["recent_window"])
        shuffled = list(moves)
        self._rng.shuffle(shuffled)  # tie-break randomly: vary the approach vector

        def value(move):
            cell = move[1]
            if cell == target:
                return (-1, -1, 0, False)  # landing on it IS the capture
            worst_room = max(
                (territory(board, reply, cell, barriers)
                 for reply in [target, *board.neighbors(target, barriers)] if reply != cell),
                default=0)
            return (escapes(board, cell, target, barriers), worst_room,
                    board.distance(cell, target), cell in recent)

        return min(shuffled, key=value)
