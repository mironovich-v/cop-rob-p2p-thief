"""A missing audit must cost one bounded wait, not the whole patience window.

Live evidence (imreeyal counted attempt two, 2026-08-23): their g3 audit never
reached our door — g1's arrived 17:22:32, g2's 17:24:29, and no third one ever
came. Our peer then sat in ``exchange_audit`` for forty minutes in silence,
because that wait was bounded by ``connect_timeout``: the SAME value we raise to
2400s so a partner can bring its doors up at leisure. Their forty g4 greetings
arrived at a peer that was still, correctly, finishing g3.

The two budgets are now separate. These tests pin that separation, the single
re-request, and that a normal audit still returns immediately.
"""

import queue
import types

from cop_thief_core.infra.mcp_client import McpTransport


class _Inboxes:
    def __init__(self, audits):
        self.audits = audits
        self.agreements = queue.Queue()
        self.turns = queue.Queue()
        self.controls = queue.Queue()


def _transport(audits, **kw):
    transport = McpTransport("http://opponent.invalid/mcp", _Inboxes(audits),
                             connect_timeout=2400.0, audit_wait=0.05, **kw)
    transport.sent = []
    transport._call_with_retry = lambda tool, arg, timeout=None: transport.sent.append(tool)
    return transport


def test_a_waiting_audit_is_returned_at_once():
    audits = queue.Queue()
    audits.put({"sender": "thief", "records": []})
    assert _transport(audits).exchange_audit({"sender": "police"}) is not None


def test_a_missing_audit_gives_up_instead_of_hanging_for_the_patience_window():
    """With connect_timeout at 2400s, this test would take forty minutes."""
    transport = _transport(queue.Queue())
    assert transport.exchange_audit({"sender": "police"}) is None


def test_the_audit_is_re_sent_once_before_giving_up():
    """Their first push may have died in flight; a live peer gets one more go."""
    transport = _transport(queue.Queue())
    transport.exchange_audit({"sender": "police"})
    assert transport.sent.count("submit_audit") == 2


def test_a_late_audit_arriving_during_the_second_window_is_accepted():
    audits = queue.Queue()
    transport = _transport(audits)

    def deliver(tool, arg, timeout=None):     # their answer to the re-request
        transport.sent.append(tool)
        if transport.sent.count("submit_audit") == 2:
            audits.put({"sender": "thief", "records": []})

    transport._call_with_retry = deliver
    assert transport.exchange_audit({"sender": "police"}) is not None


def test_the_wait_is_not_the_connect_timeout():
    """The regression itself: the two budgets must not be the same number."""
    transport = _transport(queue.Queue())
    assert transport._audit_wait != transport._connect_timeout


def test_a_missing_audit_is_announced_then_voids_the_sub_game():
    """Announced AND fatal: the series stops rather than settling unverified."""
    import pytest

    from cop_thief_core.exceptions import AuditTimeoutError
    from cop_thief_core.orchestration.summary import finish
    events = []
    rt = types.SimpleNamespace(
        role=types.SimpleNamespace(value="police"),
        _result=("survival", "thief"), records=[],
        handler=types.SimpleNamespace(history=[], received_commits={}),
        _transport=types.SimpleNamespace(exchange_audit=lambda payload: None),
        _listen=events.append, _sub_game_number=3,
        state=types.SimpleNamespace(step_number=35, log=[]),
        _tokens_total=0, _config=types.SimpleNamespace(get=lambda *a: "vm__fabi"),
        _started_at="2026-08-23T14:24:33Z", _started_monotonic=0.0,
    )
    with pytest.raises(AuditTimeoutError, match="VOID"):
        finish(rt)
    assert [e["type"] for e in events] == ["audit_wait", "audit_timeout"]
    assert events[-1]["sub_game"] == 3
