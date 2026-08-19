"""Shared pytest fixtures: an in-process FakeTransport (queue-pair "network"
between two peers — no server, no port) and the shipped per-role configs."""

import queue
from pathlib import Path

import pytest

from cop_thief_core.shared.config import ConfigManager

REPO_ROOT = Path(__file__).resolve().parent.parent


class FakeTransport:
    """One side of a queue-pair network. Mirrors the McpTransport interface."""

    def __init__(self, inbox: queue.Queue, outbox: queue.Queue):
        self._inbox = inbox
        self._outbox = outbox

    def exchange_agreement(self, signed: dict) -> dict:
        self._outbox.put(("agreement", signed))
        kind, payload = self._inbox.get(timeout=5)
        assert kind == "agreement"
        return payload

    def send_turn(self, message: dict) -> None:
        self._outbox.put(("turn", message))

    def poll_turn(self, timeout: float) -> dict | None:
        try:
            kind, payload = self._inbox.get(timeout=timeout)
        except queue.Empty:
            return None
        return payload if kind == "turn" else None

    def send_control(self, message: dict) -> None:
        pass  # control channel is opt-in; unused in tests

    def poll_control(self) -> dict | None:
        return None

    def drain_inboxes(self) -> None:
        pass

    def exchange_audit(self, payload: dict) -> dict | None:
        self._outbox.put(("audit", payload))
        try:
            kind, data = self._inbox.get(timeout=5)
        except queue.Empty:
            return None
        return data if kind == "audit" else None


def make_transport_pair() -> tuple[FakeTransport, FakeTransport]:
    a_to_b: queue.Queue = queue.Queue()
    b_to_a: queue.Queue = queue.Queue()
    return FakeTransport(b_to_a, a_to_b), FakeTransport(a_to_b, b_to_a)


@pytest.fixture
def transport_pair():
    return make_transport_pair()


@pytest.fixture
def police_config():
    return ConfigManager(REPO_ROOT / "config" / "police")


@pytest.fixture
def thief_config():
    return ConfigManager(REPO_ROOT / "config" / "thief")
