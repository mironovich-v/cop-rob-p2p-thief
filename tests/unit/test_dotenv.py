"""The stdlib .env loader (fix-env-loading): the auto-fired report must not
strand as no_credentials when the launch shell forgot to export the paths."""


def test_load_dotenv_sets_only_unset_vars(tmp_path, monkeypatch):
    # The report AUTO-FIRES at settlement — a launch shell that forgot to
    # export the Gmail paths must not silently strand the mail (no_credentials).
    from cop_thief_core.agent_cli import load_dotenv
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comment\nGMAIL_CREDENTIALS_PATH=./secrets/credentials.json\n"
        "ALREADY_SET=from-file\n\nexport QUOTED='./x'\n", encoding="utf-8")
    monkeypatch.delenv("GMAIL_CREDENTIALS_PATH", raising=False)
    monkeypatch.setenv("ALREADY_SET", "from-shell")
    load_dotenv(env_file)
    import os
    assert os.environ["GMAIL_CREDENTIALS_PATH"] == "./secrets/credentials.json"
    assert os.environ["ALREADY_SET"] == "from-shell"  # the shell always wins
    assert os.environ["QUOTED"] == "./x"


def test_load_dotenv_missing_file_is_a_noop(tmp_path):
    from cop_thief_core.agent_cli import load_dotenv
    load_dotenv(tmp_path / "absent.env")  # must not raise
