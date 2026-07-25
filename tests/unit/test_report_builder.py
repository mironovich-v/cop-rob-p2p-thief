"""Unit tests for the official Hebrew emailed report (Stage 7.3a): schema, derived
totals, consensus self-signature, and the exact canonical email body bytes."""

import json

from cop_thief_core.reporting.report_builder import build_report, report_body
from cop_thief_core.reporting.report_writer import SIGNATURE_KEY, verify_report

TERMS = {"board_size": 7, "max_steps": 35}


def _summary():
    return {
        "role": "police",
        "group_name": "VM-Fabi",
        "sub_game_number": 2,
        "started_at": "2026-07-25T10:00:00+00:00",
        "duration_seconds": 8.0,
        "tokens_total": 1234,
        "result": "capture",
        "winner": "police",
        "steps": 6,
        "audit": {"passed": True, "verified_steps": 6, "failed_steps": []},
        "records": [
            {"payload": {"type": "system_spec", "spec": {"cpu_cores": 8},
                         "model": "cli-default", "code_version": "1.0.0"}},
        ],
        "history": [
            {"step": 1, "timestamp": "t1", "sender": "thief", "hint": "אני ליד הנמל",
             "smell_grid": {"4,2": 0.9}, "barrier_placed": None, "commit": "c1"},
        ],
    }


def test_report_has_schema_and_self_signature():
    report = build_report(_summary(), TERMS)
    assert report["סוג_דוח"] == "משחק_ליגה_רשמי"
    assert report["תוצאה"] == "לכידה"  # capture -> Hebrew
    assert report["הסכם_תפאורה_משא_ומתן"] == TERMS
    assert SIGNATURE_KEY in report
    assert verify_report(report) is True  # sign-then-insert round-trips


def test_spec_declaration_and_tokens_are_derived():
    report = build_report(_summary(), TERMS)
    decl = report["הצהרת_מפרט_מחשב_וטוקנים"]
    assert decl["מפרט_מחשב"] == {"cpu_cores": 8}  # from the sealed step-0 record
    assert decl["דגם_שפה_בשימוש"] == "cli-default"
    assert decl["סך_טוקנים_שנצרכו"] == 1234  # derived from the summary, not claimed


def test_step_log_maps_received_messages():
    report = build_report(_summary(), TERMS)
    step = report["לוג_צעדים_מאומת"][0]
    assert step["מספר_צעד"] == 1
    assert step["שולח"] == "thief"
    assert step["רמז_מילולי_שנשלח"] == "אני ליד הנמל"
    assert step["חתימת_מצב"] == "c1"


def test_report_body_is_exact_canonical_bytes():
    report = build_report(_summary(), TERMS)
    body = report_body(report)
    # spaced canonical, NOT pretty-printed (no newlines / indentation)
    assert "\n" not in body
    assert body == json.dumps(report, sort_keys=True, ensure_ascii=False)
    # Hebrew is preserved literally (ensure_ascii=False), never \uXXXX-escaped
    assert "אני ליד הנמל" in body
    # a recipient can parse it and verify the popped signature
    assert verify_report(json.loads(body)) is True


def test_non_ascii_body_is_not_escaped():
    body = report_body(build_report(_summary(), TERMS))
    assert "\\u05d0" not in body  # aleph would be א under ensure_ascii=True
