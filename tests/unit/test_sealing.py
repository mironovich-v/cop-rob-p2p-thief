"""Tests for the sealing helpers (PRD_commit_reveal / orchestrator, slice 2.5a)."""

from cop_thief_core.constants import Direction, MoveType, Role
from cop_thief_core.domain.brains import Decision
from cop_thief_core.domain.own_state import OwnGameState
from cop_thief_core.interop import verify
from cop_thief_core.orchestration.sealing import (
    build_turn_message,
    identity_from_config,
    now_iso,
    sealed_step_record,
)

MOVE_SET = ["N", "S", "E", "W", "STAY"]


def _decision():
    return Decision(MoveType.MOVE, Direction.N, "hi", "truth", response_seconds=0.1)


def test_now_iso_is_isoformat():
    assert "T" in now_iso()


def test_sealed_step_record_reverifies():
    state = OwnGameState(Role.THIEF, (2, 2), 5, MOVE_SET)
    state.apply_move(MoveType.MOVE, Direction.N)
    record = sealed_step_record(state, _decision(), {"model": "template", "total": 0}, 0)
    assert set(record) >= {"payload", "nonce", "commit"}
    assert len(record["commit"]) == 64
    verify(record["payload"], record["nonce"], record["commit"])  # re-hash matches
    payload = record["payload"]
    assert payload["position"] == [1, 2]
    assert payload["move"] == "MOVE:N"
    assert payload["intent"] == "truth"
    assert payload["hint"] == "hi"
    assert "prompt_discussion" in payload
    assert "response_seconds" in payload
    assert "random_move" in payload


def test_build_turn_message_carries_barrier_and_claims():
    state = OwnGameState(Role.POLICE, (2, 2), 5, MOVE_SET)
    state.apply_move(MoveType.BARRIER, Direction.E, barriers_max=5)
    msg = build_turn_message(
        state, "police", "watch out", {"2,2": 0.9}, "c" * 64, capture_claim=[1, 1]
    )
    assert msg.sender == "police"
    assert msg.barrier_placed == [2, 3]
    assert msg.capture_claim == [1, 1]
    assert msg.smell_grid == {"2,2": 0.9}


def test_identity_from_config(police_config):
    identity = identity_from_config(police_config)
    assert identity["group_id"] == "vm__fabi-police"
    assert identity["members"]  # placeholder list present


def test_identity_declares_the_playing_commit(police_config):
    # il-nv-ai's --real-team gate refuses a negotiate whose
    # identity.github_commit is null/empty/placeholder (book p.156 commit
    # traceability, enforced by a live partner). In a git checkout the field
    # carries rev-parse HEAD; standalone exports fall back to core_manifest.
    identity = identity_from_config(police_config)
    commit = identity["github_commit"]
    assert isinstance(commit, str) and len(commit) == 40
    int(commit, 16)  # 40-hex
