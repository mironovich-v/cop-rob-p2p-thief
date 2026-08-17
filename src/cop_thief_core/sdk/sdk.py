"""SimulationSdk — the single business entry point every consumer (CLI, GUI, tests)
goes through. run_peer() plays one standalone agent through a whole series of N
sub-games against an opponent known only by URL, emits the four JSON artifacts, and
sends the official report (Gmail draft, disabled by default). The transport/server
are built once and reused; a real Claude LLM provider is wired in the language stage.
"""

from pathlib import Path

from cop_thief_core.constants import Role
from cop_thief_core.exceptions import SimulationError
from cop_thief_core.infra.email_sender import EmailSender
from cop_thief_core.interop.negotiation import terms_from_config, validate_minimums
from cop_thief_core.reporting.emit import emit_series
from cop_thief_core.reporting.report_builder import build_report, report_body
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
        self.email_sender = None  # injectable for tests; else built per-send

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
            call_timeout=cfg.get("network.call_timeout_seconds", 10),
            handshake_repush=cfg.get("network.handshake_repush_seconds", 5.0),
        )

    def run_peer(self, role: str, stub_llm: bool = True, transport=None,
                 listener=None, emit: bool = True, counted: bool = False) -> dict:
        """Play the whole series, emit the four JSON artifacts, auto-fire the
        official report at settlement (dry-run/disabled by default), and return
        summaries + shared ids + report + email result. Artifacts land under
        ``<workdir>/<logs_dir>/<group_id>/``. ``counted`` is the CLI half of the
        double arming; config ``game.counted`` is the other half (ADR-20).
        """
        peer_role = Role(role)
        armed = self._arm(counted)
        validate_minimums(terms_from_config(self.config))  # fail fast before any server
        transport = transport or self._build_transport(peer_role)
        series = run_series(self.config, peer_role, self._build_llm(stub_llm), transport, listener)
        out = {
            "summaries": series.summaries,
            "result": series.summaries[-1],
            "game_id": series.game_id,
            "game_uid": series.game_uid,
            "own_identity": series.own_identity,
            "peer_identity": series.peer_identity,
        }
        if emit:
            logs_dir = self._workdir / self.config.get("paths.logs_dir", "logs")
            out["report"] = emit_series(self.config, logs_dir, series)
            out["artifacts_dir"] = str(logs_dir / series.own_identity.get("group_id", ""))
            out["email"] = self._email_report(series, out["report"], armed)
        return out

    def _arm(self, counted_cli: bool) -> bool:
        """Double arming (ADR-20): CLI --counted AND config game.counted must
        agree; a mismatch refuses to start, an armed run preflights delivery."""
        counted_cfg = bool(self.config.get("game.counted", False))
        if counted_cli != counted_cfg:
            raise SimulationError(
                f"counted arming mismatch: CLI={counted_cli} config={counted_cfg} "
                f"— both halves must agree (ADR-20)")
        armed = counted_cli and counted_cfg
        if armed:
            (self.email_sender or EmailSender(self.config)).preflight_armed()
        return armed

    def _email_report(self, series, report: dict, armed: bool) -> dict:
        """Auto-fire the official report at settlement (rule 32): the emailed body
        is the EXACT hashed canonical bytes (`report_body`), also attached as the
        result file; subject in the reference form. Dry-run/disabled by default."""
        summary = series.summaries[-1]
        signed = build_report(summary, terms_from_config(self.config))
        winner = report["final_result"].get("winner_group") or "tie"
        subject = (f"Police-Thief series result: winner {winner} "
                   f"(reported by {summary['role']})")
        sender = self.email_sender or EmailSender(self.config)
        return sender.send_report(report_body(signed), subject,
                                  attachment_name=f"result_{series.game_id}.json",
                                  armed=armed)
