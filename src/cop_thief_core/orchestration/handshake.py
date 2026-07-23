"""Pre-game handshake: exchange signed terms + identity over the transport, verify
the opponent, refuse on any mismatch or below-App-F-minimum, and derive the shared
game ids. Both peers compute identical ids from the shared inputs (no round-trip).
"""

from cop_thief_core.interop.game_ids import derive_game_ids
from cop_thief_core.interop.negotiation import (
    Negotiation,
    terms_from_config,
    validate_minimums,
)


def run_handshake(transport, config, own_identity: dict) -> tuple[dict, str, str]:
    """Return (peer_identity, game_id, game_uid). Raises AgreementError/CryptoError
    on a terms mismatch, a bad signature, or a below-App-F-minimum term."""
    terms = terms_from_config(config)
    validate_minimums(terms)  # refuse a below-floor agreement before play begins
    negotiation = Negotiation(terms, identity=own_identity)
    peer_message = transport.exchange_agreement(negotiation.signed())
    negotiation.verify_peer(peer_message)
    peer_identity = negotiation.peer_identity
    game_id, game_uid = derive_game_ids(
        terms,
        own_identity.get("group_id", "unknown-group"),
        peer_identity.get("group_id", "unknown-group"),
    )
    return peer_identity, game_id, game_uid
