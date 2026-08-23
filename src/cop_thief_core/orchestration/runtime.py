"""PeerRuntime: one standalone agent's full lifecycle — no central server.

negotiate (mutual signatures) → turn loop (wait for a turn → think → move → seal
→ send) → end-of-game mutual audit. The turn token travels with the TurnMessage:
receiving one makes this peer's move. A rejected move falls back to HOLD so the
loop never stalls; the thief wins by surviving the step cap, the police by a
capture claim that lands on the thief's true cell.
"""

import random
import time

from cop_thief_core.constants import (
    FINAL_CAUGHT_HINT,
    RESULT_CAPTURE,
    RESULT_SURVIVAL,
    VERDICT_TRUTH,
    MoveType,
    Role,
)
from cop_thief_core.domain.belief import BeliefGrid
from cop_thief_core.domain.brains import Decision
from cop_thief_core.domain.own_state import OwnGameState
from cop_thief_core.domain.rules import GameRules
from cop_thief_core.domain.smell import SmellField
from cop_thief_core.orchestration.handshake import run_handshake
from cop_thief_core.orchestration.sealing import (
    build_turn_message,
    identity_from_config,
    now_iso,
    sealed_spec_record,
    sealed_step_record,
)
from cop_thief_core.orchestration.summary import finish, snapshot
from cop_thief_core.orchestration.turn_handler import TurnHandler
from cop_thief_core.strategy import resolve_brain


class PeerRuntime:
    """Runs one agent (thief or police) for ONE sub-game against a remote opponent."""

    def __init__(self, role, config, transport, llm=None, brain=None,
                 own_identity=None, sub_game_number=1, listener=None):
        self.role = role
        self._config = config
        self._transport = transport
        self._listen = listener or (lambda event: None)
        self._own_identity = own_identity or identity_from_config(config)
        self._sub_game_number = sub_game_number
        self.peer_identity: dict = {}
        self.game_id = None
        self.game_uid = None
        size = config.get("board.size")
        move_set = config.get("rules.move_set")
        start = tuple(config.get(f"positions.{'thief' if role is Role.THIEF else 'cop'}_start"))
        self.state = OwnGameState(role, start, size, move_set)
        self.belief = BeliefGrid(
            size, config.get("belief.smell_trust_weight", 4.0),
            orthogonal=not self.state.board.diagonal,
        )
        self.smell = self._new_scent(size, config)
        self.my_scent = self._new_scent(size, config)
        self.rules = GameRules(config.get("rules.max_steps"))
        self.handler = TurnHandler(self.state, self.belief, self.smell, self.rules,
                                   reorder_window=config.get("network.reorder_window", 1))
        # Seed varies PER SUB-GAME (deterministic given config seed): one static
        # seed replayed the identical game every sub-game — a real opponent saw
        # three identical thief games in a counted series; solve us once, win thrice.
        self.brain = brain or resolve_brain(
            config, role, llm,
            rng=random.Random(f"{config.get('play.seed')}:{sub_game_number}"))
        self._tokens_total = 0
        self._started_monotonic = time.monotonic()
        self._started_at = now_iso()
        self.records: list[dict] = [sealed_spec_record(config, sub_game_number)]
        self._result: tuple[str, str] | None = None

    @staticmethod
    def _new_scent(size, config) -> SmellField:
        return SmellField(
            size, config.get("smell.grid_size"), config.get("smell.decay_per_step"),
            config.get("smell.min_center_intensity"),
        )

    def view(self) -> dict:
        return snapshot(self)

    def run(self, skip_negotiation: bool = False) -> dict:
        if not skip_negotiation:
            # Announced BEFORE the call blocks: both 2026-08-23 aborts stalled
            # inside the handshake, and a line printed after it returns would
            # never have been written.
            self._listen({"type": "handshake_wait", "sub_game": self._sub_game_number,
                          "role": self.role.value})
            self.peer_identity, self.game_id, self.game_uid = run_handshake(
                self._transport, self._config, self._own_identity,
                role=self.role.value, sub_game_number=self._sub_game_number,
            )
            self._mark_game_start()
            self._listen({"type": "negotiated", "view": self.view(),
                          "sub_game": self._sub_game_number})
        if self.role is Role.THIEF:
            self._take_turn(None)
        self._turn_loop()
        summary = finish(self)
        self._listen({"type": "game_over", "view": self.view(), "summary": summary})
        return summary

    def _mark_game_start(self) -> None:
        """Stamp the sub-game's start at the moment it OPENS, not at launch.

        A peer may hold in the handshake for a long time waiting for the
        opponent's doors — fifteen minutes in the imreeyal window of
        2026-08-23. Only the monotonic clock used to be reset here, so the
        filed `started_at` (and `ended_at`, which is derived from it) carried
        the launch time and reported a sub-game that began before the agreed T.
        """
        self._started_monotonic = time.monotonic()
        self._started_at = now_iso()

    def _turn_loop(self) -> None:
        timeout = self._config.get("network.turn_timeout_seconds")
        poll = self._config.get("network.poll_interval_seconds")
        deadline = time.monotonic() + timeout
        while self._result is None:
            incoming = self._transport.poll_turn(poll)
            # The deadline is one clock per EXPECTED message: evaluated on EVERY
            # lap (a receiver that only checks on empty polls never checks under
            # a flood), and never renewed by tolerated junk.
            if time.monotonic() > deadline:
                self._result = ("timeout", self.role.value)
                continue
            if incoming is None:
                continue
            outcome = self.handler.receive(incoming)
            if outcome.settle:  # equivocation / flood: loud technical decision
                self._result = (outcome.settle, self.role.value)
                continue
            if outcome.ignored:
                continue  # absorbed / buffered / discarded: no state, no renewal
            deadline = time.monotonic() + timeout
            self._listen({"type": "incoming", "message": incoming, "view": self.view()})
            if outcome.i_won:
                self._result = (RESULT_CAPTURE, Role.POLICE.value)
            elif outcome.opponent_won:
                self._result = (outcome.win_type or RESULT_SURVIVAL, Role.THIEF.value)
            elif outcome.i_am_caught:
                self.state.apply_move(MoveType.HOLD, None)  # final hold: advance the step
                self._send(Decision(MoveType.HOLD, None, FINAL_CAUGHT_HINT, VERDICT_TRUTH),
                           outcome.claim_response, None, None)
                self._result = (RESULT_CAPTURE, Role.POLICE.value)
            else:
                self._take_turn(outcome.claim_response)

    def _take_turn(self, claim_response) -> None:
        opponent_hint = self.handler.history[-1]["hint"] if self.handler.history else ""
        barriers_max = self._config.get("rules.barriers_max")
        decision = self.brain.decide(
            self.state, self.belief, opponent_hint, self._config.get("play.setting"),
            barriers_max, deadline_seconds=self._config.get("llm.step_deadline_seconds"),
        )
        if not self.state.apply_move(decision.move_type, decision.direction, barriers_max):
            self.state.apply_move(MoveType.HOLD, None)  # never stall the loop
        win = self.rules.thief_result(self.state) if self.role is Role.THIEF else None
        capture_claim = (
            list(self.state.position)
            if self.role is Role.POLICE and decision.move_type is MoveType.MOVE else None
        )
        self._send(decision, claim_response, capture_claim, {"type": win} if win else None)
        if win:
            self._result = (win, Role.THIEF.value)

    def _send(self, decision, claim_response, capture_claim, win_claim) -> None:
        record = sealed_step_record(self.state, decision, {"model": "template", "total": 0}, 0)
        self.records.append(record)
        self.my_scent.deposit(self.state.position, self._config.get("smell.emit_intensity"))
        self.my_scent.decay_all()
        message = build_turn_message(
            self.state, self.role.value, decision.hint, self.my_scent.snapshot(),
            record["commit"], capture_claim, claim_response, win_claim,
        )
        self._transport.send_turn(message.to_dict())
        self._listen({
            "type": "moved", "view": self.view(), "decision": decision,
            "usage": {"total": 0, "match_total": self._tokens_total},
            "commit": record["commit"],
        })
