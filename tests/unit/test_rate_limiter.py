"""Tests for the token-bucket RateLimiter (PRD_gatekeeper_rate_limit, slice 2.2)."""

import pytest

from cop_thief_core.exceptions import RateLimitError
from cop_thief_core.shared.rate_limiter import RateLimiter


class FakeClock:
    """Deterministic clock: sleeping just advances virtual time (instant tests)."""

    def __init__(self):
        self.now = 0.0

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def _limiter(rpm, max_depth=5, drain=1.0, timeout=120.0, clock=None):
    return RateLimiter(
        {"requests_per_minute": rpm},
        {"max_depth": max_depth, "drain_interval_seconds": drain, "timeout_seconds": timeout},
        clock=clock,
    )


def test_under_limit_grants_immediately():
    clock = FakeClock()
    limiter = _limiter(3, clock=clock)
    limiter.acquire()
    limiter.acquire()
    limiter.acquire()
    assert clock.now == 0.0  # no waiting needed
    assert limiter.queue_depth == 0


def test_queue_full_raises_immediately():
    limiter = _limiter(2, max_depth=0, clock=FakeClock())
    limiter.acquire()
    limiter.acquire()
    with pytest.raises(RateLimitError, match="queue full"):
        limiter.acquire()


def test_blocks_then_grants_when_window_slides():
    clock = FakeClock()
    limiter = _limiter(2, clock=clock)
    limiter.acquire()  # grant at t=0
    limiter.acquire()  # grant at t=0
    limiter.acquire()  # must wait until the 60s window slides past the first grants
    assert clock.now >= 60.0
    assert limiter.queue_depth == 0


def test_times_out_when_never_freed():
    limiter = _limiter(1, timeout=5.0, clock=FakeClock())
    limiter.acquire()  # single grant at t=0
    with pytest.raises(RateLimitError, match="Timed out"):
        limiter.acquire()  # window never slides within the 5s timeout
