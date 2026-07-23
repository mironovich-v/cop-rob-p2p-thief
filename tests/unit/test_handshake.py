"""Tests for the pre-game handshake (PRD_pregame_agreement, TODO slice 2.5a)."""

import threading

import pytest

from cop_thief_core.exceptions import AgreementError
from cop_thief_core.interop.negotiation import Negotiation
from cop_thief_core.orchestration.handshake import run_handshake
from cop_thief_core.orchestration.sealing import identity_from_config


def test_handshake_derives_shared_ids(transport_pair, police_config, thief_config):
    police_t, thief_t = transport_pair
    results: dict = {}

    def run(name, transport, cfg):
        results[name] = run_handshake(transport, cfg, identity_from_config(cfg))

    threads = [
        threading.Thread(target=run, args=("police", police_t, police_config)),
        threading.Thread(target=run, args=("thief", thief_t, thief_config)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
        assert not thread.is_alive()

    police_identity, police_game_id, police_uid = results["police"]
    thief_identity, thief_game_id, thief_uid = results["thief"]
    assert police_uid == thief_uid  # both derive the same game_uid
    assert police_game_id == thief_game_id == "vm__fabi-police-vs-vm__fabi-thief"
    assert police_identity["group_id"] == "vm__fabi-thief"  # captured opponent id
    assert thief_identity["group_id"] == "vm__fabi-police"


class _StubTransport:
    def __init__(self, reply):
        self._reply = reply

    def exchange_agreement(self, signed):
        return self._reply


def test_handshake_refuses_mismatched_terms(police_config):
    opponent_reply = Negotiation({"board_size": 999}).signed()  # different terms
    with pytest.raises(AgreementError):
        run_handshake(_StubTransport(opponent_reply), police_config, {"group_id": "x"})
