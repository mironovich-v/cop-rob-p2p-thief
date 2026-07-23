"""Sealing helpers: build and SHA-256-seal the per-step records a peer commits to,
and assemble the wire TurnMessage. The one-time host-spec record and the identity's
`spec` field are added with sysinfo at Stage 6.1.
"""

from datetime import UTC, datetime

from cop_thief_core.interop.hashing import seal
from cop_thief_core.protocol import TurnMessage
from cop_thief_core.shared.sysinfo import collect_spec
from cop_thief_core.shared.version import CODE_VERSION


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def identity_from_config(cfg) -> dict:
    """This peer's static group identity, exchanged in the handshake (not signed).
    Roles alternate across sub-games, so identity is per-GROUP, not per-role.
    Includes the host `spec` because the declaration lists each group's hardware."""
    return {
        "group_id": cfg.get("game.group_id", "unknown-group"),
        "group_name": cfg.get("game.group_name", "unnamed"),
        "members": cfg.get("game.members", []),
        "repos": cfg.get("game.repos", {}),
        "mcp_servers": cfg.get("game.mcp_servers", {}),
        "llm_model": cfg.get("llm.model", "") or "cli-default",
        "spec": collect_spec(),
    }


def sealed_spec_record(config, sub_game_number: int = 1) -> dict:
    """Step-0 record: host spec + model + group + code version, sealed. The live
    series index (roles alternate each sub-game), not a static config value."""
    payload = {
        "step": 0,
        "type": "system_spec",
        "spec": collect_spec(),
        "model": config.get("llm.model", "") or "cli-default",
        "code_version": CODE_VERSION,
        "group_name": config.get("game.group_name", "unnamed"),
        "sub_game_number": sub_game_number,
    }
    return {"payload": payload, **seal(payload)}


def _state_str(state) -> str:
    """Compact, replayable board-state string (self only — never the opponent)."""
    barriers = sorted([list(cell) for cell in state.barriers])
    return f"grid={state.board.size}x{state.board.size};self={list(state.position)};barriers={barriers}"


def sealed_step_record(state, decision, usage: dict, tokens_total: int) -> dict:
    """One turn's true state + move + intent + hint + prompt-discussion + tokens, sealed.

    The whole payload is hashed, so the prompt discussion is audit-covered too.
    """
    payload = {
        "step": state.step_number,
        "state": _state_str(state),
        "position": list(state.position),
        "move": state.log[-1]["move"] if state.log else "-",
        "intent": decision.verdict,
        "verdict": decision.verdict,  # kept for audit/replay/report consumers
        "hint": decision.hint,
        "prompt_discussion": {
            "llm_prompt": decision.prompt_text,
            "llm_reasoning": decision.reasoning,
            "bluff_classification": decision.verdict,
        },
        "model": usage.get("model", "unknown"),
        "tokens_step": usage.get("total", 0),
        "tokens_total": tokens_total,
        "response_seconds": decision.response_seconds,
        "random_move": decision.random_move,
    }
    return {"payload": payload, **seal(payload)}


def build_turn_message(
    state,
    role: str,
    hint: str,
    smell_grid: dict,
    commit: str,
    capture_claim=None,
    claim_response=None,
    win_claim=None,
) -> TurnMessage:
    """The wire message for this turn (the turn token travels with it)."""
    barrier = state.last_barrier()
    return TurnMessage(
        step=state.step_number,
        sender=role,
        hint=hint,
        smell_grid=smell_grid,
        commit=commit,
        timestamp=now_iso(),
        barrier_placed=list(barrier) if barrier else None,
        capture_claim=capture_claim,
        claim_response=claim_response,
        win_claim=win_claim,
    )
