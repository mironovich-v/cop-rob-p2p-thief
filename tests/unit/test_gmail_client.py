"""Unit tests for the raw-HTTPS Gmail client (Stage 7.3b): MIME body fidelity and
credential parsing. No network — build_raw is pure and creds come from dicts."""

import base64
import email
import email.policy

from cop_thief_core.infra.gmail_client import build_raw, credentials_from_dicts

BODY = '{"game_uid":"u1","תוצאה":"לכידה"}'  # canonical body with Hebrew


def test_build_raw_preserves_exact_body_bytes():
    raw = build_raw("rmisegal@example.com", "vm__fabi report", BODY)
    decoded = base64.urlsafe_b64decode(raw)
    message = email.message_from_bytes(decoded, policy=email.policy.default)
    assert message["To"] == "rmisegal@example.com"
    assert message["Subject"] == "vm__fabi report"
    # after MIME decode the content is exactly the body (set_content adds one newline)
    assert message.get_content().strip() == BODY
    assert "לכידה" in message.get_content()  # Hebrew round-trips, never escaped


def test_credentials_prefer_token_then_app_block():
    cred_data = {"installed": {"client_id": "APP_ID", "client_secret": "APP_SECRET",
                               "token_uri": "https://oauth2.example/token"}}
    creds = credentials_from_dicts(cred_data, {"refresh_token": "R1"})
    assert (creds.client_id, creds.client_secret) == ("APP_ID", "APP_SECRET")
    assert creds.refresh_token == "R1"
    assert creds.token_uri == "https://oauth2.example/token"


def test_credentials_token_overrides_app_identity():
    cred_data = {"web": {"client_id": "APP_ID", "client_secret": "APP_SECRET"}}
    token_data = {"client_id": "TOK_ID", "client_secret": "TOK_SECRET", "refresh_token": "R2"}
    creds = credentials_from_dicts(cred_data, token_data)
    assert (creds.client_id, creds.client_secret) == ("TOK_ID", "TOK_SECRET")
