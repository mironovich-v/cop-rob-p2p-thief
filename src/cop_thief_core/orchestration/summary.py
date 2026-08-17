"""End-of-game: the mutual audit exchange and the peer's final match summary.

A failed audit of the opponent's revealed log forfeits the game for them
(tamper_forfeit) — the honest peer wins by technical decision regardless of the
board result. Result totals are always DERIVED from the sealed log, never trusted.
"""

import time

from cop_thief_core.constants import RESULT_CAPTURE, RESULT_DISPUTED, Role
from cop_thief_core.interop import audit_records
from cop_thief_core.orchestration.audit_checks import corroborate_capture
from cop_thief_core.protocol import AuditPayload

SKIPPED_AUDIT = {"passed": False, "verified_steps": 0, "failed_steps": [], "skipped": True}
NO_AUDIT_RESULTS = ("timeout", "stopped")  # nobody / nothing to audit with
TAMPER_FORFEIT = "tamper_forfeit"


def _thief_caught_response(rt) -> dict | None:
    """The thief's final ``caught: true`` response, as it arrived on the wire."""
    for message in reversed(rt.handler.history):
        response = message.get("claim_response")
        if response and response.get("caught"):
            return response
    return None


def snapshot(rt) -> dict:
    """GUI render snapshot: the peer's own truth + its belief, nothing more."""
    return {
        "role": rt.role.value,
        "step": rt.state.step_number,
        "position": rt.state.position,
        "barriers": sorted(rt.state.barriers),
        "barriers_used": rt.state.my_barriers,
        "visited": sorted(rt.state.visited),
        "belief": rt.belief.as_matrix(),
    }


def finish(rt) -> dict:
    """Exchange audits (when a real result exists) and build the summary dict."""
    result, winner = rt._result
    audit = SKIPPED_AUDIT
    if result not in NO_AUDIT_RESULTS:
        mine = AuditPayload(sender=rt.role.value, records=rt.records, result_claim=result)
        theirs = rt._transport.exchange_audit(mine.to_dict())
        if theirs is not None:
            their_records = AuditPayload.from_dict(theirs).records
            audit = audit_records(their_records)
            if not audit["passed"]:
                result, winner = TAMPER_FORFEIT, rt.role.value
            elif result == RESULT_CAPTURE and rt.role is Role.POLICE:
                # SPEC §3.1: a thief-sent caught:true is corroborated, not believed.
                response = _thief_caught_response(rt)
                if response is not None:
                    check = corroborate_capture(rt.state, rt.records, response, their_records)
                    audit = {**audit, "capture_corroboration": check}
                    if not check["corroborated"]:
                        result, winner = RESULT_DISPUTED, None  # never counted clean
    return {
        "result": result,
        "winner": winner,
        "steps": rt.state.step_number,
        "tokens_total": rt._tokens_total,
        "group_name": rt._config.get("game.group_name", "unnamed"),
        "sub_game_number": rt._sub_game_number,
        "started_at": rt._started_at,
        "duration_seconds": round(time.monotonic() - rt._started_monotonic, 1),
        "audit": audit,
        "records": rt.records,
        "history": rt.handler.history,
        "my_log": rt.state.log,
        "role": rt.role.value,
    }
