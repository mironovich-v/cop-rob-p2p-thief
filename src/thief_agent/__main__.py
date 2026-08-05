"""Thief agent entry point: play one series as the thief peer.

    uv run python -m thief_agent --config config/thief

The role CLI logic lives in the shared, tested `cop_thief_core.agent_cli`.
"""

from cop_thief_core.agent_cli import run_role


def main() -> None:
    run_role("thief")


if __name__ == "__main__":
    main()
