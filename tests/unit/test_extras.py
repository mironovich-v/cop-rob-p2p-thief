"""Negotiate-extras truth tables (league SPEC §7.2/§7.3, TODO 8.5).

Refusal fires ONLY on a both-declared contradiction; omission or an
uncomparable value is silence and always plays — a guard that fail-fasts on
silence forfeits the game to itself against a peer that declares nothing.
"""

import pytest

from cop_thief_core.exceptions import AgreementError
from cop_thief_core.interop.extras import build_extras, check_extras
from cop_thief_core.interop.locked_models import model_hashes


def _mine(**overrides):
    extras = build_extras(
        role="police", sub_game_number=2, game_uid="uid-aaaa",
        hashes=model_hashes(),
    )
    extras.update(overrides)
    return extras


def test_build_extras_drops_unset_fields():
    assert build_extras() == {}
    assert build_extras(role="thief") == {"role": "thief"}


def test_complementary_roles_play():
    check_extras(_mine(), {"role": "thief", "sub_game_number": 2})


def test_role_collision_refuses():
    with pytest.raises(AgreementError, match="[Rr]ole"):
        check_extras(_mine(), {"role": "police"})


def test_sub_game_mismatch_refuses():
    with pytest.raises(AgreementError, match="[Ss]ub.game"):
        check_extras(_mine(), {"sub_game_number": 3})


def test_string_sub_game_number_is_silence():
    check_extras(_mine(), {"sub_game_number": "2", "role": "thief"})
    check_extras(_mine(), {"sub_game_number": "3"})  # cosmetic type ≠ mismatch


def test_bool_sub_game_number_is_silence():
    check_extras(_mine(), {"sub_game_number": True})


def test_game_uid_mismatch_refuses():
    with pytest.raises(AgreementError, match="game_uid"):
        check_extras(_mine(), {"game_uid": "uid-bbbb"})


def test_game_uid_match_or_omission_plays():
    check_extras(_mine(), {"game_uid": "uid-aaaa"})
    check_extras(_mine(), {})  # omission never refuses
    check_extras(_mine(), {"game_uid": 12345})  # uncomparable → silence


def test_model_hash_mismatch_refuses_and_names_the_construction():
    theirs = {"scent_model_sha256": "f" * 64}
    with pytest.raises(AgreementError, match="scent_model_sha256"):
        check_extras(_mine(), theirs)


def test_model_hash_match_and_undeclared_families_play():
    check_extras(_mine(), {"scent_model_sha256": model_hashes()["scent_model_sha256"]})
    check_extras({}, _mine())  # we declare nothing → play regardless
    check_extras(_mine(), {"smell_binding_sha256": "a" * 64})  # family only they declare


def test_published_registry_hashes_reproduced():
    hashes = model_hashes()
    assert hashes == {
        "scent_model_sha256":
            "81ebee59640e80eae8ca9ee5f86abd26e7edf5cdbb27d15925cb6ee45ca6ddf4",
        "wire_shape_sha256":
            "229ae6487a418c3fcb6da9be404de2f2533c288ebc228811bff6dedc4164d6f7",
        "info_mode_sha256":
            "020947daeeb3f73494af9b04201326791742c7184085456e3517d21981ee1202",
    }
