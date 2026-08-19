"""Negotiate extras: pairing + uid + locked-model declarations (SPEC §7.2/§7.3/§7).

``role`` and ``sub_game_number`` ride BESIDE the signed terms, never inside them
(the terms are a flat signed set — adding a key breaks the signature). The rule
everywhere: refuse ONLY when both peers declare a field and contradict each
other; omission or an uncomparable value is silence and plays on. Refusals name
what was expected (SPEC §4) instead of only refusing.
"""

from cop_thief_core.exceptions import AgreementError, PairingMismatchError

_HASH_KEYS = (
    "game_uid",
    "scent_model_sha256",
    "wire_shape_sha256",
    "info_mode_sha256",
    "smell_binding_sha256",
)


def build_extras(role=None, sub_game_number=None, game_uid=None, hashes=None) -> dict:
    """My declarations for this handshake — unset fields are omitted, not nulled."""
    extras = dict(hashes or {})
    if role is not None:
        extras["role"] = role
    if sub_game_number is not None:
        extras["sub_game_number"] = sub_game_number
    if game_uid is not None:
        extras["game_uid"] = game_uid
    return extras


def _comparable_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def check_extras(mine: dict, theirs: dict) -> None:
    """Raise AgreementError on a both-declared contradiction; silence plays."""
    my_role, their_role = mine.get("role"), theirs.get("role")
    if my_role in ("police", "thief") and their_role == my_role:
        raise PairingMismatchError(
            f"Role collision: both peers declare '{my_role}' — roles must be complementary"
        )
    my_sub, their_sub = mine.get("sub_game_number"), theirs.get("sub_game_number")
    if _comparable_int(my_sub) and _comparable_int(their_sub) and my_sub != their_sub:
        raise PairingMismatchError(
            f"Sub-game mismatch: we declare {my_sub}, opponent declares {their_sub}"
        )
    for key in _HASH_KEYS:
        ours, other = mine.get(key), theirs.get(key)
        if isinstance(ours, str) and isinstance(other, str) and ours != other:
            raise AgreementError(
                f"{key} mismatch: ours {ours}, theirs {other} — both sides must "
                f"declare SHA256(canonical_json(<registered doc>)) of the same doc"
                if key != "game_uid"
                else f"game_uid mismatch: ours {ours}, theirs {other} — derive from "
                f"the FLAT negotiated terms, never the whole config (SPEC §7.3)"
            )
