"""Tests for the discrete board geometry (PRD_game_state, TODO slice 1.1)."""

import pytest

from cop_thief_core.constants import DELTAS, ORTHOGONAL, Direction
from cop_thief_core.domain.board import Board


def test_default_moves_are_king_eight():
    board = Board(5)
    assert len(board.moves) == 8
    assert board.diagonal is True


def test_orthogonal_board_has_four_moves_no_diagonal():
    board = Board(5, ORTHOGONAL)
    assert len(board.moves) == 4
    assert board.diagonal is False


def test_invalid_size_raises():
    with pytest.raises(ValueError):
        Board(0)


def test_in_bounds():
    board = Board(3)
    assert board.size == 3
    assert board.in_bounds((0, 0))
    assert board.in_bounds((2, 2))
    assert not board.in_bounds((-1, 0))
    assert not board.in_bounds((3, 0))
    assert not board.in_bounds((0, 3))


def test_distance_manhattan_when_orthogonal():
    board = Board(9, ORTHOGONAL)
    assert board.distance((0, 0), (2, 3)) == 5


def test_distance_chebyshev_when_king():
    board = Board(9)  # king default allows diagonals
    assert board.distance((0, 0), (2, 3)) == 3


def test_step_valid():
    board = Board(5, ORTHOGONAL)
    assert board.step((2, 2), Direction.N) == (1, 2)
    assert board.step((2, 2), Direction.E) == (2, 3)


def test_step_off_board_returns_none():
    board = Board(5, ORTHOGONAL)
    assert board.step((0, 0), Direction.N) is None
    assert board.step((0, 0), Direction.W) is None


def test_step_into_barrier_returns_none():
    board = Board(5, ORTHOGONAL)
    assert board.step((2, 2), Direction.E, barriers={(2, 3)}) is None


def test_neighbors_orthogonal_center_and_corner():
    board = Board(5, ORTHOGONAL)
    assert len(board.neighbors((2, 2))) == 4
    assert len(board.neighbors((0, 0))) == 2


def test_neighbors_respect_barriers():
    board = Board(5, ORTHOGONAL)
    neigh = board.neighbors((2, 2), barriers={(2, 3), (1, 2)})
    assert (2, 3) not in neigh
    assert (1, 2) not in neigh
    assert len(neigh) == 2


def test_neighbors_king_center_is_eight():
    assert len(Board(5).neighbors((2, 2))) == 8


def test_legal_moves_returns_direction_cell_pairs():
    board = Board(5, ORTHOGONAL)
    moves = board.legal_moves((0, 0))  # corner: only S and E are legal
    assert (Direction.S, (1, 0)) in moves
    assert (Direction.E, (0, 1)) in moves
    assert all(isinstance(direction, Direction) for direction, _ in moves)
    assert len(moves) == 2


def test_deltas_cover_all_directions():
    assert set(DELTAS) == set(Direction)
