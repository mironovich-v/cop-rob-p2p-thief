"""Replay view (Stage 7.5b): a pure test for barrier parsing (always runs) and a
display-guarded ReplayApp smoke test that steps through both revealed trajectories.
Skips cleanly with no display; gui/* is coverage-omitted."""

import json

import pytest

from cop_thief_core.gui.replay import barriers_from_state
from cop_thief_core.interop.hashing import seal

GAME_ID = "S01-vm__fabi-police-vs-vm__fabi-thief"


def test_barriers_from_state_parses_and_tolerates_junk():
    state = "grid=7x7;self=[4, 3];barriers=[[1, 1], [2, 2]]"
    assert barriers_from_state(state) == [(1, 1), (2, 2)]
    assert barriers_from_state("grid=7x7;self=[0, 0];barriers=[]") == []
    assert barriers_from_state("no-barriers-here") == []
    assert barriers_from_state(None) == []


def _record(payload):
    return {"payload": payload, **seal(payload)}


def _write_log(base, group, positions, opp):
    records = [_record({"step": 0, "type": "system_spec", "model": "cli-default"})]
    records += [_record({"step": i + 1, "position": list(pos),
                         "state": f"grid=7x7;self={list(pos)};barriers=[]",
                         "hint": "north", "verdict": "truth"})
                for i, pos in enumerate(positions)]
    log = {"game_id": GAME_ID, "records": records,
           "summary": {"sub_game_number": 1, "group_id": group,
                       "opponent_group_id": opp, "role": "police",
                       "result": "capture", "winner_role": "police",
                       "audit": {"passed": True, "verified_steps": len(positions)}}}
    path = base / group / f"log_{GAME_ID}_g01.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(log), encoding="utf-8")
    return path, log


@pytest.fixture
def replay_app(tmp_path, police_config):
    tk = pytest.importorskip("tkinter")
    own_path, own_log = _write_log(tmp_path, "vm__fabi-police", [(0, 0), (1, 0)],
                                   "vm__fabi-thief")
    _write_log(tmp_path, "vm__fabi-thief", [(3, 3), (3, 4), (3, 5)], "vm__fabi-police")
    from cop_thief_core.gui.replay import ReplayApp
    try:
        app = ReplayApp(police_config, own_log, log_path=str(own_path))
    except tk.TclError:
        pytest.skip("no display available for Tk")
    app._window.root.withdraw()
    yield app
    app._window.root.destroy()


def test_replay_reconstructs_both_trajectories(replay_app):
    # longest track (opponent, 3) drives the total; my track (2) freezes at its last
    assert replay_app._total() == 3
    replay_app._advance()
    replay_app._advance()
    replay_app._window.root.update()
    assert (1, 0) in replay_app._visited                 # my revealed position
    assert "verified OK" in replay_app._window.labels["commit"].cget("text")
    assert "BOTH agents shown" in replay_app._window.labels["status"].cget("text")


def test_replay_done_banner_after_all_steps(replay_app):
    for _ in range(replay_app._total() + 1):
        replay_app._advance()
    replay_app._window.root.update()
    assert "REPLAY DONE" in replay_app._window.banner.cget("text")
    assert "POLICE" in replay_app._window.banner.cget("text")
