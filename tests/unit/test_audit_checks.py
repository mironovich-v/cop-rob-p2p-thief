"""Cop-side capture corroboration at audit (league SPEC §3.1, TODO 8.2).

An answer's cell must be where the thief's revealed trail ends; a concession's
cell must be captured under the cop's OWN barrier record (never the thief's
reported list). Either check failing voids the corroboration — the capture is
never counted clean. Missing evidence degrades with a note, never an accusation.
"""

from cop_thief_core.constants import Role
from cop_thief_core.domain.own_state import OwnGameState
from cop_thief_core.orchestration.audit_checks import corroborate_capture, revealed_trail_end

MOVE_SET = ["N", "S", "E", "W", "STAY"]


def _record(position=None, state_str=None, move="MOVE:N"):
    payload = {"step": 1, "move": move}
    if position is not None:
        payload["position"] = position
    if state_str is not None:
        payload["state"] = state_str
    return {"payload": payload, "nonce": "ab", "commit": "c" * 64}


def _cop(pos=(3, 2), barriers=(), claimed=None):
    state = OwnGameState(Role.POLICE, pos, 7, MOVE_SET)
    for cell in barriers:
        state.barriers.add(cell)
        state.my_barriers += 1
    records = [_record(position=list(claimed or pos))]
    return state, records


# --- revealed_trail_end: strict parse or degrade -----------------------------

def test_trail_end_prefers_position_key():
    assert revealed_trail_end([_record(position=[3, 3])]) == (3, 3)


def test_trail_end_parses_reference_state_string():
    record = _record(state_str="grid=7x7;self=[3, 3];barriers=[]")
    assert revealed_trail_end([record]) == (3, 3)


def test_trail_end_degrades_on_missing_or_malformed_evidence():
    assert revealed_trail_end([_record()]) is None
    assert revealed_trail_end([_record(state_str="grid=7x7;self=?;barriers=[]")]) is None
    assert revealed_trail_end([]) is None


# --- answer: cell must equal the revealed trail end --------------------------

def test_answer_corroborated_when_trail_ends_on_answered_cell():
    state, records = _cop(claimed=(3, 3))
    verdict = corroborate_capture(
        state, records, {"claim": [3, 3], "caught": True}, [_record(position=[3, 3])])
    assert verdict["kind"] == "answer"
    assert verdict["corroborated"] is True


def test_answer_voided_when_trail_ends_elsewhere():
    state, records = _cop(claimed=(3, 3))
    verdict = corroborate_capture(
        state, records, {"claim": [3, 3], "caught": True}, [_record(position=[5, 5])])
    assert verdict["corroborated"] is False


# --- concession: cell captured under MY OWN barrier record -------------------

def test_concession_corroborated_by_barrier_on_cell():
    state, records = _cop(barriers=[(3, 3)], claimed=(1, 1))  # rule 46, my record
    verdict = corroborate_capture(
        state, records, {"claim": [3, 3], "caught": True}, [_record(position=[3, 3])])
    assert verdict["kind"] == "concession"
    assert verdict["corroborated"] is True


def test_concession_corroborated_by_enclosure_under_my_record():
    state, records = _cop(barriers=[(2, 3), (4, 3), (3, 2), (3, 4)], claimed=(1, 1))
    verdict = corroborate_capture(
        state, records, {"claim": [3, 3], "caught": True}, [_record(position=[3, 3])])
    assert verdict["corroborated"] is True  # rule 47 under my own barriers


def test_concession_voided_when_my_record_shows_the_cell_free():
    state, records = _cop(barriers=[(0, 1)], claimed=(1, 1))
    verdict = corroborate_capture(
        state, records, {"claim": [3, 3], "caught": True}, [_record(position=[3, 3])])
    assert verdict["corroborated"] is False  # thief-reported barriers never count


def test_degraded_evidence_notes_but_never_accuses():
    state, records = _cop(claimed=(3, 3))
    verdict = corroborate_capture(
        state, records, {"claim": [3, 3], "caught": True}, [_record()])  # no position
    assert verdict["corroborated"] is True
    assert "degraded" in verdict["note"]


def test_claimless_final_degrades_instead_of_crashing():
    """A peer whose caught:true final omits `claim` is non-conforming (SPEC
    §3.1), but an unparseable final must degrade with a note — never raise, and
    never accuse. Reproduces the live il-nv-ai warm-up crash of 2026-08-21."""
    state, records = _cop(claimed=(3, 3))
    verdict = corroborate_capture(
        state, records, {"caught": True}, [_record(position=[3, 3])])
    assert verdict["corroborated"] is True
    assert "degraded" in verdict["note"]


def test_malformed_claim_cell_degrades_rather_than_resolving():
    """Strict parse: a claim that is not a 2-int cell resolves to no cell at all
    (a loose parse would invent a way to accuse an honest peer)."""
    state, records = _cop(claimed=(3, 3))
    for bad in ([3], [3, 3, 3], ["3", "3"], "3,3", None, {}):
        verdict = corroborate_capture(
            state, records, {"claim": bad, "caught": True}, [_record(position=[3, 3])])
        assert verdict["corroborated"] is True, bad
        assert "degraded" in verdict["note"], bad


# --- settlement: a voided corroboration is never counted clean ---------------

class _FakeTransport:
    def __init__(self, payload):
        self._payload = payload

    def exchange_audit(self, mine):
        return self._payload


def _sealed(payload):
    from cop_thief_core.interop.hashing import seal
    return {"payload": payload, **seal(payload)}


def _fake_police_rt(thief_final_cell):
    """A police runtime stub that settled 'capture' on a thief concession the
    police's own barrier record does not support."""
    import time
    from types import SimpleNamespace

    state = OwnGameState(Role.POLICE, (1, 1), 7, MOVE_SET)  # no barriers placed
    my_records = [_sealed({"step": 1, "move": "MOVE:S", "position": [1, 1]})]
    thief_records = [_sealed({"step": 1, "move": "HOLD:-", "position": thief_final_cell})]
    theirs = {"sender": "thief", "records": thief_records, "result_claim": "capture"}
    history = [{"step": 1, "claim_response": {"claim": thief_final_cell, "caught": True}}]
    handler = SimpleNamespace(
        history=history, received_commits={1: thief_records[0]["commit"]})
    return SimpleNamespace(
        _result=("capture", "police"), role=Role.POLICE, records=my_records,
        state=state, handler=handler,
        _transport=_FakeTransport(theirs), _tokens_total=0,
        _config=SimpleNamespace(get=lambda key, default=None: default or "vm__fabi"),
        _sub_game_number=1, _started_at="2026-08-17T00:00:00+03:00",
        _started_monotonic=time.monotonic(),
    )


def test_unsupported_concession_settles_disputed_capture():
    from cop_thief_core.orchestration.summary import finish
    summary = finish(_fake_police_rt([3, 3]))
    assert summary["result"] == "disputed_capture"
    assert summary["winner"] is None
    check = summary["audit"]["capture_corroboration"]
    assert check["kind"] == "concession"
    assert check["corroborated"] is False
    assert summary["audit"]["passed"] is True  # crypto clean — dispute, not tamper
