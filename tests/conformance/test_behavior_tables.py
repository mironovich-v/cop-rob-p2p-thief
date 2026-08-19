"""PROMOTED behavior-table conformance: OUR production code answers every row
of the kit's decision tables (league GOVERNANCE: "these cost games exactly as
byte mismatches do"). Drives TurnHandler, validate_turn_values/receive, and
check_extras — never the kit's reference code. The delivery deadline rows are
behavior-tested in tests/integration/test_runtime.py (junk flood).
"""

import json
from pathlib import Path

import pytest

from cop_thief_core.constants import Role
from cop_thief_core.interop.extras import check_extras
from cop_thief_core.orchestration.runtime import PeerRuntime
from cop_thief_core.protocol import TurnMessage

VECTORS = Path(__file__).resolve().parents[2] / "copthief-league-protocol" / "vectors"

pytestmark = pytest.mark.skipif(
    not VECTORS.is_dir(),
    reason="league kit not fetched; run scripts/fetch_interop.sh",
)


def _load(name: str) -> dict:
    return json.loads((VECTORS / name).read_text(encoding="utf-8"))


def _msg(step: int, commit: str) -> TurnMessage:
    return TurnMessage(step=step, sender="thief", hint="", smell_grid={},
                       commit=commit, timestamp="t", barrier_placed=None,
                       capture_claim=None, claim_response=None, win_claim=None)


def _seeded_handler(police_config, state: dict):
    handler = PeerRuntime(Role.POLICE, police_config, transport=None).handler
    handler._window = state["window"]  # the vector's receiver state, verbatim
    for step, commit in state["played"].items():
        handler.process(_msg(int(step), commit))
    return handler


def test_delivery_contract_arrival_rows(police_config):
    data = _load("delivery_contract.json")
    expected_settle = {"equivocation": "tamper_forfeit", "violation": "technical_loss"}
    for row in data["arrivals"]:
        handler = _seeded_handler(police_config, data["state"])
        outcome = handler.process(_msg(**row["arrival"]))
        decision = row["decision"]
        if decision == "apply":
            assert (outcome.ignored, outcome.settle) == (False, None), row["note"]
        elif decision in ("absorb", "buffer", "discard"):
            assert (outcome.ignored, outcome.settle) == (True, None), row["note"]
        else:
            assert outcome.settle == expected_settle[decision], row["note"]


def test_turn_message_validation_rows(police_config):
    # Value validation only — sequencing is the delivery table's job above.
    from cop_thief_core.protocol.messages import validate_turn_values
    for case in _load("turn_message.json")["validation"]:
        if case["verdict"] == "accept":
            validate_turn_values(TurnMessage.from_dict(case["message"]))  # no raise
        else:
            with pytest.raises((TypeError, ValueError)):
                validate_turn_values(TurnMessage.from_dict(case["message"]))
            # and the full receive path refuses it BEFORE any state change
            handler = PeerRuntime(Role.POLICE, police_config, transport=None).handler
            outcome = handler.receive(case["message"])
            assert outcome.ignored is True, case["note"]
            assert handler.history == []


def test_pairing_declaration_rows():
    from cop_thief_core.exceptions import AgreementError
    for row in _load("pairing_declaration.json")["refusal_rule"]:
        if row["decision"].startswith("refuse"):
            with pytest.raises(AgreementError):
                check_extras(row["ours"], row["theirs"])
        else:
            check_extras(row["ours"], row["theirs"])  # must NOT raise


def test_uid_declaration_rows():
    from cop_thief_core.exceptions import AgreementError
    for row in _load("uid_declaration.json")["refusal_rule"]:
        ours = {"game_uid": row["ours"]} if row["ours"] is not None else {}
        theirs = {"game_uid": row["theirs"]} if row["theirs"] is not None else {}
        if row["decision"] == "refuse":
            with pytest.raises(AgreementError):
                check_extras(ours, theirs)
        else:
            check_extras(ours, theirs)  # omission / uncomparable never refuses
