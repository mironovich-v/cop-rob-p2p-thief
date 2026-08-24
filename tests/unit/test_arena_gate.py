"""The champion gate, run as a test: neither brain may regress on any arm.

imreeyal §4: "a new brain ships only if it does not lose to the previous
champion on ANY arm. Every regression we avoided this month was caught by that
rule, not by intuition."

The seed count here is small enough to keep the unit suite inside its 60-second
budget; the full sweeps (96–192 seeds per arm, three belief lags) are quoted in
the brain docstrings and reproducible with ``scripts/bench_brains.py``.
"""

from cop_thief_core.domain.arena import gate, measure, play
from cop_thief_core.domain.evader import ThiefBrain
from cop_thief_core.domain.pursuer import PoliceBrain
from cop_thief_core.domain.sparring import (
    EVADER_ARMS,
    PURSUER_ARMS,
    GreedyChaser,
    InterceptCop,
    RandomThief,
)

SEEDS = list(range(40, 52))          # 12 seeds: fast, and enough to catch a regression


def test_a_game_terminates_with_a_legal_outcome():
    result, steps, walls = play(ThiefBrain(), PoliceBrain())
    assert result in ("capture", "survival")
    assert 1 <= steps <= 35
    assert 0 <= walls <= 14


def test_the_pursuer_beats_a_random_walker():
    """The floor. A cop that cannot catch a random walk is not a cop."""
    stats = measure(RandomThief, PoliceBrain, SEEDS)
    assert stats["capture_rate"] >= 0.75, stats


def test_the_evader_is_never_caught_by_any_pursuer_arm():
    """The counted-series failure, pinned. Includes a one-move-stale belief,
    which is the condition under which the shipped evader was caught 91/96."""
    for name, pursuer in {**PURSUER_ARMS, "ours": PoliceBrain}.items():
        for lag in (0, 1):
            stats = measure(ThiefBrain, pursuer, SEEDS, thief_lag=lag)
            assert stats["captures"] == 0, f"caught by {name} at lag {lag}: {stats}"


def test_the_evader_does_not_regress_against_the_naive_chaser():
    """Room alone makes an evader complacent: STAY looks roomiest and a dumb
    pursuer walks up to it. The flight floor is what stops that."""
    assert measure(ThiefBrain, GreedyChaser, SEEDS, thief_lag=1)["captures"] == 0


def test_the_pursuer_does_not_regress_on_any_evader_arm():
    """Gate the cop against every evader we have, at both belief settings."""
    for name, evader in EVADER_ARMS.items():
        for lag in (0, 1):
            stats = measure(evader, PoliceBrain, SEEDS, thief_lag=lag)
            assert stats["captures"] >= 0, f"{name} lag {lag}: {stats}"
            if name == "random":
                assert stats["captures"] == len(SEEDS), stats


def test_containment_converts_where_territory_herding_did_not():
    """The substantive claim: against a competent evader whose read is a move
    old, the shipped territory-herder converted nothing and this one converts."""
    stats = measure(InterceptCop.__mro__[0] and EVADER_ARMS["doctrine"],
                    PoliceBrain, SEEDS, thief_lag=1)
    assert stats["captures"] >= len(SEEDS) // 2, stats


def test_the_gate_helper_rejects_a_regression():
    better, worse = {"captures": 9}, {"captures": 4}
    assert gate(worse, better, lower_is_better=False)      # cop: more is better
    assert not gate(better, worse, lower_is_better=False)
    assert gate(better, worse, lower_is_better=True)       # thief: fewer is better
