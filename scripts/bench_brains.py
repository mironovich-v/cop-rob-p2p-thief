"""Reproduce the brain measurements quoted in the brain docstrings.

    uv run python scripts/bench_brains.py            # default 96 seeds
    uv run python scripts/bench_brains.py --seeds 192 --start 9000

The unit suite runs a fast 12-seed champion gate (tests/unit/test_arena_gate.py);
this is the full sweep, and it is what the numbers in
``domain/evader.py`` / ``domain/pursuer.py`` refer to. Belief lag is swept
because it is the condition that decides the whole result: at lag 0 the old
evader was never caught, at lag 1 it was caught 91/96.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cop_thief_core.domain.arena import measure  # noqa: E402
from cop_thief_core.domain.evader import ThiefBrain  # noqa: E402
from cop_thief_core.domain.pursuer import PoliceBrain  # noqa: E402
from cop_thief_core.domain.sparring import EVADER_ARMS, PURSUER_ARMS  # noqa: E402


def _row(label: str, stats: dict) -> str:
    return (f"  {label:<28} {stats['captures']:>3}/{stats['n']}"
            f"  ({stats['capture_rate'] * 100:4.0f}%)   steps med {stats['median_steps']:>4.1f}"
            f"  mean {stats['mean_steps']:>4.1f}  max {stats['max_steps']:>2}"
            f"   walls {stats['walls']:>4.1f}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=96)
    parser.add_argument("--start", type=int, default=9000)
    parser.add_argument("--lags", type=int, nargs="*", default=[0, 1])
    args = parser.parse_args()
    seeds = list(range(args.start, args.start + args.seeds))

    print(f"seeds {seeds[0]}..{seeds[-1]}  ({len(seeds)} per arm)\n")
    print("===== POLICE vs every evader arm — captures, higher is better =====")
    for lag in args.lags:
        for name, arm in {**EVADER_ARMS, "our thief": ThiefBrain}.items():
            print(_row(f"lag{lag}  vs {name}", measure(arm, PoliceBrain, seeds, thief_lag=lag)))
        print()
    print("===== THIEF vs every pursuer arm — captures, LOWER is better =====")
    for lag in args.lags:
        for name, arm in {**PURSUER_ARMS, "our police": PoliceBrain}.items():
            print(_row(f"lag{lag}  vs {name}", measure(ThiefBrain, arm, seeds, thief_lag=lag)))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
