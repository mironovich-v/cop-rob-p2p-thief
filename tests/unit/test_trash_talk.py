"""Tests for the template trash-talk provider (PRD_llm_verbal_layer, slice 4.2)."""

import random

from cop_thief_core.constants import VERDICT_LIE, VERDICT_TRUTH, Role
from cop_thief_core.strategy import resolve_brain
from cop_thief_core.strategy.talk_providers import resolve_trash_talk
from cop_thief_core.strategy.trash_talk import TrashTalk


class FakeRng:
    """Deterministic: always the first choice; a fixed random() for the bluff roll."""

    def __init__(self, rand):
        self._rand = rand

    def choice(self, seq):
        return seq[0]

    def random(self):
        return self._rand


def test_thief_bluffs_when_roll_low():
    hint, verdict, _, _ = TrashTalk(FakeRng(0.0)).say(Role.THIEF, None, None, "New York", "")
    assert verdict == VERDICT_LIE
    assert "Times Square" in hint  # first New York landmark


def test_thief_truthful_when_roll_high():
    _, verdict, _, _ = TrashTalk(FakeRng(0.9)).say(Role.THIEF, None, None, "New York", "")
    assert verdict == VERDICT_TRUTH


def test_police_never_lies():
    _, verdict, _, _ = TrashTalk(FakeRng(0.0)).say(Role.POLICE, None, None, "New York", "")
    assert verdict == VERDICT_TRUTH


def test_word_cap_enforced_before_wire():
    hint, _, _, _ = TrashTalk(FakeRng(0.9), max_words=2).say(Role.POLICE, None, None, "London", "")
    assert len(hint.split()) <= 2


def test_unknown_setting_uses_default_landmarks():
    hint, _, _, _ = TrashTalk(FakeRng(0.9)).say(Role.THIEF, None, None, "Atlantis", "")
    assert "downtown" in hint  # first default landmark


def test_resolve_trash_talk_default_is_template(police_config):
    provider = resolve_trash_talk(police_config, random.Random(0))
    assert isinstance(provider, TrashTalk)
    assert provider.uses_llm is False
    assert provider.max_words == 15  # from world.hint_max_words


def test_resolve_brain_wires_template_trash(police_config):
    brain = resolve_brain(police_config, Role.POLICE)
    assert isinstance(brain._trash, TrashTalk)  # no longer the null provider
