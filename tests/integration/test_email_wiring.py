"""Stage 7.7a: the SDK wires the email step after a series. By default it is
disabled (no send); when an enabled EmailSender is injected, the EXACT report_body
bytes reach the Gmail draft. Two peers play over the in-process FakeTransport."""

import base64
import email
import email.policy
import json
import threading
from pathlib import Path

from cop_thief_core.infra.email_sender import EmailSender
from cop_thief_core.infra.gmail_client import GmailCredentials
from cop_thief_core.interop.negotiation import terms_from_config
from cop_thief_core.reporting.report_builder import build_report, report_body
from cop_thief_core.sdk import SimulationSdk

REPO_ROOT = Path(__file__).resolve().parents[2]


class _CaptureHttp:
    def __init__(self):
        self.raw = None

    def __call__(self, url, data, headers, timeout):
        if "drafts" in url:
            self.raw = json.loads(data)["message"]["raw"]
            return 201, '{"id":"draft1"}'
        return 200, '{"access_token":"AT"}'


def _run(sdk, role, transport, out):
    out[role] = sdk.run_peer(role, transport=transport)


def _play(transport_pair, tmp_path, police_sdk_setup=None):
    thief_t, police_t = transport_pair
    thief_sdk = SimulationSdk(REPO_ROOT / "config" / "thief", workdir=tmp_path / "t")
    police_sdk = SimulationSdk(REPO_ROOT / "config" / "police", workdir=tmp_path / "p")
    if police_sdk_setup:
        police_sdk_setup(police_sdk)
    out: dict = {}
    threads = [threading.Thread(target=_run, args=(thief_sdk, "thief", thief_t, out)),
               threading.Thread(target=_run, args=(police_sdk, "police", police_t, out))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
        assert not thread.is_alive()
    return out, police_sdk


def test_email_disabled_by_default(transport_pair, tmp_path):
    out, _ = _play(transport_pair, tmp_path)
    assert out["police"]["email"] == {"sent": False, "reason": "disabled"}
    assert out["thief"]["email"] == {"sent": False, "reason": "disabled"}


def test_injected_sender_drafts_the_exact_report_body(transport_pair, tmp_path):
    http = _CaptureHttp()

    def setup(sdk):
        sdk.config.override("email.enabled", True)
        sdk.email_sender = EmailSender(
            sdk.config, credentials=GmailCredentials("c", "s", "r"), http=http)

    out, police_sdk = _play(transport_pair, tmp_path, setup)
    assert out["police"]["email"] == {"sent": True, "mode": "draft", "id": "draft1"}
    # the drafted MIME body decodes to EXACTLY report_body(build_report(final summary))
    decoded = email.message_from_bytes(
        base64.urlsafe_b64decode(http.raw), policy=email.policy.default)
    expected = report_body(build_report(
        out["police"]["summaries"][-1], terms_from_config(police_sdk.config)))
    assert decoded.get_content().strip() == expected
