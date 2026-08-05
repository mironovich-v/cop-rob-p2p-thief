"""Unit tests for replay log normalization + position reconstruction (Stage 7.5a)."""

from cop_thief_core.gui.replay_data import normalize_log, reconstruct_positions
from cop_thief_core.interop.hashing import seal


def _record(payload):
    return {"payload": payload, **seal(payload)}


def _log():
    records = [
        _record({"step": 0, "type": "system_spec", "spec": {}, "model": "cli-default"}),
        _record({"step": 1, "position": [3, 3], "hint": "north", "verdict": "truth"}),
        _record({"step": 2, "position": [4, 3], "hint": "אני ליד הנמל", "verdict": "lie"}),
    ]
    return {
        "game_id": "S01-vm__fabi-police-vs-vm__fabi-thief",
        "records": records,
        "summary": {"role": "thief", "result": "survival", "winner_role": "thief",
                    "group_id": "vm__fabi-thief", "opponent_group_id": "vm__fabi-police",
                    "sub_game_number": 2, "duration_seconds": 7.0,
                    "audit": {"passed": True, "verified_steps": 3}},
    }


def test_reconstruct_skips_system_spec_record():
    positions = reconstruct_positions(_log()["records"])
    assert positions == [[3, 3], [4, 3]]  # only the two step records, step-0 skipped


def test_normalize_maps_summary_fields():
    view = normalize_log(_log())
    assert view["role"] == "thief"
    assert view["result"] == "survival"
    assert view["winner"] == "thief"          # winner_role preferred
    assert view["group"] == "vm__fabi-thief"
    assert view["opponent_group_id"] == "vm__fabi-police"
    assert view["sub_game_number"] == 2
    assert view["positions"] == [[3, 3], [4, 3]]


def test_normalize_tolerates_missing_summary():
    view = normalize_log({"records": []})
    assert view["role"] == "-"
    assert view["positions"] == []
    assert view["audit"] == {"passed": True}


def test_records_nested_under_summary_are_accepted():
    records = [_record({"step": 1, "position": [0, 0]})]
    view = normalize_log({"summary": {"records": records, "role": "police"}})
    assert view["positions"] == [[0, 0]]
    assert view["role"] == "police"
