"""Wire the four JSON artifact builders to disk for a whole series.

`emit_series` writes ONE declaration + result and a per-sub-game config + log,
all named from the shared game_id, and returns the result dict (for emailing).
Per-group scores come from `domain.scoring`; the two peers derive identical
sub-game outcomes (same roles/result/scores), so their result files agree.

Each peer writes into its OWN `<logs_dir>/<group_id>/` subfolder: game_id is
shared and roles alternate, so group_id is the stable per-peer discriminator that
keeps both peers' files from colliding on one machine. Files are written human-
readable (indent=2); the byte-exact emailed body is derived separately (Stage 7.3).
"""

import json
from pathlib import Path

from cop_thief_core.constants import RESULT_DISPUTED
from cop_thief_core.domain import scoring
from cop_thief_core.reporting.artifact_helpers import ended_at, log_filename
from cop_thief_core.reporting.artifact_schemas import DEFAULT_TIMEZONE
from cop_thief_core.reporting.artifacts import (
    build_config_artifact,
    build_declaration,
    build_log,
    build_result,
    config_filename,
    declaration_filename,
    result_filename,
)
from cop_thief_core.reporting.report_writer import consensus_signature


def _write(logs_dir: Path, filename: str, data: dict) -> Path:
    logs_dir.mkdir(parents=True, exist_ok=True)
    path = logs_dir / filename
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _roles(own_gid: str, opp_gid: str, own_role: str) -> dict:
    opp_role = "thief" if own_role == "police" else "police"
    return {own_gid: own_role, opp_gid: opp_role}


def _subgame_entry(summary, game_id, own_gid, opp_gid, scoring_cfg) -> dict:
    """One sub-game's row in the result: roles, outcome, per-group score, audit."""
    roles = _roles(own_gid, opp_gid, summary["role"])
    number = summary["sub_game_number"]
    score = scoring.score_subgame(summary["result"], roles, scoring_cfg)
    winner = next((gid for gid, role in roles.items() if role == summary["winner"]), None)
    passed = summary["audit"]["passed"]
    return {
        "sub_game_number": number,
        "roles": roles,
        "started_at": summary["started_at"],
        "ended_at": ended_at(summary["started_at"], summary["duration_seconds"]),
        "result": summary["result"],
        "winner_group": winner,
        # A disputed/technical row has no winner but is NOT a tie (playbook shape:
        # winner_group null, tie false); only a genuinely tied outcome sets tie.
        "tie": winner is None and summary["result"] not in (RESULT_DISPUTED,),
        "tokens": {own_gid: summary["tokens_total"], opp_gid: 0},
        "score": score,
        "log_files": {own_gid: f"{own_gid}/{log_filename(game_id, number)}",
                      opp_gid: f"{opp_gid}/{log_filename(game_id, number)}"},
        "audit": {"log_verified": passed, "tampered": not passed},
    }


def _symmetric(game_id: str, agg: dict, sub_games: list) -> dict:
    """The BYTE-IDENTICAL cross-peer outcome — no per-peer tokens or timestamps, so
    both peers' mutual signatures match. Roles/result/score/aggregate only."""
    return {
        "game_id": game_id,
        "aggregate": agg,
        "sub_games": [{"sub_game_number": sg["sub_game_number"], "roles": sg["roles"],
                       "result": sg["result"], "winner_group": sg["winner_group"],
                       "score": sg["score"]} for sg in sub_games],
    }


def emit_series(config, logs_dir, series) -> dict:
    """Write all four artifacts for `series` and return the result dict."""
    own = series.own_identity
    opp = series.peer_identity or own
    own_gid = own.get("group_id", "unknown-group")
    opp_gid = opp.get("group_id", "unknown-opponent")
    game_id = series.game_id or f"{own_gid}-vs-{opp_gid}"
    game_uid = series.game_uid or "0"
    scoring_cfg = config.get("scoring")
    max_tokens = config.shared.get("network_and_league", {}).get("token_budget_per_series")
    summaries = series.summaries
    first, last = summaries[0], summaries[-1]
    own_dir = Path(logs_dir) / own_gid

    _write(own_dir, declaration_filename(game_id), build_declaration(
        game_id, game_uid, DEFAULT_TIMEZONE, first["started_at"],
        ended_at(last["started_at"], last["duration_seconds"]),
        len(summaries), max_tokens, own, opp))

    sub_games = []
    for summary in summaries:
        number = summary["sub_game_number"]
        _write(own_dir, config_filename(game_id, number),
               build_config_artifact(config.shared, game_id, game_uid, number))
        _write(own_dir, log_filename(game_id, number),
               build_log(summary, game_id, game_uid, own_gid, opp_gid))
        sub_games.append(_subgame_entry(summary, game_id, own_gid, opp_gid, scoring_cfg))

    agg = scoring.aggregate([sg["score"] for sg in sub_games], scoring_cfg["tie_score"])
    mutual = consensus_signature(_symmetric(game_id, agg, sub_games))
    result = build_result(game_id, game_uid, sorted([own_gid, opp_gid]), sub_games, agg, mutual)
    _write(own_dir, result_filename(game_id), result)
    return result
