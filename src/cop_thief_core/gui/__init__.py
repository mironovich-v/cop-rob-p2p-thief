"""GUI layer — kept strictly OUTSIDE the domain and protocol packages.

Two concerns live here: a pure, headless-testable **view-model** (this package's
`game_mode` + `live_apply`) that turns config and runtime events into window
mutations, and the Tk shell that renders them (added in a later slice). The live
window shows ONLY this peer's local truth + belief heatmap — never opponent truth
(the runtime snapshot it renders carries no opponent position by construction).
"""

__all__ = ["apply_event", "LiveState", "mode_and_model", "mode_from_recorded_model"]

from cop_thief_core.gui.game_mode import mode_and_model, mode_from_recorded_model
from cop_thief_core.gui.live_apply import LiveState, apply_event
