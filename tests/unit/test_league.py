"""Rule-52 ledger + the three graded league fields (SPEC §6.2, TODO 8.7).

Rule-35 punishes two reports disagreeing on these exactly like a score
mismatch; a false first_meeting is a rule-38 disqualification produced
automatically by a stale ledger. Null means UNCLAIMED and is legal — never 0.
"""

from cop_thief_core.reporting.league import (
    advance_ledger,
    first_meeting,
    league_fields,
    load_ledger,
)


def test_empty_or_missing_ledger_means_first_meeting(tmp_path):
    ledger = load_ledger(tmp_path / "nope.json")
    assert first_meeting(ledger, "imreeyal") is True


def test_advance_then_not_first_meeting(tmp_path):
    path = tmp_path / "ledger.json"
    advance_ledger(path, "imreeyal", "imreeyal-vs-vm__fabi")
    ledger = load_ledger(path)
    assert first_meeting(ledger, "imreeyal") is False
    assert first_meeting(ledger, "someone-else") is True
    assert ledger["opponents"]["imreeyal"]["counted_series"] == 1


def test_counted_fields_bump_and_derive_diversity():
    fields = league_fields(
        own_gid="vm__fabi", opp_gid="imreeyal", own_count=0, opp_count=5,
        counted=True, first=True, winner_group="imreeyal")
    assert fields["games_played_including_this"] == {"vm__fabi": 1, "imreeyal": 6}
    assert fields["first_meeting_between_groups"] is True
    # DERIVED, winner-true in BOTH files whichever team it is — never modesty.
    assert fields["diversity_reward_applied"] == {"vm__fabi": False, "imreeyal": True}


def test_friendly_fields_stay_truthful_but_disarmed():
    fields = league_fields(
        own_gid="vm__fabi", opp_gid="imreeyal", own_count=0, opp_count=5,
        counted=False, first=True, winner_group="vm__fabi")
    assert fields["games_played_including_this"] == {"vm__fabi": 0, "imreeyal": 5}
    assert fields["first_meeting_between_groups"] is True  # truthful, not bumped
    assert fields["diversity_reward_applied"] == {"vm__fabi": False, "imreeyal": False}


def test_undeclared_opponent_count_stays_null_never_zero():
    fields = league_fields(
        own_gid="vm__fabi", opp_gid="imreeyal", own_count=2, opp_count=None,
        counted=True, first=False, winner_group=None)
    assert fields["games_played_including_this"] == {"vm__fabi": 3, "imreeyal": None}
    assert fields["diversity_reward_applied"] == {"vm__fabi": False, "imreeyal": False}
