"""Each peer's OWN FastMCP server — there is no central server, ever.

The server is this agent's public mailbox: the opponent (the only other party on
the "internet") pushes negotiation, turn, audit, and control messages into
thread-safe inboxes that the local runtime drains. Handlers only enqueue — they
never touch domain state (the orchestrator validates and applies).
"""

import queue
import socket
import threading

from fastmcp import FastMCP

from cop_thief_core.exceptions import SimulationError


def _ensure_port_free(host: str, port: int) -> None:
    """Fail fast with a helpful message if my MCP port is already taken."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        probe.bind((host, port))
    except OSError as exc:
        raise SimulationError(
            f"Port {port} on {host} is already in use — a previous peer is probably "
            f"still running. Stop it (e.g. `Get-NetTCPConnection -LocalPort {port}` on "
            f"Windows, or `lsof -i :{port}` on Linux) or change network.my_port in this "
            f"peer's config/<role>/game.toml."
        ) from exc
    finally:
        probe.close()


class PeerInboxes:
    """Thread-safe mailboxes filled by MCP tools, drained by the runtime."""

    def __init__(self) -> None:
        self.agreements: queue.Queue = queue.Queue()
        self.turns: queue.Queue = queue.Queue()
        self.audits: queue.Queue = queue.Queue()
        self.controls: queue.Queue = queue.Queue()


def build_peer_server(role: str, inboxes: PeerInboxes) -> FastMCP:
    """A FastMCP app exposing this peer's four receive tools."""
    mcp = FastMCP(name=f"cop-thief-{role}")

    @mcp.tool
    def negotiate(message: dict) -> dict:
        """Receive the opponent's signed game agreement."""
        inboxes.agreements.put(message)
        return {"ok": True}

    @mcp.tool
    def receive_turn(message: dict) -> dict:
        """Receive the opponent's turn message (passes the turn token to me)."""
        inboxes.turns.put(message)
        return {"ok": True}

    @mcp.tool
    def submit_audit(payload: dict) -> dict:
        """Receive the opponent's end-of-game audit reveal (records + nonces)."""
        inboxes.audits.put(payload)
        return {"ok": True}

    @mcp.tool
    def receive_control(message: dict) -> dict:
        """Receive an opponent control signal (enable / status / restart / quit)."""
        inboxes.controls.put(message)
        return {"ok": True}

    return mcp


def start_peer_server(role: str, host: str, port: int) -> PeerInboxes:  # pragma: no cover
    """Start this peer's MCP server on its own port in a background thread.

    Network I/O boundary — excluded from unit coverage; exercised by the live
    two-server integration run.
    """
    _ensure_port_free(host, port)
    inboxes = PeerInboxes()
    server = build_peer_server(role, inboxes)
    thread = threading.Thread(
        target=lambda: server.run(
            transport="http", host=host, port=port, show_banner=False, log_level="warning"
        ),
        daemon=True,
        name=f"mcp-{role}",
    )
    thread.start()
    return inboxes
