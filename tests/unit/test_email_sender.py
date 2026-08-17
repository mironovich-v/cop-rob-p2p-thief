"""EmailSender under ADR-20: disabled/dry-run defaults, the structural
recipient gate (lecturer unreachable unless armed), gatekeeper routing, and
structured failure. A FakeHttp records calls so no real mail is sent."""

import pytest

from cop_thief_core.exceptions import SimulationError
from cop_thief_core.infra.email_sender import EmailSender
from cop_thief_core.infra.gmail_client import SEND_URL, TOKEN_URI, GmailCredentials

CREDS = GmailCredentials("cid", "secret", "refresh")
LECTURER = "rmisegal+uoh26finalgame@gmail.com"


class FakeHttp:
    """Scripted (status, text) responses; records every call."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def __call__(self, url, data, headers, timeout):
        self.calls.append(url)
        return self._responses.pop(0)


@pytest.fixture(autouse=True)
def _no_secret_env(monkeypatch):
    monkeypatch.delenv("GMAIL_CREDENTIALS_PATH", raising=False)
    monkeypatch.delenv("GMAIL_TOKEN_PATH", raising=False)


def _sender(config, http, creds=CREDS, **overrides):
    config.override("email.enabled", True)
    config.override("email.recipient", "friendly@example.com")
    for key, value in overrides.items():
        config.override(key, value)
    return EmailSender(config, credentials=creds, http=http)


def test_disabled_is_a_noop(police_config):
    http = FakeHttp([])
    police_config.override("email.enabled", False)
    sender = EmailSender(police_config, credentials=CREDS, http=http)
    assert sender.send_report("body", "subj") == {"sent": False, "reason": "disabled"}
    assert http.calls == []  # nothing left the machine


def test_dry_run_is_the_default_and_needs_no_credentials(police_config):
    http = FakeHttp([])
    sender = _sender(police_config, http, creds=None)
    result = sender.send_report("body", "subj")
    assert result["sent"] is False
    assert result["mode"] == "dry_run"
    assert result["to"] == "friendly@example.com"
    assert http.calls == []  # dry run builds the MIME, transport untouched


def test_send_mode_hits_the_send_endpoint_only(police_config):
    http = FakeHttp([(200, '{"access_token":"AT"}'), (200, '{"id":"msg1"}')])
    sender = _sender(police_config, http, **{"email.mode": "send"})
    result = sender.send_report("body", "subj")
    assert result == {"sent": True, "mode": "send", "id": "msg1"}
    assert http.calls == [TOKEN_URI, SEND_URL]  # a draft endpoint no longer exists


def test_lecturer_is_unreachable_unarmed_even_in_send_mode(police_config):
    http = FakeHttp([])
    sender = _sender(police_config, http, **{
        "email.mode": "send", "email.recipient": f"  {LECTURER.upper()}  ",
        "email.lecturer_address": LECTURER})
    result = sender.send_report("body", "subj")
    assert result == {"sent": False, "reason": "lecturer_unreachable_unarmed"}
    assert http.calls == []  # structural refusal, case/whitespace-insensitive


def test_lecturer_hidden_in_a_recipient_list_is_still_blocked(police_config):
    http = FakeHttp([])
    sender = _sender(police_config, http, **{
        "email.mode": "send",
        "email.recipient": ["us@example.com", f" {LECTURER} "],
        "email.lecturer_address": LECTURER})
    assert sender.send_report("b", "s")["reason"] == "lecturer_unreachable_unarmed"


def test_armed_counted_run_reaches_the_lecturer(police_config):
    http = FakeHttp([(200, '{"access_token":"AT"}'), (200, '{"id":"m2"}')])
    sender = _sender(police_config, http, **{
        "email.mode": "send", "email.recipient": LECTURER,
        "email.lecturer_address": LECTURER})
    result = sender.send_report("body", "subj", armed=True)
    assert result["sent"] is True


def test_no_credentials_skips_send_mode(police_config):
    sender = _sender(police_config, FakeHttp([]), creds=None, **{"email.mode": "send"})
    assert sender.send_report("b", "s") == {"sent": False, "reason": "no_credentials"}


def test_transport_failure_returns_structured_reason(police_config):
    http = FakeHttp([(500, "boom"), (500, "boom")])  # email max_retries = 2
    sender = _sender(police_config, http, **{"email.mode": "send"})
    result = sender.send_report("body", "subj")
    assert result["sent"] is False
    assert "500" in result["reason"]
    assert len(http.calls) == 2  # gatekeeper retried, then gave up


def test_armed_preflight_refuses_a_run_that_cannot_deliver(police_config):
    # An armed counted run that owes a report refuses to START with nowhere
    # to send it (WARNINGS §3 / playbook Stage 0).
    sender = _sender(police_config, FakeHttp([]))  # mode dry_run: cannot deliver
    with pytest.raises(SimulationError, match="armed"):
        sender.preflight_armed()
    sender2 = _sender(police_config, FakeHttp([]), **{"email.mode": "send"})
    sender2.preflight_armed()  # deliverable: enabled + send + recipient + creds
    sender3 = _sender(police_config, FakeHttp([]), creds=None, **{"email.mode": "send"})
    with pytest.raises(SimulationError, match="credentials"):
        sender3.preflight_armed()
