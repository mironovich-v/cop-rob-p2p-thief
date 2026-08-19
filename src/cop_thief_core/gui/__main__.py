"""Launch a peer GUI — live play or replay:

    # live (one window per role; two windows play a game)
    uv run python -m cop_thief_core.gui --config config/police --role police

    # replay a saved sub-game log (both revealed trajectories on one board)
    uv run python -m cop_thief_core.gui --config config/police \
        --replay logs/vm__fabi-police/log_<game_id>_g01.json

Coverage-omitted (Tk entry point).
"""

import argparse

from cop_thief_core.sdk import SimulationSdk


def main() -> None:
    parser = argparse.ArgumentParser(description="Cop-Thief P2P GUI (live or replay)")
    parser.add_argument("--config", required=True, help="peer config dir, e.g. config/police")
    parser.add_argument("--role", choices=["police", "thief"], help="required for live play")
    parser.add_argument("--replay", help="path to a saved log_<game_id>_gNN.json to replay")
    parser.add_argument("--workdir", default=".", help="where live artifacts are written")
    parser.add_argument("--real-llm", action="store_true",
                        help="use the configured LLM banter provider instead of the stub")
    args = parser.parse_args()
    sdk = SimulationSdk(args.config, workdir=args.workdir)
    if args.replay:
        from cop_thief_core.gui.replay import ReplayApp, load_log_file
        ReplayApp(sdk.config, load_log_file(args.replay), log_path=args.replay).run()
        return
    if not args.role:
        parser.error("--role is required for live play (omit only with --replay)")
    from cop_thief_core.gui.player import LivePeerApp
    LivePeerApp(sdk, args.role, stub_llm=not args.real_llm).run()


if __name__ == "__main__":
    main()
