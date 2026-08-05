"""Tests for the shared role CLI (Stage 7.6a): arg parsing (pure) and that
run_role plays one series over the injected transport, printing the derived result.
Two peers drive the in-process FakeTransport — no network, no real mail."""

import threading
from pathlib import Path

from cop_thief_core.agent_cli import parse_args, run_role

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_parse_args_defaults_and_required():
    args = parse_args("police", ["--config", "config/police"])
    assert args.config == "config/police"
    assert args.workdir == "."
    assert args.real_llm is False


def test_run_role_plays_series_and_prints_result(transport_pair, tmp_path, capsys):
    thief_t, police_t = transport_pair
    outcomes: dict = {}

    def run(name, role, transport):
        argv = ["--config", str(REPO_ROOT / "config" / role),
                "--workdir", str(tmp_path / role)]
        outcomes[name] = run_role(role, argv, transport=transport)

    threads = [
        threading.Thread(target=run, args=("thief", "thief", thief_t), daemon=True),
        threading.Thread(target=run, args=("police", "police", police_t), daemon=True),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
        assert not thread.is_alive(), "role agent did not finish"

    assert outcomes["thief"]["game_uid"] == outcomes["police"]["game_uid"]
    assert outcomes["police"]["result"]["result"] in ("capture", "survival")
    printed = capsys.readouterr().out
    assert "[police]" in printed and "[thief]" in printed
    assert "game_uid=" in printed
