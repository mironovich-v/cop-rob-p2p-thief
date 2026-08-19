"""Tests for the scent field (PRD_pheromone_scent, TODO slice 4.1)."""

import pytest

from cop_thief_core.domain.smell import SmellField


def _field(board=7, grid=5, decay=0.1, min_center=0.5):
    return SmellField(board, grid, decay, min_center)


def test_deposit_radial_falloff():
    field = _field()
    field.deposit((3, 3), 0.9)
    assert field.intensity_at((3, 3)) == 0.9
    assert field.intensity_at((3, 4)) == 0.6  # Chebyshev distance 1
    assert field.intensity_at((1, 1)) == 0.3  # distance 2
    assert len(field.snapshot()) == 25  # full 5x5 in bounds


def test_deposit_clipped_at_corner():
    field = _field()
    field.deposit((0, 0), 0.9)
    assert field.intensity_at((0, 0)) == 0.9
    assert len(field.snapshot()) == 9  # 3x3 clipped to the board


def test_deposit_below_minimum_raises():
    with pytest.raises(ValueError, match="below required minimum"):
        _field().deposit((3, 3), 0.3)


def test_absorb_max_merge():
    field = _field()
    field.absorb({"2,2": 0.5})
    field.absorb({"2,2": 0.7, "9,9": 0.9})  # out-of-bounds ignored
    assert field.intensity_at((2, 2)) == 0.7
    assert field.intensity_at((9, 9)) == 0.0


def test_decay_subtracts_and_clamps():
    field = _field()
    field.absorb({"3,3": 0.9, "1,1": 0.05})
    field.decay_all()
    assert field.intensity_at((3, 3)) == 0.8
    assert field.intensity_at((1, 1)) == 0.0  # clamped at the floor


def test_strongest_cell_and_empty():
    field = _field()
    assert field.strongest_cell() is None
    field.deposit((3, 3), 0.9)
    assert field.strongest_cell() == (3, 3)


def test_snapshot_excludes_zero():
    field = _field()
    field.absorb({"2,2": 0.05})
    field.decay_all()  # -> 0.0
    assert field.snapshot() == {}
