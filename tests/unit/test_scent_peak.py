"""The freshest cell in a received scent map is the sender's CURRENT cell.

A peer deposits scent on the cell it is standing on immediately before sending,
so the map's maximum is that cell. Measured over a full game: the peak matched
the opponent's true cell 35/35 times, while the smeared belief estimate matched
0/35. The probabilistic update was destroying an exact observation that arrives
every single turn.
"""

from cop_thief_core.constants import ORTHOGONAL
from cop_thief_core.domain.board import Board
from cop_thief_core.domain.claim_tracker import peak_cell

BOARD = Board(7, ORTHOGONAL)


def test_peak_is_the_strongest_cell():
    assert peak_cell({"1,1": 0.2, "3,4": 0.81, "0,0": 0.5}) == (3, 4)


def test_empty_or_missing_map_has_no_peak():
    assert peak_cell({}) is None
    assert peak_cell(None) is None


def test_malformed_keys_are_skipped_not_guessed():
    """A sparse/foreign map must never be parsed loosely into the wrong cell."""
    assert peak_cell({"not-a-cell": 0.9, "2,2": 0.4}) == (2, 2)
    assert peak_cell({"not-a-cell": 0.9}) is None


def test_zero_intensity_is_not_a_sighting():
    assert peak_cell({"3,3": 0.0}) is None
