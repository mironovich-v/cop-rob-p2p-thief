"""A counted report is filed only for a complete, cleanly-audited series.

Rule 35's mutual-zero surface: an incomplete or unverified series is one NOBODY
should file, because two teams filing disagreeing reports of the same game is
the shape the league zeroes. vibecode's counted runbook withholds automatically
below 6/6 Verified OK; this is our equivalent, and it is deliberately armed-only
— a FRIENDLY report must still fire, because at least one partner's gate
requires a friendly report to arrive at settlement.
"""

from pathlib import Path
from types import SimpleNamespace

from cop_thief_core.sdk.filing import filable

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = {"final_result": {"winner_group": "vibecode"}}

PASS = {"passed": True, "verified_steps": 10, "failed_steps": []}
FAIL = {"passed": False, "verified_steps": 3, "failed_steps": [4]}
SKIPPED = {"passed": False, "verified_steps": 0, "failed_steps": [], "skipped": True}


def _summaries(count, audits=None):
    audits = audits or [PASS] * count
    return [{"sub_game_number": n + 1, "audit": audits[n], "result": "capture"}
            for n in range(count)]


def test_complete_and_clean_series_is_filable():
    ok, reason = filable(_summaries(6), expected=6)
    assert ok is True
    assert reason == ""


def test_short_series_is_withheld():
    """Four of six settled: the series never finished, so nobody files."""
    ok, reason = filable(_summaries(4), expected=6)
    assert ok is False
    assert "4" in reason and "6" in reason


def test_failed_audit_withholds_and_names_the_sub_game():
    audits = [PASS, PASS, FAIL, PASS, PASS, PASS]
    ok, reason = filable(_summaries(6, audits), expected=6)
    assert ok is False
    assert "3" in reason  # the operator must know WHICH sub-game to compare


def test_skipped_audit_withholds():
    """A timed-out sub-game has nothing to audit — that is not 'Verified OK'."""
    audits = [PASS] * 5 + [SKIPPED]
    ok, reason = filable(_summaries(6, audits), expected=6)
    assert ok is False


def test_a_disputed_capture_still_files():
    """SPEC §3.1: a voided corroboration is 'reported, never a unilateral
    rewrite — the logs decide'. The crypto audit passed, so the row is filed as
    disputed evidence rather than suppressed."""
    audits = [{**PASS, "capture_corroboration":
               {"kind": "concession", "corroborated": False, "note": "x"}}] + [PASS] * 5
    summaries = _summaries(6, audits)
    summaries[0]["result"] = "disputed_capture"
    ok, _ = filable(summaries, expected=6)
    assert ok is True


def test_no_sub_games_at_all_is_withheld():
    ok, reason = filable([], expected=6)
    assert ok is False
    assert reason


# --- wiring: the guard must sit on the ARMED send path only ------------------

class _Sender:
    def __init__(self):
        self.sent: list[str] = []

    def send_report(self, body, subject, attachment_name=None, armed=False):
        self.sent.append(subject)
        return {"sent": True}


def _sdk(tmp_path):
    from cop_thief_core.sdk import SimulationSdk
    sdk = SimulationSdk(REPO_ROOT / "config" / "vibecode", workdir=tmp_path)
    sdk.email_sender = _Sender()
    return sdk


def _ragged_series():
    summaries = _summaries(4)          # 4 of the signed 6
    summaries[-1]["role"] = "police"
    return SimpleNamespace(summaries=summaries, game_id="vibecode-vs-vm__fabi")


def test_armed_run_withholds_an_incomplete_series(tmp_path):
    sdk = _sdk(tmp_path)
    result = sdk._email_report(_ragged_series(), REPORT, armed=True)
    assert result["sent"] is False
    assert "withheld" in result["reason"]
    assert sdk.email_sender.sent == []   # nothing reached the lecturer


def test_friendly_still_sends_from_the_same_series(tmp_path):
    """Deliberate asymmetry: a partner gate requires a friendly report at
    settlement, and a friendly filing harms nobody."""
    sdk = _sdk(tmp_path)
    result = sdk._email_report(_ragged_series(), REPORT, armed=False)
    assert result["sent"] is True
    assert len(sdk.email_sender.sent) == 1
