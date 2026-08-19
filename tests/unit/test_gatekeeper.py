"""Tests for ApiGatekeeper (PRD_gatekeeper_rate_limit, slice 2.2)."""

import pytest

from cop_thief_core.exceptions import ProviderError
from cop_thief_core.shared.gatekeeper import ApiGatekeeper


class FakeConfig:
    """Minimal ConfigManager stand-in for gatekeeper tests."""

    def __init__(self, limits, queue):
        self._limits = limits
        self._queue = queue

    def service_limits(self, service):
        return self._limits

    @property
    def rate_limits(self):
        return {"queue": self._queue}


def _gatekeeper(max_retries=3):
    config = FakeConfig(
        {"requests_per_minute": 1000, "max_retries": max_retries, "retry_after_seconds": 0},
        {"max_depth": 100, "drain_interval_seconds": 0.1, "timeout_seconds": 300},
    )
    return ApiGatekeeper(config, "claude")


def test_execute_returns_result_and_counts_call():
    gate = _gatekeeper()
    assert gate.execute(lambda value: value + 1, 41) == 42
    assert gate.get_queue_status()["calls_total"] == 1


def test_execute_retries_transient_then_succeeds():
    gate = _gatekeeper(max_retries=3)
    attempts = {"n": 0}

    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise ProviderError("transient")
        return "ok"

    assert gate.execute(flaky) == "ok"
    status = gate.get_queue_status()
    assert status["calls_total"] == 3
    assert status["failures_total"] == 2


def test_execute_reraises_after_max_retries():
    gate = _gatekeeper(max_retries=2)

    def always_fail():
        raise ProviderError("down")

    with pytest.raises(ProviderError, match="down"):
        gate.execute(always_fail)
    assert gate.get_queue_status()["failures_total"] == 2


def test_non_provider_error_propagates_without_retry():
    gate = _gatekeeper(max_retries=3)

    def boom():
        raise ValueError("not a provider error")

    with pytest.raises(ValueError):
        gate.execute(boom)
    # Only one attempt was made; the non-provider error was not retried/swallowed.
    assert gate.get_queue_status()["calls_total"] == 1
