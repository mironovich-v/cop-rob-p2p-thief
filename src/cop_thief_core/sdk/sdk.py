"""SimulationSdk — the single business entry point every consumer (CLI, GUI, tests)
goes through. run_peer() plays one standalone agent through a whole series of N
sub-games against an opponent known only by URL. The transport/server are built
once and reused. The four JSON artifacts, the report, and Gmail sending are added
in the reporting stage; a real Claude LLM provider in the language stage.
"""

from pathlib import Path

from cop_thief_core.constants import Role
from cop_thief_core.interop.negotiation import terms_from_config, validate_minimums
from cop_thief_core.sdk.series import run_series
from cop_thief_core.shared.config import ConfigManager


class StubLlm:
    """A deterministic, offline stand-in — the move is pure Python regardless."""

    last_usage = {"model": "stub", "total": 0}
    tokens_consumed = 0

    def send(self, prompt: str) -> str:
        return "stub reply — no structured move here"


class SimulationSdk:
    """Facade over the whole simulation for one peer."""

    def __init__(self, config_dir: str | Path, workdir: str | Path = ".") -> None:
        self.config = ConfigManager(config_dir)
        self._workdir = Path(workdir)

    def _build_llm(self, stub: bool):
        return StubLlm()  # the real ClaudeCliProvider is wired at Stage 4.3

    def _build_transport(self, role: Role):  # pragma: no cover (network boundary)
        from cop_thief_core.infra.mcp_client import McpTransport
        from cop_thief_core.infra.mcp_server import start_peer_server

        cfg = self.config
        inboxes = start_peer_server(
            role.value, cfg.get("network.host", "127.0.0.1"), cfg.get("network.my_port")
        )
        return McpTransport(
            cfg.get("network.opponent_url"),
            inboxes,
            connect_timeout=cfg.get("network.connect_timeout_seconds", 60),
            retry_interval=cfg.get("network.retry_interval_seconds", 1.0),
            audit_send_timeout=cfg.get("network.audit_send_timeout_seconds", 10),
        )

    def run_peer(self, role: str, stub_llm: bool = True, transport=None, listener=None) -> dict:
        """Play the whole series and return the summaries + shared ids.

        (Artifact/report/email emission is added in the reporting stage.)
        """
        peer_role = Role(role)
        validate_minimums(terms_from_config(self.config))  # fail fast before any server
        transport = transport or self._build_transport(peer_role)
        series = run_series(self.config, peer_role, self._build_llm(stub_llm), transport, listener)
        return {
            "summaries": series.summaries,
            "result": series.summaries[-1],
            "game_id": series.game_id,
            "game_uid": series.game_uid,
            "own_identity": series.own_identity,
            "peer_identity": series.peer_identity,
        }
