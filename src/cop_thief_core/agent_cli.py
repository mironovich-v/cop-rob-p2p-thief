"""Shared headless entry point for the two role agents (`police_agent`,
`thief_agent`). Each role's `__main__` is a one-liner delegating here, so the CLI
logic lives in ONE tested place (DRY) rather than being duplicated per role.

Plays one series as the given role through the SDK (the single business entry
point) and prints the derived result. The MOVE is always pure Python; `--real-llm`
opts into the configured banter provider (default: offline stub).
"""

import argparse
import os
import sys
from pathlib import Path

from cop_thief_core.exceptions import AuditTimeoutError
from cop_thief_core.sdk import SimulationSdk
from cop_thief_core.shared.progress import progress_listener


def load_dotenv(path: str | os.PathLike = ".env") -> None:
    """Minimal stdlib .env loader: KEY=VALUE lines (quotes/`export ` stripped),
    setting only variables the shell did NOT set — the shell always wins. The
    report auto-fires at settlement, so a launch shell that forgot to export
    the Gmail paths must not silently strand the mail as `no_credentials`."""
    env_file = Path(path)
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip().removeprefix("export ").strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def parse_args(role: str, argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=f"{role}-agent", description=f"Cop-Thief P2P — play one series as {role}")
    parser.add_argument("--config", required=True, help=f"peer config dir, e.g. config/{role}")
    parser.add_argument("--workdir", default=".", help="where the four artifacts are written")
    parser.add_argument("--real-llm", action="store_true",
                        help="use the configured banter provider instead of the stub")
    parser.add_argument("--counted", action="store_true",
                        help="CLI half of the double arming for the ONE counted series "
                             "(config game.counted must agree; ADR-20)")
    return parser.parse_args(argv)


def run_role(role: str, argv=None, *, transport=None) -> dict:
    """Parse args, play one series as ``role``, print the derived result, return it.
    ``transport`` is injectable so tests drive it over the in-process FakeTransport."""
    args = parse_args(role, argv)
    load_dotenv()  # secrets paths from ./.env unless the shell already set them
    sdk = SimulationSdk(args.config, workdir=args.workdir)
    try:
        outcome = sdk.run_peer(role, stub_llm=not args.real_llm, transport=transport,
                               listener=progress_listener(), counted=args.counted)
    except AuditTimeoutError as stopped:
        # A stated reason, not a traceback: the series is over, the sub-game is
        # void, and NOTHING is filed (no artifacts, no report, no mail).
        print(f"[{role}] SERIES STOPPED — {stopped}", file=sys.stderr, flush=True)
        raise SystemExit(2) from stopped
    summary = outcome["result"]
    print(f"[{role}] result={summary['result']} winner={summary['winner']} "
          f"game_uid={outcome['game_uid']} artifacts={outcome.get('artifacts_dir', '-')}")
    return outcome
