"""Peer-to-peer wire messages exchanged over the four MCP tools.

Each message is a dataclass with symmetric ``to_dict``/``from_dict``. Parsing is
defensive: a missing REQUIRED field raises ``TypeError`` (malformed → rejected),
while unknown extra fields are ignored so a peer from another team can carry a
richer private payload without breaking us. True position/move/verdict never
travel in the clear — they are sealed inside ``commit`` until the end-of-game
audit. The turn token travels WITH a TurnMessage: receiving one makes it my turn.
"""

from dataclasses import MISSING, asdict, dataclass, fields
from typing import Any


class _Wire:
    """Mixin giving dataclass messages defensive dict (de)serialization."""

    def to_dict(self) -> dict:
        return asdict(self)  # type: ignore[call-overload]

    @classmethod
    def from_dict(cls, data: dict) -> Any:
        names = {f.name for f in fields(cls)}
        required = {f.name for f in fields(cls) if f.default is MISSING}
        missing = required - data.keys()
        if missing:
            raise TypeError(f"{cls.__name__} missing fields: {sorted(missing)}")
        return cls(**{key: value for key, value in data.items() if key in names})


@dataclass
class TurnMessage(_Wire):
    """Everything one peer tells the other about its turn — and nothing more."""

    step: int
    sender: str  # "thief" | "police"
    hint: str  # free NL message with a location cue (may lie)
    smell_grid: dict  # {"r,c": intensity} decaying scent trail (no position)
    commit: str  # SHA256(canonical(payload)|nonce), nonce withheld until audit
    timestamp: str  # real-time ISO-8601 (mandatory per move)
    barrier_placed: list | None = None  # public declaration: impassable for both
    capture_claim: list | None = None  # police only: "I claim you are at [r,c]"
    claim_response: dict | None = None  # thief's honest {"claim":[r,c],"caught":bool}
    win_claim: dict | None = None  # thief's {"type":"survival"}


@dataclass
class ControlMessage(_Wire):
    """Out-of-band signal on the opt-in bidirectional control channel.

    NOT part of the sealed game record; carries live status + enable/restart/quit
    intents so peers can coordinate a whole-series restart or a clean quit.
    """

    kind: str  # "enable" | "status" | "restart" | "quit"
    sender: str  # "thief" | "police"
    sub_game_number: int = 1
    status: str = ""  # WAITING/THINKING/PLAYING/PAUSED/STOPPED/GAME_OVER/QUIT
    step_budget: float = 0.0  # live per-step time budget (seconds)
    payload: dict | None = None


@dataclass
class AuditPayload(_Wire):
    """End-of-game reveal: full sealed records so the opponent can re-verify."""

    sender: str
    records: list  # [{"payload": {...}, "nonce": str, "commit": str}]
    result_claim: str  # "capture" | "survival" | "timeout" | ...


_HEX = set("0123456789abcdef")


def validate_turn_values(message: TurnMessage) -> TurnMessage:
    """Value-level refusals for an inbound TurnMessage (kit turn_message.json).

    An inbound turn is adversarial input: every rule here is decided BEFORE any
    state change. A missing/invalid value is refused, never defaulted — a
    defaulted commit is a move the sender never sealed.
    """
    if not isinstance(message.step, int) or isinstance(message.step, bool) or message.step < 1:
        raise ValueError(f"step must be a positive int, got {message.step!r}")
    if message.sender not in ("police", "thief"):
        raise ValueError(f"sender must be police|thief, got {message.sender!r}")
    commit = message.commit
    if not (isinstance(commit, str) and len(commit) == 64 and set(commit) <= _HEX):
        raise ValueError("commit must be 64-char lowercase hex (string-compared)")
    if not (isinstance(message.timestamp, str) and message.timestamp.strip()):
        raise ValueError("timestamp must be a non-empty ISO-8601 string")
    grid = message.smell_grid
    if not isinstance(grid, dict) or any(
        isinstance(value, bool) or not isinstance(value, int | float)
        for value in grid.values()
    ):
        raise ValueError("smell_grid intensities must be numeric, not strings")
    return message
