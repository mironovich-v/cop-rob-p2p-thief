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


# --- 8.5: extras beside the terms; refusal only on both-declared contradiction ---

class _Overlay:
    """Config proxy overriding a few dotted keys (e.g. the expected opponent)."""

    def __init__(self, cfg, overrides):
        self._cfg, self._overrides = cfg, overrides

    def get(self, key, default=None):
        if key in self._overrides:
            return self._overrides[key]
        return self._cfg.get(key, default)


def _reply(cfg, extras=None, group_id="vm__fabi-thief"):
    from cop_thief_core.interop.negotiation import terms_from_config
    return Negotiation(
        terms_from_config(cfg), identity={"group_id": group_id}, extras=extras or {}
    ).signed()


def test_handshake_declares_extras_beside_terms(police_config):
    captured = {}

    class _Capture(_StubTransport):
        def exchange_agreement(self, signed):
            captured.update(signed)
            return self._reply

    reply = _reply(police_config, extras={"role": "thief", "sub_game_number": 2})
    run_handshake(_Capture(reply), police_config, {"group_id": "g"},
                  role="police", sub_game_number=2)
    assert captured["role"] == "police"
    assert captured["sub_game_number"] == 2
    assert len(captured["scent_model_sha256"]) == 64
    assert "role" not in captured["terms"]  # extras never leak into the signed set


def test_handshake_refuses_role_collision(police_config):
    reply = _reply(police_config, extras={"role": "police"})
    with pytest.raises(AgreementError, match="[Rr]ole"):
        run_handshake(_StubTransport(reply), _ZeroPatience(police_config),
                      {"group_id": "g"}, role="police", sub_game_number=1)


def test_handshake_refuses_unexpected_opponent_group(police_config):
    config = _Overlay(police_config, {"game.opponent_group_id": "imreeyal"})
    reply = _reply(police_config, group_id="stray-team")
    with pytest.raises(AgreementError, match="imreeyal"):
        run_handshake(_StubTransport(reply), config, {"group_id": "vm__fabi"})


def test_handshake_refuses_declared_uid_mismatch(police_config):
    config = _Overlay(police_config, {"game.opponent_group_id": "imreeyal"})
    reply = _reply(police_config, extras={"game_uid": "not-the-derived-uid"})
    with pytest.raises(AgreementError, match="game_uid"):
        run_handshake(_StubTransport(reply), config, {"group_id": "vm__fabi"})


def test_handshake_plays_against_a_silent_peer(police_config):
    # Omission never refuses: opponent declares no extras at all.
    reply = _reply(police_config)
    identity, game_id, _ = run_handshake(
        _StubTransport(reply), police_config, {"group_id": "vm__fabi-police"},
        role="police", sub_game_number=1)
    assert identity["group_id"] == "vm__fabi-thief"
    assert game_id == "vm__fabi-police-vs-vm__fabi-thief"


class _QueueTransport:
    """Returns queued agreements in order — a role-split opponent whose OTHER
    process's greeting lands first."""

    def __init__(self, replies):
        self._replies = list(replies)
        self.pushes = 0

    def exchange_agreement(self, signed):
        self.pushes += 1
        return self._replies.pop(0)


def test_handshake_skips_the_other_windows_greeting(police_config):
    # Their thief-process greeting (role collision for MY thief window) is
    # skipped; the matching police greeting right behind it is accepted.
    wrong = _reply(police_config, extras={"role": "thief", "sub_game_number": 2})
    right = _reply(police_config, extras={"role": "police", "sub_game_number": 1})
    transport = _QueueTransport([wrong, right])
    identity, game_id, _ = run_handshake(
        transport, police_config, {"group_id": "vm__fabi-police"},
        role="thief", sub_game_number=1)
    assert game_id == "vm__fabi-police-vs-vm__fabi-thief"
    assert transport.pushes == 2  # re-pushed while waiting for the match


class _ZeroPatience:
    """Config proxy: no skip budget, so a mismatch raises immediately."""

    def __init__(self, cfg):
        self._cfg = cfg

    def get(self, key, default=None):
        if key == "network.connect_timeout_seconds":
            return 0
        return self._cfg.get(key, default)


def test_handshake_still_fails_loudly_on_a_true_collision(police_config):
    from cop_thief_core.exceptions import PairingMismatchError
    collide = [_reply(police_config, extras={"role": "thief"}) for _ in range(3)]
    with pytest.raises(PairingMismatchError, match="[Rr]ole"):
        run_handshake(_QueueTransport(collide), _ZeroPatience(police_config),
                      {"group_id": "g"}, role="thief", sub_game_number=1)


def test_handshake_survives_a_greeting_backlog(police_config):
    # Sub-game-2 live failure: a queued backlog of the other process's stale
    # re-pushed greetings must never exhaust the window — the budget is TIME.
    backlog = [_reply(police_config, extras={"role": "police", "sub_game_number": 3})
               for _ in range(25)]
    match = _reply(police_config, extras={"role": "thief", "sub_game_number": 2})
    transport = _QueueTransport(backlog + [match])
    identity, game_id, _ = run_handshake(
        transport, police_config, {"group_id": "vm__fabi-police"},
        role="police", sub_game_number=2)
    assert game_id == "vm__fabi-police-vs-vm__fabi-thief"
    assert transport.pushes == 26  # drained the whole backlog, then matched
