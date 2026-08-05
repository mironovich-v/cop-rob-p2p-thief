"""Launch the live GUI for one peer:

    uv run python -m cop_thief_core.gui --config config/police --role police
    uv run python -m cop_thief_core.gui --config config/thief  --role thief

Two windows (one per role, each with its own config dir + opponent URL) play a
live game. Coverage-omitted (Tk entry point).
"""

import argparse

from cop_thief_core.gui.player import LivePeerApp
from cop_thief_core.sdk import SimulationSdk


def main() -> None:
    parser = argparse.ArgumentParser(description="Cop-Thief P2P live GUI (one peer)")
    parser.add_argument("--config", required=True, help="peer config dir, e.g. config/police")
    parser.add_argument("--role", required=True, choices=["police", "thief"])
    parser.add_argument("--workdir", default=".", help="where artifacts are written")
    parser.add_argument("--real-llm", action="store_true",
                        help="use the configured LLM banter provider instead of the stub")
    args = parser.parse_args()
    sdk = SimulationSdk(args.config, workdir=args.workdir)
    LivePeerApp(sdk, args.role, stub_llm=not args.real_llm).run()


if __name__ == "__main__":
    main()
