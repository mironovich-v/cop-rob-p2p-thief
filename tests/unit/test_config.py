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


def test_call_timeout_must_stay_under_signed_deadline(tmp_path):
    # 8.11: a per-call cap at/above the signed response_timeout_sec must refuse
    # to load — a retried 30s call breaches a 30s deadline while looking fine.
    toml = MIN_TOML + 'call_timeout_seconds = 30\n'
    shared = {**SHARED, "network_and_league": {"response_timeout_sec": 30}}
    with pytest.raises(ConfigError, match="call_timeout"):
        ConfigManager(_write(tmp_path, toml=toml, shared=shared))


def test_call_timeout_under_deadline_loads(tmp_path):
    toml = MIN_TOML + 'call_timeout_seconds = 10\n'
    shared = {**SHARED, "network_and_league": {"response_timeout_sec": 30}}
    cfg = ConfigManager(_write(tmp_path, toml=toml, shared=shared))
    assert cfg.get("network.call_timeout_seconds") == 10


def test_imreeyal_pairing_config_is_playable():
    # The committed pairing config must load, clear the App-F floors, and
    # derive the ids both teams compare in chat before any window.
    from cop_thief_core.interop.game_ids import derive_game_ids
    from cop_thief_core.interop.negotiation import terms_from_config, validate_minimums

    cfg = ConfigManager(REPO_ROOT / "config" / "imreeyal")
    terms = terms_from_config(cfg)
    validate_minimums(terms)
    game_id, game_uid = derive_game_ids(terms, "vm__fabi", "imreeyal")
    assert game_id == "imreeyal-vs-vm__fabi"
    assert game_uid == "0e07bcda-4bfd-3668-1fec-86833963b58c"
    assert cfg.get("game.group_id") == "vm__fabi"
    assert cfg.get("game.opponent_group_id") == "imreeyal"
    assert cfg.get("game.num_games") == 6
    assert cfg.get("game.counted") is False  # armed only on counted day
    # The friendly recipients never include the lecturer.
    lecturer = cfg.get("email.lecturer_address").strip().lower()
    assert all(r.strip().lower() != lecturer for r in cfg.get("email.recipient"))


def test_nis_yar1_pairing_config_is_playable():
    from cop_thief_core.interop.game_ids import derive_game_ids
    from cop_thief_core.interop.negotiation import terms_from_config, validate_minimums

    cfg = ConfigManager(REPO_ROOT / "config" / "nis-yar1")
    terms = terms_from_config(cfg)
    validate_minimums(terms)
    game_id, game_uid = derive_game_ids(terms, "vm__fabi", "nis-yar1")
    assert game_id == "nis-yar1-vs-vm__fabi"
    assert game_uid == "b38f33f3-3ec8-be1d-a464-4fa5c9cb35df"
    assert cfg.get("game.opponent_group_id") == "nis-yar1"
    # Role-split opponent: both per-role dial targets are configured.
    assert cfg.get("network.opponent_url_police")
    assert cfg.get("network.opponent_url_thief")


def test_local_overlay_wins_without_dirtying_the_tree(tmp_path):
    # Window-day values (an opponent's rotating quick-tunnel URLs) live in a
    # git-ignored game.local.toml so every T is played on a CLEAN tree.
    shared = {**SHARED, "network_and_league": {"response_timeout_sec": 30}}
    _write(tmp_path, toml=MIN_TOML + 'opponent_url = "tracked"\n', shared=shared)
    (tmp_path / "game.local.toml").write_text(
        '[network]\nopponent_url = "https://live.example/mcp"\n', encoding="utf-8")
    cfg = ConfigManager(tmp_path)
    assert cfg.get("network.opponent_url") == "https://live.example/mcp"
    assert cfg.get("network.my_port") == 8802  # non-overlaid keys untouched


def test_missing_local_overlay_changes_nothing(tmp_path):
    cfg = ConfigManager(_write(tmp_path))
    assert cfg.get("network.my_port") == 8802


def test_il_nv_ai_pairing_config_is_playable():
    from cop_thief_core.interop.game_ids import derive_game_ids
    from cop_thief_core.interop.negotiation import terms_from_config, validate_minimums

    cfg = ConfigManager(REPO_ROOT / "config" / "il-nv-ai")
    terms = terms_from_config(cfg)
    validate_minimums(terms)
    game_id, game_uid = derive_game_ids(terms, "vm__fabi", "il-nv-ai")
    assert game_id == "il-nv-ai-vs-vm__fabi"
    # COUNTED series (2026-08-22): num_games moved 1 -> 6, which moves the signed
    # terms and therefore the uid. Both values were confirmed identical by
    # il-nv-ai before the window; the warm-up uid was 00aec465-….
    assert game_uid == "566d2396-e3e9-10ef-6f15-ef51ff64acba"
    assert cfg.get("game.num_games") == 6
    assert cfg.get("game.counted") is False  # armed only by the window overlay
    # We are THIEF on odd sub-games here (kit_sorted_first_police_odd_v1 puts
    # il-nv-ai first), the OPPOSITE of the warm-up: launch thief_agent.
    assert cfg.get("game.counted_games_played") == 2  # nis-yar1 + vibecode banked
