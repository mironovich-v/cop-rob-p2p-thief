"""Tests for league scoring & aggregation (PRD_scoring_league, TODO slice 1.4)."""

from cop_thief_core.constants import RESULT_CAPTURE, RESULT_SURVIVAL, Role
from cop_thief_core.domain.scoring import aggregate, score_subgame

# App-F values passed as config (never hard-coded in src).
SCORING = {"capture_cop": 20, "capture_thief": 5, "survival_cop": 5, "survival_thief": 10}
G1, G2 = "vm__fabi-police", "vm__fabi-thief"


def test_capture_awards_cop_and_thief():
    roles = {G1: Role.POLICE, G2: Role.THIEF}
    assert score_subgame(RESULT_CAPTURE, roles, SCORING) == {G1: 20, G2: 5}


def test_survival_awards_cop_and_thief():
    roles = {G1: Role.POLICE, G2: Role.THIEF}
    assert score_subgame(RESULT_SURVIVAL, roles, SCORING) == {G1: 5, G2: 10}


def test_role_string_values_also_score():
    roles = {G1: "police", G2: "thief"}
    assert score_subgame(RESULT_CAPTURE, roles, SCORING) == {G1: 20, G2: 5}


def test_technical_outcome_scores_zero():
    roles = {G1: Role.POLICE, G2: Role.THIEF}
    assert score_subgame("timeout", roles, SCORING) == {G1: 0, G2: 0}


def test_aggregate_sums_and_picks_winner():
    subgames = [{G1: 20, G2: 5}, {G1: 5, G2: 10}]  # roles alternate
    result = aggregate(subgames, tie_score=2)
    assert result["total_score"] == {G1: 25, G2: 15}
    assert result["winner_group"] == G1
    assert result["series_tie"] is False
    assert result["sub_games_won"] == {G1: 1, G2: 1}
    assert result["ties"] == 0


def test_aggregate_applies_tie_rule_on_equal_totals():
    subgames = [{G1: 20, G2: 5}, {G1: 5, G2: 20}]  # 25 each
    result = aggregate(subgames, tie_score=2)
    assert result["total_score"] == {G1: 27, G2: 27}
    assert result["winner_group"] is None
    assert result["series_tie"] is True


def test_aggregate_counts_tied_subgames():
    subgames = [{G1: 7, G2: 7}, {G1: 10, G2: 3}]
    result = aggregate(subgames, tie_score=2)
    assert result["ties"] == 1
    assert result["sub_games_won"] == {G1: 1, G2: 0}
    assert result["winner_group"] == G1


def test_aggregate_skips_empty_subgame():
    result = aggregate([{}, {G1: 5, G2: 0}], tie_score=2)
    assert result["total_score"] == {G1: 5, G2: 0}
    assert result["ties"] == 0
    assert result["winner_group"] == G1
