"""Tests for the opt-in LLM trash-talk provider (PRD_llm_verbal_layer, slice 4.3).

No live model — askers are fakes; the network askers are covered-out.
"""

import random
import time

from cop_thief_core.constants import VERDICT_LIE, Role
from cop_thief_core.strategy.talk_providers import resolve_trash_talk
from cop_thief_core.strategy.trash_talk import LlmTrashTalk, TrashTalk


class _Cfg:
    def __init__(self, values):
        self._values = values

    def get(self, key, default=None):
        return self._values.get(key, default)


def _rng():
    return random.Random(0)


def test_llm_hint_used_when_valid_json():
    def ask(prompt, deadline=None, system=""):
        return '{"message": "near Central Park", "verdict": "lie", "reasoning": "bluff"}'

    hint, verdict, reasoning, logged = LlmTrashTalk(ask, _rng()).say(
        Role.THIEF, None, None, "New York", ""
    )
    assert hint == "near Central Park"
    assert verdict == VERDICT_LIE
    assert reasoning == "bluff"
    assert "[system]" in logged


def test_bad_json_falls_back_to_template():
    def ask(prompt, deadline=None, system=""):
        return "not json at all"

    hint, _verdict, reasoning, logged = LlmTrashTalk(ask, _rng()).say(
        Role.POLICE, None, None, "New York", ""
    )
    assert hint  # a template line
    assert reasoning == ""  # template has no reasoning
    assert "[system]" in logged  # prompt still logged even on fallback


def test_every_n_steps_skips_llm():
    calls = {"n": 0}

    def ask(prompt, deadline=None, system=""):
        calls["n"] += 1
        return '{"message": "x"}'

    provider = LlmTrashTalk(ask, _rng(), every_n_steps=3)
    provider.say(Role.THIEF, None, None, "New York", "")  # turn 1 -> template
    provider.say(Role.THIEF, None, None, "New York", "")  # turn 2 -> template
    assert calls["n"] == 0
    provider.say(Role.THIEF, None, None, "New York", "")  # turn 3 -> LLM
    assert calls["n"] == 1


def test_deadline_miss_falls_back_to_template():
    def slow_ask(prompt, deadline=None, system=""):
        time.sleep(1.0)
        return '{"message": "too late"}'

    hint, _verdict, _reasoning, _logged = LlmTrashTalk(slow_ask, _rng()).say(
        Role.THIEF, None, None, "New York", "", deadline=0.05
    )
    assert "too late" not in hint  # template fallback after the timeout


def test_system_prompt_carries_setting_and_word_limit():
    captured = {}

    def ask(prompt, deadline=None, system=""):
        captured["system"] = system
        return '{"message": "ok"}'

    LlmTrashTalk(ask, _rng(), max_words=9).say(Role.THIEF, None, None, "Paris", "")
    assert "Paris" in captured["system"]
    assert "9 words" in captured["system"]


def test_resolve_claude_cli_uses_llm():
    class _Llm:
        def send(self, prompt):
            return '{"message": "hi"}'

    provider = resolve_trash_talk(_Cfg({"trash_talk.provider": "claude_cli"}), _rng(), _Llm())
    assert isinstance(provider, LlmTrashTalk)


def test_resolve_claude_cli_without_llm_falls_back():
    provider = resolve_trash_talk(_Cfg({"trash_talk.provider": "claude_cli"}), _rng(), None)
    assert isinstance(provider, TrashTalk)
    assert not isinstance(provider, LlmTrashTalk)


def test_resolve_ollama_and_api_build_llm_provider():
    for name in ("ollama", "claude_api"):
        provider = resolve_trash_talk(_Cfg({"trash_talk.provider": name}), _rng())
        assert isinstance(provider, LlmTrashTalk)


def test_resolve_unknown_provider_uses_template():
    provider = resolve_trash_talk(_Cfg({"trash_talk.provider": "gpt99"}), _rng())
    assert isinstance(provider, TrashTalk)
    assert not isinstance(provider, LlmTrashTalk)
