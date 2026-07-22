"""Tests for McpTransport (PRD_mcp_protocol, TODO slice 2.4).

The opponent handle is a FastMCP object (in-memory), so send/receive round-trips
run with no network or bound port.
"""

import pytest

from cop_thief_core.exceptions import SimulationError
from cop_thief_core.infra.mcp_client import McpTransport
from cop_thief_core.infra.mcp_server import PeerInboxes, build_peer_server


def _pair(connect_timeout=60.0):
    inboxes_b = PeerInboxes()
    server_b = build_peer_server("thief", inboxes_b)
    inboxes_a = PeerInboxes()
    transport_a = McpTransport(server_b, inboxes_a, connect_timeout=connect_timeout)
    return transport_a, inboxes_a, inboxes_b


def test_send_turn_delivers_to_opponent_inbox():
    transport_a, _, inboxes_b = _pair()
    transport_a.send_turn({"step": 7})
    assert inboxes_b.turns.get_nowait() == {"step": 7}


def test_send_control_best_effort_delivers():
    transport_a, _, inboxes_b = _pair()
    transport_a.send_control({"kind": "status"})
    assert inboxes_b.controls.get_nowait() == {"kind": "status"}


def test_exchange_agreement_sends_and_reads_own_inbox():
    transport_a, inboxes_a, inboxes_b = _pair()
    inboxes_a.agreements.put({"reply": "theirs"})  # opponent already replied
    result = transport_a.exchange_agreement({"terms": {"board_size": 7}})
    assert result == {"reply": "theirs"}
    assert inboxes_b.agreements.get_nowait() == {"terms": {"board_size": 7}}


def test_exchange_agreement_raises_if_no_reply():
    transport_a, _, _ = _pair(connect_timeout=0.01)
    with pytest.raises(SimulationError, match="never sent"):
        transport_a.exchange_agreement({"terms": {}})


def test_exchange_audit_sends_and_reads_own_inbox():
    transport_a, inboxes_a, inboxes_b = _pair()
    inboxes_a.audits.put({"their": "audit"})
    result = transport_a.exchange_audit({"my": "audit"})
    assert result == {"their": "audit"}
    assert inboxes_b.audits.get_nowait() == {"my": "audit"}


def test_poll_turn_timeout_then_value():
    transport_a, inboxes_a, _ = _pair()
    assert transport_a.poll_turn(0.01) is None
    inboxes_a.turns.put({"step": 1})
    assert transport_a.poll_turn(0.01) == {"step": 1}


def test_poll_control_empty_then_value():
    transport_a, inboxes_a, _ = _pair()
    assert transport_a.poll_control() is None
    inboxes_a.controls.put({"kind": "quit"})
    assert transport_a.poll_control() == {"kind": "quit"}


def test_drain_clears_turns_controls_audits_keeps_agreements():
    inboxes = PeerInboxes()
    inboxes.turns.put("t")
    inboxes.controls.put("c")
    inboxes.audits.put("a")
    inboxes.agreements.put("keep")
    McpTransport("http://opponent/mcp", inboxes).drain_inboxes()
    assert inboxes.turns.empty()
    assert inboxes.controls.empty()
    assert inboxes.audits.empty()
    assert not inboxes.agreements.empty()  # kept for the fresh handshake


def test_send_turn_raises_when_opponent_unreachable():
    transport = McpTransport("http://127.0.0.1:1/mcp", PeerInboxes(), connect_timeout=0.0)
    with pytest.raises(SimulationError, match="unreachable"):
        transport.send_turn({"step": 1})
