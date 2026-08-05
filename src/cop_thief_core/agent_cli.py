"""Shared headless entry point for the two role agents (`police_agent`,
`thief_agent`). Each role's `__main__` is a one-liner delegating here, so the CLI
logic lives in ONE tested place (DRY) rather than being duplicated per role.

Plays one series as the given role through the SDK (the single business entry
point) and prints the derived result. The MOVE is always pure Python; `--real-llm`
opts into the configured banter provider (default: offline stub).
"""

import argparse

from cop_thief_core.sdk import SimulationSdk


def parse_args(role: str, argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=f"{role}-agent", description=f"Cop-Thief P2P — play one series as {role}")
    parser.add_argument("--config", required=True, help=f"peer config dir, e.g. config/{role}")
    parser.add_argument("--workdir", default=".", help="where the four artifacts are written")
    parser.add_argument("--real-llm", action="store_true",
                        help="use the configured banter provider instead of the stub")
    return parser.parse_args(argv)


def run_role(role: str, argv=None, *, transport=None) -> dict:
    """Parse args, play one series as ``role``, print the derived result, return it.
    ``transport`` is injectable so tests drive it over the in-process FakeTransport."""
    args = parse_args(role, argv)
    sdk = SimulationSdk(args.config, workdir=args.workdir)
    outcome = sdk.run_peer(role, stub_llm=not args.real_llm, transport=transport)
    summary = outcome["result"]
    print(f"[{role}] result={summary['result']} winner={summary['winner']} "
          f"game_uid={outcome['game_uid']} artifacts={outcome.get('artifacts_dir', '-')}")
    return outcome
