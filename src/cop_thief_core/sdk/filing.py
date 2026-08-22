"""Whether a settled series may be FILED with the lecturer.

Rule 35 zeroes contradictory reports of one game, so an incomplete or
unverified series is one nobody should file: filing half a series, or one whose
audit did not verify, manufactures exactly the disagreement the rule punishes.
vibecode's counted runbook withholds automatically below 6/6 Verified OK
(agreed 2026-08-21); this is our equivalent.

Two deliberate boundaries:

* **Armed runs only.** A FRIENDLY report must still fire even from a ragged
  series — at least one partner's gate requires a friendly report to arrive at
  settlement, and a friendly filing harms nobody.
* **A disputed capture still files.** A voided corroboration is "reported, never
  a unilateral rewrite — the logs decide" (SPEC §3.1). Its crypto audit passed;
  suppressing the report would be the unilateral rewrite the SPEC forbids.
"""


def filable(summaries: list[dict], expected: int) -> tuple[bool, str]:
    """(may_file, reason_if_not) for a completed series.

    The reason names WHICH sub-game failed, because the operator's next move is
    to compare that log with the opponent's, and a bare "withheld" would make
    them hunt for it.
    """
    played = len(summaries)
    if played != expected:
        return False, f"incomplete series: {played} of {expected} sub-games settled"
    unverified = [
        str(summary.get("sub_game_number", "?"))
        for summary in summaries
        if not (summary.get("audit") or {}).get("passed")
    ]
    if unverified:
        return False, f"audit not verified for sub-game(s) {', '.join(unverified)}"
    return True, ""


def filable_report(result: dict) -> tuple[bool, str]:
    """The same rule as :func:`filable`, applied to a FILED result artifact.

    The deferred send (``scripts/send_filed_report.py``) reads an artifact from
    disk rather than a live series, and it must not become a way to file exactly
    the report the auto-send guard withheld — so the rule lives here once and
    both paths call it.
    """
    sub_games = result.get("sub_games") or []
    expected = result.get("num_sub_games")
    if expected is None or len(sub_games) != expected:
        return False, f"incomplete series: {len(sub_games)} of {expected} sub-games settled"
    unverified = [
        str(row.get("sub_game_number", "?"))
        for row in sub_games
        if not (row.get("audit") or {}).get("log_verified")
    ]
    if unverified:
        return False, f"audit not verified for sub-game(s) {', '.join(unverified)}"
    return True, ""
