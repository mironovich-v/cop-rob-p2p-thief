"""Tests for the opponent-location belief map (PRD_belief_map, TODO slice 3.1)."""

from cop_thief_core.domain.belief import BeliefGrid


def _total(belief):
    return sum(sum(row) for row in belief.as_matrix())


def test_initial_uniform_sums_to_one():
    belief = BeliefGrid(5)
    assert abs(_total(belief) - 1.0) < 1e-9
    assert all(abs(v - 1 / 25) < 1e-9 for row in belief.as_matrix() for v in row)


def test_as_matrix_returns_copy():
    belief = BeliefGrid(3)
    snapshot = belief.as_matrix()
    snapshot[0][0] = 999
    assert belief.as_matrix()[0][0] != 999


def test_observe_smell_concentrates_and_normalizes():
    belief = BeliefGrid(5, smell_trust=4.0)
    belief.observe_smell({"2,2": 0.9})
    assert abs(_total(belief) - 1.0) < 1e-9
    assert belief.most_likely() == (2, 2)
    assert belief.as_matrix()[2][2] > belief.as_matrix()[0][0]


def test_observe_smell_ignores_out_of_bounds():
    belief = BeliefGrid(3)
    belief.observe_smell({"9,9": 0.9, "0,0": 0.5})
    assert belief.most_likely() == (0, 0)


def test_diffuse_orthogonal_spreads_and_keeps_sum():
    belief = BeliefGrid(5, orthogonal=True)
    belief.observe_smell({"0,0": 0.9})
    belief.diffuse()
    assert abs(_total(belief) - 1.0) < 1e-9
    assert belief.as_matrix()[0][1] > 0.0  # mass leaked from the corner


def test_king_diffuse_reaches_diagonal():
    belief = BeliefGrid(5)  # orthogonal=False -> king neighbourhood
    belief.observe_smell({"2,2": 0.9})
    belief.diffuse()
    assert belief.as_matrix()[1][1] > 0.0  # diagonal neighbour got mass


def test_exclude_zeroes_cell_and_renormalizes():
    belief = BeliefGrid(4)
    belief.observe_smell({"1,1": 0.9})
    belief.exclude((1, 1))
    assert belief.as_matrix()[1][1] == 0.0
    assert abs(_total(belief) - 1.0) < 1e-9
    assert belief.most_likely() != (1, 1)


def test_degenerate_resets_to_uniform():
    belief = BeliefGrid(2)
    for cell in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        belief.exclude(cell)  # excluding every cell -> total 0 -> reset to uniform
    assert abs(_total(belief) - 1.0) < 1e-9
    assert all(abs(v - 0.25) < 1e-9 for row in belief.as_matrix() for v in row)
