"""Tests for the pre-match connectivity probe (PRD_cloud_tunnel, TODO slice 5.1)."""

from cop_thief_core.infra.connectivity import probe_opponent
from cop_thief_core.infra.mcp_server import PeerInboxes, build_peer_server


def test_probe_reaches_in_memory_server():
    server = build_peer_server("police", PeerInboxes())
    assert probe_opponent(server) is True  # lists the 4 tools in-memory


def test_probe_fails_for_unreachable_url():
    assert probe_opponent("http://127.0.0.1:1/mcp", timeout=0.5) is False
