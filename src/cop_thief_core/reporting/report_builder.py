"""Build the official Hebrew match report a peer emails to the lecturer (book ch.8).

Rich, per-peer, and audit-verified: each team emails its OWN report, self-signed
with the consensus key (`report_writer.sign_report`). The emailed BODY is the exact
hashed canonical bytes — spaced ``json.dumps(..., sort_keys=True, ensure_ascii=False)``,
never a pretty-printed re-serialization (league SPEC §6; CLAUDE.md §36.3.5). Totals
are DERIVED from the sealed summary, never trusted from a claim.
"""

import json

from cop_thief_core.reporting.report_writer import sign_report
from cop_thief_core.shared.version import CODE_VERSION

_RESULT_HEBREW = {
    "capture": "לכידה",
    "survival": "הישרדות",
    "timeout": "תוצאה_טכנית",
    "tamper_forfeit": "פסילת_זיוף",
    "stopped": "הופסק",
}


def _spec_declaration(summary: dict) -> dict:
    """Hardware + model + token declaration from the sealed step-0 system_spec record
    (so the declaration is audit-verified like every move)."""
    spec_payload = next(
        (record["payload"] for record in summary.get("records", [])
         if record["payload"].get("type") == "system_spec"), {})
    return {
        "מפרט_מחשב": spec_payload.get("spec", {}),
        "דגם_שפה_בשימוש": spec_payload.get("model", "unknown"),
        "גרסת_קוד": spec_payload.get("code_version", CODE_VERSION),
        "סך_טוקנים_שנצרכו": summary.get("tokens_total", 0),
    }


def _step_log(summary: dict) -> list[dict]:
    """The received messages in the book's verified step-log shape."""
    return [
        {
            "מספר_צעד": message["step"],
            "טביעת_זמן": message["timestamp"],
            "שולח": message["sender"],
            "רמז_מילולי_שנשלח": message["hint"],
            "גריד_ריח_מצורף": message["smell_grid"],
            "מחסום_שהוצב": message["barrier_placed"],
            "חתימת_מצב": message["commit"],
        }
        for message in summary.get("history", [])
    ]


def build_report(summary: dict, terms: dict) -> dict:
    """The official report from THIS peer's perspective (audit-verified), signed
    with the consensus key (sign-then-insert)."""
    report = {
        "סוג_דוח": "משחק_ליגה_רשמי",
        "גרסת_קוד": CODE_VERSION,
        "תפקיד_מדווח": summary["role"],
        "קבוצה_מדווחת": summary.get("group_name", "unnamed"),
        "מספר_משחקון": summary.get("sub_game_number", 1),
        "זמן_התחלה": summary.get("started_at", ""),
        "משך_משחק_שניות": summary.get("duration_seconds", 0),
        "הצהרת_מפרט_מחשב_וטוקנים": _spec_declaration(summary),
        "תוצאה": _RESULT_HEBREW.get(summary["result"], summary["result"]),
        "מנצח": summary["winner"],
        "צעדים_שבוצעו": summary["steps"],
        "הסכם_תפאורה_משא_ומתן": terms,
        "אימות_קריפטוגרפי": {
            "צעדים_מאומתים": summary["audit"]["verified_steps"],
            "צעדים_שנכשלו": summary["audit"]["failed_steps"],
        },
        "לוג_צעדים_מאומת": _step_log(summary),
        "הצהרות_חתומות_שלי": summary["records"],
        "הסכמה_הדדית": summary["audit"]["passed"],
    }
    return sign_report(report)


def report_body(signed_report: dict) -> str:
    """The EXACT bytes to email: spaced canonical JSON (the consensus preimage form),
    never indent=2. A verifier pops the signature key and re-hashes this exact form."""
    return json.dumps(signed_report, sort_keys=True, ensure_ascii=False)
