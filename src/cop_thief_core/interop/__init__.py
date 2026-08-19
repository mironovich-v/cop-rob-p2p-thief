"""Byte-exact interoperability primitives (canonical JSON, hashing, game ids)
and the pre-game agreement."""

from cop_thief_core.interop.canonical import canonical_bytes, canonical_json
from cop_thief_core.interop.game_ids import derive_game_ids
from cop_thief_core.interop.hashing import audit_records, commit_of, new_nonce, seal, verify
from cop_thief_core.interop.negotiation import (
    Negotiation,
    load_app_f_limits,
    terms_from_config,
    validate_minimums,
)

__all__ = [
    "Negotiation",
    "audit_records",
    "canonical_bytes",
    "canonical_json",
    "commit_of",
    "derive_game_ids",
    "load_app_f_limits",
    "new_nonce",
    "seal",
    "terms_from_config",
    "validate_minimums",
    "verify",
]
