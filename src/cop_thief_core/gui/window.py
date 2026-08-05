"""PeerWindow: the Tk chrome shared by the live view — a turn banner, the board
canvas, and a right-hand label panel. Exposes the window protocol the 7.4a
view-model calls: render(view) / set_label(key, text) / set_turn(mine, text).
Coverage-omitted (Tk); the view-model it serves is fully unit-tested.
"""

import tkinter as tk

from cop_thief_core.gui.board_view import BoardView
from cop_thief_core.shared.sysinfo import collect_spec
from cop_thief_core.shared.version import BOOK_VERSION, CODE_VERSION

GREEN, IDLE = "#2ecc71", "#95a5a6"

_PANEL = [("step", "Step"), ("mode", "Game mode"), ("model", "Model"),
          ("tokens", "Tokens step / total"), ("llm_time", "LLM response (s)"),
          ("barriers", "Barriers used"), ("hint_in", "Opponent says"),
          ("hint_out", "My response"), ("verdict", "My verdict"),
          ("commit", "My commit (sealed)"), ("status", "Status")]


class PeerWindow:
    """One peer's live window. Shows MY truth + the opponent-belief heatmap only."""

    def __init__(self, title: str, board_size: int, cell_px: int, game_id: str = ""):
        self.root = tk.Tk()
        self.root.title(f"{title}  |  Game: {game_id}" if game_id else title)
        self.banner = tk.Label(self.root, text="WAITING...", bg=IDLE, fg="white",
                               font=("Segoe UI", 14, "bold"), pady=6)
        self.banner.pack(fill="x")
        body = tk.Frame(self.root)
        body.pack(padx=8, pady=8)
        self.board = BoardView(body, board_size, cell_px)
        self.board.pack(side="left")
        panel = tk.Frame(body)
        panel.pack(side="left", fill="y", padx=(10, 0))
        self.labels: dict[str, tk.Label] = {}
        for key, caption in _PANEL:
            tk.Label(panel, text=caption + ":", font=("Segoe UI", 9, "bold"),
                     anchor="w").pack(fill="x")
            self.labels[key] = tk.Label(panel, text="-", anchor="w", wraplength=300,
                                        justify="left")
            self.labels[key].pack(fill="x", pady=(0, 6))

    def add_about_menu(self, extra: dict) -> None:
        menubar = tk.Menu(self.root)
        helpm = tk.Menu(menubar, tearoff=0)
        helpm.add_command(label="About", command=lambda: self._show_about(extra))
        menubar.add_cascade(label="Help", menu=helpm)
        self.root.config(menu=menubar)

    def _show_about(self, extra: dict) -> None:
        top = tk.Toplevel(self.root)
        top.title("About — Cop-Thief P2P (vm__fabi)")
        header = (f"Cop-Thief P2P — vm__fabi\nCode version: v{CODE_VERSION}\n"
                  f"Book version: v{BOOK_VERSION}")
        tk.Label(top, text=header, justify="left", anchor="w",
                 font=("Segoe UI", 11, "bold"), padx=14, pady=(12, 6)).pack(fill="x")
        spec = "\n".join(f"{key}: {value}" for key, value in {**extra, **collect_spec()}.items())
        tk.Label(top, text=spec, justify="left", anchor="w",
                 font=("Consolas", 9), padx=14, pady=(0, 10)).pack(fill="x")
        tk.Button(top, text="Close", command=top.destroy).pack(pady=(0, 10))

    def set_turn(self, mine: bool, text: str | None = None) -> None:
        self.banner.config(bg=GREEN if mine else IDLE,
                           text=text or ("MY TURN — thinking..." if mine else "WAITING..."))

    def set_label(self, key: str, value: str) -> None:
        if key in self.labels:
            self.labels[key].config(text=value)

    def render(self, view: dict) -> None:
        self.board.render(view["position"], view["role"], view["barriers"],
                          view["visited"], view["belief"],
                          view.get("opponent_position"), view.get("opponent_role"))
        self.set_label("step", str(view["step"]))
        if "barriers_used" in view:
            self.set_label("barriers", str(view["barriers_used"]))
