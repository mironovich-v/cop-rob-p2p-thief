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


class ProviderError(SimulationError):
    """A transient/permanent failure from an external provider (LLM, email, net)."""


class RateLimitError(SimulationError):
    """The rate-limit queue is full or a caller timed out waiting for a slot."""


class CryptoError(SimulationError):
    """A commit or signature failed to verify (hash mismatch)."""


class AgreementError(SimulationError):
    """The pre-game agreement is invalid: mismatched, incomplete, or below an
    Appendix-F minimum — the peer must refuse to start."""


class PairingMismatchError(AgreementError):
    """A greeting for a DIFFERENT window (role/sub-game contradiction): with a
    role-split opponent both fixed-role processes greet one mailbox, so this is
    expected traffic to skip, not a window-fatal fault. Signature/terms/uid/
    group failures stay plain AgreementError (fatal)."""
