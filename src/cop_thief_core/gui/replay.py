"""ReplayApp: the Visual Replay Player (book §7). Steps a saved sub-game log back
onto the board, re-verifying each record's commit live and — because reveal has
happened — drawing BOTH true trajectories from the mutually-revealed logs. Our
standardized log carries no received-smell history, so the belief field stays flat
in replay (integrity + full-truth reconstruction are what this view proves).
Coverage-omitted (Tk); the data layer it drives is unit-tested (`test_replay_data`).
"""

import ast
import json

from cop_thief_core.gui.game_mode import mode_from_recorded_model
from cop_thief_core.gui.replay_data import (
    normalize_log,
    opponent_positions,
    verify_record,
)

_OPPONENT = {"police": "thief", "thief": "police"}


def barriers_from_state(state_str: str) -> list:
    """Parse the `barriers=[[r, c], ...]` tail of a sealed record's state string."""
    try:
        return [tuple(cell) for cell in ast.literal_eval(state_str.split("barriers=")[1])]
    except (IndexError, ValueError, SyntaxError, AttributeError):
        return []


class ReplayApp:
    """Play/pause/restart through one peer's log, both revealed agents on one board."""

    def __init__(self, config, log_data: dict, log_path=None):
        from cop_thief_core.gui.window import PeerWindow

        self._size = config.get("board.size")
        self._cell = config.get("gui.cell_px", 52)
        self._window = PeerWindow("REPLAY", self._size, self._cell,
                                  log_data.get("game_id", ""))
        self._flat = [[0.0] * self._size for _ in range(self._size)]
        self._ingest(log_data, log_path)
        self._build_controls()

    def _ingest(self, log_data: dict, log_path) -> None:
        view = normalize_log(log_data)
        self._records = [record for record in view["records"]
                         if record["payload"].get("type") != "system_spec"]
        self._my = view["positions"]
        self._opp = opponent_positions(log_path, log_data)
        self._role, self._opp_role = view["role"], _OPPONENT.get(view["role"], "thief")
        self._result, self._winner, self._audit = (
            view["result"], view["winner"], view["audit"])
        spec = next((record["payload"] for record in view["records"]
                     if record["payload"].get("type") == "system_spec"), {})
        mode, model = mode_from_recorded_model(spec.get("model", ""))
        self._window.set_label("mode", mode)
        self._window.set_label("model", model)
        self._window.add_about_menu({"role": self._role, "mode": mode, "model": model})
        self._reset()

    def _reset(self) -> None:
        self._visited: set = set()
        self._barriers: set = set()
        self._index, self._playing = 0, False

    def _total(self) -> int:
        return max(len(self._my), len(self._opp))

    def _advance(self) -> None:
        total = self._total()
        if self._index >= total:
            self._window.set_turn(False, f"REPLAY DONE: {self._result} — "
                                         f"winner {str(self._winner).upper()}")
            self._playing = False
            return
        i = self._index
        my_pos = tuple(self._my[min(i, len(self._my) - 1)]) if self._my else None
        opp_pos = tuple(self._opp[min(i, len(self._opp) - 1)]) if self._opp else None
        if i < len(self._my):
            self._visited.add(tuple(self._my[i]))
        if i < len(self._records):
            self._apply_record_labels(i)
        self._window.render({
            "role": self._role, "step": i + 1, "position": my_pos,
            "barriers": sorted(self._barriers), "visited": self._visited,
            "belief": self._flat, "opponent_position": opp_pos,
            "opponent_role": self._opp_role,
        })
        both = "BOTH agents shown" if self._opp else "opponent log missing"
        self._window.set_label("status", f"step {i + 1}/{total} | opponent audit "
                               f"{'PASSED' if self._audit['passed'] else 'FAILED'} | {both}")
        self._index += 1

    def _apply_record_labels(self, i: int) -> None:
        payload = self._records[i]["payload"]
        self._barriers.update(barriers_from_state(payload.get("state", "")))
        status = verify_record(self._records, i)
        self._window.set_label("hint_out", f"step {i + 1}: {payload.get('hint', '-')}")
        self._window.set_label("verdict", f"{payload.get('verdict', '-')} (revealed)")
        self._window.set_label("commit", f"{self._records[i]['commit'][:24]}... [{status}]")

    def _build_controls(self) -> None:
        import tkinter as tk

        bar = tk.Frame(self._window.root)
        bar.pack(fill="x", padx=8, pady=(0, 8))
        tk.Button(bar, text="Play/Pause", command=self._toggle).pack(side="left")
        tk.Button(bar, text="Step", command=self._advance).pack(side="left", padx=6)
        tk.Button(bar, text="Restart", command=self._restart).pack(side="left")

    def _toggle(self) -> None:
        self._playing = not self._playing
        if self._playing:
            self._tick()

    def _tick(self) -> None:
        if not self._playing:
            return
        self._advance()
        self._window.root.after(600, self._tick)

    def _restart(self) -> None:
        self._reset()
        self._window.set_turn(False, "RESTARTED — press Play")

    def run(self) -> None:
        self._window.set_turn(False, "REPLAY — press Play")
        self._window.root.mainloop()


def load_log_file(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)
