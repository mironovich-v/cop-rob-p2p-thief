"""Deterministic export of the two submission repositories (Stage 7 / submission).

Generates self-contained release trees for the Police and Thief agents, each
vendoring a snapshot of ``cop_thief_core``, cross-linking the other repo, and
recording the canonical core commit/hash so a drift check can verify both exports
came from the same source. Neither export may depend at runtime on the other repo
or on a private third repo.

TODO(Stage 7): implement. See CLAUDE.md §13 (Two-repository export) and
docs/PRD_reporting_shell.md.
"""


def main() -> None:
    raise SystemExit("export_repos: not yet implemented (Stage 7)")


if __name__ == "__main__":
    main()
