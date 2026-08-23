"""Pre-game agreement (league SPEC §4): extract the signed terms, sign them,
verify the opponent, and refuse to start on any mismatch or below-floor value.

Identity (group id, members, repos) is exchanged but NOT signed — the *terms* are
what both peers verify. App-F floors are loaded from ``limits.json`` (data, not
hard-coded literals) so a minimum can be raised by agreement but never lowered.
"""

import json
from pathlib import Path

from cop_thief_core.exceptions import AgreementError
from cop_thief_core.interop.extras import check_extras
from cop_thief_core.interop.hashing import commit_of, new_nonce, verify

_LIMITS_PATH = Path(__file__).resolve().parent / "limits.json"


# Terms an Appendix-B shared config may legitimately omit, with the value the
# kit SPEC documents as the default. Everything else stays mandatory.
APP_B_OPTIONAL_TERMS = {"min_center_intensity": 0.5}


def terms_from_config(cfg) -> dict:
    """The signed-terms subset — everything both peers MUST match on.

    Appendix B and the signed terms are DIFFERENT SCOPES. The book defines
    exactly three ``pheromone_*`` keys (center_intensity, decay, grid_size) and
    the string ``min_center`` appears nowhere in it, so a conforming Appendix-B
    config legitimately omits ``min_center_intensity`` — and a partner's
    Appendix-B validator rejects a file that adds it (il-nv-ai, 2026-08-23,
    verified against the PDF). The term itself belongs to the reference-v3
    negotiation body, where the kit SPEC states ``default 0.5`` and the pinned
    CORE ``game_uid`` vector carries 0.5. So it is filled from that documented
    default when the shared file omits it — never invented, and never
    overriding a value a partner does supply.
    """
    terms = {
        "board_size": cfg.get("board.size"),
        "smell_grid_size": cfg.get("smell.grid_size"),
        "decay_per_step": cfg.get("smell.decay_per_step"),
        "emit_intensity": cfg.get("smell.emit_intensity"),
        "min_center_intensity": cfg.get(
            "smell.min_center_intensity", APP_B_OPTIONAL_TERMS["min_center_intensity"]),
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

    def __init__(
        self, terms: dict, identity: dict | None = None, extras: dict | None = None
    ) -> None:
        self.terms = terms
        self.identity = identity or {}
        self.extras = extras or {}  # role / sub_game_number / uid / model hashes
        self._nonce = new_nonce()
        self.peer_identity: dict = {}

    def signed(self) -> dict:
        """My agreement message: terms + nonce + signature; identity and the
        declared extras ride BESIDE the terms (unsigned — SPEC §7.2)."""
        return {
            "terms": self.terms,
            "nonce": self._nonce,
            "signature": commit_of(self.terms, self._nonce),
            "identity": self.identity,
            **self.extras,
        }

    def verify_peer(self, message: dict) -> None:
        """Raise on any mismatch: terms must value-equal ours; signature must
        verify; a both-declared extras contradiction refuses (omission never does)."""
        if message.get("terms") != self.terms:
            raise AgreementError("Opponent terms are not value-equal to ours")
        verify(message["terms"], message["nonce"], message["signature"])  # CryptoError on fail
        check_extras(self.extras, message)
        self.peer_identity = message.get("identity", {})
