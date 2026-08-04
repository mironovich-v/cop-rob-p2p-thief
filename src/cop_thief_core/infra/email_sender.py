"""Send the match report to the lecturer via raw-HTTPS Gmail, through the
ApiGatekeeper (service ``email``).

Safety gates (league SPEC §6): **disabled by default** and, when enabled,
**draft by default** — nothing reaches a real inbox until a deliberate human sets
``email.mode = "send"``. Under the diversity rule only the first meeting with an
opponent counts, so an accidental early send can burn the one scored game. The
Gmail service is injected, so tests never send real mail or need credentials.
"""

import json
import os
from pathlib import Path

from cop_thief_core.exceptions import ProviderError
from cop_thief_core.infra.gmail_client import _urllib_http as _default_http
from cop_thief_core.infra.gmail_client import (
    build_raw,
    credentials_from_dicts,
    deliver,
)
from cop_thief_core.shared.gatekeeper import ApiGatekeeper


class EmailSender:
    """Creates the report email as a Gmail draft (default) via the gatekeeper."""

    def __init__(self, config, credentials=None, http=None, clock=None):
        self._config = config
        self._credentials = credentials
        self._http = http or _default_http
        self._gatekeeper = ApiGatekeeper(config, service="email", clock=clock)

    def send_report(self, body: str, subject: str) -> dict:
        """Deliver ``body`` (already the exact canonical bytes) as draft/send.

        Returns a structured result — never raises — so a transport failure can
        never crash a finished match.
        """
        if not self._config.get("email.enabled", False):
            return {"sent": False, "reason": "disabled"}
        creds = self._credentials or self._load_credentials()
        if creds is None:
            return {"sent": False, "reason": "no_credentials"}
        mode = self._config.get("email.mode", "draft")
        raw = build_raw(self._config.get("email.recipient"), subject, body)
        timeout = self._config.get("email.timeout_seconds")
        try:
            result = self._gatekeeper.execute(deliver, creds, raw, mode, self._http, timeout)
            return {"sent": True, "mode": mode, "id": result.get("id")}
        except ProviderError as exc:
            return {"sent": False, "reason": str(exc)}

    def _load_credentials(self):
        """Load OAuth creds from the git-ignored secret files named in ``.env``.
        Returns None when unconfigured (the default in tests/CI) so sending skips."""
        cred_path = os.environ.get("GMAIL_CREDENTIALS_PATH")
        token_path = os.environ.get("GMAIL_TOKEN_PATH")
        if not cred_path or not token_path:
            return None
        cred_file, token_file = Path(cred_path), Path(token_path)
        if not (cred_file.is_file() and token_file.is_file()):
            return None
        return credentials_from_dicts(  # pragma: no cover (needs real secret files)
            json.loads(cred_file.read_text(encoding="utf-8")),
            json.loads(token_file.read_text(encoding="utf-8")),
        )
