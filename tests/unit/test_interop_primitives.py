"""Unit tests for interop primitives (PRD_interop_serialization, TODO slice 2.3a)."""

import pytest

from cop_thief_core.exceptions import CryptoError
from cop_thief_core.interop import (
    canonical_json,
    commit_of,
    derive_game_ids,
    new_nonce,
    verify,
)


def test_canonical_sorts_keys_and_is_compact():
    assert canonical_json({"b": 1, "a": {"d": 4, "c": 3}}) == '{"a":{"c":3,"d":4},"b":1}'


def test_canonical_keeps_native_utf8():
    assert canonical_json({"hint": "אני"}) == '{"hint":"אני"}'
    assert "\\u" not in canonical_json({"e": "🙂"})


def test_canonical_float_shortest_repr():
    assert canonical_json({"x": 0.1, "y": 6.0}) == '{"x":0.1,"y":6.0}'


def test_commit_of_deterministic_and_nonce_sensitive():
    first = commit_of({"move": "N"}, "abc")
    assert first == commit_of({"move": "N"}, "abc")
    assert len(first) == 64
    assert first != commit_of({"move": "N"}, "abd")


def test_verify_ok_and_mismatch_raises():
    payload, nonce = {"x": 1}, "n0nce"
    verify(payload, nonce, commit_of(payload, nonce))  # no raise
    with pytest.raises(CryptoError):
        verify(payload, nonce, "0" * 64)


def test_new_nonce_is_32_hex():
    nonce = new_nonce()
    assert len(nonce) == 32
    int(nonce, 16)  # parses as hex


def test_game_ids_order_independent():
    terms = {"board_size": 7}
    swapped = derive_game_ids(terms, "beta", "alpha")
    assert swapped == derive_game_ids(terms, "alpha", "beta")
    assert swapped[0] == "alpha-vs-beta"
    assert len(swapped[1]) == 36  # UUID string
