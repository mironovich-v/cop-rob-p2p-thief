"""Strategy seam — the student's mission: REPLACE the move policy (pure Python).

The MOVE is chosen entirely by the Python strategy; the LLM is NEVER consulted for
it. Students extend the shipped brains (override ``_pick_move`` and/or
``_decide_move``) or write a full policy by subclassing ``ThiefBrain`` /
``PoliceBrain``, then point an OPTIONAL config selector at it
(``strategy.thief_class`` / ``strategy.police_class`` = ``"package.module:Class"``).
With no selector the shipped heuristic brains run. The trash-talk provider is
wired in Stage 4; until then ``resolve_brain`` uses the null provider.
"""

import importlib
import random

from cop_thief_core.constants import Role
from cop_thief_core.domain.brains import BrainBase, Decision, PoliceBrain, ThiefBrain
from cop_thief_core.strategy.talk_providers import resolve_trash_talk

__all__ = [
    "BrainBase",
    "Decision",
    "PoliceBrain",
    "ThiefBrain",
    "load_brain_cls",
    "resolve_brain",
    "resolve_brain_cls",
    "resolve_trash_talk",
]

_DEFAULTS: dict[Role, type[BrainBase]] = {Role.THIEF: ThiefBrain, Role.POLICE: PoliceBrain}
_SELECTOR_KEY: dict[Role, str] = {
    Role.THIEF: "strategy.thief_class",
    Role.POLICE: "strategy.police_class",
}


def load_brain_cls(dotted: str) -> type[BrainBase]:
    """Import a brain class from a ``"package.module:ClassName"`` selector."""
    module_path, sep, class_name = dotted.partition(":")
    if not sep or not module_path or not class_name:
        raise ValueError(f"strategy selector must be 'package.module:ClassName', got {dotted!r}")
    module = importlib.import_module(module_path)
    try:
        brain_cls = getattr(module, class_name)
    except AttributeError as exc:
        raise ValueError(f"{class_name!r} not found in module {module_path!r}") from exc
    if not (isinstance(brain_cls, type) and issubclass(brain_cls, BrainBase)):
        raise TypeError(f"{dotted!r} does not name a BrainBase subclass")
    return brain_cls


def resolve_brain_cls(config, role: Role) -> type[BrainBase]:
    """The brain class for ``role``: the config selector if set, else the default."""
    selector = config.get(_SELECTOR_KEY[role]) if config is not None else None
    if selector:
        return load_brain_cls(str(selector))
    return _DEFAULTS[role]


def resolve_brain(config, role: Role, llm=None, rng: random.Random | None = None, trash=None) -> BrainBase:
    """Instantiate the resolved brain, wired with the configured trash-talk provider
    (default: the free `template`). Pass an explicit `trash` to override."""
    rng = rng or random.Random()
    if trash is None:
        trash = resolve_trash_talk(config, rng, llm)
    return resolve_brain_cls(config, role)(llm, rng=rng, trash=trash)
