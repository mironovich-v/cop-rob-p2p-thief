"""Sparring brains: the opponent arms our shipped brains are measured against.

These are TEST OPPONENTS, never played on the wire. imreeyal's §4 warning is the
reason they exist: "a thief tuned only against your cop learns your cop's blind
spots", and "model opponents from their CODE at a declared commit, never from
friendly tapes — friendlies can be played with decoy brains (ours was)".

``InterceptCop`` and ``DoctrineThief`` are therefore reconstructions of the two
designs imreeyal DESCRIBED in their debrief (§3) after the league capped them
out, not inferences from the games we lost to them.
"""

from cop_thief_core.constants import MoveType, Role
from cop_thief_core.domain.brain_base import BrainBase
from cop_thief_core.domain.tactics import escapes, territory


class RandomThief(BrainBase):
    """The floor: an unpredictable walker. Any pursuer must beat this."""

    role = Role.THIEF

    def _pick_move(self, moves, state, belief):
        return self._rng.choice(list(moves))


class GreedyRunner(BrainBase):
    """Maximise distance — our own v1 evader, which self-cornered and died."""

    role = Role.THIEF

    def _pick_move(self, moves, state, belief):
        threat = belief.most_likely()
        return max(moves, key=lambda m: state.board.distance(m[1], threat))


class TerritoryThief(BrainBase):
    """Pure room-maximiser: imreeyal's §1 fix 1 on its own, without a flight floor."""

    role = Role.THIEF

    def _pick_move(self, moves, state, belief):
        threat = belief.most_likely()
        shuffled = list(moves)
        self._rng.shuffle(shuffled)
        return max(shuffled, key=lambda m: (
            m[1] != threat and m[1] not in state.board.neighbors(threat, state.barriers),
            territory(state.board, m[1], threat, state.barriers)))


class DoctrineThief(BrainBase):
    """imreeyal's evader per §3: room after the pursuer's best WALL, then flight."""

    role = Role.THIEF
    flight_floor = 3

    def _room_after_worst_wall(self, board, cell, cop, barriers):
        worst = territory(board, cell, cop, barriers)
        for wall in board.neighbors(cop, barriers):
            if wall != cell:
                worst = min(worst, territory(board, cell, cop, barriers | {wall}))
        return worst

    def _pick_move(self, moves, state, belief):
        cop, board, barriers = belief.most_likely(), state.board, state.barriers
        centre = (board.size - 1) / 2
        hunted = board.distance(state.position, cop) <= self.flight_floor
        shuffled = list(moves)
        self._rng.shuffle(shuffled)

        def value(move):
            cell = move[1]
            safe = cell != cop and cell not in board.neighbors(cop, barriers)
            room = self._room_after_worst_wall(board, cell, cop, barriers)
            margin = -(abs(cell[0] - centre) + abs(cell[1] - centre))
            if hunted:
                return (safe, room, board.distance(cell, cop), margin)
            return (safe, room, margin, board.distance(cell, cop))

        return max(shuffled, key=value)


class GreedyChaser(BrainBase):
    """Closes distance — the classic mistake, and a useful complacency detector."""

    role = Role.POLICE

    def _decide_move(self, state, belief, barriers_max):
        moves = state.board.legal_moves(state.position, state.barriers)
        if not moves:
            return MoveType.HOLD, None
        target = belief.most_likely()
        return MoveType.MOVE, min(moves, key=lambda m: state.board.distance(m[1], target))[0]


class InterceptCop(BrainBase):
    """imreeyal's pursuer per §3: leave the evader's best reply worst."""

    role = Role.POLICE

    def _decide_move(self, state, belief, barriers_max):
        moves = state.board.legal_moves(state.position, state.barriers)
        if not moves:
            return MoveType.HOLD, None
        thief, board, barriers = belief.most_likely(), state.board, state.barriers
        options = list(moves) + [(None, state.position)]
        self._rng.shuffle(options)

        def value(move):
            cell = move[1]
            if cell == thief:
                return (-1, -1, 0)
            best_reply = max(
                (territory(board, reply, cell, barriers)
                 for reply in [thief, *board.neighbors(thief, barriers)] if reply != cell),
                default=0)
            return (escapes(board, cell, thief, barriers), best_reply,
                    board.distance(cell, thief))

        direction, _ = min(options, key=value)
        if direction is None:
            return MoveType.HOLD, None
        return MoveType.MOVE, direction


EVADER_ARMS = {"random": RandomThief, "greedy-run": GreedyRunner,
               "territory": TerritoryThief, "doctrine": DoctrineThief}
PURSUER_ARMS = {"greedy-chase": GreedyChaser, "intercept": InterceptCop}
