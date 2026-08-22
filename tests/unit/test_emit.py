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


def test_result_carries_league_fields_and_github_links(tmp_path, police_config, thief_config):
    # Friendly (counted absent): truthful but disarmed — and repos for BOTH teams.
    series = _series(police_config, thief_config)
    result = emit_series(police_config, tmp_path, series)
    own_gid = series.own_identity["group_id"]
    opp_gid = series.peer_identity["group_id"]
    final = result["final_result"]
    assert final["games_played_including_this"] == {own_gid: 0, opp_gid: 0}
    assert final["first_meeting_between_groups"] is True
    assert final["diversity_reward_applied"] == {own_gid: False, opp_gid: False}
    assert set(result["links"]["github"]) == {own_gid, opp_gid}
    assert result["links"]["github"][own_gid]  # our repos block is non-empty


def test_counted_run_bumps_counts_and_advances_ledger(tmp_path, police_config, thief_config):
    ledger_path = tmp_path / "ledger.json"
    police_config.override("game.counted", True)
    police_config.override("game.ledger_path", str(ledger_path))
    series = _series(police_config, thief_config)
    result = emit_series(police_config, tmp_path, series)
    own_gid = series.own_identity["group_id"]
    opp_gid = series.peer_identity["group_id"]
    final = result["final_result"]
    assert final["games_played_including_this"][own_gid] == 1  # inclusive of this
    assert final["diversity_reward_applied"][final["winner_group"]] is True
    ledger = json.loads(ledger_path.read_text("utf-8"))
    assert ledger["opponents"][opp_gid]["counted_series"] == 1  # committed evidence
    police_config.override("game.counted", False)  # do not leak into other tests


def test_artifacts_carry_the_playing_commit_of_both_teams(tmp_path, police_config, thief_config):
    """Commit traceability: a grader holding only the submitted repos must be able
    to tie a result to code. Previously the wire identity declared a commit and no
    artifact recorded it, so the mapping existed nowhere we submit."""
    series = _series(police_config, thief_config)
    series.own_identity["github_commit"] = "a" * 40
    series.peer_identity["github_commit"] = "b" * 40
    result = emit_series(police_config, tmp_path, series)
    own_gid = series.own_identity["group_id"]
    opp_gid = series.peer_identity["group_id"]

    for row in result["sub_games"]:
        assert row["github_commit"] == {own_gid: "a" * 40, opp_gid: "b" * 40}

    declaration = json.loads((tmp_path / own_gid / f"declaration_{GAME_ID}.json").read_text())
    blocks = {b["group_id"]: b for b in declaration["groups"].values()}
    assert blocks[own_gid]["github_commit"] == "a" * 40
    assert blocks[opp_gid]["github_commit"] == "b" * 40


def test_the_commit_field_does_not_move_the_consensus_signature(tmp_path, police_config,
                                                                thief_config):
    """The mutual signature is scoped to roles/result/score, so recording a commit
    must not change a hash two teams compare. If this ever fails, partners who
    settled a series with us would disagree about it."""
    bare = _series(police_config, thief_config)
    before = emit_series(police_config, tmp_path / "a", bare)["mutual_agreement"]["sha256"]
    stamped = _series(police_config, thief_config)
    stamped.own_identity["github_commit"] = "a" * 40
    stamped.peer_identity["github_commit"] = "b" * 40
    after = emit_series(police_config, tmp_path / "b", stamped)["mutual_agreement"]["sha256"]
    assert before == after
