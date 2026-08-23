"""A stalled peer must say where it stopped, and the line must survive SIGTERM.

Live evidence (imreeyal counted attempts, 2026-08-23): two aborts at the g3->g4
seam, and the peer's log was zero bytes for thirty minutes in both. These tests
pin the two properties that failure needed — the seam is announced BEFORE the
blocking call, and every line is flushed — plus the promise that adding a
progress consumer never displaces the GUI's listener.
"""

import io

from cop_thief_core.shared.progress import progress_listener

CLOCK = lambda: "17:30:00"  # noqa: E731 — fixed clock keeps assertions exact


def _sink():
    return io.StringIO()


def test_seam_events_are_rendered_with_their_fields():
    out = _sink()
    listen = progress_listener(stream=out, clock=CLOCK)
    listen({"type": "sub_game_open", "sub_game": 4, "of": 6, "role": "thief",
            "dial": "https://cop.example.com/mcp"})
    line = out.getvalue().strip()
    assert line.startswith("17:30:00  opening")
    assert "sub_game=4" in line and "of=6" in line and "role=thief" in line
    assert "dial=https://cop.example.com/mcp" in line


def test_the_two_stall_points_are_announced():
    """Both aborts died in these calls; a line printed after them is useless."""
    out = _sink()
    listen = progress_listener(stream=out, clock=CLOCK)
    listen({"type": "handshake_wait", "sub_game": 4, "role": "thief"})
    listen({"type": "audit_wait", "sub_game": 3, "result": "survival"})
    text = out.getvalue()
    assert "waiting for opponent agreement" in text
    assert "waiting for opponent audit" in text
    assert "sub_game=3" in text


def test_unknown_events_print_nothing():
    """The runtime emits view-carrying GUI events every step — never printed."""
    out = _sink()
    listen = progress_listener(stream=out, clock=CLOCK)
    listen({"type": "moved", "view": {"step": 1}})
    listen({"type": "incoming", "message": {"step": 1}})
    assert out.getvalue() == ""


def test_missing_fields_are_skipped_not_rendered_as_none():
    out = _sink()
    listen = progress_listener(stream=out, clock=CLOCK)
    listen({"type": "sub_game_done", "sub_game": 2, "result": "capture"})
    line = out.getvalue()
    assert "steps=" not in line and "None" not in line
    assert "result=capture" in line


def test_every_line_is_flushed():
    """Block-buffered output dies with the process; that is why we lost it."""
    flushes = []

    class Watched(io.StringIO):
        def flush(self):
            flushes.append(self.getvalue())

    out = Watched()
    listen = progress_listener(stream=out, clock=CLOCK)
    listen({"type": "sub_game_open", "sub_game": 1, "of": 6, "role": "police"})
    assert flushes, "progress was written without a flush"


def test_an_existing_listener_still_receives_everything():
    """The GUI player passes its own queue; progress must not displace it."""
    seen = []
    out = _sink()
    listen = progress_listener(inner=seen.append, stream=out, clock=CLOCK)
    listen({"type": "moved", "view": {}})
    listen({"type": "sub_game_done", "sub_game": 1, "result": "capture", "steps": 11})
    assert [e["type"] for e in seen] == ["moved", "sub_game_done"]
    assert "settled" in out.getvalue()
