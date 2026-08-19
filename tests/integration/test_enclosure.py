"""End-to-end rule-46 capture by enclosure (league SPEC §3.1, TODO 8.1).

The police walks from (0,0) to (3,2) and drops a barrier ON the thief's cell
(3,3). The thief — scripted to STAY — must SAY the ending: an unprompted
concession final (`claim_response={"claim": [3, 3], "caught": true}`), and both
peers settle CAPTURE with clean mutual audits. Without the concession this
exact scenario forks into capture-vs-timeout (reproduced live by the league).
"""

import threading

from cop_thief_core.constants import VERDICT_TRUTH, Direction, MoveType, Role
from cop_thief_core.domain.brains import Decision
from cop_thief_core.orchestration.runtime import PeerRuntime


class _ScriptBrain:
    """Plays a fixed decision list, then HOLDs forever."""

    def __init__(self, decisions):
        self._decisions = list(decisions)

    def decide(self, *args, **kwargs):
        if self._decisions:
            return self._decisions.pop(0)
        return Decision(MoveType.HOLD, None, "", VERDICT_TRUTH)


def _move(direction):
    return Decision(MoveType.MOVE, direction, "", VERDICT_TRUTH)


def _run_match(thief, police) -> dict:
    results: dict = {}
    threads = [
        threading.Thread(target=lambda: results.update(police=police.run()), daemon=True),
        threading.Thread(target=lambda: results.update(thief=thief.run()), daemon=True),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
        assert not thread.is_alive(), "peer runtime did not finish"
    return results


def test_barrier_on_thief_cell_settles_capture_both_ways(
    transport_pair, thief_config, police_config
):
    thief_t, police_t = transport_pair
    # Police: (0,0) -S,S,S-> (3,0) -E,E-> (3,2), then a barrier E onto (3,3).
    police_script = [_move(Direction.S)] * 3 + [_move(Direction.E)] * 2 + [
        Decision(MoveType.BARRIER, Direction.E, "", VERDICT_TRUTH)
    ]
    thief = PeerRuntime(Role.THIEF, thief_config, thief_t, brain=_ScriptBrain([]))
    police = PeerRuntime(Role.POLICE, police_config, police_t, brain=_ScriptBrain(police_script))
    results = _run_match(thief, police)

    assert results["thief"]["result"] == results["police"]["result"] == "capture"
    assert results["thief"]["winner"] == results["police"]["winner"] == "police"
    # The concession was SAID on the wire: the police's history holds the final
    # whose claim_response names the thief's own cell, unprompted by any claim.
    finals = [m for m in police.handler.history if m.get("claim_response")]
    assert finals[-1]["claim_response"] == {"claim": [3, 3], "caught": True}
    # Both mutual audits verify the sealed chains cleanly.
    assert results["thief"]["audit"]["passed"] is True
    assert results["police"]["audit"]["passed"] is True
    # 8.2: the cop corroborated the concession under its OWN barrier record.
    check = results["police"]["audit"]["capture_corroboration"]
    assert check == {"kind": "concession", "corroborated": True, "note": ""}
