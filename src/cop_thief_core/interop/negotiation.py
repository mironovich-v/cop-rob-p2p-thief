"""Pre-game agreement (league SPEC §4): extract the signed terms, sign them,
verify the opponent, and refuse to start on any mismatch or below-floor value.

Identity (group id, members, repos) is exchanged but NOT signed — the *terms* are
what both peers verify. App-F floors are loaded from ``limits.json`` (data, not
hard-coded literals) so a minimum can be raised by agreement but never lowered.
"""

import json
from pathlib import Path

from cop_thief_core.exceptions import AgreementError
from cop_thief_core.interop.hashing import commit_of, new_nonce, verify

_LIMITS_PATH = Path(__file__).resolve().parent / "limits.json"


def terms_from_config(cfg) -> dict:
    """The signed-terms subset — everything both peers MUST match on."""
    terms = {
        "board_size": cfg.get("board.size"),
        "smell_grid_size": cfg.get("smell.grid_size"),
        "decay_per_step": cfg.get("smell.decay_per_step"),
        "emit_intensity": cfg.get("smell.emit_intensity"),
        "min_center_intensity": cfg.get("smell.min_center_intensity"),
        "max_steps": cfg.get("rules.max_steps"),
        "barriers_max": cfg.get("rules.barriers_max"),
        "setting": cfg.get("play.setting"),
        "hint_max_words": cfg.get("play.hint_max_words"),
        "axis_origin_corner": cfg.get("board.axis_origin_corner"),
        "axis_start_index": cfg.get("board.axis_start_index"),
        "thief_start": cfg.get("positions.thief_start"),
        "cop_start": cfg.get("positions.cop_start"),
        "num_games": cfg.get("game.num_games"),
    }
    missing = sorted(key for key, value in terms.items() if value is None)
    if missing:
        raise AgreementError(f"Missing required agreed term(s): {missing}")
    return terms


def load_app_f_limits() -> dict:
    return json.loads(_LIMITS_PATH.read_text(encoding="utf-8"))


def validate_minimums(terms: dict, limits: dict | None = None) -> None:
    """Refuse the agreement if a term is below an App-F minimum or off a fixed value."""
    limits = limits or load_app_f_limits()
    for key, floor in limits["minimums"].items():
        if terms[key] < floor:
            raise AgreementError(f"Term {key}={terms[key]} below App-F minimum {floor}")
    for key, fixed in limits["fixed"].items():
        if terms[key] != fixed:
            raise AgreementError(f"Term {key}={terms[key]} must equal fixed App-F value {fixed}")


class Negotiation:
    """One peer's side of the agreement handshake (sign + verify the terms)."""

    def __init__(self, terms: dict, identity: dict | None = None) -> None:
        self.terms = terms
        self.identity = identity or {}
        self._nonce = new_nonce()
        self.peer_identity: dict = {}

    def signed(self) -> dict:
        """My agreement message: terms + nonce + signature (identity is unsigned)."""
        return {
            "terms": self.terms,
            "nonce": self._nonce,
            "signature": commit_of(self.terms, self._nonce),
            "identity": self.identity,
        }

    def verify_peer(self, message: dict) -> None:
        """Raise on any mismatch: terms must value-equal ours; signature must verify."""
        if message.get("terms") != self.terms:
            raise AgreementError("Opponent terms are not value-equal to ours")
        verify(message["terms"], message["nonce"], message["signature"])  # CryptoError on fail
        self.peer_identity = message.get("identity", {})
