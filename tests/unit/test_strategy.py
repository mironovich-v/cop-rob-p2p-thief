"""Tests for the strategy seam (PRD_strategy_brains, TODO slice 3.2)."""

import pytest

from cop_thief_core.constants import Role
from cop_thief_core.domain.brains import BrainBase, PoliceBrain, ThiefBrain
from cop_thief_core.strategy import load_brain_cls, resolve_brain, resolve_brain_cls


class _Cfg:
    def __init__(self, values):
        self._values = values

    def get(self, key, default=None):
        return self._values.get(key, default)


def test_load_brain_cls_valid():
    assert load_brain_cls("cop_thief_core.domain.brains:ThiefBrain") is ThiefBrain


def test_load_brain_cls_malformed_selector():
    with pytest.raises(ValueError):
        load_brain_cls("no_colon_here")


def test_load_brain_cls_missing_attribute():
    with pytest.raises(ValueError):
        load_brain_cls("cop_thief_core.domain.brains:NoSuchBrain")


def test_load_brain_cls_not_a_brain():
    with pytest.raises(TypeError):
        load_brain_cls("cop_thief_core.constants:Role")


def test_resolve_brain_cls_defaults():
    assert resolve_brain_cls(None, Role.THIEF) is ThiefBrain
    assert resolve_brain_cls(None, Role.POLICE) is PoliceBrain


def test_resolve_brain_cls_honours_selector():
    cfg = _Cfg({"strategy.thief_class": "cop_thief_core.domain.brains:PoliceBrain"})
    assert resolve_brain_cls(cfg, Role.THIEF) is PoliceBrain  # override proven


def test_resolve_brain_instantiates_default():
    brain = resolve_brain(None, Role.POLICE)
    assert isinstance(brain, BrainBase)
    assert brain.role is Role.POLICE
