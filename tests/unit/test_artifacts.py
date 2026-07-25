"""Unit tests for the four game-artifact builders (Stage 7.1): they share one
game_uid, cross-link, lock the config, and carry the mutual-agreement signature."""

from cop_thief_core.interop.negotiation import terms_from_config
from cop_thief_core.orchestration.sealing import identity_from_config
from cop_thief_core.reporting.artifact_helpers import canonical_sha256
from cop_thief_core.reporting.artifacts import (
    build_config_artifact,
    build_declaration,
    build_log,
    build_result,
    config_filename,
    declaration_filename,
    log_filename,
    result_filename,
)
from cop_thief_core.reporting.report_writer import consensus_signature

GAME_ID = "S01R02-vm__fabi-vs-team13"
GAME_UID = "abcdef0123456789"
GROUP_A = "vm__fabi-police"
GROUP_B = "team13-thief"


def _summary() -> dict:
    records = [{"step": 0, "commit": "c0"}, {"step": 1, "commit": "c1"}]
    return {
        "sub_game_number": 3,
        "role": "police",
        "result": "capture",
        "winner": "police",
        "steps": 1,
        "started_at": "2026-07-21T10:00:00+00:00",
        "duration_seconds": 12.5,
        "tokens_total": 4321,
        "audit": {"passed": True, "verified_steps": 2, "failed_steps": []},
        "records": records,
    }


def test_filenames_derive_from_game_id():
    assert declaration_filename(GAME_ID) == f"declaration_{GAME_ID}.json"
    assert config_filename(GAME_ID, 1) == f"config_{GAME_ID}_g01.json"
    assert log_filename(GAME_ID, 12) == f"log_{GAME_ID}_g12.json"
    assert result_filename(GAME_ID) == f"result_{GAME_ID}.json"


def test_config_artifact_locks_terms(police_config):
    terms = terms_from_config(police_config)
    art = build_config_artifact(terms, GAME_ID, GAME_UID, 2)
    assert art["config_sha256"] == canonical_sha256(terms)
    assert art["game_uid"] == GAME_UID
    assert art["config_name"] == config_filename(GAME_ID, 2)
    assert art["board_size"] == terms["board_size"]  # terms spread into the artifact


def test_declaration_has_two_signed_group_blocks(police_config, thief_config):
    own = identity_from_config(police_config)
    opp = identity_from_config(thief_config)
    decl = build_declaration(GAME_ID, GAME_UID, "Asia/Jerusalem", "t0", "t1", 6, 200000, own, opp)
    assert decl["declaration_type"] == "pre_game_declaration"
    assert set(decl["groups"]) == {"group_1", "group_2"}
    block = decl["groups"]["group_1"]
    signature = block.pop("signature")
    assert signature == consensus_signature(block)  # self-signed over the block
    assert set(block["hardware_spec"]) == {
        "cpu_type", "cpu_freq_mhz", "cpu_cores", "ram_gb", "gpu_model", "vram_gb"
    }


def test_log_mutual_agreement_signs_records():
    summary = _summary()
    log = build_log(summary, GAME_ID, GAME_UID, GROUP_A, GROUP_B)
    assert log["game_uid"] == GAME_UID
    assert log["records"] == summary["records"]
    assert log["summary"]["ended_at"] == "2026-07-21T10:00:12.500000+00:00"
    agreement = log["mutual_agreement"]
    assert agreement["opponent_group_id"] == GROUP_B
    assert agreement["sha256"] == consensus_signature(summary["records"])
    assert agreement["confirmed"] is True


def test_result_aggregates_and_confirms():
    sub_games = [
        {"sub_game_number": 1, "tokens": {GROUP_A: 100, GROUP_B: 90}, "audit": {"log_verified": True}},
        {"sub_game_number": 2, "tokens": {GROUP_A: 50, GROUP_B: 70}, "audit": {"log_verified": True}},
    ]
    aggregate_out = {"winner_group": GROUP_A, "scores": {GROUP_A: 5, GROUP_B: 3}}
    result = build_result(GAME_ID, GAME_UID, [GROUP_A, GROUP_B], sub_games, aggregate_out, "deadbeef")
    assert result["num_sub_games"] == 2
    assert result["final_result"]["tokens_total_series"] == {GROUP_A: 150, GROUP_B: 160}
    assert result["final_result"]["winner_group"] == GROUP_A
    assert result["mutual_agreement"] == {"sha256": "deadbeef", "confirmed": True}


def test_all_artifacts_share_one_game_uid(police_config, thief_config):
    terms = terms_from_config(police_config)
    own = identity_from_config(police_config)
    opp = identity_from_config(thief_config)
    decl = build_declaration(GAME_ID, GAME_UID, "Asia/Jerusalem", "t0", "t1", 6, 200000, own, opp)
    cfg = build_config_artifact(terms, GAME_ID, GAME_UID, 1)
    log = build_log(_summary(), GAME_ID, GAME_UID, GROUP_A, GROUP_B)
    res = build_result(GAME_ID, GAME_UID, [GROUP_A, GROUP_B], [], {}, "sig")
    assert {a["game_uid"] for a in (decl, cfg, log, res)} == {GAME_UID}
    assert {a["links"]["declaration"] for a in (decl, cfg, log, res)} == {declaration_filename(GAME_ID)}
