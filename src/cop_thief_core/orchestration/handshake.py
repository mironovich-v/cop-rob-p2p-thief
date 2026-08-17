"""Pre-game handshake: exchange signed terms + identity over the transport, verify
the opponent, refuse on any mismatch or below-App-F-minimum, and derive the shared
game ids. Both peers compute identical ids from the shared inputs (no round-trip).

Beside the terms we declare the PROMOTED/PROPOSED extras (SPEC §7.2/§7.3):
role, sub_game_number, the derived game_uid (only when the opponent group is
configured — the uid needs both group ids), and the locked-model hashes. A
both-declared contradiction refuses at the handshake; omission never refuses.
"""

from cop_thief_core.exceptions import AgreementError
from cop_thief_core.interop.extras import build_extras
from cop_thief_core.interop.game_ids import derive_game_ids
from cop_thief_core.interop.locked_models import model_hashes
from cop_thief_core.interop.negotiation import (
    Negotiation,
    terms_from_config,
    validate_minimums,
)


def run_handshake(
    transport, config, own_identity: dict, role: str | None = None,
    sub_game_number: int | None = None,
) -> tuple[dict, str, str]:
    """Return (peer_identity, game_id, game_uid). Raises AgreementError/CryptoError
    on a terms mismatch, a bad signature, a below-App-F-minimum term, a declared
    extras contradiction, or an unexpected opponent group."""
    terms = terms_from_config(config)
    validate_minimums(terms)  # refuse a below-floor agreement before play begins
    own_gid = own_identity.get("group_id", "unknown-group")
    expected = config.get("game.opponent_group_id", None)
    declared_uid = derive_game_ids(terms, own_gid, expected)[1] if expected else None
    extras = build_extras(role, sub_game_number, declared_uid, model_hashes())
    negotiation = Negotiation(terms, identity=own_identity, extras=extras)
    peer_message = transport.exchange_agreement(negotiation.signed())
    negotiation.verify_peer(peer_message)
    peer_identity = negotiation.peer_identity
    peer_gid = peer_identity.get("group_id", "unknown-group")
    if expected and peer_gid != expected:
        # A stray peer from another pairing answered the greeting (kit WARNINGS).
        raise AgreementError(
            f"Unexpected opponent group '{peer_gid}' — this peer is configured "
            f"to play '{expected}'"
        )
    game_id, game_uid = derive_game_ids(terms, own_gid, peer_gid)
    return peer_identity, game_id, game_uid
