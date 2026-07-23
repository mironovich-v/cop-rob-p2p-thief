"""Integration: two PeerRuntimes play a full sub-game over the in-process
FakeTransport (no central server — only message passing). PRD_orchestrator_fsm /
player_agents (TODO slice 2.5b)."""

import threading

import pytest

from cop_thief_core.constants import Role
from cop_thief_core.orchestration.runtime import PeerRuntime


class _SilentTransport:
    """Never delivers a turn — used to exercise the watchdog timeout."""

    def poll_turn(self, timeout):
        return None


def _run_match(thief, police) -> dict:
    results: dict = {}

    def runner(name, runtime):
        results[name] = runtime.run()

    threads = [
        threading.Thread(target=runner, args=("police", police), daemon=True),
        threading.Thread(target=runner, args=("thief", thief), daemon=True),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
        assert not thread.is_alive(), "peer runtime did not finish"
    return results


@pytest.fixture
def paired(transport_pair, thief_config, police_config):
    thief_t, police_t = transport_pair
    thief = PeerRuntime(Role.THIEF, thief_config, thief_t)
    police = PeerRuntime(Role.POLICE, police_config, police_t)
    return thief, police


def test_full_match_completes_and_agrees(paired):
    results = _run_match(*paired)
    assert results["thief"]["result"] == results["police"]["result"]
    assert results["thief"]["winner"] == results["police"]["winner"]
    assert results["thief"]["result"] in ("capture", "survival")


def test_audits_pass_both_ways(paired):
    results = _run_match(*paired)
    assert results["thief"]["audit"]["passed"] is True
    assert results["police"]["audit"]["passed"] is True
    assert results["thief"]["audit"]["verified_steps"] > 0


def test_logs_are_sealed_per_step(paired):
    results = _run_match(*paired)
    for record in results["thief"]["records"]:
        assert set(record) >= {"payload", "nonce", "commit"}
        assert len(record["commit"]) == 64


def test_summary_carries_identity_and_timer(paired):
    results = _run_match(*paired)
    for summary in results.values():
        assert summary["group_name"] == "VM-Fabi"
        assert summary["sub_game_number"] == 1
        assert summary["duration_seconds"] >= 0
        assert summary["started_at"]


def test_shared_game_uid_derived(paired):
    thief, police = paired
    _run_match(thief, police)
    assert thief.game_uid == police.game_uid
    assert thief.game_id == "vm__fabi-police-vs-vm__fabi-thief"


def test_timeout_when_opponent_silent(police_config):
    police_config.override("network.turn_timeout_seconds", 0.05)
    lonely = PeerRuntime(Role.POLICE, police_config, _SilentTransport())
    assert lonely.run(skip_negotiation=True)["result"] == "timeout"
