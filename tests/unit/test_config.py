"""Tests for ConfigManager (PRD_config_constitution, TODO slice 1.5)."""

import json
from pathlib import Path

import pytest

from cop_thief_core.exceptions import ConfigError, ConfigVersionError
from cop_thief_core.shared.config import ConfigManager

REPO_ROOT = Path(__file__).resolve().parents[2]

MIN_TOML = 'version = "1.10"\n[board]\nsize = 5\n[network]\nmy_port = 8802\n'
MIN_RATES = {"version": "1.10", "default": {"requests_per_minute": 9}, "queue": {"max_depth": 3}}
SHARED = {"schema_version": "1.3", "board_and_agents": {"grid_size": 7}, "scoring": {"tie_score": 2}}


def _write(dir_: Path, toml=MIN_TOML, rates=MIN_RATES, shared=None):
    (dir_ / "game.toml").write_text(toml, encoding="utf-8")
    (dir_ / "rate_limits.json").write_text(json.dumps(rates), encoding="utf-8")
    if shared is not None:
        (dir_ / "game.json").write_text(json.dumps(shared), encoding="utf-8")
    return dir_


def test_missing_dir_raises(tmp_path):
    with pytest.raises(ConfigError):
        ConfigManager(tmp_path / "nope")


def test_dotted_get_and_default(tmp_path):
    cfg = ConfigManager(_write(tmp_path))
    assert cfg.get("network.my_port") == 8802
    assert cfg.get("board.size") == 5
    assert cfg.get("missing.key", "fallback") == "fallback"


def test_unsupported_version_raises(tmp_path):
    with pytest.raises(ConfigVersionError):
        ConfigManager(_write(tmp_path, toml='version = "9.9"\n'))


def test_missing_required_file_raises(tmp_path):
    (tmp_path / "game.toml").write_text(MIN_TOML, encoding="utf-8")  # no rate_limits.json
    with pytest.raises(ConfigError):
        ConfigManager(tmp_path)


def test_shared_overlay_overrides_local(tmp_path):
    # local board.size = 5, shared grid_size = 7 -> shared wins after translate/merge
    cfg = ConfigManager(_write(tmp_path, shared=SHARED))
    assert cfg.get("board.size") == 7
    assert cfg.get("scoring.tie_score") == 2
    assert cfg.shared["schema_version"] == "1.3"


def test_service_limits_falls_back_to_default(tmp_path):
    cfg = ConfigManager(_write(tmp_path))
    assert cfg.service_limits("claude") == {"requests_per_minute": 9}
    assert cfg.rate_limits["queue"]["max_depth"] == 3


def test_shipped_police_template_loads():
    cfg = ConfigManager(REPO_ROOT / "config" / "police")
    assert cfg.get("board.size") == 7  # from signed game.json overlay
    assert cfg.get("rules.max_steps") == 35
    assert cfg.get("smell.decay_per_step") == 0.10
    assert cfg.get("network.my_port") == 8802  # from private game.toml
    assert cfg.get("game.group_id") == "vm__fabi-police"
