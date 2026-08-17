"""Rule-52 first-meeting ledger + the three graded league fields (SPEC §6.2).

The lecturer weighs these; rule 35 punishes two reports that disagree on them
exactly as it punishes a score mismatch, and a false ``first_meeting`` is a
rule-38 project-level disqualification — produced automatically by a stale
ledger. So the ledger is COMMITTED evidence (a counted series is not over until
the ledger that proves it happened is pushed), and ``null`` means UNCLAIMED —
legal, joinable, and never spelled ``0``.
"""

import json
from pathlib import Path

LEDGER_VERSION = "1.00"


def load_ledger(path: str | Path) -> dict:
    """Read the committed ledger; a missing file is an honest empty history."""
    path = Path(path)
    if not path.is_file():
        return {"version": LEDGER_VERSION, "opponents": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def first_meeting(ledger: dict, opponent_gid: str) -> bool:
    """Rule 52: only the FIRST counted series with an opponent counts."""
    return opponent_gid not in ledger.get("opponents", {})


def advance_ledger(path: str | Path, opponent_gid: str, game_id: str) -> dict:
    """Record a settled counted series — part of the settlement path, not an
    afterthought. Returns the written ledger (caller commits the file)."""
    path = Path(path)
    ledger = load_ledger(path)
    entry = ledger["opponents"].setdefault(opponent_gid, {"counted_series": 0})
    entry["counted_series"] += 1
    entry["last_game_id"] = game_id
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ledger


def league_fields(
    own_gid: str, opp_gid: str, own_count: int, opp_count: int | None,
    counted: bool, first: bool, winner_group: str | None,
) -> dict:
    """The three graded fields, armed by the RUN (not the calendar).

    Counted: counts are inclusive of this series. Friendly: truthful but
    unbumped, diversity all-false. ``diversity_reward_applied`` is DERIVED —
    counted AND first meeting AND that group won — so both teams' files mark
    the winner true whichever side it is; the +10 never enters the totals.
    """
    bump = 1 if counted else 0
    return {
        "games_played_including_this": {
            own_gid: own_count + bump,
            opp_gid: opp_count + bump if opp_count is not None else None,
        },
        "first_meeting_between_groups": first,
        "diversity_reward_applied": {
            gid: bool(counted and first and winner_group == gid)
            for gid in (own_gid, opp_gid)
        },
    }
