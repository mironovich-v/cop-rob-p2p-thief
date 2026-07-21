"""Version tracking for the vm__fabi Cop-Thief P2P project.

Our implementation version is independent of the University of Haifa book /
reference code version we target and the league interop/protocol version. The
config and game.json schema versions must match what the signed terms expect.
"""

CODE_VERSION = "1.0.0"  # our implementation (guideline: start at 1.0)
BOOK_VERSION = "3.0.0"  # University of Haifa book / reference repo we target
PROTOCOL_VERSION = "3.0.0"  # league interop kit / protocol
SUPPORTED_CONFIG_VERSIONS = ("1.10",)  # config/game.toml "version"
GAME_JSON_SCHEMA_VERSION = "1.3"  # shared config/game.json "schema_version"
