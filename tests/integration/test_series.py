"""Tests for the SDK + series runner (PRD_player_agents, TODO slice 2.6)."""

import threading
from pathlib import Path

from cop_thief_core.constants import Role
from cop_thief_core.sdk import SimulationSdk, StubLlm, role_for, run_series

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_role_for_alternates():
    assert role_for(Role.POLICE, 1) is Role.POLICE
    assert role_for(Role.POLICE, 2) is Role.THIEF
    assert role_for(Role.THIEF, 1) is Role.THIEF
    assert role_for(Role.THIEF, 2) is Role.POLICE


def _join(threads):
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
        assert not thread.is_alive(), "series did not finish"


def test_two_sub_game_series_alternates_and_shares_uid(
    transport_pair, thief_config, police_config
):
    thief_config.override("game.num_games", 2)
    police_config.override("game.num_games", 2)
    thief_t, police_t = transport_pair
    results: dict = {}

    def run(name, role, cfg, transport):
        results[name] = run_series(cfg, role, StubLlm(), transport)

    _join([
        threading.Thread(target=run, args=("thief", Role.THIEF, thief_config, thief_t)),
        threading.Thread(target=run, args=("police", Role.POLICE, police_config, police_t)),
    ])

    thief_series, police_series = results["thief"], results["police"]
    assert len(thief_series.summaries) == len(police_series.summaries) == 2
    assert thief_series.game_uid == police_series.game_uid
    # roles alternate across the series
    assert thief_series.summaries[0]["role"] == "thief"
    assert thief_series.summaries[1]["role"] == "police"
    # both peers agree on each sub-game's result
    for mine, theirs in zip(thief_series.summaries, police_series.summaries, strict=True):
        assert mine["result"] == theirs["result"]


def test_sdk_run_peer_plays_series(transport_pair, tmp_path):
    thief_t, police_t = transport_pair
    thief_sdk = SimulationSdk(REPO_ROOT / "config" / "thief", workdir=tmp_path / "thief")
    police_sdk = SimulationSdk(REPO_ROOT / "config" / "police", workdir=tmp_path / "police")
    thief_sdk.config.override("game.num_games", 2)
    police_sdk.config.override("game.num_games", 2)
    results: dict = {}

    def run(name, sdk, role, transport):
        results[name] = sdk.run_peer(role, transport=transport)

    _join([
        threading.Thread(target=run, args=("thief", thief_sdk, "thief", thief_t)),
        threading.Thread(target=run, args=("police", police_sdk, "police", police_t)),
    ])

    assert len(results["thief"]["summaries"]) == 2
    assert results["thief"]["game_uid"] == results["police"]["game_uid"]
    assert results["thief"]["result"]["result"] in ("capture", "survival")
    # both peers emitted their four artifacts and agree on the mutual signature
    for name in ("thief", "police"):
        files = sorted(p.name for p in Path(results[name]["artifacts_dir"]).glob("*.json"))
        assert len(files) == 6  # declaration + result + 2*(config+log)
        assert any(f.startswith("declaration_") for f in files)
        assert any(f.startswith("result_") for f in files)
    assert results["thief"]["report"]["mutual_agreement"]["sha256"] == \
        results["police"]["report"]["mutual_agreement"]["sha256"]


def test_injected_transport_never_lingers(tmp_path, monkeypatch):
    """A test/GUI peer that brought its own transport owns no server, so there is
    no ack to flush — it must not pay the shutdown grace."""
    slept: list[float] = []
    monkeypatch.setattr("cop_thief_core.sdk.sdk.time.sleep", slept.append)
    sdk = SimulationSdk(REPO_ROOT / "config" / "police", workdir=tmp_path)
    sdk._linger_for_final_ack(built_transport=False)
    assert slept == []


def test_owned_server_lingers_for_the_final_ack(tmp_path, monkeypatch):
    """The final submit_audit ack is written by a DAEMON server thread: exiting the
    instant the runtime drains the audit inbox drops it, and the opponent logs an
    otherwise-clean game as audit_send_unacknowledged (il-nv-ai, both runs
    2026-08-21). Reproduced at 15.0s client timeout; 0.22s ack with the grace."""
    slept: list[float] = []
    monkeypatch.setattr("cop_thief_core.sdk.sdk.time.sleep", slept.append)
    sdk = SimulationSdk(REPO_ROOT / "config" / "police", workdir=tmp_path)
    sdk._linger_for_final_ack(built_transport=True)
    assert slept and slept[0] > 0
    assert slept[0] == sdk.config.get("network.shutdown_grace_seconds", None)
