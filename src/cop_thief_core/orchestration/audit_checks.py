"""Cop-side corroboration of a capture at audit (league SPEC §3.1, TODO 8.2).

A thief-sent ``caught: true`` is corroborated, never believed: a false answer
profits BOTH peers, so neither can be left to catch it. The answer's cell must
be where the thief's revealed trail ends; a concession's cell must be captured
under the cop's OWN barrier record — never under the barrier list the thief
reports. Parsing is strict; anything unparseable degrades with a note rather
than resolving to a cell (a degraded check is not an accusation).
"""

import re

from cop_thief_core.constants import Cell

_SELF_RE = re.compile(r"self=\[(\d+),\s*(\d+)\]")


def revealed_trail_end(records: list[dict]) -> Cell | None:
    """Where the opponent's revealed trail ends — or None if the evidence is
    missing/malformed (degrade, never guess)."""
    if not records:
        return None
    payload = records[-1].get("payload", {})
    position = payload.get("position")
    if isinstance(position, list | tuple) and len(position) == 2 and all(
        isinstance(value, int) for value in position
    ):
        return (position[0], position[1])
    match = _SELF_RE.search(str(payload.get("state", "")))
    return (int(match[1]), int(match[2])) if match else None


def _parsed_cell(value) -> Cell | None:
    """Strict parse of a claimed cell: a 2-int sequence, or nothing at all.

    A looser parse would resolve a malformed claim to the WRONG cell and accuse
    an honest peer (SPEC §3.1, "widen only what you CHECK"). `bool` is excluded
    because it is an `int` subclass and no cell is ever True/False.
    """
    if isinstance(value, list | tuple) and len(value) == 2 and all(
        isinstance(item, int) and not isinstance(item, bool) for item in value
    ):
        return (value[0], value[1])
    return None


def _my_last_claimed_cell(my_records: list[dict]) -> Cell | None:
    """The cell of my latest capture claim = my position on my last MOVE turn."""
    for record in reversed(my_records):
        payload = record.get("payload", {})
        if str(payload.get("move", "")).startswith("MOVE:"):
            position = payload.get("position")
            if isinstance(position, list | tuple) and len(position) == 2:
                return (position[0], position[1])
    return None


def corroborate_capture(
    my_state, my_records: list[dict], final_response: dict, opponent_records: list[dict]
) -> dict:
    """Verdict on a thief-sent ``caught: true``: answer vs concession, checked.

    Echoing my claimed cell = answer (co-location); naming any other cell =
    concession (rule 46/47). Both settle CAPTURE at play time; they differ HERE.
    """
    cell = _parsed_cell(final_response.get("claim"))
    if cell is None:
        # A final that omits `claim` (or spells it unparseably) is non-conforming
        # — SPEC §3.1 mandates the key. But an unreadable final is missing
        # EVIDENCE, not proof of a lie: degrade with a note, never accuse, and
        # never crash the peer mid-audit (live il-nv-ai warm-up, 2026-08-21).
        return {
            "kind": "unknown",
            "corroborated": True,
            "note": "degraded: final carries no parseable claim cell",
        }
    kind = "answer" if cell == _my_last_claimed_cell(my_records) else "concession"
    if kind == "answer":
        end = revealed_trail_end(opponent_records)
        if end is None:
            return {"kind": kind, "corroborated": True, "note": "degraded: no trail evidence"}
        if end != cell:
            note = f"revealed trail ends at {list(end)}, not the answered {list(cell)}"
            return {"kind": kind, "corroborated": False, "note": note}
        return {"kind": kind, "corroborated": True, "note": ""}
    # Concession: the cell must be captured under MY OWN barrier record.
    walled = cell in my_state.barriers
    enclosed = not my_state.board.neighbors(cell, my_state.barriers)
    if walled or enclosed:
        return {"kind": kind, "corroborated": True, "note": ""}
    note = f"my barrier record leaves {list(cell)} free — concession unsupported"
    return {"kind": kind, "corroborated": False, "note": note}
