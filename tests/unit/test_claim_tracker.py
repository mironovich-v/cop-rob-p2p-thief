"""The police's declared position, trusted only when it behaves like one.

A co-location capture is the only way a cop takes the thief, so a conforming
cop's `capture_claim` names the cell it stands on. A cop whose claims are
guesses about the thief wanders instead — that must be detected and ignored,
not believed.
"""

from cop_thief_core.constants import ORTHOGONAL
from cop_thief_core.domain.board import Board
from cop_thief_core.domain.claim_tracker import ClaimTracker

BOARD = Board(7, ORTHOGONAL)


def test_first_claim_only_anchors():
    """One claim proves nothing — a lucky guess must not steer the thief."""
    tracker = ClaimTracker()
    assert tracker.accept((3, 3), step=1, board=BOARD) is None


def test_second_consistent_claim_is_trusted():
    tracker = ClaimTracker()
    tracker.accept((3, 3), step=1, board=BOARD)
    assert tracker.accept((3, 4), step=2, board=BOARD) == (3, 4)


def test_repeated_cell_is_trusted():
    """A cop that placed a barrier did not move; the same cell is consistent."""
    tracker = ClaimTracker()
    tracker.accept((3, 3), step=1, board=BOARD)
    assert tracker.accept((3, 3), step=2, board=BOARD) == (3, 3)


def test_teleporting_claims_are_refused():
    """A guessing cop's claims jump further than a cop can walk — ignore them."""
    tracker = ClaimTracker()
    tracker.accept((0, 0), step=1, board=BOARD)
    assert tracker.accept((6, 6), step=2, board=BOARD) is None


def test_tolerance_grows_with_the_elapsed_steps():
    """Claims may be skipped (our cop sends none on a barrier turn), so the
    reachable radius is the number of steps that passed, not always one."""
    tracker = ClaimTracker()
    tracker.accept((3, 3), step=1, board=BOARD)
    assert tracker.accept((3, 6), step=4, board=BOARD) == (3, 6)


def test_off_board_claim_is_refused():
    tracker = ClaimTracker()
    tracker.accept((3, 3), step=1, board=BOARD)
    assert tracker.accept((9, 9), step=2, board=BOARD) is None


def test_recovery_after_a_refusal():
    """A refused claim still re-anchors: a cop we merely mis-tracked is trusted
    again on its next consistent step, rather than being written off forever."""
    tracker = ClaimTracker()
    tracker.accept((0, 0), step=1, board=BOARD)
    assert tracker.accept((6, 6), step=2, board=BOARD) is None
    assert tracker.accept((6, 5), step=3, board=BOARD) == (6, 5)
