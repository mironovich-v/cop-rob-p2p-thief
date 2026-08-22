"""Shared, pure helpers for the artifact builders: game_id-derived filenames, the
`links` block, canonical hashing, the declaration's hardware/group blocks, and
ended-at derivation. No I/O.
"""

import hashlib
import json
from datetime import datetime, timedelta

from cop_thief_core.reporting.artifact_schemas import LINKS_REMARK
from cop_thief_core.reporting.report_writer import consensus_signature


def declaration_filename(game_id: str) -> str:
    return f"declaration_{game_id}.json"


def config_filename(game_id: str, sub_game_number: int) -> str:
    return f"config_{game_id}_g{sub_game_number:02d}.json"


def log_filename(game_id: str, sub_game_number: int) -> str:
    return f"log_{game_id}_g{sub_game_number:02d}.json"


def result_filename(game_id: str) -> str:
    return f"result_{game_id}.json"


def links(game_id: str, github: dict | None = None) -> dict:
    """Shared links block: logical role -> filename. Per-sub-game files keep the
    literal g<NN> placeholder because the sub_game_number varies per file. The
    result also carries ``github`` (rule 49): BOTH teams' repo URLs — how the
    grader reaches the repo-published declaration/configs/logs (never mailed)."""
    block = {
        "_remark": LINKS_REMARK,
        "declaration": declaration_filename(game_id),
        "config": f"config_{game_id}_g<NN>.json",
        "log": f"log_{game_id}_g<NN>.json",
        "result": result_filename(game_id),
    }
    if github is not None:
        block["github"] = github
    return block


def canonical_sha256(data) -> str:
    """Compact canonical JSON hash — the config lock (byte-identical across teams)."""
    blob = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()


def ended_at(started_at: str, duration_seconds: float) -> str:
    """started_at (ISO, tz-aware) + duration -> ISO ended_at; echo input if unparsable."""
    try:
        start = datetime.fromisoformat(started_at)
    except (TypeError, ValueError):
        return started_at
    return (start + timedelta(seconds=duration_seconds)).isoformat()


def hardware_spec(spec: dict) -> dict:
    """Exactly the six book hardware fields."""
    return {field: spec.get(field) for field in
            ("cpu_type", "cpu_freq_mhz", "cpu_cores", "ram_gb", "gpu_model", "vram_gb")}


def group_block(identity: dict) -> dict:
    """One team's static declaration block, self-signed (consensus over the block
    before its signature is inserted). A FOREIGN identity block may lack any key
    (the sparring peer sends no ``spec``; a live opponent's block once arrived
    empty for whole windows) — degrade to explicit placeholders, never crash a
    settled series at the artifact step."""
    block = {
        "group_id": identity.get("group_id", "unknown-group"),
        "group_name": identity.get("group_name", "unknown"),
        "members": identity.get("members", []),
        "repos": identity.get("repos", {}),
        "mcp_servers": identity.get("mcp_servers", {}),
        "llm_model": identity.get("llm_model", "undeclared"),
        "hardware_spec": hardware_spec(identity.get("spec") or {}),
        # Commit traceability: the wire identity declares it, but until now it
        # never reached an artifact, so a grader holding only the submitted
        # repos could not tie a result to code. A foreign block may omit it.
        "github_commit": identity.get("github_commit"),
    }
    block["signature"] = consensus_signature(block)
    return block


def tokens_series(sub_games: list, group_ids) -> dict:
    return {gid: sum(sg.get("tokens", {}).get(gid, 0) for sg in sub_games) for gid in group_ids}
