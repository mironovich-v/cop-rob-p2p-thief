"""Raw-HTTPS Gmail send-only client — no third-party dependencies.

All network I/O goes through an injected ``http`` callable (a thin urllib default),
so tests never hit the network or need credentials. Send-only surface: refresh an
access token, then create a draft (default) or send one message. Nothing else.

``http(url, data, headers, timeout) -> (status:int, text:str)``.
"""

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from email.message import EmailMessage

from cop_thief_core.exceptions import ProviderError

TOKEN_URI = "https://oauth2.googleapis.com/token"
SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
_OK_STATUS = (200, 201)


@dataclass
class GmailCredentials:
    """Send-only OAuth: a long-lived refresh token + its client app identity."""

    client_id: str
    client_secret: str
    refresh_token: str
    token_uri: str = TOKEN_URI


def credentials_from_dicts(cred_data: dict, token_data: dict) -> GmailCredentials:
    """Parse Google's ``credentials.json`` (installed/web block) + a ``token.json``
    holding the authorized refresh token. Pure — file reads happen in the caller."""
    app = cred_data.get("installed") or cred_data.get("web") or cred_data
    return GmailCredentials(
        client_id=token_data.get("client_id") or app["client_id"],
        client_secret=token_data.get("client_secret") or app["client_secret"],
        refresh_token=token_data["refresh_token"],
        token_uri=app.get("token_uri", TOKEN_URI),
    )


def build_raw(to: str, subject: str, body: str, attachment_name: str | None = None) -> str:
    """base64url of a UTF-8 MIME message whose decoded content is exactly ``body``.

    With ``attachment_name``, the SAME bytes also ride as the single named
    attachment — rule 34's two readings (text body / JSON file), both satisfied
    with one construction (kit SPEC §6.1); never a re-serialization."""
    message = EmailMessage()
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    if attachment_name:
        message.add_attachment(
            body.encode("utf-8"), maintype="application", subtype="json",
            filename=attachment_name)
    return base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")


def _urllib_http(url, data, headers, timeout):  # pragma: no cover (real network)
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise ProviderError(f"gmail transport error: {exc}") from exc


def _post_form(url, fields, http, timeout) -> dict:
    data = urllib.parse.urlencode(fields).encode()
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    status, text = http(url, data, headers, timeout)
    if status not in _OK_STATUS:
        raise ProviderError(f"gmail token endpoint {status}: {text[:200]}")
    return json.loads(text)


def _post_json(url, token, obj, http, timeout) -> dict:
    data = json.dumps(obj).encode()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    status, text = http(url, data, headers, timeout)
    if status not in _OK_STATUS:
        raise ProviderError(f"gmail api {status}: {text[:200]}")
    return json.loads(text)


def fetch_access_token(creds: GmailCredentials, http, timeout) -> str:
    payload = _post_form(creds.token_uri, {
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "refresh_token": creds.refresh_token,
        "grant_type": "refresh_token",
    }, http, timeout)
    token = payload.get("access_token")
    if not token:
        raise ProviderError("gmail token response missing access_token")
    return token


def deliver(creds: GmailCredentials, raw: str, http, timeout) -> dict:
    """Refresh a token, then SEND. Send-only by design (ADR-20): rule 30's
    send-only scope cannot create drafts, so no draft path exists to misuse."""
    token = fetch_access_token(creds, http, timeout)
    return _post_json(SEND_URL, token, {"raw": raw}, http, timeout)
