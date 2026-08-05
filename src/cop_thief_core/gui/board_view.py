"""BoardView: a Tk canvas rendering ONE peer's view of the world — my true
position, known barriers, visited trail, and the opponent-location belief heatmap.
The opponent's true position is never available to draw in live mode; the replay
viewer passes it explicitly only from revealed logs. Coverage-omitted (Tk).
"""

import tkinter as tk

ROLE_COLORS = {"thief": "#e67e22", "police": "#2980b9"}


class BoardView(tk.Canvas):
    """N×N grid canvas for one peer (cell size injected from config, not hard-coded)."""

    def __init__(self, parent, board_size: int, cell_px: int):
        self.board_size = board_size
        self.cell_px = cell_px
        side = board_size * cell_px
        super().__init__(parent, width=side, height=side, bg="white",
                         highlightthickness=1, highlightbackground="#888")

    def _cell_rect(self, row: int, col: int):
        x0, y0 = col * self.cell_px, row * self.cell_px
        return x0, y0, x0 + self.cell_px, y0 + self.cell_px

    @staticmethod
    def _heat_color(probability: float, peak: float) -> str:
        """White → red scale by probability relative to the current peak."""
        if peak <= 0:
            return "#ffffff"
        level = min(1.0, probability / peak)
        channel = int(255 * (1 - 0.8 * level))
        return f"#ff{channel:02x}{channel:02x}"

    def _draw_agent(self, pos, role: str, inset: int) -> None:
        x0, y0, x1, y1 = self._cell_rect(*pos)
        self.create_oval(x0 + inset, y0 + inset, x1 - inset, y1 - inset,
                         fill=ROLE_COLORS.get(role, "#555"), outline="black", width=2)
        self.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=role[0].upper(),
                         fill="white", font=("Segoe UI", 14, "bold"))

    def render(self, my_pos, role: str, barriers, visited, belief_matrix,
               opponent_pos=None, opponent_role: str | None = None) -> None:
        """Redraw the whole board. Live mode passes opponent_pos=None — only my
        truth and the belief heatmap show. Replay passes both revealed positions."""
        self.delete("all")
        peak = max((cell for row in belief_matrix for cell in row), default=0.0)
        inset = self.cell_px // 6
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.create_rectangle(*self._cell_rect(row, col), outline="#ccc",
                                      fill=self._heat_color(belief_matrix[row][col], peak))
        for cell in visited:
            x0, y0, x1, y1 = self._cell_rect(*cell)
            self.create_oval(x0 + 2 * inset, y0 + 2 * inset,
                             x1 - 2 * inset, y1 - 2 * inset, fill="#b0bec5", outline="")
        for cell in barriers:
            x0, y0, x1, y1 = self._cell_rect(*cell)
            self.create_rectangle(x0 + 4, y0 + 4, x1 - 4, y1 - 4, fill="#263238", outline="")
        if opponent_pos is not None and opponent_role:
            self._draw_agent(opponent_pos, opponent_role, inset)
        if my_pos is not None:
            self._draw_agent(my_pos, role, inset)
