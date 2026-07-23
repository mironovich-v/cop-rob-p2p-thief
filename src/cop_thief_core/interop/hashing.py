"""SHA-256 commit / signature over canonical JSON — the reference/CORE form.

    commit = SHA256( canonical_json(payload) + "|" + nonce )

The nonce is pipe-appended to the canonical STRING (not inserted into the hashed
object). The book publishes two other, non-conforming constructions; this is the
one the league pins (SPEC §3). The same construction seals per-step records AND
signs the pre-game terms.
"""

import hashlib
import secrets
from typing import Any

from cop_thief_core.constants import NONCE_BYTES
from cop_thief_core.exceptions import CryptoError
from cop_thief_core.interop.canonical import canonical_json


def commit_of(payload: Any, nonce: str) -> str:
    return hashlib.sha256(f"{canonical_json(payload)}|{nonce}".encode()).hexdigest()


def new_nonce() -> str:
    return secrets.token_hex(NONCE_BYTES)


def seal(payload: Any) -> dict:
    """Generate a fresh nonce and its commit for a payload: {'nonce', 'commit'}."""
    nonce = new_nonce()
    return {"nonce": nonce, "commit": commit_of(payload, nonce)}


def verify(payload: Any, nonce: str, commit: str) -> None:
    """Raise CryptoError unless (payload, nonce) hashes to commit."""
    actual = commit_of(payload, nonce)
    if actual != commit:
        raise CryptoError(f"Commit mismatch: expected {commit[:16]}…, got {actual[:16]}…")


def audit_records(records: list[dict]) -> dict:
    """Post-game audit: re-verify every {payload, nonce, commit} record.

    Both peers run this on the opponent's revealed log; any mismatch fails the
    audit (the honest peer wins by technical decision — tamper_forfeit).
    """
    failed: list[int] = []
    for record in records:
        try:
            verify(record["payload"], record["nonce"], record["commit"])
        except CryptoError:
            failed.append(record["payload"].get("step", -1))
    return {
        "passed": not failed,
        "verified_steps": len(records) - len(failed),
        "failed_steps": failed,
    }
