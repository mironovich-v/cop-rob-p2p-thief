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
from cop_thief_core.sdk import SimulationSdk

REPO_ROOT = Path(__file__).resolve().parents[2]


class _CaptureHttp:
    def __init__(self):
        self.raw = None

    def __call__(self, url, data, headers, timeout):
        if "send" in url:
            self.raw = json.loads(data)["raw"]
            return 200, '{"id":"sent1"}'
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


def test_friendly_send_autofires_exact_bytes_as_body_and_attachment(transport_pair, tmp_path):
    # imreeyal's gate: the friendly report arrives from OUR filer, auto-fired at
    # settlement — body AND identical named attachment, reference subject form.
    http = _CaptureHttp()

    def setup(sdk):
        sdk.config.override("email.enabled", True)
        sdk.config.override("email.mode", "send")
        sdk.config.override("email.recipient", "imreeyal.copthief@example.com")
        sdk.email_sender = EmailSender(
            sdk.config, credentials=GmailCredentials("c", "s", "r"), http=http)

    out, police_sdk = _play(transport_pair, tmp_path, setup)
    assert out["police"]["email"] == {"sent": True, "mode": "send", "id": "sent1"}
    decoded = email.message_from_bytes(
        base64.urlsafe_b64decode(http.raw), policy=email.policy.default)
    # SPEC §6.1 result-only mail: the body is the FILED result artifact bytes.
    expected = json.dumps(out["police"]["report"], ensure_ascii=False, indent=2)
    filed = (Path(police_sdk._workdir) / "logs"
             / out["police"]["own_identity"]["group_id"]
             / f"result_{out['police']['game_id']}.json").read_text("utf-8")
    assert expected == filed  # mail bytes == the repo-filed artifact
    winner = out["police"]["report"]["final_result"]["winner_group"] or "tie"
    assert decoded["Subject"] == (
        f"Police-Thief series result: winner {winner} (reported by "
        f"{out['police']['summaries'][-1]['role']})")
    assert decoded.get_body(preferencelist=("plain",)).get_content().strip() == expected
    attachment = next(decoded.iter_attachments())
    assert attachment.get_filename() == f"result_{out['police']['game_id']}.json"
    assert attachment.get_content().decode("utf-8") == expected  # body == attachment


def test_counted_arming_mismatch_refuses_to_start(tmp_path):
    import pytest

    from cop_thief_core.exceptions import SimulationError
    sdk = SimulationSdk(REPO_ROOT / "config" / "police", workdir=tmp_path)
    with pytest.raises(SimulationError, match="arming mismatch"):
        sdk.run_peer("police", counted=True)  # CLI armed, config not — refuse


def test_armed_run_without_delivery_path_refuses_to_start(tmp_path):
    import pytest

    from cop_thief_core.exceptions import SimulationError
    sdk = SimulationSdk(REPO_ROOT / "config" / "police", workdir=tmp_path)
    sdk.config.override("game.counted", True)  # doubly armed…
    with pytest.raises(SimulationError):  # …but email cannot deliver: refuse early
        sdk.run_peer("police", counted=True)
