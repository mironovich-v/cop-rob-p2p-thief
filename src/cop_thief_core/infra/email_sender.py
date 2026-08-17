"""Send the match report via raw-HTTPS Gmail, through the ApiGatekeeper.

Safety gates (ADR-20; kit WARNINGS §3/§6): **disabled by default**; when
enabled, **dry-run by default** (build the exact MIME, transport untouched).
Rule 30's send-only scope cannot create drafts, so no draft gate exists —
instead the gate is structural and recipient-shaped: the lecturer's address is
UNREACHABLE (matched case-/whitespace-insensitively, including inside recipient
lists) unless the run is doubly armed, and an armed run that cannot deliver its
report refuses to START. Under the diversity rule only the first meeting with an
opponent counts, so an accidental early send can burn the one scored game. The
Gmail service is injected, so tests never send real mail or need credentials.
"""

import json
import os
from pathlib import Path

from cop_thief_core.exceptions import ProviderError, SimulationError
from cop_thief_core.infra.gmail_client import _urllib_http as _default_http
from cop_thief_core.infra.gmail_client import (
    build_raw,
    credentials_from_dicts,
    deliver,
)
from cop_thief_core.shared.gatekeeper import ApiGatekeeper


def _normalize(address: str) -> str:
    return str(address).strip().lower()


class EmailSender:
    """Auto-fires the report at settlement (rule 32) behind the structural gate."""

    def __init__(self, config, credentials=None, http=None, clock=None):
        self._config = config
        self._credentials = credentials
        self._http = http or _default_http
        self._gatekeeper = ApiGatekeeper(config, service="email", clock=clock)

    def _recipients(self) -> list[str]:
        value = self._config.get("email.recipient")
        if not value:
            return []
        return list(value) if isinstance(value, list | tuple) else [value]

    def _lecturer_among(self, recipients: list[str]) -> bool:
        lecturer = self._config.get("email.lecturer_address", "")
        return bool(lecturer) and _normalize(lecturer) in {
            _normalize(address) for address in recipients
        }

    def send_report(self, body: str, subject: str,
                    attachment_name: str | None = None, armed: bool = False) -> dict:
        """Deliver ``body`` (already the exact canonical bytes) as body+attachment.

        Returns a structured result — never raises — so a transport failure can
        never crash a finished match.
        """
        if not self._config.get("email.enabled", False):
            return {"sent": False, "reason": "disabled"}
        recipients = self._recipients()
        if not recipients:
            return {"sent": False, "reason": "no_recipient"}
        if self._lecturer_among(recipients) and not armed:
            return {"sent": False, "reason": "lecturer_unreachable_unarmed"}
        to = ", ".join(recipients)
        raw = build_raw(to, subject, body, attachment_name)
        mode = self._config.get("email.mode", "dry_run")
        if mode != "send":
            return {"sent": False, "mode": "dry_run", "to": to, "raw_len": len(raw)}
        creds = self._credentials or self._load_credentials()
        if creds is None:
            return {"sent": False, "reason": "no_credentials"}
        timeout = self._config.get("email.timeout_seconds")
        try:
            result = self._gatekeeper.execute(deliver, creds, raw, self._http, timeout)
            return {"sent": True, "mode": mode, "id": result.get("id")}
        except ProviderError as exc:
            return {"sent": False, "reason": str(exc)}

    def preflight_armed(self) -> None:
        """An ARMED counted run that owes a report refuses to start with nowhere
        to send it (kit WARNINGS §3; playbook Stage 0). Raises SimulationError."""
        if not (self._credentials or self._load_credentials()):
            raise SimulationError("armed counted run: Gmail credentials missing")
        if not (
            self._config.get("email.enabled", False)
            and self._config.get("email.mode", "dry_run") == "send"
            and self._recipients()
        ):
            raise SimulationError(
                "armed counted run cannot deliver its report — require "
                "email.enabled=true, email.mode='send', and a recipient"
            )

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
