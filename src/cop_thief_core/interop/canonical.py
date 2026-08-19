"""The one canonical JSON form under every ordinary protocol hash.

Load-bearing details (league SPEC §2): keys sorted recursively, no insignificant
whitespace (compact separators), and **native UTF-8** (`ensure_ascii=False`) so
Hebrew/emoji are emitted raw — escaping them would make an opponent's audit
re-hash miss, costing both sides the match. Floats use Python's shortest
round-trip repr. This is the single production canonicalizer; reuse it everywhere.
"""

import json
from typing import Any


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def canonical_bytes(obj: Any) -> bytes:
    return canonical_json(obj).encode("utf-8")
