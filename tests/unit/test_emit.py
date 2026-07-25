"""Unit tests for emit_series (Stage 7.2): it writes the four named artifacts to
disk and returns a result whose mutual signature is byte-identical across peers."""

import json

from cop_thief_core.orchestration.sealing import identity_from_config
from cop_thief_core.reporting.emit import emit_series
from cop_thief_core.sdk.series import SeriesResult

GAME_ID = "S01R02-vm__fabi-vs-team13"
GAME_UID = "abcdef0123456789"


def _summary(number, role, result, winner):
    return {
        "sub_game_number": number, "role": role, "result": result, "winner": winner,
        "steps": 5, "started_at": "2026-07-25T10:00:00+00:00", "duration_seconds": 3.0,
        "tokens_total": 100 * number,
        "audit": {"passed": True, "verified_steps": 2, "failed_steps": []},
        "records": [{"step": 0, "commit": f"c{number}"}],
    }


def _series(police_config, thief_config):
    own = identity_from_config(police_config)
    opp = identity_from_config(thief_config)
    summaries = [_summary(1, "police", "capture", "police"),
                 _summary(2, "thief", "survival", "thief")]
    return SeriesResult(summaries, own, opp, GAME_ID, GAME_UID)


def test_emit_writes_four_named_artifacts(tmp_path, police_config, thief_config):
    series = _series(police_config, thief_config)
    emit_series(police_config, tmp_path, series)
    out = tmp_path / series.own_identity["group_id"]
    names = sorted(path.name for path in out.glob("*.json"))
    assert names == sorted([
        f"declaration_{GAME_ID}.json",
        f"config_{GAME_ID}_g01.json", f"config_{GAME_ID}_g02.json",
        f"log_{GAME_ID}_g01.json", f"log_{GAME_ID}_g02.json",
        f"result_{GAME_ID}.json",
    ])


def test_emit_result_roundtrips_and_derives_totals(tmp_path, police_config, thief_config):
    series = _series(police_config, thief_config)
    result = emit_series(police_config, tmp_path, series)
    own_gid = series.own_identity["group_id"]
    on_disk = json.loads((tmp_path / own_gid / f"result_{GAME_ID}.json").read_text("utf-8"))
    assert on_disk == result  # returned dict is exactly what was written
    assert on_disk["game_uid"] == GAME_UID
    assert on_disk["final_result"]["tokens_total_series"][own_gid] == 300  # 100 + 200, derived
    assert on_disk["mutual_agreement"]["confirmed"] is True


def test_both_peers_agree_on_mutual_signature(tmp_path, police_config, thief_config):
    own = identity_from_config(police_config)
    opp = identity_from_config(thief_config)
    police_view = [_summary(1, "police", "capture", "police"),
                   _summary(2, "thief", "survival", "thief")]
    # the thief peer sees mirrored roles but the SAME absolute outcome per sub-game
    thief_view = [_summary(1, "thief", "capture", "police"),
                  _summary(2, "police", "survival", "thief")]
    police = emit_series(police_config, tmp_path / "p",
                         SeriesResult(police_view, own, opp, GAME_ID, GAME_UID))
    thief = emit_series(thief_config, tmp_path / "t",
                        SeriesResult(thief_view, opp, own, GAME_ID, GAME_UID))
    assert police["mutual_agreement"]["sha256"] == thief["mutual_agreement"]["sha256"]
