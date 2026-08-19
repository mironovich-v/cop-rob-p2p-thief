"""LivePeerApp: run THIS peer's series in a worker thread and mirror it in a Tk
window. The runtime pushes events (negotiated/incoming/moved/game_over/error) to a
thread-safe queue; the Tk main loop drains it and applies each through the 7.4a
view-model. The board shows MY truth + the opponent-belief heatmap only.
Coverage-omitted (Tk).
"""

import queue
import threading
import time

from cop_thief_core.gui.game_mode import mode_and_model
from cop_thief_core.gui.live_apply import LiveState, apply_event
from cop_thief_core.gui.window import PeerWindow


class LivePeerApp:
    """Threads one SimulationSdk.run_peer and renders its event stream live."""

    def __init__(self, sdk, role: str, stub_llm: bool = True):
        self._sdk = sdk
        self._role = role
        self._stub = stub_llm
        self._events: queue.Queue = queue.Queue()
        self.outcome: dict | None = None
        self._t0: float | None = None
        group = sdk.config.get("game.group_name", "unnamed")
        self._window = PeerWindow(f"Cop-Thief peer: {role.upper()}",
                                  sdk.config.get("board.size"),
                                  sdk.config.get("gui.cell_px", 52))
        self._state = LiveState(role=role, window=self._window)
        game_mode, model_label = mode_and_model(sdk.config)
        self._window.add_about_menu({"role": role, "group": group,
                                     "game_mode": game_mode, "model": model_label})
        self._window.set_label("mode", game_mode)
        self._window.set_label("model", model_label)
        self._start_button = None
        self._build_start_bar()

    def _build_start_bar(self) -> None:
        import tkinter as tk
        bar = tk.Frame(self._window.root)
        bar.pack(fill="x", padx=8, pady=(0, 8))
        self._start_button = tk.Button(bar, text="Start", command=self._start)
        self._start_button.pack(side="left")

    def _start(self) -> None:
        if self._t0 is not None:
            return
        self._t0 = time.monotonic()
        self._start_button.config(state="disabled")
        self._window.set_turn(False, "STARTING...")
        threading.Thread(target=self._worker, daemon=True).start()
        self._window.root.after(1000, self._tick_clock)

    def _worker(self) -> None:
        try:
            self.outcome = self._sdk.run_peer(self._role, stub_llm=self._stub,
                                              listener=self._events.put)
        except Exception as exc:  # surface startup/runtime failures in the window
            self._events.put({"type": "error", "message": str(exc)})

    def _tick_clock(self) -> None:
        if self._t0 is not None and self._state.clock_running:
            elapsed = int(time.monotonic() - self._t0)
            self._window.banner.config(
                text=f"{self._window.banner.cget('text')}".split("  [")[0]
                + f"  [{elapsed // 60:02d}:{elapsed % 60:02d}]")
        self._window.root.after(1000, self._tick_clock)

    def _poll(self) -> None:
        while not self._events.empty():
            apply_event(self._state, self._events.get_nowait())
        self._window.root.after(100, self._poll)

    def run(self) -> dict:
        self._window.set_turn(False, "READY — press Start")
        self._window.root.after(100, self._poll)
        self._window.root.mainloop()
        return self.outcome or {"summary": {"result": "aborted", "winner": "-"}}
