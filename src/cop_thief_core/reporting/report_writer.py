"""The report consensus signature — the settlement construction.

Deliberately the release's SECOND canonical form (league SPEC §6): the SPACED
``json.dumps(report, sort_keys=True, ensure_ascii=False)`` (default separators),
NOT the compact §2 form used for every other hash. It is computed BEFORE the
signature key is inserted (sign-then-insert); verification pops the key,
re-serializes spaced, and re-hashes. Using the compact form here fails settlement
at the exact moment both teams must agree — so this stays separate on purpose.
"""

import hashlib
import hmac
import json

SIGNATURE_KEY = "חתימת_קונסנזוס_משותפת"


def consensus_signature(report: dict) -> str:
    """SHA-256 over the SPACED canonical (sorted-keys) JSON — never the compact form."""
    canonical = json.dumps(report, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def sign_report(report: dict) -> dict:
    """Return the report with its consensus signature inserted (sign-then-insert)."""
    signed = dict(report)
    signed[SIGNATURE_KEY] = consensus_signature(report)
    return signed


def verify_report(signed_report: dict) -> bool:
    """Pop the signature key, re-serialize spaced, re-hash, and compare securely."""
    report = dict(signed_report)
    claimed = report.pop(SIGNATURE_KEY, None)
    if not claimed:
        return False
    return hmac.compare_digest(claimed, consensus_signature(report))
