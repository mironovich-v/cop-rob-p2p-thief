"""A sub-game starts when it OPENS, not when the peer process launched.

Cross-diff with imreeyal (2026-08-23) caught this: our g1 reported
`started_at` 12:12:16Z against their correct 12:27:06Z — a fifteen-minute gap,
which was exactly how long our peer sat in the handshake waiting for their doors.
`_started_monotonic` was already reset after the handshake so DURATION was right,
but the wall-clock stamp was never refreshed, and `ended_at` is derived from it —
so both ends of every filed row were shifted earlier by the pre-game hold.

Filing a counted report whose start time precedes the agreed T by a quarter of an
hour is the kind of discrepancy an auditor is entitled to ask about.
"""

from cop_thief_core.constants import Role
from cop_thief_core.orchestration.runtime import PeerRuntime


def test_marking_the_start_refreshes_both_clocks(police_config, monkeypatch):
    runtime = PeerRuntime(Role.POLICE, police_config, transport=None)
    launched_at, launched_mono = runtime._started_at, runtime._started_monotonic

    monkeypatch.setattr("cop_thief_core.orchestration.runtime.now_iso",
                        lambda: "2026-08-23T12:27:06.000000+00:00")
    monkeypatch.setattr("cop_thief_core.orchestration.runtime.time.monotonic",
                        lambda: launched_mono + 900.0)          # 15 minutes holding

    runtime._mark_game_start()

    assert runtime._started_at == "2026-08-23T12:27:06.000000+00:00"
    assert runtime._started_at != launched_at
    assert runtime._started_monotonic == launched_mono + 900.0


def test_duration_is_measured_from_the_open_not_the_launch(police_config, monkeypatch):
    """The hold must not be billed to the sub-game's duration either."""
    runtime = PeerRuntime(Role.POLICE, police_config, transport=None)
    base = runtime._started_monotonic
    monkeypatch.setattr("cop_thief_core.orchestration.runtime.time.monotonic",
                        lambda: base + 900.0)
    runtime._mark_game_start()
    monkeypatch.setattr("cop_thief_core.orchestration.runtime.time.monotonic",
                        lambda: base + 900.0 + 42.0)
    import time as _t
    monkeypatch.setattr(_t, "monotonic", lambda: base + 900.0 + 42.0)
    assert round(_t.monotonic() - runtime._started_monotonic, 1) == 42.0
