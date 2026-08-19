"""Display-guarded smoke test for the Tk shell (Stage 7.4c). Builds a real
PeerWindow and drives it through the 7.4a view-model, asserting the local-truth
board + labels update. Skips cleanly when no display is available (headless CI);
gui/* is coverage-omitted, so this only proves the shell wires up when run.
"""

import pytest

tk = pytest.importorskip("tkinter")

from cop_thief_core.constants import MoveType  # noqa: E402
from cop_thief_core.domain.brains import Decision  # noqa: E402
from cop_thief_core.gui.live_apply import LiveState, apply_event  # noqa: E402
from cop_thief_core.gui.window import PeerWindow  # noqa: E402


@pytest.fixture
def window():
    try:
        win = PeerWindow("smoke", board_size=7, cell_px=20, game_id="g1")
    except tk.TclError:
        pytest.skip("no display available for Tk")
    win.root.withdraw()
    yield win
    win.root.destroy()


def _view():
    return {"role": "police", "step": 2, "position": (0, 0), "barriers": [(1, 1)],
            "barriers_used": 1, "visited": [(0, 0)],
            "belief": [[0.0] * 7 for _ in range(7)]}


def test_window_renders_local_view_and_labels(window):
    state = LiveState(role="police", window=window)
    apply_event(state, {"type": "negotiated", "view": _view()})
    window.root.update()
    assert window.labels["step"].cget("text") == "2"
    assert "Agreement" in window.labels["status"].cget("text")
    assert state.clock_running is True


def test_moved_and_game_over_update_the_window(window):
    state = LiveState(role="police", window=window)
    decision = Decision(MoveType.MOVE, None, "north", "truth")
    apply_event(state, {"type": "moved", "view": _view(), "decision": decision,
                        "usage": {"total": 0, "match_total": 0}, "commit": "a" * 40})
    apply_event(state, {"type": "game_over", "view": _view(),
                        "summary": {"result": "capture", "winner": "police",
                                    "tokens_total": 0, "duration_seconds": 1,
                                    "audit": {"passed": True, "verified_steps": 3}}})
    window.root.update()
    assert window.labels["hint_out"].cget("text") == "step 2: north"
    assert "GAME OVER" in window.banner.cget("text")
    assert state.clock_running is False
