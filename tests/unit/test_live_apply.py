"""Unit tests for the live-GUI view-model (Stage 7.4): event -> window mutations,
the clock start/freeze, and the local-truth boundary (rendered view carries no
opponent truth). A FakeWindow records calls; no Tk is imported."""

from cop_thief_core.constants import MoveType
from cop_thief_core.domain.brains import Decision
from cop_thief_core.gui.live_apply import LiveState, apply_event


class FakeWindow:
    """Records render/label/turn calls instead of drawing."""

    def __init__(self):
        self.rendered = []
        self.labels = {}
        self.turns = []

    def render(self, view):
        self.rendered.append(view)

    def set_label(self, key, text):
        self.labels[key] = text

    def set_turn(self, is_my_turn, message=None):
        self.turns.append((is_my_turn, message))


def _state(role="thief"):
    return LiveState(role=role, window=FakeWindow())


def test_negotiated_starts_clock_and_thief_moves_first():
    state = _state("thief")
    apply_event(state, {"type": "negotiated", "view": {"step": 0}})
    assert state.clock_running is True
    assert state.window.rendered == [{"step": 0}]
    assert "Agreement signed" in state.window.labels["status"]
    assert state.window.turns[-1] == (True, None)  # thief's turn first


def test_police_does_not_move_first_on_negotiated():
    state = _state("police")
    apply_event(state, {"type": "negotiated", "view": {"step": 0}})
    assert state.window.turns[-1] == (False, None)


def test_incoming_shows_hint_and_grants_turn():
    state = _state("police")
    apply_event(state, {"type": "incoming", "view": {"step": 2},
                        "message": {"step": 2, "hint": "אני ליד הנמל"}})
    assert state.window.labels["hint_in"] == "step 2: אני ליד הנמל"
    assert state.window.turns[-1] == (True, None)


def test_error_event_never_renders_a_view():
    state = _state()
    apply_event(state, {"type": "error", "message": "boom"})
    assert state.window.rendered == []  # no board update on error
    assert state.window.labels["status"] == "boom"
    assert state.window.turns[-1] == (False, "ERROR - see status")


def test_moved_reports_decision_and_ends_turn():
    state = _state()
    decision = Decision(MoveType.MOVE, None, "heading north", "truth",
                        fallback=True, response_seconds=1.23)
    apply_event(state, {"type": "moved", "view": {"step": 3}, "decision": decision,
                        "usage": {"total": 40, "match_total": 120}, "commit": "a" * 40})
    assert state.window.labels["tokens"] == "40 / 120"
    assert state.window.labels["hint_out"] == "step 3: heading north"
    assert state.window.labels["verdict"] == "truth (fallback)"
    assert state.window.labels["commit"] == "a" * 32 + "..."
    assert state.window.turns[-1] == (False, None)


def test_game_over_freezes_clock_and_summarizes():
    state = _state()
    state.clock_running = True
    summary = {"result": "capture", "winner": "police", "tokens_total": 500,
               "duration_seconds": 12, "audit": {"passed": True, "verified_steps": 6}}
    apply_event(state, {"type": "game_over", "view": {"step": 6}, "summary": summary})
    assert state.clock_running is False
    assert state.window.turns[-1] == (False, "GAME OVER: capture - winner POLICE")
    assert "Audit PASSED" in state.window.labels["status"]


def test_live_view_carries_no_opponent_truth(transport_pair, thief_config):
    """The snapshot the runtime hands the GUI must expose only local truth."""
    from cop_thief_core.constants import Role
    from cop_thief_core.orchestration.runtime import PeerRuntime

    thief_t, _ = transport_pair
    runtime = PeerRuntime(Role.THIEF, thief_config, thief_t)
    view = runtime.view()
    # only this peer's own truth + belief — never an opponent position/role
    assert set(view) <= {"role", "step", "position", "barriers", "barriers_used",
                         "visited", "belief"}
    assert not any("opp" in key or "enemy" in key for key in view)
