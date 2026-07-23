"""CORE-vector conformance: OUR production functions reproduce the league
fixtures byte-exactly (league SPEC §8). Runs against copthief-league-protocol/
vectors/ — fetch with scripts/fetch_interop.sh. These exercise production code,
never the kit's verify_vectors.py reference oracle. A mismatch means our code is
wrong (never edit a vector to pass).
"""

import hashlib
import json
from pathlib import Path

import pytest

from cop_thief_core.domain.smell import SmellField
from cop_thief_core.interop import canonical_json, commit_of, derive_game_ids
from cop_thief_core.reporting.report_writer import consensus_signature, verify_report

VECTORS = Path(__file__).resolve().parents[2] / "copthief-league-protocol" / "vectors"

pytestmark = pytest.mark.skipif(
    not VECTORS.is_dir(),
    reason="league kit not fetched; run scripts/fetch_interop.sh",
)


def _load(name: str) -> dict:
    return json.loads((VECTORS / name).read_text(encoding="utf-8"))


def test_canonical_json_vectors():
    for vector in _load("canonical_json.json")["vectors"]:
        canon = canonical_json(vector["object"])
        assert canon == vector["canonical"]
        assert hashlib.sha256(canon.encode()).hexdigest() == vector["sha256"]


def test_commit_reveal_vectors():
    data = _load("commit_reveal.json")
    for vector in data["vectors"]:
        assert commit_of(vector["payload"], vector["nonce"]) == vector["commit"]
    div = data["divergent_forms"]
    assert commit_of(div["payload"], div["nonce"]) == div["reference_form"]


def test_terms_signature_vectors():
    for vector in _load("terms_signature.json")["vectors"]:
        assert commit_of(vector["terms"], vector["nonce"]) == vector["signature"]


def test_game_uid_vectors():
    for vector in _load("game_uid.json")["vectors"]:
        _, game_uid = derive_game_ids(vector["terms"], vector["group_a"], vector["group_b"])
        assert game_uid == vector["game_uid"]


def test_pheromone_vectors():
    data = _load("pheromone.json")
    for case in data["emit"]:
        field = SmellField(case["board_size"], case["grid_size"], 0.1, 0.0)
        field.deposit(tuple(case["center"]), case["intensity"])
        assert field.snapshot() == case["field"]
    for case in data["decay"]:
        field = SmellField(64, 5, case["decay"], 0.0)
        field.absorb(case["before"])
        field.decay_all()
        # compare via intensity_at so a clamped 0.0 (dropped by snapshot) still checks
        for key, expected in case["after"].items():
            row, col = (int(part) for part in key.split(","))
            assert field.intensity_at((row, col)) == expected


def test_report_consensus_vectors():
    for vector in _load("report_consensus.json")["vectors"]:
        signature = consensus_signature(vector["report"])
        assert signature == vector["signature"]  # SPACED form
        assert signature != vector["compact_form_sha256"]  # NOT the compact §2 form
        assert verify_report(vector["signed_report"]) is True
