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


# --- Rules 46-47: an ending only the thief can see must be SAID (concession) ---

def _thief_handler(config):
    return PeerRuntime(Role.THIEF, config, transport=None).handler


def _police_msg(step: int, barrier=None, capture_claim=None) -> TurnMessage:
    return TurnMessage(
        step=step, sender="police", hint="", smell_grid={}, commit="c" * 64,
        timestamp="t", barrier_placed=barrier, capture_claim=capture_claim,
        claim_response=None, win_claim=None)


def test_thief_concedes_barrier_on_own_cell(thief_config):
    handler = _thief_handler(thief_config)  # rule 46
    pos = handler.state.position
    outcome = handler.process(_police_msg(1, barrier=list(pos)))
    assert outcome.i_am_caught is True
    assert outcome.claim_response == {"claim": list(pos), "caught": True}


def test_thief_concedes_when_boxed_in(thief_config):
    handler = _thief_handler(thief_config)  # rule 47
    row, col = handler.state.position
    for cell in [(row - 1, col), (row + 1, col), (row, col - 1)]:
        handler.state.note_barrier(cell)
    outcome = handler.process(_police_msg(1, barrier=[row, col + 1]))  # last wall
    assert outcome.i_am_caught is True
    assert outcome.claim_response == {"claim": [row, col], "caught": True}


def test_thief_plays_on_while_an_escape_remains(thief_config):
    handler = _thief_handler(thief_config)
    row, col = handler.state.position
    outcome = handler.process(_police_msg(1, barrier=[row - 1, col]))
    assert outcome.i_am_caught is False
    assert outcome.claim_response is None


def test_concession_overrides_a_missed_capture_claim(thief_config):
    handler = _thief_handler(thief_config)  # wrong claim + walling barrier together
    row, col = handler.state.position
    for cell in [(row - 1, col), (row + 1, col), (row, col - 1)]:
        handler.state.note_barrier(cell)
    outcome = handler.process(
        _police_msg(1, barrier=[row, col + 1], capture_claim=[0, 0]))
    assert outcome.i_am_caught is True
    assert outcome.claim_response == {"claim": [row, col], "caught": True}


def test_police_never_self_concedes(police_config):
    handler = _handler(police_config)  # enclosure capture is thief-only
    pos = handler.state.position
    outcome = handler.process(_msg(1))
    handler.state.note_barrier(pos)
    outcome = handler.process(_msg(2))
    assert outcome.i_am_caught is False
