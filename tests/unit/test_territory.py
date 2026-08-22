"""Territory: the cells an evader reaches before the pursuer can.

Our police was limited by TACTICS, not belief — an oracle cop with the thief's
true cell captured 2/16, no better than the shipped 3/16. A pursuer never closes
on an equally fast evader by chasing it; it wins by shrinking the space the
evader can still reach. That quantity is what this measures.
"""

from cop_thief_core.constants import ORTHOGONAL
from cop_thief_core.domain.board import Board
from cop_thief_core.domain.tactics import territory

BOARD = Board(7, ORTHOGONAL)


def test_a_cornered_evader_owns_less_than_a_central_one():
    corner = territory(BOARD, (6, 6), (5, 5), set())
    centre = territory(BOARD, (3, 3), (5, 5), set())
    assert corner < centre


def test_closing_the_pursuer_shrinks_the_evaders_room():
    """Same evader cell, nearer pursuer — strictly less room to live in."""
    near = territory(BOARD, (0, 0), (0, 1), set())
    far = territory(BOARD, (0, 0), (6, 6), set())
    assert near < far


def test_a_distant_pursuer_leaves_most_of_the_board():
    assert territory(BOARD, (3, 3), (0, 0), set()) > BOARD.size ** 2 // 3


def test_barriers_cut_reachable_territory():
    walled = {(2, 3), (4, 3), (3, 2)}  # pocket (3,3) against its last exit
    assert territory(BOARD, (3, 3), (0, 0), walled) < territory(BOARD, (3, 3), (0, 0), set())


def test_an_enclosed_evader_owns_only_itself():
    walled = {(2, 3), (4, 3), (3, 2), (3, 4)}
    assert territory(BOARD, (3, 3), (0, 0), walled) == 1
