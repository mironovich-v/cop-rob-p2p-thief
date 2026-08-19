"""Tests for pre-game agreement (PRD_pregame_agreement, TODO slice 2.3b)."""

from pathlib import Path

import pytest

from cop_thief_core.exceptions import AgreementError, CryptoError
from cop_thief_core.interop import (
    Negotiation,
    commit_of,
    terms_from_config,
    validate_minimums,
)
from cop_thief_core.shared.config import ConfigManager

REPO_ROOT = Path(__file__).resolve().parents[2]


def _real_terms():
    return terms_from_config(ConfigManager(REPO_ROOT / "config" / "police"))


class _FakeCfg:
    def __init__(self, values):
        self._values = values

    def get(self, key, default=None):
        return self._values.get(key, default)


def test_terms_from_config_has_14_keys():
    terms = _real_terms()
    assert len(terms) == 14
    assert terms["board_size"] == 7
    assert terms["max_steps"] == 35
    assert terms["num_games"] == 1
    assert terms["setting"] == "New York"


def test_terms_from_config_missing_raises():
    with pytest.raises(AgreementError, match="Missing required"):
        terms_from_config(_FakeCfg({}))  # every get() returns None


def test_validate_minimums_accepts_shipped_terms():
    validate_minimums(_real_terms())  # no raise


def test_validate_minimums_rejects_below_floor():
    terms = _real_terms()
    terms["board_size"] = 5
    with pytest.raises(AgreementError, match="below App-F minimum"):
        validate_minimums(terms)


def test_validate_minimums_rejects_wrong_fixed():
    terms = _real_terms()
    terms["decay_per_step"] = 0.2
    with pytest.raises(AgreementError, match="fixed App-F"):
        validate_minimums(terms)


def test_signed_message_structure():
    terms = _real_terms()
    neg = Negotiation(terms, identity={"group_id": "vm__fabi-police"})
    msg = neg.signed()
    assert msg["terms"] == terms
    assert msg["signature"] == commit_of(terms, msg["nonce"])
    assert msg["identity"]["group_id"] == "vm__fabi-police"


def test_mutual_verify_passes_and_captures_identity():
    terms = _real_terms()
    cop = Negotiation(terms, identity={"group_id": "cop"})
    thief = Negotiation(terms, identity={"group_id": "thief"})
    cop.verify_peer(thief.signed())
    thief.verify_peer(cop.signed())
    assert cop.peer_identity["group_id"] == "thief"


def test_verify_peer_rejects_mismatched_terms():
    ours = Negotiation({"board_size": 7})
    theirs = Negotiation({"board_size": 9})
    with pytest.raises(AgreementError, match="value-equal"):
        ours.verify_peer(theirs.signed())


def test_verify_peer_rejects_tampered_signature():
    terms = {"board_size": 7}
    ours = Negotiation(terms)
    peer_msg = Negotiation(terms).signed()
    peer_msg["signature"] = "0" * 64
    with pytest.raises(CryptoError):
        ours.verify_peer(peer_msg)
