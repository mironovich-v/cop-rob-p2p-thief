"""SimulationSdk — the single business entry point every consumer (CLI, GUI, tests)
goes through. run_peer() plays one standalone agent through a whole series of N
sub-games against an opponent known only by URL, emits the four JSON artifacts, and
sends the official report (Gmail draft, disabled by default). The transport/server
are built once and reused; a real Claude LLM provider is wired in the language stage.
"""

import json
import time
from pathlib import Path

from cop_thief_core.constants import Role
from cop_thief_core.exceptions import SimulationError
from cop_thief_core.infra.email_sender import EmailSender
from cop_thief_core.interop.negotiation import terms_from_config, validate_minimums
from cop_thief_core.orchestration.sealing import playing_commit
from cop_thief_core.reporting.emit import emit_series
from cop_thief_core.sdk.filing import filable
from cop_thief_core.sdk.series import run_series
from cop_thief_core.shared.config import ConfigManager
from cop_thief_core.shared.provenance import check_published, git_is_ancestor, git_ls_remote


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
            # Deliberately NOT connect_timeout: a long handshake patience must
            # not become a long silent hang when an audit goes missing.
            audit_wait=cfg.get("network.audit_wait_seconds", 120.0),
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
        built_transport = transport is None
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
        self._linger_for_final_ack(built_transport)
        return out

    def _linger_for_final_ack(self, built_transport: bool) -> None:
        """Hold this peer's MCP server open briefly after the last sub-game.

        The opponent's final ``submit_audit`` ack is written by a DAEMON server
        thread. Exiting the instant the runtime drains the audit inbox kills that
        thread mid-response, so the audit is fully received and acted on while the
        sender sees nothing — an otherwise-clean game logged as
        ``audit_send_unacknowledged`` (reported by il-nv-ai on both runs,
        2026-08-21; reproduced at a 15.0s client timeout, and answered in 0.22s
        once the server outlives the drain). Only a peer that OWNS its server has
        an ack to flush; an injected transport has no server and must not wait.
        """
        if built_transport:
            time.sleep(self.config.get("network.shutdown_grace_seconds", 5.0))

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
            self._require_published_commit()
        return armed

    def _require_published_commit(self) -> None:
        """Refuse an armed run whose playing commit is not in the submitted repos.

        We name the two role repositories on the wire and in every artifact, and
        a grader resolves the declared commit there. A commit that never left
        this machine makes the whole series unverifiable, and a counted series
        is the one that cannot be replayed — so this refuses BEFORE the first
        move rather than discovering it at grading. Friendlies are never blocked:
        a network check must not cost a window.
        """
        status = check_published(
            playing_commit(), self.config.get("game.repos", {}) or {},
            git_ls_remote, git_is_ancestor)
        if not status["published"]:
            raise SimulationError(
                f"armed counted run: playing commit is not published — "
                f"{status['detail']}. Re-export and push the submission repos first.")

    def _email_report(self, series, report: dict, armed: bool) -> dict:
        """Auto-fire the official report at settlement (rule 32). The mail IS the
        RESULT ARTIFACT (league SPEC §6.1 settled convention: result-only mail —
        the same bytes filed as result_<game_id>.json ride as the body AND the
        single named attachment); subject in the reference form. The Hebrew
        book-schema report stays a repo artifact, never mailed (§6.1 documented
        tension, resolved by both league teams toward the results file)."""
        if armed:
            # Rule 35: an incomplete or unverified series is one NOBODY files —
            # two teams filing disagreeing reports of one game is the shape the
            # rule zeroes. Friendlies are exempt on purpose (see sdk.filing).
            may_file, reason = filable(
                series.summaries, self.config.get("game.num_games"))
            if not may_file:
                return {"sent": False, "reason": f"withheld: {reason}"}
        summary = series.summaries[-1]
        body = json.dumps(report, ensure_ascii=False, indent=2)  # == the filed bytes
        winner = report["final_result"].get("winner_group") or "tie"
        subject = (f"Police-Thief series result: winner {winner} "
                   f"(reported by {summary['role']})")
        sender = self.email_sender or EmailSender(self.config)
        return sender.send_report(body, subject,
                                  attachment_name=f"result_{series.game_id}.json",
                                  armed=armed)
