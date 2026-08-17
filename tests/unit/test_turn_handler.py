"""Adversarial robustness for TurnHandler (AC7): a peer folds each opponent step
exactly once. Stale / duplicate / out-of-order messages are dropped without
mutating belief, smell, or history — a network re-send can never double-count."""

from cop_thief_core.constants import Role
from cop_thief_core.orchestration.runtime import PeerRuntime
from cop_thief_core.protocol import TurnMessage


def _handler(config):
    # PeerRuntime wires a real handler (state/belief/smell/rules) and never touches
    # the transport until run(), so None is fine for constructing one.
    return PeerRuntime(Role.POLICE, config, transport=None).handler


def _msg(step: int, smell=None) -> TurnMessage:
    return TurnMessage(
        step=step, sender="thief", hint="hi", smell_grid=smell or {"3,3": 0.9},
        commit="c" * 64, timestamp="t", barrier_placed=None,
        capture_claim=None, claim_response=None, win_claim=None)


def test_fresh_steps_are_folded_in_order(police_config):
    handler = _handler(police_config)
    assert handler.process(_msg(1)).ignored is False
    assert handler.process(_msg(2)).ignored is False
    assert [entry["step"] for entry in handler.history] == [1, 2]


def test_duplicate_step_is_ignored(police_config):
    handler = _handler(police_config)
    handler.process(_msg(1))
    before = handler.belief.as_matrix()
    outcome = handler.process(_msg(1))  # exact duplicate
    assert outcome.ignored is True
    assert len(handler.history) == 1               # not appended again
    assert handler.belief.as_matrix() == before    # belief not double-updated


def test_stale_and_out_of_order_steps_are_ignored(police_config):
    handler = _handler(police_config)
    handler.process(_msg(1))
    handler.process(_msg(2))
    handler.process(_msg(3))
    assert handler.process(_msg(2)).ignored is True   # stale (lower than seen)
    assert handler.process(_msg(1)).ignored is True   # far-stale / out-of-order
    assert [entry["step"] for entry in handler.history] == [1, 2, 3]


def test_forward_step_after_gap_still_accepted(police_config):
    handler = _handler(police_config)
    handler.process(_msg(1))
    assert handler.process(_msg(5)).ignored is False  # forward jump is legitimate
    assert handler.process(_msg(5)).ignored is True   # its duplicate is not
