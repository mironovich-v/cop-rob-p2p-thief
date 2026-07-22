"""Deterministic shared identifiers both peers reproduce with no round-trip.

    game_id  = "<sorted_gid_a>-vs-<sorted_gid_b>"   (human-readable, order-stable)
    game_uid = UUID( SHA256( canonical(terms) + "|" + "|".join(sorted(gids)) )[:16] )

Because the derivation is a pure function of shared inputs (with group ids sorted
first), the two peers always compute identical values (league SPEC §4).
"""

import hashlib
import uuid

from cop_thief_core.interop.canonical import canonical_json


def derive_game_ids(terms: dict, group_a: str, group_b: str) -> tuple[str, str]:
    pair = sorted([group_a, group_b])
    game_id = f"{pair[0]}-vs-{pair[1]}"
    seed = f"{canonical_json(terms)}|{'|'.join(pair)}"
    game_uid = str(uuid.UUID(bytes=hashlib.sha256(seed.encode()).digest()[:16]))
    return game_id, game_uid
