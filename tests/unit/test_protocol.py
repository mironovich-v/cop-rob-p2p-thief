"""Tests for the wire message schemas (PRD_mcp_protocol, TODO slice 2.1)."""

import pytest

from cop_thief_core.protocol import AuditPayload, ControlMessage, TurnMessage


def _turn(**overrides):
    base = {
        "step": 3,
        "sender": "thief",
        "hint": "heading uptown",
        "smell_grid": {"4,4": 0.9},
        "commit": "deadbeef",
        "timestamp": "2026-07-22T10:00:00+00:00",
    }
    base.update(overrides)
    return base


def test_turn_roundtrip_defaults_none():
    msg = TurnMessage.from_dict(_turn())
    assert msg.step == 3
    assert msg.barrier_placed is None and msg.win_claim is None
    assert TurnMessage.from_dict(msg.to_dict()) == msg


def test_turn_roundtrip_with_optionals():
    data = _turn(
        barrier_placed=[2, 3],
        capture_claim=[1, 1],
        claim_response={"claim": [1, 1], "caught": False},
        win_claim={"type": "survival"},
    )
    msg = TurnMessage.from_dict(data)
    assert msg.to_dict() == data


def test_turn_missing_required_raises():
    bad = _turn()
    del bad["commit"]
    with pytest.raises(TypeError):
        TurnMessage.from_dict(bad)


def test_turn_ignores_unknown_fields():
    msg = TurnMessage.from_dict(_turn(prev="abc", extra_team_field=123))
    assert msg.step == 3
    assert not hasattr(msg, "prev")


def test_control_defaults_and_roundtrip():
    msg = ControlMessage.from_dict({"kind": "status", "sender": "police"})
    assert msg.sub_game_number == 1
    assert msg.status == "" and msg.step_budget == 0.0
    assert ControlMessage.from_dict(msg.to_dict()) == msg


def test_control_missing_required_raises():
    with pytest.raises(TypeError):
        ControlMessage.from_dict({"kind": "quit"})  # missing sender


def test_audit_roundtrip_and_missing():
    records = [{"payload": {"step": 1}, "nonce": "n", "commit": "c"}]
    msg = AuditPayload.from_dict(
        {"sender": "thief", "records": records, "result_claim": "survival"}
    )
    assert msg.records == records
    assert AuditPayload.from_dict(msg.to_dict()) == msg
    with pytest.raises(TypeError):
        AuditPayload.from_dict({"sender": "thief", "records": records})
