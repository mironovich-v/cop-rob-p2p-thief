"""Pure log-loading for the replay viewer: normalize a sealed sub-game log,
re-verify each record against its revealed nonce (the replay crypto audit), and
reconstruct BOTH true trajectories from the mutually-revealed logs.

Full truth (both positions) is legitimate ONLY here — in retrospective replay,
after the end-of-game reveal — never in the live view. No Tk; fully unit-tested.
"""

import json
import re
from pathlib import Path

from cop_thief_core.exceptions import CryptoError
from cop_thief_core.interop.hashing import verify

_SPEC_TYPE = "system_spec"


def verify_record(records: list, index: int) -> str:
    """Re-verify one sealed record against its revealed nonce (replay audit line)."""
    if index < 0 or index >= len(records):
        return "-"
    record = records[index]
    try:
        verify(record["payload"], record["nonce"], record["commit"])
        return "verified OK"
    except CryptoError:
        return "TAMPERED!"


def reconstruct_positions(records: list) -> list:
    """This peer's per-step true positions, revealed from its sealed step records
    (the step-0 system_spec record carries no position and is skipped)."""
    return [record["payload"]["position"]
            for record in records
            if record.get("payload", {}).get("type") != _SPEC_TYPE
            and "position" in record.get("payload", {})]


def normalize_log(log_data: dict) -> dict:
    """A uniform view over our standardized sub-game log (records at top level).
    Rebuilds the move trajectory from the sealed records; crypto re-verification
    runs regardless of whether a smell history is present."""
    summary = log_data.get("summary", {})
    records = log_data.get("records") or summary.get("records", [])
    return {
        "summary": summary,
        "records": records,
        "positions": reconstruct_positions(records),
        "role": summary.get("role", "-"),
        "result": summary.get("result", "-"),
        "winner": summary.get("winner_role") or summary.get("winner", "-"),
        "group": summary.get("group_id") or summary.get("group_name", "unnamed"),
        "opponent_group_id": summary.get("opponent_group_id"),
        "sub_game_number": summary.get("sub_game_number", 1),
        "duration_seconds": summary.get("duration_seconds", 0),
        "audit": summary.get("audit", {"passed": True}),
    }


def _game_id(log_data: dict) -> str:
    return log_data.get("game_id") or log_data.get("summary", {}).get("group_id", "")


def opponent_positions(log_path, log_data: dict) -> list:
    """Locate the opponent's sibling log (logs/<opponent_group_id>/log_<game_id>_gNN)
    and reconstruct its true positions, so playback can draw BOTH agents. Returns []
    when the sibling is unavailable (the belief heatmap still shows)."""
    if not log_path:
        return []
    view = normalize_log(log_data)
    opponent, game_id = view["opponent_group_id"], _game_id(log_data)
    sub = view["sub_game_number"]
    if not opponent or not game_id:
        return []
    sibling = Path(log_path).resolve().parent.parent / opponent / \
        f"log_{game_id}_g{sub:02d}.json"
    if not sibling.is_file():
        return []
    data = json.loads(sibling.read_text(encoding="utf-8"))
    return reconstruct_positions(data.get("records", []))


def discover_subgames(log_path, log_data: dict) -> list:
    """Sub-game numbers available beside this log (log_<game_id>_gNN.json)."""
    if not log_path:
        return []
    game_id = _game_id(log_data)
    found = []
    for path in Path(log_path).resolve().parent.glob(f"log_{game_id}_g*.json"):
        match = re.search(r"_g(\d+)\.json$", path.name)
        if match:
            found.append(int(match.group(1)))
    return sorted(found)


def subgame_log_path(log_path, log_data: dict, sub: int) -> Path:
    """Path to another sub-game's log in the same folder."""
    return Path(log_path).resolve().parent / f"log_{_game_id(log_data)}_g{sub:02d}.json"
