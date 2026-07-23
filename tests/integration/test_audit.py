"""Adversarial audit: a tampered opponent log forces tamper_forfeit for the honest
peer, regardless of the board result (PRD_commit_reveal, TODO slice 6.2)."""

from cop_thief_core.constants import Role
from cop_thief_core.interop import seal
from cop_thief_core.orchestration.runtime import PeerRuntime
from cop_thief_core.orchestration.summary import finish


class _AuditTransport:
    """Returns a canned opponent audit payload at exchange_audit."""

    def __init__(self, records):
        self._records = records

    def exchange_audit(self, payload):
        return {"sender": "thief", "records": self._records, "result_claim": "survival"}


def _sealed(payload):
    return {"payload": payload, **seal(payload)}


def _police_after_survival(config, transport):
    runtime = PeerRuntime(Role.POLICE, config, transport)
    runtime._result = ("survival", "thief")  # the board says the thief survived
    return runtime


def test_valid_opponent_log_settles_normally(police_config):
    good = _sealed({"step": 1, "position": [4, 3], "move": "MOVE:S"})
    summary = finish(_police_after_survival(police_config, _AuditTransport([good])))
    assert summary["audit"]["passed"] is True
    assert summary["result"] == "survival"
    assert summary["winner"] == "thief"


def test_tampered_opponent_log_forces_forfeit(police_config):
    good = _sealed({"step": 1, "position": [4, 3], "move": "MOVE:S"})
    tampered = {**good, "payload": {**good["payload"], "position": [0, 0]}}  # commit now stale
    summary = finish(_police_after_survival(police_config, _AuditTransport([tampered])))
    assert summary["audit"]["passed"] is False
    assert summary["audit"]["failed_steps"] == [1]
    assert summary["result"] == "tamper_forfeit"
    assert summary["winner"] == "police"  # the honest peer wins by technical decision


def test_missing_opponent_audit_skips(police_config):
    class _Silent:
        def exchange_audit(self, payload):
            return None

    summary = finish(_police_after_survival(police_config, _Silent()))
    assert summary["audit"]["skipped"] is True
    assert summary["result"] == "survival"  # no forfeit when the opponent never revealed
