"""The locked-model registry docs THIS peer declares (league SPEC §7).

The three docs live verbatim in ``locked_models_data.json``, copied from the
league kit's published registry (``copthief-league-protocol/vectors/
locked_model.json``) — they are protocol, not config, and the conformance suite
re-hashes them against the kit to catch drift. Only the ``<family>_sha256``
hashes cross the wire, in the negotiate extras; refusal fires ONLY when both
peers declare a family and the hashes differ — omission is never refusal.
"""

import hashlib
import json
from pathlib import Path

from cop_thief_core.interop.canonical import canonical_bytes

_DATA_PATH = Path(__file__).resolve().parent / "locked_models_data.json"
_DOCS: list[dict] = json.loads(_DATA_PATH.read_text(encoding="utf-8"))


def declared_docs() -> dict[str, dict]:
    """The registry docs we play under, keyed by family."""
    return {doc["family"]: doc for doc in _DOCS}


def model_hashes() -> dict[str, str]:
    """The three ``<family>_sha256`` declarations we send with every negotiate."""
    return {
        f"{doc['family']}_sha256": hashlib.sha256(canonical_bytes(doc)).hexdigest()
        for doc in _DOCS
    }
