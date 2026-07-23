"""Tests for the report consensus signature (PRD_interop_serialization, slice 6.3)."""

import hashlib
import json

from cop_thief_core.reporting.report_writer import (
    SIGNATURE_KEY,
    consensus_signature,
    sign_report,
    verify_report,
)


def test_sign_then_insert_roundtrip():
    signed = sign_report({"a": 1, "game_uid": "x"})
    assert SIGNATURE_KEY in signed
    assert verify_report(signed) is True


def test_verify_fails_on_tamper():
    signed = sign_report({"a": 1})
    signed["a"] = 2  # tamper after signing
    assert verify_report(signed) is False


def test_verify_fails_without_signature():
    assert verify_report({"a": 1}) is False


def test_uses_spaced_not_compact_form():
    report = {"b": 1, "a": 2}
    compact = hashlib.sha256(
        json.dumps(report, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    assert consensus_signature(report) != compact  # spaced form differs from compact
