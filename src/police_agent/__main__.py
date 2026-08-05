"""Police agent entry point: play one series as the police peer.

    uv run python -m police_agent --config config/police

The role CLI logic lives in the shared, tested `cop_thief_core.agent_cli`.
"""

from cop_thief_core.agent_cli import run_role


def main() -> None:
    run_role("police")


if __name__ == "__main__":
    main()
