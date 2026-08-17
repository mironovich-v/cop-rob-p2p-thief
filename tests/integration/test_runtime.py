"""Integration: two PeerRuntimes play a full sub-game over the in-process
FakeTransport (no central server — only message passing). PRD_orchestrator_fsm /
player_agents (TODO slice 2.5b)."""

import threading
import time

import pytest

from cop_thief_core.constants import Role
from cop_thief_core.orchestration.runtime import PeerRuntime
from cop_thief_core.protocol import TurnMessage


class _SilentTransport:
    """Never delivers a turn — used to exercise the watchdog timeout."""

    def poll_turn(self, timeout):
        return None


class _DuplicatingTransport:
    """Wraps a transport and re-delivers each polled turn once — a network re-send.
    A robust peer must ignore the duplicate and still settle correctly."""

    def __init__(self, inner):
        self._inner = inner
        self._dup = None

    def poll_turn(self, timeout):
        if self._dup is not None:
            msg, self._dup = self._dup, None
            return msg
        msg = self._inner.poll_turn(timeout)
        if msg is not None:
            self._dup = dict(msg)
        return msg

    def __getattr__(self, name):
        return getattr(self._inner, name)


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


def test_runtime_emits_live_event_stream(transport_pair, thief_config, police_config):
    """The listener sees negotiated -> moved... -> game_over, and no `moved`
    view ever carries opponent truth (the live-GUI local-truth boundary)."""
    thief_t, police_t = transport_pair
    events: list[dict] = []
    thief = PeerRuntime(Role.THIEF, thief_config, thief_t, listener=events.append)
    police = PeerRuntime(Role.POLICE, police_config, police_t)
    _run_match(thief, police)

    kinds = [event["type"] for event in events]
    assert kinds[0] == "negotiated"
    assert kinds[-1] == "game_over"
    assert "moved" in kinds
    for event in events:
        if event["type"] == "moved":
            assert "commit" in event and len(event["commit"]) == 64
            assert not any("opp" in key or "enemy" in key for key in event["view"])
    assert events[-1]["summary"]["result"] in ("capture", "survival")


def test_duplicate_deliveries_do_not_desync(transport_pair, thief_config, police_config):
    """Every opponent turn delivered twice; the peer ignores the dups and the match
    still finishes, agrees, and audits clean (AC7 stale/duplicate robustness)."""
    thief_t, police_t = transport_pair
    thief = PeerRuntime(Role.THIEF, thief_config, thief_t)
    police = PeerRuntime(Role.POLICE, police_config, _DuplicatingTransport(police_t))
    results = _run_match(thief, police)
    assert results["thief"]["result"] == results["police"]["result"]
    assert results["thief"]["result"] in ("capture", "survival")
    assert results["police"]["audit"]["passed"] is True


class _JunkFloodTransport:
    """Delivers the SAME already-played duplicate on every poll — a flood of
    tolerated junk that must never renew the turn deadline (SPEC §7.1)."""

    def __init__(self, message):
        self._message = message

    def poll_turn(self, timeout):
        return dict(self._message)

    def exchange_audit(self, payload):
        return None


def test_junk_flood_never_renews_the_deadline(police_config):
    police_config.override("network.turn_timeout_seconds", 0.6)
    police_config.override("network.poll_interval_seconds", 0.05)
    junk = {"step": 1, "sender": "thief", "hint": "", "smell_grid": {},
            "commit": "a" * 64, "timestamp": "t", "barrier_placed": None,
            "capture_claim": None, "claim_response": None, "win_claim": None}
    runtime = PeerRuntime(Role.POLICE, police_config, _JunkFloodTransport(junk))
    runtime.handler.process(TurnMessage.from_dict(junk))  # step 1 already played
    start = time.monotonic()
    summary = runtime.run(skip_negotiation=True)
    assert summary["result"] == "timeout"  # the flood did not keep the game alive
    assert time.monotonic() - start < 5.0
