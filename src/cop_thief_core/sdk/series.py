"""Run a SERIES of N sub-games between two peers with role alternation.

The transport (and thus each peer's MCP server) is built ONCE by the caller and
reused across sub-games. Each sub-game gets a fresh PeerRuntime (fresh
state/belief/scent/commit chain). Roles alternate: a peer plays its config-natural
role on odd sub-games and the opposite on even ones, so the two peers stay
consistent (when A is cop, B is thief). Control-channel restart is deferred to the
GUI stage.
"""

from dataclasses import dataclass

from cop_thief_core.constants import Role
from cop_thief_core.orchestration.runtime import PeerRuntime
from cop_thief_core.orchestration.sealing import identity_from_config


@dataclass
class SeriesResult:
    """Everything the artifact emitters need after a whole series is played."""

    summaries: list[dict]
    own_identity: dict
    peer_identity: dict
    game_id: str | None
    game_uid: str | None


def role_for(natural: Role, sub_game_number: int) -> Role:
    """Natural role on odd sub-games, the opposite on even ones (alternation)."""
    if sub_game_number % 2 == 1:
        return natural
    return Role.THIEF if natural is Role.POLICE else Role.POLICE


def run_series(config, natural_role: Role, llm, transport, listener=None) -> SeriesResult:
    """Play the whole series (num_games sub-games) with role alternation."""
    own_identity = identity_from_config(config)
    num_games = config.get("game.num_games")
    summaries: list[dict] = []
    peer_identity: dict = {}
    game_id = game_uid = None
    for sub_game_number in range(1, num_games + 1):
        runtime = PeerRuntime(
            role_for(natural_role, sub_game_number),
            config,
            transport,
            llm=llm,
            own_identity=own_identity,
            sub_game_number=sub_game_number,
            listener=listener,
        )
        summaries.append(runtime.run())
        peer_identity = runtime.peer_identity or peer_identity
        game_id, game_uid = runtime.game_id, runtime.game_uid
    return SeriesResult(summaries, own_identity, peer_identity, game_id, game_uid)
