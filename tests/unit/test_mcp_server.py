"""Tests for the FastMCP peer server (PRD_mcp_protocol, TODO slice 2.4).

Uses fastmcp's in-memory Client(server) — no network, no port bound.
"""

import asyncio
import socket

import pytest
from fastmcp import Client

from cop_thief_core.exceptions import SimulationError
from cop_thief_core.infra.mcp_server import PeerInboxes, _ensure_port_free, build_peer_server


def test_free_port_passes():
    _ensure_port_free("127.0.0.1", 0)  # ephemeral port is always free


def test_taken_port_raises_with_instructions():
    holder = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    holder.bind(("127.0.0.1", 0))
    holder.listen(1)
    port = holder.getsockname()[1]
    try:
        with pytest.raises(SimulationError) as excinfo:
            _ensure_port_free("127.0.0.1", port)
        message = str(excinfo.value)
        assert str(port) in message
        assert "network.my_port" in message
    finally:
        holder.close()


def _call(server, tool, argument):
    async def go():
        async with Client(server) as client:
            return await client.call_tool(tool, argument)

    return asyncio.run(go())


def test_tools_enqueue_to_inboxes():
    inboxes = PeerInboxes()
    server = build_peer_server("police", inboxes)
    _call(server, "negotiate", {"message": {"a": 1}})
    _call(server, "receive_turn", {"message": {"step": 1}})
    _call(server, "submit_audit", {"payload": {"records": []}})
    _call(server, "receive_control", {"message": {"kind": "enable"}})
    assert inboxes.agreements.get_nowait() == {"a": 1}
    assert inboxes.turns.get_nowait() == {"step": 1}
    assert inboxes.audits.get_nowait() == {"records": []}
    assert inboxes.controls.get_nowait() == {"kind": "enable"}
