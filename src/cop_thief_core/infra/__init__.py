"""Infrastructure boundaries: the FastMCP server (inbox) and client (transport)."""

from cop_thief_core.infra.connectivity import probe_opponent
from cop_thief_core.infra.mcp_client import McpTransport
from cop_thief_core.infra.mcp_server import (
    PeerInboxes,
    build_peer_server,
    start_peer_server,
)

__all__ = [
    "McpTransport",
    "PeerInboxes",
    "build_peer_server",
    "probe_opponent",
    "start_peer_server",
]
