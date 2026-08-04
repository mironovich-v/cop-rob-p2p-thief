"""Unit tests for EmailSender (Stage 7.3b): disabled/draft safety gates, gatekeeper
routing, and structured failure. A FakeHttp records calls so no real mail is sent."""

import pytest

from cop_thief_core.infra.email_sender import EmailSender
from cop_thief_core.infra.gmail_client import DRAFT_URL, SEND_URL, TOKEN_URI, GmailCredentials

CREDS = GmailCredentials("cid", "secret", "refresh")


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


def test_disabled_is_a_noop(police_config):
    http = FakeHttp([])
    sender = EmailSender(police_config, credentials=CREDS, http=http)
    assert sender.send_report("body", "subj") == {"sent": False, "reason": "disabled"}
    assert http.calls == []  # nothing left the machine


def test_draft_is_created_by_default(police_config):
    police_config.override("email.enabled", True)
    http = FakeHttp([(200, '{"access_token":"AT"}'), (200, '{"id":"draft123"}')])
    sender = EmailSender(police_config, credentials=CREDS, http=http)
    result = sender.send_report("body", "subj")
    assert result == {"sent": True, "mode": "draft", "id": "draft123"}
    assert http.calls == [TOKEN_URI, DRAFT_URL]  # token refresh then DRAFT (never send)


def test_send_mode_hits_the_send_endpoint(police_config):
    police_config.override("email.enabled", True)
    police_config.override("email.mode", "send")
    http = FakeHttp([(200, '{"access_token":"AT"}'), (200, '{"id":"msg1"}')])
    sender = EmailSender(police_config, credentials=CREDS, http=http)
    result = sender.send_report("body", "subj")
    assert result["mode"] == "send"
    assert http.calls == [TOKEN_URI, SEND_URL]


def test_transport_failure_returns_structured_reason(police_config):
    police_config.override("email.enabled", True)
    http = FakeHttp([(500, "boom"), (500, "boom")])  # email max_retries = 2
    sender = EmailSender(police_config, credentials=CREDS, http=http)
    result = sender.send_report("body", "subj")
    assert result["sent"] is False
    assert "500" in result["reason"]
    assert len(http.calls) == 2  # gatekeeper retried, then gave up


def test_no_credentials_skips_send(police_config):
    police_config.override("email.enabled", True)
    sender = EmailSender(police_config, credentials=None, http=FakeHttp([]))
    assert sender.send_report("body", "subj") == {"sent": False, "reason": "no_credentials"}
