"""The cop's own declared cell beats the scent trail (thief side).

A cop claims co-location, so its capture_claim names the cell it stands on —
evidence about NOW. Scent marks where it WAS, and the thief that fled the trail
ran into corners it could have seen coming (live: nis-yar1 3/3, il-nv-ai @10).
A claim is trusted only while the claims walk like a cop.
"""

from cop_thief_core.constants import Role
from cop_thief_core.orchestration.runtime import PeerRuntime
from cop_thief_core.protocol import TurnMessage


def _thief_handler(config):
    return PeerRuntime(Role.THIEF, config, transport=None).handler


def _claim_msg(step: int, claim, smell=None) -> TurnMessage:
    """A police turn: its capture_claim names the cell it is standing on."""
    return TurnMessage(
        step=step, sender="police", hint="hi", smell_grid=smell or {"0,0": 0.9},
        commit="c" * 64, timestamp="t", barrier_placed=None,
        capture_claim=list(claim), claim_response=None, win_claim=None)


def test_consistent_cop_claims_pin_the_belief(thief_config):
    """Scent says (0,0) all game; the cop's own claims say otherwise and win.

    Without this the thief flees a trail that lags the cop by several steps —
    the live corner-running that lost every counted sub-game.
    """
    handler = _thief_handler(thief_config)
    handler.process(_claim_msg(1, (2, 2)))      # anchor only
    handler.process(_claim_msg(2, (2, 3)))      # consistent -> trusted
    assert handler.belief.most_likely() == (2, 3)


def test_teleporting_claims_leave_the_scent_estimate_alone(thief_config):
    """A cop whose claims jump further than a cop can walk is not a position
    source — belief must fall back to scent rather than be steered."""
    handler = _thief_handler(thief_config)
    handler.process(_claim_msg(1, (0, 1)))
    handler.process(_claim_msg(2, (6, 6), smell={"0,0": 0.9}))
    assert handler.belief.most_likely() != (6, 6)
