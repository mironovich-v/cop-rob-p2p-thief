"""Trash-talk providers: the natural-language hint an agent sends WITH its move.

The MOVE is always chosen by the Python strategy (`domain/brains.py`); this module
only produces the *banter*. The DEFAULT (and only, until the LLM slice) provider is
`template` — canned Python strings, ZERO tokens, instant, offline. A template line
may bluff (the thief lies ~40% of the time); the honesty verdict is sealed into the
commit and revealed at audit. Every hint is capped to the negotiated word limit
before it goes on the wire.
"""

import random

from cop_thief_core.constants import VERDICT_LIE, VERDICT_TRUTH, Role

# Landmark vocabulary keyed by the negotiated `setting`; unknown settings fall back
# so a template line always has a location cue to name.
LANDMARKS: dict[str, list[str]] = {
    "New York": ["Times Square", "Central Park", "the Brooklyn Bridge",
                 "Wall Street", "Harlem", "the East Village"],
    "London": ["Big Ben", "Tower Bridge", "Camden", "Soho", "the Thames"],
    "Paris": ["the Eiffel Tower", "Montmartre", "the Louvre", "the Left Bank"],
}
_DEFAULT_LANDMARKS = ["downtown", "the old market", "the harbor", "the north gate"]

_THIEF_LINES = [
    "Catch me if you can - I'm slipping past {landmark}!",
    "Still one step ahead, near {landmark}.",
    "You'll never pin me down around {landmark}.",
    "Too slow, officer - {landmark} is mine.",
]
_POLICE_LINES = [
    "I'm closing in around {landmark}.",
    "Nowhere left to run past {landmark}.",
    "Corner by corner - starting at {landmark}.",
    "I can see your trail near {landmark}.",
]
_THIEF_BLUFF_RATE = 0.4  # heuristic: how often the thief names a place it is NOT


class TrashTalk:
    """Template provider (the shipped default): pick and fill a canned line.
    No LLM, no tokens, no network. Returns (hint, verdict, reasoning, prompt)."""

    every_n_steps = 1
    uses_llm = False

    def __init__(self, rng: random.Random | None = None, max_words: int = 15) -> None:
        self._rng = rng or random.Random()
        self._turn = 0
        self.max_words = max(1, int(max_words))  # agreed hard cap on hint length

    def _cap(self, hint: str) -> str:
        """Enforce the negotiated word limit before a hint goes on the wire."""
        words = hint.split()
        return hint if len(words) <= self.max_words else " ".join(words[: self.max_words])

    def say(self, role, state, belief, setting, opponent_hint, deadline=None):
        hint, verdict = self._template(role, setting)
        return self._cap(hint), verdict, "", ""  # (hint, verdict, reasoning, prompt)

    def _template(self, role: Role, setting: str) -> tuple[str, str]:
        landmark = self._rng.choice(LANDMARKS.get(setting, _DEFAULT_LANDMARKS))
        lines = _THIEF_LINES if role is Role.THIEF else _POLICE_LINES
        hint = self._rng.choice(lines).format(landmark=landmark)
        lying = role is Role.THIEF and self._rng.random() < _THIEF_BLUFF_RATE
        return hint, (VERDICT_LIE if lying else VERDICT_TRUTH)
