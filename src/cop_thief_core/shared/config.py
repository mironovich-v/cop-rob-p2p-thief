"""ConfigManager: the single source of configuration for the whole app.

Loads the private ``game.toml`` + ``rate_limits.json`` and the optional signed
``game.json`` (the Appendix-F constitution). The shared game.json overlays the
private TOML so both peers play byte-identical agreed terms; values are served by
dotted key with defaults. Secrets never live in config (use ``.env`` / secrets/).
"""

import json
import tomllib
from pathlib import Path
from typing import Any

from cop_thief_core.exceptions import ConfigError, ConfigVersionError
from cop_thief_core.shared.version import SUPPORTED_CONFIG_VERSIONS

GAME_FILE = "game.toml"
RATE_FILE = "rate_limits.json"
SHARED_GAME_FILE = "game.json"


def _translate_shared(shared: dict) -> dict:
    """Map the signed game.json (Appendix-F schema) onto the internal dotted
    namespace, so ``get('board.size')`` etc. work. Only present keys are emitted."""
    out: dict[str, dict] = {}

    def put(section: str, key: str, value: Any) -> None:
        out.setdefault(section, {})[key] = value

    board = shared.get("board_and_agents", {})
    for src, (sec, dst) in {
        "grid_size": ("board", "size"),
        "axis_origin_corner": ("board", "axis_origin_corner"),
        "axis_start_index": ("board", "axis_start_index"),
        "thief_start": ("positions", "thief_start"),
        "cop_start": ("positions", "cop_start"),
    }.items():
        if src in board:
            put(sec, dst, board[src])

    world = shared.get("world", {})
    for src, dst in {"map_area": "setting", "hint_max_words": "hint_max_words"}.items():
        if src in world:
            put("play", dst, world[src])

    mov = shared.get("movement_and_barriers", {})
    for src, dst in {
        "move_set": "move_set",
        "max_barriers": "barriers_max",
        "max_moves": "max_moves",
        "survival_threshold": "max_steps",
    }.items():
        if src in mov:
            put("rules", dst, mov[src])

    if "scoring" in shared:
        out["scoring"] = dict(shared["scoring"])

    phe = shared.get("pheromones", {})
    for src, dst in {
        "pheromone_center_intensity": "emit_intensity",
        "pheromone_decay": "decay_per_step",
        "pheromone_grid_size": "grid_size",
        "pheromone_min_center_intensity": "min_center_intensity",
    }.items():
        if src in phe:
            put("smell", dst, phe[src])

    if "num_games" in shared.get("network_and_league", {}):
        put("game", "num_games", shared["network_and_league"]["num_games"])
    return out


def _deep_merge(base: dict, overlay: dict) -> None:
    """Recursively merge ``overlay`` into ``base`` (overlay wins on leaf conflicts)."""
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def _check_version(data: dict, source: str) -> None:
    version = data.get("version", "unknown")
    if version not in SUPPORTED_CONFIG_VERSIONS:
        raise ConfigVersionError(
            f"{source} version {version!r} not supported; expected {SUPPORTED_CONFIG_VERSIONS}"
        )


class ConfigManager:
    """Loads and serves the merged private + signed-shared configuration."""

    def __init__(self, config_dir: str | Path) -> None:
        self._dir = Path(config_dir)
        if not self._dir.is_dir():
            raise ConfigError(f"Config directory not found: {self._dir}")
        self._game = self._load_toml(self._dir / GAME_FILE)
        self._rates = self._load_json(self._dir / RATE_FILE)
        _check_version(self._game, GAME_FILE)
        _check_version(self._rates, RATE_FILE)
        shared_path = self._dir / SHARED_GAME_FILE
        if shared_path.is_file():
            self._shared = self._load_json(shared_path)
            _deep_merge(self._game, _translate_shared(self._shared))
        else:
            self._shared = {}

    @staticmethod
    def _load_toml(path: Path) -> dict:
        try:
            with path.open("rb") as handle:
                return tomllib.load(handle)
        except FileNotFoundError as exc:
            raise ConfigError(f"Missing config file: {path}") from exc
        except tomllib.TOMLDecodeError as exc:
            raise ConfigError(f"Invalid TOML in {path}: {exc}") from exc

    @staticmethod
    def _load_json(path: Path) -> dict:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ConfigError(f"Missing config file: {path}") from exc
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid JSON in {path}: {exc}") from exc

    def get(self, dotted_key: str, default: Any = None) -> Any:
        """Fetch a merged value by dotted key, e.g. ``get('board.size')``."""
        node: Any = self._game
        for part in dotted_key.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    @property
    def rate_limits(self) -> dict:
        return self._rates

    @property
    def shared(self) -> dict:
        return self._shared

    def service_limits(self, service: str) -> dict:
        """Rate limits for a service, falling back to the default block."""
        return self._rates.get("services", {}).get(service) or self._rates.get("default", {})
