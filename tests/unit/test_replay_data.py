"""Unit tests for replay crypto re-verification + sibling-log discovery (Stage 7.5a).
Full opponent truth is reconstructed ONLY here, from the mutually-revealed logs."""

import json

from cop_thief_core.gui.replay_data import (
    discover_subgames,
    opponent_positions,
    subgame_log_path,
    verify_record,
)
from cop_thief_core.interop.hashing import seal

GAME_ID = "S01-vm__fabi-police-vs-vm__fabi-thief"


def _record(payload):
    return {"payload": payload, **seal(payload)}


def test_verify_record_passes_reveals_and_flags_tamper():
    records = [_record({"step": 1, "position": [2, 2]})]
    assert verify_record(records, 0) == "verified OK"
    records[0]["payload"]["position"] = [5, 5]  # tamper after sealing
    assert verify_record(records, 0) == "TAMPERED!"


def test_verify_record_out_of_range_is_dash():
    assert verify_record([], 0) == "-"
    assert verify_record([_record({"step": 1})], 3) == "-"


def _write_log(base, group, sub, positions):
    records = [_record({"step": 0, "type": "system_spec"})]
    records += [_record({"step": i + 1, "position": pos}) for i, pos in enumerate(positions)]
    log = {"game_id": GAME_ID, "records": records,
           "summary": {"sub_game_number": sub, "opponent_group_id": "vm__fabi-police",
                       "group_id": group}}
    path = base / group / f"log_{GAME_ID}_g{sub:02d}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(log), encoding="utf-8")
    return path, log


def test_opponent_positions_reads_sibling_log(tmp_path):
    own_path, own_log = _write_log(tmp_path, "vm__fabi-thief", 1, [[3, 3], [4, 3]])
    _write_log(tmp_path, "vm__fabi-police", 1, [[0, 0], [1, 0], [2, 0]])
    positions = opponent_positions(own_path, own_log)
    assert positions == [[0, 0], [1, 0], [2, 0]]  # both trajectories now knowable


def test_opponent_positions_missing_sibling_returns_empty(tmp_path):
    own_path, own_log = _write_log(tmp_path, "vm__fabi-thief", 1, [[3, 3]])
    assert opponent_positions(own_path, own_log) == []  # no sibling -> heatmap only
    assert opponent_positions(None, own_log) == []


def test_discover_subgames_and_paths(tmp_path):
    own_path, own_log = _write_log(tmp_path, "vm__fabi-thief", 1, [[3, 3]])
    _write_log(tmp_path, "vm__fabi-thief", 3, [[3, 3]])
    assert discover_subgames(own_path, own_log) == [1, 3]
    expected = own_path.parent / f"log_{GAME_ID}_g03.json"
    assert subgame_log_path(own_path, own_log, 3) == expected
