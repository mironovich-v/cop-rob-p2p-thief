"""SDK: the single business entry point and the series runner."""

from cop_thief_core.sdk.sdk import SimulationSdk, StubLlm
from cop_thief_core.sdk.series import SeriesResult, role_for, run_series

__all__ = ["SeriesResult", "SimulationSdk", "StubLlm", "role_for", "run_series"]
