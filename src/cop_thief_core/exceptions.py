"""Project exception hierarchy.

A single base (``SimulationError``) so callers can catch everything the system
raises; specific subclasses give structured, non-ambiguous failure reasons.
"""


class SimulationError(Exception):
    """Base class for all cop-thief errors."""


class ConfigError(SimulationError):
    """Missing or invalid configuration."""


class ConfigVersionError(ConfigError):
    """A config file declares an unsupported version."""
