"""Agent brains — the aggregator kept for import stability.

The role brains grew past the 150-line file limit once the counted-series
forensics landed, so they live in their own modules now:

  * ``brain_base``  — ``Decision``, ``BrainBase`` (the student's seam)
  * ``evader``      — ``ThiefBrain``
  * ``pursuer``     — ``PoliceBrain``

Everything is re-exported here, so existing imports and every configured
``strategy.thief_class`` / ``police_class`` string of the form
``cop_thief_core.domain.brains:ThiefBrain`` keep resolving unchanged.
"""

from cop_thief_core.domain.brain_base import BrainBase, Decision
from cop_thief_core.domain.evader import ThiefBrain
from cop_thief_core.domain.pursuer import PoliceBrain

__all__ = ["BrainBase", "Decision", "PoliceBrain", "ThiefBrain"]
