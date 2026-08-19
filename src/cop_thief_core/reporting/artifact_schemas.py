"""Self-documenting `_schema` / `_remark` text and versions for the four game JSON
artifacts (book Appendix F). This text is explanatory only — it is never hashed —
so it need not match cross-team; the VALUES and their `config_sha256` are what must
agree.
"""

SCHEMA_VERSION = "1.1"
DEFAULT_TIMEZONE = "Asia/Jerusalem"

SCHEMA_DECLARATION = (
    "Static pre-game declaration for the whole series: team identity, members, "
    "repos, MCP URLs, hardware, model, token cap, and start/end times. Roles "
    "alternate across sub-games, so no role/sub_game_number appears here."
)
SCHEMA_CONFIG = (
    "Agreed game configuration for one sub-game (Appendix F). Both teams hold "
    "byte-identical values, locked by config_sha256; the file name is unique per game."
)
SCHEMA_LOG = (
    "Per-sub-game commit-reveal log for the replay viewer: every sealed step and the "
    "mutual-audit result. Static team metadata lives in the declaration; join by game_uid."
)
SCHEMA_RESULT = (
    "Aggregated final result over all sub-games: per-group scores, the series "
    "winner/tie, and the mutual-agreement signature. Both teams email their own copy."
)
LINKS_REMARK = (
    "Logical roles, not fixed filenames. Names derive from game_id: declaration/result "
    "= <name>_<game_id>.json; per-sub-game config/log = <name>_<game_id>_g<NN>.json."
)
