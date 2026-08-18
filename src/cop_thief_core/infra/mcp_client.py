"""McpTransport: the peer-to-peer "network" — my inboxes + the opponent's server.

Outbound tool calls go to the OPPONENT's FastMCP server; inbound messages arrive
in MY server's inboxes. The opponent handle may be a URL (real HTTP) or a FastMCP
object (in-memory, for tests) — `fastmcp.Client` accepts both. This class mirrors
the transport protocol used by the runtime so a test FakeTransport can stand in.
"""

import asyncio
import contextlib
import queue
import time

from fastmcp import Client

from cop_thief_core.exceptions import SimulationError
from cop_thief_core.infra.mcp_server import PeerInboxes


class McpTransport:
    """One peer's view of the wire: push to the opponent, pull from own inboxes."""

    def __init__(
        self,
        opponent,
        inboxes: PeerInboxes,
        connect_timeout: float = 60.0,
        retry_interval: float = 1.0,
        audit_send_timeout: float = 10.0,
        control_send_timeout: float = 2.0,
        call_timeout: float = 10.0,
        handshake_repush: float = 5.0,
    ) -> None:
        self._opponent = opponent  # URL string (real) or FastMCP object (in-memory)
        self._inboxes = inboxes
        self._connect_timeout = connect_timeout
        self._retry = retry_interval
        self._audit_timeout = audit_send_timeout
        self._control_timeout = control_send_timeout
        self._call_timeout = call_timeout  # per-call cap, strictly < signed deadline
        self._repush = handshake_repush

    def set_opponent(self, opponent) -> None:
        """Swap the dial target (role-split opponents run two fixed-role
        processes, so the dialed URL changes every sub-game). Safe mid-series:
        every call opens a fresh Client, so no session survives the swap."""
        self._opponent = opponent

    def _call(self, tool: str, argument: dict):
        # A fresh Client per call: no outbound session survives a sub-game
        # boundary, so a restarted opponent process is never dialed on a dead
        # socket (imreeyal §3.4). The per-call timeout keeps one delivered-but-
        # unanswered push from silently breaching the signed 30s deadline
        # (imreeyal §3.5): timeout budget stays with the deadline, not the call.
        key = "payload" if tool == "submit_audit" else "message"

        async def invoke():
            async with Client(self._opponent, timeout=self._call_timeout) as client:
                result = await client.call_tool(tool, {key: argument})
                return getattr(result, "data", None)

        return asyncio.run(invoke())

    def _call_with_retry(self, tool: str, argument: dict, timeout: float | None = None):
        """Retry until the opponent's server is up (peers may start seconds apart)."""
        deadline = time.time() + (timeout if timeout is not None else self._connect_timeout)
        while True:
            try:
                return self._call(tool, argument)
            except Exception as exc:
                if time.time() >= deadline:
                    raise SimulationError(f"Opponent MCP server unreachable: {exc}") from exc
                time.sleep(self._retry)

    def exchange_agreement(self, signed: dict) -> dict:
        # WARNINGS §2b: push first, then accept the agreement from EITHER place —
        # a request/response peer answers in the body, a push peer dials back.
        # The greeting is RE-pushed periodically (a push that landed in the
        # opponent's dying previous process must not strand the window), and the
        # overall patience spans their legitimate inter-sub-game door gap, during
        # which their ARRIVING negotiate opens the sub-game (imreeyal §3.4/§3.16).
        deadline = time.time() + self._connect_timeout
        while True:
            window = min(self._repush, max(deadline - time.time(), 0.1))
            with contextlib.suppress(SimulationError):
                response = self._call_with_retry("negotiate", signed, timeout=window)
                if isinstance(response, dict) and "terms" in response:
                    return response
            wait = min(self._repush, max(deadline - time.time(), 0.05))
            try:
                return self._inboxes.agreements.get(timeout=wait)
            except queue.Empty as exc:
                if time.time() >= deadline:
                    raise SimulationError(
                        "Opponent never sent its agreement (and answered no push)"
                    ) from exc

    def send_turn(self, message: dict) -> None:
        self._call_with_retry("receive_turn", message)

    def poll_turn(self, timeout: float) -> dict | None:
        try:
            return self._inboxes.turns.get(timeout=timeout)
        except queue.Empty:
            return None

    def send_control(self, message: dict) -> None:
        """Best-effort: short timeout + suppressed error so a slow/departed opponent
        never stalls the loop (control messages are advisory)."""
        with contextlib.suppress(SimulationError):
            self._call_with_retry("receive_control", message, timeout=self._control_timeout)

    def poll_control(self) -> dict | None:
        try:
            return self._inboxes.controls.get_nowait()
        except queue.Empty:
            return None

    def drain_inboxes(self) -> None:
        """Discard stale turns/controls/audits before a restarted series (agreements
        are already empty post-handshake, so they are left untouched)."""
        for inbox in (self._inboxes.turns, self._inboxes.controls, self._inboxes.audits):
            with contextlib.suppress(queue.Empty):
                while True:
                    inbox.get_nowait()

    def exchange_audit(self, payload: dict) -> dict | None:
        """Best-effort send (the winner may exit right after reading its inbox);
        then always check whether THEIR audit already sits in my inbox."""
        with contextlib.suppress(SimulationError):
            self._call_with_retry("submit_audit", payload, timeout=self._audit_timeout)
        try:
            return self._inboxes.audits.get(timeout=self._connect_timeout)
        except queue.Empty:
            return None
