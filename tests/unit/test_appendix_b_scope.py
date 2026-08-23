"""Appendix B and the signed terms are DIFFERENT SCOPES.

il-nv-ai showed this with a citation we verified against the PDF: the book
defines exactly three `pheromone_*` keys — center_intensity, decay, grid_size —
and the string `min_center` appears NOWHERE in it. So an Appendix-B config file
legitimately omits `min_center_intensity`, and a validator mirroring Appendix B
rejects a file that adds it.

The term is real, but it belongs to the reference-v3 NEGOTIATION body: the kit
SPEC gives it as `default 0.5` and the pinned CORE `game_uid` vector carries
0.5 inside the terms. Our loader conflated the two scopes by demanding all
fourteen terms from the config file.
"""

import json

from cop_thief_core.interop.negotiation import APP_B_OPTIONAL_TERMS, terms_from_config
from cop_thief_core.shared.config import ConfigManager

REPO_ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]


def _appendix_b_config(tmp_path):
    """A real Appendix-B file: three pheromone keys, no min_center."""
    source = json.loads((REPO_ROOT / "config" / "il-nv-ai" / "game.json").read_text())
    source["pheromones"].pop("pheromone_min_center_intensity", None)
    target = tmp_path / "pairing"
    target.mkdir()
    (target / "game.json").write_text(json.dumps(source), encoding="utf-8")
    for name in ("game.toml", "rate_limits.json"):
        (target / name).write_text(
            (REPO_ROOT / "config" / "il-nv-ai" / name).read_text(), encoding="utf-8")
    return target


def test_min_center_is_the_only_term_appendix_b_may_omit():
    assert APP_B_OPTIONAL_TERMS == {"min_center_intensity": 0.5}


def test_an_appendix_b_file_without_min_center_still_loads(tmp_path):
    terms = terms_from_config(ConfigManager(_appendix_b_config(tmp_path)))
    assert terms["min_center_intensity"] == 0.5      # the SPEC's documented default
    assert len(terms) == 14


def test_the_default_reproduces_the_agreed_terms_hash(tmp_path):
    """The whole point: an Appendix-B file must still derive the signed hash both
    peers compare, or the two scopes cannot coexist."""
    import hashlib

    from cop_thief_core.interop.canonical import canonical_bytes
    terms = terms_from_config(ConfigManager(_appendix_b_config(tmp_path)))
    assert hashlib.sha256(canonical_bytes(terms)).hexdigest() == (
        "a284082dfb1572236f1b614d29295a99625539c7d33a096f7f8921bafbc3d08d")


def test_an_explicit_value_still_wins_over_the_default(tmp_path):
    """A partner that DOES carry the key must not be silently overridden."""
    source = json.loads((REPO_ROOT / "config" / "il-nv-ai" / "game.json").read_text())
    source["pheromones"]["pheromone_min_center_intensity"] = 0.7
    target = tmp_path / "explicit"
    target.mkdir()
    (target / "game.json").write_text(json.dumps(source), encoding="utf-8")
    for name in ("game.toml", "rate_limits.json"):
        (target / name).write_text(
            (REPO_ROOT / "config" / "il-nv-ai" / name).read_text(), encoding="utf-8")
    assert terms_from_config(ConfigManager(target))["min_center_intensity"] == 0.7


def test_other_missing_terms_are_still_refused(tmp_path):
    """Only min_center is optional — a genuinely incomplete config must fail."""
    import pytest

    from cop_thief_core.exceptions import AgreementError
    source = json.loads((REPO_ROOT / "config" / "il-nv-ai" / "game.json").read_text())
    source["movement_and_barriers"].pop("max_barriers")
    target = tmp_path / "broken"
    target.mkdir()
    (target / "game.json").write_text(json.dumps(source), encoding="utf-8")
    for name in ("game.toml", "rate_limits.json"):
        (target / name).write_text(
            (REPO_ROOT / "config" / "il-nv-ai" / name).read_text(), encoding="utf-8")
    with pytest.raises(AgreementError, match="barriers_max"):
        terms_from_config(ConfigManager(target))
