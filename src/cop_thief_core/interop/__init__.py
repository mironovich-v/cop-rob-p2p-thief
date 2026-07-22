"""Byte-exact interoperability primitives (canonical JSON, hashing, game ids)."""

from cop_thief_core.interop.canonical import canonical_bytes, canonical_json
from cop_thief_core.interop.game_ids import derive_game_ids
from cop_thief_core.interop.hashing import commit_of, new_nonce, verify

__all__ = [
    "canonical_bytes",
    "canonical_json",
    "commit_of",
    "derive_game_ids",
    "new_nonce",
    "verify",
]
