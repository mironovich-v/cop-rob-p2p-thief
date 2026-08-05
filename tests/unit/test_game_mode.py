"""Unit tests for the GUI verbal-game mode/model classifier (Stage 7.4)."""

from cop_thief_core.gui.game_mode import (
    OLLAMA_MODE,
    PYTHON_MODE,
    REMOTE_MODE,
    mode_and_model,
    mode_from_recorded_model,
)


class _Cfg:
    def __init__(self, values):
        self._values = values

    def get(self, key, default=None):
        return self._values.get(key, default)


def test_template_provider_reports_python_none():
    assert mode_and_model(_Cfg({"trash_talk.provider": "template"})) == (PYTHON_MODE, "None")


def test_missing_config_defaults_to_python():
    assert mode_and_model(None) == (PYTHON_MODE, "None")


def test_ollama_uses_model_or_default():
    assert mode_and_model(_Cfg({"trash_talk.provider": "ollama"})) == (OLLAMA_MODE, "llama3.2")
    named = _Cfg({"trash_talk.provider": "ollama", "trash_talk.model": "mistral"})
    assert mode_and_model(named) == (OLLAMA_MODE, "mistral")


def test_claude_api_and_cli_are_remote():
    assert mode_and_model(_Cfg({"trash_talk.provider": "claude_api"}))[0] == REMOTE_MODE
    cli = _Cfg({"trash_talk.provider": "claude_cli", "llm.model": "claude-opus"})
    assert mode_and_model(cli) == (REMOTE_MODE, "claude-opus")


def test_recorded_model_classification():
    assert mode_from_recorded_model("template") == (PYTHON_MODE, "None")
    assert mode_from_recorded_model("") == (PYTHON_MODE, "None")
    assert mode_from_recorded_model("stub") == (PYTHON_MODE, "None")
    assert mode_from_recorded_model("claude-haiku-4-5") == (REMOTE_MODE, "claude-haiku-4-5")
